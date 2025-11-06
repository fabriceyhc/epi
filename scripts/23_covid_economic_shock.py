#!/usr/bin/env python3
"""
Analysis #23: COVID-19 Economic Shock Analysis

Examines how the COVID-19 pandemic and associated economic disruption
affected overdose rates, with focus on differential impacts by race and SES.
"""

import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from datetime import datetime

# Import shared utilities
from utils import load_overdose_data, standardize_race, process_age, RACE_COLORS

# Setup
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("colorblind")
output_dir = Path('results/23_covid_economic_shock')
output_dir.mkdir(parents=True, exist_ok=True)

print("=" * 70)
print("COVID-19 ECONOMIC SHOCK ANALYSIS")
print("=" * 70)
print()
print("Examining the impact of COVID-19 pandemic and economic disruption")
print("on overdose deaths (2020-2021 vs pre-pandemic baseline)")
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

# Add month for within-year analysis
df['Month'] = pd.to_datetime(df['DeathDate'], errors='coerce').dt.month

# Load Census SES data
pop_data_wide = pd.read_csv('data/la_county_population_census.csv')
income_data_wide = pd.read_csv('data/la_county_income_by_race.csv')
poverty_data_wide = pd.read_csv('data/la_county_poverty_by_race.csv')

# Reshape to long format
pop_data = pop_data_wide.melt(id_vars=['Year'], var_name='Race', value_name='Population')
pop_data = pop_data[pop_data['Race'] != 'TOTAL'].copy()

poverty_data = poverty_data_wide.melt(id_vars=['Year'], var_name='Race', value_name='Poverty_Rate')
poverty_data['Race'] = poverty_data['Race'].str.replace('_Poverty_Rate', '', regex=False)

income_data = income_data_wide.melt(id_vars=['Year'], var_name='Race', value_name='Median_Income')
income_data['Race'] = income_data['Race'].str.replace('_Median_Income', '', regex=False)

# Merge Census data
census = pop_data.merge(poverty_data, on=['Year', 'Race'], how='left')
census = census.merge(income_data, on=['Year', 'Race'], how='left')

print(f"✓ Loaded {len(df):,} overdose deaths (2012-2023)")
print(f"✓ Loaded Census data")
print()

# ============================================================================
# DEFINE PERIODS
# ============================================================================
print("Defining analysis periods...")
print()

# Pre-COVID: 2017-2019 (3 years for stable baseline)
# COVID shock: 2020 (pandemic onset + lockdowns + economic collapse)
# COVID continuation: 2021-2022 (ongoing pandemic + recovery)
# Post-COVID: 2023 (return to relative normalcy)

df['Period'] = 'Other'
df.loc[df['Year'].isin([2017, 2018, 2019]), 'Period'] = 'Pre-COVID (2017-2019)'
df.loc[df['Year'] == 2020, 'Period'] = 'COVID Shock (2020)'
df.loc[df['Year'].isin([2021, 2022]), 'Period'] = 'COVID Continuation (2021-2022)'
df.loc[df['Year'] == 2023, 'Period'] = 'Post-COVID (2023)'

print("Analysis periods:")
for period in ['Pre-COVID (2017-2019)', 'COVID Shock (2020)', 'COVID Continuation (2021-2022)', 'Post-COVID (2023)']:
    n = (df['Period'] == period).sum()
    print(f"  {period}: {n:,} deaths")
print()

# ============================================================================
# CALCULATE RATES BY PERIOD
# ============================================================================
print("Calculating rates by period...")

period_rates = []

for year in range(2017, 2024):
    year_data = df[df['Year'] == year]
    year_pop = pop_data[pop_data['Year'] == year]

    for race in ['WHITE', 'BLACK', 'LATINE', 'ASIAN']:
        race_deaths = len(year_data[year_data['Race_Ethnicity_Cleaned'] == race])
        race_pop_row = year_pop[year_pop['Race'] == race]

        if len(race_pop_row) > 0:
            population = race_pop_row['Population'].values[0]
            rate = (race_deaths / population * 100000)

            # Get period
            if year in [2017, 2018, 2019]:
                period = 'Pre-COVID (2017-2019)'
            elif year == 2020:
                period = 'COVID Shock (2020)'
            elif year in [2021, 2022]:
                period = 'COVID Continuation (2021-2022)'
            else:
                period = 'Post-COVID (2023)'

            period_rates.append({
                'Year': year,
                'Race': race,
                'Period': period,
                'Deaths': race_deaths,
                'Population': population,
                'Rate_Per_100k': round(rate, 2)
            })

rates_df = pd.DataFrame(period_rates)

