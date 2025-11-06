#!/usr/bin/env python
# coding: utf-8

"""
Polysubstance Trends Analysis
- Number of substances per death over time
- Specific dangerous combinations emerging
- Complexity of overdose deaths
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Settings
sns.set_style("whitegrid")
os.makedirs("results/02_polysubstance_trends", exist_ok=True)

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

    # Calculate number of substances
    substance_cols = ['Heroin', 'Fentanyl', 'Prescription.opioids',
                      'Methamphetamine', 'Cocaine', 'Benzodiazepines', 'Alcohol', 'Others']

    df['Number_Substances'] = df[substance_cols].sum(axis=1)
    df['Polysubstance'] = (df['Number_Substances'] > 1).astype(int)

    # === 1. Trend in number of substances over time ===
    print("Analyzing polysubstance trends...")

    # Annual statistics
    annual_stats = df.groupby('Year').agg({
        'Number_Substances': ['mean', 'median'],
        'Polysubstance': 'mean'
    }).reset_index()
    annual_stats.columns = ['Year', 'Mean_Substances', 'Median_Substances', 'Polysubstance_Rate']
    annual_stats['Polysubstance_Pct'] = annual_stats['Polysubstance_Rate'] * 100

    annual_stats.to_csv('results/02_polysubstance_trends/annual_polysubstance_stats.csv', index=False)

    # Plot
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # Mean number of substances
    ax1.plot(annual_stats['Year'], annual_stats['Mean_Substances'],
             marker='o', linewidth=2, color='#ED0000')
    ax1.set_xlabel('Year', fontsize=12)
    ax1.set_ylabel('Number of Substances', fontsize=12)
    ax1.set_title('Average Number of Substances per Overdose Death', fontsize=14, fontweight='bold')
    ax1.set_ylim(1, 2)
    ax1.grid(True, alpha=0.3)

    # Polysubstance rate
    ax2.plot(annual_stats['Year'], annual_stats['Polysubstance_Pct'],
             marker='o', linewidth=2, color='#42B540')
    ax2.set_xlabel('Year', fontsize=12)
    ax2.set_ylabel('% of Deaths', fontsize=12)
    ax2.set_title('Polysubstance Deaths Over Time', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.set_ylim(0, 100)

    plt.tight_layout()
    plt.savefig('results/02_polysubstance_trends/polysubstance_trends.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Saved: polysubstance_trends.png")

    # === 2. Distribution of number of substances by year ===
    print("Creating distribution plots...")

    # Create distribution data
    dist_data = df.groupby(['Year', 'Number_Substances']).size().reset_index(name='Count')
    dist_pivot = dist_data.pivot(index='Year', columns='Number_Substances', values='Count').fillna(0)

    # Convert to percentages
    dist_pct = dist_pivot.div(dist_pivot.sum(axis=1), axis=0) * 100

    # Stacked bar chart
    fig, ax = plt.subplots(figsize=(12, 6))
    dist_pct.plot(kind='bar', stacked=True, ax=ax, colormap='RdYlBu_r', width=0.8)

    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('% of Deaths', fontsize=12)
    ax.set_title('Distribution of Number of Substances Involved in Overdose Deaths',
                 fontsize=14, fontweight='bold')
    ax.legend(title='Number of\nSubstances', bbox_to_anchor=(1.05, 1), loc='upper left')
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
    plt.tight_layout()
    plt.savefig('results/02_polysubstance_trends/substance_count_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Saved: substance_count_distribution.png")

    # === 3. Specific dangerous combinations ===
    print("Analyzing specific combinations...")

    # Define key combinations
    combinations = {
        'Fentanyl + Meth': (df['Fentanyl'] == 1) & (df['Methamphetamine'] == 1),
        'Fentanyl + Cocaine': (df['Fentanyl'] == 1) & (df['Cocaine'] == 1),
        'Fentanyl + Benzos': (df['Fentanyl'] == 1) & (df['Benzodiazepines'] == 1),
        'Heroin + Fentanyl': (df['Heroin'] == 1) & (df['Fentanyl'] == 1),
        'Meth + Heroin': (df['Methamphetamine'] == 1) & (df['Heroin'] == 1),
        'Cocaine + Heroin': (df['Cocaine'] == 1) & (df['Heroin'] == 1)
    }

    combo_data = []
    for combo_name, condition in combinations.items():
        annual = df[condition].groupby(df['Year']).size().reset_index(name='Count')
        annual['Combination'] = combo_name
        combo_data.append(annual)

    combo_df = pd.concat(combo_data, ignore_index=True)

    # Calculate total deaths per year for percentages
    annual_totals = df.groupby('Year').size().reset_index(name='Total')
    combo_df = combo_df.merge(annual_totals, on='Year')
    combo_df['Percentage'] = (combo_df['Count'] / combo_df['Total']) * 100

    combo_df.to_csv('results/02_polysubstance_trends/dangerous_combinations.csv', index=False)

    # Plot combinations
    fig, ax = plt.subplots(figsize=(14, 7))

    for combo in combinations.keys():
        data = combo_df[combo_df['Combination'] == combo]
        ax.plot(data['Year'], data['Percentage'],
                marker='o', linewidth=2, label=combo)

    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('% of All Overdose Deaths', fontsize=12)
    ax.set_title('Trends in Specific Drug Combinations\nLos Angeles County 2012-2023',
                 fontsize=14, fontweight='bold')
    ax.legend(fontsize=10, loc='best')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('results/02_polysubstance_trends/dangerous_combinations.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Saved: dangerous_combinations.png")

    # === 3b. Detailed Fentanyl-Methamphetamine Co-involvement Analysis ===
    print("Analyzing fentanyl-methamphetamine co-involvement in detail...")

    # Create substance exposure categories
    df['Substance_Category'] = 'None'
    df.loc[(df['Fentanyl'] == 1) & (df['Methamphetamine'] == 0), 'Substance_Category'] = 'Fentanyl Only'
    df.loc[(df['Fentanyl'] == 0) & (df['Methamphetamine'] == 1), 'Substance_Category'] = 'Meth Only'
    df.loc[(df['Fentanyl'] == 1) & (df['Methamphetamine'] == 1), 'Substance_Category'] = 'Fentanyl + Meth'

    # Annual trends in fentanyl-meth co-involvement
    fen_meth_annual = []
    for year in sorted(df['Year'].unique()):
        year_data = df[df['Year'] == year]
        total = len(year_data)

        fent_only = (year_data['Substance_Category'] == 'Fentanyl Only').sum()
        meth_only = (year_data['Substance_Category'] == 'Meth Only').sum()
        both = (year_data['Substance_Category'] == 'Fentanyl + Meth').sum()
        either = fent_only + meth_only + both

        fen_meth_annual.append({
            'Year': year,
            'Fentanyl_Only': fent_only,
            'Meth_Only': meth_only,
            'Fentanyl_Meth': both,
            'Either': either,
            'Total': total,
            'Fentanyl_Only_Pct': (fent_only / total * 100) if total > 0 else 0,
            'Meth_Only_Pct': (meth_only / total * 100) if total > 0 else 0,
            'Fentanyl_Meth_Pct': (both / total * 100) if total > 0 else 0,
            'CoInvolvement_Among_Either': (both / either * 100) if either > 0 else 0
        })

    fen_meth_df = pd.DataFrame(fen_meth_annual)
    fen_meth_df.to_csv('results/02_polysubstance_trends/fentanyl_meth_coinvolvement_annual.csv', index=False)

    # Plot fentanyl-meth co-involvement
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

    # Absolute counts
    ax1.plot(fen_meth_df['Year'], fen_meth_df['Fentanyl_Only'],
            marker='o', linewidth=2, color='#ED0000', label='Fentanyl Only')
    ax1.plot(fen_meth_df['Year'], fen_meth_df['Meth_Only'],
            marker='s', linewidth=2, color='#42B540', label='Meth Only')
    ax1.plot(fen_meth_df['Year'], fen_meth_df['Fentanyl_Meth'],
            marker='^', linewidth=2.5, color='#925E9F', label='Fentanyl + Meth', markersize=8)

    ax1.set_xlabel('Year', fontsize=12)
    ax1.set_ylabel('Number of Deaths', fontsize=12)
    ax1.set_title('Fentanyl and Methamphetamine Involvement Patterns',
                  fontsize=13, fontweight='bold')
    ax1.legend(fontsize=11)
    ax1.grid(True, alpha=0.3)

    # Co-involvement rate among those with either substance
    ax2.plot(fen_meth_df['Year'], fen_meth_df['CoInvolvement_Among_Either'],
            marker='o', linewidth=2.5, color='#925E9F')
    ax2.set_xlabel('Year', fontsize=12)
    ax2.set_ylabel('% with Both Substances', fontsize=12)
    ax2.set_title('Co-involvement Rate Among Fentanyl or Meth Deaths',
                  fontsize=13, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.set_ylim(0, 100)

    plt.tight_layout()
    plt.savefig('results/02_polysubstance_trends/fentanyl_meth_detailed.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Saved: fentanyl_meth_detailed.png")

    # Age comparison by substance category
    age_comparison = []
    for category in ['Fentanyl Only', 'Meth Only', 'Fentanyl + Meth']:
        cat_data = df[df['Substance_Category'] == category]
        ages = cat_data['Age'].dropna()

        if len(ages) >= 5:
            age_comparison.append({
                'Category': category,
                'n': len(ages),
                'Median': ages.median(),
                'Mean': ages.mean(),
                'Q25': ages.quantile(0.25),
                'Q75': ages.quantile(0.75),
                'SD': ages.std()
            })

    age_comp_df = pd.DataFrame(age_comparison)
    age_comp_df.to_csv('results/02_polysubstance_trends/age_by_fentanyl_meth_category.csv', index=False)

    # Plot age comparison
    fig, ax = plt.subplots(figsize=(10, 6))

    categories = age_comp_df['Category'].values
    medians = age_comp_df['Median'].values
    colors_cat = ['#ED0000', '#42B540', '#925E9F']

    bars = ax.bar(categories, medians, color=colors_cat, alpha=0.7, edgecolor='black')
    ax.set_ylabel('Median Age (years)', fontsize=12)
    ax.set_title('Median Age at Death by Substance Exposure Pattern\nLos Angeles County 2012-2023',
                fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')

    # Add value labels on bars
    for bar, median in zip(bars, medians):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{median:.0f}',
                ha='center', va='bottom', fontsize=11, fontweight='bold')

    plt.tight_layout()
    plt.savefig('results/02_polysubstance_trends/age_comparison_fentanyl_meth.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Saved: age_comparison_fentanyl_meth.png")

    # === 4. Heatmap of combinations ===
    print("Creating combination heatmap...")

    # Most recent year analysis
    recent_year = df['Year'].max()
    df_recent = df[df['Year'] == recent_year]

    # Create correlation matrix
    corr_matrix = df_recent[substance_cols].corr()

    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='RdYlBu_r',
                center=0, square=True, ax=ax, cbar_kws={'label': 'Correlation'})
    ax.set_title(f'Co-occurrence of Substances in {recent_year}\nLos Angeles County',
                 fontsize=14, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig('results/02_polysubstance_trends/substance_correlation_heatmap.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Saved: substance_correlation_heatmap.png")

    # === 5. Triple combinations (most dangerous) ===
    print("Analyzing triple combinations...")

    df_triple = df[df['Number_Substances'] >= 3].copy()

    triple_combos = []
    for year in sorted(df_triple['Year'].unique()):
        year_data = df_triple[df_triple['Year'] == year]
        total = len(year_data)

        # Check common triple combinations
        fen_meth_benzo = ((year_data['Fentanyl'] == 1) &
                          (year_data['Methamphetamine'] == 1) &
                          (year_data['Benzodiazepines'] == 1)).sum()

        fen_coke_benzo = ((year_data['Fentanyl'] == 1) &
                          (year_data['Cocaine'] == 1) &
                          (year_data['Benzodiazepines'] == 1)).sum()

        fen_meth_coke = ((year_data['Fentanyl'] == 1) &
                         (year_data['Methamphetamine'] == 1) &
                         (year_data['Cocaine'] == 1)).sum()

        triple_combos.append({
            'Year': year,
            'Fent+Meth+Benzo': fen_meth_benzo,
            'Fent+Coke+Benzo': fen_coke_benzo,
            'Fent+Meth+Coke': fen_meth_coke,
            'Total_Triple+': total
        })

    triple_df = pd.DataFrame(triple_combos)
    triple_df.to_csv('results/02_polysubstance_trends/triple_combinations.csv', index=False)

    # Print key findings
    print("\n" + "="*60)
    print("KEY FINDINGS:")
    print("="*60)

    year_2012 = annual_stats[annual_stats['Year'] == 2012].iloc[0]
    year_2023 = annual_stats[annual_stats['Year'] == 2023].iloc[0]

    print(f"\n1. Average substances per death:")
    print(f"   2012: {year_2012['Mean_Substances']:.2f}")
    print(f"   2023: {year_2023['Mean_Substances']:.2f}")
    print(f"   Change: {((year_2023['Mean_Substances'] - year_2012['Mean_Substances']) / year_2012['Mean_Substances']) * 100:+.1f}%")

    print(f"\n2. Polysubstance death rate:")
    print(f"   2012: {year_2012['Polysubstance_Pct']:.1f}%")
    print(f"   2023: {year_2023['Polysubstance_Pct']:.1f}%")

    # Most dramatic combination increase
    combo_2012 = combo_df[combo_df['Year'] == 2012].set_index('Combination')
    combo_2023 = combo_df[combo_df['Year'] == 2023].set_index('Combination')

    print(f"\n3. Fentanyl-Methamphetamine co-involvement:")
    fm_2012 = fen_meth_df[fen_meth_df['Year'] == 2012].iloc[0]
    fm_2023 = fen_meth_df[fen_meth_df['Year'] == 2023].iloc[0]
    print(f"   Co-involvement rate (among fentanyl or meth deaths):")
    print(f"   2012: {fm_2012['CoInvolvement_Among_Either']:.1f}%")
    print(f"   2023: {fm_2023['CoInvolvement_Among_Either']:.1f}%")

    print(f"\n4. Age differences by substance category:")
    for _, row in age_comp_df.iterrows():
        if row['n'] >= 5:
            print(f"   {row['Category']}: median {row['Median']:.0f} years (n={row['n']:.0f})")

    print(f"\n5. Fastest growing combination:")
    for combo in combinations.keys():
        if combo in combo_2012.index and combo in combo_2023.index:
            val_2012 = combo_2012.loc[combo, 'Percentage']
            val_2023 = combo_2023.loc[combo, 'Percentage']
            change = val_2023 - val_2012
            print(f"   {combo}: {val_2012:.1f}% → {val_2023:.1f}% ({change:+.1f} pp)")

    print("\n" + "="*60)
    print("Analysis complete!")

if __name__ == "__main__":
    main()
