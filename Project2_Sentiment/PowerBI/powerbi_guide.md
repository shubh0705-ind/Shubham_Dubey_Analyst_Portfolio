# Power BI Dashboard Guide
## Project 2: Social Media Sentiment & Brand Intelligence

---

## DASHBOARD ARCHITECTURE (4 Pages)

### Page 1: Brand Intelligence Overview
**Visuals:**
| Visual | Type | Fields |
|--------|------|---------|
| Sentiment Gauge | KPI Card | avg_vader_compound per brand |
| Total Mentions | Card | COUNT(post_id) |
| Share of Voice | Donut | brand, mention_count |
| Monthly Sentiment Trend | Multi-line | month, avg_score, brand |
| Platform Breakdown | Clustered Bar | platform, sentiment |
| Positive vs Negative | 100% Stacked | brand, sentiment_type |

**Slicers:** Brand, Platform, Country, Date Range, Category

---

### Page 2: Complaint & Crisis Tracker
**Purpose:** Monitor negative sentiment spikes

**Visuals:**
- Heatmap: Category × Brand (negative %)
- Spike Alert Table (z_score > 2)
- Top 10 Viral Negative Posts table
- Engagement vs Sentiment Scatter

---

### Page 3: Competitor Analysis
**Visuals:**
- Side-by-side KPI cards (Samsung | Apple | OnePlus)
- Radar Chart: 6 dimensions per brand
- Monthly Share-of-Voice area chart
- NPS Score trend line

---

### Page 4: Topic & Keyword Analysis
**Visuals:**
- Word Cloud (custom visual)
- Topic Distribution Bar (LDA outputs)
- Category complaint ranking
- Positive driver topics

---

## DAX MEASURES

```dax
-- Net Sentiment Score
Net Sentiment Score = 
DIVIDE(
    CALCULATE(COUNTROWS(posts), posts[true_sentiment] = "Positive") -
    CALCULATE(COUNTROWS(posts), posts[true_sentiment] = "Negative"),
    COUNTROWS(posts),
    0
) * 100

-- Share of Voice %
Share of Voice % = 
DIVIDE(
    COUNTROWS(posts),
    CALCULATE(COUNTROWS(posts), ALL(posts[brand])),
    0
) * 100

-- Weighted Engagement Sentiment
Weighted Sentiment = 
DIVIDE(
    SUMX(posts, posts[vader_compound] * (posts[likes] + posts[shares]*2 + posts[comments])),
    SUM(posts[likes]) + SUM(posts[shares])*2 + SUM(posts[comments]),
    0
)

-- MoM Sentiment Change
MoM Sentiment Δ = 
VAR Current = CALCULATE(AVERAGE(posts[vader_compound]), DATESMTD(posts[post_date]))
VAR Previous = CALCULATE(AVERAGE(posts[vader_compound]), PREVIOUSMONTH(posts[post_date]))
RETURN Current - Previous

-- Crisis Alert Flag
Crisis Flag = 
IF(
    CALCULATE(
        DIVIDE(
            COUNTROWS(FILTER(posts, posts[true_sentiment]="Negative")),
            COUNTROWS(posts)
        )
    ) > 0.4,
    "⚠️ CRISIS",
    "✅ Normal"
)

-- Complaint Rate by Category
Complaint Rate % = 
DIVIDE(
    CALCULATE(COUNTROWS(posts), posts[true_sentiment] = "Negative"),
    COUNTROWS(posts),
    0
) * 100

-- Engagement Score
Total Engagement = SUM(posts[likes]) + SUM(posts[shares])*3 + SUM(posts[comments])*2

-- Verified vs Regular Sentiment Gap
Verified Sentiment Premium = 
CALCULATE(AVERAGE(posts[vader_compound]), posts[verified_user] = 1) -
CALCULATE(AVERAGE(posts[vader_compound]), posts[verified_user] = 0)
```

---

## COLOR CODING RULES
- Positive Sentiment: #00FF9F
- Negative Sentiment: #FF6B6B  
- Neutral: #AAAAAA
- Samsung Brand: #1428A0 (Samsung Blue)
- Apple Brand: #555555 (Apple Silver)
- OnePlus Brand: #F5000E (OnePlus Red)

## KPI THRESHOLDS
| Metric | Good | Warning | Critical |
|--------|------|---------|----------|
| Net Sentiment Score | >20 | 0-20 | <0 |
| Negative Rate | <25% | 25-35% | >35% |
| Share of Voice | >33% | 25-33% | <25% |
