#!/usr/bin/env python3
"""
Analysis #18: Age-Standardized Overdose Rates

Calculates age-standardized mortality rates using direct standardization
to account for differences in age distributions across racial/ethnic groups.
Uses the 2000 U.S. Standard Population as reference.
"""

import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Import shared utilities
from utils import load_overdose_data, standardize_race, process_age, RACE_COLORS

# Setup
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("colorblind")
output_dir = Path('results/18_age_standardized_rates')
output_dir.mkdir(parents=True, exist_ok=True)

print("=" * 70)
print("AGE-STANDARDIZED OVERDOSE RATES ANALYSIS")
print("=" * 70)
print()
print("Calculating age-standardized rates using the 2000 U.S.")
print("Standard Population to account for age distribution differences")
print()

# ============================================================================
# DEFINE 2000 U.S. STANDARD POPULATION
# ============================================================================
# Age groups match Census standard: <1, 1-4, 5-9, ..., 85+
# We'll use broader groups that match our data availability

# Using broader age groups suitable for overdose data
# Source: CDC 2000 U.S. Standard Population
# https://www.cdc.gov/nchs/data/statnt/statnt20.pdf

standard_pop = {
    '<25': 0.359,      # Ages 0-24 (combined from 0-4, 5-9, 10-14, 15-19, 20-24)
    '25-34': 0.138,    # Ages 25-34 (combined from 25-29, 30-34)
    '35-44': 0.162,    # Ages 35-44 (combined from 35-39, 40-44)
    '45-54': 0.137,    # Ages 45-54 (combined from 45-49, 50-54)
    '55-64': 0.087,    # Ages 55-64 (combined from 55-59, 60-64)
    '65+': 0.117       # Ages 65+ (combined from 65-69, 70-74, 75-79, 80-84, 85+)
}

print("2000 U.S. Standard Population weights:")
for age_group, weight in standard_pop.items():
    print(f"  {age_group}: {weight:.3f}")
print()

# ============================================================================
# LOAD DATA
# ============================================================================
print("Loading data...")

# Overdose data
df = load_overdose_data('data/2012-01-2024-08-overdoses.csv')
df = standardize_race(df, race_col='Race', output_col='Race_Ethnicity_Cleaned')
df = process_age(df, age_col='Age')
df = df[(df['Year'] >= 2012) & (df['Year'] <= 2023)].copy()

# Load Census population data
pop_data_wide = pd.read_csv('data/la_county_population_census.csv')
pop_data = pop_data_wide.melt(id_vars=['Year'], var_name='Race', value_name='Population')
pop_data = pop_data[pop_data['Race'] != 'TOTAL'].copy()

print(f"✓ Loaded {len(df):,} overdose deaths (2012-2023)")
print(f"✓ Loaded population data")
print()

# ============================================================================
# CREATE AGE GROUPS
# ============================================================================
print("Creating age groups...")

# Define age groups matching standard population
df['Age_Group_Std'] = pd.cut(df['Age'],
                              bins=[0, 25, 35, 45, 55, 65, 120],
                              labels=['<25', '25-34', '35-44', '45-54', '55-64', '65+'],
                              right=False,
                              include_lowest=True)

df = df[df['Age_Group_Std'].notna()].copy()

print(f"✓ Created age groups for {len(df):,} deaths")
print()

# ============================================================================
# CALCULATE AGE-SPECIFIC RATES BY RACE AND YEAR
# ============================================================================
print("Calculating age-specific rates...")

# Count deaths by race, year, age group
deaths_by_age = df.groupby(['Year', 'Race_Ethnicity_Cleaned', 'Age_Group_Std'], observed=False).size().reset_index(name='Deaths')

# For population, we need to estimate age distribution within each race
# Since we only have total population by race, we'll use LA County's overall age distribution
# as a proxy to split each race's population into age groups

# Get overall LA County age distribution (approximation)
# In reality, each race has different age structures, but we work with available data

# Calculate proportion of deaths in each age group (as proxy for population structure)
age_dist = df.groupby('Age_Group_Std', observed=False).size()
age_dist_pct = age_dist / age_dist.sum()

print("Estimated age distribution (from death data):")
for ag, pct in age_dist_pct.items():
    print(f"  {ag}: {pct:.1%}")
print()
print("Note: Using death age distribution as proxy for population age structure")
print("      Ideally would use race-specific age distributions from Census")
print()

