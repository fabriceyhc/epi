#!/usr/bin/env python
# coding: utf-8

"""
Descriptive Statistics and Raincloud Plots
Creates Table 1 (descriptive statistics by substance) and detailed age/race/substance visualizations
Refactored from process.py to integrate with the analysis pipeline

Originally converted from RMarkdown, now using standardized utilities
"""

import os
import warnings
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import ptitprince as pt
from tableone import TableOne
from plotnine import (
    ggplot, aes, geom_bar, geom_density, geom_violin, geom_jitter,
    scale_color_brewer, scale_fill_brewer, scale_color_manual, scale_fill_manual,
    scale_y_continuous, scale_x_continuous, theme_minimal, theme, guides,
    labs, facet_wrap, facet_grid, guide_legend, element_text
)

# Import our utilities
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from utils import (
    full_data_processing, SUBSTANCE_COLS, RACE_COLORS, LANCET_COLORS,
    get_race_labels, get_substance_labels
)

# Suppress warnings
warnings.filterwarnings('ignore')

# Set random seed
np.random.seed(100)

# Create output directories
os.makedirs("results/00_descriptive_statistics", exist_ok=True)
os.makedirs("results/00_descriptive_statistics", exist_ok=True)

print("="*70)
print("DESCRIPTIVE STATISTICS AND RAINCLOUD PLOTS")
print("="*70)

