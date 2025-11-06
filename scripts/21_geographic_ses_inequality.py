#!/usr/bin/env python3
"""
Analysis #21: Geographic SES Inequality (ZIP-level)

Examines within-county spatial variation in overdose rates and SES.
Maps hotspots and correlates ZIP-level poverty/income with overdose burden.
"""

import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import requests
import time

# Import shared utilities
from utils import load_overdose_data, standardize_race, process_age, RACE_COLORS

# Setup
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("colorblind")
output_dir = Path('results/21_geographic_ses_inequality')
output_dir.mkdir(parents=True, exist_ok=True)

print("=" * 70)
print("GEOGRAPHIC SES INEQUALITY ANALYSIS (ZIP-LEVEL)")
print("=" * 70)
print()
print("Examining spatial variation in overdose rates and SES")
print("within Los Angeles County")
print()

# ============================================================================
# LOAD AND PROCESS DATA
# ============================================================================
print("Loading overdose data...")
df = load_overdose_data('data/2012-01-2024-08-overdoses.csv')
df = standardize_race(df, race_col='Race', output_col='Race_Ethnicity_Cleaned')
df = process_age(df, age_col='Age')

# Filter to 2012-2023 (exclude partial 2024 data)
df = df[(df['Year'] >= 2012) & (df['Year'] <= 2023)].copy()

# Clean ZIP codes
df['ZIP'] = df['ZIPCODE'].astype(str).str.replace('.0', '', regex=False)
df['ZIP'] = df['ZIP'].str.strip()
df = df[df['ZIP'].str.match(r'^\d{5}$', na=False)].copy()

print(f"✓ Loaded {len(df):,} overdose deaths with valid ZIP codes")
print(f"  Unique ZIPs: {df['ZIP'].nunique()}")
print(f"  Years: {sorted(df['Year'].unique())}")
print()

# ============================================================================
# CALCULATE ZIP-LEVEL OVERDOSE RATES
# ============================================================================
print("Calculating ZIP-level overdose rates...")

# Count deaths by ZIP
zip_deaths = df.groupby('ZIP').size().reset_index(name='Total_Deaths')

# Calculate by race
zip_race_deaths = df.groupby(['ZIP', 'Race_Ethnicity_Cleaned']).size().reset_index(name='Deaths')

# Get meth involvement
zip_meth = df.groupby('ZIP')['Methamphetamine'].mean().reset_index()
zip_meth.columns = ['ZIP', 'Meth_Pct']
zip_meth['Meth_Pct'] *= 100

# Get homelessness
if 'ExperiencingHomelessness' in df.columns:
    df['Homeless'] = np.where(
        df['ExperiencingHomelessness'].astype(str).str.upper().isin(['TRUE', '1', 'YES']),
        1, 0
    )
    zip_homeless = df.groupby('ZIP')['Homeless'].mean().reset_index()
    zip_homeless.columns = ['ZIP', 'Homeless_Pct']
    zip_homeless['Homeless_Pct'] *= 100
else:
    zip_homeless = None

print(f"✓ Calculated rates for {len(zip_deaths)} ZIP codes")
print()

# ============================================================================
# FETCH CENSUS DATA BY ZIP CODE
# ============================================================================
print("Fetching Census SES data by ZIP code...")
print("(This may take a few minutes)")
print()

