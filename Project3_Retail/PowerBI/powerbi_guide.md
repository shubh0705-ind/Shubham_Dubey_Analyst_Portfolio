# Power BI Dashboard Guide
## Project 3: Retail Sales Forecasting & Insight Engine

---

## DASHBOARD ARCHITECTURE (5 Pages)

### Page 1: Executive Revenue Dashboard
**Visuals:**
| Visual | Type | Fields |
|--------|------|---------|
| Total Revenue | KPI Card | SUM(net_amount) |
| YoY Growth | KPI Card | yoy_growth_pct |
| Avg Order Value | KPI Card | AVG(net_amount) |
| Active Customers | KPI Card | DISTINCTCOUNT(customer_id) |
| Revenue Trend | Area Chart | month, revenue |
| Category Revenue | Bar | category, revenue |
| Region Heatmap | Map | region/state, revenue |
| Channel Mix | Donut | channel, revenue |

**Slicers:** Year, Quarter, Category, Region, Channel

---

### Page 2: Forecast Dashboard
**Visuals:**
- Prophet Forecast Line (actual + forecast + confidence band)
- Seasonal Decomposition (trend, seasonality)
- Festive vs Off-Season Revenue bar
- Forecast Accuracy KPI (MAPE = 1.75%)
- Next 6-month forecast table with ranges

---

### Page 3: Customer Intelligence (RFM)
**Visuals:**
- Customer Segments Donut
- Segment Value Heatmap (Recency × Monetary)
- LTV by Segment clustered bar
- New vs Returning customers trend
- At-Risk Customers Table (drill-through)

---

### Page 4: Product Performance
**Visuals:**
- Top 10 SKUs by Revenue (horizontal bar)
- Category Margin Matrix (scatter: revenue vs margin)
- Return Rate by Category
- Stock Alert Table (below reorder level)
- Slow-moving SKUs Table

---

### Page 5: Cohort Retention
**Visuals:**
- Cohort Retention Heatmap (custom matrix)
- Month-1 retention trend
- Customer Lifetime Value curve
- Cohort Revenue comparison

---

## DAX MEASURES

```dax
-- Total Revenue
Total Revenue = SUM(transactions[net_amount])

-- YoY Revenue Growth
YoY Growth % = 
VAR CurrentYear = CALCULATE([Total Revenue], YEAR(transactions[order_date]) = YEAR(TODAY()))
VAR PrevYear = CALCULATE([Total Revenue], YEAR(transactions[order_date]) = YEAR(TODAY())-1)
RETURN DIVIDE(CurrentYear - PrevYear, PrevYear, 0) * 100

-- Average Order Value
AOV = DIVIDE([Total Revenue], DISTINCTCOUNT(transactions[transaction_id]), 0)

-- Gross Profit
Gross Profit = 
SUMX(
    transactions,
    transactions[net_amount] - transactions[quantity] * RELATED(products[cost_price])
)

-- Gross Margin %
Gross Margin % = DIVIDE([Gross Profit], [Total Revenue], 0) * 100

-- Return Rate
Return Rate % = 
DIVIDE(
    CALCULATE(COUNTROWS(transactions), transactions[return_flag] = 1),
    COUNTROWS(transactions),
    0
) * 100

-- Customer Retention Rate
Retention Rate % = 
VAR NewCust = CALCULATE(DISTINCTCOUNT(transactions[customer_id]),
                        DATESINPERIOD(transactions[order_date], MIN(transactions[order_date]), 1, MONTH))
VAR TotalCust = DISTINCTCOUNT(transactions[customer_id])
RETURN DIVIDE(TotalCust - NewCust, TotalCust, 0) * 100

-- Revenue per Customer
Revenue per Customer = DIVIDE([Total Revenue], DISTINCTCOUNT(transactions[customer_id]), 0)

-- Festive Season Revenue
Festive Revenue = 
CALCULATE([Total Revenue], 
    transactions[order_month] IN {10, 11, 12})

-- Festive Revenue Lift
Festive Lift % = 
DIVIDE(
    [Festive Revenue] / 3,
    CALCULATE([Total Revenue], transactions[order_month] IN {1,2,3,4,5,6,7,8,9}) / 9,
    0
) * 100 - 100

-- Rolling 3-Month Revenue
Rolling 3M Revenue = 
CALCULATE([Total Revenue], 
    DATESINPERIOD(transactions[order_date], LASTDATE(transactions[order_date]), -3, MONTH))

-- Pareto: Top 20% Customers Revenue Share
Top 20 Customer Revenue % = 
VAR Top20Count = ROUND(DISTINCTCOUNT(transactions[customer_id]) * 0.2, 0)
VAR Top20Revenue = 
    SUMX(
        TOPN(Top20Count, 
             SUMMARIZE(transactions, transactions[customer_id], "Rev", [Total Revenue]),
             [Rev], DESC),
        [Rev]
    )
RETURN DIVIDE(Top20Revenue, [Total Revenue], 0) * 100
```

---

## FORECASTING VISUAL SETUP

To show Prophet forecast in Power BI:
1. Import `forecast_results.csv` as a new table
2. Create relationship on `ds` (date) with transactions date
3. Use Line + Shaded Area chart:
   - Line: `yhat` (forecast)
   - Lower bound: `yhat_lower`
   - Upper bound: `yhat_upper`
   - Second series: actual monthly revenue
4. Add vertical reference line at forecast start date

## PERFORMANCE OPTIMIZATION
- Use Import mode
- Disable auto-date/time hierarchy
- Create dedicated Date dimension table
- Aggregate transactions to monthly grain for trend visuals
- Use bookmarks for "Current Year" vs "All Years" toggle
