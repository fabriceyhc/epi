#!/usr/bin/env python
# coding: utf-8

"""
Create Publication Figure: SES Context for Overdose Disparities
Combines overdose rates with poverty, income, and population age data
Shows that disparities are NOT explained by age differences
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

print("="*70)
print("CREATING SES CONTEXT FIGURE")
print("="*70)

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
colors = {
    'WHITE': '#4472C4',
    'BLACK': '#ED7D31',
    'LATINE': '#A5A5A5',
    'ASIAN': '#FFC000'
}

# Load data
print("\nLoading data...")
overdose_df = pd.read_csv('results/12_ses_context_figure/race_rates_annual.csv')
poverty_df = pd.read_csv('data/la_county_poverty_by_race.csv')
income_df = pd.read_csv('data/la_county_income_by_race.csv')
age_df = pd.read_csv('data/la_county_age_by_race.csv')

print(f"Overdose data: {len(overdose_df)} rows")
print(f"Poverty data: {len(poverty_df)} rows")
print(f"Income data: {len(income_df)} rows")
print(f"Age data: {len(age_df)} rows")

# Create figure with 6 panels
fig = plt.figure(figsize=(20, 12))
gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)

race_groups = ['WHITE', 'BLACK', 'LATINE', 'ASIAN']
race_labels = {
    'WHITE': 'White (NH)',
    'BLACK': 'Black (NH)',
    'LATINE': 'Latine',
    'ASIAN': 'Asian (NH)'
}

# Panel A: Overdose Death Rates per 100k
ax1 = fig.add_subplot(gs[0, 0])
for race in race_groups:
    race_data = overdose_df[overdose_df['Race'] == race]
    ax1.plot(race_data['Year'], race_data['Rate_per_100k'],
             marker='o', linewidth=2.5, markersize=6,
             color=colors[race], label=race_labels[race])

ax1.set_xlabel('Year', fontsize=12, fontweight='bold')
ax1.set_ylabel('Overdose Deaths per 100,000', fontsize=12, fontweight='bold')
ax1.set_title('A. Overdose Death Rates by Race', fontsize=14, fontweight='bold', pad=15)
ax1.legend(loc='upper left', fontsize=10)
ax1.grid(True, alpha=0.3)
ax1.set_xlim(2011.5, 2023.5)

# Panel B: Disparity Ratios
ax2 = fig.add_subplot(gs[0, 1])
for race in race_groups:
    race_data = overdose_df[overdose_df['Race'] == race]
    ax2.plot(race_data['Year'], race_data['Disparity_Ratio'],
             marker='o', linewidth=2.5, markersize=6,
             color=colors[race], label=race_labels[race])

ax2.axhline(y=1.0, color='black', linestyle='--', linewidth=1.5, alpha=0.5,
            label='Proportional representation')
ax2.set_xlabel('Year', fontsize=12, fontweight='bold')
ax2.set_ylabel('Disparity Ratio', fontsize=12, fontweight='bold')
ax2.set_title('B. Disparity Ratios (% Deaths / % Population)', fontsize=14, fontweight='bold', pad=15)
ax2.legend(loc='upper left', fontsize=10)
ax2.grid(True, alpha=0.3)
ax2.set_xlim(2011.5, 2023.5)

# Panel C: Poverty Rates
ax3 = fig.add_subplot(gs[1, 0])
for race in race_groups:
    ax3.plot(poverty_df['Year'], poverty_df[f'{race}_Poverty_Rate'],
             marker='s', linewidth=2.5, markersize=6,
             color=colors[race], label=race_labels[race])

ax3.set_xlabel('Year', fontsize=12, fontweight='bold')
ax3.set_ylabel('Poverty Rate (%)', fontsize=12, fontweight='bold')
ax3.set_title('C. Poverty Rates by Race', fontsize=14, fontweight='bold', pad=15)
ax3.legend(loc='upper right', fontsize=10)
ax3.grid(True, alpha=0.3)
ax3.set_xlim(2011.5, 2023.5)

# Panel D: Median Household Income
ax4 = fig.add_subplot(gs[1, 1])
for race in race_groups:
    ax4.plot(income_df['Year'], income_df[f'{race}_Median_Income'] / 1000,
             marker='s', linewidth=2.5, markersize=6,
             color=colors[race], label=race_labels[race])

ax4.set_xlabel('Year', fontsize=12, fontweight='bold')
ax4.set_ylabel('Median Household Income ($1,000s)', fontsize=12, fontweight='bold')
ax4.set_title('D. Median Household Income by Race', fontsize=14, fontweight='bold', pad=15)
ax4.legend(loc='upper left', fontsize=10)
ax4.grid(True, alpha=0.3)
ax4.set_xlim(2011.5, 2023.5)

# Panel E: Median Population Age
ax5 = fig.add_subplot(gs[2, 0])
for race in race_groups:
    ax5.plot(age_df['Year'], age_df[f'{race}_Median_Age'],
             marker='s', linewidth=2.5, markersize=6,
             color=colors[race], label=race_labels[race])

ax5.set_xlabel('Year', fontsize=12, fontweight='bold')
ax5.set_ylabel('Median Age (years)', fontsize=12, fontweight='bold')
ax5.set_title('E. Median Population Age by Race', fontsize=14, fontweight='bold', pad=15)
ax5.legend(loc='upper left', fontsize=10)
ax5.grid(True, alpha=0.3)
ax5.set_xlim(2011.5, 2023.5)

# Panel F: Key Finding Text Box
ax6 = fig.add_subplot(gs[2, 1])
ax6.axis('off')

text_content = """
KEY FINDINGS: SES CONTEXT FOR OVERDOSE DISPARITIES (2023)

