# Phase 11 & 12: Interview Preparation + Project Defense
## Project 3 — Retail Sales Forecasting & Insight Engine

---

# PART A: 25 TECHNICAL QUESTIONS & ANSWERS

**Q1. What is time-series forecasting and why did you choose Prophet?**
A: Time-series forecasting predicts future values of a variable based on its historical patterns. I chose Facebook Prophet because: (1) It automatically detects yearly, weekly, and daily seasonality — critical for retail data that has festive spikes. (2) It handles missing data without imputation. (3) It supports holiday effects — I can add Diwali, Christmas as known high-demand events. (4) It decomposes forecast into trend + seasonality + holidays — making it interpretable to business stakeholders, not just data scientists. (5) Setup requires only 3 key parameters vs ARIMA's complex p,d,q tuning.

**Q2. What is MAPE and what did your model achieve?**
A: MAPE (Mean Absolute Percentage Error) = MEAN(|Actual − Forecast| / Actual) × 100. It's the most intuitive forecast accuracy metric because it's scale-independent and expressed as a percentage. My Prophet model achieved MAPE of 1.75% — meaning on average, my monthly forecasts were off by 1.75% from actual values. Industry benchmark for retail forecasting is <8%, so 1.75% is significantly above benchmark. This level of accuracy means for a month with ₹50L actual revenue, the forecast would be within ₹87,500 — sufficient for confident inventory planning.

**Q3. What is RFM analysis and how did you implement it?**
A: RFM is a customer segmentation framework based on three dimensions: Recency (how recently they bought — lower days = better), Frequency (how many times — higher = better), Monetary (how much they spent — higher = better). Implementation: (1) Computed each dimension per customer using pandas groupby. (2) Scored each dimension 1–5 using `pd.qcut` (quantile-based bucketing). (3) Added the three scores to get RFM_Total (3–15). (4) Applied business logic rules to assign segment labels like Champions, At Risk, Lost. (5) Fed the normalized RFM values into K-Means clustering (k=4) for unsupervised validation — silhouette score of 0.38 confirmed meaningful cluster separation.

**Q4. What is Cohort Analysis and what did it reveal?**
A: Cohort analysis tracks groups of customers (cohorts) who share a common event — in retail, their first purchase month — and monitors their behaviour over subsequent months. I grouped all customers by their first purchase month, then calculated how many from each cohort made purchases in months 1, 2, 3... after joining. This creates a retention matrix. Key findings: Month-1 retention was 34% (below industry benchmark of 40%), customers acquired during Oct–Dec 2023 festive campaign retained at 44% after 6 months — significantly higher than regular cohorts — validating the festive acquisition strategy.

**Q5. Explain your K-Means clustering implementation.**
A: Steps: (1) Selected 3 features: Recency, Frequency, Monetary. (2) Applied StandardScaler — essential because Recency is in days (0–500) while Monetary is in rupees (hundreds to lakhs); without scaling, Monetary would dominate distance calculations. (3) Used Elbow Method — plotted inertia for k=2 to 8; selected k=4 where the curve elbowed. (4) Validated with Silhouette Score (0.38) — scores >0.25 indicate meaningful clusters. (5) Mapped clusters back to business labels by examining each cluster's mean RFM values.

**Q6. What is the Elbow Method for choosing k in K-Means?**
A: Plot the Within-Cluster Sum of Squares (inertia) for different k values. As k increases, inertia decreases — but the rate of decrease slows. The "elbow" point is where diminishing returns begin — adding more clusters gives little additional cohesion. I plotted k=2 to 8 and found the elbow at k=4. Silhouette Score confirmed this — it peaked at k=4 before declining for higher k values.

**Q7. What is the Pareto Principle and did your data validate it?**
A: The Pareto Principle (80/20 rule) states 80% of outcomes come from 20% of inputs. In retail: 80% of revenue from 20% of customers. My analysis found top 20% of customers (1,600 out of 8,000) generated 68% of revenue — slightly less than the classic 80/20 but still strongly Pareto-shaped. This concentration justifies the Champions retention investment: losing 200 Champions would cost more revenue than losing 2,000 Regular customers.

