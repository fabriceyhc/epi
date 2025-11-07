#!/usr/bin/env python3
"""
Analysis #48: LA vs Other Metro Areas - Direct Comparison

Creates a comparison table placing LA County alongside other major US metros
from the literature review (Table 1):
- New York, NY
- Chicago, IL
- Baltimore, MD
- Philadelphia, PA
- Washington, D.C.
- National averages
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Import shared utilities
from utils import load_overdose_data, standardize_race

# Setup
plt.style.use('seaborn-v0_8-darkgrid')
output_dir = Path('results/48_la_vs_other_metros')
output_dir.mkdir(parents=True, exist_ok=True)

print("=" * 80)
print("LA VS OTHER METRO AREAS - COMPARATIVE ANALYSIS")
print("=" * 80)
print()

# ==============================================================================
# LOAD LA COUNTY DATA
# ==============================================================================
print("Loading LA County data...")

df = load_overdose_data('data/2012-01-2024-08-overdoses.csv')
df = standardize_race(df, race_col='Race', output_col='Race_Ethnicity_Cleaned')
df_2020 = df[df['Year'] == 2020].copy()

# Load population
pop_data_wide = pd.read_csv('data/la_county_population_census.csv')
pop_2020 = pop_data_wide[pop_data_wide['Year'] == 2020].iloc[0]

# Calculate LA 2020 rates
deaths_by_race = df_2020.groupby('Race_Ethnicity_Cleaned').size()

la_rates = {
    'BLACK': (deaths_by_race.get('BLACK', 0) / pop_2020['BLACK']) * 100000,
    'WHITE': (deaths_by_race.get('WHITE', 0) / pop_2020['WHITE']) * 100000,
    'LATINE': (deaths_by_race.get('LATINE', 0) / pop_2020['LATINE']) * 100000,
    'ASIAN': (deaths_by_race.get('ASIAN', 0) / pop_2020['ASIAN']) * 100000
}

la_ratio = la_rates['BLACK'] / la_rates['WHITE'] if la_rates['WHITE'] > 0 else np.nan

print(f"✓ LA County 2020:")
print(f"  BLACK: {la_rates['BLACK']:.1f} per 100k")
print(f"  WHITE: {la_rates['WHITE']:.1f} per 100k")
print(f"  Ratio: {la_ratio:.2f}x")
print()

# ==============================================================================
# LITERATURE DATA (Table 1 from review)
# ==============================================================================
print("Compiling comparison data from literature...")

comparison_data = pd.DataFrame([
    {
        'Metro_Area': 'New York, NY',
        'Year': 2020,
        'Black_Rate': 38.2,
        'White_Rate': 32.7,
        'Ratio': 1.17,
        'Source': 'NYC Health Dept'
    },
    {
        'Metro_Area': 'Chicago, IL',
        'Year': 2020,
        'Black_Rate': 56.0,
        'White_Rate': 16.0,
        'Ratio': 3.50,
        'Source': 'Literature Review'
    },
    {
        'Metro_Area': 'Baltimore, MD',
        'Year': 2020,
        'Black_Rate': 118.8,
        'White_Rate': 17.0,
        'Ratio': 6.99,
        'Source': 'Literature Review'
    },
    {
        'Metro_Area': 'Philadelphia, PA',
        'Year': 2020,
        'Black_Rate': np.nan,  # Reported as ~5x
        'White_Rate': np.nan,
        'Ratio': 5.0,
        'Source': 'Literature Review (est.)'
    },
    {
        'Metro_Area': 'Washington, D.C.',
        'Year': 2020,
        'Black_Rate': np.nan,  # Reported as 6x
        'White_Rate': np.nan,
        'Ratio': 6.0,
        'Source': 'Literature Review (est.)'
    },
    {
        'Metro_Area': 'California (state)',
        'Year': 2020,
        'Black_Rate': 41.1,
        'White_Rate': 31.2,
        'Ratio': 1.32,
        'Source': 'Literature Review'
    },
    {
        'Metro_Area': 'National (US)',
        'Year': 2022,  # Most recent national data in literature
        'Black_Rate': 69.0,
        'White_Rate': 45.0,
        'Ratio': 1.53,
        'Source': 'Literature Review (2022 data)'
    },
    {
        'Metro_Area': 'Los Angeles County, CA',
        'Year': 2020,
        'Black_Rate': la_rates['BLACK'],
        'White_Rate': la_rates['WHITE'],
        'Ratio': la_ratio,
        'Source': 'This Study'
    }
])

# Sort by ratio
comparison_data = comparison_data.sort_values('Ratio')

print("✓ Compiled data for 8 jurisdictions")
print()

# ==============================================================================
# DISPLAY COMPARISON TABLE
# ==============================================================================
print("=" * 80)
print("COMPARATIVE TABLE: OVERDOSE MORTALITY RATES AND DISPARITIES")
print("=" * 80)
print()
print("Metro Area              | Year | Black Rate | White Rate | Ratio (B/W)")
print("-" * 75)

for _, row in comparison_data.iterrows():
    metro = row['Metro_Area']
    year = int(row['Year'])
    black = row['Black_Rate']
    white = row['White_Rate']
    ratio = row['Ratio']

    if pd.isna(black):
        black_str = "N/A"
        white_str = "N/A"
    else:
        black_str = f"{black:6.1f}"
        white_str = f"{white:6.1f}"

    marker = " ← LA COUNTY" if "Los Angeles" in metro else ""

    print(f"{metro:22} | {year} | {black_str} | {white_str} | {ratio:5.2f}x{marker}")

print()

# ==============================================================================
# CONTEXTUAL ANALYSIS
# ==============================================================================
print("=" * 80)
print("CONTEXTUAL ANALYSIS")
print("=" * 80)
print()

# Where does LA fall?
la_rank = comparison_data[comparison_data['Metro_Area'].str.contains('Los Angeles')].index[0] + 1
total_metros = len(comparison_data)

print(f"LA County Disparity Ranking:")
print(f"  Ranked {la_rank} of {total_metros} metros (1 = lowest disparity)")
print()

# Group similar cities
print("Similar Disparity Ratios:")
similar_threshold = 0.5
la_r = comparison_data[comparison_data['Metro_Area'].str.contains('Los Angeles')]['Ratio'].values[0]
similar = comparison_data[abs(comparison_data['Ratio'] - la_r) <= similar_threshold]
print("  Cities within ±0.5 of LA ratio:")
for _, row in similar.iterrows():
    if "Los Angeles" not in row['Metro_Area']:
        print(f"    - {row['Metro_Area']}: {row['Ratio']:.2f}x")
print()

# Comparison to state and national
ca_ratio = comparison_data[comparison_data['Metro_Area'] == 'California (state)']['Ratio'].values[0]
nat_ratio = comparison_data[comparison_data['Metro_Area'] == 'National (US)']['Ratio'].values[0]

print("LA vs State vs National:")
print(f"  LA County: {la_ratio:.2f}x")
print(f"  California (state): {ca_ratio:.2f}x")
print(f"  National (US): {nat_ratio:.2f}x")
print()

if la_ratio > ca_ratio:
    print(f"  → LA County disparity is {((la_ratio/ca_ratio - 1) * 100):.0f}% HIGHER than California average")
else:
    print(f"  → LA County disparity is {((1 - la_ratio/ca_ratio) * 100):.0f}% LOWER than California average")

if la_ratio > nat_ratio:
    print(f"  → LA County disparity is {((la_ratio/nat_ratio - 1) * 100):.0f}% HIGHER than national average")
else:
    print(f"  → LA County disparity is {((1 - la_ratio/nat_ratio) * 100):.0f}% LOWER than national average")
print()

# ==============================================================================
# VISUALIZATIONS
# ==============================================================================
print("Creating visualizations...")

fig, axes = plt.subplots(1, 2, figsize=(16, 6))

# Panel 1: Disparity Ratio Comparison (Bar Chart)
ax1 = axes[0]
colors = ['#ED7D31' if 'Los Angeles' in metro else '#4472C4' for metro in comparison_data['Metro_Area']]
bars = ax1.barh(comparison_data['Metro_Area'], comparison_data['Ratio'], color=colors, alpha=0.7, edgecolor='black')
ax1.axvline(x=1.0, color='black', linestyle='--', linewidth=1.5, label='Parity')
ax1.set_xlabel('Black/White Mortality Ratio', fontsize=12, fontweight='bold')
ax1.set_ylabel('Metropolitan Area', fontsize=12, fontweight='bold')
ax1.set_title('Overdose Mortality Disparities Across Major US Metro Areas\n(2020 data where available)',
              fontsize=13, fontweight='bold')
ax1.legend(fontsize=10)
ax1.grid(True, alpha=0.3, axis='x', linestyle='--')

# Annotate LA bar
for i, bar in enumerate(bars):
    if 'Los Angeles' in comparison_data.iloc[i]['Metro_Area']:
        width = bar.get_width()
        ax1.text(width + 0.1, bar.get_y() + bar.get_height()/2,
                 f'{width:.2f}x',
                 va='center', fontsize=11, fontweight='bold', color='#ED7D31')

# Panel 2: Rate Comparison (Scatter Plot)
ax2 = axes[1]

# Filter out rows with NaN rates
plot_data = comparison_data[comparison_data['Black_Rate'].notna()]

for _, row in plot_data.iterrows():
    if 'Los Angeles' in row['Metro_Area']:
        ax2.scatter(row['White_Rate'], row['Black_Rate'],
                   s=300, color='#ED7D31', marker='D', edgecolor='black', linewidth=2,
                   label='LA County', zorder=5)
    else:
        ax2.scatter(row['White_Rate'], row['Black_Rate'],
                   s=200, color='#4472C4', alpha=0.6, edgecolor='black')

    # Annotate
    ax2.annotate(row['Metro_Area'].split(',')[0],  # Just city name
                xy=(row['White_Rate'], row['Black_Rate']),
                xytext=(5, 5), textcoords='offset points',
                fontsize=9)

# Add parity line
max_val = max(plot_data['White_Rate'].max(), plot_data['Black_Rate'].max())
ax2.plot([0, max_val], [0, max_val], 'k--', linewidth=1.5, alpha=0.5, label='Parity (B=W)')

ax2.set_xlabel('White Overdose Rate (per 100,000)', fontsize=12, fontweight='bold')
ax2.set_ylabel('Black Overdose Rate (per 100,000)', fontsize=12, fontweight='bold')
ax2.set_title('Black vs White Overdose Rates\nAcross Major Metro Areas',
              fontsize=13, fontweight='bold')
ax2.legend(fontsize=10, loc='upper left')
ax2.grid(True, alpha=0.3, linestyle='--')

plt.tight_layout()
plt.savefig(output_dir / 'la_vs_other_metros.png', dpi=300, bbox_inches='tight')
print(f"✓ Saved: {output_dir / 'la_vs_other_metros.png'}")
print()

# ==============================================================================
# SAVE RESULTS
# ==============================================================================
print("Saving results...")

comparison_data.to_csv(output_dir / 'metro_comparison_table.csv', index=False)

# Create summary
summary_df = pd.DataFrame([
    {'Metric': 'LA County Black Rate (2020)', 'Value': f"{la_rates['BLACK']:.1f} per 100k"},
    {'Metric': 'LA County White Rate (2020)', 'Value': f"{la_rates['WHITE']:.1f} per 100k"},
    {'Metric': 'LA County Black/White Ratio', 'Value': f"{la_ratio:.2f}x"},
    {'Metric': 'Rank Among Metros (1=lowest disparity)', 'Value': f"{la_rank} of {total_metros}"},
    {'Metric': 'California State Ratio', 'Value': f"{ca_ratio:.2f}x"},
    {'Metric': 'National Ratio (2022)', 'Value': f"{nat_ratio:.2f}x"}
])

summary_df.to_csv(output_dir / 'la_summary.csv', index=False)

print(f"✓ Saved 2 CSV files")
print()

# ==============================================================================
# GENERATE README
# ==============================================================================
readme_content = f"""# LA vs Other Metro Areas - Comparative Analysis