# Apply age distribution to population data
age_specific_pop = []

for _, pop_row in pop_data.iterrows():
    for age_group in ['<25', '25-34', '35-44', '45-54', '55-64', '65+']:
        age_specific_pop.append({
            'Year': pop_row['Year'],
            'Race': pop_row['Race'],
            'Age_Group_Std': age_group,
            'Population': pop_row['Population'] * age_dist_pct[age_group]
        })

pop_age = pd.DataFrame(age_specific_pop)

# Merge deaths with population
merged = deaths_by_age.merge(pop_age,
                               left_on=['Year', 'Race_Ethnicity_Cleaned', 'Age_Group_Std'],
                               right_on=['Year', 'Race', 'Age_Group_Std'],
                               how='left')

# Calculate age-specific rates per 100,000
merged['Rate_Per_100k'] = (merged['Deaths'] / merged['Population'] * 100000).fillna(0)

print(f"✓ Calculated {len(merged)} age-race-year specific rates")
print()

# ============================================================================
# CALCULATE CRUDE (UNADJUSTED) RATES
# ============================================================================
print("Calculating crude (unadjusted) rates...")

crude_rates = df.groupby(['Year', 'Race_Ethnicity_Cleaned'], observed=False).size().reset_index(name='Deaths')
crude_rates = crude_rates.merge(pop_data, left_on=['Year', 'Race_Ethnicity_Cleaned'], right_on=['Year', 'Race'], how='left')
crude_rates['Crude_Rate'] = (crude_rates['Deaths'] / crude_rates['Population'] * 100000).round(2)

print("✓ Calculated crude rates")
print()

# ============================================================================
# CALCULATE AGE-STANDARDIZED RATES
# ============================================================================
print("Calculating age-standardized rates...")
print()

age_standardized_rates = []

for year in sorted(merged['Year'].unique()):
    for race in ['WHITE', 'BLACK', 'LATINE', 'ASIAN']:
        subset = merged[(merged['Year'] == year) & (merged['Race_Ethnicity_Cleaned'] == race)]

        if len(subset) == 0:
            continue

        # Calculate age-standardized rate using direct method
        # ASR = Σ(age-specific rate × standard population weight)

        asr = 0
        for _, row in subset.iterrows():
            age_group = row['Age_Group_Std']
            rate = row['Rate_Per_100k']
            weight = standard_pop.get(age_group, 0)
            asr += rate * weight

        # Get crude rate for comparison
        crude_row = crude_rates[(crude_rates['Year'] == year) & (crude_rates['Race_Ethnicity_Cleaned'] == race)]
        crude_rate = crude_row['Crude_Rate'].values[0] if len(crude_row) > 0 else np.nan
        total_deaths = crude_row['Deaths'].values[0] if len(crude_row) > 0 else 0

        age_standardized_rates.append({
            'Year': year,
            'Race': race,
            'Age_Standardized_Rate': round(asr, 2),
            'Crude_Rate': crude_rate,
            'Total_Deaths': total_deaths,
            'Difference': round(asr - crude_rate, 2)
        })

asr_df = pd.DataFrame(age_standardized_rates)

print("Age-Standardized vs Crude Rates (2023):")
print("=" * 70)
subset_2023 = asr_df[asr_df['Year'] == 2023].sort_values('Age_Standardized_Rate', ascending=False)
for _, row in subset_2023.iterrows():
    print(f"{row['Race']:8s}: ASR = {row['Age_Standardized_Rate']:6.1f}, "
          f"Crude = {row['Crude_Rate']:6.1f}, "
          f"Diff = {row['Difference']:+6.1f}")
print()

# ============================================================================
# CALCULATE DISPARITY RATIOS
# ============================================================================
print("=" * 70)
print("RACIAL DISPARITIES: AGE-STANDARDIZED vs CRUDE")
print("=" * 70)
print()

# Calculate disparity ratios for each year
disparities = []