**Q8. How did you handle seasonality in your forecast model?**
A: Prophet automatically detects seasonality using Fourier series decomposition. I set `yearly_seasonality=True` and `seasonality_mode='multiplicative'` — multiplicative because festive season revenue scales proportionally with the overall revenue trend (a bigger year has a bigger Diwali spike). I also set `changepoint_prior_scale=0.1` (conservative) to prevent overfitting to one-off spikes in training data. The model correctly detected Oct–Dec as the high-seasonality period and Jun–Jul as a secondary peak.

**Q9. Explain your data cleaning steps for this project.**
A: Four main steps: (1) Removed 4,800 return transactions (return_flag=1) from revenue analysis — returns should not count as revenue. (2) Applied 1st–99th percentile winsorization on net_amount — this removed extreme outliers (bulk B2B orders) that would distort forecasting. Removed ~1,200 records total. (3) Merged product cost_price from the products table to compute gross profit per transaction. (4) Engineered time features: year_month, day_of_week, is_weekend, order_quarter — needed for both Prophet and cohort analysis.

**Q10. What is the difference between Gross Profit and Net Revenue?**
A: Net Revenue (or Net Amount) = Unit Price × Quantity − Discount. This is what the customer pays. Gross Profit = Net Revenue − Cost of Goods Sold (unit_price × quantity × cost_price ratio). Gross Margin % = Gross Profit / Net Revenue × 100. In my project, Electronics had high Net Revenue (₹2.1Cr) but low Gross Margin (18%) because cost prices are high. Beauty had lower revenue but 41% margin — meaning Beauty is more profitable per rupee earned despite lower volume.

**Q11. How would you explain your dashboard to a non-technical business person?**
A: "Think of this dashboard as your business health monitor — like a car's instrument panel. The top row shows your vital signs: total revenue this year, how much it grew vs last year, average order size, and how many customers are active. The big graph shows our monthly revenue for the past 3 years plus my model's best estimate for the next 6 months, with a shaded band showing the realistic range. Below that, you can see which products and regions are driving the most revenue. And on the next page, I've divided our customers into 7 groups based on their buying habits — so the marketing team knows exactly who to target with what message."

