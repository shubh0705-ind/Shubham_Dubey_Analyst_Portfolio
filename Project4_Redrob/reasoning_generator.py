from datetime import datetime
from feature_engineering import get_current_title, normalize_company, SERVICES_FIRMS

EVAL_DATE = datetime(2026, 7, 1)

TEMPLATES = [
    "{prefix} {title} with {yoe} years of experience. The candidate {cap_verb} {evidence}, backed by {bg}. {beh}",
    "{prefix} {yoe} YOE {title}. {cap_verb_title} {evidence} across {bg}. {beh}",
    "{prefix} {article_title} {title} with {bg}. {cap_verb_title} {evidence} over {yoe} years of experience. {beh}",
    "{prefix} Offering {yoe} years of experience, this {title} {cap_verb} {evidence}. Background: {bg}. {beh}",
    "{prefix} {title} ({yoe} YOE, {bg}). {cap_verb_title} {evidence}. Engagement: {beh}",
    "{prefix} With {yoe} years of experience as {article} {title}, the candidate {cap_verb} {evidence}. Comes from {bg}. {beh}",
    "{prefix} {title} featuring {bg}. {cap_verb_title} {evidence} with {yoe} YOE. {beh}",
    "{prefix} {yoe} YOE {title} from {bg}. {cap_verb_title} {evidence}. Behavioral assessment: {beh}",
    "{prefix} Presents {yoe} years of experience as {article} {title}. {cap_verb_title} {evidence} within {bg}. {beh}",
    "{prefix} {title} ({bg}). The candidate {cap_verb} {evidence} over {yoe} years. {beh}"
]

def _article_for(title: str) -> str:
    if not title:
        return "a"
    words = title.split()
    first_word = words[0] if words else title
    # Acronym-style titles (AI, ML, NLP, HR, ...) are pronounced by letter name, so the
    # a/an choice depends on how the first LETTER sounds spoken aloud, not how it's spelled.
    # e.g. "ML" -> "em-ell" (vowel sound) needs "an", "VP" -> "vee-pee" needs "a".
    if first_word.isupper() and 1 <= len(first_word) <= 5 and first_word.isalpha():
        vowel_sound_letters = set("AEFHILMNORSX")
        return "an" if first_word[0] in vowel_sound_letters else "a"
    return "an" if title[0].upper() in "AEIOU" else "a"

def _get_technical_evidence(career_history: list) -> str:
    if not isinstance(career_history, list):
        return "verified software engineering background"
        
    evidence_found = set()
    for job in career_history:
        if not isinstance(job, dict):
            continue
        desc = str(job.get('description', '')).lower()
        if any(k in desc for k in ['embedding', 'vector search', 'semantic search', 'pinecone', 'weaviate', 'qdrant', 'milvus', 'faiss', 'retrieval', 'bm25', 'ann', 'hnsw', 'lucene', 'solr', 'bi-encoder', 'cross-encoder']):
            evidence_found.add("retrieval systems")
        if any(k in desc for k in ['ranking', 'learning-to-rank', 'xgboost', 're-ranking', 'neural ranker', 'lambdamart', 'lightgbm', 'catboost', 'deepfm']):
            evidence_found.add("ranking systems")
        if any(k in desc for k in ['matching', 'recommender', 'recommendation', 'two-sided marketplace', 'collaborative filtering', 'matrix factorization']):
            evidence_found.add("recommendation and matching systems")
        if any(k in desc for k in ['ndcg', 'mrr', 'map', 'a/b testing', 'offline evaluation']):
            evidence_found.add("evaluation frameworks")
        if any(k in desc for k in ['shipped to production', 'deployed', 'production environment', 'model serving', 'mlops', 'kubernetes', 'sagemaker', 'tensorrt']):
            evidence_found.add("production deployment")

    priority_order = ["retrieval systems", "ranking systems", "recommendation and matching systems", "evaluation frameworks", "production deployment"]
    found_ordered = [ev for ev in priority_order if ev in evidence_found]
    
    if len(found_ordered) >= 2: return f"{found_ordered[0]} and {found_ordered[1]}"
    elif len(found_ordered) == 1: return found_ordered[0]
        
    return "verified software engineering background"

def _get_company_background(career_history: list) -> str:
    if not isinstance(career_history, list) or not career_history: 
        return "unclear company background"
        
    product_months = 0
    total_months = 0
    for job in career_history:
        if not isinstance(job, dict):
            continue
        dur = job.get('duration_months')
        try:
            dur = int(float(dur)) if dur is not None else 0
        except (ValueError, TypeError): dur = 0
        total_months += dur
        norm_company = normalize_company(job.get('company', ''))
        if norm_company not in SERVICES_FIRMS:
            product_months += dur
            
    if total_months == 0: return "an unclear company background"
    ratio = product_months / total_months
    if ratio == 0.0: return "a pure IT services background"
    elif ratio == 1.0: return "a pure product company background"
    elif ratio > 0.5: return "a strong product company background"
    return "a consulting-heavy background"

