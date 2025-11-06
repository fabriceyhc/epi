#!/usr/bin/env python
# coding: utf-8

"""
Fentanyl Crisis Timeline Analysis
- Tracks the rise of fentanyl and decline of heroin over time
- Analyzes co-occurrence patterns of fentanyl with other substances
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from plotnine import (
    ggplot, aes, geom_line, geom_area, geom_point,
    scale_color_manual, scale_fill_manual,
    theme_minimal, theme, labs, element_text,
    facet_wrap, geom_col, position_dodge
)

# Settings
sns.set_style("whitegrid")
os.makedirs("results/01_fentanyl_timeline", exist_ok=True)

DATA_PATH = "/data2/fabricehc/epi/data/2012-01-2024-08-overdoses.csv"

# Colors
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
    df['Month'] = df['Date of Death'].dt.month
    df['YearMonth'] = df['Date of Death'].dt.to_period('M')

    # Filter to complete years (2012-2023) for fair comparison
    df = df[df['Year'].between(2012, 2023)]

    # === 1. Fentanyl vs Heroin Timeline ===
    print("Analyzing fentanyl vs heroin timeline...")

    # Annual counts
    annual_counts = df.groupby('Year')[['Fentanyl', 'Heroin']].sum().reset_index()
    annual_totals = df.groupby('Year').size().reset_index(name='Total')
    annual_counts = annual_counts.merge(annual_totals, on='Year')

    # Calculate proportions
    annual_counts['Fentanyl_pct'] = (annual_counts['Fentanyl'] / annual_counts['Total']) * 100
    annual_counts['Heroin_pct'] = (annual_counts['Heroin'] / annual_counts['Total']) * 100

    # Save data
    annual_counts.to_csv('results/01_fentanyl_timeline/fentanyl_heroin_annual.csv', index=False)

    # Plot 1: Absolute counts
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    ax1.plot(annual_counts['Year'], annual_counts['Fentanyl'],
             marker='o', linewidth=2, color=colors['Fentanyl'], label='Fentanyl')
    ax1.plot(annual_counts['Year'], annual_counts['Heroin'],
             marker='o', linewidth=2, color=colors['Heroin'], label='Heroin')
    ax1.set_xlabel('Year', fontsize=12)
    ax1.set_ylabel('Number of Deaths', fontsize=12)
    ax1.set_title('Fentanyl vs Heroin: Absolute Deaths Over Time', fontsize=14, fontweight='bold')
    ax1.legend(fontsize=11)
    ax1.grid(True, alpha=0.3)

    # Plot 2: Proportions
    ax2.plot(annual_counts['Year'], annual_counts['Fentanyl_pct'],
             marker='o', linewidth=2, color=colors['Fentanyl'], label='Fentanyl')
    ax2.plot(annual_counts['Year'], annual_counts['Heroin_pct'],
             marker='o', linewidth=2, color=colors['Heroin'], label='Heroin')
    ax2.set_xlabel('Year', fontsize=12)
    ax2.set_ylabel('% of All Overdose Deaths', fontsize=12)
    ax2.set_title('Fentanyl vs Heroin: Proportion of Deaths Over Time', fontsize=14, fontweight='bold')
    ax2.legend(fontsize=11)
    ax2.grid(True, alpha=0.3)
    ax2.set_ylim(0, 100)

    plt.tight_layout()
    plt.savefig('results/01_fentanyl_timeline/fentanyl_heroin_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Saved: fentanyl_heroin_comparison.png")

    # === 2. All Substances Timeline ===
    print("Analyzing all substances over time...")

    substance_cols = ['Fentanyl', 'Heroin', 'Methamphetamine', 'Cocaine',
                      'Prescription.opioids', 'Benzodiazepines', 'Alcohol', 'Others']

    # Annual proportions for all substances
    substance_annual = df.groupby('Year')[substance_cols].sum()
    substance_annual_pct = substance_annual.div(annual_totals.set_index('Year')['Total'], axis=0) * 100
    substance_annual_pct = substance_annual_pct.reset_index()

    # Melt for plotting
    substance_long = substance_annual_pct.melt(id_vars='Year',
                                                value_vars=substance_cols,
                                                var_name='Substance',
                                                value_name='Percentage')

    substance_long.to_csv('results/01_fentanyl_timeline/all_substances_annual.csv', index=False)

    # Plot
    fig, ax = plt.subplots(figsize=(12, 6))
    for substance in substance_cols:
        data = substance_long[substance_long['Substance'] == substance]
        ax.plot(data['Year'], data['Percentage'],
                marker='o', linewidth=2, label=substance,
                color=colors.get(substance, '#666666'))

    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('% of All Overdose Deaths', fontsize=12)
    ax.set_title('Timeline of All Substances Involved in Overdose Deaths\nLos Angeles County 2012-2023',
                 fontsize=14, fontweight='bold')
    ax.legend(fontsize=10, loc='best')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('results/01_fentanyl_timeline/all_substances_timeline.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Saved: all_substances_timeline.png")

    # === 3. Fentanyl Co-occurrence Patterns ===
    print("Analyzing fentanyl co-occurrence patterns...")

    # Filter to fentanyl deaths only
    df_fentanyl = df[df['Fentanyl'] == 1].copy()

    # Calculate co-occurrence rates
    other_substances = ['Heroin', 'Methamphetamine', 'Cocaine',
                       'Prescription.opioids', 'Benzodiazepines']

    cooccurrence = []
    for year in sorted(df_fentanyl['Year'].unique()):
        year_data = df_fentanyl[df_fentanyl['Year'] == year]
        total_fentanyl = len(year_data)

        for substance in other_substances:
            count = year_data[substance].sum()
            pct = (count / total_fentanyl * 100) if total_fentanyl > 0 else 0
            cooccurrence.append({
                'Year': year,
                'Substance': substance,
                'Count': count,
                'Percentage': pct,
                'Total_Fentanyl_Deaths': total_fentanyl
            })

    cooccurrence_df = pd.DataFrame(cooccurrence)
    cooccurrence_df.to_csv('results/01_fentanyl_timeline/fentanyl_cooccurrence.csv', index=False)

    # Plot co-occurrence trends
    fig, ax = plt.subplots(figsize=(12, 6))
    for substance in other_substances:
        data = cooccurrence_df[cooccurrence_df['Substance'] == substance]
        ax.plot(data['Year'], data['Percentage'],
                marker='o', linewidth=2, label=substance,
                color=colors.get(substance, '#666666'))

    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('% of Fentanyl Deaths', fontsize=12)
    ax.set_title('Co-occurrence of Other Substances in Fentanyl Deaths\nLos Angeles County 2012-2023',
                 fontsize=14, fontweight='bold')
    ax.legend(fontsize=10, loc='best')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('results/01_fentanyl_timeline/fentanyl_cooccurrence.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Saved: fentanyl_cooccurrence.png")

    # === 4. Stacked area chart of substance proportions ===
    print("Creating stacked area chart...")

    fig, ax = plt.subplots(figsize=(12, 6))

    # Prepare data for stacked area
    pivot_data = substance_annual_pct.set_index('Year')[substance_cols]

    ax.stackplot(pivot_data.index,
                 *[pivot_data[col] for col in substance_cols],
                 labels=substance_cols,
                 colors=[colors.get(col, '#666666') for col in substance_cols],
                 alpha=0.8)

    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('% of All Overdose Deaths', fontsize=12)
    ax.set_title('Composition of Overdose Deaths by Substance Over Time\nLos Angeles County 2012-2023',
                 fontsize=14, fontweight='bold')
    ax.legend(loc='upper left', fontsize=10)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('results/01_fentanyl_timeline/substance_composition_stacked.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Saved: substance_composition_stacked.png")

    # Print key findings
    print("\n" + "="*60)
    print("KEY FINDINGS:")
    print("="*60)

    # Find crossover year
    crossover = annual_counts[annual_counts['Fentanyl'] > annual_counts['Heroin']]
    if len(crossover) > 0:
        crossover_year = crossover['Year'].min()
        print(f"\n1. Fentanyl surpassed heroin in {crossover_year}")

        year_2012 = annual_counts[annual_counts['Year'] == 2012].iloc[0]
        year_2023 = annual_counts[annual_counts['Year'] == 2023].iloc[0]

        print(f"\n2. Fentanyl deaths:")
        print(f"   2012: {year_2012['Fentanyl']:.0f} ({year_2012['Fentanyl_pct']:.1f}%)")
        print(f"   2023: {year_2023['Fentanyl']:.0f} ({year_2023['Fentanyl_pct']:.1f}%)")
        print(f"   Increase: {((year_2023['Fentanyl'] / year_2012['Fentanyl']) - 1) * 100:.0f}%")

        print(f"\n3. Heroin deaths:")
        print(f"   2012: {year_2012['Heroin']:.0f} ({year_2012['Heroin_pct']:.1f}%)")
        print(f"   2023: {year_2023['Heroin']:.0f} ({year_2023['Heroin_pct']:.1f}%)")
        print(f"   Change: {((year_2023['Heroin'] / year_2012['Heroin']) - 1) * 100:.0f}%")

    print("\n" + "="*60)
    print("Analysis complete!")

if __name__ == "__main__":
    main()
