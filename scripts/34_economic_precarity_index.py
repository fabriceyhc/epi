"""Analysis 34: Economic Precarity Index (Composite)"""
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
OUTPUT_DIR = Path('results/34_economic_precarity_index')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def main():
    print("="*70)
    print("Analysis 34: Economic Precarity Index")
    print("="*70)

    df = load_overdose_data()
    df = df[(df['Year'] >= 2012) & (df['Year'] <= 2023)].copy()
    annual_deaths = df.groupby('Year').size().reset_index(name='Deaths')

    # Fetch multiple indicators
    indicators = {}
    try:
        unemp = fred.get_series('UNRATE', observation_start='2012-01-01', observation_end='2023-12-31')
        annual_unemp = unemp.resample('Y').mean()
        annual_unemp.index = annual_unemp.index.year
        indicators['Unemployment'] = annual_unemp
        print("✓ Fetched unemployment")
    except:
        pass

    try:
        lfpr = fred.get_series('CIVPART', observation_start='2012-01-01', observation_end='2023-12-31')
        annual_lfpr = lfpr.resample('Y').mean()
        annual_lfpr.index = annual_lfpr.index.year
        indicators['LFPR'] = annual_lfpr
        print("✓ Fetched LFPR")
    except:
        pass

    # Merge
    for name, series in indicators.items():
        annual_deaths[name] = annual_deaths['Year'].map(dict(zip(series.index, series.values)))

    # Build composite index (simple average of normalized indicators)
    if len(indicators) >= 2:
        # Normalize each
        for col in indicators.keys():
            if col in annual_deaths.columns:
                if col == 'LFPR':  # Invert: lower LFPR = higher precarity
                    annual_deaths[f'{col}_norm'] = (annual_deaths[col].max() - annual_deaths[col]) / (annual_deaths[col].max() - annual_deaths[col].min()) * 100
                else:  # Higher unemployment = higher precarity
                    annual_deaths[f'{col}_norm'] = (annual_deaths[col] - annual_deaths[col].min()) / (annual_deaths[col].max() - annual_deaths[col].min()) * 100

        # Composite
        norm_cols = [c for c in annual_deaths.columns if c.endswith('_norm')]
        annual_deaths['Economic_Precarity_Index'] = annual_deaths[norm_cols].mean(axis=1)

        annual_deaths.to_csv(OUTPUT_DIR / 'precarity_index.csv', index=False)
        print("✓ Saved: precarity_index.csv")

        # Correlation
        corr, pval = stats.pearsonr(annual_deaths['Economic_Precarity_Index'], annual_deaths['Deaths'])
        pd.DataFrame([{'Correlation': corr, 'P_Value': pval}]).to_csv(
            OUTPUT_DIR / 'precarity_correlation.csv', index=False)
        print(f"✓ Precarity-Deaths correlation: {corr:.3f}, p={pval:.4f}")

        # Plot
        fig, ax1 = plt.subplots(figsize=(14, 8))
        ax1.plot(annual_deaths['Year'], annual_deaths['Economic_Precarity_Index'],
                'purple', marker='o', linewidth=3.5, markersize=10)
        ax1.fill_between(annual_deaths['Year'], 0, annual_deaths['Economic_Precarity_Index'],
                        alpha=0.3, color='purple')
        ax1.set_ylabel('Economic Precarity Index', fontsize=13, fontweight='bold', color='purple')
        ax1.tick_params(axis='y', labelcolor='purple')

        ax2 = ax1.twinx()
        ax2.plot(annual_deaths['Year'], annual_deaths['Deaths'],
                'darkred', marker='s', linewidth=3, markersize=9)
        ax2.set_ylabel('Annual Deaths', color='darkred', fontsize=13, fontweight='bold')
        ax2.tick_params(axis='y', labelcolor='darkred')

        ax1.set_xlabel('Year', fontsize=13, fontweight='bold')
        ax1.set_title('Economic Precarity Index vs Overdose Deaths',
                      fontsize=15, fontweight='bold', pad=20)
        ax1.grid(alpha=0.3)
        plt.tight_layout()
        plt.savefig(OUTPUT_DIR / 'precarity_index_timeseries.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("✓ Saved: precarity_index_timeseries.png")

    print("\n" + "="*70)
    print("Analysis complete!")
    print("="*70)

if __name__ == '__main__':
    main()
