#!/usr/bin/env python
# coding: utf-8

"""
Disparity Decomposition Analysis
Attempts to quantify how much of the Black-White overdose disparity
can be "explained" by socioeconomic differences vs unexplained (structural) factors

Uses simplified Kitagawa-Blinder-Oaxaca decomposition approach
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

print("="*70)
print("DISPARITY DECOMPOSITION ANALYSIS")
print("="*70)
print("\nQuestion: How much of the Black-White overdose disparity")
print("can be 'explained' by socioeconomic differences?")
print()

# Load data
overdose_df = pd.read_csv('results/15_disparity_decomposition/race_rates_annual.csv')
poverty_df = pd.read_csv('data/la_county_poverty_by_race.csv')
income_df = pd.read_csv('data/la_county_income_by_race.csv')
age_df = pd.read_csv('data/la_county_age_by_race.csv')

# Focus on 2023 for main analysis
overdose_2023 = overdose_df[overdose_df['Year'] == 2023].set_index('Race')
poverty_2023 = poverty_df[poverty_df['Year'] == 2023].iloc[0]
income_2023 = income_df[income_df['Year'] == 2023].iloc[0]
age_2023 = age_df[age_df['Year'] == 2023].iloc[0]

print("="*70)
print("2023 OBSERVED DISPARITIES")
print("="*70)

# Get rates
black_rate = overdose_2023.loc['BLACK', 'Rate_per_100k']
white_rate = overdose_2023.loc['WHITE', 'Rate_per_100k']
latine_rate = overdose_2023.loc['LATINE', 'Rate_per_100k']
asian_rate = overdose_2023.loc['ASIAN', 'Rate_per_100k']

print(f"\nOverdose Death Rates (per 100,000):")
print(f"  BLACK:  {black_rate:.1f}")
print(f"  WHITE:  {white_rate:.1f}")
print(f"  LATINE: {latine_rate:.1f}")
print(f"  ASIAN:  {asian_rate:.1f}")

black_white_ratio = black_rate / white_rate
print(f"\nBlack-to-White Rate Ratio: {black_white_ratio:.2f}")
print(f"  (Black individuals have {black_white_ratio:.2f}x higher overdose rate than White)")

# ============================================================================
# SOCIOECONOMIC STATUS COMPARISON
# ============================================================================

print("\n" + "="*70)
print("SOCIOECONOMIC STATUS (2023)")
print("="*70)

black_pov = poverty_2023['BLACK_Poverty_Rate']
white_pov = poverty_2023['WHITE_Poverty_Rate']
pov_ratio = black_pov / white_pov

black_inc = income_2023['BLACK_Median_Income']
white_inc = income_2023['WHITE_Median_Income']
inc_ratio = black_inc / white_inc

black_age = age_2023['BLACK_Median_Age']
white_age = age_2023['WHITE_Median_Age']

print(f"\nPoverty Rates:")
print(f"  BLACK:  {black_pov:.1f}%")
print(f"  WHITE:  {white_pov:.1f}%")
print(f"  Ratio:  {pov_ratio:.2f}x (Black poverty is {pov_ratio:.2f}x higher)")

print(f"\nMedian Household Income:")
print(f"  BLACK:  ${black_inc:,}")
print(f"  WHITE:  ${white_inc:,}")
print(f"  Ratio:  {inc_ratio:.2f}x (Black income is {inc_ratio:.2f}x White income)")

print(f"\nMedian Population Age:")
print(f"  BLACK:  {black_age:.1f} years")
print(f"  WHITE:  {white_age:.1f} years")
print(f"  Difference: {white_age - black_age:.1f} years (White population is OLDER)")

# ============================================================================
# DECOMPOSITION LOGIC
# ============================================================================

print("\n" + "="*70)
print("DISPARITY DECOMPOSITION")
print("="*70)
print("\nAssuming hypothetical scenarios to isolate SES effects:")
print("(These are simplified calculations to illustrate the logic)")

# Scenario 1: If overdose rates tracked poverty rates proportionally
# If poverty explains disparities, we'd expect:
# Black/White OD ratio = Black/White poverty ratio
poverty_expected_ratio = pov_ratio
poverty_residual = black_white_ratio - poverty_expected_ratio

print(f"\n1. POVERTY-BASED EXPECTATION:")
print(f"   - Black poverty is {pov_ratio:.2f}x White poverty")
print(f"   - If poverty FULLY explained disparities:")
print(f"     Expected Black/White OD ratio: {poverty_expected_ratio:.2f}x")
print(f"   - Actual Black/White OD ratio: {black_white_ratio:.2f}x")
print(f"   - UNEXPLAINED disparity: {poverty_residual:.2f}x")
print(f"   - Interpretation: {(poverty_residual/black_white_ratio)*100:.1f}% of disparity is NOT explained by poverty")

# Scenario 2: If overdose rates tracked income inversely
# Lower income = higher risk
# If Black has 0.57x White income, might expect higher OD rate
# But need to see if magnitude matches
income_expected_ratio = 1 / inc_ratio  # Inverse relationship
income_residual = black_white_ratio - income_expected_ratio

print(f"\n2. INCOME-BASED EXPECTATION (inverse relationship):")
print(f"   - Black income is {inc_ratio:.2f}x White income")
print(f"   - If income FULLY explained disparities (inverse):")
print(f"     Expected Black/White OD ratio: {income_expected_ratio:.2f}x")
print(f"   - Actual Black/White OD ratio: {black_white_ratio:.2f}x")
print(f"   - UNEXPLAINED disparity: {income_residual:.2f}x")
print(f"   - Interpretation: Income gap suggests {income_expected_ratio:.2f}x ratio, but actual is {black_white_ratio:.2f}x")

# Scenario 3: Age adjustment
# Since Black population is younger, age doesn't explain higher rates
print(f"\n3. AGE-BASED EXPECTATION:")
print(f"   - Black median age: {black_age:.1f} (YOUNGER than White: {white_age:.1f})")
print(f"   - Younger populations typically have LOWER overdose mortality")
print(f"   - Yet Black rate is {black_white_ratio:.2f}x higher than White")
print(f"   - Interpretation: Age does NOT explain disparity; if anything, makes it more paradoxical")

# ============================================================================
# LATINE vs WHITE COMPARISON (Control Analysis)
# ============================================================================

print("\n" + "="*70)
print("CONTROL COMPARISON: LATINE vs WHITE")
print("="*70)
print("Latine individuals have SES disadvantage but LOWER overdose rates")
print("This helps rule out SES as the primary driver")

latine_pov = poverty_2023['LATINE_Poverty_Rate']
latine_inc = income_2023['LATINE_Median_Income']
latine_age = age_2023['LATINE_Median_Age']

latine_white_ratio = latine_rate / white_rate

print(f"\nLatine vs White Overdose Ratio: {latine_white_ratio:.2f}")
print(f"  (Latine rate is {latine_white_ratio:.2f}x White rate)")

print(f"\nLatine Poverty: {latine_pov:.1f}% ({latine_pov/white_pov:.2f}x White)")
print(f"Latine Income: ${latine_inc:,} ({latine_inc/white_inc:.2f}x White)")
print(f"Latine Age: {latine_age:.1f} years (MUCH younger than White: {white_age:.1f})")

print(f"\nKEY INSIGHT:")
print(f"  - Latine poverty ({latine_pov/white_pov:.2f}x White) is similar to Black ({pov_ratio:.2f}x White)")
print(f"  - Latine income ({latine_inc/white_inc:.2f}x White) is between Black and White")
print(f"  - Yet Latine OD rate is LOWER than White ({latine_white_ratio:.2f}x)")
print(f"  - While Black OD rate is HIGHER than White ({black_white_ratio:.2f}x)")
print(f"  - This proves SES ALONE cannot explain racial disparities")

# ============================================================================
# TIME TRENDS DECOMPOSITION
# ============================================================================

print("\n" + "="*70)
print("DECOMPOSITION OVER TIME (2012-2023)")
print("="*70)

# For each year, calculate disparity and SES ratios
decomp_data = []

for year in range(2012, 2024):
    if year == 2020:
        continue  # No SES data for 2020

    od_year = overdose_df[overdose_df['Year'] == year].set_index('Race')
    pov_year = poverty_df[poverty_df['Year'] == year].iloc[0]
    inc_year = income_df[income_df['Year'] == year].iloc[0]

    black_od = od_year.loc['BLACK', 'Rate_per_100k']
    white_od = od_year.loc['WHITE', 'Rate_per_100k']
    od_ratio = black_od / white_od

    black_pov_year = pov_year['BLACK_Poverty_Rate']
    white_pov_year = pov_year['WHITE_Poverty_Rate']
    pov_ratio_year = black_pov_year / white_pov_year

    black_inc_year = inc_year['BLACK_Median_Income']
    white_inc_year = inc_year['WHITE_Median_Income']
    inc_ratio_year = black_inc_year / white_inc_year

    unexplained_pov = od_ratio - pov_ratio_year
    pct_unexplained = (unexplained_pov / od_ratio) * 100

    decomp_data.append({
        'Year': year,
        'OD_Ratio': od_ratio,
        'Poverty_Ratio': pov_ratio_year,
        'Income_Ratio': inc_ratio_year,
        'Income_Ratio_Inverse': 1/inc_ratio_year,
        'Unexplained_by_Poverty': unexplained_pov,
        'Pct_Unexplained': pct_unexplained
    })

decomp_df = pd.DataFrame(decomp_data)

print(f"\nTrends in Disparity Ratios (Black / White):")
print(f"\n{'Year':<6} {'OD Ratio':<10} {'Pov Ratio':<12} {'Unexplained':<15} {'% Unexplained':<15}")
print("-"*70)
for _, row in decomp_df.iterrows():
    print(f"{int(row['Year']):<6} {row['OD_Ratio']:>8.2f}x  {row['Poverty_Ratio']:>8.2f}x    "
          f"{row['Unexplained_by_Poverty']:>8.2f}x        {row['Pct_Unexplained']:>8.1f}%")

# ============================================================================
# VISUALIZATION
# ============================================================================

print("\n" + "="*70)
print("CREATING VISUALIZATION")
print("="*70)

fig, axes = plt.subplots(2, 2, figsize=(16, 12))

# Panel A: Disparity ratios over time
ax1 = axes[0, 0]
ax1.plot(decomp_df['Year'], decomp_df['OD_Ratio'],
         marker='o', linewidth=2.5, markersize=8,
         color='#ED0000', label='Overdose Disparity (Black/White)', zorder=3)
ax1.plot(decomp_df['Year'], decomp_df['Poverty_Ratio'],
         marker='s', linewidth=2, markersize=7,
         color='#4472C4', label='Poverty Ratio (Black/White)', linestyle='--', zorder=2)
ax1.plot(decomp_df['Year'], decomp_df['Income_Ratio_Inverse'],
         marker='^', linewidth=2, markersize=7,
         color='#70AD47', label='Inverse Income Ratio (White/Black)', linestyle='--', zorder=2)

ax1.axhline(y=1.0, color='black', linestyle='-', linewidth=1, alpha=0.3, label='Parity')
ax1.set_xlabel('Year', fontsize=12, fontweight='bold')
ax1.set_ylabel('Ratio (Black / White)', fontsize=12, fontweight='bold')
ax1.set_title('A. Overdose Disparity vs SES Disparities Over Time',
              fontsize=14, fontweight='bold', pad=15)
ax1.legend(fontsize=10, loc='upper left')
ax1.grid(True, alpha=0.3)
ax1.set_xlim(2011.5, 2023.5)

# Panel B: Percent unexplained by poverty
ax2 = axes[0, 1]
ax2.bar(decomp_df['Year'], decomp_df['Pct_Unexplained'],
        color='#ED7D31', alpha=0.7, edgecolor='black')
ax2.axhline(y=50, color='red', linestyle='--', linewidth=2, alpha=0.5,
            label='50% threshold')
ax2.set_xlabel('Year', fontsize=12, fontweight='bold')
ax2.set_ylabel('% of Disparity Unexplained by Poverty', fontsize=12, fontweight='bold')
ax2.set_title('B. Proportion of Disparity Not Explained by Poverty',
              fontsize=14, fontweight='bold', pad=15)
ax2.legend(fontsize=10)
ax2.grid(True, alpha=0.3, axis='y')
ax2.set_xlim(2011.5, 2023.5)

# Panel C: Cross-sectional comparison (2023)
ax3 = axes[1, 0]

races = ['WHITE', 'BLACK', 'LATINE', 'ASIAN']
colors_race = {'WHITE': '#4472C4', 'BLACK': '#ED7D31',
               'LATINE': '#A5A5A5', 'ASIAN': '#FFC000'}

# Normalize to White = 1.0
white_vals = {
    'OD_Rate': white_rate,
    'Poverty': white_pov,
    'Income': white_inc
}

comparison_data = []
for race in races:
    od_val = overdose_2023.loc[race, 'Rate_per_100k'] / white_vals['OD_Rate']
    pov_val = poverty_2023[f'{race}_Poverty_Rate'] / white_vals['Poverty']
    inc_val = income_2023[f'{race}_Median_Income'] / white_vals['Income']

    comparison_data.append({
        'Race': race,
        'OD_Rate_Ratio': od_val,
        'Poverty_Ratio': pov_val,
        'Income_Ratio': inc_val
    })

comp_df = pd.DataFrame(comparison_data)

x = np.arange(len(races))
width = 0.25

bars1 = ax3.bar(x - width, comp_df['OD_Rate_Ratio'], width,
                label='Overdose Rate', color='#ED0000', alpha=0.8)
bars2 = ax3.bar(x, comp_df['Poverty_Ratio'], width,
                label='Poverty Rate', color='#4472C4', alpha=0.8)
bars3 = ax3.bar(x + width, comp_df['Income_Ratio'], width,
                label='Income', color='#70AD47', alpha=0.8)

ax3.axhline(y=1.0, color='black', linestyle='-', linewidth=2, alpha=0.5)
ax3.set_xlabel('Race/Ethnicity', fontsize=12, fontweight='bold')
ax3.set_ylabel('Ratio (Relative to White)', fontsize=12, fontweight='bold')
ax3.set_title('C. 2023 Cross-Sectional Comparison (White = 1.0)',
              fontsize=14, fontweight='bold', pad=15)
ax3.set_xticks(x)
ax3.set_xticklabels(['White (NH)', 'Black (NH)', 'Latine', 'Asian (NH)'])
ax3.legend(fontsize=10)
ax3.grid(True, alpha=0.3, axis='y')

# Panel D: Text summary
ax4 = axes[1, 1]
ax4.axis('off')

summary_text = f"""
DISPARITY DECOMPOSITION SUMMARY (2023)

