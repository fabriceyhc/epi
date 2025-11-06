#!/usr/bin/env python
# coding: utf-8

"""
Homelessness and Overdose Analysis
- Trends in overdoses among people experiencing homelessness
- Which substances are most associated with homelessness
- Geographic patterns of homeless overdoses
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Settings
sns.set_style("whitegrid")
os.makedirs("results/04_homelessness_analysis", exist_ok=True)

DATA_PATH = "/data2/fabricehc/epi/data/2012-01-2024-08-overdoses.csv"

def main():
    print("Loading data...")
    df = pd.read_csv(DATA_PATH, low_memory=False)

    # Process dates
    df['Date of Death'] = pd.to_datetime(df['DeathDate'], errors='coerce')
    if 'DateofDeath' in df.columns:
        df['Date of Death'] = df['Date of Death'].fillna(
            pd.to_datetime(df['DateofDeath'], errors='coerce')
        )

    df['Year'] = df['Date of Death'].dt.year
    df = df[df['Year'].between(2012, 2023)]

    substance_cols = ['Heroin', 'Fentanyl', 'Prescription.opioids',
                      'Methamphetamine', 'Cocaine', 'Benzodiazepines', 'Alcohol', 'Others']

    # Use ResidenceType as primary source (available for all years)
    print("Creating homelessness indicator from ResidenceType...")
    if 'ResidenceType' in df.columns:
        df['Homeless_from_ResidenceType'] = df['ResidenceType'].str.upper().str.contains(
            'HOMELESS|TRANSIENT|UNHOUSED|INDIGENT|SHELTER', na=False
        ).astype(int)
    else:
        df['Homeless_from_ResidenceType'] = 0

    # Overlay ExperiencingHomelessness data where available (2022-2023)
    if 'ExperiencingHomelessness' in df.columns:
        non_null_count = df['ExperiencingHomelessness'].notna().sum()
        print(f"Also using ExperiencingHomelessness column: {non_null_count} non-null values")
        df['Homeless_from_Column'] = df['ExperiencingHomelessness'].fillna(0).astype(int)
        # Use OR logic: if either source indicates homeless, mark as homeless
        df['Homeless'] = df['Homeless_from_ResidenceType'] | df['Homeless_from_Column']
    else:
        df['Homeless'] = df['Homeless_from_ResidenceType']

    total_homeless = df['Homeless'].sum()
    print(f"Total cases identified as experiencing homelessness: {total_homeless}")

    # Check data completeness by year
    residence_completeness = df.groupby('Year').apply(
        lambda x: x['ResidenceType'].notna().sum() / len(x) * 100
    )
    print(f"\nResidenceType data completeness by year:")
    print(residence_completeness.tail())

    # Filter out years with <10% data completeness for homelessness analysis
    incomplete_years = residence_completeness[residence_completeness < 10].index.tolist()
    if incomplete_years:
        print(f"\nWarning: Excluding years with incomplete data: {incomplete_years}")
        df_complete = df[~df['Year'].isin(incomplete_years)].copy()
    else:
        df_complete = df.copy()

    # === 1. Trends in homeless overdoses over time ===
    print("Analyzing homelessness trends...")

    homeless_annual = df_complete.groupby(['Year', 'Homeless']).size().reset_index(name='Deaths')
    annual_totals = df_complete.groupby('Year').size().reset_index(name='Total')
    homeless_annual = homeless_annual.merge(annual_totals, on='Year')
    homeless_annual['Percentage'] = (homeless_annual['Deaths'] / homeless_annual['Total']) * 100

    # Separate homeless and housed
    homeless_data = homeless_annual[homeless_annual['Homeless'] == 1]
    housed_data = homeless_annual[homeless_annual['Homeless'] == 0]

    homeless_annual.to_csv('results/04_homelessness_analysis/homeless_trends_annual.csv', index=False)

    # Plot
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # Absolute numbers
    ax1.plot(homeless_data['Year'], homeless_data['Deaths'],
             marker='o', linewidth=2, color='#ED0000', label='Experiencing Homelessness')
    ax1.plot(housed_data['Year'], housed_data['Deaths'],
             marker='s', linewidth=2, color='#00468B', label='Housed')
    ax1.set_xlabel('Year', fontsize=12)
    ax1.set_ylabel('Number of Deaths', fontsize=12)
    ax1.set_title('Overdose Deaths by Housing Status (Absolute)',
                  fontsize=13, fontweight='bold')
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)

    # Percentage of homeless deaths
    ax2.plot(homeless_data['Year'], homeless_data['Percentage'],
             marker='o', linewidth=3, color='#ED0000')
    ax2.set_xlabel('Year', fontsize=12)
    ax2.set_ylabel('% of All Overdose Deaths', fontsize=12)
    ax2.set_title('Proportion of Overdoses Among People Experiencing Homelessness',
                  fontsize=13, fontweight='bold')
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('results/04_homelessness_analysis/homeless_trends.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Saved: homeless_trends.png")

    # === 2. Substances by homelessness status ===
    print("Analyzing substance patterns by housing status...")

    substance_homeless = []
    for substance in substance_cols:
        for homeless_status in [0, 1]:
            status_data = df_complete[df_complete['Homeless'] == homeless_status]
            total = len(status_data)
            count = status_data[substance].sum()
            pct = (count / total * 100) if total > 0 else 0

            substance_homeless.append({
                'Substance': substance,
                'Housing_Status': 'Homeless' if homeless_status == 1 else 'Housed',
                'Count': count,
                'Total': total,
                'Percentage': pct
            })

    substance_homeless_df = pd.DataFrame(substance_homeless)
    substance_homeless_df.to_csv('results/04_homelessness_analysis/substances_by_housing_status.csv', index=False)

    # Plot comparison
    fig, ax = plt.subplots(figsize=(12, 6))

    x = np.arange(len(substance_cols))
    width = 0.35

    homeless_vals = substance_homeless_df[substance_homeless_df['Housing_Status'] == 'Homeless']['Percentage'].values
    housed_vals = substance_homeless_df[substance_homeless_df['Housing_Status'] == 'Housed']['Percentage'].values

    ax.bar(x - width/2, homeless_vals, width, label='Experiencing Homelessness', color='#ED0000', alpha=0.8)
    ax.bar(x + width/2, housed_vals, width, label='Housed', color='#00468B', alpha=0.8)

    ax.set_xlabel('Substance', fontsize=12)
    ax.set_ylabel('% of Group Deaths', fontsize=12)
    ax.set_title('Substance Involvement by Housing Status\nLos Angeles County 2012-2023',
                 fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(substance_cols, rotation=45, ha='right')
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.savefig('results/04_homelessness_analysis/substances_by_housing.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Saved: substances_by_housing.png")

    # === 3. Trends in specific substances for homeless population ===
    print("Analyzing substance trends for homeless population...")

    homeless_substance_trends = []
    df_homeless = df_complete[df_complete['Homeless'] == 1]

    for year in sorted(df_homeless['Year'].unique()):
        year_data = df_homeless[df_homeless['Year'] == year]
        total = len(year_data)

        for substance in substance_cols:
            count = year_data[substance].sum()
            pct = (count / total * 100) if total > 0 else 0

            homeless_substance_trends.append({
                'Year': year,
                'Substance': substance,
                'Count': count,
                'Percentage': pct
            })

    homeless_trends_df = pd.DataFrame(homeless_substance_trends)
    homeless_trends_df.to_csv('results/04_homelessness_analysis/homeless_substance_trends.csv', index=False)

    # Plot
    colors = {
        'Fentanyl': '#ED0000',
        'Heroin': '#00468B',
        'Methamphetamine': '#42B540',
        'Cocaine': '#0099B4',
        'Prescription.opioids': '#925E9F',
        'Benzodiazepines': '#FDAF91',
        'Alcohol': '#FF8C00',
        'Others': '#808080'
    }

    fig, ax = plt.subplots(figsize=(12, 6))

    for substance in substance_cols:
        data = homeless_trends_df[homeless_trends_df['Substance'] == substance]
        ax.plot(data['Year'], data['Percentage'],
                marker='o', linewidth=2, label=substance,
                color=colors.get(substance, '#666666'))

    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('% of Homeless Overdose Deaths', fontsize=12)
    ax.set_title('Substance Trends in Overdoses Among People Experiencing Homelessness\nLos Angeles County 2012-2023',
                 fontsize=14, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('results/04_homelessness_analysis/homeless_substance_trends.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Saved: homeless_substance_trends.png")

    # === 4. Demographics of homeless overdoses ===
    print("Analyzing demographics of homeless overdoses...")

    # Age comparison
    age_comparison = df_complete.groupby('Homeless')['Age'].agg(['mean', 'median', 'std']).reset_index()
    age_comparison['Housing_Status'] = age_comparison['Homeless'].map({0: 'Housed', 1: 'Homeless'})

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # Age distribution
    df_clean_age = df_complete[df_complete['Age'].notna()]
    homeless_ages = df_clean_age[df_clean_age['Homeless'] == 1]['Age']
    housed_ages = df_clean_age[df_clean_age['Homeless'] == 0]['Age']

    ax1.hist(homeless_ages, bins=30, alpha=0.7, label='Homeless', color='#ED0000', density=True)
    ax1.hist(housed_ages, bins=30, alpha=0.7, label='Housed', color='#00468B', density=True)
    ax1.set_xlabel('Age (years)', fontsize=12)
    ax1.set_ylabel('Density', fontsize=12)
    ax1.set_title('Age Distribution by Housing Status', fontsize=13, fontweight='bold')
    ax1.legend(fontsize=11)
    ax1.grid(True, alpha=0.3)

    # Mean age comparison
    ax2.bar(['Housed', 'Experiencing\nHomelessness'],
            [age_comparison[age_comparison['Homeless'] == 0]['mean'].values[0],
             age_comparison[age_comparison['Homeless'] == 1]['mean'].values[0]],
            color=['#00468B', '#ED0000'], alpha=0.8)
    ax2.set_ylabel('Mean Age (years)', fontsize=12)
    ax2.set_title('Mean Age of Overdose Victims', fontsize=13, fontweight='bold')
    ax2.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.savefig('results/04_homelessness_analysis/homeless_demographics_age.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Saved: homeless_demographics_age.png")

    # === 5. Geographic analysis (if location data available) ===
    print("Analyzing geographic patterns...")

    if 'lat' in df_complete.columns and 'lon' in df_complete.columns:
        df_geo = df_complete[(df_complete['lat'].notna()) & (df_complete['lon'].notna())].copy()

        # Filter to LA County bounds (approximate)
        df_geo = df_geo[
            (df_geo['lat'].between(33.7, 34.8)) &
            (df_geo['lon'].between(-118.7, -117.6))
        ]

        if len(df_geo) > 0:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

            # Homeless overdoses
            homeless_geo = df_geo[df_geo['Homeless'] == 1]
            ax1.scatter(homeless_geo['lon'], homeless_geo['lat'],
                       alpha=0.3, s=1, color='#ED0000')
            ax1.set_xlabel('Longitude', fontsize=11)
            ax1.set_ylabel('Latitude', fontsize=11)
            ax1.set_title('Overdoses Among People Experiencing Homelessness\n(Heat Map)',
                         fontsize=12, fontweight='bold')
            ax1.set_aspect('equal')

            # Housed overdoses
            housed_geo = df_geo[df_geo['Homeless'] == 0]
            ax2.scatter(housed_geo['lon'], housed_geo['lat'],
                       alpha=0.3, s=1, color='#00468B')
            ax2.set_xlabel('Longitude', fontsize=11)
            ax2.set_ylabel('Latitude', fontsize=11)
            ax2.set_title('Overdoses Among Housed Individuals\n(Heat Map)',
                         fontsize=12, fontweight='bold')
            ax2.set_aspect('equal')

            plt.tight_layout()
            plt.savefig('results/04_homelessness_analysis/homeless_geographic_distribution.png', dpi=300, bbox_inches='tight')
            plt.close()
            print("Saved: homeless_geographic_distribution.png")

    # Print key findings
    print("\n" + "="*60)
    print("KEY FINDINGS:")
    print("="*60)

    total_homeless = df_complete['Homeless'].sum()
    total_deaths = len(df_complete)
    homeless_pct = (total_homeless / total_deaths) * 100

    years_analyzed = f"{df_complete['Year'].min():.0f}-{df_complete['Year'].max():.0f}"
    if incomplete_years:
        print(f"\nNote: {incomplete_years} excluded due to incomplete ResidenceType data (<10% populated)")

    print(f"\n1. Overall statistics ({years_analyzed}):")
    print(f"   Total overdoses: {total_deaths:,}")
    print(f"   Overdoses among homeless: {total_homeless:,} ({homeless_pct:.1f}%)")

    if len(homeless_data) > 0:
        first_year = homeless_data.iloc[0]
        last_year = homeless_data.iloc[-1]
        print(f"\n2. Trend in homeless overdoses:")
        print(f"   {first_year['Year']:.0f}: {first_year['Deaths']:.0f} ({first_year['Percentage']:.1f}%)")
        print(f"   {last_year['Year']:.0f}: {last_year['Deaths']:.0f} ({last_year['Percentage']:.1f}%)")

    print(f"\n3. Most common substances in homeless overdoses:")
    homeless_sub = substance_homeless_df[substance_homeless_df['Housing_Status'] == 'Homeless'].sort_values('Percentage', ascending=False)
    for _, row in homeless_sub.head(3).iterrows():
        print(f"   {row['Substance']}: {row['Percentage']:.1f}%")

    print(f"\n4. Age comparison:")
    for _, row in age_comparison.iterrows():
        print(f"   {row['Housing_Status']}: {row['mean']:.1f} years (±{row['std']:.1f})")

    print("\n" + "="*60)
    print("Analysis complete!")

if __name__ == "__main__":
    main()
