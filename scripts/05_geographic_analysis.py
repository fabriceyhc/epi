#!/usr/bin/env python
# coding: utf-8

"""
Geographic Analysis of Overdoses
- Hotspot mapping by zip code and census tract
- Substance geography (does fentanyl vs meth vary by location?)
- Temporal-spatial analysis (how have hotspots shifted?)
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter

# Settings
sns.set_style("whitegrid")
os.makedirs("results/05_geographic_analysis", exist_ok=True)

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

    substance_cols = ['Heroin', 'Fentanyl', 'Prescription.opioids',
                      'Methamphetamine', 'Cocaine', 'Benzodiazepines', 'Alcohol', 'Others']

    # === 1. Hotspot analysis by ZIP code ===
    print("Analyzing ZIP code hotspots...")

    if 'ZIPCODE' in df.columns:
        # Clean ZIP codes
        df['ZIP'] = df['ZIPCODE'].astype(str).str.replace('.0', '', regex=False)
        df['ZIP'] = df['ZIP'].str.strip()
        df['ZIP'] = df['ZIP'].apply(lambda x: x[:5] if len(x) >= 5 else x)

        # Overall hotspots
        zip_counts = df['ZIP'].value_counts().head(20).reset_index()
        zip_counts.columns = ['ZIP', 'Deaths']

        zip_counts.to_csv('results/05_geographic_analysis/top_20_zip_codes.csv', index=False)

        # Plot top ZIP codes
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.barh(range(len(zip_counts)), zip_counts['Deaths'], color='#ED0000', alpha=0.7)
        ax.set_yticks(range(len(zip_counts)))
        ax.set_yticklabels(zip_counts['ZIP'])
        ax.invert_yaxis()
        ax.set_xlabel('Number of Overdose Deaths', fontsize=12)
        ax.set_ylabel('ZIP Code', fontsize=12)
        ax.set_title('Top 20 ZIP Codes for Overdose Deaths\nLos Angeles County 2012-2023',
                     fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='x')

        plt.tight_layout()
        plt.savefig('results/05_geographic_analysis/top_zip_codes.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("Saved: top_zip_codes.png")

        # === 2. Temporal changes in hotspots ===
        print("Analyzing temporal changes in hotspots...")

        # Top ZIPs in early period vs late period
        df_early = df[df['Year'] <= 2017]
        df_late = df[df['Year'] >= 2018]

        zip_early = df_early['ZIP'].value_counts().head(15)
        zip_late = df_late['ZIP'].value_counts().head(15)

        # Compare
        comparison = pd.DataFrame({
            'ZIP': list(set(zip_early.index) | set(zip_late.index)),
        })
        comparison['Deaths_2012_2017'] = comparison['ZIP'].map(zip_early).fillna(0)
        comparison['Deaths_2018_2024'] = comparison['ZIP'].map(zip_late).fillna(0)
        comparison['Total'] = comparison['Deaths_2012_2017'] + comparison['Deaths_2018_2024']
        comparison = comparison.sort_values('Total', ascending=False).head(15)

        comparison.to_csv('results/05_geographic_analysis/zip_comparison_early_late.csv', index=False)

        # Plot
        fig, ax = plt.subplots(figsize=(12, 8))

        x = np.arange(len(comparison))
        width = 0.35

        ax.barh(x - width/2, comparison['Deaths_2012_2017'], width,
                label='2012-2017', color='#00468B', alpha=0.8)
        ax.barh(x + width/2, comparison['Deaths_2018_2024'], width,
                label='2018-2023', color='#ED0000', alpha=0.8)

        ax.set_yticks(x)
        ax.set_yticklabels(comparison['ZIP'])
        ax.invert_yaxis()
        ax.set_xlabel('Number of Deaths', fontsize=12)
        ax.set_ylabel('ZIP Code', fontsize=12)
        ax.set_title('Overdose Death Hotspots: Early vs Late Period',
                     fontsize=14, fontweight='bold')
        ax.legend(fontsize=11)
        ax.grid(True, alpha=0.3, axis='x')

        plt.tight_layout()
        plt.savefig('results/05_geographic_analysis/zip_temporal_comparison.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("Saved: zip_temporal_comparison.png")

    # === 3. Substance geography ===
    print("Analyzing substance geography...")

    if 'ZIPCODE' in df.columns:
        # For top 10 ZIP codes, show substance breakdown
        top_zips = df['ZIP'].value_counts().head(10).index

        substance_by_zip = []
        for zipcode in top_zips:
            zip_data = df[df['ZIP'] == zipcode]
            total = len(zip_data)

            for substance in substance_cols:
                count = zip_data[substance].sum()
                pct = (count / total * 100) if total > 0 else 0

                substance_by_zip.append({
                    'ZIP': zipcode,
                    'Substance': substance,
                    'Count': count,
                    'Percentage': pct
                })

        substance_zip_df = pd.DataFrame(substance_by_zip)
        substance_zip_df.to_csv('results/05_geographic_analysis/substances_by_zip.csv', index=False)

        # Create heatmap
        pivot = substance_zip_df.pivot(index='ZIP', columns='Substance', values='Percentage')

        fig, ax = plt.subplots(figsize=(12, 8))
        sns.heatmap(pivot, annot=True, fmt='.1f', cmap='RdYlBu_r',
                    cbar_kws={'label': '% of Deaths in ZIP'}, ax=ax)
        ax.set_title('Substance Patterns in Top 10 ZIP Codes\nLos Angeles County 2012-2023',
                     fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel('Substance', fontsize=12)
        ax.set_ylabel('ZIP Code', fontsize=12)

        plt.tight_layout()
        plt.savefig('results/05_geographic_analysis/substance_by_zip_heatmap.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("Saved: substance_by_zip_heatmap.png")

        # === 4. Fentanyl vs Meth geography ===
        print("Comparing fentanyl vs meth geography...")

        # Top ZIPs for each substance
        fentanyl_zips = df[df['Fentanyl'] == 1]['ZIP'].value_counts().head(15)
        meth_zips = df[df['Methamphetamine'] == 1]['ZIP'].value_counts().head(15)

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))

        # Fentanyl
        ax1.barh(range(len(fentanyl_zips)), fentanyl_zips.values, color='#ED0000', alpha=0.7)
        ax1.set_yticks(range(len(fentanyl_zips)))
        ax1.set_yticklabels(fentanyl_zips.index)
        ax1.invert_yaxis()
        ax1.set_xlabel('Number of Fentanyl Deaths', fontsize=11)
        ax1.set_ylabel('ZIP Code', fontsize=11)
        ax1.set_title('Top 15 ZIP Codes for Fentanyl Deaths', fontsize=12, fontweight='bold')
        ax1.grid(True, alpha=0.3, axis='x')

        # Methamphetamine
        ax2.barh(range(len(meth_zips)), meth_zips.values, color='#42B540', alpha=0.7)
        ax2.set_yticks(range(len(meth_zips)))
        ax2.set_yticklabels(meth_zips.index)
        ax2.invert_yaxis()
        ax2.set_xlabel('Number of Methamphetamine Deaths', fontsize=11)
        ax2.set_ylabel('ZIP Code', fontsize=11)
        ax2.set_title('Top 15 ZIP Codes for Methamphetamine Deaths', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3, axis='x')

        plt.tight_layout()
        plt.savefig('results/05_geographic_analysis/fentanyl_vs_meth_geography.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("Saved: fentanyl_vs_meth_geography.png")

    # === 5. Spatial visualization ===
    print("Creating spatial visualizations...")

    if 'lat' in df.columns and 'lon' in df.columns:
        df_geo = df[(df['lat'].notna()) & (df['lon'].notna())].copy()

        # Filter to LA County bounds
        df_geo = df_geo[
            (df_geo['lat'].between(33.7, 34.8)) &
            (df_geo['lon'].between(-118.7, -117.6))
        ]

        if len(df_geo) > 0:
            # Overall heatmap
            fig, ax = plt.subplots(figsize=(12, 10))
            ax.scatter(df_geo['lon'], df_geo['lat'],
                      alpha=0.2, s=0.5, color='#ED0000')
            ax.set_xlabel('Longitude', fontsize=12)
            ax.set_ylabel('Latitude', fontsize=12)
            ax.set_title('All Overdose Deaths - Geographic Distribution\nLos Angeles County 2012-2023',
                        fontsize=14, fontweight='bold')
            ax.set_aspect('equal')

            plt.tight_layout()
            plt.savefig('results/05_geographic_analysis/all_overdoses_map.png', dpi=300, bbox_inches='tight')
            plt.close()
            print("Saved: all_overdoses_map.png")

            # Substance-specific maps
            key_substances = ['Fentanyl', 'Methamphetamine', 'Heroin', 'Cocaine']
            colors = {
                'Fentanyl': '#ED0000',
                'Methamphetamine': '#42B540',
                'Heroin': '#00468B',
                'Cocaine': '#0099B4'
            }

            fig, axes = plt.subplots(2, 2, figsize=(16, 14))
            axes = axes.flatten()

            for idx, substance in enumerate(key_substances):
                sub_data = df_geo[df_geo[substance] == 1]

                axes[idx].scatter(sub_data['lon'], sub_data['lat'],
                                alpha=0.3, s=0.5, color=colors[substance])
                axes[idx].set_xlabel('Longitude', fontsize=11)
                axes[idx].set_ylabel('Latitude', fontsize=11)
                axes[idx].set_title(f'{substance} Deaths - Geographic Distribution',
                                  fontsize=12, fontweight='bold')
                axes[idx].set_aspect('equal')

            plt.tight_layout()
            plt.savefig('results/05_geographic_analysis/substance_specific_maps.png', dpi=300, bbox_inches='tight')
            plt.close()
            print("Saved: substance_specific_maps.png")

            # Temporal comparison - early vs late
            df_geo_early = df_geo[df_geo['Year'] <= 2017]
            df_geo_late = df_geo[df_geo['Year'] >= 2018]

            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8))

            ax1.scatter(df_geo_early['lon'], df_geo_early['lat'],
                       alpha=0.3, s=0.5, color='#00468B')
            ax1.set_xlabel('Longitude', fontsize=11)
            ax1.set_ylabel('Latitude', fontsize=11)
            ax1.set_title('Overdose Deaths 2012-2017', fontsize=13, fontweight='bold')
            ax1.set_aspect('equal')

            ax2.scatter(df_geo_late['lon'], df_geo_late['lat'],
                       alpha=0.3, s=0.5, color='#ED0000')
            ax2.set_xlabel('Longitude', fontsize=11)
            ax2.set_ylabel('Latitude', fontsize=11)
            ax2.set_title('Overdose Deaths 2018-2023', fontsize=13, fontweight='bold')
            ax2.set_aspect('equal')

            plt.tight_layout()
            plt.savefig('results/05_geographic_analysis/temporal_spatial_comparison.png', dpi=300, bbox_inches='tight')
            plt.close()
            print("Saved: temporal_spatial_comparison.png")

    # === 6. Death location analysis ===
    print("Analyzing death locations...")

    if 'DeathPlace' in df.columns:
        death_place_counts = df['DeathPlace'].value_counts().head(10)

        fig, ax = plt.subplots(figsize=(12, 6))
        death_place_counts.plot(kind='barh', ax=ax, color='#ED0000', alpha=0.7)
        ax.set_xlabel('Number of Deaths', fontsize=12)
        ax.set_ylabel('Location Type', fontsize=12)
        ax.set_title('Top 10 Death Locations\nLos Angeles County 2012-2023',
                     fontsize=14, fontweight='bold')
        ax.invert_yaxis()
        ax.grid(True, alpha=0.3, axis='x')

        plt.tight_layout()
        plt.savefig('results/05_geographic_analysis/death_locations.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("Saved: death_locations.png")

    # Print key findings
    print("\n" + "="*60)
    print("KEY FINDINGS:")
    print("="*60)

    if 'ZIPCODE' in df.columns:
        print(f"\n1. Top 5 hotspot ZIP codes (2012-2023):")
        for i, (zipcode, count) in enumerate(zip_counts.head(5).values, 1):
            print(f"   {i}. ZIP {zipcode}: {count:,} deaths")

        print(f"\n2. Geographic shift:")
        early_top = comparison['Deaths_2012_2017'].sum()
        late_top = comparison['Deaths_2018_2024'].sum()
        print(f"   Deaths in top ZIPs 2012-2017: {early_top:,.0f}")
        print(f"   Deaths in top ZIPs 2018-2023: {late_top:,.0f}")
        print(f"   Change: {((late_top/early_top - 1) * 100):+.1f}%")

    print("\n" + "="*60)
    print("Analysis complete!")

if __name__ == "__main__":
    main()