def fetch_census_zip_data(year=2021):
    """
    Fetch poverty, income, and population data by ZCTA
    Using ACS 5-Year estimates for better ZIP-level coverage
    """
    api_key = None  # Census API works without key but with rate limits
    base_url = "https://api.census.gov/data"

    # Use 5-year estimates for better coverage at ZIP level
    # 2021 5-year = 2017-2021 data
    api_url = f"{base_url}/2021/acs/acs5"

    # Tables:
    # B17001_002E = Income below poverty level
    # B17001_001E = Total for poverty calc
    # B19013_001E = Median household income
    # B01003_001E = Total population

    params = {
        'get': 'NAME,B17001_002E,B17001_001E,B19013_001E,B01003_001E',
        'for': 'zip code tabulation area:*',
    }

    if api_key:
        params['key'] = api_key

    try:
        response = requests.get(api_url, params=params, timeout=60)
        response.raise_for_status()
        data = response.json()

        # Convert to DataFrame
        df = pd.DataFrame(data[1:], columns=data[0])

        # Rename columns
        df.columns = ['Name', 'Poverty_Count', 'Poverty_Total',
                      'Median_Income', 'Population', 'ZCTA']

        # Convert to numeric
        numeric_cols = ['Poverty_Count', 'Poverty_Total', 'Median_Income', 'Population']
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        # Calculate poverty rate
        df['Poverty_Rate'] = (df['Poverty_Count'] / df['Poverty_Total'] * 100).round(2)

        # Filter to LA County ZIPs (90000-91XXX range, roughly)
        df['ZCTA'] = df['ZCTA'].astype(str)
        df = df[df['ZCTA'].str.match(r'^9[01]\d{3}$')].copy()

        print(f"✓ Fetched data for {len(df)} LA County ZIP codes")
        return df[['ZCTA', 'Population', 'Poverty_Rate', 'Median_Income']]

    except Exception as e:
        print(f"✗ Error fetching Census data: {e}")
        return None

# Fetch Census data
census_zip = fetch_census_zip_data()

if census_zip is None:
    print("Could not fetch Census data. Exiting.")
    exit(1)

print()

# ============================================================================
# MERGE OVERDOSE AND CENSUS DATA
# ============================================================================
print("Merging overdose and Census data...")

# Merge with overdose deaths
zip_data = zip_deaths.merge(census_zip, left_on='ZIP', right_on='ZCTA', how='inner')

# Calculate crude rates per 100k
zip_data['Rate_Per_100k'] = (zip_data['Total_Deaths'] / zip_data['Population'] * 100000).round(2)

# Merge meth data
zip_data = zip_data.merge(zip_meth, on='ZIP', how='left')

# Merge homelessness data
if zip_homeless is not None:
    zip_data = zip_data.merge(zip_homeless, on='ZIP', how='left')

print(f"✓ Merged data for {len(zip_data)} ZIP codes (before cleaning)")

# CLEAN DATA: Remove invalid entries
# Filter out ZIPs with very small populations (< 500) or missing data
initial_count = len(zip_data)

# Remove negative incomes (Census missing data code)
zip_data = zip_data[zip_data['Median_Income'] > 0].copy()

# Remove missing poverty rates
zip_data = zip_data[zip_data['Poverty_Rate'].notna()].copy()

# Remove very small population ZIPs (< 500 people)
zip_data = zip_data[zip_data['Population'] >= 500].copy()

# Remove infinite or extreme rates
zip_data = zip_data[np.isfinite(zip_data['Rate_Per_100k'])].copy()
zip_data = zip_data[zip_data['Rate_Per_100k'] < 10000].copy()  # Remove extreme outliers

cleaned_count = len(zip_data)
print(f"✓ After data cleaning: {cleaned_count} ZIP codes ({initial_count - cleaned_count} removed)")
print()

# Save merged data
zip_data.to_csv(output_dir / 'zip_level_overdoses_ses.csv', index=False)
print(f"✓ Saved: {output_dir / 'zip_level_overdoses_ses.csv'}")
print()

# ============================================================================
# SUMMARY STATISTICS
# ============================================================================
print("=" * 70)
print("ZIP-LEVEL SUMMARY STATISTICS")
print("=" * 70)
print()

print(f"Number of ZIP codes analyzed: {len(zip_data)}")
print()

print("Overdose rates per 100k:")
print(f"  Mean:   {zip_data['Rate_Per_100k'].mean():.1f}")
print(f"  Median: {zip_data['Rate_Per_100k'].median():.1f}")
print(f"  Range:  {zip_data['Rate_Per_100k'].min():.1f} - {zip_data['Rate_Per_100k'].max():.1f}")
print(f"  IQR:    {zip_data['Rate_Per_100k'].quantile(0.25):.1f} - {zip_data['Rate_Per_100k'].quantile(0.75):.1f}")
print()

