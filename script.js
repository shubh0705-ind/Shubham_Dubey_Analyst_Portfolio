// ==========================================================================
// PORTFOLIO DATABASE & INTERACTIVITY ENGINE
// ==========================================================================

const projectData = {
    p1: {
        domain: "Education / HR Analytics",
        title: "Placement Management Analytics System",
        summary: "A 4-table PostgreSQL database combined with Python EDA, Random Forest classifiers, and a Power BI executive dashboard to predict student placement outcomes 12 months in advance.",
        overview: {
            problem: "Academic placement tracking was completely manual and spreadsheet-reliant, lacking predictive analysis. The institution could not identify at-risk students who needed targeted skills support before final placement drives commenced.",
            solution: "Created a schema-validated PostgreSQL database tracking 46,000+ records. Built a predictive pipeline utilizing Random Forest, logistic regression, and Gradient Boosting models, backed by an executive Power BI dashboard showing current pipeline rates and predictions.",
            highlights: [
                "<strong>86.4% ML Accuracy:</strong> Achieved by Random Forest Classifier to identify at-risk students 12 months ahead.",
                "<strong>₹6.4 LPA Average Package:</strong> Tracked across branches with full pipeline transparency.",
                "<strong>30% Reporting Efficiency:</strong> Saved academic heads hours of manual dashboard synthesis.",
                "<strong>Feature Importance Analysis:</strong> Uncovered that internship count and CGPA are the top 2 indicators of success."
            ],
            tech: ["Python", "Pandas", "Scikit-Learn", "PostgreSQL", "Power BI", "DAX", "SQL Server"]
        },
        visuals: [
            {
                src: "Project1_Placement/Images/P1_executive_dashboard.png",
                caption: "Executive Placement Dashboard",
                sub: "Power BI view highlighting key KPIs, branch-wise placements, application funnel stages, and top technical skills."
            },
            {
                src: "Project1_Placement/Images/P1_cgpa_analysis.png",
                caption: "Academic CGPA & Placement Analytics",
                sub: "Distribution analysis of placed/unplaced students, placement rate by CGPA band, and composite score rankings."
            },
            {
                src: "Project1_Placement/Images/P1_ml_model_results.png",
                caption: "Machine Learning Model Performance",
                sub: "Confusion matrix, ROC curves, and feature importance scores for placement prediction (Random Forest vs Logistic Regression)."
            }
        ],
        sql: {
            desc: "The schema is modeled as a star schema to optimize analytic queries. Below is the SQL script illustrating table creation, relationships, and indexes optimized for placement funnel throughput.",
            code: `-- SCHEMA CREATION
CREATE SCHEMA IF NOT EXISTS placement_db;

-- TABLE 1: STUDENTS (Star Schema Dimension)
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
    created_at      TIMESTAMP       DEFAULT CURRENT_TIMESTAMP
);

-- INDEXES FOR QUICK FILTERING
CREATE INDEX idx_students_branch       ON placement_db.students(branch);
CREATE INDEX idx_students_cgpa         ON placement_db.students(cgpa);

-- ANALYTIC QUERY: Top Package & Placement Rate by Branch
SELECT
    branch,
    COUNT(*) AS total_students,
    ROUND(SUM(is_placed)*100.0/COUNT(*), 2) AS placement_rate_pct,
    ROUND(AVG(package_offered_lpa), 2) AS avg_package_lpa,
    MAX(package_offered_lpa) AS max_package_lpa
FROM (
    SELECT 
        s.branch,
        s.student_id,
        CASE WHEN a.status = 'Offer Accepted' THEN 1 ELSE 0 END AS is_placed,
        COALESCE(a.package_offered_lpa, 0) AS package_offered_lpa
    FROM placement_db.students s
    LEFT JOIN placement_db.applications a ON s.student_id = a.student_id
) sub
GROUP BY branch
ORDER BY placement_rate_pct DESC;`
        },
        python: {
            desc: "Python handles data cleaning, feature engineering, and predictive model training. Below is the machine learning training pipeline using Scikit-Learn to evaluate Random Forest Classifier vs Logistic Regression.",
            code: `import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, roc_auc_score

# 1. Feature Engineering
students = pd.read_csv('../Data/students.csv')
placed_ids = applications[applications['status'] == 'Offer Accepted']['student_id'].unique()
students['is_placed'] = students['student_id'].isin(placed_ids).astype(int)

# Create composite score
students['composite_score'] = (
    students['cgpa'] * 5 +
    students['internships_count'] * 8 +
    students['certifications'] * 3 +
    students['projects_count'] * 4 -
    students['backlogs'] * 10 -
    students['gap_year'] * 5
)

# Encode categorical branches
le = LabelEncoder()
students['branch_enc'] = le.fit_transform(students['branch'].fillna('Unknown'))

feature_cols = ['cgpa','backlogs','internships_count','projects_count',
                'certifications','gap_year','branch_enc','composite_score']
X = students[feature_cols]
y = students['is_placed']

# 2. Train-Test Split and Scale
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
scaler = StandardScaler()
X_train_sc = scaler.fit_transform(X_train)
X_test_sc = scaler.transform(X_test)

# 3. Random Forest Model
rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
rf_model.fit(X_train, y_train)
y_pred = rf_model.predict(X_test)

print(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}")
print(classification_report(y_test, y_pred))`
        },
        insights: [
            {
                title: "CGPA 7.5 Threshold Effect",
                desc: "Students with CGPA ≥ 7.5 are placed at 2.3× the rate of students below 7.0. The data shows a hard inflection point at 7.5, which is the minimum CGPA requirement for 78% of visiting companies. <em>Action: Introduce mandatory CGPA improvement tracks early in the curriculum.</em>"
            },
            {
                title: "Internship as Primary Predictor",
                desc: "Students with 2+ internships score a 67% placement rate vs 31% for those with zero. This holds the highest weight in Random Forest feature importance. <em>Action: Build industry partnerships to make at least one internship compulsory before the final year.</em>"
            },
            {
                title: "GitHub Portfolio Impact",
                desc: "Students with an active GitHub profile have a 22% higher placement rate. Recruiters increasingly screen code quality. <em>Action: Integrate Git and GitHub portfolio reviews as a placement cells criteria.</em>"
            },
            {
                title: "Technical Round Bottleneck",
                desc: "Data reveals that 62% of candidate rejections happen during the Technical Interview (Round 2). HR and Aptitude rounds pass at 73%+. <em>Action: Run weekly mock coding and technical interview sessions.</em>"
            }
        ],
        prep: [
            {
                q: "Why did you select Random Forest over Logistic Regression for this dataset?",
                a: "Random Forest can capture non-linear relationships and interactions between features (e.g., how backlogs impact students with high vs. low CGPAs differently) without requiring explicit interaction terms. It achieved a higher testing accuracy of 86.4% and handles multicollinearity between composite scores and sub-metrics naturally."
            },
            {
                q: "How does the Placement Cell use the 'Composite Score' in practice?",
                a: "The composite score acts as an early warning system. By calculating it at the start of the 3rd semester, the system flags students scoring below a threshold. This allows counselors to direct them to targeted technical bootcamps and resume-building workshops 12 months before company recruitment starts."
            }
        ]
    },
    p2: {
        domain: "NLP / Marketing Intelligence",
        title: "Sentiment & Brand Intelligence Dashboard",
        summary: "A 30,000-post Natural Language Processing pipeline evaluating brand reputation shifts across Twitter and Reddit for Samsung, Apple, and OnePlus using VADER, TextBlob, and LDA topic modeling.",
        overview: {
            problem: "Marketing teams had no systematic way to track competitors or detect product-specific crisis spikes before they escalated into viral reputation damage in search results.",
            solution: "Designed a text preprocessing pipeline connecting VADER and TextBlob as an ensemble classifier (82% accuracy) with LDA topic modeling to cluster complaints. Built a Power BI crisis warning dashboard using Z-score outlier detection on negative post volumes.",
            highlights: [
                "<strong>30,000 Posts Processed:</strong> Extracted, cleaned, and sentiment-scored from Twitter and Reddit.",
                "<strong>Ensemble Classifiers:</strong> Combined VADER and TextBlob to improve accuracy by 6.7% and better flag sarcastic comments.",
                "<strong>Z-Score Crisis Trigger:</strong> Detects daily negative post volume spikes (>2 SD from baseline) to issue 48hr early warnings.",
                "<strong>Unsupervised LDA Topics:</strong> Automatically surfaced top customer complaints (e.g., battery degradation, night mode photo noise)."
            ],
            tech: ["Python", "NLTK", "VADER", "TextBlob", "LDA Topic Modelling", "Scikit-Learn", "MySQL", "Power BI"]
        },
        visuals: [
            {
                src: "Project2_Sentiment/Images/P2_brand_intelligence_dashboard.png",
                caption: "Social Media Sentiment Dashboard",
                sub: "Overall sentiment distribution across Samsung, Apple, and OnePlus, monthly VADER trend lines, share-of-voice, and category engagement metrics."
            }
        ],
        sql: {
            desc: "Wrote 30 complex SQL queries in MySQL to analyze posts. Below is the query structure that performs engagement-weighted sentiment calculation and daily sentiment volatility tracking.",
            code: `-- Q12. Engagement-Weighted Sentiment Score (Captures true viral impact)
SELECT
    brand,
    post_month,
    ROUND(SUM(vader_score * (likes + shares * 3 + comments * 2)) /
          NULLIF(SUM(likes + shares * 3 + comments * 2), 0), 4) AS weighted_sentiment,
    ROUND(AVG(vader_score), 4)                                 AS simple_avg_sentiment,
    SUM(likes + shares + comments)                            AS total_engagement
FROM sentiment_db.posts
GROUP BY brand, post_month
ORDER BY brand, post_month;

-- Q11. Sentiment Spike Z-Score Outlier Detection (Crisis alert)
WITH daily_stats AS (
    SELECT 
        brand, 
        DATE(post_date) AS dt,
        AVG(vader_score) AS daily_score,
        COUNT(*) AS posts
    FROM sentiment_db.posts
    GROUP BY brand, DATE(post_date)
),
brand_baseline AS (
    SELECT 
        brand,
        AVG(daily_score) AS mean_score,
        STDDEV(daily_score) AS std_score
    FROM daily_stats 
    GROUP BY brand
)
SELECT 
    d.brand, d.dt, d.daily_score, d.posts,
    ROUND((d.daily_score - b.mean_score) / NULLIF(b.std_score, 0), 2) AS z_score,
    CASE WHEN ABS((d.daily_score - b.mean_score) / NULLIF(b.std_score, 0)) > 2
         THEN 'SPIKE ALERT' ELSE 'Normal' END AS alert_flag
FROM daily_stats d 
JOIN brand_baseline b ON d.brand = b.brand
ORDER BY z_score DESC;`
        },
        python: {
            desc: "The Python engine handles Lemmatization, TF-IDF vectorization, LDA modeling, and ensemble sentiment scoring. Below is the text preprocessor and VADER classification pipeline.",
            code: `import re
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Text Preprocessing Pipeline
stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

def clean_text(text):
    text = str(text).lower()
    text = re.sub(r'http\\S+|www\\S+', '', text)    # Strip URLs
    text = re.sub(r'@\\w+|#\\w+', '', text)         # Strip Mentions
    text = re.sub(r'[^\\w\\s]', '', text)            # Strip Punctuation
    tokens = [lemmatizer.lemmatize(w) for w in text.split() 
              if w not in stop_words and len(w) > 2]
    return ' '.join(tokens)

# Ensemble Sentiment Predictor
analyzer = SentimentIntensityAnalyzer()

def predict_sentiment(row):
    vader_comp = analyzer.polarity_scores(row['text'])['compound']
    tb_pol = TextBlob(row['text']).sentiment.polarity
    
    # Combined scoring logic
    scores = []
    scores.append(1 if vader_comp >= 0.05 else -1 if vader_comp <= -0.05 else 0)
    scores.append(1 if tb_pol > 0.1 else -1 if tb_pol < -0.1 else 0)
    
    avg_score = sum(scores) / len(scores)
    return 'Positive' if avg_score > 0 else 'Negative' if avg_score < 0 else 'Neutral'`
        },
        insights: [
            {
                title: "Reddit Holds High Reputation Risk",
                desc: "Reddit negative sentiment rate (34.1%) is higher than Twitter (28.6%). Reddit posts are longer, index in Google search, and carry longer-term damage. <em>Action: Assign community moderators to respond directly to highly engaged threads in r/samsung, r/apple, and r/oneplus subreddits.</em>"
            },
            {
                title: "Camera is the #1 Complaint Category",
                desc: "Across all brands, camera-related topics account for 31% of negative posts. The top themes surfaced are night mode photo noise and overheating. <em>Action: Feed these clusters directly to the product engineering team for OTA firmware enhancements.</em>"
            },
            {
                title: "Verified Users Drive Outsized Impact",
                desc: "Posts by verified accounts drive 3.7× more engagement (likes + shares) per post. If a verified account posts negative sentiment, it represents a brand emergency. <em>Action: Implement real-time alerts specifically filtering verified account mentions.</em>"
            },
            {
                title: "Software Updates Cause Bimodal Spikes",
                desc: "Update cycles create heavy positive sentiment (excitement for new features) combined with sharp negative spikes (bug reports). <em>Action: Run preemptive FAQ and support campaigns concurrently with OTA rollouts to flatten the negative curve.</em>"
            }
        ],
        prep: [
            {
                q: "How does the ensemble model resolve sarcasm better than VADER alone?",
                a: "VADER relies on a lexicon-based lookup which frequently misclassifies sarcastic remarks containing positive words (e.g., 'Oh great, another bug. Thanks Apple!'). TextBlob scores based on polarity and subjectivity. When a post has high subjectivity (>0.7) and conflicting polarity between VADER and TextBlob, the ensemble marks it for neutral/manual review, which protects data integrity."
            },
            {
                q: "What is the business value of Z-Score Outlier Detection?",
                a: "In brand management, monitoring absolute numbers is misleading because mention volumes fluctuate daily. By using a rolling 14-day standard deviation to calculate a Z-score, the dashboard triggers alerts only when the negative mention rate increases at a statistically significant rate. This gives the PR team a 48 to 72-hour head start to address product issues before they go viral."
            }
        ]
    },
    p3: {
        domain: "E-Commerce Analytics",
        title: "Retail Sales Forecasting & Insight Engine",
        summary: "An end-to-end sales engine utilizing Facebook Prophet for revenue forecasting (1.75% MAPE), RFM cohort segmentation for 8,000 customers, and a Power BI executive reporting dashboard.",
        overview: {
            problem: "Manual financial reporting consumed 70% of analyst time, and the procurement team suffered from high storage costs due to over-stocking slow-moving categories.",
            solution: "Cleaned and structured 3 years of transaction history. Deployed a Facebook Prophet model tracking monthly trends and seasonality to generate 6-month demand forecasts. Developed an RFM scoring matrix to segment customers into 7 action categories.",
            highlights: [
                "<strong>1.75% Forecast Error (MAPE):</strong> High-precision Prophet prediction with multiplicative seasonality.",
                "<strong>7 Customer Segments Identified:</strong> RFM classification dividing buyers from 'Champions' to 'Lost' customers.",
                "<strong>70% Reporting Reduction:</strong> Replaced static spreadsheets with interactive Power BI dashboards.",
                "<strong>High-Margin Cross-Selling:</strong> Projected a 12% revenue uplift by cross-selling beauty products to electronics buyers."
            ],
            tech: ["Python", "Prophet", "Scikit-Learn", "K-Means Clustering", "PostgreSQL", "Power BI", "Excel"]
        },
        visuals: [
            {
                src: "Project3_Retail/Images/P3_executive_dashboard.png",
                caption: "Executive Retail Performance & Forecasts",
                sub: "Prophet monthly forecasts (with 95% confidence intervals) plotted against actual sales, along with category revenue breakdown, channel performance, and regional sales."
            },
            {
                src: "Project3_Retail/Images/P3_rfm_segmentation.png",
                caption: "RFM Customer Segmentation",
                sub: "Visual distribution of RFM segments (Champions, Loyalists, At Risk) and scatter analysis of purchase frequency vs total monetary spend."
            },
            {
                src: "Project3_Retail/Images/P3_cohort_retention.png",
                caption: "Cohort Retention Analysis Heatmap",
                sub: "Month-on-month customer retention percentages for cohorts over a 12-month window, highlighting higher retention rates for festive-acquired cohorts."
            }
        ],
        sql: {
            desc: "Designed queries to track transaction history, regional margins, and cohort groups. Below is the SQL script running the RFM segmentation using SQL window functions.",
            code: `-- RFM Base Score CTE
WITH rfm_base AS (
    SELECT
        customer_id,
        DATEDIFF('2025-01-01', MAX(order_date))          AS recency_days,
        COUNT(DISTINCT transaction_id)                   AS frequency,
        ROUND(SUM(net_amount), 2)                        AS monetary
    FROM retail_db.transactions
    WHERE return_flag = 0
    GROUP BY customer_id
),
rfm_scored AS (
    SELECT
        customer_id, recency_days, frequency, monetary,
        NTILE(5) OVER (ORDER BY recency_days ASC)        AS r_score,
        NTILE(5) OVER (ORDER BY frequency DESC)          AS f_score,
        NTILE(5) OVER (ORDER BY monetary DESC)           AS m_score
    FROM rfm_base
)
SELECT
    customer_id,
    recency_days, frequency, monetary,
    r_score, f_score, m_score,
    (r_score + f_score + m_score)                        AS rfm_total,
    CASE
        WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'Champions'
        WHEN r_score >= 3 AND f_score >= 3                  THEN 'Loyal Customers'
        WHEN r_score >= 4 AND f_score <= 2                  THEN 'New Customers'
        WHEN r_score >= 3 AND m_score >= 3                  THEN 'Potential Loyalists'
        WHEN r_score <= 2 AND f_score >= 3                  THEN 'At Risk'
        WHEN r_score <= 1 AND f_score <= 1                  THEN 'Lost'
        ELSE 'Others'
    END                                                  AS customer_segment_rfm
FROM rfm_scored;`
        },
        python: {
            desc: "The forecasting engine uses Prophet to model trend, yearly seasonality, and monsoon/festive outliers. Below is the script used to generate predictions.",
            code: `import pandas as pd
from prophet import Prophet

# 1. Load & Format Data
transactions = pd.read_csv('../Data/transactions.csv', parse_dates=['order_date'])
df_sales = transactions[transactions['return_flag'] == 0].copy()

# Group to monthly revenue
monthly_rev = df_sales.groupby(df_sales['order_date'].dt.to_period('M'))['net_amount'].sum().reset_index()
monthly_rev.columns = ['ds', 'y']
monthly_rev['ds'] = monthly_rev['ds'].dt.to_timestamp()

# 2. Deploy Prophet Model
m = Prophet(
    yearly_seasonality=True,
    weekly_seasonality=False,
    daily_seasonality=False,
    seasonality_mode='multiplicative',
    changepoint_prior_scale=0.1,
    interval_width=0.95
)
m.fit(monthly_rev)

# 3. Forecast 6 Months Forward
future = m.make_future_dataframe(periods=6, freq='MS')
forecast = m.predict(future)

# 4. Review predictions
next_6 = forecast[forecast['ds'] > monthly_rev['ds'].max()][['ds','yhat','yhat_lower','yhat_upper']]
print(next_6.head())`
        },
        insights: [
            {
                title: "Festive Season Revenue Spike",
                desc: "Festive months (Oct–Dec) drive 38% of annual revenue. Electronics and Clothing show a 55% and 42% lift, respectively. <em>Action: Increase Electronics inventory stocks by 40% in September to prevent stockouts.</em>"
            },
            {
                title: "High-Margin Cross-Selling Opportunity",
                desc: "Electronics drives 34% of revenue but only 18% margin, while Beauty yields 41% margin on 12% revenue. <em>Action: Implement product recommendation triggers to cross-sell Beauty products to Electronics buyers during checkout.</em>"
            },
            {
                title: "UPI Leads Transaction Checkout Speed",
                desc: "UPI accounts for 31.4% of transactions (surpassing Credit Cards) and finishes checkout 8% faster. <em>Action: Promote UPI-exclusive cashbacks and ensure zero-downtime gateway integrations.</em>"
            },
            {
                title: "Monsoon Season Cooking Spike",
                desc: "Monsoon months (Jun–Jul) trigger a 22% spike in Home & Kitchen appliances. <em>Action: Align regional marketing campaigns for kitchen gadgets to start in May.</em>"
            }
        ],
        prep: [
            {
                q: "What is MAPE and why is it important in retail forecasting?",
                a: "MAPE stands for Mean Absolute Percentage Error. It measures the average percentage size of forecasting errors regardless of sign. In retail, achieving a low MAPE (1.75% in our model) is critical because it directly prevents capital from being tied up in overstocking while eliminating lost sales from stockouts."
            },
            {
                q: "How does the cohort retention heatmap impact your acquisition budget?",
                a: "The cohort heatmap revealed that customers acquired during the Q4 festive campaign had a 6-month retention rate of 44% vs 28% for regular-month cohorts. This demonstrates that festive acquisitions have a 57% higher lifetime value, justifying a higher customer acquisition cost (CAC) budget during Q4."
            }
        ]
    }
};

