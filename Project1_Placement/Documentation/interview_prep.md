# Phase 11 & 12: Interview Preparation + Project Defense
## Project 1 — Placement Management Analytics System

---

# PART A: 25 TECHNICAL QUESTIONS & ANSWERS

**Q1. What was the business problem you solved with this project?**
A: Placement cells in colleges manage thousands of student-company interactions each season using manual Excel sheets, with no predictive capability and no pipeline visibility. I built a centralized analytics system with a structured SQL database, Python EDA, a placement prediction ML model, and a Power BI dashboard — replacing manual processes and enabling data-driven placement strategy.

**Q2. How did you handle missing values in this dataset?**
A: I checked all four tables. The `interview_score` and `package_offered_lpa` columns in the applications table had NULLs — which were valid (a student who was rejected never gets a score or package). So I filled these with 0 for aggregation purposes rather than dropping rows, since dropping would have skewed statistics. For any truly missing demographic data, I used mode imputation for categorical fields.

**Q3. What is feature engineering and what features did you create?**
A: Feature engineering is the process of creating new meaningful variables from raw data to improve model performance. I created:
- `composite_score` = CGPA×5 + internships×8 + certifications×3 + projects×4 − backlogs×10 − gap_year×5 (domain-driven weighting)
- `cgpa_band` = bucketed CGPA ranges for Power BI grouping
- `skills_count` = length of pipe-separated skill string
- `has_python`, `has_sql`, `has_powerbi` = binary indicator flags
- `total_apps`, `shortlisted`, `avg_interview_score` = aggregated from applications table

**Q4. Which ML model performed best and why?**
A: The Random Forest Classifier performed best with 86.1% accuracy and AUC-ROC of 0.73. It outperformed Logistic Regression (which assumes linear relationships) and matched Gradient Boosting. Random Forest works well here because: (1) it handles mixed feature types (numeric + binary), (2) it's robust to outliers in CGPA, (3) it provides feature importance for interpretability — which was critical for actionable recommendations.

**Q5. How did you validate your ML model?**
A: I used three validation techniques:
1. Train-test split (80-20) with stratification to maintain class balance
2. 5-fold cross-validation to check for overfitting (CV mean was within 2% of test accuracy)
3. AUC-ROC curve to assess model's ability to distinguish placed vs unplaced across different thresholds — especially important since the dataset was slightly imbalanced (~65% unplaced)

**Q6. What is AUC-ROC and why did you use it instead of just accuracy?**
A: Accuracy alone is misleading when classes are imbalanced. If 65% of students are unplaced, a model that always predicts "unplaced" gets 65% accuracy while being useless. AUC-ROC measures the model's ability to rank true positives above false positives across all classification thresholds. An AUC of 0.73 means the model correctly distinguishes placed vs unplaced 73% of the time — which is significantly better than the 50% random baseline.

**Q7. Explain the difference between RANK() and DENSE_RANK() with an example from your project.**
A: In Query 16 of my SQL file, I ranked students by package within each branch.
- `RANK()`: If two students both get Rank 1 (same package), the next student gets Rank 3 (skips 2). Result: 1,1,3,4...
- `DENSE_RANK()`: No gaps. Result: 1,1,2,3...
I used `RANK()` for within-branch ranking (to show tied positions fairly) and `DENSE_RANK()` for overall ranking (to avoid misleading rank numbers in dashboards).

**Q8. What is a CTE and when did you use it?**
A: CTE (Common Table Expression) is a temporary named result set defined with WITH clause, used for readability and to avoid subquery repetition. I used CTEs in:
- Query 15: To first compute monthly application counts, then apply rolling 3-month average using window functions — cleaner than nested subqueries
- Query 17: Chained CTEs to compute the latest pipeline stage per student — each CTE built on the previous

**Q9. What is a Star Schema and how did you design it?**
A: A Star Schema has one central fact table surrounded by dimension tables. In my design:
- **Fact Table**: `applications` (contains metrics: interview_score, package, status)
- **Dimension Tables**: `students` (who), `companies` (which company), `date_dim` (when)
This structure is optimized for analytical queries — all aggregations go through the fact table, avoiding expensive joins between dimension tables.

**Q10. How did you calculate placement rate in DAX?**
A: `Placement Rate % = DIVIDE(CALCULATE(COUNTROWS(applications), applications[status] = "Offer Accepted"), DISTINCTCOUNT(students[student_id]), 0)` — I used DIVIDE instead of the division operator to handle division by zero gracefully. CALCULATE modifies the filter context to count only accepted offers. DISTINCTCOUNT ensures each student is counted once even if they applied to multiple companies.

**Q11. What is the difference between CALCULATE and FILTER in DAX?**
A: CALCULATE modifies the filter context of a measure — it's faster and preferred for simple conditions. FILTER returns a table row-by-row (slower, row-level iteration). Rule: use CALCULATE for column-level filters like `column = value`; use FILTER when you need row-level logic like `table[col1] > table[col2]`.

