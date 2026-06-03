-- ============================================================
-- PROJECT 1: 35 INTERVIEW-QUALITY SQL ANALYTICS QUERIES
-- Placement Management Analytics System
-- Author: Shubham Dubey | MCA - BVICAM GGSIPU
-- ============================================================

USE placement_db;

-- ============================================================
-- SECTION A: BASIC ANALYTICS (Queries 1–7)
-- ============================================================

-- Q1. Overall Placement Rate by Branch
-- Business: Which branch has the highest placement success?
SELECT
    s.branch,
    COUNT(DISTINCT s.student_id)                         AS total_students,
    COUNT(DISTINCT CASE WHEN a.status = 'Offer Accepted'
                   THEN s.student_id END)                AS placed_students,
    ROUND(COUNT(DISTINCT CASE WHEN a.status = 'Offer Accepted'
               THEN s.student_id END) * 100.0
          / COUNT(DISTINCT s.student_id), 2)             AS placement_rate_pct
FROM students s
LEFT JOIN applications a ON s.student_id = a.student_id
GROUP BY s.branch
ORDER BY placement_rate_pct DESC;

-- Q2. Top 10 Recruiting Companies by Number of Offers
SELECT
    c.company_name,
    c.sector,
    c.company_size,
    COUNT(a.application_id)                              AS total_applications,
    COUNT(CASE WHEN a.status = 'Offer Accepted' THEN 1 END) AS offers_accepted,
    ROUND(AVG(a.package_offered_lpa),2)                  AS avg_package_lpa
FROM companies c
JOIN applications a ON c.company_id = a.company_id
WHERE a.status = 'Offer Accepted'
GROUP BY c.company_name, c.sector, c.company_size
ORDER BY offers_accepted DESC
LIMIT 10;

-- Q3. CGPA Band Analysis: Placement Success vs Academic Performance
SELECT
    CASE
        WHEN cgpa >= 9.0 THEN '9.0-10.0 (Distinction)'
        WHEN cgpa >= 8.0 THEN '8.0-8.9 (Excellent)'
        WHEN cgpa >= 7.0 THEN '7.0-7.9 (Good)'
        WHEN cgpa >= 6.0 THEN '6.0-6.9 (Average)'
        ELSE 'Below 6.0 (Below Average)'
    END                                                  AS cgpa_band,
    COUNT(DISTINCT s.student_id)                         AS total_students,
    COUNT(DISTINCT CASE WHEN a.status = 'Offer Accepted'
                   THEN s.student_id END)                AS placed,
    ROUND(AVG(a.package_offered_lpa),2)                  AS avg_package_lpa,
    ROUND(COUNT(DISTINCT CASE WHEN a.status = 'Offer Accepted'
               THEN s.student_id END) * 100.0 /
          COUNT(DISTINCT s.student_id), 2)               AS placement_pct
FROM students s
LEFT JOIN applications a ON s.student_id = a.student_id
GROUP BY cgpa_band
ORDER BY MIN(s.cgpa) DESC;

-- Q4. Company Sector-wise Average Package Offered
SELECT
    c.sector,
    COUNT(DISTINCT c.company_id)                         AS companies_count,
    ROUND(AVG(a.package_offered_lpa), 2)                 AS avg_package_lpa,
    ROUND(MIN(a.package_offered_lpa), 2)                 AS min_package_lpa,
    ROUND(MAX(a.package_offered_lpa), 2)                 AS max_package_lpa,
    COUNT(CASE WHEN a.status = 'Offer Accepted' THEN 1 END) AS total_joiners
FROM companies c
JOIN applications a ON c.company_id = a.company_id
WHERE a.package_offered_lpa IS NOT NULL
GROUP BY c.sector
ORDER BY avg_package_lpa DESC;

