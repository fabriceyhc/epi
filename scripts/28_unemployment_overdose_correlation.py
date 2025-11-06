"""
Analysis 28: Unemployment-Overdose Correlation by Race (Annual Analysis)

Examines the relationship between unemployment rates and overdose deaths.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from fredapi import Fred
from scipy import stats
from pathlib import Path
import os
import sys

sys.path.append(str(Path(__file__).parent.parent))
from scripts.utils import load_overdose_data

fred = Fred(api_key=os.getenv('FRED_API_KEY'))
OUTPUT_DIR = Path('results/28_unemployment_overdose_correlation')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def fetch_fred_safe(series_id, name):
    """Safely fetch FRED series with error handling"""
    try:
        data = fred.get_series(series_id, observation_start='2012-01-01', observation_end='2023-12-31')
        print(f"  ✓ Fetched {name}")
        return data
    except Exception as e:
        print(f"  ✗ Could not fetch {name}: {e}")
        return None

def main():
    print("="*70)
    print("Analysis 28: Unemployment-Overdose Correlation")
    print("="*70)

    # Load overdose data
    df = load_overdose_data()
    df = df[(df['Year'] >= 2012) & (df['Year'] <= 2023)].copy()
    print(f"\nLoaded {len(df):,} overdose deaths (2012-2023)")

    # Annual deaths
    annual_deaths = df.groupby('Year').size().reset_index(name='Deaths')

    # Fetch FRED data
    print("\nFetching economic indicators from FRED...")
    unemployment = fetch_fred_safe('UNRATE', 'National Unemployment')
    ca_unemployment = fetch_fred_safe('CAUR', 'California Unemployment')

    # Process FRED data (annual averages)
    fred_data = {}
    if unemployment is not None:
        annual_unemp = unemployment.resample('Y').mean()
        annual_unemp.index = annual_unemp.index.year
        fred_data['National_Unemployment'] = annual_unemp

    if ca_unemployment is not None:
        annual_ca = ca_unemployment.resample('Y').mean()
        annual_ca.index = annual_ca.index.year
        fred_data['CA_Unemployment'] = annual_ca

    # Merge with deaths
    for name, series in fred_data.items():
        annual_deaths[name] = annual_deaths['Year'].map(dict(zip(series.index, series.values)))

    annual_deaths.to_csv(OUTPUT_DIR / 'annual_unemployment_deaths.csv', index=False)
    print(f"\n✓ Saved: annual_unemployment_deaths.csv")

    # Correlations
    correlations = []
    for col in ['National_Unemployment', 'CA_Unemployment']:
        if col in annual_deaths.columns and annual_deaths[col].notna().sum() >= 5:
            valid = annual_deaths[[col, 'Deaths']].dropna()
            corr, pval = stats.pearsonr(valid[col], valid['Deaths'])
            correlations.append({
                'Indicator': col,
                'Correlation': corr,
                'P_Value': pval,
                'Significant': pval < 0.05
            })

    if correlations:
        corr_df = pd.DataFrame(correlations)
        corr_df.to_csv(OUTPUT_DIR / 'unemployment_correlations.csv', index=False)
        print(f"✓ Saved: unemployment_correlations.csv")
        print("\nCorrelations:")
        print(corr_df)

    # By race analysis
    race_annual = df.groupby(['Year', 'Race']).size().reset_index(name='Deaths')
    if 'CA_Unemployment' in annual_deaths.columns:
        race_unemp = race_annual.merge(
            annual_deaths[['Year', 'CA_Unemployment']],
            on='Year', how='left'
        )
        race_unemp.to_csv(OUTPUT_DIR / 'unemployment_deaths_by_race.csv', index=False)
        print(f"✓ Saved: unemployment_deaths_by_race.csv")

        # Race correlations
        race_corrs = []
        for race in ['WHITE', 'BLACK', 'LATINE', 'ASIAN']:
            race_data = race_unemp[race_unemp['Race'] == race]
            if len(race_data) >= 5:
                corr, pval = stats.pearsonr(race_data['CA_Unemployment'], race_data['Deaths'])
                race_corrs.append({
                    'Race': race,
                    'Correlation': corr,
                    'P_Value': pval,
                    'Significant': pval < 0.05
                })

        if race_corrs:
            race_corr_df = pd.DataFrame(race_corrs)
            race_corr_df.to_csv(OUTPUT_DIR / 'correlations_by_race.csv', index=False)
            print(f"✓ Saved: correlations_by_race.csv")

    # VISUALIZATIONS
    print("\nCreating visualizations...")

    # Plot 1: Time series
    if 'CA_Unemployment' in annual_deaths.columns:
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))

        ax1.plot(annual_deaths['Year'], annual_deaths['CA_Unemployment'],
                'r-o', linewidth=2.5, markersize=8)
        ax1.set_ylabel('Unemployment Rate (%)', fontsize=12, fontweight='bold')
        ax1.set_title('California Unemployment Rate', fontsize=14, fontweight='bold')
        ax1.grid(alpha=0.3)

        ax2.plot(annual_deaths['Year'], annual_deaths['Deaths'],
                'b-s', linewidth=2.5, markersize=8)
        ax2.set_ylabel('Annual Overdose Deaths', fontsize=12, fontweight='bold')
        ax2.set_xlabel('Year', fontsize=12, fontweight='bold')
        ax2.set_title('Overdose Deaths', fontsize=14, fontweight='bold')
        ax2.grid(alpha=0.3)

        plt.tight_layout()
        plt.savefig(OUTPUT_DIR / 'unemployment_deaths_timeseries.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("✓ Saved: unemployment_deaths_timeseries.png")

        # Plot 2: Scatter
        fig, ax = plt.subplots(figsize=(10, 8))
        scatter = ax.scatter(annual_deaths['CA_Unemployment'], annual_deaths['Deaths'],
                           c=annual_deaths['Year'], cmap='viridis', s=200,
                           edgecolors='black', linewidth=2)

        for _, row in annual_deaths.iterrows():
            ax.annotate(int(row['Year']), (row['CA_Unemployment'], row['Deaths']),
                       fontsize=10, ha='center', va='center', fontweight='bold')

        z = np.polyfit(annual_deaths['CA_Unemployment'], annual_deaths['Deaths'], 1)
        p = np.poly1d(z)
        x_line = np.linspace(annual_deaths['CA_Unemployment'].min(),
                            annual_deaths['CA_Unemployment'].max(), 100)
        ax.plot(x_line, p(x_line), "r--", linewidth=2)

        corr, pval = stats.pearsonr(annual_deaths['CA_Unemployment'], annual_deaths['Deaths'])
        ax.text(0.05, 0.95, f'r = {corr:.3f}\np = {pval:.4f}',
               transform=ax.transAxes, fontsize=12, fontweight='bold',
               verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))

        ax.set_xlabel('California Unemployment Rate (%)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Annual Overdose Deaths', fontsize=12, fontweight='bold')
        ax.set_title('Unemployment vs Overdose Deaths (2012-2023)', fontsize=14, fontweight='bold')
        plt.colorbar(scatter, ax=ax, label='Year')
        ax.grid(alpha=0.3)
        plt.tight_layout()
        plt.savefig(OUTPUT_DIR / 'unemployment_deaths_scatter.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("✓ Saved: unemployment_deaths_scatter.png")

    # Plot 3: By race
    if 'race_corr_df' in locals():
        fig, ax = plt.subplots(figsize=(10, 6))
        colors = ['red' if sig else 'gray' for sig in race_corr_df['Significant']]
        bars = ax.bar(race_corr_df['Race'], race_corr_df['Correlation'], color=colors)
        ax.axhline(0, color='black', linewidth=0.5)
        ax.set_ylabel('Correlation Coefficient', fontsize=12, fontweight='bold')
        ax.set_title('Unemployment-Overdose Correlation by Race\n(Red = p < 0.05)',
                     fontsize=14, fontweight='bold')

        for bar, corr, pval in zip(bars, race_corr_df['Correlation'], race_corr_df['P_Value']):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'r={corr:.2f}\np={pval:.3f}',
                   ha='center', va='bottom' if height > 0 else 'top', fontsize=9)

        ax.grid(alpha=0.3, axis='y')
        plt.tight_layout()
        plt.savefig(OUTPUT_DIR / 'correlation_by_race.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("✓ Saved: correlation_by_race.png")

    print("\n" + "="*70)
    print("Analysis complete!")
    print(f"Results saved to: {OUTPUT_DIR}")
    print("="*70)

if __name__ == '__main__':
    main()
