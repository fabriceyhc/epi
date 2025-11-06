#!/usr/bin/env python3
"""
Analysis #19: Substance-Specific SES Patterns

Examines whether the relationship between SES and overdose deaths
varies by substance type (meth, fentanyl, heroin, cocaine, etc.).
"""

import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Import shared utilities
from utils import load_overdose_data, standardize_race, process_age, SUBSTANCE_COLS

# Setup
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("colorblind")
output_dir = Path('results/19_substance_specific_ses')
output_dir.mkdir(parents=True, exist_ok=True)

print("=" * 70)
print("SUBSTANCE-SPECIFIC SES PATTERNS ANALYSIS")
print("=" * 70)
print()
print("Question: Does the relationship between SES and overdose deaths")
print("          vary by substance type?")
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
print(f"✓ Loaded Census data for {len(census)} race-year combinations")
print()

# ============================================================================
# DEFINE SUBSTANCES TO ANALYZE
# ============================================================================
print("Identifying substance involvement...")

# Key substances to analyze
substances = {
    'Methamphetamine': 'Methamphetamine',
    'Fentanyl': 'Fentanyl',
    'Heroin': 'Heroin',
    'Cocaine': 'Cocaine',
    'Prescription opioids': 'Prescription.opioids'
}

# Calculate substance involvement by race and year
substance_data = []

for substance_name, substance_col in substances.items():
    if substance_col in df.columns:
        # Count deaths involving this substance by race and year
        substance_df = df[df[substance_col] == 1].groupby(['Year', 'Race_Ethnicity_Cleaned']).size().reset_index(name=f'{substance_name}_Deaths')

        # Also get total deaths for rate calculation
        total_df = df.groupby(['Year', 'Race_Ethnicity_Cleaned']).size().reset_index(name='Total_Deaths')

        # Merge
        merged = substance_df.merge(total_df, on=['Year', 'Race_Ethnicity_Cleaned'], how='right')
        merged[f'{substance_name}_Deaths'] = merged[f'{substance_name}_Deaths'].fillna(0)
        merged[f'{substance_name}_Pct'] = (merged[f'{substance_name}_Deaths'] / merged['Total_Deaths'] * 100).round(2)

        # Merge with Census data
        merged = merged.merge(census, left_on=['Year', 'Race_Ethnicity_Cleaned'], right_on=['Year', 'Race'], how='left')

        # Calculate rate per 100k
        merged[f'{substance_name}_Rate'] = (merged[f'{substance_name}_Deaths'] / merged['Population'] * 100000).round(2)

        # Add substance name
        merged['Substance'] = substance_name

        substance_data.append(merged[[
            'Year', 'Race_Ethnicity_Cleaned', 'Substance',
            f'{substance_name}_Deaths', f'{substance_name}_Pct', f'{substance_name}_Rate',
            'Poverty_Rate', 'Median_Income', 'Population'
        ]].rename(columns={
            f'{substance_name}_Deaths': 'Deaths',
            f'{substance_name}_Pct': 'Percentage_of_Total',
            f'{substance_name}_Rate': 'Rate_Per_100k'
        }))

# Combine all substance data
all_substances = pd.concat(substance_data, ignore_index=True)

print(f"✓ Analyzed {len(substances)} substances")
print(f"✓ Created {len(all_substances)} substance-race-year observations")
print()

# ============================================================================
# CALCULATE SES CORRELATIONS BY SUBSTANCE
# ============================================================================
print("=" * 70)
print("SES CORRELATIONS BY SUBSTANCE TYPE")
print("=" * 70)
print()

correlations = []

for substance_name in substances.keys():
    subset = all_substances[all_substances['Substance'] == substance_name].copy()

    # Remove missing data
    subset_clean = subset.dropna(subset=['Poverty_Rate', 'Median_Income', 'Rate_Per_100k'])

    if len(subset_clean) > 5:
        # Poverty correlation
        corr_pov, pval_pov = stats.pearsonr(subset_clean['Poverty_Rate'], subset_clean['Rate_Per_100k'])

        # Income correlation
        corr_inc, pval_inc = stats.pearsonr(subset_clean['Median_Income'], subset_clean['Rate_Per_100k'])

        print(f"{substance_name}:")
        print(f"  N = {len(subset_clean)} observations")
        print(f"  Poverty  ↔ Rate: r = {corr_pov:+.3f}, p = {pval_pov:.4f}")
        print(f"  Income   ↔ Rate: r = {corr_inc:+.3f}, p = {pval_inc:.4f}")
        print()

        correlations.append({
            'Substance': substance_name,
            'N': len(subset_clean),
            'Poverty_Corr': corr_pov,
            'Poverty_P': pval_pov,
            'Income_Corr': corr_inc,
            'Income_P': pval_inc
        })

