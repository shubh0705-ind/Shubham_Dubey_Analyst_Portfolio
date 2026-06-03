# Phase 1: Business Understanding
## Project 3 — Retail Sales Forecasting & Insight Engine

---

## BUSINESS PROBLEM

A multi-category retail business with 3 years of transactional data (60,000+ records) across online, offline, and app channels was unable to:
- Forecast monthly revenue accurately for inventory planning
- Identify customer churn patterns before revenue impact
- Understand which product categories were underperforming
- Quantify the revenue impact of festive seasons
- Segment customers for targeted marketing campaigns

Manual Excel-based reporting was creating 70% overhead in analysis time with no predictive capability.

---

## WHY COMPANIES NEED THIS

| Department | Business Need |
|-----------|--------------|
| Finance | Accurate revenue forecasts for budgeting |
| Supply Chain | Stock replenishment based on demand predictions |
| Marketing | Customer segment-specific campaign targeting |
| Product | Identify underperforming categories for promotion |
| Executive | Real-time KPI visibility with drill-through |

---

## BUSINESS OBJECTIVES

1. Build a 3-year retail analytics database (60,000+ transactions)
2. Develop Prophet time-series model for 6-month revenue forecast
3. Perform RFM-based customer segmentation (7 actionable segments)
4. Conduct cohort retention analysis across 34 monthly cohorts
5. Identify top 3 underperforming categories via Pareto analysis
6. Build Power BI executive dashboard with 8 KPIs
7. Replace 70% of manual reporting with automated visuals

---

## KEY PERFORMANCE INDICATORS

| KPI | Definition | Benchmark |
|-----|-----------|-----------|
| Monthly Revenue | SUM(net_amount) by month | Track trend |
| YoY Growth % | (Current − Prev Year) / Prev Year × 100 | >10% target |
| Average Order Value | Revenue / Orders | Increase quarterly |
| Gross Margin % | (Revenue − COGS) / Revenue × 100 | >20% |
| Return Rate % | Returned orders / Total × 100 | <10% |
| Customer Retention Rate | Repeat buyers / Total customers | >40% |
| Forecast MAPE | Mean Absolute Percentage Error | <8% |
| Festive Revenue Lift | Festive avg / Regular avg − 1 | >30% |

---

## FORECASTING APPROACH

### Facebook Prophet Model
- **Architecture**: Additive/multiplicative trend + seasonality + holidays
- **Seasonality**: Yearly (detected festive peaks: Oct–Dec, Jun–Jul)
- **Changepoint detection**: Automatic with prior_scale=0.1 (conservative)
- **Confidence interval**: 95%
- **Achieved MAPE**: 1.75% (industry benchmark: <8%)
- **Horizon**: 6 months ahead

### Why Prophet over ARIMA?
| Feature | Prophet | ARIMA |
|---------|---------|-------|
| Missing data | Handles automatically | Requires imputation |
| Seasonality | Multiple seasonalities | Single |
| Holidays | Built-in support | Manual encoding |
| Interpretability | Trend/seasonality decomposition | Limited |
| Setup complexity | Low (3 parameters) | High (p,d,q tuning) |

---

## RFM SEGMENTATION RESULTS

| Segment | Customers | Avg Spend | Action |
|---------|-----------|-----------|--------|
| Champions | 1,211 | ₹48,604 | Reward and retain |
| Loyal Customers | 1,668 | ₹34,965 | Upsell premium products |
| At Risk | 1,185 | ₹37,857 | Win-back campaign |
| New Customers | 1,209 | ₹22,328 | Onboarding nurture |
| Cannot Lose Them | 554 | ₹31,830 | Urgent re-engagement |
| Lost | 897 | ₹14,844 | Low-cost reactivation |

