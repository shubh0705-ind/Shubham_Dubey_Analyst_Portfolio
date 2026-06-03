# Phase 1: Business Understanding
## Project 1 — Placement Management Analytics System

---

## BUSINESS PROBLEM

Colleges and universities manage thousands of students and hundreds of recruiting companies each placement season. Without a centralized analytics system, placement cells rely on manual spreadsheets, miss pipeline bottlenecks, cannot identify at-risk students, and have no visibility into historical performance trends.

**Core problems:**
- No single source of truth for student-company interaction data
- Placement coordinators cannot predict which students are likely to be placed
- No tracking of company visit conversion rates
- Cannot compare batch-over-batch performance
- Cannot identify which skills are driving placement success

---

## WHY COMPANIES NEED THIS

| Stakeholder | Need |
|---|---|
| Placement Cell Director | Track KPIs, report to management, identify trends |
| Placement Coordinator | Manage daily application flow, schedule interviews |
| Student | Know where they stand in the pipeline |
| College Management | Benchmark against peer institutions |
| Recruiting Company | Identify best-fit candidates quickly |

---

## BUSINESS OBJECTIVES

1. **Centralize** all placement data into one structured database
2. **Visualize** placement pipeline using interactive dashboards
3. **Predict** student placement probability using ML
4. **Identify** top-performing skills and attributes
5. **Benchmark** company conversion rates
6. **Automate** reporting for management (replace manual Excel reports)
7. **Reduce** unplaced student count by early identification and intervention

---

## KEY PERFORMANCE INDICATORS (KPIs)

| KPI | Definition | Target |
|-----|-----------|--------|
| Overall Placement Rate | Placed / Total Eligible × 100 | >85% |
| Avg Package Offered | Mean CTC of all offers | >12 LPA |
| Highest Package | Max CTC in the batch | >40 LPA |
| Application-to-Shortlist Rate | Shortlisted / Applied × 100 | >40% |
| Shortlist-to-Offer Rate | Offers / Shortlisted × 100 | >30% |
| Avg Days to Placement | Offer Date − Application Date | <60 days |
| Offer Acceptance Rate | Accepted / Offered × 100 | >80% |
| Branch Placement Parity | Std Dev of branch placement rates | <10% |
| Unplaced Student Count | Students with no offer | Minimize |
| Company Return Rate | % companies visiting 2+ years | >60% |

---

## EXPECTED BUSINESS IMPACT

- **30% reduction** in manual reporting time (replace Excel trackers)
- **~40% improvement** in shortlisting efficiency through CGPA/skill filters
- **Early intervention** for at-risk students identified 3 months before placement
- **Data-driven company targeting** — prioritize companies with higher selection rates
- **Benchmark capability** — compare with national placement averages

---

## DATA DICTIONARY

### students table
| Column | Type | Description |
|--------|------|-------------|
| student_id | VARCHAR(10) | Primary key, format STU00001 |
| cgpa | DECIMAL(4,2) | Cumulative GPA on 10-point scale |
| backlogs | INT | Active backlog subjects (0 = none) |
| internships_count | INT | Number of internships completed |
| composite_score | FLOAT | Derived: cgpa×5 + internships×8 + certs×3 − backlogs×10 |

### applications table
| Column | Type | Description |
|--------|------|-------------|
| status | VARCHAR | Pipeline stage: Applied → Offer Accepted |
| package_offered_lpa | DECIMAL | CTC in Lakhs Per Annum (NULL if not selected) |
| interview_score | DECIMAL | Average score across all interview rounds |

