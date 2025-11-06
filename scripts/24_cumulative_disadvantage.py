#!/usr/bin/env python3
"""
Analysis #24: Cumulative Disadvantage Score

Creates a composite index combining multiple SES indicators to measure
cumulative disadvantage and its relationship with overdose deaths.
"""

import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from sklearn.preprocessing import StandardScaler

# Import shared utilities
from utils import load_overdose_data, standardize_race, RACE_COLORS

# Setup
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("colorblind")
output_dir = Path('results/24_cumulative_disadvantage')
output_dir.mkdir(parents=True, exist_ok=True)

print("=" * 70)
print("CUMULATIVE DISADVANTAGE SCORE ANALYSIS")
print("=" * 70)
print()
print("Creating composite index of socioeconomic disadvantage")
print("combining poverty, income, and housing burden")
print()

# ============================================================================
# LOAD DATA
# ============================================================================
print("Loading data...")

# Overdose data
df = load_overdose_data('data/2012-01-2024-08-overdoses.csv')
df = standardize_race(df, race_col='Race', output_col='Race_Ethnicity_Cleaned')
df = df[(df['Year'] >= 2012) & (df['Year'] <= 2023)].copy()

# Load Census SES data
pop_data_wide = pd.read_csv('data/la_county_population_census.csv')
income_data_wide = pd.read_csv('data/la_county_income_by_race.csv')
poverty_data_wide = pd.read_csv('data/la_county_poverty_by_race.csv')

# Load housing data
housing_data = pd.read_csv('data/la_county_housing_costs.csv')

# Reshape population to long format
pop_data = pop_data_wide.melt(id_vars=['Year'], var_name='Race', value_name='Population')
pop_data = pop_data[pop_data['Race'] != 'TOTAL'].copy()

# Reshape poverty to long format
poverty_data = poverty_data_wide.melt(id_vars=['Year'], var_name='Race', value_name='Poverty_Rate')
poverty_data['Race'] = poverty_data['Race'].str.replace('_Poverty_Rate', '', regex=False)

# Reshape income to long format
income_data = income_data_wide.melt(id_vars=['Year'], var_name='Race', value_name='Median_Income')
income_data['Race'] = income_data['Race'].str.replace('_Median_Income', '', regex=False)

print(f"✓ Loaded {len(df):,} overdose deaths (2012-2023)")
print(f"✓ Loaded SES data")
print()

# ============================================================================
# CALCULATE DEATH RATES
# ============================================================================
print("Calculating overdose rates by race and year...")

death_counts = df.groupby(['Year', 'Race_Ethnicity_Cleaned'], observed=False).size().reset_index(name='Deaths')

# Merge with population
rates_df = death_counts.merge(pop_data, left_on=['Year', 'Race_Ethnicity_Cleaned'], right_on=['Year', 'Race'], how='left')
rates_df['Rate_Per_100k'] = (rates_df['Deaths'] / rates_df['Population'] * 100000).round(2)

print(f"✓ Calculated rates for {len(rates_df)} race-year combinations")
print()

# ============================================================================
# MERGE SES INDICATORS
# ============================================================================
print("Merging SES indicators...")

# Merge all SES data
ses_data = pop_data.merge(poverty_data, on=['Year', 'Race'], how='left')
ses_data = ses_data.merge(income_data, on=['Year', 'Race'], how='left')

# Add housing costs (apply to all races)
ses_data = ses_data.merge(housing_data[['Year', 'Median_Gross_Rent', 'Median_Home_Value']],
                           on='Year', how='left')

# Calculate housing cost burden (rent as % of income)
ses_data['Rent_Burden_Pct'] = (ses_data['Median_Gross_Rent'] * 12 / ses_data['Median_Income'] * 100).round(2)

print(f"✓ Merged {len(ses_data)} observations with SES data")
print()

# Display available indicators
print("Available SES indicators:")
print("  1. Poverty Rate (% below poverty line)")
print("  2. Median Income ($)")
print("  3. Rent Burden (% of income spent on rent)")
print()

# ============================================================================
# CREATE CUMULATIVE DISADVANTAGE SCORE
# ============================================================================
print("=" * 70)
print("CREATING CUMULATIVE DISADVANTAGE SCORE")
print("=" * 70)
print()

# Prepare data for scoring
score_data = ses_data[['Year', 'Race', 'Population', 'Poverty_Rate', 'Median_Income', 'Rent_Burden_Pct']].copy()
score_data = score_data.dropna()