corr_df = pd.DataFrame(correlations)

# ============================================================================
# COMPARE HIGH VS LOW POVERTY
# ============================================================================
print("=" * 70)
print("SUBSTANCE INVOLVEMENT: HIGH vs LOW POVERTY")
print("=" * 70)
print()

# Categorize poverty
all_substances['Poverty_Level'] = pd.cut(all_substances['Poverty_Rate'],
                                          bins=[0, 12, 18, 100],
                                          labels=['Low (<12%)', 'Medium (12-18%)', 'High (>18%)'])

poverty_comparison = []

for substance_name in substances.keys():
    subset = all_substances[all_substances['Substance'] == substance_name].copy()

    high_pov = subset[subset['Poverty_Level'] == 'High (>18%)']
    low_pov = subset[subset['Poverty_Level'] == 'Low (<12%)']

    if len(high_pov) > 0 and len(low_pov) > 0:
        high_rate = high_pov['Rate_Per_100k'].mean()
        low_rate = low_pov['Rate_Per_100k'].mean()
        ratio = high_rate / low_rate if low_rate > 0 else np.nan

        print(f"{substance_name}:")
        print(f"  High poverty rate: {high_rate:.1f} per 100k")
        print(f"  Low poverty rate:  {low_rate:.1f} per 100k")
        print(f"  Ratio (high/low):  {ratio:.2f}x")
        print()

        poverty_comparison.append({
            'Substance': substance_name,
            'High_Poverty_Rate': high_rate,
            'Low_Poverty_Rate': low_rate,
            'Ratio': ratio
        })

poverty_comp_df = pd.DataFrame(poverty_comparison)

# ============================================================================
# RACE-SPECIFIC SUBSTANCE PATTERNS
# ============================================================================
print("=" * 70)
print("SUBSTANCE USE PATTERNS BY RACE")
print("=" * 70)
print()

# Calculate percentage of deaths involving each substance by race
race_substance_pct = []

for race in ['WHITE', 'BLACK', 'LATINE', 'ASIAN']:
    race_subset = df[df['Race_Ethnicity_Cleaned'] == race]

    if len(race_subset) > 0:
        print(f"{race} (N = {len(race_subset):,} deaths):")

        for substance_name, substance_col in substances.items():
            if substance_col in df.columns:
                n_involved = (race_subset[substance_col] == 1).sum()
                pct = n_involved / len(race_subset) * 100

                print(f"  {substance_name}: {pct:.1f}% ({n_involved:,} deaths)")

                race_substance_pct.append({
                    'Race': race,
                    'Substance': substance_name,
                    'Percentage': pct,
                    'Deaths': n_involved
                })
        print()

race_subst_df = pd.DataFrame(race_substance_pct)

# ============================================================================
# VISUALIZATIONS
# ============================================================================
print("Creating visualizations...")

fig = plt.figure(figsize=(20, 12))
gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)

# Panel 1: Correlation strengths by substance
ax1 = fig.add_subplot(gs[0, 0])
x_pos = np.arange(len(corr_df))
colors = ['red' if p < 0.05 else 'lightcoral' for p in corr_df['Poverty_P']]
ax1.barh(x_pos, corr_df['Poverty_Corr'], color=colors, alpha=0.7)
ax1.set_yticks(x_pos)
ax1.set_yticklabels(corr_df['Substance'], fontsize=9)
ax1.axvline(0, color='black', linestyle='--', linewidth=1)
ax1.set_xlabel('Poverty-Rate Correlation (Pearson r)', fontsize=10)
ax1.set_title('Poverty Correlation by Substance\n(Red = p<0.05)', fontsize=11, fontweight='bold')
ax1.set_xlim(-0.5, 1.0)

# Panel 2: Income correlations
ax2 = fig.add_subplot(gs[0, 1])
colors = ['blue' if p < 0.05 else 'lightblue' for p in corr_df['Income_P']]
ax2.barh(x_pos, corr_df['Income_Corr'], color=colors, alpha=0.7)
ax2.set_yticks(x_pos)
ax2.set_yticklabels(corr_df['Substance'], fontsize=9)
ax2.axvline(0, color='black', linestyle='--', linewidth=1)
ax2.set_xlabel('Income-Rate Correlation (Pearson r)', fontsize=10)
ax2.set_title('Income Correlation by Substance\n(Blue = p<0.05)', fontsize=11, fontweight='bold')
ax2.set_xlim(-1.0, 0.5)