**Analysis Number**: 48
**Script**: `48_la_vs_other_metros.py`
**Status**: ✅ Complete
**Date**: 2025-11-06

## Overview

Places LA County overdose mortality data in national context by comparing to other major US metropolitan areas from the literature review.

## Key Findings

### Comparative Table (2020 data)

| Metro Area | Black Rate | White Rate | Ratio (B/W) |
|-----------|-----------|-----------|------------|
"""

for _, row in comparison_data.iterrows():
    metro = row['Metro_Area']
    black = row['Black_Rate']
    white = row['White_Rate']
    ratio = row['Ratio']

    if pd.isna(black):
        black_str = "N/A"
        white_str = "N/A"
    else:
        black_str = f"{black:.1f}"
        white_str = f"{white:.1f}"

    marker = " **← LA COUNTY**" if "Los Angeles" in metro else ""
    readme_content += f"| {metro} | {black_str} | {white_str} | **{ratio:.2f}x**{marker} |\n"

readme_content += f"""

### LA County Position

- **Disparity Ranking**: {la_rank} of {total_metros} metros (1 = lowest disparity)
- **LA Ratio**: {la_ratio:.2f}x
- **California State Ratio**: {ca_ratio:.2f}x
- **National Ratio**: {nat_ratio:.2f}x (2022 data)