let currentProject = 'p1';
let currentSubTab = 'overview';
let activePanel = 'project'; // 'project', 'resume', 'achievements'

// Master resume ATS bullets to load
const resumeATSContent = `• Designed a centralized placement analytics system with a 4-table star schema SQL database (46K+ records); wrote 35 interview-quality queries using CTEs, window functions, and joins to answer 8 key business KPIs.

• Built Random Forest placement prediction model achieving 86% accuracy and 0.73 AUC-ROC on 5,000 student records; engineered 7 features including a composite placement score using CGPA, internships, certifications, and backlogs.

• Developed 4-page Power BI dashboard with 10 DAX measures, drill-through pages, and dynamic slicers; identified internship count as the #1 placement predictor, enabling data-driven counselling intervention.

• Collected and preprocessed 30,000+ social media posts across Samsung, Apple, and OnePlus; built 7-step NLP cleaning pipeline (URL removal, stop words, lemmatization) using regex and NLTK.

• Applied VADER and TextBlob sentiment classification achieving 82% accuracy on 500-record labelled sample; implemented ensemble model combining both scores to reduce sarcasm misclassification.

• Cleaned 50,000+ rows of 3-year retail transactional data; built Facebook Prophet time-series model achieving MAPE of 1.75% for monthly revenue forecasting with 6-month forward horizon.

• Performed RFM customer segmentation dividing 8,000 customers into 7 actionable groups (Champions to Lost); K-Means clustering (k=4) validated with silhouette score of 0.38 for targeted marketing campaigns.`;