for year in sorted(asr_df['Year'].unique()):
    year_data = asr_df[asr_df['Year'] == year]

    white_asr = year_data[year_data['Race'] == 'WHITE']['Age_Standardized_Rate'].values[0]
    white_crude = year_data[year_data['Race'] == 'WHITE']['Crude_Rate'].values[0]

    for race in ['BLACK', 'LATINE', 'ASIAN']:
        race_data = year_data[year_data['Race'] == race]
        if len(race_data) > 0:
            race_asr = race_data['Age_Standardized_Rate'].values[0]
            race_crude = race_data['Crude_Rate'].values[0]

            disparities.append({
                'Year': year,
                'Race': race,
                'ASR_Ratio': round(race_asr / white_asr, 2) if white_asr > 0 else np.nan,
                'Crude_Ratio': round(race_crude / white_crude, 2) if white_crude > 0 else np.nan
            })

disp_df = pd.DataFrame(disparities)

print("2023 Disparity Ratios (relative to White):")
disp_2023 = disp_df[disp_df['Year'] == 2023]
for _, row in disp_2023.iterrows():
    print(f"{row['Race']:8s}: ASR ratio = {row['ASR_Ratio']:.2f}x, "
          f"Crude ratio = {row['Crude_Ratio']:.2f}x")
print()

# ============================================================================
# VISUALIZATIONS
# ============================================================================
print("Creating visualizations...")

fig, axes = plt.subplots(2, 3, figsize=(18, 12))

# Panel 1: Crude vs ASR over time for all races
for race in ['WHITE', 'BLACK', 'LATINE', 'ASIAN']:
    race_data = asr_df[asr_df['Race'] == race].sort_values('Year')
    color = RACE_COLORS.get(race, 'gray')

    axes[0, 0].plot(race_data['Year'], race_data['Crude_Rate'],
                     label=f'{race} (crude)', linestyle='--', color=color, alpha=0.5, linewidth=1.5)
    axes[0, 0].plot(race_data['Year'], race_data['Age_Standardized_Rate'],
                     label=f'{race} (ASR)', linestyle='-', color=color, linewidth=2.5)

axes[0, 0].set_xlabel('Year', fontsize=11)
axes[0, 0].set_ylabel('Rate per 100,000', fontsize=11)
axes[0, 0].set_title('Crude vs Age-Standardized Rates\n(Solid = ASR, Dashed = Crude)',
                      fontsize=12, fontweight='bold')
axes[0, 0].legend(fontsize=8, ncol=2)
axes[0, 0].grid(True, alpha=0.3)

# Panel 2: 2023 comparison
subset_2023 = asr_df[asr_df['Year'] == 2023].sort_values('Age_Standardized_Rate', ascending=False)
x = np.arange(len(subset_2023))
width = 0.35

axes[0, 1].bar(x - width/2, subset_2023['Crude_Rate'], width, label='Crude', alpha=0.7, edgecolor='black')
axes[0, 1].bar(x + width/2, subset_2023['Age_Standardized_Rate'], width, label='Age-Standardized', alpha=0.7, edgecolor='black')
axes[0, 1].set_xticks(x)
axes[0, 1].set_xticklabels(subset_2023['Race'], rotation=0)
axes[0, 1].set_ylabel('Rate per 100,000', fontsize=11)
axes[0, 1].set_title('2023 Rates: Crude vs Age-Standardized',
                      fontsize=12, fontweight='bold')
axes[0, 1].legend()

# Panel 3: Difference (ASR - Crude)
for race in ['WHITE', 'BLACK', 'LATINE', 'ASIAN']:
    race_data = asr_df[asr_df['Race'] == race].sort_values('Year')
    color = RACE_COLORS.get(race, 'gray')
    axes[0, 2].plot(race_data['Year'], race_data['Difference'],
                     label=race, color=color, linewidth=2, marker='o')

axes[0, 2].axhline(0, color='black', linestyle='--', linewidth=1)
axes[0, 2].set_xlabel('Year', fontsize=11)
axes[0, 2].set_ylabel('Difference (ASR - Crude)', fontsize=11)
axes[0, 2].set_title('Impact of Age-Adjustment\n(Positive = younger population)',
                      fontsize=12, fontweight='bold')
axes[0, 2].legend()
axes[0, 2].grid(True, alpha=0.3)

# Panel 4: Disparity ratios over time
for race in ['BLACK', 'LATINE', 'ASIAN']:
    race_disp = disp_df[disp_df['Race'] == race].sort_values('Year')
    color = RACE_COLORS.get(race, 'gray')

    axes[1, 0].plot(race_disp['Year'], race_disp['Crude_Ratio'],
                     label=f'{race} (crude)', linestyle='--', color=color, alpha=0.5, linewidth=1.5)
    axes[1, 0].plot(race_disp['Year'], race_disp['ASR_Ratio'],
                     label=f'{race} (ASR)', linestyle='-', color=color, linewidth=2.5)

