#!/usr/bin/env python
# coding: utf-8

"""
Years of Potential Life Lost (YPLL) Analysis by Race
Calculates YPLL using standard reference age of 75 years
Shows true population burden accounting for age at death
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

print("="*70)
print("YEARS OF POTENTIAL LIFE LOST (YPLL) ANALYSIS")
print("="*70)

# Load data
print("\nLoading data...")
df = pd.read_csv('data/2012-01-2024-08-overdoses.csv', low_memory=False)
population_df = pd.read_csv('data/la_county_population_census.csv')

print(f"✓ Loaded {len(df):,} overdose records")
print(f"✓ Loaded {len(population_df)} years of population data")

# Process dates to extract year
df['Date of Death'] = pd.to_datetime(df['DeathDate'], errors='coerce')
if 'DateofDeath' in df.columns:
    df['Date of Death'] = df['Date of Death'].fillna(
        pd.to_datetime(df['DateofDeath'], errors='coerce')
    )
df['Year'] = df['Date of Death'].dt.year

# Filter to 2012-2023
df = df[df['Year'].between(2012, 2023)].copy()
print(f"✓ Filtered to {len(df):,} records (2012-2023)")

# Process Age
if df['Age'].dtype == 'object':
    df['Age'] = df['Age'].str.extract(r"(\d+\.?\d*)")[0].astype(float)
else:
    df['Age'] = pd.to_numeric(df['Age'], errors='coerce')

# Process Race/Ethnicity
conditions = [
    df['Race'].isin(["CAUCASIAN", "WHITE", "White/Caucasian"]),
    df['Race'].isin(["LATINE", "HISPANIC/LATIN AMERICAN", "Hispanic/Latino"]) | df['Race'].str.contains("Hispanic", na=False),
    df['Race'].isin(["BLACK", "Black"]),
    df['Race'].isin(["ASIAN", "Asian", "CHINESE", "FILIPINO", "JAPANESE", "KOREAN", "VIETNAMESE"]),
]
choices = ['WHITE', 'LATINE', 'BLACK', 'ASIAN']
df['Race_Ethnicity_Cleaned'] = np.select(conditions, choices, default=None)

# Remove missing age or race
df = df[df['Age'].notna() & df['Race_Ethnicity_Cleaned'].notna()].copy()
print(f"✓ After removing missing age/race: {len(df):,} records")

# Standard YPLL reference age
REFERENCE_AGE = 75

print(f"\nUsing reference age: {REFERENCE_AGE} years")
print("(Standard used by CDC and public health agencies)")

# Calculate YPLL for each death
df['YPLL'] = df['Age'].apply(lambda age: max(0, REFERENCE_AGE - age))

# Remove deaths at or above reference age (YPLL = 0)
df_ypll = df[df['YPLL'] > 0].copy()
print(f"\n✓ {len(df_ypll):,} deaths occurred before age {REFERENCE_AGE}")
print(f"✗ {len(df) - len(df_ypll):,} deaths occurred at/after age {REFERENCE_AGE} (excluded from YPLL)")

# ============================================================================
# CALCULATE YPLL BY RACE AND YEAR
# ============================================================================

print("\n" + "="*70)
print("YPLL BY RACE AND YEAR")
print("="*70)

# Group by race and year
ypll_by_race_year = df_ypll.groupby(['Race_Ethnicity_Cleaned', 'Year']).agg({
    'YPLL': ['sum', 'mean', 'median'],
    'Age': ['count', 'mean', 'median']
}).reset_index()

ypll_by_race_year.columns = ['Race', 'Year', 'Total_YPLL', 'Mean_YPLL_per_Death',
                              'Median_YPLL_per_Death', 'Deaths', 'Mean_Age', 'Median_Age']

# Merge with population data to calculate YPLL rates
population_long = []
for _, row in population_df.iterrows():
    year = row['Year']
    for race in ['WHITE', 'BLACK', 'LATINE', 'ASIAN']:
        population_long.append({
            'Year': year,
            'Race': race,
            'Population': row[race]
        })

pop_df = pd.DataFrame(population_long)
ypll_by_race_year = ypll_by_race_year.merge(pop_df, on=['Race', 'Year'], how='left')

# Calculate YPLL rate per 100,000 population
ypll_by_race_year['YPLL_Rate_per_100k'] = (
    ypll_by_race_year['Total_YPLL'] / ypll_by_race_year['Population'] * 100000
)

# Save detailed table
output_path = 'results/14_ypll_analysis/ypll_by_race_year.csv'
ypll_by_race_year.to_csv(output_path, index=False)
print(f"\n✓ Saved detailed YPLL table: {output_path}")

# ============================================================================
# SUMMARY BY RACE (2012-2023)
# ============================================================================

print("\n" + "="*70)
print("CUMULATIVE YPLL BY RACE (2012-2023)")
print("="*70)

race_summary = ypll_by_race_year.groupby('Race').agg({
    'Total_YPLL': 'sum',
    'Deaths': 'sum',
    'YPLL_Rate_per_100k': 'mean'  # Average annual rate
}).reset_index()

race_summary['Mean_YPLL_per_Death'] = race_summary['Total_YPLL'] / race_summary['Deaths']
race_summary = race_summary.sort_values('Total_YPLL', ascending=False)

race_labels = {
    'WHITE': 'White (NH)',
    'BLACK': 'Black (NH)',
    'LATINE': 'Latine',
    'ASIAN': 'Asian (NH)'
}

print("\nTotal YPLL (2012-2023):")
for _, row in race_summary.iterrows():
    print(f"\n{race_labels.get(row['Race'], row['Race'])}:")
    print(f"  Total YPLL:            {row['Total_YPLL']:>12,.0f} years")
    print(f"  Total Deaths:          {row['Deaths']:>12,.0f}")
    print(f"  Mean YPLL per Death:   {row['Mean_YPLL_per_Death']:>12.1f} years")
    print(f"  Avg Annual YPLL Rate:  {row['YPLL_Rate_per_100k']:>12.1f} per 100k")

# ============================================================================
# 2023 SNAPSHOT
# ============================================================================

print("\n" + "="*70)
print("2023 YPLL SNAPSHOT")
print("="*70)

ypll_2023 = ypll_by_race_year[ypll_by_race_year['Year'] == 2023].copy()
ypll_2023 = ypll_2023.sort_values('YPLL_Rate_per_100k', ascending=False)

print("\n2023 YPLL Rates (per 100,000 population):")
for _, row in ypll_2023.iterrows():
    print(f"\n{race_labels.get(row['Race'], row['Race'])}:")
    print(f"  YPLL Rate per 100k:    {row['YPLL_Rate_per_100k']:>12.1f}")
    print(f"  Total YPLL:            {row['Total_YPLL']:>12,.0f} years")
    print(f"  Deaths:                {row['Deaths']:>12,.0f}")
    print(f"  Mean YPLL per Death:   {row['Mean_YPLL_per_Death']:>12.1f} years")
    print(f"  Median Age at Death:   {row['Median_Age']:>12.1f} years")

# ============================================================================
# VISUALIZATION
# ============================================================================

print("\n" + "="*70)
print("CREATING VISUALIZATIONS")
print("="*70)

colors = {
    'WHITE': '#4472C4',
    'BLACK': '#ED7D31',
    'LATINE': '#A5A5A5',
    'ASIAN': '#FFC000'
}

# Figure 1: YPLL Rates Over Time
fig, axes = plt.subplots(2, 2, figsize=(16, 12))

# Panel A: YPLL Rate per 100k
ax1 = axes[0, 0]
for race in ['WHITE', 'BLACK', 'LATINE', 'ASIAN']:
    race_data = ypll_by_race_year[ypll_by_race_year['Race'] == race]
    ax1.plot(race_data['Year'], race_data['YPLL_Rate_per_100k'],
             marker='o', linewidth=2.5, markersize=7,
             color=colors[race], label=race_labels[race])

ax1.set_xlabel('Year', fontsize=12, fontweight='bold')
ax1.set_ylabel('YPLL per 100,000 Population', fontsize=12, fontweight='bold')
ax1.set_title('A. Years of Potential Life Lost Rates by Race',
              fontsize=14, fontweight='bold', pad=15)
ax1.legend(loc='upper left', fontsize=11)
ax1.grid(True, alpha=0.3)
ax1.set_xlim(2011.5, 2023.5)

# Panel B: Total YPLL (absolute numbers)
ax2 = axes[0, 1]
for race in ['WHITE', 'BLACK', 'LATINE', 'ASIAN']:
    race_data = ypll_by_race_year[ypll_by_race_year['Race'] == race]
    ax2.plot(race_data['Year'], race_data['Total_YPLL'],
             marker='o', linewidth=2.5, markersize=7,
             color=colors[race], label=race_labels[race])

ax2.set_xlabel('Year', fontsize=12, fontweight='bold')
ax2.set_ylabel('Total YPLL (Years)', fontsize=12, fontweight='bold')
ax2.set_title('B. Total Years of Life Lost by Race',
              fontsize=14, fontweight='bold', pad=15)
ax2.legend(loc='upper left', fontsize=11)
ax2.grid(True, alpha=0.3)
ax2.set_xlim(2011.5, 2023.5)

# Panel C: Mean YPLL per Death
ax3 = axes[1, 0]
for race in ['WHITE', 'BLACK', 'LATINE', 'ASIAN']:
    race_data = ypll_by_race_year[ypll_by_race_year['Race'] == race]
    ax3.plot(race_data['Year'], race_data['Mean_YPLL_per_Death'],
             marker='s', linewidth=2.5, markersize=7,
             color=colors[race], label=race_labels[race])

ax3.set_xlabel('Year', fontsize=12, fontweight='bold')
ax3.set_ylabel('Mean YPLL per Death (Years)', fontsize=12, fontweight='bold')
ax3.set_title('C. Average Years Lost per Overdose Death',
              fontsize=14, fontweight='bold', pad=15)
ax3.legend(loc='upper left', fontsize=11)
ax3.grid(True, alpha=0.3)
ax3.set_xlim(2011.5, 2023.5)

# Panel D: 2023 Comparison Bar Chart
ax4 = axes[1, 1]
races_ordered = ['BLACK', 'WHITE', 'LATINE', 'ASIAN']
ypll_2023_sorted = ypll_2023.set_index('Race').loc[races_ordered]

x_pos = np.arange(len(races_ordered))
bars = ax4.bar(x_pos, ypll_2023_sorted['YPLL_Rate_per_100k'],
               color=[colors[r] for r in races_ordered], alpha=0.8, edgecolor='black')

ax4.set_xticks(x_pos)
ax4.set_xticklabels([race_labels[r] for r in races_ordered], fontsize=11)
ax4.set_ylabel('YPLL per 100,000 Population', fontsize=12, fontweight='bold')
ax4.set_title('D. 2023 YPLL Rates Comparison',
              fontsize=14, fontweight='bold', pad=15)
ax4.grid(True, alpha=0.3, axis='y')

# Add value labels on bars
for bar, race in zip(bars, races_ordered):
    height = bar.get_height()
    ax4.text(bar.get_x() + bar.get_width()/2., height,
             f'{height:.0f}',
             ha='center', va='bottom', fontsize=11, fontweight='bold')

plt.suptitle('Years of Potential Life Lost (YPLL) from Overdose Deaths\n' +
             f'Los Angeles County, 2012-2023 (Reference Age: {REFERENCE_AGE} years)',
             fontsize=16, fontweight='bold', y=0.995)

plt.tight_layout()
output_path = 'results/14_ypll_analysis/ypll_analysis.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
print(f"✓ Saved YPLL visualization: {output_path}")
plt.close()

# ============================================================================
# AGE DISTRIBUTION COMPARISON
# ============================================================================

print("\nCreating age distribution comparison...")

fig, ax = plt.subplots(1, 1, figsize=(14, 8))

for race in ['WHITE', 'BLACK', 'LATINE', 'ASIAN']:
    race_data = df_ypll[df_ypll['Race_Ethnicity_Cleaned'] == race]['Age']
    ax.hist(race_data, bins=30, alpha=0.5, label=race_labels[race],
            color=colors[race], edgecolor='black', linewidth=0.5)

ax.axvline(x=REFERENCE_AGE, color='red', linestyle='--', linewidth=2,
           label=f'Reference Age ({REFERENCE_AGE})', alpha=0.7)

ax.set_xlabel('Age at Death (Years)', fontsize=12, fontweight='bold')
ax.set_ylabel('Number of Deaths', fontsize=12, fontweight='bold')
ax.set_title('Age Distribution of Overdose Deaths by Race\n' +
             'Los Angeles County, 2012-2023',
             fontsize=14, fontweight='bold', pad=15)
ax.legend(fontsize=11)
ax.grid(True, alpha=0.3, axis='y')

output_path = 'results/14_ypll_analysis/ypll_age_distribution.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
print(f"✓ Saved age distribution: {output_path}")
plt.close()

# ============================================================================
# KEY INSIGHTS
# ============================================================================

print("\n" + "="*70)
print("KEY INSIGHTS")
print("="*70)

# Rank by YPLL rate 2023
ypll_2023_sorted = ypll_2023.sort_values('YPLL_Rate_per_100k', ascending=False)

print("\n1. YPLL RATES (2023) - Ranking by Burden per 100k:")
for idx, (_, row) in enumerate(ypll_2023_sorted.iterrows(), 1):
    print(f"   {idx}. {race_labels[row['Race']]}: {row['YPLL_Rate_per_100k']:.1f} years per 100k")

print("\n2. MEAN YEARS LOST PER DEATH (2023):")
ypll_2023_sorted_mean = ypll_2023.sort_values('Mean_YPLL_per_Death', ascending=False)
for idx, (_, row) in enumerate(ypll_2023_sorted_mean.iterrows(), 1):
    print(f"   {idx}. {race_labels[row['Race']]}: {row['Mean_YPLL_per_Death']:.1f} years per death " +
          f"(median age: {row['Median_Age']:.0f})")

print("\n3. TOTAL BURDEN (2012-2023):")
for idx, (_, row) in enumerate(race_summary.iterrows(), 1):
    print(f"   {idx}. {race_labels[row['Race']]}: {row['Total_YPLL']:,.0f} total years lost")

print("\n4. INTERPRETATION:")
print("   - Latine individuals die youngest (median ~34), so highest YPLL per death")
print("   - Black individuals have highest YPLL RATE (per 100k population)")
print("   - This combines high death rates + relatively young age at death")
print("   - White individuals have moderate rates despite more total deaths")
print("   - Asian individuals have lowest YPLL rates across all metrics")

print("\n" + "="*70)
print("ANALYSIS COMPLETE")
print("="*70)
