#!/usr/bin/env python
# coding: utf-8

"""
Seasonal Patterns Analysis
- Monthly/seasonal trends in overdoses
- Does seasonality vary by substance?
- Day of week patterns
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import calendar

# Settings
sns.set_style("whitegrid")
os.makedirs("results/06_seasonal_patterns", exist_ok=True)

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

    df = df[df['Date of Death'].notna()].copy()

    df['Year'] = df['Date of Death'].dt.year
    df['Month'] = df['Date of Death'].dt.month
    df['MonthName'] = df['Date of Death'].dt.month_name()
    df['DayOfWeek'] = df['Date of Death'].dt.dayofweek
    df['DayName'] = df['Date of Death'].dt.day_name()
    df['Quarter'] = df['Date of Death'].dt.quarter
    df['Season'] = df['Quarter'].map({1: 'Winter', 2: 'Spring', 3: 'Summer', 4: 'Fall'})

    df = df[df['Year'].between(2012, 2023)]

    substance_cols = ['Heroin', 'Fentanyl', 'Prescription.opioids',
                      'Methamphetamine', 'Cocaine', 'Benzodiazepines', 'Alcohol', 'Others']

    # === 1. Monthly patterns across all years ===
    print("Analyzing monthly patterns...")

    monthly_counts = df.groupby('Month').size().reset_index(name='Deaths')
    monthly_counts['MonthName'] = monthly_counts['Month'].apply(lambda x: calendar.month_abbr[x])

    monthly_counts.to_csv('results/06_seasonal_patterns/monthly_pattern.csv', index=False)

    # Plot
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(monthly_counts['Month'], monthly_counts['Deaths'],
           color='#ED0000', alpha=0.7, edgecolor='black')
    ax.set_xlabel('Month', fontsize=12)
    ax.set_ylabel('Number of Deaths', fontsize=12)
    ax.set_title('Overdose Deaths by Month\nLos Angeles County 2012-2023',
                 fontsize=14, fontweight='bold')
    ax.set_xticks(range(1, 13))
    ax.set_xticklabels(monthly_counts['MonthName'])
    ax.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.savefig('results/06_seasonal_patterns/monthly_pattern.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Saved: monthly_pattern.png")

    # === 2. Seasonal patterns ===
    print("Analyzing seasonal patterns...")

    seasonal_counts = df.groupby('Season').size().reset_index(name='Deaths')
    seasonal_order = ['Winter', 'Spring', 'Summer', 'Fall']
    seasonal_counts['Season'] = pd.Categorical(seasonal_counts['Season'],
                                               categories=seasonal_order, ordered=True)
    seasonal_counts = seasonal_counts.sort_values('Season')

    seasonal_counts.to_csv('results/06_seasonal_patterns/seasonal_pattern.csv', index=False)

    # Plot
    colors_season = {'Winter': '#00468B', 'Spring': '#42B540',
                     'Summer': '#ED0000', 'Fall': '#0099B4'}

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(seasonal_counts['Season'], seasonal_counts['Deaths'],
                  color=[colors_season[s] for s in seasonal_counts['Season']],
                  alpha=0.7, edgecolor='black')
    ax.set_xlabel('Season', fontsize=12)
    ax.set_ylabel('Number of Deaths', fontsize=12)
    ax.set_title('Overdose Deaths by Season\nLos Angeles County 2012-2023',
                 fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.savefig('results/06_seasonal_patterns/seasonal_pattern.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Saved: seasonal_pattern.png")

    # === 3. Monthly trends over time (time series) ===
    print("Creating monthly time series...")

    monthly_ts = df.groupby([df['Date of Death'].dt.to_period('M')]).size().reset_index(name='Deaths')
    monthly_ts.columns = ['YearMonth', 'Deaths']
    monthly_ts['Date'] = monthly_ts['YearMonth'].dt.to_timestamp()

    monthly_ts.to_csv('results/06_seasonal_patterns/monthly_timeseries.csv', index=False)

    # Plot
    fig, ax = plt.subplots(figsize=(14, 6))
    ax.plot(monthly_ts['Date'], monthly_ts['Deaths'],
            linewidth=1.5, color='#ED0000', alpha=0.7)

    # Add 12-month rolling average
    monthly_ts['Rolling_Avg'] = monthly_ts['Deaths'].rolling(window=12, center=True).mean()
    ax.plot(monthly_ts['Date'], monthly_ts['Rolling_Avg'],
            linewidth=2.5, color='#00468B', label='12-Month Rolling Average')

    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Number of Deaths', fontsize=12)
    ax.set_title('Monthly Overdose Deaths with Trend\nLos Angeles County 2012-2023',
                 fontsize=14, fontweight='bold')
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('results/06_seasonal_patterns/monthly_timeseries.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Saved: monthly_timeseries.png")

    # === 4. Seasonality by substance ===
    print("Analyzing seasonality by substance...")

    substance_season = []
    for substance in substance_cols:
        for season in seasonal_order:
            season_data = df[df['Season'] == season]
            total = len(season_data)
            count = season_data[substance].sum()
            pct = (count / total * 100) if total > 0 else 0

            substance_season.append({
                'Substance': substance,
                'Season': season,
                'Count': count,
                'Percentage': pct
            })

    substance_season_df = pd.DataFrame(substance_season)
    substance_season_df.to_csv('results/06_seasonal_patterns/substance_by_season.csv', index=False)

    # Create heatmap
    pivot = substance_season_df.pivot(index='Substance', columns='Season', values='Percentage')
    pivot = pivot[seasonal_order]  # Reorder columns

    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(pivot, annot=True, fmt='.1f', cmap='RdYlBu_r',
                cbar_kws={'label': '% of Seasonal Deaths'}, ax=ax)
    ax.set_title('Substance Patterns by Season\nLos Angeles County 2012-2023',
                 fontsize=14, fontweight='bold', pad=20)
    ax.set_xlabel('Season', fontsize=12)
    ax.set_ylabel('Substance', fontsize=12)

    plt.tight_layout()
    plt.savefig('results/06_seasonal_patterns/substance_by_season_heatmap.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Saved: substance_by_season_heatmap.png")

    # === 5. Day of week patterns ===
    print("Analyzing day of week patterns...")

    dow_counts = df.groupby(['DayOfWeek', 'DayName']).size().reset_index(name='Deaths')
    dow_counts = dow_counts.sort_values('DayOfWeek')

    dow_counts.to_csv('results/06_seasonal_patterns/day_of_week_pattern.csv', index=False)

    # Plot
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(dow_counts['DayName'], dow_counts['Deaths'],
           color='#ED0000', alpha=0.7, edgecolor='black')
    ax.set_xlabel('Day of Week', fontsize=12)
    ax.set_ylabel('Number of Deaths', fontsize=12)
    ax.set_title('Overdose Deaths by Day of Week\nLos Angeles County 2012-2023',
                 fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.savefig('results/06_seasonal_patterns/day_of_week_pattern.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Saved: day_of_week_pattern.png")

    # === 6. Weekend vs Weekday ===
    print("Comparing weekend vs weekday...")

    df['IsWeekend'] = df['DayOfWeek'].isin([5, 6]).astype(int)

    weekend_comparison = df.groupby('IsWeekend').size().reset_index(name='Deaths')
    weekend_comparison['Type'] = weekend_comparison['IsWeekend'].map({0: 'Weekday', 1: 'Weekend'})

    # Calculate per-day average
    weekend_comparison['Days'] = weekend_comparison['IsWeekend'].map({0: 5, 1: 2})  # 5 weekdays, 2 weekend days
    weekend_comparison['Avg_Per_Day'] = weekend_comparison['Deaths'] / weekend_comparison['Days']

    weekend_comparison.to_csv('results/06_seasonal_patterns/weekend_vs_weekday.csv', index=False)

    # Plot
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # Total deaths
    ax1.bar(weekend_comparison['Type'], weekend_comparison['Deaths'],
            color=['#00468B', '#ED0000'], alpha=0.7, edgecolor='black')
    ax1.set_ylabel('Total Number of Deaths', fontsize=12)
    ax1.set_title('Total Overdose Deaths: Weekday vs Weekend',
                  fontsize=13, fontweight='bold')
    ax1.grid(True, alpha=0.3, axis='y')

    # Average per day
    ax2.bar(weekend_comparison['Type'], weekend_comparison['Avg_Per_Day'],
            color=['#00468B', '#ED0000'], alpha=0.7, edgecolor='black')
    ax2.set_ylabel('Average Deaths Per Day', fontsize=12)
    ax2.set_title('Average Daily Overdose Deaths: Weekday vs Weekend',
                  fontsize=13, fontweight='bold')
    ax2.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.savefig('results/06_seasonal_patterns/weekend_vs_weekday.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Saved: weekend_vs_weekday.png")

    # === 7. Monthly patterns by year (to see if seasonality is consistent) ===
    print("Analyzing year-by-year seasonality...")

    monthly_by_year = df.groupby(['Year', 'Month']).size().reset_index(name='Deaths')

    fig, ax = plt.subplots(figsize=(14, 8))

    for year in sorted(df['Year'].unique()):
        year_data = monthly_by_year[monthly_by_year['Year'] == year]
        ax.plot(year_data['Month'], year_data['Deaths'],
                marker='o', linewidth=1.5, label=str(year), alpha=0.7)

    ax.set_xlabel('Month', fontsize=12)
    ax.set_ylabel('Number of Deaths', fontsize=12)
    ax.set_title('Monthly Patterns by Year\nLos Angeles County 2012-2023',
                 fontsize=14, fontweight='bold')
    ax.set_xticks(range(1, 13))
    ax.set_xticklabels([calendar.month_abbr[i] for i in range(1, 13)])
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=9)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('results/06_seasonal_patterns/monthly_by_year.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Saved: monthly_by_year.png")

    # Print key findings
    print("\n" + "="*60)
    print("KEY FINDINGS:")
    print("="*60)

    print(f"\n1. Peak month:")
    peak_month = monthly_counts.loc[monthly_counts['Deaths'].idxmax()]
    print(f"   {peak_month['MonthName']}: {peak_month['Deaths']:,} deaths")

    print(f"\n2. Lowest month:")
    low_month = monthly_counts.loc[monthly_counts['Deaths'].idxmin()]
    print(f"   {low_month['MonthName']}: {low_month['Deaths']:,} deaths")

    print(f"\n3. Peak season:")
    peak_season = seasonal_counts.loc[seasonal_counts['Deaths'].idxmax()]
    print(f"   {peak_season['Season']}: {peak_season['Deaths']:,} deaths")

    print(f"\n4. Day of week pattern:")
    peak_day = dow_counts.loc[dow_counts['Deaths'].idxmax()]
    low_day = dow_counts.loc[dow_counts['Deaths'].idxmin()]
    print(f"   Highest: {peak_day['DayName']} ({peak_day['Deaths']:,} deaths)")
    print(f"   Lowest: {low_day['DayName']} ({low_day['Deaths']:,} deaths)")

    print(f"\n5. Weekend vs Weekday (average per day):")
    for _, row in weekend_comparison.iterrows():
        print(f"   {row['Type']}: {row['Avg_Per_Day']:.1f} deaths/day")

    print("\n" + "="*60)
    print("Analysis complete!")

if __name__ == "__main__":
    main()
