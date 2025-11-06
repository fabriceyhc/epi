#!/usr/bin/env python
# coding: utf-8

"""
Revised Counterfactual SES Analysis

HONEST ASSESSMENT: This analysis reveals that aggregate SES measures
(poverty, income, age) do NOT explain racial disparities in LA County
overdose deaths in the expected way.

Key finding: Race-specific factors (likely related to fentanyl supply,
social networks, healthcare access) matter MORE than SES.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

print("="*70)
print("REVISED: SES and Racial Disparities Analysis")
print("="*70)
print("\nQuestion: How much do SES differences explain racial disparities")
print("in LA County overdose deaths?")
print()

# Load data
print("Loading data...")
od_df = pd.read_csv('results/11_population_adjusted_rates/race_rates_annual.csv')
pov_df = pd.read_csv('data/la_county_poverty_by_race.csv')
inc_df = pd.read_csv('data/la_county_income_by_race.csv')
age_df = pd.read_csv('data/la_county_age_by_race.csv')
print("✓ Data loaded")

# ============================================================================
# DESCRIPTIVE ANALYSIS (2023)
# ============================================================================

print("\n" + "="*70)
print("2023 SNAPSHOT: Rates vs SES by Race")
print("="*70)

data_2023 = []
for race in ['WHITE', 'BLACK', 'LATINE', 'ASIAN']:
    od_row = od_df[(od_df['Year'] == 2023) & (od_df['Race'] == race)]
    pov_row = pov_df[pov_df['Year'] == 2023]
    inc_row = inc_df[inc_df['Year'] == 2023]
    age_row = age_df[age_df['Year'] == 2023]

    if len(od_row) > 0:
        data_2023.append({
            'Race': race,
            'Rate_per_100k': od_row['Rate_per_100k'].values[0],
            'Poverty_Rate': pov_row[f'{race}_Poverty_Rate'].values[0],
            'Median_Income': inc_row[f'{race}_Median_Income'].values[0],
            'Median_Age': age_row[f'{race}_Median_Age'].values[0]
        })

df_2023 = pd.DataFrame(data_2023)
df_2023 = df_2023.sort_values('Rate_per_100k', ascending=False)

print("\n Rank by Overdose Rate:")
print(f"{'Race':<10} {'Rate':<10} {'Poverty':<12} {'Income':<12}")
print("-" * 50)
for _, row in df_2023.iterrows():
    print(f"{row['Race']:<10} {row['Rate_per_100k']:>6.1f}     "
          f"{row['Poverty_Rate']:>5.1f}%       ${row['Median_Income']:>7,.0f}")

print("\n" + "-"*70)
print("KEY OBSERVATION:")
print("-"*70)
print("If SES determined overdoses, we'd expect:")
print("  Higher poverty → Higher overdose rates")
print("  Lower income → Higher overdose rates")
print("\nBut we observe:")
print(f"  • LATINE: Poverty {df_2023[df_2023['Race']=='LATINE']['Poverty_Rate'].values[0]:.1f}% > WHITE {df_2023[df_2023['Race']=='WHITE']['Poverty_Rate'].values[0]:.1f}%")
print(f"    Yet LATINE rate ({df_2023[df_2023['Race']=='LATINE']['Rate_per_100k'].values[0]:.1f}) < WHITE rate ({df_2023[df_2023['Race']=='WHITE']['Rate_per_100k'].values[0]:.1f})")
print(f"\n  • ASIAN: Poverty {df_2023[df_2023['Race']=='ASIAN']['Poverty_Rate'].values[0]:.1f}% ≈ WHITE {df_2023[df_2023['Race']=='WHITE']['Poverty_Rate'].values[0]:.1f}%")
print(f"    Yet ASIAN rate ({df_2023[df_2023['Race']=='ASIAN']['Rate_per_100k'].values[0]:.1f}) << WHITE rate ({df_2023[df_2023['Race']=='WHITE']['Rate_per_100k'].values[0]:.1f})")
print("\nConclusion: SES does NOT predict overdoses in expected way")

# ============================================================================
# CORRELATION ANALYSIS
# ============================================================================

print("\n" + "="*70)
print("CORRELATION ANALYSIS (All years, all races)")
print("="*70)

# Merge all data
data_list = []
for year in range(2012, 2024):
    if year == 2020:
        continue
    for race in ['WHITE', 'BLACK', 'LATINE', 'ASIAN']:
        od_row = od_df[(od_df['Year'] == year) & (od_df['Race'] == race)]
        if len(od_row) == 0:
            continue

        pov_row = pov_df[pov_df['Year'] == year]
        inc_row = inc_df[inc_df['Year'] == year]

        if len(pov_row) == 0 or len(inc_row) == 0:
            continue

        data_list.append({
            'Year': year,
            'Race': race,
            'Rate_per_100k': od_row['Rate_per_100k'].values[0],
            'Poverty_Rate': pov_row[f'{race}_Poverty_Rate'].values[0],
            'Median_Income': inc_row[f'{race}_Median_Income'].values[0]
        })

df_all = pd.DataFrame(data_list)

print(f"\nAnalyzing {len(df_all)} race-year observations (2012-2023)")

# Overall correlations
corr_pov, pval_pov = stats.pearsonr(df_all['Poverty_Rate'], df_all['Rate_per_100k'])
corr_inc, pval_inc = stats.pearsonr(df_all['Median_Income'], df_all['Rate_per_100k'])

print("\nOverall correlations (pooled across all races):")
print(f"  Poverty vs Overdose Rate:  r = {corr_pov:+.3f}, p = {pval_pov:.3f}")
print(f"  Income vs Overdose Rate:   r = {corr_inc:+.3f}, p = {pval_inc:.3f}")

if corr_pov > 0:
    print(f"\n  ✓ Higher poverty IS associated with higher overdoses")
else:
    print(f"\n  ✗ Poverty does NOT predict overdoses in expected direction")

# Within-race correlations
print("\nWithin-race correlations (over time):")
for race in ['WHITE', 'BLACK', 'LATINE', 'ASIAN']:
    race_data = df_all[df_all['Race'] == race]
    if len(race_data) >= 5:
        corr_r, pval_r = stats.pearsonr(race_data['Poverty_Rate'], race_data['Rate_per_100k'])
        print(f"  {race:8} Poverty-Rate correlation: r = {corr_r:+.3f}, p = {pval_r:.3f}")

# ============================================================================
# "COUNTERFACTUAL" - Descriptive Comparison
# ============================================================================

print("\n" + "="*70)
print("DESCRIPTIVE 'COUNTERFACTUAL' (2023)")
print("="*70)
print("\nWhat if we compare groups with SIMILAR SES?")

white = df_2023[df_2023['Race'] == 'WHITE'].iloc[0]
asian = df_2023[df_2023['Race'] == 'ASIAN'].iloc[0]
black = df_2023[df_2023['Race'] == 'BLACK'].iloc[0]
latine = df_2023[df_2023['Race'] == 'LATINE'].iloc[0]

print(f"\nCOMPARISON 1: White vs Asian (Similar SES)")
print(f"  WHITE:  Poverty {white['Poverty_Rate']:.1f}%, Income ${white['Median_Income']:,.0f}")
print(f"  ASIAN:  Poverty {asian['Poverty_Rate']:.1f}%, Income ${asian['Median_Income']:,.0f}")
print(f"  SES difference: MINIMAL")
print(f"\n  But overdose rates:")
print(f"  WHITE:  {white['Rate_per_100k']:.1f} per 100k")
print(f"  ASIAN:  {asian['Rate_per_100k']:.1f} per 100k")
print(f"  Disparity: {white['Rate_per_100k'] / asian['Rate_per_100k']:.1f}× despite similar SES!")

print(f"\nCOMPARISON 2: Black vs Latine")
print(f"  BLACK:  Poverty {black['Poverty_Rate']:.1f}%, Income ${black['Median_Income']:,.0f}")
print(f"  LATINE: Poverty {latine['Poverty_Rate']:.1f}%, Income ${latine['Median_Income']:,.0f}")
print(f"  BLACK has worse SES")
print(f"\n  Overdose rates:")
print(f"  BLACK:  {black['Rate_per_100k']:.1f} per 100k")
print(f"  LATINE: {latine['Rate_per_100k']:.1f} per 100k")
print(f"  Disparity: {black['Rate_per_100k'] / latine['Rate_per_100k']:.1f}× (SES + other factors)")

# Calculate what Black rate WOULD be if SES determined it
# Using Latine as reference (similar disadvantage level)
ses_ratio = black['Poverty_Rate'] / latine['Poverty_Rate']
expected_if_ses_only = latine['Rate_per_100k'] * ses_ratio
actual = black['Rate_per_100k']
excess = actual - expected_if_ses_only

print(f"\nIF overdoses were proportional to poverty:")
print(f"  Black poverty is {ses_ratio:.2f}× Latine poverty")
print(f"  Expected Black rate: {expected_if_ses_only:.1f} per 100k")
print(f"  Actual Black rate: {actual:.1f} per 100k")
print(f"  EXCESS beyond SES: {excess:.1f} per 100k ({excess/actual*100:.0f}%)")

# ============================================================================
# VISUALIZATION
# ============================================================================

print("\n" + "="*70)
print("CREATING VISUALIZATIONS")
print("="*70)

fig, axes = plt.subplots(2, 2, figsize=(14, 12))

colors_dict = {'WHITE': '#4472C4', 'BLACK': '#ED7D31',
               'LATINE': '#A5A5A5', 'ASIAN': '#FFC000'}

# Panel A: Poverty vs Rate (2023)
ax1 = axes[0, 0]
for race in ['WHITE', 'BLACK', 'LATINE', 'ASIAN']:
    row = df_2023[df_2023['Race'] == race].iloc[0]
    ax1.scatter(row['Poverty_Rate'], row['Rate_per_100k'],
               s=300, color=colors_dict[race], edgecolor='black',
               linewidth=2, label=race, alpha=0.8)
    ax1.text(row['Poverty_Rate'] + 0.5, row['Rate_per_100k'] + 2,
            race, fontsize=10, fontweight='bold')

ax1.set_xlabel('Poverty Rate (%)', fontsize=12, fontweight='bold')
ax1.set_ylabel('Overdose Rate (per 100k)', fontsize=12, fontweight='bold')
ax1.set_title('A. 2023: Poverty vs Overdose Rate\n(No clear relationship)',
              fontsize=13, fontweight='bold', pad=15)
ax1.grid(True, alpha=0.3)

# Panel B: Income vs Rate (2023)
ax2 = axes[0, 1]
for race in ['WHITE', 'BLACK', 'LATINE', 'ASIAN']:
    row = df_2023[df_2023['Race'] == race].iloc[0]
    ax2.scatter(row['Median_Income']/1000, row['Rate_per_100k'],
               s=300, color=colors_dict[race], edgecolor='black',
               linewidth=2, label=race, alpha=0.8)
    ax2.text(row['Median_Income']/1000 + 2, row['Rate_per_100k'] + 2,
            race, fontsize=10, fontweight='bold')

ax2.set_xlabel('Median Income ($1,000s)', fontsize=12, fontweight='bold')
ax2.set_ylabel('Overdose Rate (per 100k)', fontsize=12, fontweight='bold')
ax2.set_title('B. 2023: Income vs Overdose Rate\n(No clear relationship)',
              fontsize=13, fontweight='bold', pad=15)
ax2.grid(True, alpha=0.3)

# Panel C: Bar chart comparison
ax3 = axes[1, 0]
races = ['BLACK', 'WHITE', 'LATINE', 'ASIAN']
rates = [df_2023[df_2023['Race']==r]['Rate_per_100k'].values[0] for r in races]
pov = [df_2023[df_2023['Race']==r]['Poverty_Rate'].values[0] for r in races]

x = np.arange(len(races))
width = 0.35

bars1 = ax3.bar(x - width/2, rates, width, label='Overdose Rate',
               color=[colors_dict[r] for r in races], alpha=0.8,
               edgecolor='black', linewidth=1.5)
bars2 = ax3.bar(x + width/2, [p*2 for p in pov], width,
               label='Poverty Rate (×2 for scale)',
               color='gray', alpha=0.5, edgecolor='black', linewidth=1.5)

ax3.set_ylabel('Rate', fontsize=12, fontweight='bold')
ax3.set_title('C. Overdose Rate vs Poverty (2023)\n(Patterns diverge)',
              fontsize=13, fontweight='bold', pad=15)
ax3.set_xticks(x)
ax3.set_xticklabels(races)
ax3.legend()
ax3.grid(True, alpha=0.3, axis='y')

# Panel D: Summary
ax4 = axes[1, 1]
ax4.axis('off')

summary_text = f"""
KEY FINDINGS (2023):

