#!/usr/bin/env python3
"""
Analysis #25: Housing Costs and Overdose Deaths

Examines the relationship between housing costs (rent and home values)
and overdose mortality patterns over time.
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
output_dir = Path('results/25_housing_costs')
output_dir.mkdir(parents=True, exist_ok=True)

print("=" * 70)
print("HOUSING COSTS AND OVERDOSE DEATHS ANALYSIS")
print("=" * 70)
print()
print("Examining how rising housing costs correlate with overdose trends")
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

# Load income data
income_data_wide = pd.read_csv('data/la_county_income_by_race.csv')
income_data = income_data_wide.melt(id_vars=['Year'], var_name='Race', value_name='Median_Income')
income_data['Race'] = income_data['Race'].str.replace('_Median_Income', '', regex=False)

# Load housing costs
housing_data = pd.read_csv('data/la_county_housing_costs.csv')

print(f"✓ Loaded {len(df):,} overdose deaths (2012-2023)")
print(f"✓ Loaded housing cost data for {len(housing_data)} years")
print()

# ============================================================================
# CALCULATE OVERDOSE RATES
# ============================================================================
print("Calculating overdose rates...")

# Overall rates by year
yearly_deaths = df.groupby('Year').size().reset_index(name='Deaths')
yearly_pop = pop_data.groupby('Year')['Population'].sum().reset_index()
yearly = yearly_deaths.merge(yearly_pop, on='Year')
yearly['Rate_Per_100k'] = (yearly['Deaths'] / yearly['Population'] * 100000).round(2)

# Rates by race and year
race_deaths = df.groupby(['Year', 'Race_Ethnicity_Cleaned'], observed=False).size().reset_index(name='Deaths')
race_rates = race_deaths.merge(pop_data, left_on=['Year', 'Race_Ethnicity_Cleaned'], right_on=['Year', 'Race'], how='left')
race_rates['Rate_Per_100k'] = (race_rates['Deaths'] / race_rates['Population'] * 100000).round(2)

print(f"✓ Calculated rates")
print()

# ============================================================================
# MERGE WITH HOUSING DATA
# ============================================================================
print("Merging with housing costs...")

# Merge overall rates with housing
yearly_full = yearly.merge(housing_data, on='Year', how='left')

# Merge race-specific rates with housing and income
race_full = race_rates.merge(housing_data, on='Year', how='left')
race_full = race_full.merge(income_data, on=['Year', 'Race'], how='left')

# Calculate housing cost burden
race_full['Rent_Burden_Pct'] = (race_full['Median_Gross_Rent'] * 12 / race_full['Median_Income'] * 100).round(2)
race_full['Home_Value_to_Income'] = (race_full['Median_Home_Value'] / race_full['Median_Income']).round(2)

print(f"✓ Merged data")
print()

# ============================================================================
# HOUSING COST TRENDS
# ============================================================================
print("=" * 70)
print("HOUSING COST TRENDS (2012-2023)")
print("=" * 70)
print()

# Calculate changes
rent_2012 = housing_data[housing_data['Year'] == 2012]['Median_Gross_Rent'].values[0]
rent_2023 = housing_data[housing_data['Year'] == 2023]['Median_Gross_Rent'].values[0]
rent_pct_change = (rent_2023 - rent_2012) / rent_2012 * 100

home_2012 = housing_data[housing_data['Year'] == 2012]['Median_Home_Value'].values[0]
home_2023 = housing_data[housing_data['Year'] == 2023]['Median_Home_Value'].values[0]
home_pct_change = (home_2023 - home_2012) / home_2012 * 100

print(f"Median Gross Rent:")
print(f"  2012: ${rent_2012:,}")
print(f"  2023: ${rent_2023:,}")
print(f"  Change: +${rent_2023 - rent_2012:,} (+{rent_pct_change:.1f}%)")
print()

print(f"Median Home Value:")
print(f"  2012: ${home_2012:,}")
print(f"  2023: ${home_2023:,}")
print(f"  Change: +${home_2023 - home_2012:,} (+{home_pct_change:.1f}%)")
print()

# ============================================================================
# CORRELATIONS
# ============================================================================
print("=" * 70)
print("HOUSING COSTS vs OVERDOSE RATES")
print("=" * 70)
print()

# Overall correlations
yearly_clean = yearly_full.dropna()

corr_rent, p_rent = stats.pearsonr(yearly_clean['Median_Gross_Rent'], yearly_clean['Rate_Per_100k'])
corr_home, p_home = stats.pearsonr(yearly_clean['Median_Home_Value'], yearly_clean['Rate_Per_100k'])

print("Overall Correlations (2012-2023):")
print(f"  Rent vs Overdose Rate:       r = {corr_rent:+.3f}, p = {p_rent:.4f}")
print(f"  Home Value vs Overdose Rate: r = {corr_home:+.3f}, p = {p_home:.4f}")
print()

# Race-specific correlations with rent burden
print("Rent Burden vs Overdose Rate (by race):")
for race in ['WHITE', 'BLACK', 'LATINE', 'ASIAN']:
    race_subset = race_full[race_full['Race'] == race].dropna(subset=['Rent_Burden_Pct', 'Rate_Per_100k'])
    if len(race_subset) > 5:
        corr, pval = stats.pearsonr(race_subset['Rent_Burden_Pct'], race_subset['Rate_Per_100k'])
        print(f"  {race:8s}: r = {corr:+.3f}, p = {pval:.4f}")
print()

# ============================================================================
# RENT BURDEN BY RACE OVER TIME
# ============================================================================
print("=" * 70)
print("RENT BURDEN TRENDS BY RACE")
print("=" * 70)
print()

print("2023 Rent Burden:")
race_2023 = race_full[race_full['Year'] == 2023].sort_values('Rent_Burden_Pct', ascending=False)
for _, row in race_2023.iterrows():
    if pd.notna(row['Rent_Burden_Pct']):
        print(f"  {row['Race']:8s}: {row['Rent_Burden_Pct']:.1f}% "
              f"(Income: ${row['Median_Income']:,.0f}, Rent: ${row['Median_Gross_Rent']:,.0f})")
print()

# ============================================================================
# HOUSING AFFORDABILITY CRISIS PERIODS
# ============================================================================
print("=" * 70)
print("HOUSING COST ACCELERATION PERIODS")
print("=" * 70)
print()

# Calculate year-over-year changes
housing_data['Rent_YoY_Change'] = housing_data['Median_Gross_Rent'].pct_change() * 100
housing_data['Home_YoY_Change'] = housing_data['Median_Home_Value'].pct_change() * 100

# Merge with overdose data
yearly_with_changes = yearly_full.merge(
    housing_data[['Year', 'Rent_YoY_Change', 'Home_YoY_Change']],
    on='Year', how='left'
)

# Find years with biggest housing cost increases
top_rent_years = housing_data.nlargest(3, 'Rent_YoY_Change')
print("Years with largest rent increases:")
for _, row in top_rent_years.iterrows():
    if pd.notna(row['Rent_YoY_Change']):
        print(f"  {int(row['Year'])}: +{row['Rent_YoY_Change']:.1f}%")
print()

# ============================================================================
# VISUALIZATIONS
# ============================================================================
print("Creating visualizations...")

fig, axes = plt.subplots(2, 3, figsize=(18, 12))

# Panel 1: Rent and overdose rate trends
ax1 = axes[0, 0].twinx()
axes[0, 0].plot(yearly_full['Year'], yearly_full['Median_Gross_Rent'], color='blue', linewidth=2.5, marker='o', label='Median Rent')
ax1.plot(yearly_full['Year'], yearly_full['Rate_Per_100k'], color='red', linewidth=2.5, marker='s', label='Overdose Rate')

axes[0, 0].set_xlabel('Year', fontsize=11)
axes[0, 0].set_ylabel('Median Gross Rent ($)', fontsize=11, color='blue')
ax1.set_ylabel('Overdose Rate per 100,000', fontsize=11, color='red')
axes[0, 0].set_title(f'Rent vs Overdose Rate\nr = {corr_rent:+.3f}, p = {p_rent:.4f}',
                      fontsize=12, fontweight='bold')
axes[0, 0].tick_params(axis='y', labelcolor='blue')
ax1.tick_params(axis='y', labelcolor='red')
axes[0, 0].grid(True, alpha=0.3)

# Panel 2: Home value and overdose rate trends
ax2 = axes[0, 1].twinx()
axes[0, 1].plot(yearly_full['Year'], yearly_full['Median_Home_Value'], color='green', linewidth=2.5, marker='o', label='Home Value')
ax2.plot(yearly_full['Year'], yearly_full['Rate_Per_100k'], color='red', linewidth=2.5, marker='s', label='Overdose Rate')

axes[0, 1].set_xlabel('Year', fontsize=11)
axes[0, 1].set_ylabel('Median Home Value ($)', fontsize=11, color='green')
ax2.set_ylabel('Overdose Rate per 100,000', fontsize=11, color='red')
axes[0, 1].set_title(f'Home Value vs Overdose Rate\nr = {corr_home:+.3f}, p = {p_home:.4f}',
                      fontsize=12, fontweight='bold')
axes[0, 1].tick_params(axis='y', labelcolor='green')
ax2.tick_params(axis='y', labelcolor='red')
axes[0, 1].ticklabel_format(style='plain', axis='y')
axes[0, 1].grid(True, alpha=0.3)

# Panel 3: Rent burden by race over time
for race in ['WHITE', 'BLACK', 'LATINE', 'ASIAN']:
    race_data = race_full[race_full['Race'] == race].dropna(subset=['Rent_Burden_Pct']).sort_values('Year')
    if len(race_data) > 0:
        color = RACE_COLORS.get(race, 'gray')
        axes[0, 2].plot(race_data['Year'], race_data['Rent_Burden_Pct'], label=race, color=color, linewidth=2, marker='o')

axes[0, 2].set_xlabel('Year', fontsize=11)
axes[0, 2].set_ylabel('Rent as % of Income', fontsize=11)
axes[0, 2].set_title('Rent Burden by Race\n(Annual Rent / Annual Income)', fontsize=12, fontweight='bold')
axes[0, 2].legend()
axes[0, 2].grid(True, alpha=0.3)

# Panel 4: Scatter - rent vs overdose rate
yearly_scatter = yearly_full.dropna()
axes[1, 0].scatter(yearly_scatter['Median_Gross_Rent'], yearly_scatter['Rate_Per_100k'], s=100, alpha=0.7)

# Add regression line
z = np.polyfit(yearly_scatter['Median_Gross_Rent'], yearly_scatter['Rate_Per_100k'], 1)
p = np.poly1d(z)
x_line = np.linspace(yearly_scatter['Median_Gross_Rent'].min(), yearly_scatter['Median_Gross_Rent'].max(), 100)
axes[1, 0].plot(x_line, p(x_line), "r--", alpha=0.8, linewidth=2)

# Label points with years
for _, row in yearly_scatter.iterrows():
    axes[1, 0].text(row['Median_Gross_Rent'] + 10, row['Rate_Per_100k'], str(int(row['Year'])), fontsize=8)

axes[1, 0].set_xlabel('Median Gross Rent ($)', fontsize=11)
axes[1, 0].set_ylabel('Overdose Rate per 100,000', fontsize=11)
axes[1, 0].set_title('Rent vs Overdose Rate\n(Each point = 1 year)', fontsize=12, fontweight='bold')

# Panel 5: Year-over-year rent changes vs overdose changes
yearly_w_lag = yearly_with_changes.copy()
yearly_w_lag['Death_YoY_Change'] = yearly_w_lag['Deaths'].pct_change() * 100

scatter_yoy = yearly_w_lag.dropna(subset=['Rent_YoY_Change', 'Death_YoY_Change'])
if len(scatter_yoy) > 2:
    axes[1, 1].scatter(scatter_yoy['Rent_YoY_Change'], scatter_yoy['Death_YoY_Change'], s=100, alpha=0.7)

    for _, row in scatter_yoy.iterrows():
        axes[1, 1].text(row['Rent_YoY_Change'] + 0.1, row['Death_YoY_Change'], str(int(row['Year'])), fontsize=8)

    axes[1, 1].axhline(0, color='gray', linestyle='--', alpha=0.5)
    axes[1, 1].axvline(0, color='gray', linestyle='--', alpha=0.5)
    axes[1, 1].set_xlabel('Rent Change (% YoY)', fontsize=11)
    axes[1, 1].set_ylabel('Death Change (% YoY)', fontsize=11)
    axes[1, 1].set_title('Rent Increases vs Death Increases\n(Year-over-year)', fontsize=12, fontweight='bold')
    axes[1, 1].grid(True, alpha=0.3)

# Panel 6: Summary text
axes[1, 2].axis('off')

summary_text = f"""
HOUSING COSTS SUMMARY

