#!/usr/bin/env python3
"""
Analysis #26: Income Volatility and Overdose Deaths

Examines the relationship between income instability (year-to-year
fluctuations) and overdose mortality.
"""

import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Import shared utilities
from utils import load_overdose_data, standardize_race, RACE_COLORS

# Setup
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("colorblind")
output_dir = Path('results/26_income_volatility')
output_dir.mkdir(parents=True, exist_ok=True)

print("=" * 70)
print("INCOME VOLATILITY AND OVERDOSE DEATHS ANALYSIS")
print("=" * 70)
print()
print("Examining how income instability relates to overdose patterns")
print()

# ============================================================================
# LOAD DATA
# ============================================================================
print("Loading data...")

# Overdose data
df = load_overdose_data('data/2012-01-2024-08-overdoses.csv')
df = standardize_race(df, race_col='Race', output_col='Race_Ethnicity_Cleaned')
df = df[(df['Year'] >= 2012) & (df['Year'] <= 2023)].copy()

# Load Census population data
pop_data_wide = pd.read_csv('data/la_county_population_census.csv')
pop_data = pop_data_wide.melt(id_vars=['Year'], var_name='Race', value_name='Population')
pop_data = pop_data[pop_data['Race'] != 'TOTAL'].copy()

# Load income data (nominal and real)
income_real_nominal = pd.read_csv('data/la_county_income_real_nominal.csv')

print(f"✓ Loaded {len(df):,} overdose deaths (2012-2023)")
print(f"✓ Loaded income data")
print()

# ============================================================================
# PROCESS INCOME DATA
# ============================================================================
print("Processing income data...")

# Extract nominal income
income_nominal = income_real_nominal[['Year', 'WHITE_Median_Income', 'BLACK_Median_Income',
                                       'LATINE_Median_Income', 'ASIAN_Median_Income']]

# Reshape to long format
income_data = income_nominal.melt(id_vars=['Year'], var_name='Race', value_name='Median_Income')
income_data['Race'] = income_data['Race'].str.replace('_Median_Income', '', regex=False)

# Extract real income (inflation-adjusted to 2023 dollars)
income_real = income_real_nominal[['Year', 'WHITE_Real_Income_2023', 'BLACK_Real_Income_2023',
                                    'LATINE_Real_Income_2023', 'ASIAN_Real_Income_2023']]

income_real_long = income_real.melt(id_vars=['Year'], var_name='Race', value_name='Real_Income')
income_real_long['Race'] = income_real_long['Race'].str.replace('_Real_Income_2023', '', regex=False)

# Merge nominal and real
income_combined = income_data.merge(income_real_long, on=['Year', 'Race'], how='left')

print(f"✓ Processed income data for {len(income_combined)} race-year combinations")
print()

# ============================================================================
# CALCULATE INCOME VOLATILITY METRICS
# ============================================================================
print("Calculating income volatility metrics...")

volatility_data = []

for race in ['WHITE', 'BLACK', 'LATINE', 'ASIAN']:
    race_income = income_combined[income_combined['Race'] == race].sort_values('Year').copy()

    # Calculate year-over-year changes
    race_income['Income_YoY_Change'] = race_income['Real_Income'].pct_change() * 100
    race_income['Income_Absolute_Change'] = race_income['Real_Income'].diff()

    # Calculate rolling volatility (3-year rolling std dev)
    race_income['Rolling_Volatility'] = race_income['Real_Income'].rolling(window=3).std()

    # Calculate coefficient of variation (std dev / mean) over entire period
    cv = race_income['Real_Income'].std() / race_income['Real_Income'].mean()

    volatility_data.append({
        'Race': race,
        'CV': round(cv, 4),
        'Mean_Income': race_income['Real_Income'].mean(),
        'Std_Income': race_income['Real_Income'].std()
    })

    # Add to main dataframe
    for _, row in race_income.iterrows():
        volatility_data.append({
            'Year': row['Year'],
            'Race': race,
            'Real_Income': row['Real_Income'],
            'Income_YoY_Change': row['Income_YoY_Change'],
            'Rolling_Volatility': row['Rolling_Volatility']
        })

