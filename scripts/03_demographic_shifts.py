#!/usr/bin/env python
# coding: utf-8

"""
Demographic Shifts Analysis
- Age trends over time by substance
- Racial disparities and changes
- Gender patterns (previously unused in the data)
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Settings
sns.set_style("whitegrid")
os.makedirs("results/03_demographic_shifts", exist_ok=True)

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

    substance_cols = ['Heroin', 'Fentanyl', 'Prescription.opioids',
                      'Methamphetamine', 'Cocaine', 'Benzodiazepines', 'Alcohol', 'Others']

    # === 1. Age trends over time ===
    print("Analyzing age trends...")

    age_annual = df.groupby('Year').agg({
        'Age': ['mean', 'median', 'std']
    }).reset_index()
    age_annual.columns = ['Year', 'Mean_Age', 'Median_Age', 'Std_Age']

    age_annual.to_csv('results/03_demographic_shifts/age_trends_annual.csv', index=False)

    # Plot overall age trend
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(age_annual['Year'], age_annual['Mean_Age'],
            marker='o', linewidth=2, color='#ED0000', label='Mean Age')
    ax.plot(age_annual['Year'], age_annual['Median_Age'],
            marker='s', linewidth=2, color='#00468B', label='Median Age', linestyle='--')
    ax.fill_between(age_annual['Year'],
                     age_annual['Mean_Age'] - age_annual['Std_Age'],
                     age_annual['Mean_Age'] + age_annual['Std_Age'],
                     alpha=0.2, color='#ED0000')
    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('Age (years)', fontsize=12)
    ax.set_title('Age of Overdose Victims Over Time\nLos Angeles County 2012-2023',
                 fontsize=14, fontweight='bold')
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('results/03_demographic_shifts/age_trends_overall.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Saved: age_trends_overall.png")

    # === 2. Age trends by substance ===
    print("Analyzing age trends by substance...")

    # Create long format for substance analysis
    df_long = df.melt(id_vars=['CaseNumber', 'Age', 'Year'],
                      value_vars=substance_cols,
                      var_name='Substance', value_name='Present')
    df_long = df_long[df_long['Present'] == 1]

    age_substance = df_long.groupby(['Year', 'Substance'])['Age'].mean().reset_index()
    age_substance.to_csv('results/03_demographic_shifts/age_by_substance_annual.csv', index=False)

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
        data = age_substance[age_substance['Substance'] == substance]
        ax.plot(data['Year'], data['Age'],
                marker='o', linewidth=2, label=substance,
                color=colors.get(substance, '#666666'))

    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('Mean Age (years)', fontsize=12)
    ax.set_title('Mean Age of Overdose Victims by Substance Over Time\nLos Angeles County 2012-2023',
                 fontsize=14, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('results/03_demographic_shifts/age_by_substance.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Saved: age_by_substance.png")

    # === 3. Racial disparities over time ===
    print("Analyzing racial disparities...")

    # Annual deaths by race
    race_annual = df.groupby(['Year', 'Race']).size().reset_index(name='Deaths')

    # Calculate rates per 100k population (would need census data for true rates)
    # For now, show absolute numbers and proportions
    race_totals = df.groupby('Year').size().reset_index(name='Total')
    race_annual = race_annual.merge(race_totals, on='Year')
    race_annual['Percentage'] = (race_annual['Deaths'] / race_annual['Total']) * 100

    race_annual.to_csv('results/03_demographic_shifts/race_trends_annual.csv', index=False)

    # Plot - absolute numbers
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

    race_colors = {
        'WHITE': '#00468B',
        'LATINE': '#ED0000',
        'BLACK': '#42B540',
        'ASIAN': '#0099B4',
        'OTHER': '#999999'
    }

    for race in ['WHITE', 'LATINE', 'BLACK', 'ASIAN', 'OTHER']:
        data = race_annual[race_annual['Race'] == race]
        ax1.plot(data['Year'], data['Deaths'],
                marker='o', linewidth=2, label=race,
                color=race_colors.get(race, '#666666'))

    ax1.set_xlabel('Year', fontsize=12)
    ax1.set_ylabel('Number of Deaths', fontsize=12)
    ax1.set_title('Overdose Deaths by Race/Ethnicity Over Time (Absolute)',
                  fontsize=13, fontweight='bold')
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)

    # Plot - proportions
    for race in ['WHITE', 'LATINE', 'BLACK', 'ASIAN', 'OTHER']:
        data = race_annual[race_annual['Race'] == race]
        ax2.plot(data['Year'], data['Percentage'],
                marker='o', linewidth=2, label=race,
                color=race_colors.get(race, '#666666'))

    ax2.set_xlabel('Year', fontsize=12)
    ax2.set_ylabel('% of All Deaths', fontsize=12)
    ax2.set_title('Overdose Deaths by Race/Ethnicity Over Time (Proportional)',
                  fontsize=13, fontweight='bold')
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('results/03_demographic_shifts/race_trends.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Saved: race_trends.png")

    # === 4. Race by substance analysis ===
    print("Analyzing race-substance patterns...")

    # For key substances, show racial breakdown over time
    key_substances = ['Fentanyl', 'Heroin', 'Methamphetamine', 'Cocaine']

    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    axes = axes.flatten()

    for idx, substance in enumerate(key_substances):
        df_sub = df[df[substance] == 1]
        race_sub = df_sub.groupby(['Year', 'Race']).size().reset_index(name='Deaths')

        for race in ['WHITE', 'LATINE', 'BLACK', 'ASIAN']:
            data = race_sub[race_sub['Race'] == race]
            axes[idx].plot(data['Year'], data['Deaths'],
                          marker='o', linewidth=2, label=race,
                          color=race_colors.get(race, '#666666'))

        axes[idx].set_xlabel('Year', fontsize=11)
        axes[idx].set_ylabel('Number of Deaths', fontsize=11)
        axes[idx].set_title(f'{substance} Deaths by Race/Ethnicity', fontsize=12, fontweight='bold')
        axes[idx].legend(fontsize=9)
        axes[idx].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('results/03_demographic_shifts/race_by_substance.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Saved: race_by_substance.png")

    # === 5. Gender analysis ===
    print("Analyzing gender patterns...")

    if 'Gender' in df.columns:
        # Clean gender data
        df['Gender'] = df['Gender'].str.upper().str.strip()

        # Standardize gender values: F → FEMALE, M → MALE
        df['Gender'] = df['Gender'].map({
            'F': 'FEMALE',
            'M': 'MALE',
            'FEMALE': 'FEMALE',
            'MALE': 'MALE'
        })

        # Annual gender breakdown
        gender_annual = df.groupby(['Year', 'Gender']).size().reset_index(name='Deaths')
        gender_totals = df.groupby('Year').size().reset_index(name='Total')
        gender_annual = gender_annual.merge(gender_totals, on='Year')
        gender_annual['Percentage'] = (gender_annual['Deaths'] / gender_annual['Total']) * 100

        gender_annual.to_csv('results/03_demographic_shifts/gender_trends_annual.csv', index=False)

        # Plot
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

        for gender in ['MALE', 'FEMALE']:
            if gender in gender_annual['Gender'].values:
                data = gender_annual[gender_annual['Gender'] == gender]
                color = '#00468B' if gender == 'MALE' else '#ED0000'
                ax1.plot(data['Year'], data['Deaths'],
                        marker='o', linewidth=2, label=gender, color=color)
                ax2.plot(data['Year'], data['Percentage'],
                        marker='o', linewidth=2, label=gender, color=color)

        ax1.set_xlabel('Year', fontsize=12)
        ax1.set_ylabel('Number of Deaths', fontsize=12)
        ax1.set_title('Overdose Deaths by Gender (Absolute)', fontsize=13, fontweight='bold')
        ax1.legend(fontsize=11)
        ax1.grid(True, alpha=0.3)

        ax2.set_xlabel('Year', fontsize=12)
        ax2.set_ylabel('% of All Deaths', fontsize=12)
        ax2.set_title('Overdose Deaths by Gender (Proportional)', fontsize=13, fontweight='bold')
        ax2.legend(fontsize=11)
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig('results/03_demographic_shifts/gender_trends.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("Saved: gender_trends.png")

        # Gender by substance
        gender_substance = []
        for substance in substance_cols:
            for year in sorted(df['Year'].unique()):
                year_data = df[(df['Year'] == year) & (df[substance] == 1)]
                for gender in ['MALE', 'FEMALE']:
                    count = (year_data['Gender'] == gender).sum()
                    if count > 0:
                        gender_substance.append({
                            'Year': year,
                            'Substance': substance,
                            'Gender': gender,
                            'Deaths': count
                        })

        gender_sub_df = pd.DataFrame(gender_substance)
        gender_sub_df.to_csv('results/03_demographic_shifts/gender_by_substance.csv', index=False)

    # Print key findings
    print("\n" + "="*60)
    print("KEY FINDINGS:")
    print("="*60)

    year_2012 = age_annual[age_annual['Year'] == 2012].iloc[0]
    year_2023 = age_annual[age_annual['Year'] == 2023].iloc[0]

    print(f"\n1. Age trends:")
    print(f"   2012: Mean = {year_2012['Mean_Age']:.1f} years")
    print(f"   2023: Mean = {year_2023['Mean_Age']:.1f} years")
    print(f"   Change: {year_2023['Mean_Age'] - year_2012['Mean_Age']:+.1f} years")

    print(f"\n2. Racial composition (2023):")
    race_2023 = race_annual[race_annual['Year'] == 2023].sort_values('Percentage', ascending=False)
    for _, row in race_2023.iterrows():
        print(f"   {row['Race']}: {row['Deaths']:.0f} ({row['Percentage']:.1f}%)")

    if 'Gender' in df.columns:
        print(f"\n3. Gender distribution (2023):")
        gender_2023 = gender_annual[gender_annual['Year'] == 2023].sort_values('Percentage', ascending=False)
        for _, row in gender_2023.head(2).iterrows():
            if pd.notna(row['Gender']):
                print(f"   {row['Gender']}: {row['Deaths']:.0f} ({row['Percentage']:.1f}%)")

    print("\n" + "="*60)
    print("Analysis complete!")

if __name__ == "__main__":
    main()
