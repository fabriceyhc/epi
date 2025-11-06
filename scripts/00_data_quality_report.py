#!/usr/bin/env python
# coding: utf-8

"""
Data Quality and Sample Derivation Report
- Documents sample selection process
- Reports data completeness by year
- Identifies exclusions and missing data
- Creates CONSORT-style flow diagram data
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Settings
sns.set_style("whitegrid")
os.makedirs("results/data_quality", exist_ok=True)

DATA_PATH = "/data2/fabricehc/epi/data/2012-01-2024-08-overdoses.csv"

def main():
    print("Loading raw data...")
    df_raw = pd.read_csv(DATA_PATH, low_memory=False)

    total_records = len(df_raw)
    print(f"Total records in raw data: {total_records:,}")

    # === Sample Derivation ===
    exclusions = []

    # Step 1: Date processing
    df = df_raw.copy()
    df['Date of Death'] = pd.to_datetime(df['DeathDate'], errors='coerce')
    if 'DateofDeath' in df.columns:
        df['Date of Death'] = df['Date of Death'].fillna(
            pd.to_datetime(df['DateofDeath'], errors='coerce')
        )

    missing_dates = df['Date of Death'].isna().sum()
    exclusions.append({
        'Step': 'Missing death date',
        'Excluded': missing_dates,
        'Remaining': total_records - missing_dates
    })

    df = df[df['Date of Death'].notna()].copy()

    # Step 2: Year extraction and filtering
    df['Year'] = df['Date of Death'].dt.year

    # Count by year before filtering
    print("\nRecords by year (before filtering):")
    year_counts = df.groupby('Year').size().sort_index()
    for year, count in year_counts.items():
        print(f"  {year}: {count:,}")

    # Filter to study period (2012-2023)
    outside_range = len(df[~df['Year'].between(2012, 2023)])
    exclusions.append({
        'Step': 'Outside study period (2012-2023)',
        'Excluded': outside_range,
        'Remaining': len(df[df['Year'].between(2012, 2023)])
    })

    df = df[df['Year'].between(2012, 2023)].copy()

    # Final analytical sample
    final_n = len(df)

    # Create exclusion table
    exclusion_df = pd.DataFrame(exclusions)
    exclusion_df.to_csv('results/data_quality/sample_derivation.csv', index=False)

    print("\n" + "="*60)
    print("SAMPLE DERIVATION")
    print("="*60)
    print(f"Total raw records: {total_records:,}")
    for _, row in exclusion_df.iterrows():
        print(f"  - {row['Step']}: excluded {row['Excluded']:,} (remaining: {row['Remaining']:,})")
    print(f"\nFinal analytical sample: {final_n:,}")

    # === Data Completeness Analysis ===
    print("\n" + "="*60)
    print("DATA COMPLETENESS BY YEAR")
    print("="*60)

    # Key variables
    key_vars = {
        'Age': 'Age',
        'Gender': 'Gender',
        'Race': 'Race',
        'ResidenceType': 'Homelessness indicator',
        'ZIPCODE': 'ZIP code',
        'lat': 'Latitude',
        'lon': 'Longitude'
    }

    completeness_data = []
    for year in sorted(df['Year'].unique()):
        year_data = df[df['Year'] == year]
        total = len(year_data)

        row = {'Year': year, 'Total_Deaths': total}
        for var, label in key_vars.items():
            if var in df.columns:
                complete = year_data[var].notna().sum()
                pct = (complete / total * 100) if total > 0 else 0
                row[f'{var}_n'] = complete
                row[f'{var}_pct'] = pct

        completeness_data.append(row)

    completeness_df = pd.DataFrame(completeness_data)
    completeness_df.to_csv('results/data_quality/completeness_by_year.csv', index=False)

    # Print completeness summary
    print("\nCompleteness of key variables by year (%):")
    print(f"{'Year':<6} {'Age':<8} {'Gender':<8} {'Race':<8} {'ResType':<8} {'ZIP':<8} {'Coords':<8}")
    print("-" * 60)
    for _, row in completeness_df.iterrows():
        year = int(row['Year'])
        age_pct = row.get('Age_pct', 0)
        gender_pct = row.get('Gender_pct', 0)
        race_pct = row.get('Race_pct', 0)
        res_pct = row.get('ResidenceType_pct', 0)
        zip_pct = row.get('ZIPCODE_pct', 0)
        lat_pct = row.get('lat_pct', 0)

        print(f"{year:<6} {age_pct:>6.1f}% {gender_pct:>6.1f}% {race_pct:>6.1f}% "
              f"{res_pct:>6.1f}% {zip_pct:>6.1f}% {lat_pct:>6.1f}%")

    # === Substance Field Completeness ===
    print("\n" + "="*60)
    print("SUBSTANCE FIELD COMPLETENESS")
    print("="*60)

    substance_cols = ['Heroin', 'Fentanyl', 'Prescription.opioids',
                      'Methamphetamine', 'Cocaine', 'Benzodiazepines',
                      'Alcohol', 'Others']

    substance_completeness = []
    for year in sorted(df['Year'].unique()):
        year_data = df[df['Year'] == year]
        total = len(year_data)

        row = {'Year': year, 'Total': total}
        for substance in substance_cols:
            if substance in df.columns:
                complete = year_data[substance].notna().sum()
                positive = year_data[substance].sum()
                pct_complete = (complete / total * 100) if total > 0 else 0
                pct_positive = (positive / complete * 100) if complete > 0 else 0

                row[f'{substance}_complete_pct'] = pct_complete
                row[f'{substance}_positive_n'] = positive
                row[f'{substance}_positive_pct'] = pct_positive

        substance_completeness.append(row)

    substance_comp_df = pd.DataFrame(substance_completeness)
    substance_comp_df.to_csv('results/data_quality/substance_completeness.csv', index=False)

    # Plot completeness over time
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))

    # Key demographics completeness
    for var in ['Age', 'Gender', 'Race', 'ResidenceType']:
        if f'{var}_pct' in completeness_df.columns:
            ax1.plot(completeness_df['Year'], completeness_df[f'{var}_pct'],
                    marker='o', linewidth=2, label=key_vars[var])

    ax1.set_xlabel('Year', fontsize=12)
    ax1.set_ylabel('% Complete', fontsize=12)
    ax1.set_title('Data Completeness of Key Demographic Variables Over Time',
                  fontsize=14, fontweight='bold')
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim(0, 105)

    # Substance detection rates
    colors_sub = {
        'Fentanyl': '#ED0000',
        'Heroin': '#00468B',
        'Methamphetamine': '#42B540',
        'Cocaine': '#0099B4'
    }

    for substance in ['Fentanyl', 'Heroin', 'Methamphetamine', 'Cocaine']:
        if f'{substance}_positive_pct' in substance_comp_df.columns:
            ax2.plot(substance_comp_df['Year'],
                    substance_comp_df[f'{substance}_positive_pct'],
                    marker='o', linewidth=2, label=substance,
                    color=colors_sub.get(substance, '#666666'))

    ax2.set_xlabel('Year', fontsize=12)
    ax2.set_ylabel('% of Deaths with Substance Detected', fontsize=12)
    ax2.set_title('Substance Detection Rates Over Time',
                  fontsize=14, fontweight='bold')
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('results/data_quality/completeness_trends.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Saved: completeness_trends.png")

    # === Summary Statistics ===
    print("\n" + "="*60)
    print("ANALYTICAL SAMPLE CHARACTERISTICS")
    print("="*60)

    print(f"\nStudy period: 2012-2023")
    print(f"Total deaths: {final_n:,}")
    print(f"\nDeaths by year:")
    year_dist = df.groupby('Year').size()
    for year, count in year_dist.items():
        pct = (count / final_n * 100)
        print(f"  {year}: {count:,} ({pct:.1f}%)")

    # Demographic summary
    if 'Age' in df.columns:
        age_clean = df['Age'].dropna()
        print(f"\nAge: median {age_clean.median():.0f} (IQR: {age_clean.quantile(0.25):.0f}-{age_clean.quantile(0.75):.0f})")

    if 'Gender' in df.columns:
        print("\nGender distribution:")
        gender_dist = df['Gender'].value_counts()
        for gender, count in gender_dist.items():
            pct = (count / final_n * 100)
            print(f"  {gender}: {count:,} ({pct:.1f}%)")

    if 'Race' in df.columns:
        print("\nRace/ethnicity distribution:")
        race_dist = df['Race'].value_counts()
        for race, count in race_dist.items():
            pct = (count / final_n * 100)
            print(f"  {race}: {count:,} ({pct:.1f}%)")

    print("\n" + "="*60)
    print("Data quality report complete!")
    print("="*60)

if __name__ == "__main__":
    main()