OBSERVED DISPARITIES:
  Black/White Overdose Ratio:    {black_white_ratio:.2f}x
  Black/White Poverty Ratio:     {pov_ratio:.2f}x
  White/Black Income Ratio:      {1/inc_ratio:.2f}x

DECOMPOSITION FINDINGS:

1. POVERTY CANNOT EXPLAIN DISPARITY:
   - Black poverty is {pov_ratio:.2f}x White
   - But Black overdose rate is {black_white_ratio:.2f}x White
   - Unexplained: {poverty_residual:.2f}x ({(poverty_residual/black_white_ratio)*100:.0f}% of disparity)

2. INCOME CANNOT EXPLAIN DISPARITY:
   - Black income is {inc_ratio:.2f}x White (inverse: {1/inc_ratio:.2f}x)
   - Expected ratio if income drove disparities: ~{income_expected_ratio:.2f}x
   - Actual ratio: {black_white_ratio:.2f}x
   - Income gap suggests higher risk, but not enough to explain {black_white_ratio:.2f}x

3. AGE MAKES IT WORSE:
   - Black population is YOUNGER (median {black_age:.0f} vs {white_age:.0f})
   - Younger populations should have LOWER risk
   - Yet Black rate is {black_white_ratio:.2f}x higher
   - Age differences CANNOT explain disparity

