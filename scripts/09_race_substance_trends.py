#!/usr/bin/env python
# coding: utf-8

"""
Race-Stratified Substance Trends Analysis
- Temporal trends in substance involvement by race/ethnicity
- Disparities in fentanyl and methamphetamine detection
- Age differences by substance and race
- Statistical testing for racial disparities
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

# Settings
sns.set_style("whitegrid")
os.makedirs("results/09_race_substance_trends", exist_ok=True)

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

    # Process Age
    if df['Age'].dtype == 'object':
        df['Age'] = df['Age'].str.extract(r"(\d+\.?\d*)")[0].astype(float)
    else:
        df['Age'] = pd.to_numeric(df['Age'], errors='coerce')

    # Process Race
    conditions = [
        df['Race'].isin(["CAUCASIAN", "WHITE", "White/Caucasian"]),
        df['Race'].isin(["LATINE", "HISPANIC/LATIN AMERICAN", "Hispanic/Latino"]) | df['Race'].str.contains("Hispanic", na=False),
        df['Race'].isin(["BLACK", "Black"]),
        df['Race'].isin(["ASIAN", "Asian", "CHINESE", "FILIPINO", "JAPANESE", "KOREAN", "VIETNAMESE"]),
    ]
    choices = ["WHITE", "LATINE", "BLACK", "ASIAN"]
    df['Race'] = np.select(conditions, choices, default="OTHER")

    # Focus on major racial/ethnic groups
    df_main = df[df['Race'].isin(['WHITE', 'LATINE', 'BLACK', 'ASIAN'])].copy()

    substance_cols = ['Heroin', 'Fentanyl', 'Prescription.opioids',
                      'Methamphetamine', 'Cocaine', 'Benzodiazepines', 'Alcohol', 'Others']

    # === 1. Substance involvement by race over time ===
    print("Analyzing substance trends by race...")

    race_substance_trends = []
    for year in sorted(df_main['Year'].unique()):
        year_data = df_main[df_main['Year'] == year]

        for race in ['WHITE', 'LATINE', 'BLACK', 'ASIAN']:
            race_data = year_data[year_data['Race'] == race]
            total = len(race_data)

            if total > 0:
                for substance in substance_cols:
                    count = race_data[substance].sum()
                    pct = (count / total * 100) if total > 0 else 0

                    race_substance_trends.append({
                        'Year': year,
                        'Race': race,
                        'Substance': substance,
                        'Count': count,
                        'Total': total,
                        'Percentage': pct
                    })

    trends_df = pd.DataFrame(race_substance_trends)
    trends_df.to_csv('results/09_race_substance_trends/race_substance_trends_annual.csv', index=False)

    # === 2. Plot fentanyl trends by race ===
    print("Creating fentanyl trends by race plot...")

    race_colors = {
        'WHITE': '#00468B',
        'LATINE': '#ED0000',
        'BLACK': '#42B540',
        'ASIAN': '#0099B4'
    }

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

    # Fentanyl
    fent_trends = trends_df[trends_df['Substance'] == 'Fentanyl']
    for race in ['WHITE', 'LATINE', 'BLACK', 'ASIAN']:
        data = fent_trends[fent_trends['Race'] == race]
        ax1.plot(data['Year'], data['Percentage'],
                marker='o', linewidth=2.5, label=race,
                color=race_colors.get(race, '#666666'))

    ax1.set_xlabel('Year', fontsize=12)
    ax1.set_ylabel('% of Deaths', fontsize=12)
    ax1.set_title('Fentanyl-Involved Deaths by Race/Ethnicity\nLos Angeles County 2012-2023',
                  fontsize=14, fontweight='bold')
    ax1.legend(fontsize=11)
    ax1.grid(True, alpha=0.3)

    # Methamphetamine
    meth_trends = trends_df[trends_df['Substance'] == 'Methamphetamine']
    for race in ['WHITE', 'LATINE', 'BLACK', 'ASIAN']:
        data = meth_trends[meth_trends['Race'] == race]
        ax2.plot(data['Year'], data['Percentage'],
                marker='o', linewidth=2.5, label=race,
                color=race_colors.get(race, '#666666'))

    ax2.set_xlabel('Year', fontsize=12)
    ax2.set_ylabel('% of Deaths', fontsize=12)
    ax2.set_title('Methamphetamine-Involved Deaths by Race/Ethnicity\nLos Angeles County 2012-2023',
                  fontsize=14, fontweight='bold')
    ax2.legend(fontsize=11)
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('results/09_race_substance_trends/fentanyl_meth_by_race.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Saved: fentanyl_meth_by_race.png")

    # === 3. Four-panel plot for key substances ===
    print("Creating multi-substance panel plot...")

    key_substances = ['Fentanyl', 'Methamphetamine', 'Heroin', 'Cocaine']
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    axes = axes.flatten()

    for idx, substance in enumerate(key_substances):
        sub_trends = trends_df[trends_df['Substance'] == substance]

        for race in ['WHITE', 'LATINE', 'BLACK', 'ASIAN']:
            data = sub_trends[sub_trends['Race'] == race]
            axes[idx].plot(data['Year'], data['Percentage'],
                          marker='o', linewidth=2, label=race,
                          color=race_colors.get(race, '#666666'))

        axes[idx].set_xlabel('Year', fontsize=11)
        axes[idx].set_ylabel('% of Deaths', fontsize=11)
        axes[idx].set_title(f'{substance}-Involved Deaths by Race/Ethnicity',
                           fontsize=12, fontweight='bold')
        axes[idx].legend(fontsize=9)
        axes[idx].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('results/09_race_substance_trends/key_substances_by_race.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Saved: key_substances_by_race.png")

    # === 4. Age by race by substance ===
    print("Analyzing age patterns by race and substance...")

    age_race_substance = []
    for substance in ['Fentanyl', 'Methamphetamine', 'Heroin', 'Cocaine']:
        sub_data = df_main[df_main[substance] == 1]

        for race in ['WHITE', 'LATINE', 'BLACK', 'ASIAN']:
            race_sub_data = sub_data[sub_data['Race'] == race]

            if len(race_sub_data) >= 5:  # Suppress small cells
                ages = race_sub_data['Age'].dropna()
                if len(ages) >= 5:
                    age_race_substance.append({
                        'Substance': substance,
                        'Race': race,
                        'n': len(ages),
                        'Median_Age': ages.median(),
                        'Mean_Age': ages.mean(),
                        'Q25': ages.quantile(0.25),
                        'Q75': ages.quantile(0.75)
                    })

    age_summary = pd.DataFrame(age_race_substance)
    age_summary.to_csv('results/09_race_substance_trends/age_by_race_substance.csv', index=False)

    # Create publication-ready table
    print("Creating publication-ready age summary table...")

    pub_table = []
    for substance in ['Fentanyl', 'Methamphetamine', 'Heroin', 'Cocaine']:
        sub_data = df_main[df_main[substance] == 1]

        for race in ['WHITE', 'LATINE', 'BLACK', 'ASIAN']:
            race_sub_data = sub_data[sub_data['Race'] == race]
            ages = race_sub_data['Age'].dropna()

            if len(ages) >= 5:
                pub_table.append({
                    'Substance': substance,
                    'Race/Ethnicity': race,
                    'N': len(ages),
                    'Median (IQR)': f"{ages.median():.0f} ({ages.quantile(0.25):.0f}-{ages.quantile(0.75):.0f})",
                    'Mean (SD)': f"{ages.mean():.1f} ({ages.std():.1f})",
                    'Median': ages.median(),  # For sorting
                    'Mean': ages.mean()  # For sorting
                })

    pub_table_df = pd.DataFrame(pub_table)

    # Create separate table for each substance
    for substance in ['Fentanyl', 'Methamphetamine', 'Heroin', 'Cocaine']:
        sub_table = pub_table_df[pub_table_df['Substance'] == substance].copy()
        sub_table = sub_table.sort_values('Median')  # Sort by median age
        sub_table = sub_table[['Race/Ethnicity', 'N', 'Median (IQR)', 'Mean (SD)']]

        # Save as CSV
        sub_table.to_csv(f'results/09_race_substance_trends/age_table_{substance.lower()}.csv', index=False)

        # Print formatted table
        print(f"\n{substance} Deaths - Age by Race/Ethnicity (2012-2023)")
        print("="*70)
        print(f"{'Race/Ethnicity':<20} {'N':<8} {'Median (IQR)':<20} {'Mean (SD)':<15}")
        print("-"*70)
        for _, row in sub_table.iterrows():
            print(f"{row['Race/Ethnicity']:<20} {row['N']:<8.0f} {row['Median (IQR)']:<20} {row['Mean (SD)']:<15}")

    # Create combined table (all substances)
    combined_table = pub_table_df.pivot_table(
        index='Race/Ethnicity',
        columns='Substance',
        values='Median (IQR)',
        aggfunc='first'
    )
    combined_table = combined_table[['Fentanyl', 'Methamphetamine', 'Heroin', 'Cocaine']]
    combined_table.to_csv('results/09_race_substance_trends/age_table_combined.csv')

    print("\n\nCombined Age Table - Median (IQR) by Race and Substance")
    print("="*90)
    print(combined_table.to_string())

    age_summary.to_csv('results/09_race_substance_trends/age_by_race_substance.csv', index=False)

    # Plot median ages
    fig, ax = plt.subplots(figsize=(12, 6))

    x = np.arange(len(key_substances))
    width = 0.2

    for idx, race in enumerate(['WHITE', 'LATINE', 'BLACK', 'ASIAN']):
        race_data = age_summary[age_summary['Race'] == race]
        median_ages = [race_data[race_data['Substance'] == s]['Median_Age'].values[0]
                      if len(race_data[race_data['Substance'] == s]) > 0 else np.nan
                      for s in key_substances]

        ax.bar(x + (idx - 1.5) * width, median_ages, width,
              label=race, color=race_colors.get(race, '#666666'), alpha=0.8)

    ax.set_xlabel('Substance', fontsize=12)
    ax.set_ylabel('Median Age (years)', fontsize=12)
    ax.set_title('Median Age at Death by Substance and Race/Ethnicity\nLos Angeles County 2012-2023',
                fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(key_substances)
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.savefig('results/09_race_substance_trends/median_age_by_race_substance.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Saved: median_age_by_race_substance.png")

    # === 5. Racial composition changes over time ===
    print("Analyzing racial composition changes...")

    composition_data = []
    for year in sorted(df_main['Year'].unique()):
        year_data = df_main[df_main['Year'] == year]
        total = len(year_data)

        for race in ['WHITE', 'LATINE', 'BLACK', 'ASIAN']:
            count = (year_data['Race'] == race).sum()
            pct = (count / total * 100) if total > 0 else 0

            composition_data.append({
                'Year': year,
                'Race': race,
                'Count': count,
                'Percentage': pct
            })

    composition_df = pd.DataFrame(composition_data)
    composition_df.to_csv('results/09_race_substance_trends/racial_composition_annual.csv', index=False)

    # Stacked area chart
    fig, ax = plt.subplots(figsize=(12, 6))

    pivot_data = composition_df.pivot(index='Year', columns='Race', values='Percentage')
    ax.stackplot(pivot_data.index,
                 pivot_data['WHITE'], pivot_data['LATINE'],
                 pivot_data['BLACK'], pivot_data['ASIAN'],
                 labels=['WHITE', 'LATINE', 'BLACK', 'ASIAN'],
                 colors=[race_colors[r] for r in ['WHITE', 'LATINE', 'BLACK', 'ASIAN']],
                 alpha=0.8)

    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('% of Total Deaths', fontsize=12)
    ax.set_title('Racial/Ethnic Composition of Substance-Involved Deaths Over Time\nLos Angeles County 2012-2023',
                fontsize=14, fontweight='bold')
    ax.legend(loc='upper left', fontsize=11)
    ax.grid(True, alpha=0.3, axis='y')
    ax.set_ylim(0, 100)

    plt.tight_layout()
    plt.savefig('results/09_race_substance_trends/racial_composition_stacked.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Saved: racial_composition_stacked.png")

    # === KEY FINDINGS ===
    print("\n" + "="*60)
    print("KEY FINDINGS:")
    print("="*60)

    # Compare 2012 vs 2023 fentanyl involvement
    print("\n1. Fentanyl involvement by race (2012 vs 2023):")
    for race in ['WHITE', 'LATINE', 'BLACK', 'ASIAN']:
        fent_2012 = fent_trends[(fent_trends['Race'] == race) & (fent_trends['Year'] == 2012)]
        fent_2023 = fent_trends[(fent_trends['Race'] == race) & (fent_trends['Year'] == 2023)]

        if len(fent_2012) > 0 and len(fent_2023) > 0:
            pct_2012 = fent_2012['Percentage'].values[0]
            pct_2023 = fent_2023['Percentage'].values[0]
            change = pct_2023 - pct_2012
            print(f"   {race}: {pct_2012:.1f}% → {pct_2023:.1f}% ({change:+.1f} pp)")

    # Compare 2012 vs 2023 meth involvement
    print("\n2. Methamphetamine involvement by race (2012 vs 2023):")
    for race in ['WHITE', 'LATINE', 'BLACK', 'ASIAN']:
        meth_2012 = meth_trends[(meth_trends['Race'] == race) & (meth_trends['Year'] == 2012)]
        meth_2023 = meth_trends[(meth_trends['Race'] == race) & (meth_trends['Year'] == 2023)]

        if len(meth_2012) > 0 and len(meth_2023) > 0:
            pct_2012 = meth_2012['Percentage'].values[0]
            pct_2023 = meth_2023['Percentage'].values[0]
            change = pct_2023 - pct_2012
            print(f"   {race}: {pct_2012:.1f}% → {pct_2023:.1f}% ({change:+.1f} pp)")

    # Median ages by substance and race (2023)
    print("\n3. Median age by substance and race (2012-2023 combined):")
    for substance in ['Fentanyl', 'Methamphetamine']:
        print(f"\n   {substance}:")
        sub_age = age_summary[age_summary['Substance'] == substance].sort_values('Median_Age')
        for _, row in sub_age.iterrows():
            if row['n'] >= 5:
                print(f"      {row['Race']}: {row['Median_Age']:.0f} years (n={row['n']:.0f})")

    # Racial composition shift
    print("\n4. Racial composition shift (2012 vs 2023):")
    comp_2012 = composition_df[composition_df['Year'] == 2012].set_index('Race')
    comp_2023 = composition_df[composition_df['Year'] == 2023].set_index('Race')

    for race in ['WHITE', 'LATINE', 'BLACK', 'ASIAN']:
        pct_2012 = comp_2012.loc[race, 'Percentage']
        pct_2023 = comp_2023.loc[race, 'Percentage']
        change = pct_2023 - pct_2012
        print(f"   {race}: {pct_2012:.1f}% → {pct_2023:.1f}% ({change:+.1f} pp)")

    print("\n" + "="*60)
    print("Analysis complete!")

if __name__ == "__main__":
    main()