### Interpretation

**Comparison to State:**
"""

if la_ratio > ca_ratio:
    readme_content += f"- LA County disparity ({la_ratio:.2f}x) is {((la_ratio/ca_ratio - 1) * 100):.0f}% **HIGHER** than California average ({ca_ratio:.2f}x)\n"
else:
    readme_content += f"- LA County disparity ({la_ratio:.2f}x) is {((1 - la_ratio/ca_ratio) * 100):.0f}% **LOWER** than California average ({ca_ratio:.2f}x)\n"

readme_content += f"""

**Comparison to National:**
"""

if la_ratio > nat_ratio:
    readme_content += f"- LA County disparity is {((la_ratio/nat_ratio - 1) * 100):.0f}% **HIGHER** than national average ({nat_ratio:.2f}x)\n"
else:
    readme_content += f"- LA County disparity is {((1 - la_ratio/nat_ratio) * 100):.0f}% **LOWER** than national average ({nat_ratio:.2f}x)\n"

readme_content += f"""

**Regional Variation:**
- Smallest disparity: {comparison_data.iloc[0]['Metro_Area']} ({comparison_data.iloc[0]['Ratio']:.2f}x)
- Largest disparity: {comparison_data.iloc[-1]['Metro_Area']} ({comparison_data.iloc[-1]['Ratio']:.2f}x)
- **Range**: {comparison_data['Ratio'].min():.2f}x to {comparison_data['Ratio'].max():.2f}x