# Panel 3: High vs Low poverty ratios
ax3 = fig.add_subplot(gs[0, 2])
x_pos = np.arange(len(poverty_comp_df))
ax3.bar(x_pos, poverty_comp_df['Ratio'], color='darkred', alpha=0.7, edgecolor='black')
ax3.set_xticks(x_pos)
ax3.set_xticklabels(poverty_comp_df['Substance'], rotation=45, ha='right', fontsize=9)
ax3.axhline(1, color='black', linestyle='--', linewidth=1)
ax3.set_ylabel('Rate Ratio (High/Low Poverty)', fontsize=10)
ax3.set_title('Poverty Disparity by Substance\n(High vs Low Poverty Areas)', fontsize=11, fontweight='bold')
# Add values on bars
for i, row in poverty_comp_df.iterrows():
    ax3.text(i, row['Ratio'] + 0.1, f"{row['Ratio']:.2f}x", ha='center', fontsize=9, fontweight='bold')

# Panel 4-8: Scatterplots for each substance
for idx, substance_name in enumerate(substances.keys()):
    row = (idx + 3) // 3
    col = (idx + 3) % 3
    ax = fig.add_subplot(gs[row, col])

    subset = all_substances[all_substances['Substance'] == substance_name].dropna(subset=['Poverty_Rate', 'Rate_Per_100k'])

    if len(subset) > 0:
        ax.scatter(subset['Poverty_Rate'], subset['Rate_Per_100k'], alpha=0.6, s=30)

        # Add regression line
        if len(subset) > 2:
            z = np.polyfit(subset['Poverty_Rate'], subset['Rate_Per_100k'], 1)
            p = np.poly1d(z)
            x_line = np.linspace(subset['Poverty_Rate'].min(), subset['Poverty_Rate'].max(), 100)
            ax.plot(x_line, p(x_line), "r--", alpha=0.8, linewidth=2)

        corr_row = corr_df[corr_df['Substance'] == substance_name]
        if len(corr_row) > 0:
            r = corr_row['Poverty_Corr'].values[0]
            p_val = corr_row['Poverty_P'].values[0]
            ax.set_title(f'{substance_name}\nr = {r:+.3f}, p = {p_val:.4f}', fontsize=10, fontweight='bold')
        else:
            ax.set_title(substance_name, fontsize=10, fontweight='bold')

        ax.set_xlabel('Poverty Rate (%)', fontsize=9)
        ax.set_ylabel('Rate per 100,000', fontsize=9)
        ax.tick_params(labelsize=8)

# Panel 9: Substance use by race (heatmap)
ax9 = fig.add_subplot(gs[2, 2])
pivot = race_subst_df.pivot(index='Substance', columns='Race', values='Percentage')
sns.heatmap(pivot, annot=True, fmt='.1f', cmap='YlOrRd', ax=ax9, cbar_kws={'label': '% of Deaths'})
ax9.set_title('Substance Involvement by Race\n(% of Deaths)', fontsize=11, fontweight='bold')
ax9.set_xlabel('')
ax9.set_ylabel('')

plt.savefig(output_dir / 'substance_specific_ses_patterns.png', dpi=300, bbox_inches='tight')
print(f"✓ Saved: {output_dir / 'substance_specific_ses_patterns.png'}")
print()

# Save results
corr_df.to_csv(output_dir / 'substance_ses_correlations.csv', index=False)
poverty_comp_df.to_csv(output_dir / 'substance_poverty_comparison.csv', index=False)
race_subst_df.to_csv(output_dir / 'substance_by_race.csv', index=False)
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

# Find strongest and weakest poverty correlations
strongest = corr_df.loc[corr_df['Poverty_Corr'].abs().idxmax()]
weakest = corr_df.loc[corr_df['Poverty_Corr'].abs().idxmin()]

print(f"POVERTY CORRELATIONS:")
print(f"• Strongest: {strongest['Substance']} (r = {strongest['Poverty_Corr']:+.3f}, p = {strongest['Poverty_P']:.4f})")
print(f"• Weakest:   {weakest['Substance']} (r = {weakest['Poverty_Corr']:+.3f}, p = {weakest['Poverty_P']:.4f})")
print()

# Find highest poverty disparity
highest_ratio = poverty_comp_df.loc[poverty_comp_df['Ratio'].idxmax()]
print(f"POVERTY DISPARITIES:")
print(f"• Highest ratio: {highest_ratio['Substance']} ({highest_ratio['Ratio']:.2f}x higher in high-poverty areas)")
print()

# Most common substance by race
for race in ['WHITE', 'BLACK', 'LATINE']:
    race_top = race_subst_df[race_subst_df['Race'] == race].nlargest(1, 'Percentage')
    if len(race_top) > 0:
        print(f"• {race}: {race_top.iloc[0]['Substance']} most common ({race_top.iloc[0]['Percentage']:.1f}%)")

print()
print("=" * 70)