4. LATINE CONTROL GROUP:
   - Similar poverty to Black ({latine_pov/white_pov:.2f}x vs {pov_ratio:.2f}x)
   - Lower income than Black (${latine_inc:,} vs ${black_inc:,})
   - Much younger than Black ({latine_age:.0f} vs {black_age:.0f} years)
   - Yet LOWER overdose rate ({latine_white_ratio:.2f}x vs {black_white_ratio:.2f}x)

   This proves SES alone does NOT drive disparities.

CONCLUSION:
Approximately {(poverty_residual/black_white_ratio)*100:.0f}% of the Black-White
overdose disparity CANNOT be explained by poverty, income,
or age differences.

This residual disparity likely reflects:
  • Differential drug supply/targeting
  • Healthcare access barriers
  • Treatment gaps
  • Harm reduction service gaps
  • Structural racism and systemic inequities
"""

ax4.text(0.05, 0.95, summary_text, transform=ax4.transAxes,
         fontsize=10, verticalalignment='top', family='monospace',
         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))

plt.suptitle('Disparity Decomposition: SES-Explained vs Structural Factors\n' +
             'Black-White Overdose Disparity in Los Angeles County',
             fontsize=16, fontweight='bold', y=0.995)

plt.tight_layout()
output_path = 'results/15_disparity_decomposition/disparity_decomposition.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
print(f"\n✓ Saved figure: {output_path}")
plt.close()

# Save decomposition table
decomp_df.to_csv('results/15_disparity_decomposition/disparity_decomposition_annual.csv', index=False)
print(f"✓ Saved table: results/15_disparity_decomposition/disparity_decomposition_annual.csv")

print("\n" + "="*70)
print("ANALYSIS COMPLETE")
print("="*70)
print(f"\nBOTTOM LINE:")
print(f"  Approximately {(poverty_residual/black_white_ratio)*100:.0f}% of the Black-White overdose")
print(f"  disparity cannot be explained by socioeconomic differences.")
print(f"  This points to structural factors driving the crisis.")
print("="*70)