print(f"Complete data for {len(score_data)} race-year combinations")
print()

# Standardize indicators (z-scores)
# Higher disadvantage = higher score, so we flip income (low income = disadvantage)

scaler = StandardScaler()

# Create component scores
# For poverty and rent burden: higher = more disadvantage (positive z-score)
# For income: lower = more disadvantage (negative z-score, so we flip it)

score_data['Poverty_z'] = scaler.fit_transform(score_data[['Poverty_Rate']])
score_data['Income_z'] = scaler.fit_transform(score_data[['Median_Income']]) * -1  # Flip so low income = high score
score_data['Rent_Burden_z'] = scaler.fit_transform(score_data[['Rent_Burden_Pct']])

# Calculate cumulative disadvantage score (average of z-scores)
score_data['Disadvantage_Score'] = (
    (score_data['Poverty_z'] + score_data['Income_z'] + score_data['Rent_Burden_z']) / 3
).round(3)

# Create disadvantage categories
score_data['Disadvantage_Level'] = pd.cut(score_data['Disadvantage_Score'],
                                           bins=[-np.inf, -0.5, 0.5, np.inf],
                                           labels=['Low', 'Medium', 'High'])

print("Disadvantage Score Components (standardized):")
print("  • Poverty Rate (higher = more disadvantage)")
print("  • Median Income (lower = more disadvantage)")
print("  • Rent Burden (higher = more disadvantage)")
print()
print("Final score = average of 3 z-scores")
print()

# Display score distribution by race
print("Average Disadvantage Score by Race (2023):")
score_2023 = score_data[score_data['Year'] == 2023].sort_values('Disadvantage_Score', ascending=False)
for _, row in score_2023.iterrows():
    print(f"  {row['Race']:8s}: {row['Disadvantage_Score']:+.2f} "
          f"(Poverty: {row['Poverty_Rate']:.1f}%, Income: ${row['Median_Income']:,.0f}, "
          f"Rent: {row['Rent_Burden_Pct']:.1f}%)")
print()

# ============================================================================
# MERGE WITH OVERDOSE RATES
# ============================================================================
print("Merging with overdose rates...")

merged = rates_df.merge(score_data, left_on=['Year', 'Race_Ethnicity_Cleaned'], right_on=['Year', 'Race'], how='inner')

print(f"✓ Merged {len(merged)} observations")
print()

# ============================================================================
# ANALYZE RELATIONSHIP BETWEEN DISADVANTAGE AND OVERDOSE RATES
# ============================================================================
print("=" * 70)
print("DISADVANTAGE SCORE vs OVERDOSE RATES")
print("=" * 70)
print()

# Overall correlation
corr, pval = stats.pearsonr(merged['Disadvantage_Score'], merged['Rate_Per_100k'])
print(f"Overall correlation: r = {corr:+.3f}, p = {pval:.6f}")
print()

# By disadvantage level
print("Average overdose rates by disadvantage level:")
for level in ['Low', 'Medium', 'High']:
    subset = merged[merged['Disadvantage_Level'] == level]
    if len(subset) > 0:
        mean_rate = subset['Rate_Per_100k'].mean()
        print(f"  {level:8s}: {mean_rate:.1f} per 100k (N = {len(subset)})")
print()

# Compare extreme groups
low_disadv = merged[merged['Disadvantage_Level'] == 'Low']['Rate_Per_100k'].mean()
high_disadv = merged[merged['Disadvantage_Level'] == 'High']['Rate_Per_100k'].mean()
ratio = high_disadv / low_disadv if low_disadv > 0 else np.nan

print(f"High vs Low disadvantage ratio: {ratio:.2f}x")
print()

# Statistical test
low_rates = merged[merged['Disadvantage_Level'] == 'Low']['Rate_Per_100k']
high_rates = merged[merged['Disadvantage_Level'] == 'High']['Rate_Per_100k']
t_stat, t_pval = stats.ttest_ind(high_rates, low_rates)
print(f"t-test (High vs Low): t = {t_stat:.2f}, p = {t_pval:.6f}")
print()

# ============================================================================
# EXAMINE INDIVIDUAL COMPONENTS
# ============================================================================
print("=" * 70)
print("INDIVIDUAL COMPONENT CORRELATIONS")
print("=" * 70)
print()

components = {
    'Poverty Rate': 'Poverty_Rate',
    'Median Income': 'Median_Income',
    'Rent Burden': 'Rent_Burden_Pct'
}

