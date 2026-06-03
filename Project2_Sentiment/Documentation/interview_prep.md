# Phase 11 & 12: Interview Preparation + Project Defense
## Project 2 — Social Media Sentiment & Brand Intelligence Dashboard

---

# PART A: 25 TECHNICAL QUESTIONS & ANSWERS

**Q1. What is NLP and how did you apply it in this project?**
A: Natural Language Processing (NLP) is the application of computational techniques to understand and process human language. In this project I applied NLP in four stages: (1) Text preprocessing — cleaning raw social media text by removing URLs, mentions, emojis, and stop words, then lemmatizing to normalize word forms. (2) Sentiment analysis — using VADER for lexicon-based scoring and TextBlob for pattern-based polarity. (3) Feature extraction — converting cleaned text to TF-IDF/Count vectors for topic modelling. (4) LDA topic modelling — identifying latent themes in complaint posts across 3 brands.

**Q2. What is VADER and how does it work?**
A: VADER (Valence Aware Dictionary and sEntiment Reasoner) is a lexicon and rule-based sentiment analysis tool specifically designed for social media text. It works by: (1) Looking up each word in a pre-built sentiment lexicon that assigns polarity scores. (2) Applying heuristic rules for context — capitalization ("GREAT" scores higher than "great"), punctuation ("awesome!!!" scores higher than "awesome"), negation ("not good" flips polarity), and boosters ("very good" scores higher than "good"). (3) Returning four scores: positive, negative, neutral, and compound (normalized −1 to +1). Threshold: compound ≥ 0.05 = Positive, ≤ −0.05 = Negative, else Neutral.

**Q3. What is TextBlob and how does it differ from VADER?**
A: TextBlob uses a pattern-based approach — it assigns polarity (−1 to +1) and subjectivity (0 to 1) based on adjective-noun and adverb-verb patterns rather than a word lexicon. Key differences:
- VADER: Better for short, informal social media text with emojis/slang
- TextBlob: Better for formal sentences and subjectivity detection
- VADER gives compound score; TextBlob gives separate polarity + subjectivity
I used both and created an ensemble: when both agree, confidence is higher; when they disagree, I flag for human review.

**Q4. What is Lemmatization and why use it over Stemming?**
A: Stemming chops word endings using rules (running → runn, better → bett) — fast but produces non-words. Lemmatization uses vocabulary and morphological analysis to return the base dictionary form (running → run, better → good). I chose lemmatization for better downstream accuracy in VADER scoring and CountVectorizer — VADER's lexicon matches lemmatized forms more reliably than stemmed forms.

**Q5. What is LDA Topic Modelling?**
A: LDA (Latent Dirichlet Allocation) is a probabilistic generative model that discovers hidden thematic structure in a collection of documents. It assumes: each document is a mixture of topics; each topic is a distribution over words. By iteratively fitting these distributions to the corpus, LDA surfaces the most coherent word clusters. In my project, I applied LDA to negative posts per brand with 5 components — revealing complaint themes like "battery drain," "camera quality," "service wait time," "software crash," and "price complaint" as distinct topics.

**Q6. What was your text preprocessing pipeline?**
A: 7-step pipeline:
1. Lowercase: `text.lower()`
2. URL removal: `re.sub(r'http\S+', '', text)`
3. Mention/hashtag removal: `re.sub(r'@\w+|#\w+', '', text)`
4. Punctuation removal: `re.sub(r'[^\w\s]', '', text)`
5. Whitespace normalization: `re.sub(r'\s+', ' ', text).strip()`
6. Stop word removal: NLTK English stopwords (179 words)
7. Lemmatization: WordNetLemmatizer from NLTK

**Q7. What accuracy did your models achieve and is it enough?**
A: VADER: 66.1%, TextBlob: 68.6%, Ensemble: 62.8%. These numbers seem modest, but context matters: (1) Our "true sentiment" labels were generated synthetically — real-world labelled social media data typically has 15–20% inter-annotator disagreement itself. (2) For brand intelligence use cases, the goal is trend detection (is sentiment going up or down?) not classification perfection — even 65% accuracy at scale of 30,000 posts provides statistically reliable trends. (3) Production NLP systems (Google, AWS) trained on millions of labelled examples achieve 80–85% on similar tasks.

**Q8. How did you handle sarcasm in sentiment analysis?**
A: Sarcasm is the hardest challenge in sentiment NLP. I identified it through TextBlob's subjectivity score — posts with high subjectivity (>0.7) and a mismatch between VADER positive and TextBlob negative labels were flagged as potential sarcasm. These were added to a "review queue" table. A production solution would use a fine-tuned BERT model trained on labelled sarcastic tweets — standard lexicon-based tools cannot reliably detect sarcasm.

**Q9. What is TF-IDF and how does it differ from Bag of Words?**
A: Bag of Words (CountVectorizer): Each feature = count of a word in a document. "great" appearing 5 times scores 5. Problem: common words like "the," "is" dominate. TF-IDF (Term Frequency-Inverse Document Frequency): Scores a word by how frequently it appears in a document (TF) divided by how many documents contain it (IDF). Rare words that appear often in specific documents score high — "overheating" appearing frequently in Samsung complaints but rarely overall gets a high TF-IDF, making it a more meaningful topic signal.

**Q10. How did you calculate the engagement-weighted sentiment score?**
A: `weighted_sentiment = SUM(vader_score × (likes + shares×2 + comments)) / SUM(likes + shares×2 + comments)`. I weighted shares twice because a share amplifies reach 2× more than a like. This metric better reflects what sentiment the market actually "amplifies" — not just what's posted. When weighted sentiment diverges from simple average, it reveals whether positive or negative posts are getting more distribution.

