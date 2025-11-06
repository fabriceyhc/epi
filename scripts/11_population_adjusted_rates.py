#!/usr/bin/env python
# coding: utf-8

"""
Population-Adjusted Overdose Rates by Race/Ethnicity
- Gets LA County population estimates by race (Census/ACS data)
- Calculates overdose death rates per 100,000 population
- Determines if increases in overdose proportions exceed population growth
- Shows whether racial disparities are due to demographic shifts or true rate increases
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Settings
sns.set_style("whitegrid")
os.makedirs("results/11_population_adjusted_rates", exist_ok=True)

DATA_PATH = "/data2/fabricehc/epi/data/2012-01-2024-08-overdoses.csv"

# LA County population data by race/ethnicity (2012-2023)
# Source: U.S. Census Bureau, American Community Survey 1-Year Estimates + 2020 Census
# Table: B03002 (Hispanic or Latino Origin by Race)
# Geography: Los Angeles County, California
# Fetched via Census API on 2025-11-05

LA_COUNTY_POPULATION = {
    2012: {
        'WHITE': 2704343,
        'LATINE': 4802133,
        'BLACK': 799140,
        'ASIAN': 1366001,
        'TOTAL': 9962789
    },
    2013: {
        'WHITE': 2703681,
        'LATINE': 4834936,
        'BLACK': 801603,
        'ASIAN': 1392815,
        'TOTAL': 10017068
    },
    2014: {
        'WHITE': 2695087,
        'LATINE': 4897745,
        'BLACK': 802664,
        'ASIAN': 1431071,
        'TOTAL': 10116705
    },
    2015: {
        'WHITE': 2686804,
        'LATINE': 4926661,
        'BLACK': 812731,
        'ASIAN': 1455392,
        'TOTAL': 10170292
    },
    2016: {
        'WHITE': 2667102,
        'LATINE': 4918830,
        'BLACK': 793213,
        'ASIAN': 1456307,
        'TOTAL': 10137915
    },
    2017: {
        'WHITE': 2644767,
        'LATINE': 4939605,
        'BLACK': 794235,
        'ASIAN': 1482797,
        'TOTAL': 10163507
    },
    2018: {
        'WHITE': 2619709,
        'LATINE': 4915287,
        'BLACK': 783932,
        'ASIAN': 1473462,
        'TOTAL': 10105518
    },
    2019: {
        'WHITE': 2596980,
        'LATINE': 4881970,
        'BLACK': 777195,
        'ASIAN': 1456809,
        'TOTAL': 10039107
    },
    2020: {
        'WHITE': 2563609,
        'LATINE': 5209246,
        'BLACK': 760689,
        'ASIAN': 1474237,
        'TOTAL': 10014009
    },
    2021: {
        'WHITE': 2420466,
        'LATINE': 4824989,
        'BLACK': 722464,
        'ASIAN': 1434374,
        'TOTAL': 9829544
    },
    2022: {
        'WHITE': 2380266,
        'LATINE': 4766616,
        'BLACK': 712156,
        'ASIAN': 1432462,
        'TOTAL': 9721138
    },
    2023: {
        'WHITE': 2369899,
        'LATINE': 4695902,
        'BLACK': 709583,
        'ASIAN': 1454666,
        'TOTAL': 9663345
    }
}

def main():
    print("="*70)
    print("POPULATION-ADJUSTED OVERDOSE RATE ANALYSIS")
    print("="*70)
    print("\nUsing OFFICIAL Census Bureau population data")
    print("Source: U.S. Census Bureau API")
    print("  - American Community Survey 1-Year Estimates (2012-2019, 2021-2023)")
    print("  - 2020 Decennial Census")
    print("  - Table B03002: Hispanic or Latino Origin by Race")
    print("  - Geography: Los Angeles County, CA")
    print("="*70)

    # Load overdose data
    print("\nLoading overdose data...")
    df = pd.read_csv(DATA_PATH, low_memory=False)

    # Process dates
    df['Date of Death'] = pd.to_datetime(df['DeathDate'], errors='coerce')
    if 'DateofDeath' in df.columns:
        df['Date of Death'] = df['Date of Death'].fillna(
            pd.to_datetime(df['DateofDeath'], errors='coerce')
        )

    df['Year'] = df['Date of Death'].dt.year
    df = df[df['Year'].between(2012, 2023)]

    # Process Race
    conditions = [
        df['Race'].isin(["CAUCASIAN", "WHITE", "White/Caucasian"]),
        df['Race'].isin(["LATINE", "HISPANIC/LATIN AMERICAN", "Hispanic/Latino"]) | df['Race'].str.contains("Hispanic", na=False),
        df['Race'].isin(["BLACK", "Black"]),
        df['Race'].isin(["ASIAN", "Asian", "CHINESE", "FILIPINO", "JAPANESE", "KOREAN", "VIETNAMESE"]),
    ]
    choices = ["WHITE", "LATINE", "BLACK", "ASIAN"]
    df['Race'] = np.select(conditions, choices, default="OTHER")

    df_main = df[df['Race'].isin(['WHITE', 'LATINE', 'BLACK', 'ASIAN'])].copy()

    # === Calculate counts and proportions ===
    print("Calculating death counts by race and year...")

    race_year_counts = df_main.groupby(['Year', 'Race']).size().reset_index(name='Deaths')
    total_by_year = df_main.groupby('Year').size().reset_index(name='Total_Deaths')

    race_year_counts = race_year_counts.merge(total_by_year, on='Year')
    race_year_counts['Proportion_of_Deaths'] = (race_year_counts['Deaths'] /
                                                 race_year_counts['Total_Deaths'] * 100)

    # === Add population data and calculate rates ===
    print("Adding population data and calculating rates...")

    # Create population dataframe
    pop_data = []
    for year in range(2012, 2024):
        for race in ['WHITE', 'LATINE', 'BLACK', 'ASIAN']:
            pop_data.append({
                'Year': year,
                'Race': race,
                'Population': LA_COUNTY_POPULATION[year][race],
                'Total_Population': LA_COUNTY_POPULATION[year]['TOTAL']
            })

    pop_df = pd.DataFrame(pop_data)

    # Merge with death counts
    analysis_df = race_year_counts.merge(pop_df, on=['Year', 'Race'], how='left')

    # Calculate rates per 100,000
    analysis_df['Rate_per_100k'] = (analysis_df['Deaths'] /
                                     analysis_df['Population'] * 100000)

    # Calculate proportion of LA County population
    analysis_df['Proportion_of_Population'] = (analysis_df['Population'] /
                                                analysis_df['Total_Population'] * 100)

    # Calculate rate ratio (proportion of deaths / proportion of population)
    analysis_df['Disparity_Ratio'] = (analysis_df['Proportion_of_Deaths'] /
                                       analysis_df['Proportion_of_Population'])

    # Save results
    analysis_df.to_csv('results/11_population_adjusted_rates/race_rates_annual.csv', index=False)

    # === Summary statistics ===
    print("\n" + "="*70)
    print("POPULATION CHANGES (2012-2023)")
    print("="*70)

    for race in ['WHITE', 'LATINE', 'BLACK', 'ASIAN']:
        pop_2012 = LA_COUNTY_POPULATION[2012][race]
        pop_2023 = LA_COUNTY_POPULATION[2023][race]
        change = pop_2023 - pop_2012
        pct_change = (change / pop_2012 * 100)

        print(f"\n{race}:")
        print(f"  2012: {pop_2012:>10,} ({pop_2012/LA_COUNTY_POPULATION[2012]['TOTAL']*100:.1f}% of LA County)")
        print(f"  2023: {pop_2023:>10,} ({pop_2023/LA_COUNTY_POPULATION[2023]['TOTAL']*100:.1f}% of LA County)")
        print(f"  Change: {change:>10,} ({pct_change:+.1f}%)")

    print("\n" + "="*70)
    print("OVERDOSE DEATH COUNTS (2012 vs 2023)")
    print("="*70)

    for race in ['WHITE', 'LATINE', 'BLACK', 'ASIAN']:
        deaths_2012 = analysis_df[(analysis_df['Year'] == 2012) &
                                   (analysis_df['Race'] == race)]['Deaths'].values
        deaths_2023 = analysis_df[(analysis_df['Year'] == 2023) &
                                   (analysis_df['Race'] == race)]['Deaths'].values

        if len(deaths_2012) > 0 and len(deaths_2023) > 0:
            d_2012 = deaths_2012[0]
            d_2023 = deaths_2023[0]
            change = d_2023 - d_2012
            pct_change = (change / d_2012 * 100) if d_2012 > 0 else 0

            print(f"\n{race}:")
            print(f"  2012: {d_2012:>6} deaths")
            print(f"  2023: {d_2023:>6} deaths")
            print(f"  Change: {change:>6} ({pct_change:+.1f}%)")

    print("\n" + "="*70)
    print("OVERDOSE RATES PER 100,000 POPULATION (2012 vs 2023)")
    print("="*70)

    for race in ['WHITE', 'LATINE', 'BLACK', 'ASIAN']:
        rate_2012 = analysis_df[(analysis_df['Year'] == 2012) &
                                (analysis_df['Race'] == race)]['Rate_per_100k'].values
        rate_2023 = analysis_df[(analysis_df['Year'] == 2023) &
                                (analysis_df['Race'] == race)]['Rate_per_100k'].values

        if len(rate_2012) > 0 and len(rate_2023) > 0:
            r_2012 = rate_2012[0]
            r_2023 = rate_2023[0]
            fold_change = r_2023 / r_2012 if r_2012 > 0 else 0

            print(f"\n{race}:")
            print(f"  2012: {r_2012:>6.2f} per 100,000")
            print(f"  2023: {r_2023:>6.2f} per 100,000")
            print(f"  Fold change: {fold_change:.2f}x")

    print("\n" + "="*70)
    print("DISPARITY RATIOS (2023)")
    print("Ratio > 1.0 = Overrepresented in overdose deaths")
    print("Ratio < 1.0 = Underrepresented in overdose deaths")
    print("="*70)

    for race in ['WHITE', 'LATINE', 'BLACK', 'ASIAN']:
        data_2023 = analysis_df[(analysis_df['Year'] == 2023) &
                                (analysis_df['Race'] == race)]

        if len(data_2023) > 0:
            prop_deaths = data_2023['Proportion_of_Deaths'].values[0]
            prop_pop = data_2023['Proportion_of_Population'].values[0]
            ratio = data_2023['Disparity_Ratio'].values[0]

            print(f"\n{race}:")
            print(f"  % of overdose deaths: {prop_deaths:>6.2f}%")
            print(f"  % of LA County population: {prop_pop:>6.2f}%")
            print(f"  Disparity ratio: {ratio:>6.2f}")

    # === Create visualizations ===
    print("\n" + "="*70)
    print("Creating visualizations...")
    print("="*70)

    # Figure 1: Rates over time
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))

    race_colors = {
        'WHITE': '#00468B',
        'LATINE': '#ED0000',
        'BLACK': '#42B540',
        'ASIAN': '#0099B4'
    }

    # Panel A: Death rates per 100,000
    ax = axes[0, 0]
    for race in ['WHITE', 'LATINE', 'BLACK', 'ASIAN']:
        data = analysis_df[analysis_df['Race'] == race]
        ax.plot(data['Year'], data['Rate_per_100k'],
               marker='o', linewidth=2.5, label=race,
               color=race_colors[race])

    ax.set_xlabel('Year', fontsize=12, fontweight='bold')
    ax.set_ylabel('Deaths per 100,000 Population', fontsize=12, fontweight='bold')
    ax.set_title('A. Overdose Death Rates by Race/Ethnicity\n(Population-Adjusted)',
                fontsize=13, fontweight='bold')
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)

    # Panel B: Population proportions over time
    ax = axes[0, 1]
    for race in ['WHITE', 'LATINE', 'BLACK', 'ASIAN']:
        data = analysis_df[analysis_df['Race'] == race]
        ax.plot(data['Year'], data['Proportion_of_Population'],
               marker='o', linewidth=2.5, label=race,
               color=race_colors[race])

    ax.set_xlabel('Year', fontsize=12, fontweight='bold')
    ax.set_ylabel('% of LA County Population', fontsize=12, fontweight='bold')
    ax.set_title('B. Population Composition Over Time',
                fontsize=13, fontweight='bold')
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)

    # Panel C: Death proportions over time
    ax = axes[1, 0]
    for race in ['WHITE', 'LATINE', 'BLACK', 'ASIAN']:
        data = analysis_df[analysis_df['Race'] == race]
        ax.plot(data['Year'], data['Proportion_of_Deaths'],
               marker='o', linewidth=2.5, label=race,
               color=race_colors[race])

    ax.set_xlabel('Year', fontsize=12, fontweight='bold')
    ax.set_ylabel('% of Overdose Deaths', fontsize=12, fontweight='bold')
    ax.set_title('C. Proportion of Overdose Deaths Over Time',
                fontsize=13, fontweight='bold')
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)

    # Panel D: Disparity ratios over time
    ax = axes[1, 1]
    for race in ['WHITE', 'LATINE', 'BLACK', 'ASIAN']:
        data = analysis_df[analysis_df['Race'] == race]
        ax.plot(data['Year'], data['Disparity_Ratio'],
               marker='o', linewidth=2.5, label=race,
               color=race_colors[race])

    ax.axhline(y=1.0, color='black', linestyle='--', linewidth=1.5, alpha=0.7,
              label='Proportional representation')
    ax.set_xlabel('Year', fontsize=12, fontweight='bold')
    ax.set_ylabel('Disparity Ratio', fontsize=12, fontweight='bold')
    ax.set_title('D. Disparity Ratios Over Time\n(% of Deaths / % of Population)',
                fontsize=13, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('results/11_population_adjusted_rates/population_adjusted_rates.png',
               dpi=300, bbox_inches='tight')
    plt.close()
    print("Saved: population_adjusted_rates.png")

    # Figure 2: 2012 vs 2023 comparison
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    races = ['WHITE', 'LATINE', 'BLACK', 'ASIAN']
    x_pos = np.arange(len(races))

    # Rates comparison
    ax = axes[0]
    rates_2012 = [analysis_df[(analysis_df['Year'] == 2012) &
                              (analysis_df['Race'] == r)]['Rate_per_100k'].values[0]
                 for r in races]
    rates_2023 = [analysis_df[(analysis_df['Year'] == 2023) &
                              (analysis_df['Race'] == r)]['Rate_per_100k'].values[0]
                 for r in races]

    width = 0.35
    ax.bar(x_pos - width/2, rates_2012, width, label='2012', alpha=0.7, color='#4472C4')
    ax.bar(x_pos + width/2, rates_2023, width, label='2023', alpha=0.7, color='#ED7D31')

    ax.set_ylabel('Deaths per 100,000', fontsize=12, fontweight='bold')
    ax.set_title('Overdose Death Rates\n2012 vs 2023', fontsize=13, fontweight='bold')
    ax.set_xticks(x_pos)
    ax.set_xticklabels(races)
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3, axis='y')

    # Population proportion comparison
    ax = axes[1]
    pop_2012 = [LA_COUNTY_POPULATION[2012][r]/LA_COUNTY_POPULATION[2012]['TOTAL']*100
               for r in races]
    pop_2023 = [LA_COUNTY_POPULATION[2023][r]/LA_COUNTY_POPULATION[2023]['TOTAL']*100
               for r in races]

    ax.bar(x_pos - width/2, pop_2012, width, label='2012', alpha=0.7, color='#4472C4')
    ax.bar(x_pos + width/2, pop_2023, width, label='2023', alpha=0.7, color='#ED7D31')

    ax.set_ylabel('% of LA County Population', fontsize=12, fontweight='bold')
    ax.set_title('Population Composition\n2012 vs 2023', fontsize=13, fontweight='bold')
    ax.set_xticks(x_pos)
    ax.set_xticklabels(races)
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3, axis='y')

    # Disparity ratio comparison
    ax = axes[2]
    ratio_2012 = [analysis_df[(analysis_df['Year'] == 2012) &
                              (analysis_df['Race'] == r)]['Disparity_Ratio'].values[0]
                 for r in races]
    ratio_2023 = [analysis_df[(analysis_df['Year'] == 2023) &
                              (analysis_df['Race'] == r)]['Disparity_Ratio'].values[0]
                 for r in races]

    ax.bar(x_pos - width/2, ratio_2012, width, label='2012', alpha=0.7, color='#4472C4')
    ax.bar(x_pos + width/2, ratio_2023, width, label='2023', alpha=0.7, color='#ED7D31')
    ax.axhline(y=1.0, color='black', linestyle='--', linewidth=1.5, alpha=0.7)

    ax.set_ylabel('Disparity Ratio', fontsize=12, fontweight='bold')
    ax.set_title('Disparity Ratios\n2012 vs 2023', fontsize=13, fontweight='bold')
    ax.set_xticks(x_pos)
    ax.set_xticklabels(races)
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.savefig('results/11_population_adjusted_rates/disparity_comparison.png',
               dpi=300, bbox_inches='tight')
    plt.close()
    print("Saved: disparity_comparison.png")

    print("\n" + "="*70)
    print("ANALYSIS COMPLETE")
    print("="*70)
    print("\nThese results use OFFICIAL Census Bureau population data.")
    print("Data fetched via Census API on 2025-11-05")
    print("\nKey outputs saved to:")
    print("  - results/11_population_adjusted_rates/race_rates_annual.csv")
    print("  - results/11_population_adjusted_rates/population_adjusted_rates.png")
    print("  - results/11_population_adjusted_rates/disparity_comparison.png")
    print("="*70)

if __name__ == "__main__":
    main()
