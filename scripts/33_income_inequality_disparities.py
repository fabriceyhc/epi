"""Analysis 33: Income Inequality and Disparities"""
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
OUTPUT_DIR = Path('results/33_income_inequality_disparities')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def main():
    print("="*70)
    print("Analysis 33: Income Inequality & Disparities")
    print("="*70)

    df = load_overdose_data()
    df = df[(df['Year'] >= 2012) & (df['Year'] <= 2023)].copy()

    # Load population rates to get disparity ratios
    try:
        pop_rates = pd.read_csv('results/11_population_adjusted_rates/race_rates_annual.csv')
        disparity_by_year = pop_rates[pop_rates['Race'].isin(['BLACK', 'WHITE'])].pivot_table(
            index='Year', columns='Race', values='Rate_per_100k')
        disparity_by_year['Black_White_Ratio'] = disparity_by_year['BLACK'] / disparity_by_year['WHITE']
        print("✓ Calculated Black-White disparity ratios")
    except:
        print("✗ Could not load population rate data")
        disparity_by_year = pd.DataFrame()

    # Fetch Gini
    try:
        gini = fred.get_series('SIPOVGINIUSA', observation_start='2012-01-01', observation_end='2023-12-31')
        if len(gini) > 0:
            gini_annual = gini.resample('Y').mean()
            gini_annual.index = gini_annual.index.year
            disparity_by_year['Gini_Index'] = disparity_by_year.index.map(dict(zip(gini_annual.index, gini_annual.values)))
            print("✓ Fetched Gini index data")
    except:
        print("✗ Could not fetch Gini data")

    if not disparity_by_year.empty:
        disparity_by_year.to_csv(OUTPUT_DIR / 'inequality_disparity_trends.csv')
        print("✓ Saved: inequality_disparity_trends.csv")

        # Correlation if we have Gini
        if 'Gini_Index' in disparity_by_year.columns and 'Black_White_Ratio' in disparity_by_year.columns:
            valid = disparity_by_year[['Gini_Index', 'Black_White_Ratio']].dropna()
            if len(valid) >= 3:
                corr, pval = stats.pearsonr(valid['Gini_Index'], valid['Black_White_Ratio'])
                pd.DataFrame([{'Correlation': corr, 'P_Value': pval}]).to_csv(
                    OUTPUT_DIR / 'inequality_disparity_correlation.csv', index=False)
                print(f"✓ Gini-Disparity correlation: {corr:.3f}, p={pval:.4f}")

        # Plot
        fig, ax = plt.subplots(figsize=(12, 7))
        ax.plot(disparity_by_year.index, disparity_by_year['Black_White_Ratio'],
               'r-o', linewidth=3, markersize=10)
        ax.axhline(1.0, color='black', linestyle='--', linewidth=1)
        ax.set_xlabel('Year', fontsize=12, fontweight='bold')
        ax.set_ylabel('Black/White Overdose Rate Ratio', fontsize=12, fontweight='bold')
        ax.set_title('Racial Disparity Trend (2012-2023)', fontsize=14, fontweight='bold')
        ax.grid(alpha=0.3)
        plt.tight_layout()
        plt.savefig(OUTPUT_DIR / 'disparity_trend.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("✓ Saved: disparity_trend.png")

    print("\n" + "="*70)
    print("Analysis complete!")
    print("="*70)

if __name__ == '__main__':
    main()