volatility_df = pd.DataFrame([v for v in volatility_data if 'Year' in v])
cv_df = pd.DataFrame([v for v in volatility_data if 'CV' in v])

print(f"✓ Calculated volatility metrics")
print()

# ============================================================================
# DISPLAY VOLATILITY STATISTICS
# ============================================================================
print("=" * 70)
print("INCOME VOLATILITY BY RACE (2012-2023)")
print("=" * 70)
print()

print("Coefficient of Variation (lower = more stable):")
cv_df_sorted = cv_df.sort_values('CV')
for _, row in cv_df_sorted.iterrows():
    print(f"  {row['Race']:8s}: {row['CV']:.4f} "
          f"(Mean: ${row['Mean_Income']:,.0f}, SD: ${row['Std_Income']:,.0f})")
print()

# Identify largest income drops
print("Largest year-over-year income declines:")
biggest_drops = volatility_df.nsmallest(5, 'Income_YoY_Change')[['Year', 'Race', 'Income_YoY_Change', 'Real_Income']]
for _, row in biggest_drops.iterrows():
    if pd.notna(row['Income_YoY_Change']):
        print(f"  {int(row['Year'])} {row['Race']:8s}: {row['Income_YoY_Change']:+.1f}% "
              f"(Income: ${row['Real_Income']:,.0f})")
print()

# ============================================================================
# CALCULATE OVERDOSE RATES
# ============================================================================
print("Calculating overdose rates...")

race_deaths = df.groupby(['Year', 'Race_Ethnicity_Cleaned'], observed=False).size().reset_index(name='Deaths')
race_rates = race_deaths.merge(pop_data, left_on=['Year', 'Race_Ethnicity_Cleaned'], right_on=['Year', 'Race'], how='left')
race_rates['Rate_Per_100k'] = (race_rates['Deaths'] / race_rates['Population'] * 100000).round(2)

print(f"✓ Calculated overdose rates")
print()

# ============================================================================
# MERGE WITH VOLATILITY DATA
# ============================================================================
print("Merging overdose rates with income volatility...")

merged = race_rates.merge(volatility_df, left_on=['Year', 'Race_Ethnicity_Cleaned'], right_on=['Year', 'Race'], how='inner')

print(f"✓ Merged {len(merged)} observations")
print()

# ============================================================================
# ANALYZE RELATIONSHIPS
# ============================================================================
print("=" * 70)
print("INCOME CHANGES vs OVERDOSE RATES")
print("=" * 70)
print()

# Overall correlation with year-over-year change
merged_clean = merged.dropna(subset=['Income_YoY_Change', 'Rate_Per_100k'])
if len(merged_clean) > 5:
    corr_yoy, p_yoy = stats.pearsonr(merged_clean['Income_YoY_Change'], merged_clean['Rate_Per_100k'])
    print(f"Overall: Income YoY Change vs Overdose Rate")
    print(f"  r = {corr_yoy:+.3f}, p = {p_yoy:.4f}")
    print()

# By race
print("By Race:")
for race in ['WHITE', 'BLACK', 'LATINE', 'ASIAN']:
    race_subset = merged_clean[merged_clean['Race_Ethnicity_Cleaned'] == race]
    if len(race_subset) > 5:
        corr, pval = stats.pearsonr(race_subset['Income_YoY_Change'], race_subset['Rate_Per_100k'])
        print(f"  {race:8s}: r = {corr:+.3f}, p = {pval:.4f}")
print()

# Correlation with rolling volatility
merged_vol = merged.dropna(subset=['Rolling_Volatility', 'Rate_Per_100k'])
if len(merged_vol) > 5:
    corr_vol, p_vol = stats.pearsonr(merged_vol['Rolling_Volatility'], merged_vol['Rate_Per_100k'])
    print(f"Rolling Income Volatility vs Overdose Rate:")
    print(f"  r = {corr_vol:+.3f}, p = {p_vol:.4f}")
    print()

# ============================================================================
# EXAMINE SPECIFIC PERIODS
# ============================================================================
print("=" * 70)
print("ECONOMIC STRESS PERIODS")
print("=" * 70)
print()