-- Q5. Monthly Application Trend (Time Series)
SELECT
    DATE_FORMAT(application_date, '%Y-%m')               AS month,
    COUNT(application_id)                                AS total_applications,
    COUNT(CASE WHEN status = 'Selected' THEN 1 END)      AS selected,
    COUNT(CASE WHEN status = 'Rejected' THEN 1 END)      AS rejected,
    COUNT(CASE WHEN status = 'Offer Accepted' THEN 1 END) AS offers_accepted
FROM applications
GROUP BY DATE_FORMAT(application_date, '%Y-%m')
ORDER BY month;

-- Q6. Students With Multiple Offers (Premium Candidates)
SELECT
    s.student_id,
    s.name,
    s.branch,
    s.cgpa,
    COUNT(a.application_id)                              AS offers_received,
    ROUND(MAX(a.package_offered_lpa),2)                  AS highest_package_lpa,
    ROUND(AVG(a.package_offered_lpa),2)                  AS avg_package_lpa
FROM students s
JOIN applications a ON s.student_id = a.student_id
WHERE a.status IN ('Selected','Offer Accepted')
GROUP BY s.student_id, s.name, s.branch, s.cgpa
HAVING COUNT(a.application_id) > 1
ORDER BY offers_received DESC, highest_package_lpa DESC;

-- Q7. Unplaced Students Profile (for counselling)
SELECT
    s.student_id,
    s.name,
    s.branch,
    s.cgpa,
    s.backlogs,
    s.internships_count,
    s.skills,
    COUNT(a.application_id)                              AS total_applications,
    MAX(a.status)                                        AS last_status
FROM students s
LEFT JOIN applications a ON s.student_id = a.student_id
WHERE s.student_id NOT IN (
    SELECT DISTINCT student_id FROM applications
    WHERE status IN ('Selected','Offer Accepted')
)
GROUP BY s.student_id, s.name, s.branch, s.cgpa, s.backlogs, s.internships_count, s.skills
ORDER BY s.cgpa DESC;


-- ============================================================
-- SECTION B: JOINS & SUBQUERIES (Queries 8–14)
-- ============================================================

-- Q8. Application Funnel: Stage-wise Conversion Rates
SELECT
    a.status,
    COUNT(*)                                             AS count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2)   AS pct_of_total
FROM applications a
GROUP BY a.status
ORDER BY
    CASE a.status
        WHEN 'Applied' THEN 1
        WHEN 'Shortlisted' THEN 2
        WHEN 'Interview Scheduled' THEN 3
        WHEN 'Interviewed' THEN 4
        WHEN 'Selected' THEN 5
        WHEN 'Offer Accepted' THEN 6
        WHEN 'Offer Declined' THEN 7
        WHEN 'Rejected' THEN 8
    END;

-- Q9. Students Who Applied But Never Got Shortlisted
SELECT
    s.student_id,
    s.name,
    s.cgpa,
    s.branch,
    COUNT(a.application_id)                              AS applications_sent
FROM students s
JOIN applications a ON s.student_id = a.student_id
WHERE s.student_id NOT IN (
    SELECT student_id FROM applications
    WHERE status NOT IN ('Applied','Rejected')
)
GROUP BY s.student_id, s.name, s.cgpa, s.branch
HAVING COUNT(a.application_id) >= 3
ORDER BY applications_sent DESC;

-- Q10. Company Eligibility Gap Analysis
-- How many students are eligible but haven't applied?
SELECT
    c.company_id,
    c.company_name,
    c.sector,
    c.min_cgpa,
    COUNT(DISTINCT s.student_id)                         AS eligible_students,
    COUNT(DISTINCT a.student_id)                         AS students_applied,
    COUNT(DISTINCT s.student_id) - COUNT(DISTINCT a.student_id) AS opportunity_gap
FROM companies c
CROSS JOIN students s
LEFT JOIN applications a
    ON a.company_id = c.company_id AND a.student_id = s.student_id
WHERE s.cgpa >= c.min_cgpa
  AND (c.allows_backlogs = 1 OR s.backlogs = 0)