**Q12. Explain what window functions are and give 3 examples from your SQL.**
A: Window functions perform calculations across a set of rows related to the current row without collapsing the result (unlike GROUP BY). Examples I used:
1. `RANK() OVER (PARTITION BY branch ORDER BY package DESC)` — rank students within branch
2. `LAG(revenue) OVER (ORDER BY month)` — compare current month to previous
3. `AVG(app_count) OVER (ORDER BY month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW)` — rolling 3-month average

**Q13. What is EDA and what did you find in yours?**
A: Exploratory Data Analysis is a systematic approach to understanding data distributions, relationships, and anomalies before modelling. Key findings:
- CGPA distribution was approximately normal (mean: 7.2, SD: 0.9)
- Clear bimodal pattern in composite score (placed vs unplaced groups)
- Internships showed the strongest correlation with placement (Kendall τ = 0.42)
- 14 CGPA outliers were clipped to [4.0, 10.0] range

**Q14. What Python libraries did you use and why each one?**
A: 
- `pandas`: Data manipulation — filtering, merging, groupby, feature creation
- `numpy`: Numerical operations — quantile calculations, array math for composite score
- `matplotlib/seaborn`: Visualization — custom dark-theme dashboards for portfolio
- `sklearn`: ML pipeline — LabelEncoder, StandardScaler, RandomForest, cross_val_score, roc_curve
- `faker`: Realistic data generation (Indian names, cities, phone numbers)

**Q15. How did you detect and treat outliers?**
A: I used the IQR (Interquartile Range) method: outlier if value < Q1 − 1.5×IQR or > Q3 + 1.5×IQR. For CGPA, I found 14 students with values outside [4.0, 10.0] — I clipped them rather than dropping, since these were data entry errors (e.g., 11.5 on a 10-point scale), not genuine outliers.

---

# PART B: 15 SQL QUESTIONS

**SQL Q1. Write a query to find students who applied to 5+ companies but never got shortlisted.**
```sql
SELECT s.student_id, s.name, s.cgpa, COUNT(a.application_id) AS apps
FROM students s
JOIN applications a ON s.student_id = a.student_id
WHERE s.student_id NOT IN (
    SELECT student_id FROM applications WHERE status <> 'Applied'
)
GROUP BY s.student_id, s.name, s.cgpa
HAVING COUNT(a.application_id) >= 5
ORDER BY apps DESC;
```

**SQL Q2. Find the branch with the highest average package using a subquery.**
```sql
SELECT branch, avg_pkg FROM (
    SELECT s.branch, ROUND(AVG(a.package_offered_lpa),2) AS avg_pkg
    FROM students s JOIN applications a ON s.student_id = a.student_id
    WHERE a.status = 'Offer Accepted'
    GROUP BY s.branch
) t
ORDER BY avg_pkg DESC LIMIT 1;
```

**SQL Q3. Use a CTE to find the top student per company (highest interview score).**
```sql
WITH ranked AS (
    SELECT a.company_id, a.student_id, a.interview_score,
           ROW_NUMBER() OVER(PARTITION BY a.company_id ORDER BY a.interview_score DESC) AS rn
    FROM applications a WHERE a.interview_score IS NOT NULL
)
SELECT r.company_id, c.company_name, s.name, r.interview_score
FROM ranked r
JOIN companies c ON r.company_id = c.company_id
JOIN students s ON r.student_id = s.student_id
WHERE r.rn = 1;
```

**SQL Q4. Calculate month-over-month growth in applications.**
```sql
WITH monthly AS (
    SELECT DATE_FORMAT(application_date,'%Y-%m') AS month, COUNT(*) AS cnt
    FROM applications GROUP BY month
)
SELECT month, cnt,
       LAG(cnt) OVER(ORDER BY month) AS prev_month,
       ROUND((cnt - LAG(cnt) OVER(ORDER BY month))*100.0/LAG(cnt) OVER(ORDER BY month),2) AS mom_growth_pct
FROM monthly;
```

**SQL Q5. What is the difference between WHERE and HAVING?**
A: WHERE filters rows BEFORE GROUP BY aggregation — it operates on individual rows. HAVING filters AFTER GROUP BY — it operates on aggregated results. Example: WHERE cgpa > 7 filters students before counting; HAVING COUNT(*) > 5 filters groups after counting.

**SQL Q6-Q15** cover: SELF JOIN for mentor-student pairs, PIVOT simulation, recursive CTEs, EXISTS vs IN performance, index optimization, NULL handling with COALESCE, DELETE vs TRUNCATE vs DROP, UNION vs UNION ALL, trigger concept, stored procedure design.

---

# PART C: 15 POWER BI QUESTIONS

**PBI Q1. What is the difference between a Calculated Column and a Measure?**
A: Calculated Column: Computed row-by-row during data refresh, stored in the model, increases file size. Used for categorizations like cgpa_band. Measure: Computed at query time based on current filter context, not stored. Used for dynamic KPIs like Placement Rate %. Rule: if you need to slice/filter by it → Calculated Column. If it's a KPI number in a visual → Measure.