component_corrs = []

for comp_name, comp_col in components.items():
    subset = merged.dropna(subset=[comp_col, 'Rate_Per_100k'])
    if len(subset) > 2:
        corr_comp, pval_comp = stats.pearsonr(subset[comp_col], subset['Rate_Per_100k'])
        print(f"{comp_name:20s}: r = {corr_comp:+.3f}, p = {pval_comp:.6f}")

        component_corrs.append({
            'Component': comp_name,
            'Correlation': corr_comp,
            'P_value': pval_comp
        })

print()

# ============================================================================
# TEMPORAL TRENDS
# ============================================================================
print("=" * 70)
print("TEMPORAL TRENDS IN DISADVANTAGE")
print("=" * 70)
print()

# Average disadvantage score by year
yearly_disadv = score_data.groupby('Year')['Disadvantage_Score'].mean().reset_index()
yearly_disadv.columns = ['Year', 'Avg_Disadvantage']

print("Average disadvantage score over time:")
for _, row in yearly_disadv.iterrows():
    print(f"  {int(row['Year'])}: {row['Avg_Disadvantage']:+.2f}")
print()

# ============================================================================
# VISUALIZATIONS
# ============================================================================
print("Creating visualizations...")

fig, axes = plt.subplots(2, 3, figsize=(18, 12))

# Panel 1: Scatter plot - disadvantage vs overdose rate
axes[0, 0].scatter(merged['Disadvantage_Score'], merged['Rate_Per_100k'], alpha=0.6, s=50)

# Add regression line
z = np.polyfit(merged['Disadvantage_Score'], merged['Rate_Per_100k'], 1)
p = np.poly1d(z)
x_line = np.linspace(merged['Disadvantage_Score'].min(), merged['Disadvantage_Score'].max(), 100)
axes[0, 0].plot(x_line, p(x_line), "r--", alpha=0.8, linewidth=2)

axes[0, 0].set_xlabel('Cumulative Disadvantage Score', fontsize=11)
axes[0, 0].set_ylabel('Overdose Rate per 100,000', fontsize=11)
axes[0, 0].set_title(f'Cumulative Disadvantage vs Overdose Rate\nr = {corr:+.3f}, p = {pval:.6f}',
                      fontsize=12, fontweight='bold')
axes[0, 0].axvline(0, color='gray', linestyle=':', alpha=0.5)

# Panel 2: Bar chart - rates by disadvantage level
level_data = merged.groupby('Disadvantage_Level')['Rate_Per_100k'].agg(['mean', 'sem']).reset_index()
colors_bar = ['lightblue', 'orange', 'darkred']
axes[0, 1].bar(level_data['Disadvantage_Level'], level_data['mean'],
                yerr=level_data['sem'], capsize=10, color=colors_bar, alpha=0.7, edgecolor='black')
axes[0, 1].set_ylabel('Overdose Rate per 100,000', fontsize=11)
axes[0, 1].set_xlabel('Disadvantage Level', fontsize=11)
axes[0, 1].set_title(f'Rates by Disadvantage Level\n(Ratio: {ratio:.2f}x)', fontsize=12, fontweight='bold')
# Add values
for i, row in level_data.iterrows():
    axes[0, 1].text(i, row['mean'] + row['sem'] + 2, f"{row['mean']:.1f}", ha='center', fontsize=10, fontweight='bold')

# Panel 3: Component correlations
comp_df = pd.DataFrame(component_corrs)
colors_comp = ['red' if abs(r) > 0.3 else 'gray' for r in comp_df['Correlation']]
axes[0, 2].barh(comp_df['Component'], comp_df['Correlation'], color=colors_comp, alpha=0.7, edgecolor='black')
axes[0, 2].axvline(0, color='black', linestyle='--', linewidth=1)
axes[0, 2].set_xlabel('Correlation with Overdose Rate', fontsize=11)
axes[0, 2].set_title('Individual Component Correlations\n(Red = |r| > 0.3)', fontsize=12, fontweight='bold')
axes[0, 2].set_xlim(-0.5, 0.8)
# Add values
for i, row in comp_df.iterrows():
    axes[0, 2].text(row['Correlation'] + 0.02, i, f"{row['Correlation']:+.3f}", va='center', fontsize=9)

# Panel 4: Disadvantage score by race over time
for race in ['WHITE', 'BLACK', 'LATINE', 'ASIAN']:
    race_data = score_data[score_data['Race'] == race].sort_values('Year')
    color = RACE_COLORS.get(race, 'gray')
    axes[1, 0].plot(race_data['Year'], race_data['Disadvantage_Score'], label=race, color=color, linewidth=2, marker='o')