// ==========================================================================
// CORE UI FUNCTIONS
// ==========================================================================

// Switch between Project 1, 2, and 3
function switchProject(projId) {
    currentProject = projId;
    activePanel = 'project';
    
    // Update sidebar button states
    document.querySelectorAll('.nav-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.nav-btn-alt').forEach(btn => btn.classList.remove('active'));
    document.getElementById(`nav-${projId}`).classList.add('active');
    
    // Show project view and hide others
    document.getElementById('project-view-panel').classList.add('active');
    document.getElementById('resume-panel').classList.remove('active');
    document.getElementById('achievements-panel').classList.remove('active');
    
    // Load project data
    const data = projectData[projId];
    document.getElementById('proj-domain').textContent = data.domain;
    document.getElementById('proj-title').textContent = data.title;
    document.getElementById('proj-summary').textContent = data.summary;
    
    // Load Overview Subtab
    document.getElementById('overview-problem').textContent = data.overview.problem;
    document.getElementById('overview-solution').textContent = data.overview.solution;
    
    // Load highlights
    const highlightsUl = document.getElementById('overview-highlights');
    highlightsUl.innerHTML = '';
    data.overview.highlights.forEach(h => {
        const li = document.createElement('li');
        li.innerHTML = h;
        highlightsUl.appendChild(li);
    });
    
    // Load Tech
    const techDiv = document.getElementById('overview-tech');
    techDiv.innerHTML = '';
    data.overview.tech.forEach(t => {
        const span = document.createElement('span');
        span.className = 'tech-pill';
        span.textContent = t;
        techDiv.appendChild(span);
    });
    
    // Load SQL
    document.getElementById('sql-schema-desc').textContent = data.sql.desc;
    document.getElementById('sql-code-block').textContent = data.sql.code;
    
    // Load Python
    document.getElementById('python-desc').textContent = data.python.desc;
    document.getElementById('python-code-block').textContent = data.python.code;
    
    // Load Insights
    const insightsOl = document.getElementById('insights-list');
    insightsOl.innerHTML = '';
    data.insights.forEach(ins => {
        const li = document.createElement('li');
        li.innerHTML = `<h4>${ins.title}</h4><p>${ins.desc}</p>`;
        insightsOl.appendChild(li);
    });
    
    // Load FAQ / Prep
    const faqDiv = document.getElementById('faq-list');
    faqDiv.innerHTML = '';
    data.prep.forEach((item, index) => {
        const faqItem = document.createElement('div');
        faqItem.className = 'faq-item';
        faqItem.innerHTML = `
            <div class="faq-question" onclick="toggleFaq(this)">
                <span>${index + 1}. ${item.q}</span>
            </div>
            <div class="faq-answer">
                <p>${item.a}</p>
            </div>
        `;
        faqDiv.appendChild(faqItem);
    });
    
    // Load Gallery
    const galleryDiv = document.getElementById('visuals-gallery');
    galleryDiv.innerHTML = '';
    data.visuals.forEach(v => {
        const item = document.createElement('div');
        item.className = 'gallery-item';
        item.onclick = () => openLightbox(v.src, v.caption + " — " + v.sub);
        item.innerHTML = `
            <div class="gallery-image-box">
                <img src="${v.src}" alt="${v.caption}">
            </div>
            <div class="gallery-caption">
                <h4>${v.caption}</h4>
                <p>${v.sub}</p>
            </div>
        `;
        galleryDiv.appendChild(item);
    });
    
    // Maintain current subtab active view
    switchSubTab(currentSubTab);
}