OVERDOSE BURDEN:
  • Black individuals: Highest death rate (85.4 per 100k)
  • White individuals: 42.5 per 100k
  • Latine individuals: 24.4 per 100k
  • Asian individuals: 6.0 per 100k

DISPARITY RATIOS (% deaths / % population):
  • Black: 2.90 (nearly 3x overrepresented)
  • White: 1.44 (moderately overrepresented)
  • Latine: 0.83 (slightly underrepresented)
  • Asian: 0.20 (highly underrepresented)

SOCIOECONOMIC CONTEXT:
Poverty Rates:
  • Black: 20.9% (highest) - BUT poverty alone doesn't explain
  • Latine: 15.0%           disparity (Black 2.9x vs 1.4x poverty)
  • Asian: 11.7%
  • White: 10.8% (lowest)

Median Household Income:
  • White: $107,041 (highest)
  • Asian: $100,119
  • Latine: $75,772
  • Black: $60,696 (lowest)

Median Population Age:
  • White: 45.8 years (oldest population)
  • Asian: 44.2 years
  • Black: 40.2 years
  • Latine: 33.8 years (youngest population)

CRITICAL INSIGHT:
Black individuals experience the highest overdose death rates despite
having a YOUNGER population age than White individuals (40.2 vs 45.8
years). This contradicts the notion that age alone explains disparities.

The 2.9x overrepresentation in deaths cannot be explained solely by
poverty rates (Black poverty is only 1.9x higher than White, not 2.9x).

These findings suggest structural inequities beyond individual-level
SES factors drive racial disparities in overdose deaths.
"""

ax6.text(0.05, 0.95, text_content, transform=ax6.transAxes,
         fontsize=11, verticalalignment='top',
         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3),
         family='monospace')

# Overall title
fig.suptitle('Socioeconomic Context for Racial Disparities in Overdose Deaths\nLos Angeles County, 2012-2023',
             fontsize=16, fontweight='bold', y=0.995)

# Save figure
output_path = 'results/12_ses_context_figure/ses_context_figure.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
print(f"\n✓ Saved figure: {output_path}")

plt.close()

print("\n" + "="*70)
print("CREATING 2023 SNAPSHOT TABLE")
print("="*70)

# Create publication table comparing 2023 values
data_2023 = {
    'Race': ['Black (NH)', 'White (NH)', 'Latine', 'Asian (NH)'],
    'Overdose_Rate_per_100k': [85.40, 42.49, 24.36, 5.98],
    'Disparity_Ratio': [2.90, 1.44, 0.83, 0.20],
    'Poverty_Rate_%': [20.9, 10.8, 15.0, 11.7],
    'Median_Income': [60696, 107041, 75772, 100119],
    'Median_Age': [40.2, 45.8, 33.8, 44.2],
    'Population': [709583, 2369899, 4695902, 1454666],
    'Pct_of_LA_County': [7.3, 24.5, 48.6, 15.1]
}

table_df = pd.DataFrame(data_2023)

# Calculate poverty ratio (relative to White)
table_df['Poverty_Ratio_vs_White'] = table_df['Poverty_Rate_%'] / table_df.loc[table_df['Race'] == 'White (NH)', 'Poverty_Rate_%'].values[0]

# Calculate income ratio (relative to White)
table_df['Income_Ratio_vs_White'] = table_df['Median_Income'] / table_df.loc[table_df['Race'] == 'White (NH)', 'Median_Income'].values[0]

# Save table
table_path = 'results/12_ses_context_figure/ses_comparison_2023.csv'
table_df.to_csv(table_path, index=False)
print(f"\n✓ Saved table: {table_path}")

# Display table
print("\n2023 SNAPSHOT COMPARISON:")
print("="*100)
print(table_df.to_string(index=False))

print("\n" + "="*70)
print("ANALYSIS COMPLETE")
print("="*70)
print("\nKEY INSIGHT:")
print("Black individuals have 2.9x overrepresentation in overdose deaths,")
print("but only 1.9x higher poverty rate compared to White individuals.")
print("This suggests structural factors beyond individual SES drive disparities.")
print("="*70)
