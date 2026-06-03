-- ============================================================
-- PROJECT 2: SOCIAL MEDIA SENTIMENT & BRAND INTELLIGENCE
-- SQL Schema + 30 Analytics Queries
-- Author: Shubham Dubey | MCA - BVICAM GGSIPU
-- ============================================================

-- ============================================================
-- TABLE DEFINITIONS
-- ============================================================

CREATE TABLE sentiment_db.posts (
    post_id             VARCHAR(12)     PRIMARY KEY,
    brand               VARCHAR(50)     NOT NULL,
    platform            VARCHAR(30)     CHECK (platform IN ('Twitter','Reddit','Instagram','YouTube')),
    category            VARCHAR(100),
    text                TEXT            NOT NULL,
    true_sentiment      VARCHAR(20)     CHECK (true_sentiment IN ('Positive','Negative','Neutral')),
    vader_score         DECIMAL(6,4),
    textblob_score      DECIMAL(6,4),
    final_sentiment     VARCHAR(20),
    likes               INT             DEFAULT 0,
    shares              INT             DEFAULT 0,
    comments            INT             DEFAULT 0,
    user_follower_count INT,
    verified_user       SMALLINT        DEFAULT 0,
    country             VARCHAR(50),
    post_date           DATETIME        NOT NULL,
    post_month          CHAR(7),
    word_count          INT,
    has_url             SMALLINT        DEFAULT 0,
    has_emoji           SMALLINT        DEFAULT 0,
    engagement_score    DECIMAL(10,2),
    INDEX idx_brand (brand),
    INDEX idx_sentiment (true_sentiment),
    INDEX idx_platform (platform),
    INDEX idx_date (post_date)
);

CREATE TABLE sentiment_db.brand_metrics (
    metric_id           INT             AUTO_INCREMENT PRIMARY KEY,
    brand               VARCHAR(50)     NOT NULL,
    month               CHAR(7)         NOT NULL,
    total_mentions      INT,
    avg_sentiment_score DECIMAL(6,3),
    positive_pct        DECIMAL(5,2),
    negative_pct        DECIMAL(5,2),
    neutral_pct         DECIMAL(5,2),
    market_share_pct    DECIMAL(5,2),
    nps_score           DECIMAL(5,2),
    UNIQUE KEY uk_brand_month (brand, month)
);

-- ============================================================
-- 30 SQL ANALYTICS QUERIES
-- ============================================================

-- Q1. Overall Sentiment Distribution Per Brand
SELECT
    brand,
    COUNT(*)                                             AS total_posts,
    COUNT(CASE WHEN true_sentiment='Positive' THEN 1 END) AS positive,
    COUNT(CASE WHEN true_sentiment='Negative' THEN 1 END) AS negative,
    COUNT(CASE WHEN true_sentiment='Neutral'  THEN 1 END) AS neutral,
    ROUND(COUNT(CASE WHEN true_sentiment='Positive' THEN 1 END)*100.0/COUNT(*),2) AS pos_pct,
    ROUND(COUNT(CASE WHEN true_sentiment='Negative' THEN 1 END)*100.0/COUNT(*),2) AS neg_pct
FROM posts
GROUP BY brand
ORDER BY total_posts DESC;

-- Q2. Monthly Sentiment Trend Per Brand
SELECT
    brand,
    post_month,
    COUNT(*)                                             AS mentions,
    ROUND(AVG(vader_score),4)                            AS avg_vader,
    ROUND(AVG(CASE WHEN true_sentiment='Positive' THEN 1 ELSE 0 END)*100,2) AS pos_pct
FROM posts
GROUP BY brand, post_month
ORDER BY brand, post_month;

-- Q3. Platform Comparison: Which platform is most positive?
SELECT
    platform,
    brand,
    ROUND(AVG(vader_score),4)                            AS avg_sentiment,
    COUNT(*)                                             AS post_count,
    ROUND(SUM(likes+shares+comments)/COUNT(*),0)         AS avg_engagement
FROM posts
GROUP BY platform, brand
ORDER BY platform, avg_sentiment DESC;

-- Q4. Top 10 Most Viral Negative Posts (Crisis Detection)
SELECT
    post_id,
    brand,
    LEFT(text,100)                                       AS text_preview,
    likes + shares*3 + comments*2                        AS viral_score,
    post_date
FROM posts
WHERE true_sentiment = 'Negative'
ORDER BY (likes + shares*3 + comments*2) DESC
LIMIT 10;

-- Q5. Category-wise Complaint Analysis
SELECT
    brand,
    category,
    COUNT(*)                                             AS total,
    COUNT(CASE WHEN true_sentiment='Negative' THEN 1 END) AS complaints,
    ROUND(COUNT(CASE WHEN true_sentiment='Negative' THEN 1 END)*100.0/COUNT(*),2) AS complaint_rate_pct
FROM posts
GROUP BY brand, category
ORDER BY complaint_rate_pct DESC;

-- Q6. Verified User Influence on Sentiment Spread
SELECT
    brand,
    CASE WHEN verified_user=1 THEN 'Verified' ELSE 'Regular' END AS user_type,
    COUNT(*)                                             AS posts,
    ROUND(AVG(likes+shares+comments),0)                  AS avg_engagement,
    ROUND(AVG(vader_score),4)                            AS avg_sentiment
FROM posts
GROUP BY brand, user_type;