// Switch sub-tabs (Overview, Visuals, SQL, Python, etc.)
function switchSubTab(tabId) {
    currentSubTab = tabId;
    
    // Update subtab button class
    document.querySelectorAll('.tab-link').forEach(tab => tab.classList.remove('active'));
    document.getElementById(`tab-${tabId}`).classList.add('active');
    
    // Show subtab panel
    document.querySelectorAll('.subtab-content').forEach(content => content.classList.remove('active'));
    document.getElementById(`content-${tabId}`).classList.add('active');
}

// Switch between Project, Resume, and Achievements panel
function switchPanel(panelId) {
    activePanel = panelId;
    
    // Update sidebar selection
    document.querySelectorAll('.nav-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.nav-btn-alt').forEach(btn => btn.classList.remove('active'));
    document.getElementById(`nav-${panelId}`).classList.add('active');
    
    // Toggle primary view panel visibility
    document.getElementById('project-view-panel').classList.remove('active');
    document.getElementById('resume-panel').classList.remove('active');
    document.getElementById('achievements-panel').classList.remove('active');
    
    document.getElementById(`${panelId}-panel`).classList.add('active');
}

// Expandable FAQ Accordions
function toggleFaq(element) {
    const parent = element.parentElement;
    const isOpen = parent.classList.contains('open');
    
    // Close other FAQ items
    document.querySelectorAll('.faq-item').forEach(item => item.classList.remove('open'));
    
    // Toggle current
    if (!isOpen) {
        parent.classList.add('open');
    }
}