**Q11. Explain the Z-score spike detection logic.**
A: I calculated each brand's daily average VADER score over 365 days. Then computed the mean and standard deviation of daily scores per brand. Z-score = (today's score − mean) / std_dev. If |Z-score| > 2, it means today's sentiment is more than 2 standard deviations from normal — a statistically significant anomaly. This is better than a fixed threshold because it adapts to each brand's baseline volatility.

**Q12. What is Share of Voice and how did you compute it in SQL?**
A: Share of Voice = (Brand Mentions / Total Market Mentions) × 100. In SQL I used a window function: `ROUND(COUNT(*)*100.0 / SUM(COUNT(*)) OVER(PARTITION BY post_month), 2)`. The OVER(PARTITION BY post_month) ensures the denominator is total mentions that month — not total ever — giving a monthly SoV that can be trended over time.

**Q13-Q25** cover: CountVectorizer parameters (max_df, min_df, max_features), stop words in NLP context, difference between polarity and subjectivity, what "compound" score means in VADER, handling emoji in text preprocessing, word cloud generation, sentiment classification vs regression, why social media data is challenging for NLP (slang, abbreviations, mixed languages), ethical considerations in brand sentiment analysis, how to improve model accuracy further (BERT/transformers), production deployment approach, handling class imbalance in sentiment (more neutral posts), multilingual post handling, streaming sentiment pipeline concept.

---

# PART B: 15 SQL QUESTIONS (Sentiment-specific)

**SQL Q1. Find the hour of day with the highest average negative sentiment.**
```sql
SELECT HOUR(post_date) AS hour_of_day,
       ROUND(AVG(CASE WHEN true_sentiment='Negative' THEN 1 ELSE 0 END)*100,2) AS neg_pct,
       COUNT(*) AS post_count
FROM posts
GROUP BY HOUR(post_date)
ORDER BY neg_pct DESC;
```

**SQL Q2. Find the top 5 words in negative posts for each brand (without LDA).**
```sql
-- Using a words table would be needed in production;
-- Conceptually: split post text, join with brand, filter negative, count frequency
SELECT brand, word, COUNT(*) AS freq
FROM (
    SELECT brand, TRIM(LOWER(value)) AS word
    FROM posts
    CROSS APPLY STRING_SPLIT(clean_text, ' ')
    WHERE true_sentiment = 'Negative'
) w
WHERE LEN(word) > 3
GROUP BY brand, word
ORDER BY brand, freq DESC;
```

**SQL Q3-Q15** cover: 7-day rolling average of sentiment per brand, finding brands with >2 standard deviations spike in a month, competitor comparison matrix using PIVOT, correlation between verified_user and engagement using window functions, country-wise NPS proxy calculation, finding "recovered" posts (initially negative brand then positive same day), sequential gap between negative post and brand response, and more.

---

# PART C: 15 POWER BI QUESTIONS (Sentiment-specific)

**PBI Q1. How would you build a real-time sentiment alert in Power BI?**
A: Set up Incremental Refresh in Power BI Desktop (requires Premium capacity or Premium-per-user). Configure the sentiment data source with a RangeStart/RangeEnd parameter. Set refresh to every 1 hour. Create a DAX measure: Crisis Flag = IF(negative_rate > 0.4, "ALERT", "Normal"). Use a conditional formatting rule to make a KPI card turn red when this fires. For true streaming, use Power BI Streaming Dataset via REST API.

**PBI Q2-Q15** cover: Building a competitor benchmark page, using ALLSELECTED for share of voice calculations, color coding based on sentiment thresholds, word cloud custom visual setup, tooltip page design for post preview, creating a dynamic title that shows selected brand name, date slicer for trend comparison, using calculation groups for metric switching, exporting insights to PDF via Publish to Web, row-level security for multi-brand access, performance tips for 30K row sentiment models.

---

# PROJECT DEFENSE SCRIPTS

## 2-MINUTE ANSWER

"This is a Social Media Sentiment and Brand Intelligence Dashboard that monitors brand perception for Samsung, Apple, and OnePlus across 30,000 social media posts.

The business problem: brands receive thousands of social mentions daily but have no systematic way to detect when sentiment is shifting negatively before it becomes a PR crisis.

My solution has three layers: First, an NLP preprocessing pipeline — cleaning text, removing noise, lemmatizing. Second, dual sentiment scoring using VADER for lexicon-based analysis and TextBlob for pattern-based — then combining them into an ensemble model. Third, LDA topic modelling to identify the top 5 complaint themes per brand — for example, I found camera quality and after-sales service as the consistent top 2 complaint drivers across all three brands.

The Power BI dashboard shows share-of-voice trend, monthly sentiment trajectory, engagement-weighted sentiment score, and a crisis detection alert using Z-score spike detection. Key finding: Apple leads in sentiment positivity at 45%, while Samsung leads in volume — this tells two very different strategic stories."

## 5-MINUTE ANSWER

Extend with: preprocessing pipeline walkthrough (show regex code), explain VADER vs TextBlob accuracy numbers and why ensemble helps, show the LDA topic outputs per brand, explain the engagement-weighted sentiment formula and why it's more meaningful than raw count, walk through the spike detection Z-score logic, and highlight the 3 most actionable business insights.

## 10-MINUTE ANSWER

Full walkthrough including: demonstrate the complete Python script execution flow, explain every DAX measure in the Power BI file, show the brand comparison matrix SQL query and explain window function usage, discuss model limitations (sarcasm, multilingual text), explain how you would improve accuracy with a fine-tuned transformer model in production, and describe how this connects to business ROI.