print("Poverty rates (%):")
print(f"  Mean:   {zip_data['Poverty_Rate'].mean():.1f}%")
print(f"  Median: {zip_data['Poverty_Rate'].median():.1f}%")
print(f"  Range:  {zip_data['Poverty_Rate'].min():.1f}% - {zip_data['Poverty_Rate'].max():.1f}%")
print()

print("Median household income:")
print(f"  Mean:   ${zip_data['Median_Income'].mean():,.0f}")
print(f"  Median: ${zip_data['Median_Income'].median():,.0f}")
print(f"  Range:  ${zip_data['Median_Income'].min():,.0f} - ${zip_data['Median_Income'].max():,.0f}")
print()

# ============================================================================
# CALCULATE GEOGRAPHIC INEQUALITY
# ============================================================================
print("=" * 70)
print("GEOGRAPHIC INEQUALITY MEASURES")
print("=" * 70)
print()

# Compare high vs low poverty ZIPs
high_poverty_threshold = zip_data['Poverty_Rate'].quantile(0.75)
low_poverty_threshold = zip_data['Poverty_Rate'].quantile(0.25)

high_poverty = zip_data[zip_data['Poverty_Rate'] >= high_poverty_threshold]
low_poverty = zip_data[zip_data['Poverty_Rate'] <= low_poverty_threshold]

print(f"High poverty ZIPs (≥{high_poverty_threshold:.1f}% poverty):")
print(f"  N = {len(high_poverty)}")
print(f"  Mean overdose rate: {high_poverty['Rate_Per_100k'].mean():.1f} per 100k")
print()

print(f"Low poverty ZIPs (≤{low_poverty_threshold:.1f}% poverty):")
print(f"  N = {len(low_poverty)}")
print(f"  Mean overdose rate: {low_poverty['Rate_Per_100k'].mean():.1f} per 100k")
print()

rate_ratio = high_poverty['Rate_Per_100k'].mean() / low_poverty['Rate_Per_100k'].mean()
print(f"High-to-low poverty rate ratio: {rate_ratio:.2f}x")
print()

# Statistical test
t_stat, p_val = stats.ttest_ind(high_poverty['Rate_Per_100k'],
                                 low_poverty['Rate_Per_100k'])
print(f"t-test: t={t_stat:.2f}, p={p_val:.4f}")
print()

# ============================================================================
# CORRELATIONS
# ============================================================================
print("=" * 70)
print("CORRELATIONS: OVERDOSE RATE vs SES")
print("=" * 70)
print()

# Poverty correlation
corr_poverty, p_poverty = stats.pearsonr(zip_data['Poverty_Rate'],
                                         zip_data['Rate_Per_100k'])
print(f"Poverty Rate vs Overdose Rate:")
print(f"  r = {corr_poverty:+.3f}, p = {p_poverty:.4f}")
print()

# Income correlation
corr_income, p_income = stats.pearsonr(zip_data['Median_Income'],
                                       zip_data['Rate_Per_100k'])
print(f"Median Income vs Overdose Rate:")
print(f"  r = {corr_income:+.3f}, p = {p_income:.4f}")
print()

# Meth correlation
if 'Meth_Pct' in zip_data.columns:
    zip_meth_clean = zip_data.dropna(subset=['Meth_Pct', 'Poverty_Rate'])
    if len(zip_meth_clean) > 2:
        corr_meth, p_meth = stats.pearsonr(zip_meth_clean['Poverty_Rate'],
                                           zip_meth_clean['Meth_Pct'])
        print(f"Poverty Rate vs Methamphetamine %:")
        print(f"  r = {corr_meth:+.3f}, p = {p_meth:.4f}")
        print()

# ============================================================================
# IDENTIFY HOTSPOTS
# ============================================================================
print("=" * 70)
print("TOP 10 HIGHEST-RATE ZIP CODES")
print("=" * 70)
print()

top_10 = zip_data.nlargest(10, 'Rate_Per_100k')
for idx, row in top_10.iterrows():
    print(f"{row['ZIP']}: {row['Rate_Per_100k']:.1f} per 100k "
          f"(Poverty: {row['Poverty_Rate']:.1f}%, Income: ${row['Median_Income']:,.0f})")