GROUP BY c.company_id, c.company_name, c.sector, c.min_cgpa
ORDER BY opportunity_gap DESC
LIMIT 20;

-- Q11. Interview Performance by Round Type
SELECT
    i.interview_type,
    COUNT(*)                                             AS total_interviews,
    ROUND(AVG(i.score), 2)                               AS avg_score,
    COUNT(CASE WHEN i.result = 'Pass' THEN 1 END)        AS pass_count,
    COUNT(CASE WHEN i.result = 'Fail' THEN 1 END)        AS fail_count,
    ROUND(COUNT(CASE WHEN i.result = 'Pass' THEN 1 END) * 100.0 / COUNT(*), 2) AS pass_rate_pct
FROM interviews i
GROUP BY i.interview_type
ORDER BY pass_rate_pct DESC;

-- Q12. Company-wise Interview Difficulty Index
SELECT
    c.company_name,
    c.sector,
    COUNT(DISTINCT i.interview_id)                       AS total_rounds_conducted,
    ROUND(AVG(i.score), 2)                               AS avg_interview_score,
    ROUND(AVG(i.duration_minutes), 0)                    AS avg_duration_mins,
    COUNT(CASE WHEN i.result = 'Fail' THEN 1 END) * 100.0 /
    NULLIF(COUNT(i.interview_id),0)                      AS fail_rate_pct
FROM companies c
JOIN applications a ON c.company_id = a.company_id
JOIN interviews i ON a.application_id = i.application_id
GROUP BY c.company_name, c.sector
HAVING COUNT(DISTINCT i.interview_id) >= 5
ORDER BY fail_rate_pct DESC;

-- Q13. Students With Internships vs Without: Placement Comparison
SELECT
    CASE WHEN s.internships_count = 0 THEN 'No Internship'
         WHEN s.internships_count = 1 THEN '1 Internship'
         WHEN s.internships_count = 2 THEN '2 Internships'
         ELSE '3+ Internships' END                       AS internship_group,
    COUNT(DISTINCT s.student_id)                         AS total_students,
    COUNT(DISTINCT CASE WHEN a.status = 'Offer Accepted'
                   THEN s.student_id END)                AS placed,
    ROUND(COUNT(DISTINCT CASE WHEN a.status = 'Offer Accepted'
               THEN s.student_id END) * 100.0 /
          COUNT(DISTINCT s.student_id), 2)               AS placement_rate_pct,
    ROUND(AVG(a.package_offered_lpa), 2)                 AS avg_package_lpa
FROM students s
LEFT JOIN applications a ON s.student_id = a.student_id
GROUP BY internship_group
ORDER BY internship_group;

-- Q14. Skills Impact on Placement Rate
SELECT
    skill_name,
    COUNT(DISTINCT s.student_id)                         AS students_with_skill,
    COUNT(DISTINCT CASE WHEN a.status = 'Offer Accepted'
                   THEN s.student_id END)                AS placed_with_skill,
    ROUND(COUNT(DISTINCT CASE WHEN a.status = 'Offer Accepted'
               THEN s.student_id END) * 100.0 /
          NULLIF(COUNT(DISTINCT s.student_id),0), 2)     AS placement_rate_pct
FROM students s
JOIN (
    SELECT student_id, TRIM(value) AS skill_name
    FROM students
    CROSS APPLY STRING_SPLIT(skills, '|')
) skill_breakdown ON s.student_id = skill_breakdown.student_id
LEFT JOIN applications a ON s.student_id = a.student_id
GROUP BY skill_name
ORDER BY placement_rate_pct DESC;


-- ============================================================
-- SECTION C: CTEs & WINDOW FUNCTIONS (Queries 15–22)
-- ============================================================