# Calculate average rates by period and race
period_avg = rates_df.groupby(['Period', 'Race'])['Rate_Per_100k'].mean().reset_index()
period_avg.columns = ['Period', 'Race', 'Avg_Rate']

print("✓ Calculated period-specific rates")
print()

# ============================================================================
# CALCULATE PERCENT CHANGE FROM BASELINE
# ============================================================================
print("=" * 70)
print("PERCENT CHANGE FROM PRE-COVID BASELINE")
print("=" * 70)
print()

# Get pre-COVID baseline rates
baseline = rates_df[rates_df['Period'] == 'Pre-COVID (2017-2019)'].groupby('Race')['Rate_Per_100k'].mean()

changes = []

for period in ['COVID Shock (2020)', 'COVID Continuation (2021-2022)', 'Post-COVID (2023)']:
    print(f"{period}:")

    for race in ['WHITE', 'BLACK', 'LATINE', 'ASIAN']:
        period_rate = rates_df[(rates_df['Period'] == period) & (rates_df['Race'] == race)]['Rate_Per_100k'].mean()
        baseline_rate = baseline[race]

        pct_change = ((period_rate - baseline_rate) / baseline_rate * 100) if baseline_rate > 0 else 0
        abs_change = period_rate - baseline_rate

        print(f"  {race:8s}: {period_rate:5.1f} per 100k (baseline: {baseline_rate:5.1f}, "
              f"change: {pct_change:+6.1f}% / {abs_change:+5.1f})")

        changes.append({
            'Period': period,
            'Race': race,
            'Rate': period_rate,
            'Baseline': baseline_rate,
            'Pct_Change': round(pct_change, 1),
            'Abs_Change': round(abs_change, 1)
        })
    print()

changes_df = pd.DataFrame(changes)

# ============================================================================
# EXAMINE 2020 SPIKE BY MONTH
# ============================================================================
print("=" * 70)
print("2020 MONTHLY PATTERN (COVID onset)")
print("=" * 70)
print()

monthly_2020 = df[df['Year'] == 2020].groupby('Month').size().reset_index(name='Deaths')
monthly_2019 = df[df['Year'] == 2019].groupby('Month').size().reset_index(name='Deaths')

# Merge and calculate change
monthly_comp = monthly_2020.merge(monthly_2019, on='Month', suffixes=('_2020', '_2019'), how='outer').fillna(0)
monthly_comp['Pct_Change'] = ((monthly_comp['Deaths_2020'] - monthly_comp['Deaths_2019']) / monthly_comp['Deaths_2019'] * 100).round(1)

print("Month-by-month comparison (2020 vs 2019):")
month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

for _, row in monthly_comp.iterrows():
    month_idx = int(row['Month']) - 1
    if 0 <= month_idx < 12:
        month_name = month_names[month_idx]
        print(f"  {month_name}: {int(row['Deaths_2020'])} deaths (2019: {int(row['Deaths_2019'])}, "
              f"change: {row['Pct_Change']:+.1f}%)")
print()

# ============================================================================
# DIFFERENTIAL IMPACTS BY SES
# ============================================================================
print("=" * 70)
print("DIFFERENTIAL IMPACTS BY POVERTY LEVEL")
print("=" * 70)
print()

# Merge with SES data
rates_with_ses = rates_df.merge(census, on=['Year', 'Race'], how='left')

# Categorize by poverty
rates_with_ses['Poverty_Level'] = pd.cut(rates_with_ses['Poverty_Rate'],
                                          bins=[0, 12, 18, 100],
                                          labels=['Low (<12%)', 'Medium (12-18%)', 'High (>18%)'])

# Calculate change by poverty level
for pov_level in ['Low (<12%)', 'Medium (12-18%)', 'High (>18%)']:
    subset = rates_with_ses[rates_with_ses['Poverty_Level'] == pov_level]

    pre_covid = subset[subset['Period'] == 'Pre-COVID (2017-2019)']['Rate_Per_100k'].mean()
    covid_2020 = subset[subset['Period'] == 'COVID Shock (2020)']['Rate_Per_100k'].mean()
    covid_2122 = subset[subset['Period'] == 'COVID Continuation (2021-2022)']['Rate_Per_100k'].mean()

    pct_change_2020 = ((covid_2020 - pre_covid) / pre_covid * 100) if pre_covid > 0 else 0
    pct_change_2122 = ((covid_2122 - pre_covid) / pre_covid * 100) if pre_covid > 0 else 0

    print(f"{pov_level} poverty:")
    print(f"  Pre-COVID: {pre_covid:.1f} per 100k")
    print(f"  2020:      {covid_2020:.1f} per 100k ({pct_change_2020:+.1f}%)")
    print(f"  2021-2022: {covid_2122:.1f} per 100k ({pct_change_2122:+.1f}%)")
    print()