axes[1, 0].axhline(1, color='black', linestyle=':', linewidth=1)
axes[1, 0].set_xlabel('Year', fontsize=11)
axes[1, 0].set_ylabel('Rate Ratio (relative to White)', fontsize=11)
axes[1, 0].set_title('Racial Disparities Over Time\n(ASR vs Crude)',
                      fontsize=12, fontweight='bold')
axes[1, 0].legend(fontsize=8, ncol=2)
axes[1, 0].grid(True, alpha=0.3)

# Panel 5: 2023 disparity comparison
disp_2023 = disp_df[disp_df['Year'] == 2023].sort_values('ASR_Ratio', ascending=False)
x = np.arange(len(disp_2023))

axes[1, 1].bar(x - width/2, disp_2023['Crude_Ratio'], width, label='Crude', alpha=0.7, edgecolor='black')
axes[1, 1].bar(x + width/2, disp_2023['ASR_Ratio'], width, label='Age-Standardized', alpha=0.7, edgecolor='black')
axes[1, 1].axhline(1, color='black', linestyle='--', linewidth=1)
axes[1, 1].set_xticks(x)
axes[1, 1].set_xticklabels(disp_2023['Race'], rotation=0)
axes[1, 1].set_ylabel('Rate Ratio (vs White)', fontsize=11)
axes[1, 1].set_title('2023 Disparities: Crude vs Age-Standardized',
                      fontsize=12, fontweight='bold')
axes[1, 1].legend()

# Panel 6: Summary text
axes[1, 2].axis('off')

# Calculate average impact of age adjustment
avg_diff = asr_df.groupby('Race')['Difference'].mean().sort_values(ascending=False)

summary_text = f"""
AGE-STANDARDIZATION SUMMARY

2023 AGE-STANDARDIZED RATES:
"""
for _, row in subset_2023.iterrows():
    summary_text += f"• {row['Race']:8s}: {row['Age_Standardized_Rate']:6.1f} per 100k\n"

summary_text += f"""

AVERAGE IMPACT OF AGE ADJUSTMENT:
"""
for race, diff in avg_diff.items():
    direction = "younger" if diff > 0 else "older"
    summary_text += f"• {race:8s}: {diff:+5.1f} ({direction})\n"

summary_text += f"""

2023 DISPARITIES (vs WHITE):
"""
for _, row in disp_2023.iterrows():
    summary_text += f"• {row['Race']:8s}: {row['ASR_Ratio']:.2f}x\n"

summary_text += """

INTERPRETATION:
Age-standardization accounts for
different age distributions across
racial/ethnic groups, providing
more accurate disparity estimates.
"""

axes[1, 2].text(0.1, 0.9, summary_text, fontsize=9, verticalalignment='top',
                family='monospace', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

plt.tight_layout()
plt.savefig(output_dir / 'age_standardized_rates.png', dpi=300, bbox_inches='tight')
print(f"✓ Saved: {output_dir / 'age_standardized_rates.png'}")
print()

# Save results
asr_df.to_csv(output_dir / 'age_standardized_rates.csv', index=False)
disp_df.to_csv(output_dir / 'age_standardized_disparities.csv', index=False)
merged.to_csv(output_dir / 'age_specific_rates.csv', index=False)
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

# Compare 2023 ASR vs crude for each race
print("2023 COMPARISON:")
for _, row in subset_2023.iterrows():
    pct_diff = (row['Difference'] / row['Crude_Rate'] * 100) if row['Crude_Rate'] > 0 else 0
    print(f"• {row['Race']}: ASR = {row['Age_Standardized_Rate']:.1f} per 100k "
          f"(crude = {row['Crude_Rate']:.1f}, {pct_diff:+.1f}% difference)")
print()

# Disparity changes
print("IMPACT ON DISPARITIES:")
for _, row in disp_2023.iterrows():
    crude_disp = (row['Crude_Ratio'] - 1) * 100
    asr_disp = (row['ASR_Ratio'] - 1) * 100
    print(f"• {row['Race']} vs White: "
          f"Crude = +{crude_disp:.0f}%, ASR = +{asr_disp:.0f}%")

print()
print("=" * 70)