-- Q15. Rolling 3-Month Average of Applications
WITH monthly_apps AS (
    SELECT
        DATE_FORMAT(application_date,'%Y-%m')            AS month,
        COUNT(*)                                         AS app_count
    FROM applications
    GROUP BY DATE_FORMAT(application_date,'%Y-%m')
)
SELECT
    month,
    app_count,
    ROUND(AVG(app_count) OVER (
        ORDER BY month
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ), 2)                                                AS rolling_3m_avg
FROM monthly_apps
ORDER BY month;

-- Q16. Rank Students by Package Within Each Branch (RANK / DENSE_RANK)
WITH ranked_placements AS (
    SELECT
        s.student_id,
        s.name,
        s.branch,
        s.cgpa,
        a.package_offered_lpa,
        RANK() OVER (PARTITION BY s.branch ORDER BY a.package_offered_lpa DESC) AS rank_in_branch,
        DENSE_RANK() OVER (ORDER BY a.package_offered_lpa DESC)                 AS overall_rank
    FROM students s
    JOIN applications a ON s.student_id = a.student_id
    WHERE a.status = 'Offer Accepted'
)
SELECT * FROM ranked_placements
WHERE rank_in_branch <= 5
ORDER BY branch, rank_in_branch;

-- Q17. Student Journey Funnel Using CTE Chains
WITH all_stages AS (
    SELECT student_id, status, application_date FROM applications
),
latest_stage AS (
    SELECT
        student_id,
        status,
        ROW_NUMBER() OVER (PARTITION BY student_id ORDER BY
            CASE status
                WHEN 'Offer Accepted' THEN 8
                WHEN 'Offer Declined' THEN 7
                WHEN 'Selected' THEN 6
                WHEN 'Interviewed' THEN 5
                WHEN 'Interview Scheduled' THEN 4
                WHEN 'Shortlisted' THEN 3
                WHEN 'Applied' THEN 2
                WHEN 'Rejected' THEN 1
            END DESC) AS rn
    FROM all_stages
)
SELECT status, COUNT(*) AS students_at_stage
FROM latest_stage
WHERE rn = 1
GROUP BY status
ORDER BY
    CASE status WHEN 'Offer Accepted' THEN 1 WHEN 'Offer Declined' THEN 2 ELSE 3 END;

-- Q18. Percentile Distribution of Packages Offered
SELECT
    student_id,
    package_offered_lpa,
    NTILE(4) OVER (ORDER BY package_offered_lpa)         AS quartile,
    PERCENT_RANK() OVER (ORDER BY package_offered_lpa)   AS percentile_rank,
    ROUND(package_offered_lpa - AVG(package_offered_lpa)
          OVER(), 2)                                     AS deviation_from_avg
FROM applications
WHERE package_offered_lpa IS NOT NULL
ORDER BY package_offered_lpa DESC;

-- Q19. First vs Latest Application Performance Per Student
WITH student_apps AS (
    SELECT
        student_id,
        application_id,
        application_date,
        status,
        package_offered_lpa,
        ROW_NUMBER() OVER (PARTITION BY student_id ORDER BY application_date ASC)  AS rn_first,
        ROW_NUMBER() OVER (PARTITION BY student_id ORDER BY application_date DESC) AS rn_last
    FROM applications
)
SELECT
    f.student_id,
    f.status                                             AS first_app_status,
    l.status                                             AS latest_app_status,
    CASE WHEN l.package_offered_lpa > f.package_offered_lpa
         THEN 'Improved' ELSE 'Same/Declined' END        AS package_trend
FROM student_apps f
JOIN student_apps l ON f.student_id = l.student_id
WHERE f.rn_first = 1 AND l.rn_last = 1 AND f.application_id <> l.application_id;

-- Q20. Company Repeat Visit Analysis
SELECT
    company_id,
    company_name,
    sector,
    COUNT(DISTINCT YEAR(visit_date))                     AS years_visited,
    GROUP_CONCAT(YEAR(visit_date) ORDER BY visit_date)   AS visit_years,
    ROUND(AVG(package_max_lpa),2)                        AS avg_max_package