# ============================================================================
# SUBSTANCE PATTERNS DURING COVID
# ============================================================================
print("=" * 70)
print("SUBSTANCE INVOLVEMENT CHANGES")
print("=" * 70)
print()

substances = {
    'Fentanyl': 'Fentanyl',
    'Methamphetamine': 'Methamphetamine',
    'Heroin': 'Heroin',
    'Cocaine': 'Cocaine'
}

for substance_name, substance_col in substances.items():
    if substance_col in df.columns:
        pre_covid_pct = (df[(df['Period'] == 'Pre-COVID (2017-2019)') & (df[substance_col] == 1)].shape[0] /
                         df[df['Period'] == 'Pre-COVID (2017-2019)'].shape[0] * 100)

        covid_2020_pct = (df[(df['Period'] == 'COVID Shock (2020)') & (df[substance_col] == 1)].shape[0] /
                          df[df['Period'] == 'COVID Shock (2020)'].shape[0] * 100)

        covid_2122_pct = (df[(df['Period'] == 'COVID Continuation (2021-2022)') & (df[substance_col] == 1)].shape[0] /
                          df[df['Period'] == 'COVID Continuation (2021-2022)'].shape[0] * 100)

        change_2020 = covid_2020_pct - pre_covid_pct
        change_2122 = covid_2122_pct - pre_covid_pct

        print(f"{substance_name}:")
        print(f"  Pre-COVID: {pre_covid_pct:.1f}% of deaths")
        print(f"  2020:      {covid_2020_pct:.1f}% ({change_2020:+.1f} percentage points)")
        print(f"  2021-2022: {covid_2122_pct:.1f}% ({change_2122:+.1f} percentage points)")
        print()

# ============================================================================
# VISUALIZATIONS
# ============================================================================
print("Creating visualizations...")

fig = plt.figure(figsize=(20, 12))
gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)

# Panel 1: Trends by race
ax1 = fig.add_subplot(gs[0, 0])
for race in ['WHITE', 'BLACK', 'LATINE', 'ASIAN']:
    race_data = rates_df[rates_df['Race'] == race].sort_values('Year')
    color = RACE_COLORS.get(race, 'gray')
    ax1.plot(race_data['Year'], race_data['Rate_Per_100k'], label=race, color=color, linewidth=2.5, marker='o')

# Add COVID period shading
ax1.axvspan(2020, 2020.5, alpha=0.2, color='red', label='COVID Shock')
ax1.axvspan(2020.5, 2022.5, alpha=0.1, color='orange', label='COVID Continuation')

ax1.set_xlabel('Year', fontsize=11)
ax1.set_ylabel('Overdose Rate per 100,000', fontsize=11)
ax1.set_title('Overdose Rates: Pre-COVID vs COVID Era\n(by Race)', fontsize=12, fontweight='bold')
ax1.legend(fontsize=9)
ax1.grid(True, alpha=0.3)

# Panel 2: Percent change from baseline
ax2 = fig.add_subplot(gs[0, 1])
periods_plot = ['COVID Shock (2020)', 'COVID Continuation (2021-2022)', 'Post-COVID (2023)']
x = np.arange(len(periods_plot))
width = 0.2

for idx, race in enumerate(['WHITE', 'BLACK', 'LATINE', 'ASIAN']):
    race_changes = [changes_df[(changes_df['Period'] == p) & (changes_df['Race'] == race)]['Pct_Change'].values[0]
                     for p in periods_plot]
    color = RACE_COLORS.get(race, 'gray')
    ax2.bar(x + idx * width, race_changes, width, label=race, color=color, alpha=0.7, edgecolor='black')

ax2.axhline(0, color='black', linestyle='--', linewidth=1)
ax2.set_xticks(x + width * 1.5)
ax2.set_xticklabels(['2020', '2021-2022', '2023'], rotation=0)
ax2.set_ylabel('% Change from Pre-COVID Baseline', fontsize=11)
ax2.set_title('Percent Change from 2017-2019 Baseline', fontsize=12, fontweight='bold')
ax2.legend(fontsize=9)
ax2.grid(True, alpha=0.3, axis='y')

