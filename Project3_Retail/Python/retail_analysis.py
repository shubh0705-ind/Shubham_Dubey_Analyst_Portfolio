"""
=============================================================
PROJECT 3: RETAIL SALES FORECASTING & INSIGHT ENGINE
Python: EDA + Prophet Forecasting + Customer Segmentation + Cohort Analysis
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

from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from prophet import Prophet

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
PALETTE = ['#00d4ff','#ff6b6b','#ffd700','#00ff9f','#b44fff','#ff8c00']
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(BASE_DIR, 'Images') + os.sep

print("=" * 60)
print("RETAIL SALES FORECASTING & INSIGHT ENGINE")
print("=" * 60)

# ── LOAD DATA ─────────────────────────────────────────────────────────────────
products     = pd.read_csv(os.path.join(BASE_DIR, 'Data', 'products.csv'))
customers    = pd.read_csv(os.path.join(BASE_DIR, 'Data', 'customers.csv'))
transactions = pd.read_csv(os.path.join(BASE_DIR, 'Data', 'transactions.csv'),
                            parse_dates=['order_date'])

print(f"\n📊 Data Loaded:")
print(f"  Products:     {len(products):,} | Customers: {len(customers):,} | Transactions: {len(transactions):,}")

# ── PHASE 1: DATA CLEANING ────────────────────────────────────────────────────
print("\n" + "─" * 50)
print("PHASE 1: DATA CLEANING & VALIDATION")
print("─" * 50)

# Remove returns for revenue analysis
df_sales = transactions[transactions['return_flag'] == 0].copy()
print(f"  Total transactions: {len(transactions):,}")
print(f"  After removing returns ({(transactions['return_flag']==1).sum():,}): {len(df_sales):,}")

# Outlier treatment on net_amount
q1, q3 = df_sales['net_amount'].quantile([0.01, 0.99])
outliers_before = len(df_sales)
df_sales = df_sales[(df_sales['net_amount'] >= q1) & (df_sales['net_amount'] <= q3)]
print(f"  Outliers removed (price): {outliers_before - len(df_sales)}")

# Feature engineering
df_sales['year_month']  = df_sales['order_date'].dt.to_period('M')
df_sales['day_of_week'] = df_sales['order_date'].dt.day_name()
df_sales['is_weekend']  = df_sales['order_date'].dt.dayofweek >= 5

# Merge product category
df_sales = df_sales.merge(products[['product_id','category','cost_price']], on='product_id', how='left')
df_sales['gross_profit'] = df_sales['net_amount'] - df_sales['quantity'] * df_sales['cost_price']
df_sales['margin_pct']   = df_sales['gross_profit'] / df_sales['net_amount'] * 100

print(f"  ✓ Feature engineering complete")

# ── PHASE 2: KPI SUMMARY ──────────────────────────────────────────────────────
total_rev  = df_sales['net_amount'].sum()
total_orders = len(df_sales)
aov = total_rev / total_orders
total_cust = df_sales['customer_id'].nunique()

print(f"\n{'═'*50}")
print(f"  EXECUTIVE KPIs")
print(f"{'═'*50}")
print(f"  Total Revenue:       ₹{total_rev/1e7:.2f} Cr")
print(f"  Total Orders:        {total_orders:,}")
print(f"  Avg Order Value:     ₹{aov:.2f}")
print(f"  Active Customers:    {total_cust:,}")
print(f"  Avg Margin:          {df_sales['margin_pct'].mean():.1f}%")

# ── PHASE 3: PROPHET FORECASTING ──────────────────────────────────────────────
print("\n" + "─" * 50)
print("PHASE 3: PROPHET TIME-SERIES FORECASTING")
print("─" * 50)

# Monthly revenue for Prophet
monthly_rev = df_sales.groupby('year_month')['net_amount'].sum().reset_index()
monthly_rev.columns = ['ds', 'y']
monthly_rev['ds'] = monthly_rev['ds'].dt.to_timestamp()
monthly_rev = monthly_rev.sort_values('ds')

print(f"  Training on {len(monthly_rev)} months of data...")
print(f"  Date range: {monthly_rev['ds'].min().date()} → {monthly_rev['ds'].max().date()}")

m = Prophet(
    yearly_seasonality=True,
    weekly_seasonality=False,
    daily_seasonality=False,
    seasonality_mode='multiplicative',
    changepoint_prior_scale=0.1,
    seasonality_prior_scale=10,
    interval_width=0.95
)
m.fit(monthly_rev)

future   = m.make_future_dataframe(periods=6, freq='MS')
forecast = m.predict(future)

# MAPE calculation
merged = monthly_rev.merge(forecast[['ds','yhat']], on='ds')
mape = np.mean(np.abs((merged['y'] - merged['yhat']) / merged['y'])) * 100
print(f"  ✓ MAPE: {mape:.2f}%")
print(f"  ✓ 6-month forecast generated")

next_6 = forecast[forecast['ds'] > monthly_rev['ds'].max()][['ds','yhat','yhat_lower','yhat_upper']]
print("\n  Forecast Preview (Next 6 Months):")
for _, row in next_6.iterrows():
    print(f"    {row['ds'].strftime('%b %Y')}: ₹{row['yhat']:>10,.0f}  [{row['yhat_lower']:,.0f} – {row['yhat_upper']:,.0f}]")

# ── PHASE 4: RFM CUSTOMER SEGMENTATION ───────────────────────────────────────
print("\n" + "─" * 50)
print("PHASE 4: RFM CUSTOMER SEGMENTATION")
print("─" * 50)

snapshot_date = df_sales['order_date'].max() + pd.Timedelta(days=1)

rfm = df_sales.groupby('customer_id').agg(
    Recency  =('order_date', lambda x: (snapshot_date - x.max()).days),
    Frequency=('transaction_id', 'count'),
    Monetary =('net_amount', 'sum')
).reset_index()

# RFM Scores
for col, ascending in [('Recency', False), ('Frequency', True), ('Monetary', True)]:
    rfm[f'{col[0]}_score'] = pd.qcut(rfm[col], q=5, labels=[5,4,3,2,1] if not ascending else [1,2,3,4,5], duplicates='drop').astype(int)

rfm['RFM_Score'] = rfm['R_score'] + rfm['F_score'] + rfm['M_score']

def segment_customer(row):
    r, f, m = row['R_score'], row['F_score'], row['M_score']
    if r >= 4 and f >= 4 and m >= 4: return 'Champions'
    if r >= 3 and f >= 3:            return 'Loyal Customers'
    if r >= 4 and f <= 2:            return 'New Customers'
    if r >= 3 and m >= 3:            return 'Potential Loyalists'
    if r <= 2 and f >= 3:            return 'At Risk'
    if r <= 2 and m >= 3:            return 'Cannot Lose Them'
    if r <= 1:                       return 'Lost'
    return 'Others'

rfm['Segment'] = rfm.apply(segment_customer, axis=1)
seg_summary = rfm.groupby('Segment').agg(
    Customers=('customer_id','count'),
    Avg_Recency=('Recency','mean'),
    Avg_Frequency=('Frequency','mean'),
    Avg_Monetary=('Monetary','mean')
).round(1)

print("\n  RFM Segment Summary:")
print(f"  {'Segment':<25} {'Customers':>10} {'Avg Days Since':>15} {'Avg Orders':>12} {'Avg Spend':>12}")
print(f"  {'─'*75}")
for seg, row in seg_summary.iterrows():
    print(f"  {seg:<25} {int(row['Customers']):>10,} {row['Avg_Recency']:>14.0f} {row['Avg_Frequency']:>11.1f} ₹{row['Avg_Monetary']:>10,.0f}")

# K-Means on RFM
rfm_scaled = StandardScaler().fit_transform(rfm[['Recency','Frequency','Monetary']])
inertias   = []
for k in range(2, 9):
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    km.fit(rfm_scaled)
    inertias.append(km.inertia_)

optimal_k = 4
km_final  = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
rfm['Cluster'] = km_final.fit_predict(rfm_scaled)
sil_score = silhouette_score(rfm_scaled, rfm['Cluster'])
print(f"\n  K-Means (k=4) Silhouette Score: {sil_score:.4f}")

# ── PHASE 5: COHORT ANALYSIS ──────────────────────────────────────────────────
print("\n" + "─" * 50)
print("PHASE 5: COHORT RETENTION ANALYSIS")
print("─" * 50)

df_sales['cohort_month'] = df_sales.groupby('customer_id')['order_date'].transform('min').dt.to_period('M')
df_sales['order_period'] = df_sales['order_date'].dt.to_period('M')
df_sales['cohort_index'] = (df_sales['order_period'] - df_sales['cohort_month']).apply(lambda x: x.n)

cohort_data = df_sales.groupby(['cohort_month','cohort_index'])['customer_id'].nunique().reset_index()
cohort_pivot = cohort_data.pivot_table(index='cohort_month', columns='cohort_index', values='customer_id')

cohort_size = cohort_pivot.iloc[:,0]
retention   = cohort_pivot.divide(cohort_size, axis=0) * 100

print(f"  Cohorts generated: {len(retention)} monthly cohorts")
print(f"  Month-1 retention range: {retention.iloc[:,1].min():.1f}% – {retention.iloc[:,1].max():.1f}%")

# ── PHASE 6: VISUALIZATIONS ───────────────────────────────────────────────────
print("\n" + "─" * 50)
print("PHASE 6: GENERATING DASHBOARDS")
print("─" * 50)

# VIZ 1: Executive Revenue Dashboard
fig = plt.figure(figsize=(22, 14))
fig.patch.set_facecolor('#0a0e1a')
gs = gridspec.GridSpec(3, 3, figure=fig, hspace=0.5, wspace=0.4)

# KPI cards
kpis = [
    ('Total Revenue', f'₹{total_rev/1e7:.2f}Cr', '#00d4ff'),
    ('Total Orders',  f'{total_orders:,}', '#00ff9f'),
    ('Avg Order Val', f'₹{aov:.0f}', '#ffd700'),
]
for i, (label, val, color) in enumerate(kpis):
    ax = fig.add_subplot(gs[0, i])
    ax.set_facecolor('#1a1d2e')
    ax.add_patch(plt.Rectangle((0.05,0.05),0.9,0.9, facecolor='#0f1117',
                                edgecolor=color, linewidth=2))
    ax.text(0.5,0.62, val, ha='center', va='center', fontsize=22,
            fontweight='bold', color=color)
    ax.text(0.5,0.28, label, ha='center', va='center', fontsize=11, color='#aaa')
    ax.set_xlim(0,1); ax.set_ylim(0,1); ax.axis('off')

# Monthly Revenue Trend + Forecast
ax2 = fig.add_subplot(gs[1, :])
ax2.fill_between(forecast['ds'], forecast['yhat_lower'], forecast['yhat_upper'],
                  alpha=0.15, color='#00d4ff', label='95% CI')
ax2.plot(forecast['ds'], forecast['yhat'], color='#00d4ff', linewidth=2, label='Forecast', linestyle='--')
ax2.plot(monthly_rev['ds'], monthly_rev['y'], color='#ffd700', linewidth=2, label='Actual Revenue')
ax2.axvline(monthly_rev['ds'].max(), color='#ff6b6b', linestyle=':', linewidth=1.5, label='Forecast Start')
ax2.set_title(f'Monthly Revenue Trend + Prophet Forecast (MAPE={mape:.1f}%)',
              color='#e0e0e0', fontsize=12)
ax2.set_ylabel('Revenue (₹)')
ax2.legend(facecolor='#1a1d2e', edgecolor='#444', labelcolor='#e0e0e0')
ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'₹{x/1e5:.0f}L'))

# Category Revenue
ax3 = fig.add_subplot(gs[2, 0])
cat_rev = df_sales.groupby('category')['net_amount'].sum().sort_values(ascending=True)
colors  = plt.cm.plasma(np.linspace(0.2, 0.9, len(cat_rev)))
ax3.barh(cat_rev.index, cat_rev.values, color=colors, edgecolor='#333')
ax3.set_title('Revenue by Category', color='#e0e0e0')
ax3.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'₹{x/1e5:.0f}L'))

# Channel performance
ax4 = fig.add_subplot(gs[2, 1])
ch  = df_sales.groupby('channel')['net_amount'].sum()
ax4.pie(ch.values, labels=ch.index, colors=PALETTE[:len(ch)],
        autopct='%1.1f%%', startangle=90,
        wedgeprops=dict(width=0.5, edgecolor='#0a0e1a', linewidth=2),
        textprops={'color':'#e0e0e0'})
ax4.set_title('Revenue by Channel', color='#e0e0e0')

# Regional Revenue
ax5 = fig.add_subplot(gs[2, 2])
reg = df_sales.groupby('region')['net_amount'].sum().sort_values(ascending=False)
ax5.bar(reg.index, reg.values, color=PALETTE[:len(reg)], edgecolor='#333')
ax5.set_title('Revenue by Region', color='#e0e0e0')
ax5.set_ylabel('Revenue (₹)')
ax5.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'₹{x/1e5:.0f}L'))
plt.setp(ax5.xaxis.get_majorticklabels(), rotation=30, ha='right')

fig.suptitle('RETAIL SALES FORECASTING & INSIGHT ENGINE — EXECUTIVE DASHBOARD',
             fontsize=14, color='#00d4ff', fontweight='bold', y=0.99)

plt.savefig(OUT_DIR + 'P3_executive_dashboard.png', dpi=150, bbox_inches='tight',
            facecolor='#0a0e1a')
plt.close()
print("  ✓ Saved: P3_executive_dashboard.png")

# VIZ 2: RFM Segmentation
fig, axes = plt.subplots(1, 2, figsize=(16, 7))
fig.patch.set_facecolor('#0a0e1a')
for ax in axes: ax.set_facecolor('#1a1d2e')

seg_counts = rfm['Segment'].value_counts()
axes[0].pie(seg_counts.values, labels=seg_counts.index, colors=PALETTE[:len(seg_counts)],
            autopct='%1.1f%%', startangle=90,
            wedgeprops=dict(width=0.6, edgecolor='#0a0e1a', linewidth=2),
            textprops={'color':'#e0e0e0', 'fontsize':9})
axes[0].set_title('Customer Segmentation (RFM)', color='#e0e0e0', fontsize=12)

sc = axes[1].scatter(rfm['Frequency'], rfm['Monetary'],
                      c=rfm['R_score'], cmap='plasma',
                      alpha=0.4, s=8, edgecolors='none')
plt.colorbar(sc, ax=axes[1], label='Recency Score')
axes[1].set_xlabel('Frequency (Orders)')
axes[1].set_ylabel('Monetary (₹)')
axes[1].set_title('RFM Scatter: Frequency vs Monetary', color='#e0e0e0')
axes[1].yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'₹{x/1e3:.0f}K'))

plt.suptitle('Customer Segmentation Analysis', fontsize=14, color='#00d4ff')
plt.tight_layout()
plt.savefig(OUT_DIR + 'P3_rfm_segmentation.png', dpi=150, bbox_inches='tight',
            facecolor='#0a0e1a')
plt.close()
print("  ✓ Saved: P3_rfm_segmentation.png")

# VIZ 3: Cohort Retention Heatmap
fig, ax = plt.subplots(figsize=(18, 8))
fig.patch.set_facecolor('#0a0e1a')
ax.set_facecolor('#1a1d2e')
ret_display = retention.iloc[:12, :7].fillna(0)
sns.heatmap(ret_display, annot=True, fmt='.0f', cmap='YlOrRd',
            ax=ax, linewidths=0.5, linecolor='#0a0e1a',
            cbar_kws={'label':'Retention %'},
            annot_kws={'size':10, 'weight':'bold'})
ax.set_title('Monthly Cohort Retention Analysis (%)', color='#e0e0e0', fontsize=14)
ax.set_xlabel('Months Since First Purchase')
ax.set_ylabel('Cohort Month')
plt.tight_layout()
plt.savefig(OUT_DIR + 'P3_cohort_retention.png', dpi=150, bbox_inches='tight',
            facecolor='#0a0e1a')
plt.close()
print("  ✓ Saved: P3_cohort_retention.png")

# Save enriched data
rfm.to_csv(os.path.join(BASE_DIR, 'Data', 'rfm_segments.csv'), index=False)
forecast.to_csv(os.path.join(BASE_DIR, 'Data', 'forecast_results.csv'), index=False)
print("  ✓ Saved: rfm_segments.csv + forecast_results.csv")

print("\n✅ RETAIL ANALYSIS COMPLETE")