FROM companies
GROUP BY company_id, company_name, sector
HAVING COUNT(DISTINCT YEAR(visit_date)) >= 1
ORDER BY years_visited DESC;

-- Q21. Skill-to-Company Match Score
WITH student_skills AS (
    SELECT student_id, TRIM(value) AS skill
    FROM students
    CROSS APPLY STRING_SPLIT(skills, '|')
),
company_skills AS (
    SELECT company_id, TRIM(value) AS skill
    FROM companies
    CROSS APPLY STRING_SPLIT(required_skills, '|')
)
SELECT
    a.student_id,
    a.company_id,
    COUNT(DISTINCT ss.skill)                             AS matched_skills,
    COUNT(DISTINCT cs.skill)                             AS required_skills_total,
    ROUND(COUNT(DISTINCT ss.skill) * 100.0 /
          NULLIF(COUNT(DISTINCT cs.skill),0), 0)         AS skill_match_pct
FROM applications a
JOIN student_skills ss ON a.student_id = ss.student_id
JOIN company_skills cs ON a.company_id = cs.company_id AND ss.skill = cs.skill
GROUP BY a.student_id, a.company_id
ORDER BY skill_match_pct DESC;

-- Q22. Year-over-Year Placement Comparison
WITH yearly_stats AS (
    SELECT
        s.passout_year,
        COUNT(DISTINCT s.student_id)                     AS total_students,
        COUNT(DISTINCT CASE WHEN a.status = 'Offer Accepted'
                       THEN s.student_id END)            AS placed,
        ROUND(AVG(a.package_offered_lpa), 2)             AS avg_package
    FROM students s
    LEFT JOIN applications a ON s.student_id = a.student_id
    GROUP BY s.passout_year
)
SELECT
    passout_year,
    total_students,
    placed,
    avg_package,
    placed - LAG(placed) OVER (ORDER BY passout_year)   AS yoy_change,
    ROUND((avg_package - LAG(avg_package) OVER (ORDER BY passout_year)) * 100.0 /
          NULLIF(LAG(avg_package) OVER (ORDER BY passout_year), 0), 2) AS avg_package_growth_pct
FROM yearly_stats;


-- ============================================================
-- SECTION D: KPI BUSINESS QUERIES (Queries 23–35)
-- ============================================================

-- Q23. Executive KPI Dashboard Query
SELECT
    COUNT(DISTINCT s.student_id)                         AS total_registered_students,
    COUNT(DISTINCT c.company_id)                         AS total_companies,
    COUNT(DISTINCT a.application_id)                     AS total_applications,
    COUNT(DISTINCT CASE WHEN a.status = 'Offer Accepted'
                   THEN s.student_id END)                AS placed_students,
    ROUND(COUNT(DISTINCT CASE WHEN a.status = 'Offer Accepted'
               THEN s.student_id END) * 100.0 /
          COUNT(DISTINCT s.student_id), 2)               AS overall_placement_pct,
    ROUND(AVG(CASE WHEN a.status = 'Offer Accepted'
              THEN a.package_offered_lpa END), 2)        AS avg_package_lpa,
    ROUND(MAX(a.package_offered_lpa), 2)                 AS highest_package_lpa,
    ROUND(MIN(CASE WHEN a.status = 'Offer Accepted'
              THEN a.package_offered_lpa END), 2)        AS lowest_package_lpa
FROM students s
LEFT JOIN applications a ON s.student_id = a.student_id
LEFT JOIN companies c ON a.company_id = c.company_id;

-- Q24. Placement Cell Efficiency: Time from Application to Offer
SELECT
    c.company_name,
    c.sector,
    ROUND(AVG(DATEDIFF(a.offer_date, a.application_date)), 0) AS avg_days_to_offer,
    MIN(DATEDIFF(a.offer_date, a.application_date))      AS min_days,
    MAX(DATEDIFF(a.offer_date, a.application_date))      AS max_days,
    COUNT(*)                                             AS total_offers