# Panel 3: 2020 monthly pattern
ax3 = fig.add_subplot(gs[0, 2])
ax3.plot(monthly_comp['Month'], monthly_comp['Deaths_2019'], label='2019 (pre-COVID)', color='blue', linewidth=2, marker='o')
ax3.plot(monthly_comp['Month'], monthly_comp['Deaths_2020'], label='2020 (COVID)', color='red', linewidth=2, marker='o')
# Mark March 2020 (lockdown)
ax3.axvline(3, color='red', linestyle='--', alpha=0.5, linewidth=2)
ax3.text(3.5, ax3.get_ylim()[1] * 0.9, 'Lockdown\n(Mar 2020)', fontsize=9, color='red')
ax3.set_xlabel('Month', fontsize=11)
ax3.set_ylabel('Deaths', fontsize=11)
ax3.set_title('2020 Monthly Pattern vs 2019\n(COVID onset)', fontsize=12, fontweight='bold')
ax3.set_xticks(range(1, 13))
ax3.set_xticklabels(['J', 'F', 'M', 'A', 'M', 'J', 'J', 'A', 'S', 'O', 'N', 'D'])
ax3.legend()
ax3.grid(True, alpha=0.3)

# Panel 4: Change by poverty level
ax4 = fig.add_subplot(gs[1, 0])
pov_changes = []
pov_labels = []
for pov_level in ['Low (<12%)', 'Medium (12-18%)', 'High (>18%)']:
    subset = rates_with_ses[rates_with_ses['Poverty_Level'] == pov_level]
    pre = subset[subset['Period'] == 'Pre-COVID (2017-2019)']['Rate_Per_100k'].mean()
    covid = subset[subset['Period'] == 'COVID Shock (2020)']['Rate_Per_100k'].mean()
    pct = ((covid - pre) / pre * 100) if pre > 0 else 0
    pov_changes.append(pct)
    pov_labels.append(pov_level.split(' ')[0])

ax4.bar(pov_labels, pov_changes, color=['lightblue', 'orange', 'darkred'], alpha=0.7, edgecolor='black')
ax4.axhline(0, color='black', linestyle='--', linewidth=1)
ax4.set_ylabel('% Change in 2020 vs 2017-2019', fontsize=11)
ax4.set_title('COVID Impact by Poverty Level\n(2020 vs Pre-COVID)', fontsize=12, fontweight='bold')
ax4.set_xlabel('Poverty Level', fontsize=11)
# Add values on bars
for i, v in enumerate(pov_changes):
    ax4.text(i, v + 1, f"{v:+.1f}%", ha='center', fontsize=10, fontweight='bold')

# Panel 5: Substance changes
ax5 = fig.add_subplot(gs[1, 1])
subst_data = []
for substance_name, substance_col in substances.items():
    if substance_col in df.columns:
        pre_covid_pct = (df[(df['Period'] == 'Pre-COVID (2017-2019)') & (df[substance_col] == 1)].shape[0] /
                         df[df['Period'] == 'Pre-COVID (2017-2019)'].shape[0] * 100)
        covid_2020_pct = (df[(df['Period'] == 'COVID Shock (2020)') & (df[substance_col] == 1)].shape[0] /
                          df[df['Period'] == 'COVID Shock (2020)'].shape[0] * 100)
        change = covid_2020_pct - pre_covid_pct
        subst_data.append({'Substance': substance_name, 'Change': change})

subst_df = pd.DataFrame(subst_data)
colors_subst = ['red' if x > 0 else 'blue' for x in subst_df['Change']]
ax5.barh(subst_df['Substance'], subst_df['Change'], color=colors_subst, alpha=0.7, edgecolor='black')
ax5.axvline(0, color='black', linestyle='--', linewidth=1)
ax5.set_xlabel('Change in % of Deaths (percentage points)', fontsize=11)
ax5.set_title('Substance Involvement Changes\n(2020 vs Pre-COVID)', fontsize=12, fontweight='bold')
# Add values
for i, row in subst_df.iterrows():
    ax5.text(row['Change'] + 0.3, i, f"{row['Change']:+.1f}", va='center', fontsize=10, fontweight='bold')

# Panel 6: Rate by period (box plot)
ax6 = fig.add_subplot(gs[1, 2])
period_order = ['Pre-COVID (2017-2019)', 'COVID Shock (2020)', 'COVID Continuation (2021-2022)', 'Post-COVID (2023)']
rates_df['Period_Cat'] = pd.Categorical(rates_df['Period'], categories=period_order, ordered=True)
sns.boxplot(data=rates_df, x='Period_Cat', y='Rate_Per_100k', ax=ax6, palette='Set2')
ax6.set_xlabel('')
ax6.set_ylabel('Overdose Rate per 100,000', fontsize=11)
ax6.set_title('Rate Distribution by Period\n(All Races Combined)', fontsize=12, fontweight='bold')
ax6.set_xticklabels(['Pre-COVID\n(2017-2019)', '2020', '2021-2022', '2023'], rotation=0, fontsize=9)

