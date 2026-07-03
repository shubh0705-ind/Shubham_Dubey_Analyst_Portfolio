import re
from typing import Dict, Any
from feature_engineering import get_current_title

AI_SKILLS_PATTERN = re.compile(r'\b(rags?|pinecone|qdrant|langchain|fine-tuning|faiss|llms?|openai|weaviate|milvus|vector databases?|genai|huggingface)\b', re.IGNORECASE)
NON_TECH_TITLE_PATTERN = re.compile(r'\b(hr|human resources|marketing|sales|accountant|finance|graphic|content writer|operations|customer support|recruiter|business analyst)\b', re.IGNORECASE)
STRONG_EVIDENCE_PATTERN = re.compile(r'\b(embeddings?|vector search|pinecone|weaviate|qdrant|milvus|faiss|bm25|learning-to-rank|xgboost|re-ranking|neural rankers?|ndcg|mrr|map|offline evaluations?|shipped to production|deployed|production environments?|information retrieval|ann|hnsw|lucene|solr|lambdamart|lightgbm|catboost|collaborative filtering|matrix factorization|model serving|mlops|kubernetes|sagemaker)\b', re.IGNORECASE)
LLM_ONLY_PATTERN = re.compile(r'\b(langchain|openai|gpt|prompt engineering|rag)\b', re.IGNORECASE)
LEADERSHIP_TITLE_PATTERN = re.compile(r'\b(cto|chief technology officer|vp|vice president|director|head of)\b', re.IGNORECASE)

def analyze_honeypot_risk(candidate: Dict[str, Any]) -> Dict[str, Any]:
    reasons = []
    penalty = 1.0
    
    profile_raw = candidate.get('profile')
    profile = profile_raw if isinstance(profile_raw, dict) else {}
    
    career_raw = candidate.get('career_history')
    career = career_raw if isinstance(career_raw, list) else []
    
    skills_raw = candidate.get('skills')
    skills = skills_raw if isinstance(skills_raw, list) else []
    
    stated_yoe_raw = profile.get('years_of_experience')
    try:
        yoe_val = float(stated_yoe_raw) if stated_yoe_raw is not None else 0.0
    except (ValueError, TypeError):
        yoe_val = 0.0
        
    current_title = get_current_title(candidate).lower()
    
    ai_skill_count = 0
    has_delusional_expert = False
    
    for skill in skills:
        if not isinstance(skill, dict):
            continue
        skill_name = str(skill.get('name', '')).lower()
        duration = skill.get('duration_months')
        try:
            duration = int(float(duration)) if duration is not None else -1
        except (ValueError, TypeError):
            duration = -1
            
        if skill.get('proficiency') == 'expert' and duration == 0:
            has_delusional_expert = True
        if AI_SKILLS_PATTERN.search(skill_name):
            ai_skill_count += 1

    actual_career_months = 0
    strong_evidence_hits = 0
    has_llm_evidence = False
    
    for job in career:
        if not isinstance(job, dict):
            continue
        duration = job.get('duration_months', 0)
        try:
            duration = int(float(duration)) if duration is not None else 0
        except (ValueError, TypeError):
            duration = 0
            
        actual_career_months += duration
        desc = str(job.get('description', '')).lower()
        
        if STRONG_EVIDENCE_PATTERN.search(desc):
            strong_evidence_hits += 1
        if LLM_ONLY_PATTERN.search(desc):
            has_llm_evidence = True

    # 1. Severe Risk: 0.05x multiplier
    # NOTE: no "yoe_val > 0.0" guard here on purpose. The max(1.0, yoe_val) floor already
    # gives a sane 24-month threshold when yoe_val == 0, so a candidate who declares 0
    # years of experience while listing a multi-year career history is exactly the case
    # this check should catch, not exempt.
    if actual_career_months > (max(1.0, yoe_val) * 12 * 2.0) or has_delusional_expert:
        reasons.append("Severe Risk: Mathematical impossibility or delusional expertise.")
        penalty = 0.05
        
    # 2. Medium Risk: 0.3x multiplier
    elif NON_TECH_TITLE_PATTERN.search(current_title) and ai_skill_count >= 5 and strong_evidence_hits == 0:
        reasons.append("Medium Risk: Non-technical title with high AI skill stuffing but zero evidence.")
        penalty = 0.3

    # 2b. Medium Risk: 0.3x multiplier - LLM-wrapper-only evidence, no underlying ML substance
    elif has_llm_evidence and strong_evidence_hits == 0 and actual_career_months > 0:
        reasons.append("Medium Risk: LLM-wrapper terminology (LangChain/prompt engineering/RAG) with no retrieval, ranking, evaluation, or production evidence.")
        penalty = 0.3
        
    # 3. Low Risk: 0.6x multiplier
    elif len(skills) > 20 and len(skills) > (max(1.0, yoe_val) * 8):
        reasons.append("Low Risk: Excessive skill breadth relative to experience.")
        penalty = 0.6

    risk_level = "none" if penalty == 1.0 else ("high" if penalty < 0.2 else ("medium" if penalty < 0.4 else "low"))
    
    return {"risk_level": risk_level, "penalty_multiplier": penalty, "reasons": reasons}

def calculate_risk_penalty(candidate: Dict[str, Any]) -> float:
    signals_raw = candidate.get('redrob_signals')
    signals = signals_raw if isinstance(signals_raw, dict) else {}
    
    career_raw = candidate.get('career_history')
    career = career_raw if isinstance(career_raw, list) else []
    
    risk_penalty = 0.0
    
    completeness = signals.get('profile_completeness_score')
    try:
        completeness = float(completeness) if completeness is not None else 100.0
    except (ValueError, TypeError):
        completeness = 100.0
    # Clamp to the documented 0-100 range: corrupted/out-of-range values (e.g. 150)
    # must never be allowed to flip this term negative and turn a penalty into a bonus.
    completeness = max(0.0, min(100.0, completeness))
        
    risk_penalty += (100.0 - completeness) / 100.0
    
    if not signals.get('verified_email', True) or not signals.get('verified_phone', True):
        risk_penalty += 0.10
        
    valid_jobs = [job for job in career if isinstance(job, dict)]
    job_count = len(valid_jobs)
    if job_count >= 3:
        total_months = 0
        for job in valid_jobs:
            dur = job.get('duration_months')
            try:
                total_months += int(float(dur)) if dur is not None else 0
            except (ValueError, TypeError):
                pass
        avg_duration = total_months / job_count
        if avg_duration < 12:
            risk_penalty += 0.15
            
    return max(0.0, min(0.8, risk_penalty))