FROM applications a
JOIN companies c ON a.company_id = c.company_id
WHERE a.offer_date IS NOT NULL AND a.application_date IS NOT NULL
GROUP BY c.company_name, c.sector
ORDER BY avg_days_to_offer ASC;

-- Q25. Offer Decline Analysis: Lost Opportunities
SELECT
    s.branch,
    s.college,
    COUNT(CASE WHEN a.status = 'Offer Declined' THEN 1 END)  AS declined_offers,
    ROUND(AVG(CASE WHEN a.status = 'Offer Declined'
              THEN a.package_offered_lpa END), 2)            AS avg_declined_package,
    COUNT(CASE WHEN a.status = 'Offer Accepted' THEN 1 END)  AS accepted_offers,
    ROUND(COUNT(CASE WHEN a.status = 'Offer Declined' THEN 1 END) * 100.0 /
          NULLIF(COUNT(CASE WHEN a.status IN ('Offer Accepted','Offer Declined') THEN 1 END),0), 2)
                                                             AS decline_rate_pct
FROM students s
JOIN applications a ON s.student_id = a.student_id
WHERE a.status IN ('Offer Accepted','Offer Declined')
GROUP BY s.branch, s.college
ORDER BY decline_rate_pct DESC;

-- Q26. Cohort Analysis: Placement Rate by CGPA and Branch Matrix
SELECT
    branch,
    ROUND(AVG(CASE WHEN cgpa_band='9+' THEN placement_flag END)*100,1) AS placed_9plus_pct,
    ROUND(AVG(CASE WHEN cgpa_band='8-9' THEN placement_flag END)*100,1) AS placed_8to9_pct,
    ROUND(AVG(CASE WHEN cgpa_band='7-8' THEN placement_flag END)*100,1) AS placed_7to8_pct,
    ROUND(AVG(CASE WHEN cgpa_band='6-7' THEN placement_flag END)*100,1) AS placed_6to7_pct,
    ROUND(AVG(CASE WHEN cgpa_band='<6'  THEN placement_flag END)*100,1) AS placed_below6_pct
FROM (
    SELECT
        s.student_id,
        s.branch,
        CASE WHEN s.cgpa >= 9 THEN '9+'
             WHEN s.cgpa >= 8 THEN '8-9'
             WHEN s.cgpa >= 7 THEN '7-8'
             WHEN s.cgpa >= 6 THEN '6-7'
             ELSE '<6' END                               AS cgpa_band,
        MAX(CASE WHEN a.status = 'Offer Accepted' THEN 1 ELSE 0 END) AS placement_flag
    FROM students s
    LEFT JOIN applications a ON s.student_id = a.student_id
    GROUP BY s.student_id, s.branch, cgpa_band
) t
GROUP BY branch
ORDER BY branch;

-- Q27. Gender-wise (proxy: name-based) Placement Insights
SELECT
    s.passout_year,
    s.college,
    COUNT(DISTINCT s.student_id)                         AS students,
    ROUND(AVG(s.cgpa),2)                                 AS avg_cgpa,
    COUNT(DISTINCT CASE WHEN a.status = 'Offer Accepted'
                   THEN s.student_id END)                AS placed,
    ROUND(COUNT(DISTINCT CASE WHEN a.status = 'Offer Accepted'
               THEN s.student_id END) * 100.0 /
          COUNT(DISTINCT s.student_id), 2)               AS placement_pct,
    ROUND(AVG(CASE WHEN a.status='Offer Accepted'
              THEN a.package_offered_lpa END),2)         AS avg_ctc_lpa
FROM students s
LEFT JOIN applications a ON s.student_id = a.student_id
GROUP BY s.passout_year, s.college
ORDER BY s.passout_year, placement_pct DESC;