def main():
    # ========================================================================
    # 1. LOAD AND PROCESS DATA
    # ========================================================================

    print("\nLoading and processing data...")
    df = full_data_processing(filter_years=True)  # 2012-2023 only

    print(f"✓ Loaded {len(df):,} overdose deaths (2012-2023)")
    print(f"✓ Standardized race/ethnicity categories")
    print(f"✓ Created age groups and polysubstance indicators")

    # ========================================================================
    # 2. CREATE TABLE 1 (Descriptive Statistics by Substance)
    # ========================================================================

    print("\n" + "="*70)
    print("CREATING TABLE 1: DESCRIPTIVE STATISTICS BY SUBSTANCE")
    print("="*70)

    # Pivot to long format
    df_long = df.melt(
        id_vars=['Age', 'Age_Group', 'Race_Ethnicity_Cleaned',
                 'Polysubstance', 'Number_Substances', 'Fentanyl', 'Year'],
        value_vars=SUBSTANCE_COLS,
        var_name='Substance',
        value_name='Present'
    )

    # Filter to rows where substance is present
    df_table = df_long[df_long['Present'] == 1].copy()

    # Prepare for TableOne
    df_table['Fentanyl_Present'] = np.where(df_table['Fentanyl'] == 1, 'Yes', 'No')
    df_table['Substance'] = df_table['Substance'].replace(
        {'Prescription.opioids': 'Prescription Opioids'}
    )

    # Convert categorical to strings for TableOne
    for col in ['Age_Group', 'Race_Ethnicity_Cleaned', 'Substance']:
        if col in df_table.columns:
            df_table[col] = df_table[col].astype(str)

    # Create Table 1
    columns = ['Age', 'Age_Group', 'Race_Ethnicity_Cleaned',
               'Polysubstance', 'Number_Substances', 'Fentanyl_Present', 'Year']
    categorical = ['Age_Group', 'Race_Ethnicity_Cleaned',
                   'Polysubstance', 'Fentanyl_Present']

    table_one = TableOne(
        df_table,
        columns=columns,
        categorical=categorical,
        groupby='Substance',
        pval=True,
        htest_name=True
    )

    # Save to CSV
    table_one_df = table_one.tableone
    table_one_df.to_csv('results/00_descriptive_statistics/Table_1_by_substance.csv')
    print("\n✓ Saved Table 1: results/00_descriptive_statistics/Table_1_by_substance.csv")

    # Also create a version for the main results folder (for backwards compatibility)
    table_one_df.to_csv('results/Table_1.csv')
    print("✓ Saved copy: results/Table_1.csv")

    # ========================================================================
    # 3. AGE DISTRIBUTION PLOTS BY SUBSTANCE
    # ========================================================================

    print("\n" + "="*70)
    print("CREATING AGE DISTRIBUTION PLOTS")
    print("="*70)

    # Prepare data for age plots
    age_substance_cols = ["Any Opioids", "Heroin", "Fentanyl",
                          "Prescription.opioids", "Methamphetamine",
                          "Cocaine", "Benzodiazepines", "Alcohol", "Others"]

    df_age = df.melt(
        id_vars=['Age', 'Year', 'Fentanyl'],
        value_vars=[col for col in age_substance_cols if col in df.columns],
        var_name='Substance',
        value_name='Present'
    )

    df_age = df_age[df_age['Present'] == 1].copy()
    df_age['Fentanyl_Status'] = np.where(df_age['Fentanyl'] == 1, "Present", "Absent")

    # Reverse substance order for better visualization
    substance_order = list(reversed(age_substance_cols))
    df_age['Substance'] = pd.Categorical(
        df_age['Substance'],
        categories=[s for s in substance_order if s in df_age['Substance'].unique()],
        ordered=True
    )

    # Plot 1: Density plots by substance (faceted)
    print("\nCreating density plots...")

    plot1 = (
        ggplot(df_age, aes(x='Age')) +
        geom_density(fill="lightgrey", alpha=0.7) +
        scale_x_continuous(limits=(10, 80)) +
        labs(title="Age distribution of overdose deaths by substance involved",
             subtitle="Los Angeles County, 2012-2023") +
        facet_wrap('~Substance', ncol=1) +
        theme_minimal() +
        theme(figure_size=(8, 12))
    )

    plot1.save('results/00_descriptive_statistics/age_density_by_substance.png',
               dpi=300, width=8, height=12)
    print("✓ Saved: results/00_descriptive_statistics/age_density_by_substance.png")

    # Plot 2: Density by time period
    df_age['Time_Period'] = np.where(df_age['Year'] < 2017, "2012-2016", "2017-2023")

    plot2 = (
        ggplot(df_age, aes(x='Age', color='Substance', fill='Substance')) +
        geom_density(alpha=0.3) +
        scale_x_continuous(limits=(10, 80)) +
        scale_color_manual(values=LANCET_COLORS) +
        scale_fill_manual(values=LANCET_COLORS) +
        labs(title="Age distribution by substance and time period",
             subtitle="Los Angeles County") +
        facet_wrap("~Time_Period", nrow=1) +
        theme_minimal() +
        theme(figure_size=(12, 5))
    )

    plot2.save('results/00_descriptive_statistics/age_density_by_time_period.png',
               dpi=300, width=12, height=5)
    print("✓ Saved: results/00_descriptive_statistics/age_density_by_time_period.png")

    # Plot 3: Violin + jitter plot
    df_age_filt = df_age[(df_age['Age'] > 10) & (df_age['Age'] < 80)].copy()

    plot3 = (
        ggplot(df_age_filt, aes(x='Substance', y='Age')) +
        geom_violin() +
        geom_jitter(aes(color='Fentanyl_Status', group='Substance'),
                    size=0.1, alpha=0.8, width=0.25, random_state=100) +
        scale_color_brewer(type='qual') +
        theme_minimal() +
        guides(color=guide_legend(override_aes={'size': 2})) +
        theme(axis_text_x=element_text(angle=45, hjust=1),
              figure_size=(10, 6))
    )

    plot3.save('results/00_descriptive_statistics/age_violin_by_substance_fentanyl.png',
               dpi=300, width=10, height=6)
    print("✓ Saved: results/00_descriptive_statistics/age_violin_by_substance_fentanyl.png")

    # ========================================================================
    # 4. RAINCLOUD PLOTS BY RACE
    # ========================================================================

    print("\n" + "="*70)
    print("CREATING RAINCLOUD PLOTS BY RACE")
    print("="*70)

    # Prepare data for race plots
    df_race = df.melt(
        id_vars=['Age', 'Age_Binary', 'Race_Ethnicity_Cleaned', 'Year', 'Fentanyl'],
        value_vars=SUBSTANCE_COLS,
        var_name='Substance',
        value_name='Present'
    )

    df_race = df_race[df_race['Present'] == 1].copy()

    # Rename substances for display
    display_labels = get_substance_labels('display')
    df_race['Substance'] = df_race['Substance'].replace(display_labels)

    # Set factor levels
    substance_display_order = list(display_labels.values())
    df_race['Substance'] = pd.Categorical(
        df_race['Substance'],
        categories=substance_display_order,
        ordered=True
    )

    # Add fentanyl status
    df_race['Fentanyl_Status'] = np.where(df_race['Fentanyl'] == 1, "Present", "Absent")

    # Filter to main race groups and title case
    df_race['Race'] = df_race['Race_Ethnicity_Cleaned'].astype(str).str.title()
    df_race = df_race[df_race['Race'].isin(["Black", "Latine", "White", "Asian"])].copy()

    # Raincloud plot parameters
    races = ["Black", "Latine", "White", "Asian"]
    palette = {"Present": LANCET_COLORS[0], "Absent": LANCET_COLORS[1]}

    # Create main raincloud plot
    print("\nCreating main raincloud plot (all years)...")

    fig, axes = plt.subplots(4, 1, figsize=(16, 8), sharex=True, sharey=True)

    for idx, race in enumerate(races):
        ax = axes[idx]
        race_data = df_race[df_race['Race'] == race]

        # Use ptitprince for raincloud
        pt.RainCloud(
            data=race_data,
            x='Substance',
            y='Age',
            hue='Fentanyl_Status',
            palette=palette,
            order=substance_display_order,
            ax=ax,
            move=0.3,
            width_viol=0.6,
            width_box=0.25,
            alpha=0.5,
            dodge=True,
            point_size=0.1,
            pointplot=False  # Remove connecting lines
        )

        ax.set_title(race, fontsize=12, fontweight='bold')
        ax.set_ylabel('Age', fontsize=10)
        ax.set_xlabel('')
        ax.set_ylim(0, 80)

        # Move x-axis to top
        ax.xaxis.set_ticks_position("top")
        ax.xaxis.set_label_position("top")

        # Only show legend on first subplot
        if idx > 0:
            ax.get_legend().remove()

    axes[-1].set_xlabel('Substance', fontsize=11, fontweight='bold')
    axes[-1].xaxis.set_ticks_position("bottom")
    axes[-1].xaxis.set_label_position("bottom")

    plt.suptitle('Age Distribution of Overdose Deaths by Race and Substance\n' +
                 'Los Angeles County, 2012-2023',
                 fontsize=14, fontweight='bold', y=1.02)

    plt.tight_layout()
    plt.savefig('results/00_descriptive_statistics/race_age_substance_raincloud.png',
                dpi=300, bbox_inches='tight', facecolor='white')
    print("✓ Saved: results/00_descriptive_statistics/race_age_substance_raincloud.png")
    plt.close()

    # Raincloud plots by time period
    print("\nCreating raincloud plots by time period...")

    df_race['Time_Period'] = np.where(df_race['Year'] < 2017, "2012-2016", "2017-2023")

    for period in ["2012-2016", "2017-2023"]:
        period_data = df_race[df_race['Time_Period'] == period]

        fig, axes = plt.subplots(4, 1, figsize=(16, 8), sharex=True, sharey=True)

        for idx, race in enumerate(races):
            ax = axes[idx]
            race_period_data = period_data[period_data['Race'] == race]

            pt.RainCloud(
                data=race_period_data,
                x='Substance',
                y='Age',
                hue='Fentanyl_Status',
                palette=palette,
                order=substance_display_order,
                ax=ax,
                move=0.3,
                width_viol=0.6,
                width_box=0.25,
                alpha=0.5,
                dodge=True,
                point_size=0.1,
                pointplot=False
            )

            ax.set_title(race, fontsize=12, fontweight='bold')
            ax.set_ylabel('Age', fontsize=10)
            ax.set_xlabel('')
            ax.set_ylim(0, 80)

            ax.xaxis.set_ticks_position("top")
            ax.xaxis.set_label_position("top")

            if idx > 0:
                ax.get_legend().remove()

        axes[-1].set_xlabel('Substance', fontsize=11, fontweight='bold')
        axes[-1].xaxis.set_ticks_position("bottom")
        axes[-1].xaxis.set_label_position("bottom")

        plt.suptitle(f'Age Distribution by Race and Substance\n' +
                     f'Los Angeles County, {period}',
                     fontsize=14, fontweight='bold', y=1.02)

        plt.tight_layout()

        filename = period.replace("-", "_")
        plt.savefig(f'results/00_descriptive_statistics/race_age_substance_{filename}.png',
                    dpi=300, bbox_inches='tight', facecolor='white')
        print(f"✓ Saved: results/00_descriptive_statistics/race_age_substance_{filename}.png")
        plt.close()

    # ========================================================================
    # 5. BASIC DESCRIPTIVE PLOTS
    # ========================================================================

    print("\n" + "="*70)
    print("CREATING BASIC DESCRIPTIVE PLOTS")
    print("="*70)

    # Mean age by substance
    df_long_present = df_long[df_long['Present'] == 1].copy()

    plot_mean_age = (
        ggplot(df_long_present, aes(x='Substance', y='Age', fill='Substance', color='Substance')) +
        geom_bar(stat="summary", fun_y=np.mean) +
        scale_color_brewer(type='qual', palette='Dark2') +
        scale_fill_brewer(type='qual', palette='Dark2') +
        scale_y_continuous(limits=(0, 50)) +
        labs(title="Mean Age by Substance Involved",
             y="Mean Age (years)") +
        theme_minimal() +
        theme(axis_text_x=element_text(angle=45, hjust=1),
              legend_position='none',
              figure_size=(10, 6))
    )

    plot_mean_age.save('results/00_descriptive_statistics/mean_age_by_substance.png',
                       dpi=300, width=10, height=6)
    print("✓ Saved: results/00_descriptive_statistics/mean_age_by_substance.png")

    # Substance proportion by race
    df_race_prop = df_long[
        (df_long['Present'] == 1) &
        (~df_long['Race_Ethnicity_Cleaned'].isin(["OTHER", "UNKNOWN"]))
    ].copy()

    plot_race_prop = (
        ggplot(df_race_prop, aes(x='Race_Ethnicity_Cleaned', fill='Substance')) +
        geom_bar(position="fill") +
        scale_fill_manual(values=LANCET_COLORS) +
        labs(title="Substance Proportions by Race/Ethnicity",
             y="Proportion",
             x="Race or Ethnicity") +
        theme_minimal() +
        theme(axis_text_x=element_text(angle=45, hjust=1),
              figure_size=(10, 6))
    )

    plot_race_prop.save('results/00_descriptive_statistics/substance_proportion_by_race.png',
                        dpi=300, width=10, height=6)
    print("✓ Saved: results/00_descriptive_statistics/substance_proportion_by_race.png")

    # ========================================================================
    # SUMMARY
    # ========================================================================

    print("\n" + "="*70)
    print("ANALYSIS COMPLETE")
    print("="*70)
    print("\nFiles created:")
    print("\nDescriptive Statistics:")
    print("  • results/00_descriptive_statistics/Table_1_by_substance.csv")
    print("  • results/Table_1.csv (copy)")
    print("\nAge Distribution Plots:")
    print("  • results/00_descriptive_statistics/age_density_by_substance.png")
    print("  • results/00_descriptive_statistics/age_density_by_time_period.png")
    print("  • results/00_descriptive_statistics/age_violin_by_substance_fentanyl.png")
    print("\nRaincloud Plots:")
    print("  • results/00_descriptive_statistics/race_age_substance_raincloud.png")
    print("  • results/00_descriptive_statistics/race_age_substance_2012_2016.png")
    print("  • results/00_descriptive_statistics/race_age_substance_2017_2023.png")
    print("\nBasic Plots:")
    print("  • results/00_descriptive_statistics/mean_age_by_substance.png")
    print("  • results/00_descriptive_statistics/substance_proportion_by_race.png")
    print("\n" + "="*70)
    print("\nThis script creates publication-ready descriptive statistics and")
    print("detailed age/race/substance visualizations using raincloud plots.")
    print("="*70)


if __name__ == "__main__":
    main()
