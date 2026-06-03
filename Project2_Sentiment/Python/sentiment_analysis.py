"""
=============================================================
PROJECT 2: SOCIAL MEDIA SENTIMENT & BRAND INTELLIGENCE
NLP Analysis: VADER + TextBlob + Topic Modelling
Author: Shubham Dubey | MCA - BVICAM, GGSIPU
=============================================================
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
import re
import warnings
warnings.filterwarnings('ignore')

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
import nltk
nltk.download('stopwords', quiet=True)
nltk.download('punkt', quiet=True)
nltk.download('wordnet', quiet=True)
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation

# ── CONFIG ────────────────────────────────────────────────────────────────────
plt.rcParams.update({
    'figure.facecolor': '#0a0e1a',
    'axes.facecolor': '#1a1d2e',
    'text.color': '#e0e0e0',
    'axes.labelcolor': '#e0e0e0',
    'xtick.color': '#aaa',
    'ytick.color': '#aaa',
    'grid.color': '#333',
    'grid.alpha': 0.4,
})
PALETTE  = ['#00d4ff','#ff6b6b','#ffd700','#00ff9f','#b44fff']
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR  = os.path.join(BASE_DIR, 'Images') + os.sep
BRANDS   = ['Samsung','Apple','OnePlus']

print("=" * 60)
print("SOCIAL MEDIA SENTIMENT & BRAND INTELLIGENCE DASHBOARD")
print("=" * 60)

# ── LOAD DATA ─────────────────────────────────────────────────────────────────
df = pd.read_csv(os.path.join(BASE_DIR, 'Data', 'social_media_posts.csv'))
df_metrics = pd.read_csv(os.path.join(BASE_DIR, 'Data', 'brand_metrics.csv'))
print(f"\n📊 Posts loaded: {len(df):,} | Columns: {list(df.columns)}")

# ── PHASE 1: TEXT PREPROCESSING ───────────────────────────────────────────────
print("\n" + "─" * 50)
print("PHASE 1: TEXT PREPROCESSING & CLEANING")
print("─" * 50)

stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

def clean_text(text):
    text = str(text).lower()
    text = re.sub(r'http\S+|www\S+', '', text)          # Remove URLs
    text = re.sub(r'@\w+|#\w+', '', text)               # Remove mentions/hashtags
    text = re.sub(r'[^\w\s]', '', text)                 # Remove punctuation
    text = re.sub(r'\s+', ' ', text).strip()            # Normalize whitespace
    tokens = [lemmatizer.lemmatize(w) for w in text.split()
              if w not in stop_words and len(w) > 2]
    return ' '.join(tokens)

# Apply on sample for speed
print("  Cleaning text corpus...")
df['clean_text'] = df['text'].apply(clean_text)
df['word_count_clean'] = df['clean_text'].str.split().str.len()
print(f"  ✓ Cleaned {len(df):,} posts")
print(f"  ✓ Avg words before cleaning: {df['word_count'].mean():.1f}")
print(f"  ✓ Avg words after cleaning:  {df['word_count_clean'].mean():.1f}")

# ── PHASE 2: VADER SENTIMENT ──────────────────────────────────────────────────
print("\n" + "─" * 50)
print("PHASE 2: VADER SENTIMENT SCORING")
print("─" * 50)

analyzer = SentimentIntensityAnalyzer()

def vader_sentiment(text):
    scores = analyzer.polarity_scores(str(text))
    return scores

vader_scores = df['text'].apply(vader_sentiment)
df['vader_pos']   = vader_scores.apply(lambda x: x['pos'])
df['vader_neg']   = vader_scores.apply(lambda x: x['neg'])
df['vader_neu']   = vader_scores.apply(lambda x: x['neu'])
df['vader_compound'] = vader_scores.apply(lambda x: x['compound'])

def vader_label(score):
    if score >= 0.05: return 'Positive'
    if score <= -0.05: return 'Negative'
    return 'Neutral'

df['vader_sentiment'] = df['vader_compound'].apply(vader_label)

vader_acc = (df['vader_sentiment'] == df['true_sentiment']).mean()
print(f"  ✓ VADER accuracy vs labeled data: {vader_acc*100:.1f}%")

# ── PHASE 3: TEXTBLOB SENTIMENT ───────────────────────────────────────────────
print("\n" + "─" * 50)
print("PHASE 3: TEXTBLOB SENTIMENT SCORING")
print("─" * 50)

def textblob_analyze(text):
    analysis = TextBlob(str(text))
    return pd.Series({
        'tb_polarity': analysis.sentiment.polarity,
        'tb_subjectivity': analysis.sentiment.subjectivity
    })

tb_results = df['text'].apply(textblob_analyze)
df['tb_polarity']    = tb_results['tb_polarity']
df['tb_subjectivity']= tb_results['tb_subjectivity']

def textblob_label(score):
    if score > 0.1: return 'Positive'
    if score < -0.1: return 'Negative'
    return 'Neutral'

df['tb_sentiment'] = df['tb_polarity'].apply(textblob_label)
tb_acc = (df['tb_sentiment'] == df['true_sentiment']).mean()
print(f"  ✓ TextBlob accuracy vs labeled data: {tb_acc*100:.1f}%")

# Ensemble: combine VADER + TextBlob
def ensemble_sentiment(row):
    scores = []
    if row['vader_compound'] >= 0.05: scores.append(1)
    elif row['vader_compound'] <= -0.05: scores.append(-1)
    else: scores.append(0)
    if row['tb_polarity'] > 0.1: scores.append(1)
    elif row['tb_polarity'] < -0.1: scores.append(-1)
    else: scores.append(0)
    avg = np.mean(scores)
    if avg > 0: return 'Positive'
    if avg < 0: return 'Negative'
    return 'Neutral'

df['ensemble_sentiment'] = df.apply(ensemble_sentiment, axis=1)
ens_acc = (df['ensemble_sentiment'] == df['true_sentiment']).mean()
print(f"  ✓ Ensemble accuracy:             {ens_acc*100:.1f}%")

# ── PHASE 4: LDA TOPIC MODELLING ──────────────────────────────────────────────
print("\n" + "─" * 50)
print("PHASE 4: LDA TOPIC MODELLING")
print("─" * 50)

for brand in BRANDS:
    brand_df = df[df['brand'] == brand]
    
    # Sample 3000 posts per brand for speed
    sample = brand_df['clean_text'].dropna().sample(min(3000, len(brand_df)), random_state=42)
    
    # Negative posts topic modelling
    neg_texts = df[(df['brand']==brand) & (df['true_sentiment']=='Negative')]['clean_text'].dropna()
    
    if len(neg_texts) < 50:
        continue
    
    vectorizer = CountVectorizer(max_df=0.95, min_df=2, max_features=500, stop_words='english')
    try:
        dtm = vectorizer.fit_transform(neg_texts)
        lda = LatentDirichletAllocation(n_components=5, random_state=42, max_iter=20)
        lda.fit(dtm)
        
        feature_names = vectorizer.get_feature_names_out()
        print(f"\n  {brand} — Top Complaint Themes:")
        for idx, topic in enumerate(lda.components_):
            top_words = [feature_names[i] for i in topic.argsort()[:-6:-1]]
            print(f"    Topic {idx+1}: {', '.join(top_words)}")
    except Exception as e:
        print(f"  {brand} LDA: {e}")

# ── PHASE 5: BRAND COMPARISON VISUALIZATIONS ──────────────────────────────────
print("\n" + "─" * 50)
print("PHASE 5: GENERATING BRAND INTELLIGENCE DASHBOARD")
print("─" * 50)

fig = plt.figure(figsize=(22, 16))
fig.patch.set_facecolor('#0a0e1a')
gs  = gridspec.GridSpec(3, 3, figure=fig, hspace=0.5, wspace=0.4)

# 1. Overall sentiment distribution per brand
ax1 = fig.add_subplot(gs[0, :])
brand_sent = df.groupby(['brand','true_sentiment']).size().unstack(fill_value=0)
x   = np.arange(len(BRANDS))
w   = 0.25
for i, sent in enumerate(['Positive','Negative','Neutral']):
    if sent in brand_sent.columns:
        ax1.bar(x + i*w, brand_sent.loc[BRANDS, sent], w,
                label=sent, color=PALETTE[i], alpha=0.85, edgecolor='#333')
ax1.set_xticks(x + w); ax1.set_xticklabels(BRANDS, fontsize=12)
ax1.set_ylabel('Post Count'); ax1.set_title('Brand Sentiment Distribution', color='#e0e0e0', fontsize=13)
ax1.legend(facecolor='#1a1d2e', edgecolor='#444', labelcolor='#e0e0e0')

# 2. Monthly Sentiment Trend (VADER compound)
ax2 = fig.add_subplot(gs[1, :2])
for i, brand in enumerate(BRANDS):
    monthly = df[df['brand']==brand].groupby('post_month')['vader_compound'].mean()
    ax2.plot(monthly.index, monthly.values, marker='o', markersize=4,
             linewidth=2, label=brand, color=PALETTE[i])
ax2.set_title('Monthly Sentiment Trend (VADER Score)', color='#e0e0e0')
ax2.set_xlabel('Month'); ax2.set_ylabel('Avg VADER Score')
ax2.axhline(0, color='#555', linestyle='--', linewidth=1)
ax2.legend(facecolor='#1a1d2e', edgecolor='#444', labelcolor='#e0e0e0')
plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right', fontsize=8)

# 3. Share of Voice
ax3 = fig.add_subplot(gs[1, 2])
sov = df['brand'].value_counts()
wedge_props = dict(width=0.5, edgecolor='#0a0e1a', linewidth=2)
ax3.pie(sov.values, labels=sov.index, colors=PALETTE[:len(sov)],
        autopct='%1.1f%%', startangle=90,
        wedgeprops=wedge_props, textprops={'color':'#e0e0e0'})
ax3.set_title('Share of Voice', color='#e0e0e0')

# 4. Category-wise Negative Sentiment
ax4 = fig.add_subplot(gs[2, :2])
cat_neg = df.groupby(['category','true_sentiment']).size().unstack(fill_value=0)
cat_neg['neg_pct'] = cat_neg.get('Negative',0) * 100 / cat_neg.sum(axis=1)
cat_neg_sorted = cat_neg['neg_pct'].sort_values(ascending=True)
colors = ['#ff4444' if v > 35 else '#ffa500' if v > 25 else '#00d4ff'
          for v in cat_neg_sorted.values]
ax4.barh(cat_neg_sorted.index, cat_neg_sorted.values, color=colors, edgecolor='#333')
ax4.axvline(30, color='#ffd700', linestyle='--', linewidth=1.5, alpha=0.8)
ax4.set_title('Negative Sentiment Rate by Category', color='#e0e0e0')
ax4.set_xlabel('Negative Sentiment (%)')
ax4.text(30.5, -0.5, 'Threshold\n(30%)', color='#ffd700', fontsize=8)

# 5. Engagement vs Sentiment Scatter
ax5 = fig.add_subplot(gs[2, 2])
for i, brand in enumerate(BRANDS):
    bdf = df[df['brand']==brand].sample(min(500, len(df[df['brand']==brand])), random_state=42)
    ax5.scatter(bdf['vader_compound'],
                np.log1p(bdf['likes'] + bdf['shares'] + bdf['comments']),
                alpha=0.3, s=10, color=PALETTE[i], label=brand)
ax5.set_xlabel('VADER Sentiment Score')
ax5.set_ylabel('log(Engagement)')
ax5.set_title('Sentiment vs Engagement', color='#e0e0e0')
ax5.legend(facecolor='#1a1d2e', edgecolor='#444', labelcolor='#e0e0e0', markerscale=3)

fig.suptitle('BRAND INTELLIGENCE DASHBOARD — Sentiment & Competitive Analysis',
             fontsize=14, color='#00d4ff', fontweight='bold', y=0.99)

plt.savefig(OUT_DIR + 'P2_brand_intelligence_dashboard.png', dpi=150,
            bbox_inches='tight', facecolor='#0a0e1a')
plt.close()
print("  ✓ Saved: P2_brand_intelligence_dashboard.png")

# Save enriched data
df.to_csv(os.path.join(BASE_DIR, 'Data', 'posts_with_sentiment.csv'), index=False)
print("  ✓ Saved: posts_with_sentiment.csv (enriched with VADER + TextBlob)")

# Summary stats
print(f"\n{'═'*50}")
print("  SENTIMENT ANALYSIS SUMMARY")
print(f"{'═'*50}")
for brand in BRANDS:
    bdf = df[df['brand']==brand]
    pos_pct = (bdf['true_sentiment']=='Positive').mean()*100
    neg_pct = (bdf['true_sentiment']=='Negative').mean()*100
    avg_vader = bdf['vader_compound'].mean()
    print(f"  {brand:<12} Pos={pos_pct:.1f}%  Neg={neg_pct:.1f}%  VADER={avg_vader:+.3f}")

print("\n✅ SENTIMENT ANALYSIS COMPLETE")