# 2020 COVID shock
print("COVID-19 Economic Shock (2020):")
for race in ['WHITE', 'BLACK', 'LATINE', 'ASIAN']:
    race_2019 = volatility_df[(volatility_df['Year'] == 2019) & (volatility_df['Race'] == race)]
    race_2020 = volatility_df[(volatility_df['Year'] == 2020) & (volatility_df['Race'] == race)]

    if len(race_2019) > 0 and len(race_2020) > 0:
        income_2019 = race_2019['Real_Income'].values[0]
        income_2020 = race_2020['Real_Income'].values[0]
        change = ((income_2020 - income_2019) / income_2019 * 100) if income_2019 > 0 else 0

        # Get overdose rate change
        rate_2019 = race_rates[(race_rates['Year'] == 2019) & (race_rates['Race'] == race)]['Rate_Per_100k'].values
        rate_2020 = race_rates[(race_rates['Year'] == 2020) & (race_rates['Race'] == race)]['Rate_Per_100k'].values

        if len(rate_2019) > 0 and len(rate_2020) > 0:
            rate_change = rate_2020[0] - rate_2019[0]
            print(f"  {race:8s}: Income {change:+.1f}%, Overdose rate {rate_change:+.1f} per 100k")
print()

# ============================================================================
# VISUALIZATIONS
# ============================================================================
print("Creating visualizations...")

fig, axes = plt.subplots(2, 3, figsize=(18, 12))

# Panel 1: Real income trends by race
for race in ['WHITE', 'BLACK', 'LATINE', 'ASIAN']:
    race_data = volatility_df[volatility_df['Race'] == race].sort_values('Year')
    color = RACE_COLORS.get(race, 'gray')
    axes[0, 0].plot(race_data['Year'], race_data['Real_Income'], label=race, color=color, linewidth=2, marker='o')

axes[0, 0].set_xlabel('Year', fontsize=11)
axes[0, 0].set_ylabel('Real Median Income (2023 $)', fontsize=11)
axes[0, 0].set_title('Real Income Trends by Race\n(Inflation-adjusted to 2023 $)', fontsize=12, fontweight='bold')
axes[0, 0].legend()
axes[0, 0].grid(True, alpha=0.3)
axes[0, 0].ticklabel_format(style='plain', axis='y')

# Panel 2: Year-over-year income changes
for race in ['WHITE', 'BLACK', 'LATINE', 'ASIAN']:
    race_data = volatility_df[volatility_df['Race'] == race].dropna(subset=['Income_YoY_Change']).sort_values('Year')
    color = RACE_COLORS.get(race, 'gray')
    axes[0, 1].plot(race_data['Year'], race_data['Income_YoY_Change'], label=race, color=color, linewidth=2, marker='o')

axes[0, 1].axhline(0, color='black', linestyle='--', linewidth=1, alpha=0.5)
axes[0, 1].axvspan(2020, 2021, alpha=0.2, color='red', label='COVID')
axes[0, 1].set_xlabel('Year', fontsize=11)
axes[0, 1].set_ylabel('Year-over-Year Change (%)', fontsize=11)
axes[0, 1].set_title('Income Volatility\n(Annual % Change)', fontsize=12, fontweight='bold')
axes[0, 1].legend(fontsize=9)
axes[0, 1].grid(True, alpha=0.3)

# Panel 3: Coefficient of variation
cv_df_plot = cv_df.sort_values('CV', ascending=False)
colors_cv = [RACE_COLORS.get(r, 'gray') for r in cv_df_plot['Race']]
axes[0, 2].barh(cv_df_plot['Race'], cv_df_plot['CV'], color=colors_cv, alpha=0.7, edgecolor='black')
axes[0, 2].set_xlabel('Coefficient of Variation', fontsize=11)
axes[0, 2].set_title('Income Stability by Race\n(Lower = More Stable)', fontsize=12, fontweight='bold')
# Add values
for i, row in cv_df_plot.iterrows():
    axes[0, 2].text(row['CV'] + 0.001, i, f"{row['CV']:.4f}", va='center', fontsize=9)

