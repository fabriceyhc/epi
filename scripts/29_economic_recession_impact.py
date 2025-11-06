"""Analysis 29: Economic Recession Impact Analysis"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from fredapi import Fred
from scipy import stats
from pathlib import Path
import os, sys

sys.path.append(str(Path(__file__).parent.parent))
from scripts.utils import load_overdose_data

fred = Fred(api_key=os.getenv('FRED_API_KEY'))
OUTPUT_DIR = Path('results/29_economic_recession_impact')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def main():
    print("="*70)
    print("Analysis 29: Economic Recession Impact")
    print("="*70)

    df = load_overdose_data()
    df = df[(df['Year'] >= 2012) & (df['Year'] <= 2023)].copy()
    print(f"\nLoaded {len(df):,} overdose deaths")

    annual_deaths = df.groupby('Year').size().reset_index(name='Deaths')

    # Define periods
    annual_deaths['Period'] = annual_deaths['Year'].apply(lambda x:
        'Pre-Pandemic (2012-2019)' if x < 2020 else
        'Pandemic (2020-2021)' if x <= 2021 else
        'Post-Pandemic (2022-2023)')

    # Period comparison
    period_stats = annual_deaths.groupby('Period').agg({
        'Deaths': ['mean', 'sum', 'std']
    }).round(1)
    period_stats.to_csv(OUTPUT_DIR / 'period_comparison.csv')
    print("\n✓ Saved: period_comparison.csv")

    # By race
    race_period = df.groupby(['Year', 'Race']).size().reset_index(name='Deaths')
    race_period['Period'] = race_period['Year'].apply(lambda x:
        'Pre-Pandemic' if x < 2020 else 'Pandemic' if x <= 2021 else 'Post-Pandemic')

    race_period_summary = race_period.groupby(['Period', 'Race'])['Deaths'].mean().reset_index()
    race_period_summary.to_csv(OUTPUT_DIR / 'recession_impact_by_race.csv', index=False)
    print("✓ Saved: recession_impact_by_race.csv")

    # Visualization
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    # Period comparison
    period_means = annual_deaths.groupby('Period')['Deaths'].mean()
    axes[0].bar(range(len(period_means)), period_means.values,
               color=['blue', 'red', 'orange'])
    axes[0].set_xticks(range(len(period_means)))
    axes[0].set_xticklabels(period_means.index, rotation=45, ha='right')
    axes[0].set_ylabel('Mean Annual Deaths', fontweight='bold')
    axes[0].set_title('Overdose Deaths by Period', fontweight='bold')
    axes[0].grid(alpha=0.3, axis='y')

    # By race
    pivot = race_period_summary.pivot(index='Race', columns='Period', values='Deaths')
    pivot.plot(kind='bar', ax=axes[1])
    axes[1].set_ylabel('Mean Annual Deaths', fontweight='bold')
    axes[1].set_title('Impact by Race', fontweight='bold')
    axes[1].legend(title='Period', bbox_to_anchor=(1.05, 1))
    axes[1].grid(alpha=0.3, axis='y')

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'recession_period_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Saved: recession_period_comparison.png")

    print("\n" + "="*70)
    print("Analysis complete!")
    print("="*70)

if __name__ == '__main__':
    main()
