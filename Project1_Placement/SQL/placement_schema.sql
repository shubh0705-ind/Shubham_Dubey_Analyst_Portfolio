-- ============================================================
-- PROJECT 1: PLACEMENT MANAGEMENT ANALYTICS SYSTEM
-- Database: PostgreSQL / SQL Server Compatible
-- Author: Shubham Dubey (MCA Student - BVICAM, GGSIPU)
-- ============================================================

-- ============================================================
-- SCHEMA CREATION
-- ============================================================
CREATE SCHEMA IF NOT EXISTS placement_db;

-- ============================================================
-- TABLE 1: STUDENTS
-- ============================================================
CREATE TABLE placement_db.students (
    student_id      VARCHAR(10)     PRIMARY KEY,
    name            VARCHAR(100)    NOT NULL,
    email           VARCHAR(150)    UNIQUE NOT NULL,
    phone           VARCHAR(20),
    college         VARCHAR(150)    NOT NULL,
    branch          VARCHAR(50)     NOT NULL,
    cgpa            DECIMAL(4,2)    NOT NULL CHECK (cgpa BETWEEN 0 AND 10),
    backlogs        INT             DEFAULT 0 CHECK (backlogs >= 0),
    internships_count INT           DEFAULT 0,
    projects_count  INT             DEFAULT 1,
    skills          TEXT,           -- Pipe-separated: Python|SQL|Power BI
    certifications  INT             DEFAULT 0,
    passout_year    INT             NOT NULL,
    gap_year        SMALLINT        DEFAULT 0 CHECK (gap_year IN (0,1)),
    github_profile  SMALLINT        DEFAULT 0 CHECK (github_profile IN (0,1)),
    linkedin_profile SMALLINT       DEFAULT 0 CHECK (linkedin_profile IN (0,1)),
    city            VARCHAR(100),
    state           VARCHAR(100),
    created_at      TIMESTAMP       DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- TABLE 2: COMPANIES
-- ============================================================
CREATE TABLE placement_db.companies (
    company_id      VARCHAR(10)     PRIMARY KEY,
    company_name    VARCHAR(200)    NOT NULL,
    sector          VARCHAR(100)    NOT NULL,
    company_size    VARCHAR(50)     CHECK (company_size IN ('Startup','SME','MNC','Enterprise')),
    min_cgpa        DECIMAL(3,1),
    allows_backlogs SMALLINT        DEFAULT 0,
    package_min_lpa DECIMAL(6,2),
    package_max_lpa DECIMAL(6,2),
    bond_years      INT             DEFAULT 0,
    required_skills TEXT,
    branches_eligible TEXT,
    visit_date      DATE,
    city            VARCHAR(100),
    work_mode       VARCHAR(20)     CHECK (work_mode IN ('Onsite','Hybrid','Remote')),
    created_at      TIMESTAMP       DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- TABLE 3: APPLICATIONS
-- ============================================================
CREATE TABLE placement_db.applications (
    application_id  VARCHAR(12)     PRIMARY KEY,
    student_id      VARCHAR(10)     NOT NULL REFERENCES placement_db.students(student_id) ON DELETE CASCADE,
    company_id      VARCHAR(10)     NOT NULL REFERENCES placement_db.companies(company_id),
    application_date DATE           NOT NULL,
    status          VARCHAR(30)     CHECK (status IN ('Applied','Shortlisted','Interview Scheduled',
                                    'Interviewed','Selected','Rejected','Offer Accepted','Offer Declined')),
    round_cleared   INT             DEFAULT 0,
    interview_score DECIMAL(5,2),
    package_offered_lpa DECIMAL(6,2),
    offer_date      DATE,
    joining_date    DATE,
    created_at      TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (student_id, company_id)
);

-- ============================================================
-- TABLE 4: INTERVIEWS
-- ============================================================
CREATE TABLE placement_db.interviews (
    interview_id    VARCHAR(12)     PRIMARY KEY,
    application_id  VARCHAR(12)     NOT NULL REFERENCES placement_db.applications(application_id),
    round_number    INT             NOT NULL,
    interview_type  VARCHAR(50)     CHECK (interview_type IN ('Aptitude','Technical','HR',
                                    'Group Discussion','Case Study','Coding')),
    score           DECIMAL(5,2),
    result          VARCHAR(20)     CHECK (result IN ('Pass','Fail','On Hold')),
    interviewer_feedback TEXT,
    duration_minutes INT,
    created_at      TIMESTAMP       DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================
CREATE INDEX idx_students_branch       ON placement_db.students(branch);
CREATE INDEX idx_students_cgpa         ON placement_db.students(cgpa);
CREATE INDEX idx_students_college      ON placement_db.students(college);
CREATE INDEX idx_applications_status   ON placement_db.applications(status);
CREATE INDEX idx_applications_student  ON placement_db.applications(student_id);
CREATE INDEX idx_applications_company  ON placement_db.applications(company_id);
CREATE INDEX idx_interviews_app        ON placement_db.interviews(application_id);