def _get_behavioral_notes(signals: dict) -> str:
    if not isinstance(signals, dict):
        return "standard engagement"
        
    strengths, weaknesses = [], []
    rr = signals.get('recruiter_response_rate')
    try:
        rr = float(rr) if rr is not None else 0.0
    except (ValueError, TypeError): rr = 0.0
    # Clamp to a valid rate before it ever reaches reviewer-facing text - corrupted input
    # (e.g. 2.5) must never render as a nonsensical "250% reply rate".
    rr = max(0.0, min(1.0, rr))
    
    if rr >= 0.7: strengths.append(f"highly responsive ({int(rr*100)}% reply rate)")
    elif rr < 0.3: weaknesses.append(f"poor response rate ({int(rr*100)}%)")
        
    notice = signals.get('notice_period_days')
    try:
        notice = float(notice) if notice is not None else 90.0
    except (ValueError, TypeError): notice = 90.0
    # Negative/corrupted notice periods shouldn't render as "short notice period (-10 days)".
    notice = max(0.0, notice)
        
    if notice <= 30: strengths.append(f"short notice period ({int(notice)} days)")
    elif notice > 60: weaknesses.append(f"long notice period ({int(notice)} days)")
        
    if signals.get('open_to_work_flag'): strengths.append("actively open to work")
    
    last_active = signals.get('last_active_date')
    if last_active:
        try:
            la_date = datetime.strptime(str(last_active)[:10], "%Y-%m-%d")
            days_inactive = (EVAL_DATE - la_date).days
            if days_inactive > 120: weaknesses.append(f"inactive for {days_inactive} days")
        except (ValueError, TypeError): pass

    strength_str = ", ".join(strengths) if strengths else "standard engagement"
    weak_str = f" Concerns include: {', '.join(weaknesses)}." if weaknesses else ""
    return strength_str + weak_str

def generate_reasoning(candidate: dict, score_breakdown: dict) -> str:
    if score_breakdown.get('is_honeypot'):
        reasons = score_breakdown.get('honeypot_reasons', [])
        return f"Candidate dropped: Triggered honeypot rules. {reasons[0] if reasons else ''}"

    cid = candidate.get('candidate_id', 'CAND_0000000')
    
    profile_raw = candidate.get('profile')
    profile = profile_raw if isinstance(profile_raw, dict) else {}
    
    yoe = profile.get('years_of_experience', '0')
    title = get_current_title(candidate)

    career_raw = candidate.get('career_history')
    career = career_raw if isinstance(career_raw, list) else []
    
    tech_evidence = _get_technical_evidence(career)
    bg = _get_company_background(career)
    
    signals_raw = candidate.get('redrob_signals')
    signals = signals_raw if isinstance(signals_raw, dict) else {}
    
    beh_str = _get_behavioral_notes(signals)

    base = score_breakdown.get('base_tech_score', 0.0)
    beh = score_breakdown.get('behavioral_multiplier', 1.0)
    pen = score_breakdown.get('penalty_scalars', 1.0)
    risk = score_breakdown.get('risk_penalty', 0.0)
    # Use the same final_score that's written to the CSV, rather than recomputing it here -
    # recomputing risked silently drifting from the real score if the formula ever changed.
    # Fall back to the local recomputation only if an older score_breakdown without
    # 'final_score' is ever passed in.
    if 'final_score' in score_breakdown:
        score = score_breakdown['final_score']
    else:
        score = (base * beh * pen) * (1.0 - risk) / 1.5

    # Thresholds are 0.7/0.4/0.15 expressed relative to candidate_scorer.py's historical
    # 1.5 ceiling, rescaled by the same /1.5 factor so fit categories keep the same meaning.
    if score >= 0.7 / 1.5:
        fit_prefix = "Exceptional fit:"
        cap_verb = "demonstrates elite capability in" if tech_evidence != "verified software engineering background" else "has a"
    elif score >= 0.4 / 1.5:
        fit_prefix = "Strong fit:"
        cap_verb = "shows verified capability in" if tech_evidence != "verified software engineering background" else "has a"
    elif score >= 0.15 / 1.5:
        fit_prefix = "Partial fit:"
        cap_verb = "has some adjacent experience in" if tech_evidence != "verified software engineering background" else "has a"
    else:
        fit_prefix = "Limited fit:"
        cap_verb = "lacks core JD evidence but maintains" if tech_evidence != "verified software engineering background" else "has a"

    # Only call out an actual constraint violation - a pure-services background or a
    # non-zero (but not hard-dropped) honeypot suspicion - not routine behavioral softness
    # like a normal 45/60-day notice period, which penalty_scalars < 1.0 used to conflate.
    services_scalar = score_breakdown.get('services_scalar', 1.0)
    honeypot_risk_level = score_breakdown.get('honeypot_risk_level', 'none')
    if services_scalar < 1.0 or honeypot_risk_level in ('medium', 'low'):
        if "Concerns include:" in beh_str:
            beh_str = beh_str.replace("Concerns include:", "Major red flags:")
        else:
            beh_str += " Major red flags: violates core JD constraints."

    try:
        variant = int(cid.split('_')[-1]) % len(TEMPLATES)
    except (ValueError, IndexError, AttributeError):
        variant = 0

    article_str = _article_for(str(title))
    reasoning = TEMPLATES[variant].format(
        prefix=fit_prefix, title=title, yoe=yoe, cap_verb=cap_verb, 
        cap_verb_title=cap_verb.capitalize(),
        evidence=tech_evidence, bg=bg, beh=beh_str, article=article_str,
        article_title=article_str.capitalize()
    )
    
    return reasoning.replace("..", ".").replace(" .", ".")