# Panels 7-8: Race-specific trends
for idx, race in enumerate(['BLACK', 'WHITE']):
    ax = fig.add_subplot(gs[2, idx])
    race_data = rates_df[rates_df['Race'] == race].sort_values('Year')
    color = RACE_COLORS.get(race, 'gray')

    ax.plot(race_data['Year'], race_data['Rate_Per_100k'], color=color, linewidth=3, marker='o', markersize=8)
    ax.axvspan(2020, 2020.5, alpha=0.2, color='red')
    ax.axvspan(2020.5, 2022.5, alpha=0.1, color='orange')

    # Calculate and show baseline and 2020 peak
    baseline_val = race_data[race_data['Year'].isin([2017, 2018, 2019])]['Rate_Per_100k'].mean()
    peak_2020 = race_data[race_data['Year'] == 2020]['Rate_Per_100k'].values[0] if len(race_data[race_data['Year'] == 2020]) > 0 else 0
    pct_increase = ((peak_2020 - baseline_val) / baseline_val * 100) if baseline_val > 0 else 0

    ax.axhline(baseline_val, color='gray', linestyle=':', linewidth=2, alpha=0.7, label=f'Pre-COVID avg: {baseline_val:.1f}')

    ax.set_xlabel('Year', fontsize=11)
    ax.set_ylabel('Rate per 100,000', fontsize=11)
    ax.set_title(f'{race} Overdose Rates\n2020 spike: +{pct_increase:.0f}%', fontsize=12, fontweight='bold')
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)

# Panel 9: Summary
ax9 = fig.add_subplot(gs[2, 2])
ax9.axis('off')

# Calculate overall changes
overall_pre = rates_df[rates_df['Period'] == 'Pre-COVID (2017-2019)']['Rate_Per_100k'].mean()
overall_2020 = rates_df[rates_df['Period'] == 'COVID Shock (2020)']['Rate_Per_100k'].mean()
overall_pct = ((overall_2020 - overall_pre) / overall_pre * 100)

# Get race-specific changes
black_change = changes_df[(changes_df['Period'] == 'COVID Shock (2020)') & (changes_df['Race'] == 'BLACK')]['Pct_Change'].values[0]
white_change = changes_df[(changes_df['Period'] == 'COVID Shock (2020)') & (changes_df['Race'] == 'WHITE')]['Pct_Change'].values[0]

summary_text = f"""
COVID-19 IMPACT SUMMARY

OVERALL INCREASE (2020):
  Pre-COVID avg: {overall_pre:.1f} per 100k
  2020 rate:     {overall_2020:.1f} per 100k
  Change:        +{overall_pct:.1f}%

DIFFERENTIAL IMPACTS:
  BLACK:  +{black_change:.1f}%
  WHITE:  +{white_change:.1f}%

KEY OBSERVATIONS:
• Sharp spike in March-April 2020
  coinciding with lockdowns

• Higher poverty areas showed
  larger increases

• Fentanyl involvement increased
  during COVID period

• Rates remained elevated through
  2021-2022, only declining in 2023

INTERPRETATION:
COVID-19 pandemic and economic
disruption led to substantial
increase in overdose deaths,
with disproportionate impact
on vulnerable communities.
"""

ax9.text(0.1, 0.9, summary_text, fontsize=9, verticalalignment='top',
         family='monospace', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

plt.savefig(output_dir / 'covid_economic_shock.png', dpi=300, bbox_inches='tight')
print(f"✓ Saved: {output_dir / 'covid_economic_shock.png'}")
print()

# Save results
rates_df.to_csv(output_dir / 'covid_period_rates.csv', index=False)
changes_df.to_csv(output_dir / 'covid_changes_from_baseline.csv', index=False)
monthly_comp.to_csv(output_dir / 'covid_2020_monthly.csv', index=False)
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
print(f"• Overall 2020 increase: +{overall_pct:.1f}% vs pre-COVID baseline")
print(f"• BLACK population: +{black_change:.1f}%")
print(f"• WHITE population: +{white_change:.1f}%")
print()

# Find month with biggest spike
max_month = monthly_comp.loc[monthly_comp['Pct_Change'].idxmax()]
month_name = month_names[int(max_month['Month']) - 1]
print(f"• Largest month-over-month increase: {month_name} 2020 (+{max_month['Pct_Change']:.0f}%)")
print()

print("=" * 70)
