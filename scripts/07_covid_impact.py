#!/usr/bin/env python
# coding: utf-8

"""
COVID-19 Pandemic Impact Analysis
- Pre-pandemic vs pandemic vs post-pandemic comparison
- Acceleration of existing trends during lockdowns
- Substance-specific pandemic effects
- Demographic changes during pandemic
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

# Settings
sns.set_style("whitegrid")
os.makedirs("results/07_covid_impact", exist_ok=True)

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
    df['Month'] = df['Date of Death'].dt.month
    df['YearMonth'] = df['Date of Death'].dt.to_period('M')

    df = df[df['Year'].between(2012, 2023)]

    # Define pandemic periods
    # Pre-pandemic: 2012-2019
    # Pandemic: 2020-2021 (height of restrictions and disruption)
    # Post-pandemic: 2022-2023

    df['Period'] = pd.cut(df['Year'],
                          bins=[2011, 2019, 2021, 2023],
                          labels=['Pre-Pandemic (2012-2019)',
                                 'Pandemic (2020-2021)',
                                 'Post-Pandemic (2022-2023)'])

    substance_cols = ['Heroin', 'Fentanyl', 'Prescription.opioids',
                      'Methamphetamine', 'Cocaine', 'Benzodiazepines', 'Alcohol', 'Others']

    # Process Age
    if df['Age'].dtype == 'object':
        df['Age'] = df['Age'].str.extract(r"(\d+\.?\d*)")[0].astype(float)
    else:
        df['Age'] = pd.to_numeric(df['Age'], errors='coerce')

    # === 1. Overall impact - annual deaths ===
    print("Analyzing overall COVID impact...")

    annual_deaths = df.groupby('Year').size().reset_index(name='Deaths')
    annual_deaths.to_csv('results/07_covid_impact/annual_deaths.csv', index=False)

    # Calculate year-over-year growth rate
    annual_deaths['Growth_Rate'] = annual_deaths['Deaths'].pct_change() * 100

    # Plot
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))

    # Absolute numbers with pandemic shading
    ax1.plot(annual_deaths['Year'], annual_deaths['Deaths'],
            marker='o', linewidth=2.5, color='#ED0000', markersize=8)
    ax1.axvspan(2020, 2021, alpha=0.2, color='red', label='Pandemic Period')
    ax1.set_xlabel('Year', fontsize=12)
    ax1.set_ylabel('Number of Deaths', fontsize=12)
    ax1.set_title('Annual Overdose Deaths with COVID-19 Pandemic Period\nLos Angeles County 2012-2023',
                 fontsize=14, fontweight='bold')
    ax1.legend(fontsize=11)
    ax1.grid(True, alpha=0.3)

    # Growth rate
    ax2.bar(annual_deaths['Year'][1:], annual_deaths['Growth_Rate'][1:],
           color=['#00468B' if x < 2020 or x > 2021 else '#ED0000'
                  for x in annual_deaths['Year'][1:]],
           alpha=0.7, edgecolor='black')
    ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
    ax2.axvspan(2020, 2021, alpha=0.2, color='red')
    ax2.set_xlabel('Year', fontsize=12)
    ax2.set_ylabel('Year-over-Year Growth (%)', fontsize=12)
    ax2.set_title('Year-over-Year Growth Rate in Overdose Deaths',
                 fontsize=13, fontweight='bold')
    ax2.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.savefig('results/07_covid_impact/overall_impact.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Saved: overall_impact.png")

    # === 2. Monthly timeline showing pandemic onset ===
    print("Creating detailed pandemic timeline...")

    monthly_ts = df.groupby(df['YearMonth']).size().reset_index(name='Deaths')
    monthly_ts['Date'] = monthly_ts['YearMonth'].dt.to_timestamp()

    # Add COVID events
    covid_events = [
        ('2020-03-01', 'LA County\nStay-at-Home'),
        ('2020-12-01', 'Vaccine\nRollout'),
        ('2021-06-01', 'Restrictions\nLifted')
    ]

    fig, ax = plt.subplots(figsize=(16, 6))

    ax.plot(monthly_ts['Date'], monthly_ts['Deaths'],
           linewidth=1.5, color='#ED0000', alpha=0.8)

    # Add 6-month rolling average
    monthly_ts['Rolling_Avg'] = monthly_ts['Deaths'].rolling(window=6, center=True).mean()
    ax.plot(monthly_ts['Date'], monthly_ts['Rolling_Avg'],
           linewidth=2.5, color='#00468B', label='6-Month Rolling Average')

    # Shade pandemic period
    ax.axvspan(pd.Timestamp('2020-01-01'), pd.Timestamp('2021-12-31'),
              alpha=0.2, color='red', label='Pandemic Period')

    # Add event markers
    for date, label in covid_events:
        ax.axvline(x=pd.Timestamp(date), color='black', linestyle='--', alpha=0.5)
        ax.text(pd.Timestamp(date), ax.get_ylim()[1] * 0.95, label,
               rotation=0, verticalalignment='top', fontsize=9,
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Monthly Deaths', fontsize=12)
    ax.set_title('Detailed Pandemic Timeline of Overdose Deaths\nLos Angeles County 2019-2024',
                fontsize=14, fontweight='bold')
    ax.legend(fontsize=11, loc='upper left')
    ax.grid(True, alpha=0.3)
    ax.set_xlim([pd.Timestamp('2019-01-01'), monthly_ts['Date'].max()])

    plt.tight_layout()
    plt.savefig('results/07_covid_impact/pandemic_timeline.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Saved: pandemic_timeline.png")

    # === 3. Period comparison ===
    print("Comparing pre/during/post pandemic...")

    period_stats = df.groupby('Period', observed=True).agg({
        'CaseNumber': 'count',
        'Age': 'mean'
    }).reset_index()
    period_stats.columns = ['Period', 'Total_Deaths', 'Mean_Age']

    # Calculate annual average for each period
    period_years = {
        'Pre-Pandemic (2012-2019)': 8,
        'Pandemic (2020-2021)': 2,
        'Post-Pandemic (2022-2023)': 2
    }
    period_stats['Annual_Average'] = period_stats.apply(
        lambda row: row['Total_Deaths'] / period_years[row['Period']], axis=1
    )

    period_stats.to_csv('results/07_covid_impact/period_comparison.csv', index=False)

    # Plot
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # Total deaths
    colors = ['#00468B', '#ED0000', '#42B540']
    ax1.bar(period_stats['Period'], period_stats['Total_Deaths'],
           color=colors, alpha=0.7, edgecolor='black')
    ax1.set_ylabel('Total Deaths', fontsize=12)
    ax1.set_title('Total Overdose Deaths by Period', fontsize=13, fontweight='bold')
    ax1.tick_params(axis='x', rotation=15)
    ax1.grid(True, alpha=0.3, axis='y')

    # Annual average
    ax2.bar(period_stats['Period'], period_stats['Annual_Average'],
           color=colors, alpha=0.7, edgecolor='black')
    ax2.set_ylabel('Average Annual Deaths', fontsize=12)
    ax2.set_title('Average Annual Deaths by Period', fontsize=13, fontweight='bold')
    ax2.tick_params(axis='x', rotation=15)
    ax2.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.savefig('results/07_covid_impact/period_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Saved: period_comparison.png")

    # === 4. Substance-specific pandemic effects ===
    print("Analyzing substance-specific pandemic effects...")

    substance_period = []
    for period in ['Pre-Pandemic (2012-2019)', 'Pandemic (2020-2021)', 'Post-Pandemic (2022-2023)']:
        period_data = df[df['Period'] == period]
        total = len(period_data)

        for substance in substance_cols:
            count = period_data[substance].sum()
            pct = (count / total * 100) if total > 0 else 0

            substance_period.append({
                'Period': period,
                'Substance': substance,
                'Count': count,
                'Percentage': pct
            })

    substance_period_df = pd.DataFrame(substance_period)
    substance_period_df.to_csv('results/07_covid_impact/substances_by_period.csv', index=False)

    # Plot
    fig, ax = plt.subplots(figsize=(14, 7))

    x = np.arange(len(substance_cols))
    width = 0.25

    for idx, period in enumerate(['Pre-Pandemic (2012-2019)', 'Pandemic (2020-2021)', 'Post-Pandemic (2022-2023)']):
        period_data = substance_period_df[substance_period_df['Period'] == period]
        ax.bar(x + (idx - 1) * width, period_data['Percentage'],
              width, label=period, color=colors[idx], alpha=0.8)

    ax.set_xlabel('Substance', fontsize=12)
    ax.set_ylabel('% of Period Deaths', fontsize=12)
    ax.set_title('Substance Involvement by Pandemic Period\nLos Angeles County',
                fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(substance_cols, rotation=45, ha='right')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.savefig('results/07_covid_impact/substances_by_period.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Saved: substances_by_period.png")

    # === 5. Polysubstance changes ===
    print("Analyzing polysubstance changes...")

    df['Number_Substances'] = df[substance_cols].sum(axis=1)

    poly_period = df.groupby('Period', observed=True)['Number_Substances'].agg(['mean', 'median', 'std']).reset_index()
    poly_period.to_csv('results/07_covid_impact/polysubstance_by_period.csv', index=False)

    fig, ax = plt.subplots(figsize=(12, 6))

    x = np.arange(len(poly_period))
    ax.bar(x, poly_period['mean'], color=colors, alpha=0.7, edgecolor='black', yerr=poly_period['std'],
          capsize=5)

    ax.set_xticks(x)
    ax.set_xticklabels(poly_period['Period'], rotation=15)
    ax.set_ylabel('Average Number of Substances', fontsize=12)
    ax.set_title('Polysubstance Use by Pandemic Period\nLos Angeles County',
                fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.savefig('results/07_covid_impact/polysubstance_by_period.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Saved: polysubstance_by_period.png")

    # === 6. Demographic changes ===
    print("Analyzing demographic changes during pandemic...")

    # Age by period
    age_period = df.groupby('Period', observed=True)['Age'].agg(['mean', 'median', 'std']).reset_index()

    fig, ax = plt.subplots(figsize=(10, 6))

    x = np.arange(len(age_period))
    ax.bar(x, age_period['mean'], color=colors, alpha=0.7, edgecolor='black', yerr=age_period['std'],
          capsize=5)

    ax.set_xticks(x)
    ax.set_xticklabels(age_period['Period'], rotation=15)
    ax.set_ylabel('Mean Age (years)', fontsize=12)
    ax.set_title('Age of Overdose Victims by Pandemic Period\nLos Angeles County',
                fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.savefig('results/07_covid_impact/age_by_period.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Saved: age_by_period.png")

    # === 7. Acceleration analysis ===
    print("Analyzing trend acceleration...")

    # Compare growth rates
    pre_pandemic_years = df[df['Year'].between(2017, 2019)].groupby('Year').size()
    pandemic_years = df[df['Year'].between(2020, 2021)].groupby('Year').size()

    pre_pandemic_growth = pre_pandemic_years.pct_change().mean() * 100
    pandemic_growth = pandemic_years.pct_change().iloc[-1] * 100  # 2020 to 2021

    # Print key findings
    print("\n" + "="*60)
    print("KEY FINDINGS:")
    print("="*60)

    print(f"\n1. Overall impact:")
    for _, row in period_stats.iterrows():
        print(f"   {row['Period']}:")
        print(f"      Total: {row['Total_Deaths']:,.0f} deaths")
        print(f"      Annual average: {row['Annual_Average']:.0f} deaths/year")

    # Calculate percent increase
    pre_pandemic_avg = period_stats[period_stats['Period'] == 'Pre-Pandemic (2012-2019)']['Annual_Average'].values[0]
    pandemic_avg = period_stats[period_stats['Period'] == 'Pandemic (2020-2021)']['Annual_Average'].values[0]
    post_pandemic_avg = period_stats[period_stats['Period'] == 'Post-Pandemic (2022-2023)']['Annual_Average'].values[0]

    print(f"\n2. Changes from pre-pandemic baseline:")
    print(f"   During pandemic: {((pandemic_avg / pre_pandemic_avg - 1) * 100):+.1f}%")
    print(f"   Post-pandemic: {((post_pandemic_avg / pre_pandemic_avg - 1) * 100):+.1f}%")

    print(f"\n3. Biggest substance increases during pandemic:")
    pre_sub = substance_period_df[substance_period_df['Period'] == 'Pre-Pandemic (2012-2019)'].set_index('Substance')
    pan_sub = substance_period_df[substance_period_df['Period'] == 'Pandemic (2020-2021)'].set_index('Substance')

    changes = []
    for substance in substance_cols:
        change = pan_sub.loc[substance, 'Percentage'] - pre_sub.loc[substance, 'Percentage']
        changes.append((substance, change))

    changes.sort(key=lambda x: x[1], reverse=True)
    for substance, change in changes[:3]:
        print(f"   {substance}: {change:+.1f} percentage points")

    print(f"\n4. Polysubstance complexity:")
    for _, row in poly_period.iterrows():
        print(f"   {row['Period']}: {row['mean']:.2f} substances per death")

    print("\n" + "="*60)
    print("Analysis complete!")

if __name__ == "__main__":
    main()