print()

# ============================================================================
# VISUALIZATIONS
# ============================================================================
print("Creating visualizations...")

fig, axes = plt.subplots(2, 3, figsize=(18, 12))

# Panel 1: Distribution of ZIP-level rates
axes[0, 0].hist(zip_data['Rate_Per_100k'], bins=30, edgecolor='black', alpha=0.7)
axes[0, 0].axvline(zip_data['Rate_Per_100k'].mean(), color='red',
                    linestyle='--', label=f'Mean: {zip_data["Rate_Per_100k"].mean():.1f}')
axes[0, 0].axvline(zip_data['Rate_Per_100k'].median(), color='blue',
                    linestyle='--', label=f'Median: {zip_data["Rate_Per_100k"].median():.1f}')
axes[0, 0].set_xlabel('Overdose Rate per 100,000', fontsize=11)
axes[0, 0].set_ylabel('Number of ZIP Codes', fontsize=11)
axes[0, 0].set_title('Distribution of ZIP-Level Overdose Rates\n(2012-2023)',
                     fontsize=12, fontweight='bold')
axes[0, 0].legend()

# Panel 2: Poverty vs Overdose Rate
axes[0, 1].scatter(zip_data['Poverty_Rate'], zip_data['Rate_Per_100k'],
                   alpha=0.6, s=50)
# Add regression line
z = np.polyfit(zip_data['Poverty_Rate'], zip_data['Rate_Per_100k'], 1)
p = np.poly1d(z)
x_line = np.linspace(zip_data['Poverty_Rate'].min(), zip_data['Poverty_Rate'].max(), 100)
axes[0, 1].plot(x_line, p(x_line), "r--", alpha=0.8, linewidth=2)
axes[0, 1].set_xlabel('Poverty Rate (%)', fontsize=11)
axes[0, 1].set_ylabel('Overdose Rate per 100,000', fontsize=11)
axes[0, 1].set_title(f'Poverty vs Overdose Rate\nr = {corr_poverty:+.3f}, p = {p_poverty:.4f}',
                     fontsize=12, fontweight='bold')

# Panel 3: Income vs Overdose Rate
axes[0, 2].scatter(zip_data['Median_Income'], zip_data['Rate_Per_100k'],
                   alpha=0.6, s=50, color='green')
# Add regression line
z = np.polyfit(zip_data['Median_Income'], zip_data['Rate_Per_100k'], 1)
p = np.poly1d(z)
x_line = np.linspace(zip_data['Median_Income'].min(), zip_data['Median_Income'].max(), 100)
axes[0, 2].plot(x_line, p(x_line), "r--", alpha=0.8, linewidth=2)
axes[0, 2].set_xlabel('Median Household Income ($)', fontsize=11)
axes[0, 2].set_ylabel('Overdose Rate per 100,000', fontsize=11)
axes[0, 2].set_title(f'Income vs Overdose Rate\nr = {corr_income:+.3f}, p = {p_income:.4f}',
                     fontsize=12, fontweight='bold')
axes[0, 2].ticklabel_format(style='plain', axis='x')

# Panel 4: High vs Low Poverty comparison
poverty_comparison = pd.DataFrame({
    'Poverty Level': ['Low Poverty\n(Q1)', 'High Poverty\n(Q4)'],
    'Rate': [low_poverty['Rate_Per_100k'].mean(), high_poverty['Rate_Per_100k'].mean()],
    'SE': [low_poverty['Rate_Per_100k'].sem(), high_poverty['Rate_Per_100k'].sem()]
})
axes[1, 0].bar(poverty_comparison['Poverty Level'], poverty_comparison['Rate'],
               yerr=poverty_comparison['SE'], capsize=10,
               color=['lightblue', 'darkred'], edgecolor='black', alpha=0.7)
axes[1, 0].set_ylabel('Overdose Rate per 100,000', fontsize=11)
axes[1, 0].set_title(f'High vs Low Poverty ZIP Codes\nRate Ratio: {rate_ratio:.2f}x',
                     fontsize=12, fontweight='bold')