**Q12. What is SUMX and when would you use it over SUM in DAX?**
A: SUM simply adds up a column: `SUM(transactions[net_amount])`. SUMX is an iterator — it evaluates an expression row-by-row then sums the results: `SUMX(transactions, transactions[quantity] * RELATED(products[cost_price]))`. Use SUMX when the calculation requires multiplying columns from different tables row-by-row (like COGS = quantity × cost_price where they're in different tables). SUMX is slower on large datasets because it iterates row-by-row — use it only when SUM is insufficient.

**Q13. How did you create the YoY Growth % measure?**
A: Using DAX time intelligence: `VAR CurrentYear = CALCULATE([Total Revenue], YEAR(transactions[order_date]) = YEAR(TODAY()))` then `VAR PrevYear = CALCULATE([Total Revenue], SAMEPERIODLASTYEAR(dates[Date]))`. SAMEPERIODLASTYEAR shifts the filter context back exactly one year. Then `DIVIDE(CurrentYear - PrevYear, PrevYear, 0) * 100`. The DIVIDE with 0 as third argument prevents division-by-zero when previous year has no data (e.g., for new product categories).

**Q14. What is Incremental Refresh in Power BI and why is it relevant for retail?**
A: Incremental Refresh allows Power BI to only refresh new/changed data rather than the entire dataset. For retail transactions that grow by thousands of rows daily, full refresh would take 30+ minutes and strain the database. With Incremental Refresh: configure a RangeStart–RangeEnd date parameter, set "Archive data: 3 years," "Refresh: last 7 days." Power BI refreshes only the last 7 days of transactions, which completes in seconds, while keeping 3 years of historical data in the model.

**Q15-Q25** cover: Star schema design for retail analytics, slowly changing dimensions, window functions for running totals, the difference between DATEADD and SAMEPERIODLASTYEAR, Prophet uncertainty intervals interpretation, K-Means limitations (spherical clusters, outlier sensitivity), difference between classification and clustering, silhouette score interpretation, MAPE vs RMSE tradeoff, handling data drift in production ML models, deploying Prophet as an API using FastAPI/Flask.

---

# PART B: 15 SQL QUESTIONS (Retail-specific)

**SQL Q1. Calculate rolling 3-month revenue with window functions.**
```sql
WITH monthly AS (
    SELECT order_year, order_month,
           DATE(CONCAT(order_year,'-',LPAD(order_month,2,'0'),'-01')) AS dt,
           SUM(net_amount) AS revenue
    FROM transactions WHERE return_flag=0
    GROUP BY order_year, order_month
)
SELECT dt, revenue,
       ROUND(AVG(revenue) OVER(ORDER BY dt ROWS BETWEEN 2 PRECEDING AND CURRENT ROW),2) AS rolling_3m
FROM monthly ORDER BY dt;
```

**SQL Q2. Find top product per category by revenue using ROW_NUMBER.**
```sql
SELECT category, product_name, revenue FROM (
    SELECT p.category, p.product_name,
           ROUND(SUM(t.net_amount),2) AS revenue,
           ROW_NUMBER() OVER(PARTITION BY p.category ORDER BY SUM(t.net_amount) DESC) AS rn
    FROM products p JOIN transactions t ON p.product_id=t.product_id
    WHERE t.return_flag=0 GROUP BY p.category, p.product_name
) r WHERE rn=1 ORDER BY revenue DESC;
```

**SQL Q3-Q15** cover: RFM segmentation in pure SQL, cohort retention matrix SQL, Pareto analysis using cumulative window functions, channel-wise YoY growth, payment method trend, customer churn detection (no purchase in 90 days), seasonal index calculation, inventory turnover days, CASE-based cross-sell indicator, and running total with OVER(ORDER BY) pattern.

---

# PROJECT DEFENSE SCRIPTS

## 2-MINUTE ANSWER

"This is a Retail Sales Forecasting and Insight Engine built on 3 years of transactional data — 60,000+ records across 8,000 customers and 48 products.

The business problem was clear: the retail team was spending 70% of reporting time on manual Excel work with no ability to forecast future revenue or understand which customers were about to churn.

My solution delivered three major analytical outputs: First, a Facebook Prophet time-series model that forecasts monthly revenue 6 months ahead with just 1.75% MAPE — well below the 8% industry benchmark. This means inventory can be planned with confidence. Second, an RFM customer segmentation that divided 8,000 customers into 7 actionable segments — Champions, Loyal, At Risk, New, and Lost — each requiring a different marketing approach. Third, a cohort retention analysis showing that festive season customers (Oct–Dec cohort) retain 44% after 6 months vs 28% for regular cohorts — directly proving the ROI of festive acquisition campaigns.

The Power BI dashboard has 5 pages with 10 DAX measures and reduced manual reporting time by 70%."

## 5-MINUTE ANSWER
Extend with: Prophet model configuration details (multiplicative seasonality, changepoint scale), walk through RFM scoring methodology (pd.qcut to score 1–5), explain the cohort heatmap interpretation, highlight the 3 most surprising insights (Electronics margin is lowest despite highest revenue, App channel AOV is 23% higher, UPI has overtaken credit cards), and explain the business recommendations derived from each.

## 10-MINUTE ANSWER
Full technical depth: show the complete Python pipeline execution, explain every Prophet parameter choice, demonstrate the K-Means elbow curve and silhouette score, walk through 3 complex SQL queries line by line, explain 4 DAX measures with filter context discussion, present 5 business insights with quantified impact, and close with deployment roadmap: "Next step would be to build a FastAPI endpoint that runs Prophet weekly and pushes results directly to Power BI via REST API — creating a fully automated forecast refresh pipeline."