-- Q28. Top Performing Students: Composite Score
SELECT
    s.student_id,
    s.name,
    s.branch,
    s.cgpa,
    s.internships_count,
    s.certifications,
    s.projects_count,
    s.github_profile + s.linkedin_profile                AS online_presence,
    ROUND(
        (s.cgpa * 5) +
        (s.internships_count * 8) +
        (s.certifications * 3) +
        (s.projects_count * 4) +
        ((s.github_profile + s.linkedin_profile) * 2) -
        (s.backlogs * 10) -
        (s.gap_year * 5), 2
    )                                                    AS composite_score,
    CASE WHEN a.status = 'Offer Accepted' THEN 'Placed' ELSE 'Unplaced' END AS placement_status
FROM students s
LEFT JOIN applications a ON s.student_id = a.student_id
    AND a.status = 'Offer Accepted'
ORDER BY composite_score DESC
LIMIT 50;

-- Q29. Company Shortlisting Efficiency
SELECT
    c.company_name,
    c.sector,
    COUNT(a.application_id)                              AS applications_received,
    COUNT(CASE WHEN a.status != 'Applied' THEN 1 END)    AS shortlisted,
    COUNT(CASE WHEN a.status IN ('Selected','Offer Accepted') THEN 1 END) AS selected,
    ROUND(COUNT(CASE WHEN a.status != 'Applied' THEN 1 END) * 100.0 /
          NULLIF(COUNT(a.application_id),0), 1)          AS shortlist_rate_pct,
    ROUND(COUNT(CASE WHEN a.status IN ('Selected','Offer Accepted') THEN 1 END) * 100.0 /
          NULLIF(COUNT(a.application_id),0), 1)          AS selection_rate_pct
FROM companies c
JOIN applications a ON c.company_id = a.company_id
GROUP BY c.company_name, c.sector
HAVING COUNT(a.application_id) >= 10
ORDER BY selection_rate_pct DESC;

-- Q30. Interview Round Progression Rates
SELECT
    i.round_number,
    i.interview_type,
    COUNT(*)                                             AS students_reached_round,
    COUNT(CASE WHEN i.result = 'Pass' THEN 1 END)        AS passed,
    ROUND(COUNT(CASE WHEN i.result = 'Pass' THEN 1 END) * 100.0 / COUNT(*), 2) AS pass_rate_pct,
    ROUND(AVG(i.score), 2)                               AS avg_score,
    ROUND(AVG(i.duration_minutes), 0)                    AS avg_duration_mins
FROM interviews i
GROUP BY i.round_number, i.interview_type
ORDER BY i.round_number, pass_rate_pct DESC;

-- Q31. Top Hiring Sectors vs Student Branch Demand Analysis
WITH sector_demand AS (
    SELECT
        c.sector,
        COUNT(a.application_id)                          AS total_applications,
        COUNT(CASE WHEN a.status = 'Offer Accepted' THEN 1 END) AS offers_made
    FROM companies c
    JOIN applications a ON c.company_id = a.company_id
    GROUP BY c.sector
),
branch_supply AS (
    SELECT branch, COUNT(*) AS total_students
    FROM students
    GROUP BY branch
)
SELECT
    sd.sector,
    sd.total_applications,
    sd.offers_made,
    ROUND(sd.offers_made * 100.0 / NULLIF(sd.total_applications,0), 2) AS sector_conversion_pct
FROM sector_demand sd
ORDER BY offers_made DESC;

-- Q32. Batch Comparison: 2024 vs 2025 Batch
SELECT
    passout_year                                         AS batch,
    COUNT(DISTINCT s.student_id)                         AS total,
    ROUND(AVG(s.cgpa),2)                                 AS avg_cgpa,
    COUNT(DISTINCT CASE WHEN a.status = 'Offer Accepted'
                   THEN s.student_id END)                AS placed,
    ROUND(AVG(CASE WHEN a.status='Offer Accepted'
              THEN a.package_offered_lpa END),2)         AS avg_package_lpa