# Add values on bars
for i, row in poverty_comparison.iterrows():
    axes[1, 0].text(i, row['Rate'] + row['SE'] + 2, f"{row['Rate']:.1f}",
                    ha='center', fontsize=11, fontweight='bold')

# Panel 5: Top 10 highest-rate ZIPs
top_5 = zip_data.nlargest(5, 'Rate_Per_100k')
axes[1, 1].barh(range(len(top_5)), top_5['Rate_Per_100k'], color='darkred', alpha=0.7)
axes[1, 1].set_yticks(range(len(top_5)))
axes[1, 1].set_yticklabels([f"{row['ZIP']}\n({row['Poverty_Rate']:.0f}% pov)"
                             for _, row in top_5.iterrows()], fontsize=9)
axes[1, 1].set_xlabel('Overdose Rate per 100,000', fontsize=11)
axes[1, 1].set_title('Top 5 Highest-Rate ZIP Codes\n(with poverty %)',
                     fontsize=12, fontweight='bold')
axes[1, 1].invert_yaxis()
# Add values
for i, (_, row) in enumerate(top_5.iterrows()):
    axes[1, 1].text(row['Rate_Per_100k'] + 1, i, f"{row['Rate_Per_100k']:.1f}",
                    va='center', fontsize=10, fontweight='bold')

# Panel 6: Inequality summary text
axes[1, 2].axis('off')
summary_text = f"""
GEOGRAPHIC INEQUALITY SUMMARY

ZIP Codes Analyzed: {len(zip_data)}

OVERDOSE RATES:
• Mean: {zip_data['Rate_Per_100k'].mean():.1f} per 100k
• Range: {zip_data['Rate_Per_100k'].min():.1f} - {zip_data['Rate_Per_100k'].max():.1f}
• Ratio (max/min): {zip_data['Rate_Per_100k'].max() / zip_data['Rate_Per_100k'].min():.1f}x

SES CORRELATIONS:
• Poverty ↔ Overdose: r = {corr_poverty:+.3f} ***
• Income ↔ Overdose: r = {corr_income:+.3f} ***

HIGH vs LOW POVERTY:
• High poverty ZIPs: {high_poverty['Rate_Per_100k'].mean():.1f} per 100k
• Low poverty ZIPs: {low_poverty['Rate_Per_100k'].mean():.1f} per 100k
• Disparity ratio: {rate_ratio:.2f}x

INTERPRETATION:
{"Significant positive" if corr_poverty > 0.3 else "Weak"} correlation between
poverty and overdose rates at ZIP level.
High-poverty areas have {rate_ratio:.1f}x higher
rates than low-poverty areas.
"""
axes[1, 2].text(0.1, 0.9, summary_text, fontsize=10, verticalalignment='top',
                family='monospace', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

plt.tight_layout()
plt.savefig(output_dir / 'geographic_ses_inequality.png', dpi=300, bbox_inches='tight')
print(f"✓ Saved: {output_dir / 'geographic_ses_inequality.png'}")
print()

# ============================================================================
# SUMMARY
# ============================================================================
print("=" * 70)
print("ANALYSIS COMPLETE")
print("=" * 70)
print()
print("KEY FINDINGS:")
print(f"• {len(zip_data)} LA County ZIP codes analyzed")
print(f"• Overdose rates range from {zip_data['Rate_Per_100k'].min():.1f} to "
      f"{zip_data['Rate_Per_100k'].max():.1f} per 100k ({zip_data['Rate_Per_100k'].max() / zip_data['Rate_Per_100k'].min():.1f}x difference)")
print(f"• Poverty and overdose rates: r = {corr_poverty:+.3f} (p = {p_poverty:.4f})")
print(f"• High-poverty ZIPs have {rate_ratio:.2f}x higher rates than low-poverty ZIPs")
print(f"• Top 5 hotspot ZIPs account for {top_5['Total_Deaths'].sum() / zip_data['Total_Deaths'].sum() * 100:.1f}% "
      f"of deaths in {top_5['Population'].sum() / zip_data['Population'].sum() * 100:.1f}% of population")
print()
print("=" * 70)