axes[1, 0].axhline(0, color='gray', linestyle='--', linewidth=1, alpha=0.5)
axes[1, 0].set_xlabel('Year', fontsize=11)
axes[1, 0].set_ylabel('Cumulative Disadvantage Score', fontsize=11)
axes[1, 0].set_title('Disadvantage Score Trends by Race', fontsize=12, fontweight='bold')
axes[1, 0].legend()
axes[1, 0].grid(True, alpha=0.3)

# Panel 5: Overdose rate vs disadvantage by race (2023)
merged_2023 = merged[merged['Year'] == 2023]
for race in ['WHITE', 'BLACK', 'LATINE', 'ASIAN']:
    race_data = merged_2023[merged_2023['Race_Ethnicity_Cleaned'] == race]
    if len(race_data) > 0:
        color = RACE_COLORS.get(race, 'gray')
        axes[1, 1].scatter(race_data['Disadvantage_Score'], race_data['Rate_Per_100k'],
                            label=race, color=color, s=200, alpha=0.7, edgecolors='black', linewidth=2)

axes[1, 1].axhline(merged_2023['Rate_Per_100k'].mean(), color='gray', linestyle=':', alpha=0.5, label='Mean rate')
axes[1, 1].axvline(merged_2023['Disadvantage_Score'].mean(), color='gray', linestyle=':', alpha=0.5, label='Mean score')
axes[1, 1].set_xlabel('Cumulative Disadvantage Score', fontsize=11)
axes[1, 1].set_ylabel('Overdose Rate per 100,000', fontsize=11)
axes[1, 1].set_title('2023: Disadvantage vs Overdose Rate\n(by Race)', fontsize=12, fontweight='bold')
axes[1, 1].legend()
axes[1, 1].grid(True, alpha=0.3)

# Panel 6: Summary text
axes[1, 2].axis('off')

summary_text = f"""
CUMULATIVE DISADVANTAGE SUMMARY

SCORE COMPONENTS:
• Poverty Rate
• Median Income (inverted)
• Rent Burden

OVERALL RELATIONSHIP:
• Correlation: r = {corr:+.3f}
• Significance: p = {pval:.6f}

RATES BY LEVEL:
• Low disadvantage:  {low_disadv:.1f} per 100k
• High disadvantage: {high_disadv:.1f} per 100k
• Ratio (high/low):  {ratio:.2f}x

2023 DISADVANTAGE SCORES:
"""

for _, row in score_2023.iterrows():
    summary_text += f"• {row['Race']:8s}: {row['Disadvantage_Score']:+.2f}\n"

summary_text += f"""

INTERPRETATION:
Cumulative disadvantage (combining
poverty, low income, and high rent
burden) shows {"strong" if abs(corr) > 0.5 else "moderate" if abs(corr) > 0.3 else "weak"}
correlation with overdose rates.

Multiple stressors compound to
increase vulnerability to overdose.
"""

axes[1, 2].text(0.1, 0.9, summary_text, fontsize=9, verticalalignment='top',
                family='monospace', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

plt.tight_layout()
plt.savefig(output_dir / 'cumulative_disadvantage.png', dpi=300, bbox_inches='tight')
print(f"✓ Saved: {output_dir / 'cumulative_disadvantage.png'}")
print()

# Save results
score_data.to_csv(output_dir / 'cumulative_disadvantage_scores.csv', index=False)
merged.to_csv(output_dir / 'disadvantage_overdose_rates.csv', index=False)
comp_df.to_csv(output_dir / 'disadvantage_component_correlations.csv', index=False)
print(f"✓ Saved CSV results")
print()

# ============================================================================
# SUMMARY
# ============================================================================
print("=" * 70)
print("ANALYSIS COMPLETE")
print("=" * 70)
print()

print("KEY FINDINGS:")
print(f"• Cumulative disadvantage score correlates with overdose rates (r = {corr:+.3f})")
print(f"• High-disadvantage areas have {ratio:.2f}x higher rates than low-disadvantage areas")
print(f"• Statistical significance: p = {pval:.6f}")
print()

# Individual component contributions
print("Component correlations:")
for _, row in comp_df.iterrows():
    print(f"  • {row['Component']:20s}: r = {row['Correlation']:+.3f}")

print()
print("=" * 70)