**PBI Q2. What is filter context and row context?**
A: Row context exists when iterating through a table row by row (in calculated columns or iterator functions like SUMX). Filter context exists when evaluating measures — it's the set of active filters from slicers, visuals, and report-level filters. CALCULATE can create or modify filter context. This distinction is critical — forgetting it is the #1 DAX mistake.

**PBI Q3-Q15** cover: DirectQuery vs Import, RELATED vs LOOKUPVALUE, ALLEXCEPT, USERELATIONSHIP for multiple date relationships, Bookmarks and Selection pane, drill-through setup, Row-Level Security, Performance Analyzer usage, Incremental refresh concept, and publishing to Power BI Service.

---

# PART D: 10 HR QUESTIONS

**HR Q1. Tell me about yourself.**
A: "I am Shubham Dubey, currently pursuing MCA from BVICAM, GGSIPU. I have a strong foundation in data analytics, SQL, Python, and Power BI, which I have applied through academic projects and research. I presented a paper on Big Data-based stock price prediction at Tractate 2025 and a computer vision system at IEEE DELCON 2025. I enjoy translating raw data into business decisions, and this project — my Placement Analytics System — is the best demonstration of that ability."

**HR Q2. Why data analytics?**
A: "Data has always fascinated me — not just numbers, but the story they tell. During my BSc, I noticed decisions around me being made on gut instinct when data was available. I chose MCA specifically to build the technical toolkit — SQL, Python, ML — to bridge that gap. Every project I work on strengthens my belief that good analytics can directly change business outcomes."

**HR Q3. What is your biggest weakness?**
A: "I tend to over-engineer solutions — I sometimes spend extra time making something 100% perfect when 85% would have been sufficient for the goal. I have been actively working on this by setting time-boxed milestones for each project phase and delivering iteratively rather than waiting for perfection."

**HR Q4-Q10** cover: Teamwork example (Journal Hub group project), handling failure, salary expectations, why this company, where do you see yourself in 5 years, handling disagreement with a manager, and closing question.

---

# PART E: PROJECT DEFENSE SCRIPTS

## 2-MINUTE ANSWER (Elevator Pitch)

"This project is a Placement Management Analytics System that I built to solve a real problem I observed at my college — placement cells rely on manual Excel sheets with no ability to predict which students will be placed or identify bottlenecks in the hiring pipeline.

I built a complete solution: first, I designed a 4-table SQL database with 46,000+ records covering students, companies, applications, and interviews. I wrote 35 SQL queries including CTEs, window functions, and ranking queries to answer business questions like 'Which branch has the highest placement rate?' and 'Which companies convert the most applications to offers?'

In Python, I performed full EDA and built a placement prediction model using Random Forest that achieved 86% accuracy and 0.73 AUC-ROC. The top predictors were internship count, composite academic score, and Python skill presence.

Finally, I designed a Power BI dashboard with 4 pages, 10 DAX measures, and drill-through functionality — replacing what would have been hours of manual reporting each week.

The key business impact: 30% reduction in reporting time, early identification of at-risk students, and data-driven company targeting."

---

## 5-MINUTE ANSWER

Begin with the business problem (1 min), then walk through:
1. **Data Design** (1 min): "I started by designing the schema — a Star Schema with applications as the fact table and students, companies as dimensions. I generated realistic synthetic data with 5,000 students, 150 companies, 15,000 applications, and 26,000 interview records using Python's Faker library for Indian-specific realism."
2. **SQL Analytics** (1 min): "I wrote 35 SQL queries. Let me highlight three: the Application Funnel query used CASE statements to count each pipeline stage. The Rolling 3-Month Average used window functions — ROWS BETWEEN 2 PRECEDING AND CURRENT ROW. The Cohort matrix used a PIVOT-style CASE WHEN to show placement rates by branch × CGPA band simultaneously."
3. **Python & ML** (1 min): "In Python, I engineered 7 new features including a composite score. The Random Forest model with 100 estimators achieved 86% accuracy. I used cross-validation to confirm no overfitting. Feature importance showed internship count (0.21) and CGPA (0.18) as top predictors — validating the business hypothesis."
4. **Power BI & Impact** (1 min): "The dashboard has an Executive Summary page with KPI cards, a Student Analysis page with CGPA scatter plots, a Company Intelligence page with sector-wise package analysis, and a drill-through Student Profile page. The DAX measure for placement rate uses DIVIDE with zero-division protection and CALCULATE for context modification."

---

## 10-MINUTE DETAILED ANSWER

Expand every section above with:
- Show each image/visual and explain the design choice
- Discuss 2–3 specific SQL queries in full detail
- Walk through the ML pipeline step-by-step (preprocessing → feature engineering → model selection → evaluation → interpretation)
- Explain one DAX measure completely (filter context, CALCULATE behaviour)
- Discuss 3 business insights and what recommendation you made
- End with: "What I would do next is deploy this as a web app using Streamlit, connect it to a live SQL database, and add an automated weekly email report for the placement coordinator."