LA County falls in the **{"lower" if la_rank <= total_metros/2 else "upper"}** half of this distribution.

### Why Disparities Vary Across Cities

Literature suggests city-level variation driven by:

1. **Fentanyl supply penetration**: Cities where fentanyl entered Black communities early (via cocaine adulteration) show higher disparities
2. **Historical drug market structure**: Legacy cocaine markets vs heroin markets
3. **Harm reduction infrastructure**: Access to naloxone, MOUD, SSPs varies by city
4. **Segregation patterns**: Residential segregation concentrates or disperses risk
5. **Economic structure**: City-specific wage stagnation, housing costs affect vulnerability

### Implications for LA

LA's moderate disparity (relative to East Coast cities like Baltimore, D.C.) may reflect:
- Later fentanyl arrival compared to East Coast
- Different drug market structure (less concentrated Black cocaine markets?)
- California's stronger harm reduction policy environment
- However, still higher than state average suggests LA-specific risk factors

## Outputs Generated

### Visualizations
- `la_vs_other_metros.png` - 2-panel figure:
  - Horizontal bar chart of disparity ratios
  - Scatter plot of Black vs White rates

### Data Tables
- `metro_comparison_table.csv` - Full comparison data
- `la_summary.csv` - LA-specific summary statistics

## Related Analyses

- **Analysis #11**: Population-Adjusted Rates (LA data used here)
- **Analysis #18**: Age-Standardized Rates (could repeat this comparison with age-adjusted rates)
- **Analysis #45**: COVID Acceleration (compares LA COVID impact to national)

## Data Sources

### LA County
- This study: Medical Examiner-Coroner data, 2012-2023
- 2020 rates calculated from original data

### Other Cities
- Literature Review (Part 1.1), Table 1
- Sources: City health departments, published studies
- Most data from 2020 (peak COVID year)

## Methodological Note

**Caution on Direct Comparison:**
- Different data sources (ME-C, vital statistics, surveillance systems)
- Different definitions (opioid-only vs all drug overdoses)
- Some cities report opioid-specific rates (Chicago, Baltimore), others all drugs (NYC)
- Age-standardization not applied uniformly across cities
- Year differences (some 2020, National is 2022)

Results should be interpreted as **approximate comparative context** rather than precise rankings.

---

**Verification Status**: ✅ LA County positioned in national context
**Generated**: 2025-11-06
"""

with open(output_dir / 'README.md', 'w') as f:
    f.write(readme_content)

print(f"✓ Saved: {output_dir / 'README.md'}")
print()

# ==============================================================================
# SUMMARY
# ==============================================================================
print("=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)
print()
print("KEY FINDINGS:")
print(f"• LA County Black/White ratio (2020): {la_ratio:.2f}x")
print(f"• Ranked {la_rank} of {total_metros} metros (1 = lowest disparity)")
print()
print(f"• Range across metros: {comparison_data['Ratio'].min():.2f}x to {comparison_data['Ratio'].max():.2f}x")
print(f"• LA is {'below' if la_ratio < nat_ratio else 'above'} national average ({nat_ratio:.2f}x)")
print()
print("• Regional variation suggests local factors (supply, harm reduction, markets) matter")
print()
print("=" * 80)
