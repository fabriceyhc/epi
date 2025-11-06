#!/usr/bin/env python
# coding: utf-8

"""
Temporal Correlation Analysis: SES Changes vs Overdose Rate Changes
Examines whether improvements in poverty, income, and age correlate with
changes in overdose death rates by race over time (2012-2023)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import seaborn as sns

print("="*70)
print("TEMPORAL CORRELATION ANALYSIS: SES vs OVERDOSE RATES")
print("="*70)

# Load all datasets
print("\nLoading data...")
overdose_df = pd.read_csv('results/13_temporal_correlation/race_rates_annual.csv')
poverty_df = pd.read_csv('data/la_county_poverty_by_race.csv')
income_df = pd.read_csv('data/la_county_income_by_race.csv')
age_df = pd.read_csv('data/la_county_age_by_race.csv')

print(f"✓ Loaded {len(overdose_df)} overdose records")
print(f"✓ Loaded {len(poverty_df)} poverty records")
print(f"✓ Loaded {len(income_df)} income records")
print(f"✓ Loaded {len(age_df)} age records")

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
colors = {
    'WHITE': '#4472C4',
    'BLACK': '#ED7D31',
    'LATINE': '#A5A5A5',
    'ASIAN': '#FFC000'
}

race_labels = {
    'WHITE': 'White (NH)',
    'BLACK': 'Black (NH)',
    'LATINE': 'Latine',
    'ASIAN': 'Asian (NH)'
}

# ============================================================================
# ANALYSIS 1: Correlation Between Poverty and Overdose Rates
# ============================================================================

print("\n" + "="*70)
print("CORRELATION: POVERTY RATE vs OVERDOSE DEATH RATE")
print("="*70)

correlation_results = []

for race in ['WHITE', 'BLACK', 'LATINE', 'ASIAN']:
    # Get overdose rates for this race
    overdose_race = overdose_df[overdose_df['Race'] == race].copy()
    overdose_race = overdose_race[overdose_race['Year'] != 2020]  # Exclude 2020 (no SES data)

    # Merge with poverty data
    poverty_race = poverty_df[['Year', f'{race}_Poverty_Rate']].copy()
    poverty_race.columns = ['Year', 'Poverty_Rate']

    merged = overdose_race.merge(poverty_race, on='Year')

    # Calculate correlation
    if len(merged) > 2:
        corr, pval = stats.pearsonr(merged['Poverty_Rate'], merged['Rate_per_100k'])

        correlation_results.append({
            'Race': race,
            'Metric': 'Poverty Rate',
            'Correlation': corr,
            'P_value': pval,
            'N': len(merged),
            'Significant': pval < 0.05
        })

        sig_marker = "***" if pval < 0.001 else "**" if pval < 0.01 else "*" if pval < 0.05 else "ns"
        print(f"\n{race_labels[race]}:")
        print(f"  Correlation (r): {corr:+.3f} {sig_marker}")
        print(f"  P-value: {pval:.4f}")
        print(f"  N: {len(merged)} years")

# ============================================================================
# ANALYSIS 2: Correlation Between Income and Overdose Rates
# ============================================================================

print("\n" + "="*70)
print("CORRELATION: MEDIAN INCOME vs OVERDOSE DEATH RATE")
print("="*70)

for race in ['WHITE', 'BLACK', 'LATINE', 'ASIAN']:
    # Get overdose rates for this race
    overdose_race = overdose_df[overdose_df['Race'] == race].copy()
    overdose_race = overdose_race[overdose_race['Year'] != 2020]

    # Merge with income data
    income_race = income_df[['Year', f'{race}_Median_Income']].copy()
    income_race.columns = ['Year', 'Median_Income']

    merged = overdose_race.merge(income_race, on='Year')

    # Calculate correlation
    if len(merged) > 2:
        corr, pval = stats.pearsonr(merged['Median_Income'], merged['Rate_per_100k'])

        correlation_results.append({
            'Race': race,
            'Metric': 'Median Income',
            'Correlation': corr,
            'P_value': pval,
            'N': len(merged),
            'Significant': pval < 0.05
        })

        sig_marker = "***" if pval < 0.001 else "**" if pval < 0.01 else "*" if pval < 0.05 else "ns"
        print(f"\n{race_labels[race]}:")
        print(f"  Correlation (r): {corr:+.3f} {sig_marker}")
        print(f"  P-value: {pval:.4f}")
        print(f"  N: {len(merged)} years")

# ============================================================================
# ANALYSIS 3: Year-over-Year Changes (Do improvements correlate?)
# ============================================================================

print("\n" + "="*70)
print("YEAR-OVER-YEAR CHANGE CORRELATIONS")
print("="*70)
print("Question: When poverty decreases or income increases, do overdose rates decrease?")
print()

yoy_results = []

for race in ['WHITE', 'BLACK', 'LATINE', 'ASIAN']:
    overdose_race = overdose_df[overdose_df['Race'] == race].copy()
    overdose_race = overdose_race[overdose_race['Year'] != 2020].sort_values('Year')

    poverty_race = poverty_df[['Year', f'{race}_Poverty_Rate']].copy()
    poverty_race.columns = ['Year', 'Poverty_Rate']

    income_race = income_df[['Year', f'{race}_Median_Income']].copy()
    income_race.columns = ['Year', 'Median_Income']

    # Merge all
    merged = overdose_race.merge(poverty_race, on='Year').merge(income_race, on='Year')

    # Calculate year-over-year changes
    merged['OD_Rate_Change'] = merged['Rate_per_100k'].diff()
    merged['Poverty_Change'] = merged['Poverty_Rate'].diff()
    merged['Income_Change'] = merged['Median_Income'].diff()

    # Drop first row (no change data)
    merged = merged.dropna()

    if len(merged) > 2:
        # Poverty change vs OD rate change
        corr_pov, pval_pov = stats.pearsonr(merged['Poverty_Change'], merged['OD_Rate_Change'])

        # Income change vs OD rate change
        corr_inc, pval_inc = stats.pearsonr(merged['Income_Change'], merged['OD_Rate_Change'])

        print(f"\n{race_labels[race]}:")
        print(f"  Poverty Δ vs OD Rate Δ: r={corr_pov:+.3f}, p={pval_pov:.3f}")
        print(f"  Income Δ vs OD Rate Δ:  r={corr_inc:+.3f}, p={pval_inc:.3f}")

        yoy_results.append({
            'Race': race,
            'Poverty_Change_Corr': corr_pov,
            'Income_Change_Corr': corr_inc,
            'Poverty_P': pval_pov,
            'Income_P': pval_inc
        })

# ============================================================================
# VISUALIZATION: Scatter Plots
# ============================================================================

print("\n" + "="*70)
print("CREATING VISUALIZATION")
print("="*70)

fig, axes = plt.subplots(2, 4, figsize=(24, 12))

for idx, race in enumerate(['WHITE', 'BLACK', 'LATINE', 'ASIAN']):
    # Top row: Poverty vs Overdose Rate
    ax1 = axes[0, idx]

    overdose_race = overdose_df[overdose_df['Race'] == race].copy()
    overdose_race = overdose_race[overdose_race['Year'] != 2020]

    poverty_race = poverty_df[['Year', f'{race}_Poverty_Rate']].copy()
    poverty_race.columns = ['Year', 'Poverty_Rate']

    merged = overdose_race.merge(poverty_race, on='Year')

    ax1.scatter(merged['Poverty_Rate'], merged['Rate_per_100k'],
                s=100, alpha=0.7, color=colors[race])

    # Add trend line
    if len(merged) > 2:
        z = np.polyfit(merged['Poverty_Rate'], merged['Rate_per_100k'], 1)
        p = np.poly1d(z)
        x_line = np.linspace(merged['Poverty_Rate'].min(), merged['Poverty_Rate'].max(), 100)
        ax1.plot(x_line, p(x_line), "--", color=colors[race], alpha=0.5, linewidth=2)

        # Add correlation
        corr, pval = stats.pearsonr(merged['Poverty_Rate'], merged['Rate_per_100k'])
        sig = "***" if pval < 0.001 else "**" if pval < 0.01 else "*" if pval < 0.05 else ""
        ax1.text(0.05, 0.95, f'r = {corr:+.3f}{sig}',
                transform=ax1.transAxes, fontsize=11, fontweight='bold',
                verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    ax1.set_xlabel('Poverty Rate (%)', fontsize=11, fontweight='bold')
    ax1.set_ylabel('Overdose Deaths per 100k', fontsize=11, fontweight='bold')
    ax1.set_title(f'{race_labels[race]}: Poverty vs Overdose Rate',
                  fontsize=12, fontweight='bold')
    ax1.grid(True, alpha=0.3)

    # Bottom row: Income vs Overdose Rate
    ax2 = axes[1, idx]

    income_race = income_df[['Year', f'{race}_Median_Income']].copy()
    income_race.columns = ['Year', 'Median_Income']

    merged = overdose_race.merge(income_race, on='Year')

    ax2.scatter(merged['Median_Income']/1000, merged['Rate_per_100k'],
                s=100, alpha=0.7, color=colors[race])

    # Add trend line
    if len(merged) > 2:
        z = np.polyfit(merged['Median_Income'], merged['Rate_per_100k'], 1)
        p = np.poly1d(z)
        x_line = np.linspace(merged['Median_Income'].min(), merged['Median_Income'].max(), 100)
        ax2.plot(x_line/1000, p(x_line), "--", color=colors[race], alpha=0.5, linewidth=2)

        # Add correlation
        corr, pval = stats.pearsonr(merged['Median_Income'], merged['Rate_per_100k'])
        sig = "***" if pval < 0.001 else "**" if pval < 0.01 else "*" if pval < 0.05 else ""
        ax2.text(0.05, 0.95, f'r = {corr:+.3f}{sig}',
                transform=ax2.transAxes, fontsize=11, fontweight='bold',
                verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    ax2.set_xlabel('Median Household Income ($1,000s)', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Overdose Deaths per 100k', fontsize=11, fontweight='bold')
    ax2.set_title(f'{race_labels[race]}: Income vs Overdose Rate',
                  fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.3)

plt.suptitle('Temporal Correlations: Socioeconomic Status vs Overdose Death Rates\n' +
             'Los Angeles County, 2012-2023 (excluding 2020)',
             fontsize=16, fontweight='bold', y=0.995)

plt.tight_layout()
output_path = 'results/13_temporal_correlation/temporal_correlation_scatterplots.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
print(f"\n✓ Saved scatter plots: {output_path}")
plt.close()

# ============================================================================
# Save Correlation Results Table
# ============================================================================

corr_df = pd.DataFrame(correlation_results)
corr_df['Sig_Label'] = corr_df['P_value'].apply(
    lambda p: '***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else 'ns'
)

output_table = 'results/13_temporal_correlation/temporal_correlations.csv'
corr_df.to_csv(output_table, index=False)
print(f"✓ Saved correlation table: {output_table}")

# ============================================================================
# KEY FINDINGS SUMMARY
# ============================================================================

print("\n" + "="*70)
print("KEY FINDINGS")
print("="*70)

print("\n1. POVERTY vs OVERDOSE RATES:")
for _, row in corr_df[corr_df['Metric'] == 'Poverty Rate'].iterrows():
    direction = "POSITIVE" if row['Correlation'] > 0 else "NEGATIVE"
    strength = "STRONG" if abs(row['Correlation']) > 0.7 else "MODERATE" if abs(row['Correlation']) > 0.4 else "WEAK"
    print(f"   {race_labels[row['Race']]}: {strength} {direction} correlation (r={row['Correlation']:+.3f}, {row['Sig_Label']})")

print("\n2. INCOME vs OVERDOSE RATES:")
for _, row in corr_df[corr_df['Metric'] == 'Median Income'].iterrows():
    direction = "POSITIVE" if row['Correlation'] > 0 else "NEGATIVE"
    strength = "STRONG" if abs(row['Correlation']) > 0.7 else "MODERATE" if abs(row['Correlation']) > 0.4 else "WEAK"
    print(f"   {race_labels[row['Race']]}: {strength} {direction} correlation (r={row['Correlation']:+.3f}, {row['Sig_Label']})")

print("\n3. INTERPRETATION:")
print("   - If correlation is POSITIVE: higher poverty/income associates with higher OD rates")
print("     (suggests temporal trend, not protective effect)")
print("   - If correlation is NEGATIVE: higher poverty associates with lower OD rates")
print("     (paradoxical - suggests SES is NOT the driver)")
print("   - Strong POSITIVE correlations suggest both are increasing due to time trend,")
print("     not necessarily causal relationship")

print("\n" + "="*70)
print("ANALYSIS COMPLETE")
print("="*70)