FROM students s
LEFT JOIN applications a ON s.student_id = a.student_id
GROUP BY passout_year;

-- Q33. Skill Gap Analysis: What skills placed students have vs unplaced
WITH placed_skills AS (
    SELECT TRIM(value) AS skill, 'Placed' AS group_label, COUNT(*) AS cnt
    FROM students s
    CROSS APPLY STRING_SPLIT(s.skills,'|')
    WHERE s.student_id IN (
        SELECT DISTINCT student_id FROM applications WHERE status = 'Offer Accepted')
    GROUP BY TRIM(value)
),
unplaced_skills AS (
    SELECT TRIM(value) AS skill, 'Unplaced' AS group_label, COUNT(*) AS cnt
    FROM students s
    CROSS APPLY STRING_SPLIT(s.skills,'|')
    WHERE s.student_id NOT IN (
        SELECT DISTINCT student_id FROM applications WHERE status = 'Offer Accepted')
    GROUP BY TRIM(value)
)
SELECT
    COALESCE(p.skill, u.skill)                           AS skill,
    COALESCE(p.cnt, 0)                                   AS placed_count,
    COALESCE(u.cnt, 0)                                   AS unplaced_count,
    COALESCE(p.cnt,0) - COALESCE(u.cnt,0)                AS advantage_for_placed
FROM placed_skills p
FULL OUTER JOIN unplaced_skills u ON p.skill = u.skill
ORDER BY advantage_for_placed DESC;

-- Q34. Predictive Score: Placement Probability (Rule-based)
SELECT
    student_id,
    name,
    branch,
    cgpa,
    CASE
        WHEN cgpa >= 8.5 AND internships_count >= 2 AND backlogs = 0 THEN 'Very High (>85%)'
        WHEN cgpa >= 7.5 AND internships_count >= 1 AND backlogs = 0 THEN 'High (65-85%)'
        WHEN cgpa >= 6.5 AND backlogs <= 1 THEN 'Medium (40-65%)'
        WHEN cgpa >= 6.0 THEN 'Low (20-40%)'
        ELSE 'Very Low (<20%)'
    END                                                  AS placement_probability,
    ROUND(
        CASE
            WHEN cgpa >= 8.5 AND internships_count >= 2 AND backlogs = 0 THEN 90
            WHEN cgpa >= 7.5 AND internships_count >= 1 AND backlogs = 0 THEN 75
            WHEN cgpa >= 6.5 AND backlogs <= 1 THEN 52
            WHEN cgpa >= 6.0 THEN 30
            ELSE 15
        END, 0)                                          AS estimated_placement_pct
FROM students
ORDER BY estimated_placement_pct DESC;

-- Q35. Final Placement Cell Dashboard: KPIs for Management
SELECT
    'Total Students'                                     AS kpi, COUNT(DISTINCT student_id)::TEXT AS value FROM students
UNION ALL SELECT 'Total Companies', COUNT(DISTINCT company_id)::TEXT FROM companies
UNION ALL SELECT 'Total Applications', COUNT(DISTINCT application_id)::TEXT FROM applications
UNION ALL SELECT 'Offers Accepted', COUNT(*)::TEXT FROM applications WHERE status='Offer Accepted'
UNION ALL SELECT 'Overall Placement %', ROUND(
    (SELECT COUNT(*) FROM applications WHERE status='Offer Accepted') * 100.0 /
    NULLIF((SELECT COUNT(DISTINCT student_id) FROM students),0), 2)::TEXT
UNION ALL SELECT 'Average Package (LPA)', ROUND(AVG(package_offered_lpa),2)::TEXT
    FROM applications WHERE status='Offer Accepted'
UNION ALL SELECT 'Highest Package (LPA)', MAX(package_offered_lpa)::TEXT
    FROM applications WHERE package_offered_lpa IS NOT NULL;
