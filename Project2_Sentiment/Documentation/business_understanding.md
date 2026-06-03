# Phase 1: Business Understanding
## Project 2 — Social Media Sentiment & Brand Intelligence Dashboard

---

## BUSINESS PROBLEM

Consumer electronics brands like Samsung, Apple, and OnePlus receive thousands of social media mentions every day across Twitter, Reddit, and other platforms. Without NLP-powered analysis, marketing and PR teams cannot:
- Detect negative sentiment spikes before they become PR crises
- Understand which product features customers love or hate
- Compare their brand perception against competitors in real time
- Prioritize customer service escalations based on sentiment severity

---

## WHY COMPANIES NEED THIS

| Team | Benefit |
|------|---------|
| Marketing | Measure campaign effectiveness via sentiment lift |
| PR / Communications | Catch crises early; respond before virality |
| Product Management | Identify top complaint themes per feature category |
| Customer Success | Triage high-impact negative posts from verified users |
| Strategy | Track share-of-voice vs competitors over time |

---

## BUSINESS OBJECTIVES

1. Collect and preprocess 30,000+ social media posts across 3 brands
2. Apply VADER and TextBlob for sentiment scoring
3. Classify posts into Positive / Negative / Neutral with 80%+ accuracy
4. Use LDA topic modelling to surface top 5 complaint and praise themes per brand
5. Build a real-time-style dashboard for brand health monitoring
6. Generate competitor comparison view (Samsung vs Apple vs OnePlus)

---

## KEY PERFORMANCE INDICATORS

| KPI | Definition | Alert Threshold |
|-----|-----------|-----------------|
| Net Sentiment Score | (Pos − Neg) / Total × 100 | Alert if < 0 |
| Negative Rate % | Negative posts / Total × 100 | Alert if > 35% |
| Share of Voice | Brand mentions / Market total × 100 | Watch if < 25% |
| Engagement-Weighted Sentiment | Likes/shares-weighted VADER avg | Alert if < −0.1 |
| Crisis Index | Z-score of daily negative count | Alert if > 2.0 |
| Complaint Repeat Rate | % repeated complaint themes | Alert if > 40% |
| NPS Proxy Score | Positive% − Negative% | Alert if < 20 |

---

## EXPECTED BUSINESS IMPACT

- **Early crisis detection**: Catch sentiment spikes 48–72 hours before mainstream press
- **Feature prioritization**: Camera complaints = fix in next OTA update
- **Competitor advantage**: Apple 45% positive vs Samsung 36% → Samsung gap analysis
- **Influencer targeting**: Verified user posts drive 3× more engagement
- **Marketing ROI**: Measure sentiment before vs after ad campaign launches

---

## NLP METHODOLOGY

### Text Preprocessing Pipeline
1. Lowercase conversion
2. URL/mention/hashtag removal (regex)
3. Emoji and special character removal
4. Stop word removal (NLTK corpus)
5. Lemmatization (WordNetLemmatizer)

### Sentiment Models Used
| Model | Method | Accuracy on Dataset |
|-------|--------|---------------------|
| VADER | Lexicon + rule-based | 66.1% |
| TextBlob | Pattern-based | 68.6% |
| Ensemble | Majority vote | 62.8% |

### Topic Modelling
- Algorithm: Latent Dirichlet Allocation (LDA)
- Components: 5 topics per brand per sentiment class
- Vectorizer: CountVectorizer (max 500 features, min_df=2)
- Outputs: Top 5 words per topic = actionable complaint/praise theme