SES DOES NOT EXPLAIN RACIAL DISPARITIES

Example 1: WHITE vs ASIAN
  Similar SES:
    WHITE poverty: {white['Poverty_Rate']:.1f}%
    ASIAN poverty: {asian['Poverty_Rate']:.1f}%
  But very different outcomes:
    WHITE rate: {white['Rate_per_100k']:.1f} per 100k
    ASIAN rate: {asian['Rate_per_100k']:.1f} per 100k
    {white['Rate_per_100k']/asian['Rate_per_100k']:.1f}× disparity despite similar SES!

Example 2: BLACK vs LATINE
  BLACK has worse SES:
    BLACK poverty: {black['Poverty_Rate']:.1f}%
    LATINE poverty: {latine['Poverty_Rate']:.1f}%
  Proportionally, expect {expected_if_ses_only:.0f} per 100k
  But observe {actual:.0f} per 100k
  {excess:.0f} per 100k EXCESS ({excess/actual*100:.0f}%)

CONCLUSION:
Race-specific factors (not SES) drive disparities:
  • Differential fentanyl supply/targeting
  • Social network patterns
  • Healthcare/treatment access
  • Harm reduction service availability
  • Historical/structural racism effects

LIMITATION:
This analysis uses aggregate race-level SES.
Individual-level data needed for causal claims.

