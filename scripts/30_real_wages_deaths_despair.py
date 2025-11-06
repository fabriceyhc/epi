"""Analysis 30: Real Wages vs Deaths of Despair"""
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
OUTPUT_DIR = Path('results/30_real_wages_deaths_despair')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def main():
    print("="*70)
    print("Analysis 30: Real Wages vs Deaths of Despair")
    print("="*70)

    df = load_overdose_data()
    df = df[(df['Year'] >= 2012) & (df['Year'] <= 2023)].copy()
    annual_deaths = df.groupby('Year').size().reset_index(name='Deaths')

    # Fetch real earnings
    try:
        earnings = fred.get_series('LES1252881600Q', observation_start='2012-01-01', observation_end='2023-12-31')
        annual_earnings = earnings.resample('Y').mean()
        annual_earnings.index = annual_earnings.index.year
        annual_deaths['Real_Earnings'] = annual_deaths['Year'].map(dict(zip(annual_earnings.index, annual_earnings.values)))
        print("✓ Fetched real earnings data")
    except:
        print("✗ Could not fetch earnings data")

    # Index to 2012
    if 'Real_Earnings' in annual_deaths.columns:
        baseline_deaths = annual_deaths[annual_deaths['Year'] == 2012]['Deaths'].iloc[0]
        baseline_earnings = annual_deaths[annual_deaths['Year'] == 2012]['Real_Earnings'].iloc[0]
        annual_deaths['Deaths_Index'] = (annual_deaths['Deaths'] / baseline_deaths) * 100
        annual_deaths['Earnings_Index'] = (annual_deaths['Real_Earnings'] / baseline_earnings) * 100

        annual_deaths.to_csv(OUTPUT_DIR / 'wages_deaths_indexed.csv', index=False)
        print("✓ Saved: wages_deaths_indexed.csv")

        # Divergence
        annual_deaths['Divergence'] = annual_deaths['Deaths_Index'] - annual_deaths['Earnings_Index']
        annual_deaths[['Year', 'Deaths_Index', 'Earnings_Index', 'Divergence']].to_csv(
            OUTPUT_DIR / 'deaths_of_despair_divergence.csv', index=False)
        print("✓ Saved: deaths_of_despair_divergence.csv")

        # Correlation
        corr, pval = stats.pearsonr(annual_deaths['Real_Earnings'], annual_deaths['Deaths'])
        print(f"\nCorrelation: {corr:.3f}, p-value: {pval:.4f}")

        # Plot
        fig, ax = plt.subplots(figsize=(14, 8))
        ax.plot(annual_deaths['Year'], annual_deaths['Deaths_Index'],
               'r-o', linewidth=3, markersize=10, label='Overdose Deaths')
        ax.plot(annual_deaths['Year'], annual_deaths['Earnings_Index'],
               'b-s', linewidth=3, markersize=9, label='Real Earnings')
        ax.fill_between(annual_deaths['Year'],
                       annual_deaths['Deaths_Index'],
                       annual_deaths['Earnings_Index'],
                       alpha=0.2, color='orange', label='Divergence')
        ax.axhline(100, color='black', linestyle='--', linewidth=1)
        ax.set_xlabel('Year', fontsize=13, fontweight='bold')
        ax.set_ylabel('Index (2012 = 100)', fontsize=13, fontweight='bold')
        ax.set_title('Deaths of Despair: Divergence\nOverdose Deaths vs Real Earnings',
                     fontsize=15, fontweight='bold', pad=20)
        ax.legend(fontsize=12)
        ax.grid(alpha=0.3)
        plt.tight_layout()
        plt.savefig(OUTPUT_DIR / 'deaths_of_despair_divergence.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("✓ Saved: deaths_of_despair_divergence.png")

    print("\n" + "="*70)
    print("Analysis complete!")
    print("="*70)

if __name__ == '__main__':
    main()
