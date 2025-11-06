#!/usr/bin/env python
# coding: utf-8

"""
Housing Burden → Homelessness → Overdose Pipeline Analysis
Examines whether rising housing costs led to increased homelessness,
and whether this contributed to overdose disparities by race
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from utils import full_data_processing, RACE_COLORS, get_race_labels

print("="*70)
print("HOUSING BURDEN → HOMELESSNESS → OVERDOSE PIPELINE")
print("="*70)

# Load data
print("\nLoading data...")
df = full_data_processing(filter_years=True)  # 2012-2023

# Load housing cost data
housing_df = pd.read_csv('data/la_county_housing_costs.csv')
income_housing = pd.read_csv('results/20_housing_homelessness/income_housing_burden.csv')

print(f"✓ Loaded {len(df):,} overdose deaths (2012-2023)")

# ============================================================================
# PROCESS HOMELESSNESS DATA
# ============================================================================

print("\n" + "="*70)
print("PROCESSING HOMELESSNESS DATA")
print("="*70)

# Check homelessness indicators
homeless_indicators = []
if 'ExperiencingHomelessness' in df.columns:
    homeless_indicators.append('ExperiencingHomelessness')
if 'ResidenceType' in df.columns:
    homeless_indicators.append('ResidenceType')

print(f"\nHomelessness indicators found: {homeless_indicators}")

# Create standardized homeless flag
df['Homeless'] = 0

if 'ExperiencingHomelessness' in df.columns:
    df['Homeless'] = np.where(
        df['ExperiencingHomelessness'].astype(str).str.upper().isin(['TRUE', '1', 'YES']),
        1, df['Homeless']
    )

if 'ResidenceType' in df.columns:
    homeless_types = ['HOMELESS', 'TRANSIENT', 'VAGRANT', 'STREET']
    df['Homeless'] = np.where(
        df['ResidenceType'].astype(str).str.upper().str.contains('|'.join(homeless_types), na=False),
        1, df['Homeless']
    )

# Housing status categories
df['Housing_Status'] = 'Unknown'
df.loc[df['Homeless'] == 1, 'Housing_Status'] = 'Unhoused'
df.loc[df['Homeless'] == 0, 'Housing_Status'] = 'Housed'

# Filter to known housing status for main analysis
df_known = df[df['Housing_Status'] != 'Unknown'].copy()

print(f"\nHousing Status Distribution:")
print(df['Housing_Status'].value_counts())
print(f"\nAnalysis sample (known housing status): {len(df_known):,} deaths")

# ============================================================================
# TEMPORAL TRENDS: HOMELESSNESS RATES
# ============================================================================

print("\n" + "="*70)
print("TEMPORAL TRENDS IN HOMELESSNESS")
print("="*70)

# Annual homelessness rates
annual_homeless = df_known.groupby('Year').agg({
    'Homeless': ['sum', 'mean']
}).reset_index()
annual_homeless.columns = ['Year', 'Homeless_Deaths', 'Homeless_Rate']
annual_homeless['Homeless_Rate'] *= 100  # Convert to percentage

# Merge with housing costs
trends = annual_homeless.merge(housing_df, on='Year', how='left')
trends = trends.merge(
    income_housing[['Year', 'BLACK_Rent_Burden_Pct', 'WHITE_Rent_Burden_Pct',
                     'LATINE_Rent_Burden_Pct', 'ASIAN_Rent_Burden_Pct']],
    on='Year', how='left'
)

print("\nHomelessness among overdose deaths over time:")
print(f"{'Year':<6} {'N Unhoused':<12} {'% Unhoused':<12} {'Median Rent':<12}")
print("-"*50)
for _, row in trends.iterrows():
    print(f"{int(row['Year']):<6} {int(row['Homeless_Deaths']):<12} "
          f"{row['Homeless_Rate']:>10.1f}%  ${row['Median_Gross_Rent']:>10,}")

# Correlation: rent vs homelessness
trends_clean = trends.dropna(subset=['Median_Gross_Rent', 'Homeless_Rate'])
if len(trends_clean) > 2:
    corr_rent, pval_rent = stats.pearsonr(
        trends_clean['Median_Gross_Rent'],
        trends_clean['Homeless_Rate']
    )
    print(f"\nCorrelation: Median Rent vs % Unhoused")
    print(f"  r = {corr_rent:+.3f}, p = {pval_rent:.4f}")

# ============================================================================
# BY RACE: HOMELESSNESS RATES
# ============================================================================

print("\n" + "="*70)
print("HOMELESSNESS RATES BY RACE")
print("="*70)

# Filter to main race groups
df_race = df_known[
    df_known['Race_Ethnicity_Cleaned'].isin(['WHITE', 'BLACK', 'LATINE', 'ASIAN'])
].copy()

# Annual rates by race
race_homeless = df_race.groupby(['Year', 'Race_Ethnicity_Cleaned']).agg({
    'Homeless': ['sum', 'count', 'mean']
}).reset_index()
race_homeless.columns = ['Year', 'Race', 'Homeless_Deaths', 'Total_Deaths', 'Homeless_Rate']
race_homeless['Homeless_Rate'] *= 100

print("\n2023 Homelessness Rates by Race:")
race_2023 = race_homeless[race_homeless['Year'] == 2023].sort_values('Homeless_Rate', ascending=False)
race_labels = get_race_labels('long')

for _, row in race_2023.iterrows():
    print(f"  {race_labels[row['Race']]:15} {row['Homeless_Rate']:>6.1f}% "
          f"({int(row['Homeless_Deaths'])}/{int(row['Total_Deaths'])} deaths)")

# ============================================================================
# OVERDOSE RATES: HOUSED VS UNHOUSED
# ============================================================================

print("\n" + "="*70)
print("OVERDOSE CHARACTERISTICS: HOUSED VS UNHOUSED")
print("="*70)

# Compare demographics
comparison_vars = ['Age', 'Number_Substances', 'Fentanyl',
                   'Methamphetamine', 'Heroin', 'Cocaine']

housed_stats = df_known[df_known['Housing_Status'] == 'Housed'][comparison_vars].describe()
unhoused_stats = df_known[df_known['Housing_Status'] == 'Unhoused'][comparison_vars].describe()

print("\nComparison of Housed vs Unhoused Overdose Deaths:")
print(f"\n{'Measure':<20} {'Housed':<15} {'Unhoused':<15} {'Difference':<15}")
print("-"*70)

# Mean age
housed_age = df_known[df_known['Housing_Status'] == 'Housed']['Age'].mean()
unhoused_age = df_known[df_known['Housing_Status'] == 'Unhoused']['Age'].mean()
print(f"{'Mean Age':<20} {housed_age:>13.1f}   {unhoused_age:>13.1f}   {unhoused_age-housed_age:>+13.1f}")

# Mean substances
housed_subst = df_known[df_known['Housing_Status'] == 'Housed']['Number_Substances'].mean()
unhoused_subst = df_known[df_known['Housing_Status'] == 'Unhoused']['Number_Substances'].mean()
print(f"{'Mean Substances':<20} {housed_subst:>13.2f}   {unhoused_subst:>13.2f}   {unhoused_subst-housed_subst:>+13.2f}")

# Substance prevalence
for substance in ['Fentanyl', 'Methamphetamine', 'Heroin', 'Cocaine']:
    housed_pct = df_known[df_known['Housing_Status'] == 'Housed'][substance].mean() * 100
    unhoused_pct = df_known[df_known['Housing_Status'] == 'Unhoused'][substance].mean() * 100
    print(f"{substance:<20} {housed_pct:>12.1f}%  {unhoused_pct:>12.1f}%  {unhoused_pct-housed_pct:>+12.1f}pp")

# ============================================================================
# RENT BURDEN AND HOMELESSNESS BY RACE
# ============================================================================

print("\n" + "="*70)
print("RENT BURDEN vs HOMELESSNESS CORRELATION BY RACE")
print("="*70)

for race in ['WHITE', 'BLACK', 'LATINE', 'ASIAN']:
    race_trend = race_homeless[race_homeless['Race'] == race].copy()
    race_trend = race_trend.merge(
        income_housing[['Year', f'{race}_Rent_Burden_Pct']],
        on='Year', how='left'
    )
    race_trend = race_trend.dropna()

    if len(race_trend) > 2:
        corr, pval = stats.pearsonr(
            race_trend[f'{race}_Rent_Burden_Pct'],
            race_trend['Homeless_Rate']
        )
        sig = "***" if pval < 0.001 else "**" if pval < 0.01 else "*" if pval < 0.05 else "ns"

        print(f"\n{race_labels[race]}:")
        print(f"  Rent Burden vs Homelessness Rate: r = {corr:+.3f}, p = {pval:.4f} {sig}")

        # Show 2012 vs 2023 change
        if 2012 in race_trend['Year'].values and 2023 in race_trend['Year'].values:
            burden_2012 = race_trend[race_trend['Year'] == 2012][f'{race}_Rent_Burden_Pct'].values[0]
            burden_2023 = race_trend[race_trend['Year'] == 2023][f'{race}_Rent_Burden_Pct'].values[0]
            homeless_2012 = race_trend[race_trend['Year'] == 2012]['Homeless_Rate'].values[0]
            homeless_2023 = race_trend[race_trend['Year'] == 2023]['Homeless_Rate'].values[0]

            print(f"  Rent Burden: {burden_2012:.1f}% (2012) → {burden_2023:.1f}% (2023) = {burden_2023-burden_2012:+.1f}pp")
            print(f"  Homeless Rate: {homeless_2012:.1f}% (2012) → {homeless_2023:.1f}% (2023) = {homeless_2023-homeless_2012:+.1f}pp")

# ============================================================================
# VISUALIZATION
# ============================================================================

print("\n" + "="*70)
print("CREATING VISUALIZATIONS")
print("="*70)

fig, axes = plt.subplots(2, 3, figsize=(18, 12))

# Panel A: Homelessness rate over time
ax1 = axes[0, 0]
ax1.plot(trends['Year'], trends['Homeless_Rate'],
         marker='o', linewidth=2.5, markersize=8, color='#ED7D31')
ax1.set_xlabel('Year', fontsize=12, fontweight='bold')
ax1.set_ylabel('% of Overdose Deaths\nExperiencing Homelessness', fontsize=12, fontweight='bold')
ax1.set_title('A. Homelessness Among Overdose Deaths',
              fontsize=14, fontweight='bold', pad=15)
ax1.grid(True, alpha=0.3)
ax1.set_xlim(2011.5, 2023.5)

# Panel B: Rent over time (dual axis with homelessness)
ax2 = axes[0, 1]
ax2_twin = ax2.twinx()

ax2.plot(trends['Year'], trends['Median_Gross_Rent'],
         marker='s', linewidth=2.5, markersize=7, color='#4472C4',
         label='Median Rent')
ax2_twin.plot(trends['Year'], trends['Homeless_Rate'],
              marker='o', linewidth=2.5, markersize=7, color='#ED7D31',
              label='% Unhoused', linestyle='--')

ax2.set_xlabel('Year', fontsize=12, fontweight='bold')
ax2.set_ylabel('Median Gross Rent ($)', fontsize=12, fontweight='bold', color='#4472C4')
ax2_twin.set_ylabel('% Unhoused', fontsize=12, fontweight='bold', color='#ED7D31')
ax2.set_title('B. Rent vs Homelessness Rate',
              fontsize=14, fontweight='bold', pad=15)
ax2.tick_params(axis='y', labelcolor='#4472C4')
ax2_twin.tick_params(axis='y', labelcolor='#ED7D31')
ax2.grid(True, alpha=0.3)
ax2.set_xlim(2011.5, 2023.5)

# Combine legends
lines1, labels1 = ax2.get_legend_handles_labels()
lines2, labels2 = ax2_twin.get_legend_handles_labels()
ax2.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=10)

# Panel C: Homelessness rate by race over time
ax3 = axes[0, 2]
for race in ['WHITE', 'BLACK', 'LATINE', 'ASIAN']:
    race_data = race_homeless[race_homeless['Race'] == race]
    ax3.plot(race_data['Year'], race_data['Homeless_Rate'],
             marker='o', linewidth=2.5, markersize=6,
             color=RACE_COLORS[race], label=race_labels[race])

ax3.set_xlabel('Year', fontsize=12, fontweight='bold')
ax3.set_ylabel('% Experiencing Homelessness', fontsize=12, fontweight='bold')
ax3.set_title('C. Homelessness Rate by Race',
              fontsize=14, fontweight='bold', pad=15)
ax3.legend(fontsize=10)
ax3.grid(True, alpha=0.3)
ax3.set_xlim(2011.5, 2023.5)

# Panel D: Rent burden vs homelessness rate by race
ax4 = axes[1, 0]
for race in ['WHITE', 'BLACK', 'LATINE', 'ASIAN']:
    race_trend = race_homeless[race_homeless['Race'] == race].merge(
        income_housing[['Year', f'{race}_Rent_Burden_Pct']],
        on='Year', how='left'
    ).dropna()

    ax4.scatter(race_trend[f'{race}_Rent_Burden_Pct'],
                race_trend['Homeless_Rate'],
                s=100, alpha=0.7, color=RACE_COLORS[race],
                label=race_labels[race])

    # Add trend line
    if len(race_trend) > 2:
        z = np.polyfit(race_trend[f'{race}_Rent_Burden_Pct'],
                       race_trend['Homeless_Rate'], 1)
        p = np.poly1d(z)
        x_line = np.linspace(race_trend[f'{race}_Rent_Burden_Pct'].min(),
                            race_trend[f'{race}_Rent_Burden_Pct'].max(), 100)
        ax4.plot(x_line, p(x_line), '--', alpha=0.5,
                color=RACE_COLORS[race], linewidth=2)

ax4.set_xlabel('Rent as % of Median Income', fontsize=12, fontweight='bold')
ax4.set_ylabel('% Experiencing Homelessness', fontsize=12, fontweight='bold')
ax4.set_title('D. Rent Burden vs Homelessness',
              fontsize=14, fontweight='bold', pad=15)
ax4.legend(fontsize=10)
ax4.grid(True, alpha=0.3)

# Panel E: Age distribution (housed vs unhoused)
ax5 = axes[1, 1]
housed_ages = df_known[df_known['Housing_Status'] == 'Housed']['Age'].dropna()
unhoused_ages = df_known[df_known['Housing_Status'] == 'Unhoused']['Age'].dropna()

ax5.hist(housed_ages, bins=30, alpha=0.6, label='Housed',
         color='#4472C4', edgecolor='black', density=True)
ax5.hist(unhoused_ages, bins=30, alpha=0.6, label='Unhoused',
         color='#ED7D31', edgecolor='black', density=True)

ax5.axvline(housed_ages.median(), color='#4472C4', linestyle='--',
            linewidth=2, label=f'Housed median: {housed_ages.median():.0f}')
ax5.axvline(unhoused_ages.median(), color='#ED7D31', linestyle='--',
            linewidth=2, label=f'Unhoused median: {unhoused_ages.median():.0f}')

ax5.set_xlabel('Age at Death', fontsize=12, fontweight='bold')
ax5.set_ylabel('Density', fontsize=12, fontweight='bold')
ax5.set_title('E. Age Distribution by Housing Status',
              fontsize=14, fontweight='bold', pad=15)
ax5.legend(fontsize=9)
ax5.grid(True, alpha=0.3, axis='y')

# Panel F: Substance patterns (housed vs unhoused)
ax6 = axes[1, 2]
substances = ['Fentanyl', 'Methamphetamine', 'Heroin', 'Cocaine']
housed_pct = [df_known[df_known['Housing_Status'] == 'Housed'][s].mean() * 100
              for s in substances]
unhoused_pct = [df_known[df_known['Housing_Status'] == 'Unhoused'][s].mean() * 100
                for s in substances]

x = np.arange(len(substances))
width = 0.35

ax6.bar(x - width/2, housed_pct, width, label='Housed',
        color='#4472C4', alpha=0.8, edgecolor='black')
ax6.bar(x + width/2, unhoused_pct, width, label='Unhoused',
        color='#ED7D31', alpha=0.8, edgecolor='black')

ax6.set_xlabel('Substance', fontsize=12, fontweight='bold')
ax6.set_ylabel('% of Deaths', fontsize=12, fontweight='bold')
ax6.set_title('F. Substance Involvement by Housing Status',
              fontsize=14, fontweight='bold', pad=15)
ax6.set_xticks(x)
ax6.set_xticklabels(substances, rotation=45, ha='right')
ax6.legend(fontsize=10)
ax6.grid(True, alpha=0.3, axis='y')

plt.suptitle('Housing Burden, Homelessness, and Overdose Deaths\nLos Angeles County, 2012-2023',
             fontsize=16, fontweight='bold', y=0.998)

plt.tight_layout()
output_path = 'results/20_housing_homelessness/housing_homelessness_pipeline.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
print(f"\n✓ Saved figure: {output_path}")
plt.close()

# ============================================================================
# SAVE DATA
# ============================================================================

# Save trends
trends.to_csv('results/20_housing_homelessness/housing_homeless_trends.csv', index=False)
print("✓ Saved trends: results/20_housing_homelessness/housing_homeless_trends.csv")

# Save by race
race_homeless.to_csv('results/20_housing_homelessness/homeless_by_race_year.csv', index=False)
print("✓ Saved by race: results/20_housing_homelessness/homeless_by_race_year.csv")

# ============================================================================
# KEY FINDINGS
# ============================================================================

print("\n" + "="*70)
print("KEY FINDINGS")
print("="*70)

print("\n1. HOUSING CRISIS → HOMELESSNESS:")
first_year = trends.iloc[0]
last_year = trends.iloc[-1]
rent_increase = ((last_year['Median_Gross_Rent'] / first_year['Median_Gross_Rent']) - 1) * 100
homeless_increase = last_year['Homeless_Rate'] - first_year['Homeless_Rate']

print(f"   • Median rent: ${first_year['Median_Gross_Rent']:,.0f} (2012) → "
      f"${last_year['Median_Gross_Rent']:,.0f} (2023) (+{rent_increase:.1f}%)")
print(f"   • Homelessness among overdose deaths: {first_year['Homeless_Rate']:.1f}% → "
      f"{last_year['Homeless_Rate']:.1f}% ({homeless_increase:+.1f}pp)")

print("\n2. RACE-SPECIFIC VULNERABILITY:")
print(f"   2023 Homelessness Rates:")
for _, row in race_2023.iterrows():
    print(f"   • {race_labels[row['Race']]}: {row['Homeless_Rate']:.1f}%")

print("\n3. HOUSED vs UNHOUSED DIFFERENCES:")
print(f"   • Age: Housed {housed_age:.1f} years vs Unhoused {unhoused_age:.1f} years")
print(f"   • Methamphetamine: Housed {housed_pct[1]:.1f}% vs Unhoused {unhoused_pct[1]:.1f}%")

print("\n4. INTERPRETATION:")
print("   • Rising rent associated with increased homelessness among overdose deaths")
print("   • But homelessness increased for ALL races, not just Black")
print("   • Cannot explain why Black disparity increased specifically")
print("   • Housing crisis is real but not the sole driver of racial disparities")

print("\n" + "="*70)
print("ANALYSIS COMPLETE")
print("="*70)
