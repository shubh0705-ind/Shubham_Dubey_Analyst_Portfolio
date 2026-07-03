import re
import math
from typing import Dict, Any, Tuple

# Precompile all regex patterns for O(1) loop execution
COMPANY_SUFFIXES = re.compile(r'\b(ltd|limited|pvt|private|inc|incorporated|corp|corporation|llp|technologies|digital|services|group|solutions)\b')
PUNCTUATION_PATTERN = re.compile(r'[^\w\s]')

RETRIEVAL_PATTERN = re.compile(
    r'\b(embeddings?|vector search|semantic search|pinecone|weaviate|qdrant|milvus|faiss|bm25|semantic retrieval|retrieval quality|ann|hnsw|lucene|solr|bi-encoders?|cross-encoders?|approximate nearest neighbors?|product quantization|ivf-pq)\b'
)
PRODUCTION_PATTERN = re.compile(
    r'\b(shipped to production|deployed|real users|production environments?|model serving|mlops|kubernetes|sagemaker|model registr(?:y|ies)|feature stores?|vertex ai|model quantization|tensorrt)\b'
)
EVALUATION_PATTERN = re.compile(
    r'\b(ndcg|mrr|map|a/b testing|offline evaluations?)\b'
)
RANKING_PATTERN = re.compile(
    r'\b(learning-to-rank|xgboost|re-ranking|neural rankers?|lambdamart|lightgbm|catboost|deepfm|wide and deep|din)\b'
)
MATCHING_PATTERN = re.compile(
    r'\b(candidate matching|two-sided marketplaces?|recommender systems?|recommendation engines?|collaborative filtering|matrix factorization)\b'
)
LEADERSHIP_PATTERN = re.compile(
    r'\b(led|mentored|managed|hired|technical leads?|team leads?)\b'
)

def normalize_company(company_name: str) -> str:
    if not company_name:
        return ""
    name = str(company_name).lower()
    name = COMPANY_SUFFIXES.sub('', name)
    name = PUNCTUATION_PATTERN.sub('', name)
    return " ".join(name.split())

# Pre-normalized set of pure IT services firms
SERVICES_FIRMS = {normalize_company(f) for f in [
    "tcs", "tata consultancy services", "infosys", "wipro", 
    "accenture", "cognizant", "capgemini", "tech mahindra", "hcl"
]}

def get_current_title(candidate: Dict[str, Any]) -> str:
    profile_raw = candidate.get('profile')
    profile = profile_raw if isinstance(profile_raw, dict) else {}
    
    if profile.get('current_title'):
        return str(profile['current_title'])
    
    career_raw = candidate.get('career_history')
    career = career_raw if isinstance(career_raw, list) else []
    
    if not career:
        return "Unknown"
        
    for job in career:
        if isinstance(job, dict) and job.get('is_current'):
            return str(job.get('title', 'Unknown'))
            
    first_job = career[0]
    if isinstance(first_job, dict):
        return str(first_job.get('title', 'Unknown'))
        
    return "Unknown"

def calculate_yoe_score(yoe: float) -> float:
    if 5.0 <= yoe <= 9.0:
        return 1.0
    elif yoe < 5.0:
        return max(0.0, yoe / 5.0)
    else:
        return max(0.1, 1.0 - (math.log1p(yoe - 9.0) * 0.15))

def extract_career_features(career_history: list) -> Tuple[float, float, float, float, float, float, float]:
    retrieval_hits = production_hits = eval_hits = ranking_hits = matching_hits = leadership_hits = 0
    product_company_months = total_months = 0
    
    if isinstance(career_history, list):
        for job in career_history:
            if not isinstance(job, dict):
                continue
                
            desc = str(job.get('description', '')).lower()
            
            retrieval_hits += len(RETRIEVAL_PATTERN.findall(desc))
            production_hits += len(PRODUCTION_PATTERN.findall(desc))
            eval_hits += len(EVALUATION_PATTERN.findall(desc))
            ranking_hits += len(RANKING_PATTERN.findall(desc))
            matching_hits += len(MATCHING_PATTERN.findall(desc))
            leadership_hits += len(LEADERSHIP_PATTERN.findall(desc))
            
            duration = job.get('duration_months', 0)
            try:
                duration = int(float(duration)) if duration is not None else 0
            except (ValueError, TypeError):
                duration = 0
                
            total_months += duration
            
            norm_company = normalize_company(job.get('company', ''))
            if norm_company not in SERVICES_FIRMS:
                product_company_months += duration

    def normalize(hits: int, scale: float) -> float:
        return min(1.0, math.log1p(hits) / scale)

    product_ratio = (product_company_months / total_months) if total_months > 0 else 0.5
    
    return (
        normalize(retrieval_hits, scale=1.5),
        normalize(production_hits, scale=1.2),
        normalize(eval_hits, scale=1.2),
        normalize(ranking_hits, scale=1.2),
        normalize(matching_hits, scale=1.0),
        normalize(leadership_hits, scale=1.5),
        product_ratio
    )