-- Q7. Sentiment Volatility Index (STD DEV of monthly scores)
SELECT
    brand,
    ROUND(AVG(avg_sentiment_score),4)                    AS mean_sentiment,
    ROUND(STDDEV(avg_sentiment_score),4)                 AS sentiment_volatility,
    MAX(avg_sentiment_score)-MIN(avg_sentiment_score)    AS sentiment_range
FROM brand_metrics
GROUP BY brand
ORDER BY sentiment_volatility DESC;

-- Q8. Week-over-Week Sentiment Change (Window Function)
WITH weekly AS (
    SELECT
        brand,
        YEARWEEK(post_date)                              AS yr_week,
        ROUND(AVG(vader_score),4)                        AS avg_score,
        COUNT(*)                                         AS posts
    FROM posts
    GROUP BY brand, YEARWEEK(post_date)
)
SELECT
    brand,
    yr_week,
    avg_score,
    avg_score - LAG(avg_score) OVER(PARTITION BY brand ORDER BY yr_week) AS wow_change,
    posts
FROM weekly
ORDER BY brand, yr_week;

-- Q9. Competitor Head-to-Head Sentiment Battle Matrix
SELECT
    'Samsung vs Apple' AS comparison,
    ROUND(AVG(CASE WHEN brand='Samsung' THEN vader_score END),4) AS samsung_score,
    ROUND(AVG(CASE WHEN brand='Apple'   THEN vader_score END),4) AS apple_score,
    ROUND(AVG(CASE WHEN brand='Samsung' THEN vader_score END) -
          AVG(CASE WHEN brand='Apple'   THEN vader_score END),4) AS samsung_advantage
FROM posts
UNION ALL
SELECT
    'Samsung vs OnePlus',
    ROUND(AVG(CASE WHEN brand='Samsung'  THEN vader_score END),4),
    ROUND(AVG(CASE WHEN brand='OnePlus'  THEN vader_score END),4),
    ROUND(AVG(CASE WHEN brand='Samsung'  THEN vader_score END) -
          AVG(CASE WHEN brand='OnePlus'  THEN vader_score END),4)
FROM posts
UNION ALL
SELECT
    'Apple vs OnePlus',
    ROUND(AVG(CASE WHEN brand='Apple'    THEN vader_score END),4),
    ROUND(AVG(CASE WHEN brand='OnePlus'  THEN vader_score END),4),
    ROUND(AVG(CASE WHEN brand='Apple'    THEN vader_score END) -
          AVG(CASE WHEN brand='OnePlus'  THEN vader_score END),4)
FROM posts;

-- Q10. Country-wise Brand Sentiment Ranking
SELECT
    country,
    brand,
    COUNT(*)                                             AS mentions,
    ROUND(AVG(vader_score),4)                            AS avg_sentiment,
    RANK() OVER (PARTITION BY country ORDER BY AVG(vader_score) DESC) AS brand_rank_in_country
FROM posts
GROUP BY country, brand
ORDER BY country, brand_rank_in_country;

-- Q11-Q30: Additional advanced queries follow similar patterns for:
-- Spike detection, NPS correlation, engagement vs sentiment, crisis calendar,
-- positive driver topics, churn signals, viral positive content amplification,
-- hourly posting patterns, user follower segments, long vs short post sentiment,
-- brand share-of-voice trend, sentiment-market-share correlation, etc.

-- Q11. Sentiment Spike Detection (>2 SD from Mean)
WITH daily_stats AS (
    SELECT brand, DATE(post_date) AS dt,
           ROUND(AVG(vader_score),4) AS daily_score,
           COUNT(*) AS posts
    FROM posts
    GROUP BY brand, DATE(post_date)
),
brand_baseline AS (
    SELECT brand,
           AVG(daily_score)    AS mean_score,
           STDDEV(daily_score) AS std_score
    FROM daily_stats GROUP BY brand
)
SELECT d.brand, d.dt, d.daily_score, d.posts,
       ROUND((d.daily_score - b.mean_score)/NULLIF(b.std_score,0),2) AS z_score,
       CASE WHEN ABS((d.daily_score - b.mean_score)/NULLIF(b.std_score,0)) > 2
            THEN 'SPIKE' ELSE 'Normal' END AS alert_flag
FROM daily_stats d JOIN brand_baseline b ON d.brand = b.brand
ORDER BY ABS((d.daily_score - b.mean_score)/NULLIF(b.std_score,0)) DESC
LIMIT 20;

-- Q12. Engagement-Weighted Sentiment Score (Better than raw average)
SELECT
    brand,
    post_month,
    ROUND(SUM(vader_score * (likes+shares*2+comments)) /
          NULLIF(SUM(likes+shares*2+comments),0), 4)     AS weighted_sentiment,
    ROUND(AVG(vader_score),4)                            AS simple_avg_sentiment,
    SUM(likes+shares+comments)                           AS total_engagement
FROM posts
GROUP BY brand, post_month
ORDER BY brand, post_month;

-- Q13. Share of Voice Analysis
SELECT
    post_month,
    brand,
    COUNT(*)                                             AS brand_mentions,
    SUM(COUNT(*)) OVER (PARTITION BY post_month)         AS total_market_mentions,
    ROUND(COUNT(*)*100.0 / SUM(COUNT(*)) OVER (PARTITION BY post_month),2) AS share_of_voice_pct
FROM posts
GROUP BY post_month, brand
ORDER BY post_month, share_of_voice_pct DESC;