# Panel 4: Scatter - YoY income change vs overdose rate
if len(merged_clean) > 0:
    for race in ['WHITE', 'BLACK', 'LATINE', 'ASIAN']:
        race_data = merged_clean[merged_clean['Race_Ethnicity_Cleaned'] == race]
        if len(race_data) > 0:
            color = RACE_COLORS.get(race, 'gray')
            axes[1, 0].scatter(race_data['Income_YoY_Change'], race_data['Rate_Per_100k'],
                                label=race, color=color, s=60, alpha=0.7)

    axes[1, 0].axvline(0, color='gray', linestyle='--', alpha=0.5)
    axes[1, 0].set_xlabel('Income YoY Change (%)', fontsize=11)
    axes[1, 0].set_ylabel('Overdose Rate per 100,000', fontsize=11)
    axes[1, 0].set_title(f'Income Change vs Overdose Rate\nr = {corr_yoy:+.3f}, p = {p_yoy:.4f}',
                          fontsize=12, fontweight='bold')
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)

# Panel 5: Rolling volatility trends
for race in ['WHITE', 'BLACK', 'LATINE', 'ASIAN']:
    race_data = volatility_df[volatility_df['Race'] == race].dropna(subset=['Rolling_Volatility']).sort_values('Year')
    if len(race_data) > 0:
        color = RACE_COLORS.get(race, 'gray')
        axes[1, 1].plot(race_data['Year'], race_data['Rolling_Volatility'], label=race, color=color, linewidth=2, marker='o')

axes[1, 1].set_xlabel('Year', fontsize=11)
axes[1, 1].set_ylabel('Rolling 3-Year Std Dev ($)', fontsize=11)
axes[1, 1].set_title('Rolling Income Volatility\n(3-Year Window)', fontsize=12, fontweight='bold')
axes[1, 1].legend()
axes[1, 1].grid(True, alpha=0.3)
axes[1, 1].ticklabel_format(style='plain', axis='y')

# Panel 6: Summary text
axes[1, 2].axis('off')

summary_text = f"""
INCOME VOLATILITY SUMMARY

STABILITY RANKING (CV):
"""

for _, row in cv_df_plot.iterrows():
    summary_text += f"• {row['Race']:8s}: {row['CV']:.4f}\n"

summary_text += f"""

CORRELATIONS:
• YoY Change ↔ Overdose: r = {corr_yoy:+.3f}
• Volatility ↔ Overdose:  r = {corr_vol:+.3f}

2020 COVID SHOCK:
"""

for race in ['WHITE', 'BLACK']:
    race_2020 = volatility_df[(volatility_df['Year'] == 2020) & (volatility_df['Race'] == race)]
    if len(race_2020) > 0 and pd.notna(race_2020['Income_YoY_Change'].values[0]):
        change = race_2020['Income_YoY_Change'].values[0]
        summary_text += f"• {race:8s}: {change:+.1f}%\n"

summary_text += f"""

INTERPRETATION:
Income instability shows {"strong" if abs(corr_yoy) > 0.5 else "moderate" if abs(corr_yoy) > 0.3 else "weak"}
correlation with overdose rates.

Economic shocks and income
volatility may contribute to
overdose vulnerability.
"""

axes[1, 2].text(0.1, 0.9, summary_text, fontsize=9, verticalalignment='top',
                family='monospace', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

plt.tight_layout()
plt.savefig(output_dir / 'income_volatility.png', dpi=300, bbox_inches='tight')
print(f"✓ Saved: {output_dir / 'income_volatility.png'}")
print()

# Save results
volatility_df.to_csv(output_dir / 'income_volatility_metrics.csv', index=False)
merged.to_csv(output_dir / 'income_volatility_overdoses.csv', index=False)
cv_df.to_csv(output_dir / 'income_stability_by_race.csv', index=False)
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
print()

print("Income Stability (Coefficient of Variation):")
for _, row in cv_df_sorted.iterrows():
    print(f"  • {row['Race']:8s}: {row['CV']:.4f} ({'Most stable' if row['CV'] == cv_df_sorted['CV'].min() else 'Least stable' if row['CV'] == cv_df_sorted['CV'].max() else 'Moderate'})")
print()

print("Correlations:")
print(f"  • Income change vs overdose rate: r = {corr_yoy:+.3f} (p = {p_yoy:.4f})")
print(f"  • Income volatility vs overdose rate: r = {corr_vol:+.3f} (p = {p_vol:.4f})")
print()

print("=" * 70)