// ==========================================================================
// UTILITY FUNCTIONS (Lightbox, Copy, Init)
// ==========================================================================

// Fullscreen Image Lightbox Viewer
function openLightbox(src, caption) {
    const modal = document.getElementById('lightbox');
    const modalImg = document.getElementById('lightbox-img');
    const modalCap = document.getElementById('lightbox-caption');
    
    modal.style.display = 'flex';
    modalImg.src = src;
    modalCap.innerHTML = caption;
}

function closeLightbox() {
    document.getElementById('lightbox').style.display = 'none';
}

// Copy Code to Clipboard with feedback
function copyCode(elementId) {
    const codeText = document.getElementById(elementId).textContent;
    const btn = event.target;
    
    navigator.clipboard.writeText(codeText).then(() => {
        const originalText = btn.textContent;
        btn.textContent = 'Copied!';
        btn.style.backgroundColor = 'var(--green)';
        btn.style.color = '#000';
        btn.style.borderColor = 'var(--green)';
        
        setTimeout(() => {
            btn.textContent = originalText;
            btn.style.backgroundColor = '';
            btn.style.color = '';
            btn.style.borderColor = '';
        }, 1500);
    }).catch(err => {
        console.error('Failed to copy code: ', err);
    });
}

// Initialize Application
document.addEventListener('DOMContentLoaded', () => {
    // Load resume ATS content into pre block
    document.getElementById('resume-text').textContent = resumeATSContent;
    
    // Load project 1 by default
    switchProject('p1');
});