RENT TRENDS (2012-2023):
• 2012: ${rent_2012:,}/month
• 2023: ${rent_2023:,}/month
• Change: +{rent_pct_change:.1f}%

HOME VALUE TRENDS:
• 2012: ${home_2012:,}
• 2023: ${home_2023:,}
• Change: +{home_pct_change:.1f}%

CORRELATIONS:
• Rent ↔ Overdose:  r = {corr_rent:+.3f}
• Home ↔ Overdose:  r = {corr_home:+.3f}

2023 RENT BURDEN:
"""

for _, row in race_2023.iterrows():
    if pd.notna(row['Rent_Burden_Pct']):
        summary_text += f"• {row['Race']:8s}: {row['Rent_Burden_Pct']:.1f}%\n"

summary_text += f"""

INTERPRETATION:
{"Strong positive" if corr_rent > 0.7 else "Moderate positive" if corr_rent > 0.5 else "Positive but modest"}
correlation between
rising rent costs and overdose
deaths, suggesting housing
affordability crisis may
contribute to overdose risk.
"""

axes[1, 2].text(0.1, 0.9, summary_text, fontsize=9, verticalalignment='top',
                family='monospace', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

plt.tight_layout()
plt.savefig(output_dir / 'housing_costs_analysis.png', dpi=300, bbox_inches='tight')
print(f"✓ Saved: {output_dir / 'housing_costs_analysis.png'}")
print()

# Save results
yearly_full.to_csv(output_dir / 'housing_costs_overdose_trends.csv', index=False)
race_full.to_csv(output_dir / 'housing_costs_by_race.csv', index=False)
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
print(f"• Median rent increased {rent_pct_change:.1f}% from 2012 to 2023")
print(f"• Median home value increased {home_pct_change:.1f}% from 2012 to 2023")
print(f"• Rent-overdose correlation: r = {corr_rent:+.3f} (p = {p_rent:.4f})")
print(f"• Home value-overdose correlation: r = {corr_home:+.3f} (p = {p_home:.4f})")
print()

print("=" * 70)
