import math
from datetime import datetime
from feature_engineering import extract_career_features, calculate_yoe_score, get_current_title
from honeypot_detector import analyze_honeypot_risk, calculate_risk_penalty

EVAL_DATE = datetime(2026, 7, 1)

def _safe_float(val, default=0.0):
    try:
        f = float(val)
        return default if math.isnan(f) else f
    except (ValueError, TypeError):
        return default

def get_title_relevance(title: str) -> float:
    t = title.lower()
    if any(x in t for x in ['search engineer', 'recommendation engineer', 'applied ml', 'ml engineer']):
        return 1.0
    if any(x in t for x in ['data scientist', 'ai engineer', 'nlp engineer']):
        return 0.8
    if any(x in t for x in ['backend', 'software engineer']):
        return 0.6
    return 0.3

def score_candidate(candidate: dict) -> dict:
    candidate_id = candidate.get("candidate_id", "")
    
    honeypot_eval = analyze_honeypot_risk(candidate)
    
    profile_raw = candidate.get('profile')
    profile = profile_raw if isinstance(profile_raw, dict) else {}
    
    career_raw = candidate.get('career_history')
    career = career_raw if isinstance(career_raw, list) else []
    
    signals_raw = candidate.get('redrob_signals')
    signals = signals_raw if isinstance(signals_raw, dict) else {}
    
    (
        retrieval_score, production_score, eval_score, 
        ranking_score, matching_score, leadership_score, 
        product_ratio
    ) = extract_career_features(career)
    
    yoe = _safe_float(profile.get('years_of_experience'))
    yoe_score = calculate_yoe_score(yoe)
    
    raw_base_tech = (
        (retrieval_score * 0.25) +
        (production_score * 0.20) +
        (eval_score * 0.15) +
        (ranking_score * 0.10) +
        (matching_score * 0.10) +
        (product_ratio * 0.10) +
        (yoe_score * 0.05) +
        (leadership_score * 0.05)
    )
    
    title_score = get_title_relevance(get_current_title(candidate))
    base_tech_score = (raw_base_tech * 0.8) + (title_score * 0.2)
    base_tech_score = max(0.0, min(1.0, base_tech_score))
    
    # Rates are clamped to their documented [0,1] (or [0,100] for the raw activity score)
    # ranges at the point of use: corrupted/out-of-range input must never earn MORE than
    # the maximum legitimate credit a perfect, valid value would earn.
    rr = max(0.0, min(1.0, _safe_float(signals.get('recruiter_response_rate'))))
    icr = max(0.0, min(1.0, _safe_float(signals.get('interview_completion_rate'))))
    gh_raw = _safe_float(signals.get('github_activity_score'), -1.0)
    gh = max(0.0, min(100.0, gh_raw)) / 100.0 if gh_raw != -1.0 else 0.0
    saves = _safe_float(signals.get('saved_by_recruiters_30d'))
    searches = _safe_float(signals.get('search_appearance_30d'))
    mh = min(1.0, math.log1p(max(0.0, saves + searches)) / 4.0)
    otw = 1.0 if signals.get('open_to_work_flag') else 0.0
    
    beh_score = (0.40 * rr) + (0.25 * icr) + (0.15 * gh) + (0.10 * mh) + (0.10 * otw)
    beh_mult = max(0.5, min(1.5, 0.5 + beh_score))
    
    services_scalar = 0.1 if product_ratio == 0.0 else 1.0
    
    inactivity_scalar = 1.0
    last_active_str = signals.get('last_active_date')
    if last_active_str:
        try:
            last_active = datetime.strptime(str(last_active_str)[:10], "%Y-%m-%d")
            if (EVAL_DATE - last_active).days > 120:
                inactivity_scalar = 0.2
        except (ValueError, TypeError):
            pass
            
    notice_days = _safe_float(signals.get('notice_period_days'), 90.0)
    if notice_days <= 30: notice_scalar = 1.0
    elif notice_days <= 60: notice_scalar = 0.9
    elif notice_days <= 90: notice_scalar = 0.8
    else: notice_scalar = 0.6
        
    penalty_scalars = services_scalar * inactivity_scalar * notice_scalar * honeypot_eval['penalty_multiplier']
    risk_penalty = calculate_risk_penalty(candidate)
    
    # Theoretical ceiling of base_tech_score(<=1.0) * beh_mult(<=1.5) * penalty_scalars(<=1.0)
    # * (1-risk_penalty)(<=1.0) is 1.5. Rescale by that ceiling so a "perfect" candidate
    # lands at ~1.0 instead of ~1.5 - this is a pure monotonic transform, so it changes
    # nothing about relative ranking or tie-breaking, only the display range of the score.
    raw_product = (base_tech_score * beh_mult * penalty_scalars) * (1.0 - risk_penalty)
    # Floor at 0.01 (post-rescale) so legit candidates don't tie with hard 0.0 honeypots
    final_score = max(0.01, raw_product / 1.5)
    
    if honeypot_eval['risk_level'] == 'high':
        final_score = 0.0
    
    return {
        "candidate_id": candidate_id,
        "final_score": final_score,
        "score_breakdown": {
            "is_honeypot": honeypot_eval['risk_level'] == 'high',
            "honeypot_risk_level": honeypot_eval['risk_level'],
            "honeypot_reasons": honeypot_eval['reasons'],
            "base_tech_score": base_tech_score,
            "behavioral_multiplier": beh_mult,
            "penalty_scalars": penalty_scalars,
            "services_scalar": services_scalar,
            "risk_penalty": risk_penalty,
            "final_score": final_score
        }
    }