# Power BI Dashboard Design Guide
## Project 1: Placement Management Analytics System

---

## DASHBOARD ARCHITECTURE (4 Pages)

### Page 1: Executive Summary Dashboard
**Purpose:** High-level KPIs for placement cell director

**Visuals:**
| Visual | Type | Fields | Purpose |
|--------|------|---------|---------|
| Placement Rate | KPI Card | Placed/Total | Top KPI |
| Total Applications | KPI Card | COUNT(application_id) | Volume |
| Avg Package | KPI Card | AVG(package_lpa) | Salary insight |
| Highest Package | KPI Card | MAX(package_lpa) | Top performer |
| Monthly Trend | Line Chart | Month vs Applications | Trend |
| Branch Heatmap | Matrix | Branch × Status | Status breakdown |
| Application Funnel | Funnel Chart | status, count | Pipeline view |
| Package Distribution | Box Plot | package_lpa | Salary range |

**Slicers:** Branch, College, Passout Year, Company Sector

---

### Page 2: Student Performance Analysis
**Purpose:** Identify strong/weak student profiles

**Visuals:**
| Visual | Type | Fields |
|--------|------|---------|
| CGPA vs Package | Scatter Plot | cgpa, package, branch |
| Placement by CGPA Band | Clustered Bar | cgpa_band, placement_pct |
| Skills Distribution | Word Cloud / Bar | skill_name, count |
| Internship Impact | 100% Stacked Bar | internships, placed |
| Composite Score Ranking | Table | Top 50 students |
| State-wise Placement Map | Filled Map | state, placement_pct |

---

### Page 3: Company Intelligence
**Purpose:** Understand company hiring patterns

**Visuals:**
| Visual | Type | Fields |
|--------|------|---------|
| Top Companies | Bar Chart | company_name, offers |
| Sector Package Comparison | Box Plot | sector, package |
| Work Mode Breakdown | Donut | work_mode, count |
| Shortlist vs Select Rate | Gauge | rates |
| Time to Offer | Scatter | company, avg_days |
| Company Size vs Package | Scatter | size, avg_package |

---

### Page 4: Drill-Through – Student Profile
**Purpose:** Individual student deep-dive

**Visuals:**
- Student card with all attributes
- Application timeline visual
- Interview round performance
- Company comparison for that student

---

## DAX MEASURES

```dax
-- MEASURE 1: Overall Placement Rate
Placement Rate % = 
DIVIDE(
    CALCULATE(COUNTROWS(applications), applications[status] = "Offer Accepted"),
    DISTINCTCOUNT(students[student_id]),
    0
)

-- MEASURE 2: Average Package Offered
Avg Package LPA = 
CALCULATE(
    AVERAGE(applications[package_offered_lpa]),
    applications[status] IN {"Selected", "Offer Accepted"}
)

-- MEASURE 3: Application Conversion Rate
Conversion Rate % = 
DIVIDE(
    CALCULATE(COUNTROWS(applications), 
              applications[status] = "Offer Accepted"),
    COUNTROWS(applications),
    0
) * 100

-- MEASURE 4: MoM Application Growth
MoM Growth % = 
VAR CurrentMonth = CALCULATE(COUNTROWS(applications), 
    DATESMTD(applications[application_date]))
VAR PrevMonth = CALCULATE(COUNTROWS(applications), 
    PREVIOUSMONTH(applications[application_date]))
RETURN
DIVIDE(CurrentMonth - PrevMonth, PrevMonth, 0) * 100

-- MEASURE 5: Placement Rate by Branch (for ranking)
Branch Placement Rank = 
RANKX(
    ALL(students[branch]),
    CALCULATE([Placement Rate %]),
    ,
    DESC,
    DENSE
)

-- MEASURE 6: Shortlisting Efficiency
Shortlist Rate % = 
DIVIDE(
    CALCULATE(COUNTROWS(applications), 
              applications[status] <> "Applied"),
    COUNTROWS(applications),
    0
) * 100

-- MEASURE 7: Days to Placement (avg)
Avg Days to Offer = 
AVERAGE(applications[days_to_offer])

-- MEASURE 8: YTD Revenue (Packages)
YTD Package Value Cr = 
CALCULATE(
    SUMX(applications, applications[package_offered_lpa]),
    DATESYTD(applications[offer_date])
) / 100  -- Convert LPA to Crore

-- MEASURE 9: Unplaced Students Count
Unplaced Students = 
CALCULATE(
    DISTINCTCOUNT(students[student_id]),
    NOT(students[student_id] IN 
        CALCULATETABLE(VALUES(applications[student_id]),
                       applications[status] = "Offer Accepted"))
)

-- MEASURE 10: Skill-Placement Correlation
Top Skill Placement Boost = 
VAR PythonPlaced = CALCULATE([Placement Rate %], 
    FILTER(students, CONTAINSSTRING(students[skills], "Python")))
VAR Overall = [Placement Rate %]
RETURN PythonPlaced - Overall
```

---

## POWER BI DESIGN GUIDELINES

### Color Theme (Dark Professional)
- Background: #0F1117
- Card Background: #1A1D2E
- Primary Accent: #00D4FF (Teal/Cyan)
- Positive: #00FF9F (Green)
- Negative: #FF6B6B (Red)
- Warning: #FFD700 (Gold)
- Text Primary: #E0E0E0
- Text Secondary: #AAAAAA

### Data Model Relationships
```
students (1) ──── (many) applications
companies (1) ──── (many) applications
applications (1) ──── (many) interviews
```

### Performance Tips
1. Import mode (not DirectQuery) for <1M rows
2. Create Date table for time intelligence
3. Disable Auto-date/time
4. Aggregate measures in DAX not in data source
5. Use star schema (avoid many-to-many)

---

## TOOLTIPS DESIGN

**Student Card Tooltip** (hover on scatter point):
- Student Name
- CGPA
- Branch
- Skills (top 3)
- Status

**Company Profile Tooltip:**
- Sector
- Package Range
- Selection Rate %
- Visit Date

---

## DRILL-THROUGH SETUP

Right-click on any branch bar → Drill-through to:
- All students in that branch
- Their application history
- Average scores

---

## BOOKMARK ACTIONS

| Bookmark | Purpose |
|----------|---------|
| Overview | Reset all filters |
| Unplaced Students | Filter: not placed |
| IT Sector | Filter: IT companies |
| Top Packages | Filter: >15 LPA |