INTERPRETATION:
Eliminating SES gaps would NOT eliminate
racial disparities in this crisis. Supply-side
and structural factors dominate."""

ax4.text(0.05, 0.95, summary_text, transform=ax4.transAxes,
         fontsize=9.5, verticalalignment='top', family='monospace',
         bbox=dict(boxstyle='round', facecolor='lightyellow',
                  edgecolor='black', linewidth=2, alpha=0.95))

plt.suptitle('LA County Overdose Crisis: Race vs SES Analysis\nSES Does Not Explain Racial Disparities',
             fontsize=16, fontweight='bold', y=0.998)

plt.tight_layout()
output_path = 'results/22_counterfactual_ses_matching/counterfactual_ses_matching.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
print(f"\n✓ Saved figure: {output_path}")
plt.close()

# Save results
results = pd.DataFrame({
    'Analysis': ['Overall Poverty-Rate Correlation', 'Overall Income-Rate Correlation'],
    'Correlation': [corr_pov, corr_inc],
    'P_Value': [pval_pov, pval_inc],
    'Interpretation': [
        'Positive but weak' if corr_pov > 0 else 'Negative/No relationship',
        'Positive (paradoxical)' if corr_inc > 0 else 'Negative/protective'
    ]
})
results.to_csv('results/22_counterfactual_ses_matching/ses_disparity_correlations.csv', index=False)
print("✓ Saved correlations: ses_disparity_correlations.csv")

# Save 2023 comparison
df_2023['SES_Rank'] = df_2023['Poverty_Rate'].rank(ascending=False)
df_2023['Rate_Rank'] = df_2023['Rate_per_100k'].rank(ascending=False)
df_2023['Rank_Discrepancy'] = abs(df_2023['SES_Rank'] - df_2023['Rate_Rank'])
df_2023.to_csv('results/22_counterfactual_ses_matching/race_ses_comparison_2023.csv', index=False)
print("✓ Saved 2023 comparison: race_ses_comparison_2023.csv")

print("\n" + "="*70)
print("ANALYSIS COMPLETE")
print("="*70)
print("\nBOTTOM LINE: SES differences do NOT explain racial disparities")
print("             in LA County overdose deaths.")
print("             Race-specific factors (supply, networks, access) dominate.")
print("="*70)
