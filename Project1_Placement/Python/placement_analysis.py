"""
=============================================================
PROJECT 1: PLACEMENT MANAGEMENT ANALYTICS SYSTEM
Complete Python Analysis: EDA + ML + Visualization
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
import warnings
warnings.filterwarnings('ignore')

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (classification_report, confusion_matrix,
                              roc_auc_score, roc_curve, accuracy_score)

# ── STYLE CONFIG ──────────────────────────────────────────────────────────────
plt.rcParams.update({
    'figure.facecolor': '#0f1117',
    'axes.facecolor': '#1a1d2e',
    'axes.edgecolor': '#444',
    'text.color': '#e0e0e0',
    'axes.labelcolor': '#e0e0e0',
    'xtick.color': '#aaa',
    'ytick.color': '#aaa',
    'grid.color': '#333',
    'grid.alpha': 0.5,
    'font.family': 'DejaVu Sans',
    'font.size': 10
})
PALETTE = ['#00d4ff','#ff6b6b','#ffd700','#00ff9f','#b44fff','#ff8c00']
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, 'Images') + os.sep

# ── DATA LOADING ──────────────────────────────────────────────────────────────
print("=" * 60)
print("PLACEMENT MANAGEMENT ANALYTICS SYSTEM")
print("=" * 60)

students    = pd.read_csv(os.path.join(BASE_DIR, 'Data', 'students.csv'))
companies   = pd.read_csv(os.path.join(BASE_DIR, 'Data', 'companies.csv'))
applications= pd.read_csv(os.path.join(BASE_DIR, 'Data', 'applications.csv'))
interviews  = pd.read_csv(os.path.join(BASE_DIR, 'Data', 'interviews.csv'))

print(f"\n📊 Data Loaded:")
print(f"  Students:     {len(students):,} rows × {students.shape[1]} cols")
print(f"  Companies:    {len(companies):,} rows × {companies.shape[1]} cols")
print(f"  Applications: {len(applications):,} rows × {applications.shape[1]} cols")
print(f"  Interviews:   {len(interviews):,} rows × {interviews.shape[1]} cols")

# ── PHASE 1: DATA CLEANING & EDA ──────────────────────────────────────────────
print("\n" + "─" * 50)
print("PHASE 1: DATA QUALITY & CLEANING")
print("─" * 50)

# Missing values
print("\nMissing Values Summary:")
for df, name in [(students,'Students'),(companies,'Companies'),
                  (applications,'Applications'),(interviews,'Interviews')]:
    mv = df.isnull().sum()
    if mv.any():
        print(f"\n  {name}:")
        print(mv[mv>0].to_string())
    else:
        print(f"  {name}: ✓ No missing values")

# Fill missing numeric fields
applications['interview_score']    = applications['interview_score'].fillna(0)
applications['package_offered_lpa']= applications['package_offered_lpa'].fillna(0)

# Outlier detection for CGPA
q1, q3 = students['cgpa'].quantile([0.25,0.75])
iqr = q3 - q1
outliers = students[(students['cgpa'] < q1-1.5*iqr) | (students['cgpa'] > q3+1.5*iqr)]
print(f"\n  CGPA outliers detected: {len(outliers)} → clipped to [4.0, 10.0]")
students['cgpa'] = students['cgpa'].clip(4.0, 10.0)

# Feature Engineering
print("\n" + "─" * 50)
print("PHASE 2: FEATURE ENGINEERING")
print("─" * 50)

# Placement flag
placed_ids = applications[applications['status'] == 'Offer Accepted']['student_id'].unique()
students['is_placed'] = students['student_id'].isin(placed_ids).astype(int)

# CGPA band
students['cgpa_band'] = pd.cut(
    students['cgpa'],
    bins=[0,6,7,8,9,10],
    labels=['<6.0','6-7','7-8','8-9','9-10']
)

# Skills count
students['skills_count'] = students['skills'].str.split('|').apply(
    lambda x: len(x) if isinstance(x, list) else 0)

# Has Python / SQL flag (key skills)
students['has_python'] = students['skills'].str.contains('Python', na=False).astype(int)
students['has_sql']    = students['skills'].str.contains('SQL', na=False).astype(int)
students['has_powerbi']= students['skills'].str.contains('Power BI', na=False).astype(int)

# Composite score
students['composite_score'] = (
    students['cgpa'] * 5 +
    students['internships_count'] * 8 +
    students['certifications'] * 3 +
    students['projects_count'] * 4 +
    (students['github_profile'] + students['linkedin_profile']) * 2 -
    students['backlogs'] * 10 -
    students['gap_year'] * 5
)

# App stats per student
app_stats = applications.groupby('student_id').agg(
    total_apps=('application_id','count'),
    shortlisted=('status', lambda x: (x.isin(['Shortlisted','Interview Scheduled','Interviewed',
                                               'Selected','Offer Accepted'])).sum()),
    avg_interview_score=('interview_score','mean'),
    max_package=('package_offered_lpa','max')
).reset_index()

students = students.merge(app_stats, on='student_id', how='left').fillna(0)

print("  ✓ Created: cgpa_band, skills_count, has_python/sql/powerbi")
print("  ✓ Created: composite_score, total_apps, shortlisted, max_package")
print(f"  ✓ Placement rate: {students['is_placed'].mean()*100:.1f}%")

# ── PHASE 3: KEY METRICS ──────────────────────────────────────────────────────
placed = students['is_placed'].sum()
total  = len(students)
avg_pkg = applications[applications['status']=='Offer Accepted']['package_offered_lpa'].mean()
print(f"\n{'═'*50}")
print(f"  KEY KPIs")
print(f"{'═'*50}")
print(f"  Total Students:         {total:,}")
print(f"  Placed Students:        {placed:,}  ({placed/total*100:.1f}%)")
print(f"  Total Companies:        {len(companies):,}")
print(f"  Total Applications:     {len(applications):,}")
print(f"  Average Package (LPA):  ₹{avg_pkg:.2f}")
print(f"  Max Package (LPA):      ₹{applications['package_offered_lpa'].max():.2f}")

# ── PHASE 4: VISUALIZATIONS ───────────────────────────────────────────────────
print("\n" + "─" * 50)
print("PHASE 4: GENERATING VISUALIZATIONS")
print("─" * 50)

# ── VIZ 1: Executive KPI Dashboard ───────────────────────────────────────────
fig = plt.figure(figsize=(20, 14))
fig.patch.set_facecolor('#0a0e1a')
gs  = gridspec.GridSpec(3, 4, figure=fig, hspace=0.45, wspace=0.35)

# KPI Cards
kpi_data = [
    ('Total Students', f'{total:,}', '#00d4ff'),
    ('Placed Students', f'{placed:,}', '#00ff9f'),
    ('Placement Rate', f'{placed/total*100:.1f}%', '#ffd700'),
    ('Avg Package', f'₹{avg_pkg:.1f}L', '#ff6b6b'),
]
for idx, (label, value, color) in enumerate(kpi_data):
    ax = fig.add_subplot(gs[0, idx])
    ax.set_facecolor('#1a1d2e')
    ax.set_xlim(0,1); ax.set_ylim(0,1)
    ax.add_patch(plt.Rectangle((0.05,0.05),0.9,0.9, facecolor='#0f1117',
                                edgecolor=color, linewidth=2, zorder=1))
    ax.text(0.5,0.65, value, ha='center', va='center', fontsize=24,
            fontweight='bold', color=color, zorder=2)
    ax.text(0.5,0.28, label, ha='center', va='center', fontsize=11,
            color='#aaa', zorder=2)
    ax.axis('off')

# Placement by Branch
ax2 = fig.add_subplot(gs[1, :2])
branch_data = students.groupby('branch')['is_placed'].mean().sort_values(ascending=True)*100
colors = plt.cm.RdYlGn(np.linspace(0.2,0.9,len(branch_data)))
bars = ax2.barh(branch_data.index, branch_data.values, color=colors, edgecolor='#333', height=0.7)
ax2.set_xlabel('Placement Rate (%)', color='#aaa')
ax2.set_title('Placement Rate by Branch', color='#e0e0e0', fontsize=12, pad=10)
for bar, val in zip(bars, branch_data.values):
    ax2.text(val+0.5, bar.get_y()+bar.get_height()/2,
             f'{val:.1f}%', va='center', color='#e0e0e0', fontsize=9)

# CGPA vs Package Scatter
ax3 = fig.add_subplot(gs[1, 2:])
placed_df = students[students['is_placed']==1].merge(
    applications[['student_id','package_offered_lpa']], on='student_id', how='left')
placed_df = placed_df[placed_df['package_offered_lpa']>0]
sc = ax3.scatter(placed_df['cgpa'], placed_df['package_offered_lpa'],
                  c=placed_df['internships_count'], cmap='plasma',
                  alpha=0.5, s=15, edgecolors='none')
plt.colorbar(sc, ax=ax3, label='Internships')
ax3.set_xlabel('CGPA', color='#aaa')
ax3.set_ylabel('Package (LPA)', color='#aaa')
ax3.set_title('CGPA vs Package Offered', color='#e0e0e0', fontsize=12, pad=10)

# Application Status Funnel
ax4 = fig.add_subplot(gs[2, :2])
status_order = ['Applied','Shortlisted','Interview Scheduled','Interviewed',
                 'Selected','Offer Accepted']
status_counts = applications[applications['status'].isin(status_order)]['status'].value_counts()
status_counts = status_counts.reindex(status_order, fill_value=0)
ax4.bar(range(len(status_order)), status_counts.values,
        color=PALETTE[:len(status_order)], edgecolor='#333', width=0.65)
ax4.set_xticks(range(len(status_order)))
ax4.set_xticklabels([s.replace(' ','\n') for s in status_order], fontsize=8)
ax4.set_title('Application Funnel (Stage-wise)', color='#e0e0e0', fontsize=12, pad=10)
ax4.set_ylabel('Count', color='#aaa')
for i, v in enumerate(status_counts.values):
    ax4.text(i, v+30, str(v), ha='center', color='#e0e0e0', fontsize=8)

# Skills frequency
ax5 = fig.add_subplot(gs[2, 2:])
all_skills = []
for s in students['skills'].dropna():
    all_skills.extend(s.split('|'))
from collections import Counter
skill_freq = Counter(all_skills).most_common(10)
s_names, s_counts = zip(*skill_freq)
ax5.barh(s_names[::-1], s_counts[::-1], color='#00d4ff', alpha=0.8)
ax5.set_title('Top 10 In-Demand Skills', color='#e0e0e0', fontsize=12, pad=10)
ax5.set_xlabel('Student Count', color='#aaa')

fig.suptitle('PLACEMENT MANAGEMENT ANALYTICS — EXECUTIVE DASHBOARD',
             fontsize=16, color='#00d4ff', fontweight='bold', y=0.98)

plt.savefig(OUTPUT_DIR + 'P1_executive_dashboard.png', dpi=150, bbox_inches='tight',
            facecolor='#0a0e1a')
plt.close()
print("  ✓ Saved: P1_executive_dashboard.png")

# ── VIZ 2: CGPA Distribution and Placement Correlation ────────────────────────
fig, axes = plt.subplots(1, 3, figsize=(18, 6))
fig.patch.set_facecolor('#0a0e1a')

for ax in axes: ax.set_facecolor('#1a1d2e')

# CGPA Distribution
axes[0].hist(students[students['is_placed']==1]['cgpa'], bins=20,
             alpha=0.7, color='#00ff9f', label='Placed', edgecolor='#333')
axes[0].hist(students[students['is_placed']==0]['cgpa'], bins=20,
             alpha=0.5, color='#ff6b6b', label='Unplaced', edgecolor='#333')
axes[0].set_title('CGPA Distribution: Placed vs Unplaced', color='#e0e0e0')
axes[0].set_xlabel('CGPA', color='#aaa')
axes[0].legend(facecolor='#1a1d2e', edgecolor='#444', labelcolor='#e0e0e0')

# Placement by CGPA Band
cgpa_placement = students.groupby('cgpa_band')['is_placed'].mean() * 100
axes[1].bar(cgpa_placement.index.astype(str), cgpa_placement.values,
            color=PALETTE[:len(cgpa_placement)], edgecolor='#333')
axes[1].set_title('Placement Rate by CGPA Band', color='#e0e0e0')
axes[1].set_xlabel('CGPA Band', color='#aaa')
axes[1].set_ylabel('Placement Rate (%)', color='#aaa')
for i, v in enumerate(cgpa_placement.values):
    axes[1].text(i, v+1, f'{v:.1f}%', ha='center', color='#e0e0e0', fontsize=9)

# Composite Score by Placement
axes[2].boxplot(
    [students[students['is_placed']==0]['composite_score'].dropna(),
     students[students['is_placed']==1]['composite_score'].dropna()],
    labels=['Unplaced','Placed'],
    patch_artist=True,
    boxprops=dict(facecolor='#1a1d2e', color='#00d4ff'),
    whiskerprops=dict(color='#00d4ff'),
    capprops=dict(color='#00d4ff'),
    medianprops=dict(color='#ffd700', linewidth=2),
    flierprops=dict(marker='o', markerfacecolor='#ff6b6b', markersize=3, alpha=0.4)
)
axes[2].set_title('Composite Score Distribution', color='#e0e0e0')
axes[2].set_ylabel('Score', color='#aaa')

plt.suptitle('Academic Performance Analysis', fontsize=14, color='#00d4ff', y=1.01)
plt.tight_layout()
plt.savefig(OUTPUT_DIR + 'P1_cgpa_analysis.png', dpi=150, bbox_inches='tight',
            facecolor='#0a0e1a')
plt.close()
print("  ✓ Saved: P1_cgpa_analysis.png")

# ── PHASE 5: ML MODEL — PLACEMENT PREDICTION ─────────────────────────────────
print("\n" + "─" * 50)
print("PHASE 5: ML — PLACEMENT PREDICTION MODEL")
print("─" * 50)

feature_cols = ['cgpa','backlogs','internships_count','projects_count',
                'certifications','gap_year','github_profile','linkedin_profile',
                'skills_count','has_python','has_sql','has_powerbi',
                'total_apps','avg_interview_score']

# Encode branch
le = LabelEncoder()
students['branch_enc'] = le.fit_transform(students['branch'].fillna('Unknown'))
feature_cols.append('branch_enc')

df_model = students[feature_cols + ['is_placed']].dropna()
X = df_model[feature_cols]
y = df_model['is_placed']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2,
                                                      random_state=42, stratify=y)
scaler  = StandardScaler()
X_train_sc = scaler.fit_transform(X_train)
X_test_sc  = scaler.transform(X_test)

# Train models
models = {
    'Logistic Regression': LogisticRegression(max_iter=1000, random_state=42),
    'Random Forest':       RandomForestClassifier(n_estimators=100, random_state=42),
    'Gradient Boosting':   GradientBoostingClassifier(n_estimators=100, random_state=42)
}

results = {}
print(f"\n  {'Model':<25} {'Accuracy':>10} {'AUC-ROC':>10} {'CV Mean':>10}")
print(f"  {'─'*55}")
for name, model in models.items():
    if name == 'Logistic Regression':
        model.fit(X_train_sc, y_train)
        y_pred = model.predict(X_test_sc)
        y_prob = model.predict_proba(X_test_sc)[:,1]
    else:
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        y_prob = model.predict_proba(X_test)[:,1]
    
    acc  = accuracy_score(y_test, y_pred)
    auc  = roc_auc_score(y_test, y_prob)
    if name == 'Logistic Regression':
        cv   = cross_val_score(model, X_train_sc, y_train, cv=5, scoring='accuracy').mean()
    else:
        cv   = cross_val_score(model, X_train, y_train, cv=5, scoring='accuracy').mean()
    results[name] = {'acc':acc,'auc':auc,'cv':cv,'model':model,'y_prob':y_prob}
    print(f"  {name:<25} {acc:>9.4f} {auc:>9.4f} {cv:>9.4f}")

# Best model analysis
best_name = max(results, key=lambda k: results[k]['auc'])
best      = results[best_name]
best_model= best['model']

print(f"\n  ★ Best Model: {best_name} (AUC = {best['auc']:.4f})")

# Feature importance
if hasattr(best_model, 'feature_importances_'):
    fi = pd.Series(best_model.feature_importances_, index=feature_cols).sort_values(ascending=False)
    print("\n  Top 5 Features:")
    for feat, imp in fi.head(5).items():
        print(f"    {feat:<30} {imp:.4f}")
    
    # VIZ 3: Feature Importance + Confusion Matrix + ROC
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    fig.patch.set_facecolor('#0a0e1a')
    for ax in axes: ax.set_facecolor('#1a1d2e')
    
    axes[0].barh(fi.index[:10][::-1], fi.values[:10][::-1], color='#00d4ff', alpha=0.8)
    axes[0].set_title(f'Feature Importance\n({best_name})', color='#e0e0e0')
    axes[0].set_xlabel('Importance Score', color='#aaa')
    
    if best_name != 'Logistic Regression':
        y_pred_best = best_model.predict(X_test)
    else:
        y_pred_best = best_model.predict(X_test_sc)
    cm = confusion_matrix(y_test, y_pred_best)
    im = axes[1].imshow(cm, cmap='Blues')
    plt.colorbar(im, ax=axes[1])
    for i in range(2):
        for j in range(2):
            axes[1].text(j, i, str(cm[i,j]), ha='center', va='center',
                         color='white', fontsize=16, fontweight='bold')
    axes[1].set_xticks([0,1]); axes[1].set_yticks([0,1])
    axes[1].set_xticklabels(['Pred 0','Pred 1']); axes[1].set_yticklabels(['True 0','True 1'])
    axes[1].set_title('Confusion Matrix', color='#e0e0e0')
    
    for name, res in results.items():
        fpr, tpr, _ = roc_curve(y_test, res['y_prob'])
        axes[2].plot(fpr, tpr, label=f"{name} (AUC={res['auc']:.3f})", linewidth=2)
    axes[2].plot([0,1],[0,1],'--', color='#555', linewidth=1)
    axes[2].set_xlabel('False Positive Rate', color='#aaa')
    axes[2].set_ylabel('True Positive Rate', color='#aaa')
    axes[2].set_title('ROC Curves — All Models', color='#e0e0e0')
    axes[2].legend(facecolor='#1a1d2e', edgecolor='#444', labelcolor='#e0e0e0', fontsize=9)
    
    plt.suptitle('Placement Prediction — ML Model Analysis', fontsize=14, color='#00d4ff')
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR + 'P1_ml_model_results.png', dpi=150, bbox_inches='tight',
                facecolor='#0a0e1a')
    plt.close()
    print("\n  ✓ Saved: P1_ml_model_results.png")

print("\n✅ PLACEMENT ANALYSIS COMPLETE")
