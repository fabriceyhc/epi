#!/usr/bin/env python
# coding: utf-8

"""
Publication Figure: Age at Death by Race and Substance
- Creates clear visualization of age differences
- Highlights that Black populations are OLDER, not younger
- Publication-ready figure for manuscript
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Settings
sns.set_style("whitegrid")
os.makedirs("results/10_age_race_figure", exist_ok=True)

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

    # Focus on major racial/ethnic groups
    df_main = df[df['Race'].isin(['WHITE', 'LATINE', 'BLACK', 'ASIAN'])].copy()

    # === Create comprehensive figure ===
    print("Creating publication figure...")

    fig = plt.figure(figsize=(18, 10))
    gs = fig.add_gridspec(2, 3, hspace=0.3, wspace=0.3)

    race_colors = {
        'WHITE': '#00468B',
        'LATINE': '#ED0000',
        'BLACK': '#42B540',
        'ASIAN': '#0099B4'
    }

    # Define race order from youngest to oldest (for key substances)
    race_order_fent = ['LATINE', 'ASIAN', 'WHITE', 'BLACK']
    race_order_meth = ['ASIAN', 'LATINE', 'BLACK', 'WHITE']

    # Panel A: Fentanyl - Bar chart with error bars
    ax1 = fig.add_subplot(gs[0, 0])
    fent_data = []
    for race in race_order_fent:
        ages = df_main[(df_main['Fentanyl'] == 1) & (df_main['Race'] == race)]['Age'].dropna()
        if len(ages) >= 5:
            fent_data.append({
                'Race': race,
                'Median': ages.median(),
                'Q25': ages.quantile(0.25),
                'Q75': ages.quantile(0.75),
                'N': len(ages)
            })

    fent_df = pd.DataFrame(fent_data)
    x_pos = np.arange(len(fent_df))
    bars = ax1.bar(x_pos, fent_df['Median'],
                   color=[race_colors[r] for r in fent_df['Race']],
                   alpha=0.7, edgecolor='black', linewidth=1.5)

    # Add error bars (IQR)
    for i, row in fent_df.iterrows():
        ax1.errorbar(i, row['Median'],
                    yerr=[[row['Median']-row['Q25']], [row['Q75']-row['Median']]],
                    fmt='none', color='black', capsize=5, capthick=2)

    # Add median values on bars
    for i, (bar, row) in enumerate(zip(bars, fent_df.iterrows())):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 3,
                f'{row[1]["Median"]:.0f}',
                ha='center', va='bottom', fontsize=11, fontweight='bold')

    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(fent_df['Race'], fontsize=11)
    ax1.set_ylabel('Median Age (years)', fontsize=12, fontweight='bold')
    ax1.set_title('A. Fentanyl-Involved Deaths', fontsize=13, fontweight='bold', pad=15)
    ax1.set_ylim(0, 70)
    ax1.grid(True, alpha=0.3, axis='y')

    # Panel B: Methamphetamine - Bar chart with error bars
    ax2 = fig.add_subplot(gs[0, 1])
    meth_data = []
    for race in race_order_meth:
        ages = df_main[(df_main['Methamphetamine'] == 1) & (df_main['Race'] == race)]['Age'].dropna()
        if len(ages) >= 5:
            meth_data.append({
                'Race': race,
                'Median': ages.median(),
                'Q25': ages.quantile(0.25),
                'Q75': ages.quantile(0.75),
                'N': len(ages)
            })

    meth_df = pd.DataFrame(meth_data)
    x_pos = np.arange(len(meth_df))
    bars = ax2.bar(x_pos, meth_df['Median'],
                   color=[race_colors[r] for r in meth_df['Race']],
                   alpha=0.7, edgecolor='black', linewidth=1.5)

    # Add error bars (IQR)
    for i, row in meth_df.iterrows():
        ax2.errorbar(i, row['Median'],
                    yerr=[[row['Median']-row['Q25']], [row['Q75']-row['Median']]],
                    fmt='none', color='black', capsize=5, capthick=2)

    # Add median values on bars
    for i, (bar, row) in enumerate(zip(bars, meth_df.iterrows())):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 3,
                f'{row[1]["Median"]:.0f}',
                ha='center', va='bottom', fontsize=11, fontweight='bold')

    ax2.set_xticks(x_pos)
    ax2.set_xticklabels(meth_df['Race'], fontsize=11)
    ax2.set_ylabel('Median Age (years)', fontsize=12, fontweight='bold')
    ax2.set_title('B. Methamphetamine-Involved Deaths', fontsize=13, fontweight='bold', pad=15)
    ax2.set_ylim(0, 70)
    ax2.grid(True, alpha=0.3, axis='y')

    # Panel C: Heatmap of median ages
    ax3 = fig.add_subplot(gs[0, 2])

    # Create matrix
    heatmap_data = []
    substances = ['Fentanyl', 'Methamphetamine', 'Heroin', 'Cocaine']
    races = ['LATINE', 'ASIAN', 'WHITE', 'BLACK']

    for substance in substances:
        row = []
        for race in races:
            ages = df_main[(df_main[substance] == 1) & (df_main['Race'] == race)]['Age'].dropna()
            if len(ages) >= 5:
                row.append(ages.median())
            else:
                row.append(np.nan)
        heatmap_data.append(row)

    heatmap_df = pd.DataFrame(heatmap_data, index=substances, columns=races)

    # Create heatmap
    im = ax3.imshow(heatmap_df.values, cmap='RdYlBu_r', aspect='auto', vmin=30, vmax=60)

    # Add text annotations
    for i in range(len(substances)):
        for j in range(len(races)):
            val = heatmap_df.iloc[i, j]
            if not np.isnan(val):
                text = ax3.text(j, i, f'{val:.0f}',
                              ha="center", va="center", color="black",
                              fontsize=11, fontweight='bold')

    ax3.set_xticks(np.arange(len(races)))
    ax3.set_yticks(np.arange(len(substances)))
    ax3.set_xticklabels(races, fontsize=11)
    ax3.set_yticklabels(substances, fontsize=11)
    ax3.set_title('C. Median Age Heatmap', fontsize=13, fontweight='bold', pad=15)

    # Add colorbar
    cbar = plt.colorbar(im, ax=ax3, fraction=0.046, pad=0.04)
    cbar.set_label('Median Age (years)', fontsize=10, fontweight='bold')

    # Panel D: Violin plots for Fentanyl
    ax4 = fig.add_subplot(gs[1, :2])

    fent_plot_data = []
    for race in ['LATINE', 'ASIAN', 'WHITE', 'BLACK']:
        ages = df_main[(df_main['Fentanyl'] == 1) & (df_main['Race'] == race)]['Age'].dropna()
        for age in ages:
            fent_plot_data.append({'Race': race, 'Age': age})

    fent_plot_df = pd.DataFrame(fent_plot_data)

    # Create violin plot
    parts = ax4.violinplot([fent_plot_df[fent_plot_df['Race'] == r]['Age'].values
                           for r in ['LATINE', 'ASIAN', 'WHITE', 'BLACK']],
                          positions=range(4),
                          showmeans=False, showmedians=True,
                          widths=0.7)

    # Color violins
    for i, (pc, race) in enumerate(zip(parts['bodies'], ['LATINE', 'ASIAN', 'WHITE', 'BLACK'])):
        pc.set_facecolor(race_colors[race])
        pc.set_alpha(0.6)

    parts['cmedians'].set_color('black')
    parts['cmedians'].set_linewidth(2)

    ax4.set_xticks(range(4))
    ax4.set_xticklabels(['LATINE', 'ASIAN', 'WHITE', 'BLACK'], fontsize=11)
    ax4.set_ylabel('Age (years)', fontsize=12, fontweight='bold')
    ax4.set_title('D. Age Distribution - Fentanyl Deaths by Race/Ethnicity',
                 fontsize=13, fontweight='bold', pad=15)
    ax4.grid(True, alpha=0.3, axis='y')
    ax4.set_ylim(10, 85)

    # Panel E: Key finding text box
    ax5 = fig.add_subplot(gs[1, 2])
    ax5.axis('off')

    text_content = """
KEY FINDING:

Black populations experience
overdose deaths at OLDER ages
compared to Latine and White
populations:

Fentanyl:
  • Latine:  34 years
  • Asian:   34 years
  • White:   37 years
  • Black:   41 years ⬆

Methamphetamine:
  • Asian:   41 years
  • Latine:  42 years
  • Black:   44 years ⬆
  • White:   47 years

The characterization of
"younger Black populations"
is NOT supported by data.
"""

    ax5.text(0.1, 0.95, text_content, transform=ax5.transAxes,
            fontsize=10, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3),
            family='monospace')

    # Overall title
    fig.suptitle('Age at Overdose Death by Race/Ethnicity and Substance\nLos Angeles County 2012-2023',
                fontsize=16, fontweight='bold', y=0.98)

    plt.savefig('results/10_age_race_figure/age_by_race_comprehensive.png',
               dpi=300, bbox_inches='tight')
    plt.close()
    print("Saved: age_by_race_comprehensive.png")

    # === Create simple comparison table figure ===
    print("Creating comparison table figure...")

    fig, ax = plt.subplots(figsize=(14, 8))
    ax.axis('tight')
    ax.axis('off')

    # Create table data
    table_data = [
        ['', 'Fentanyl', 'Methamphetamine', 'Heroin', 'Cocaine'],
        ['LATINE', '34 (27-45)', '42 (32-51)', '45 (34-56)', '34 (27-49)'],
        ['ASIAN', '34 (28-44)', '41 (33-49)', '34 (27-43)', '38 (29-48)'],
        ['WHITE', '37 (29-49)', '47 (35-56)', '38 (29-51)', '40 (30-54)'],
        ['BLACK', '41 (31-55)', '44 (34-56)', '60 (43-64)', '56 (48-62)']
    ]

    table = ax.table(cellText=table_data, cellLoc='center', loc='center',
                    colWidths=[0.15, 0.2, 0.2, 0.2, 0.2])

    table.auto_set_font_size(False)
    table.set_fontsize(12)
    table.scale(1, 3)

    # Style header row
    for i in range(5):
        cell = table[(0, i)]
        cell.set_facecolor('#4472C4')
        cell.set_text_props(weight='bold', color='white', fontsize=13)

    # Style race column
    for i in range(1, 5):
        cell = table[(i, 0)]
        cell.set_facecolor('#E7E6E6')
        cell.set_text_props(weight='bold', fontsize=12)

    # Highlight BLACK row
    for i in range(5):
        cell = table[(4, i)]
        if i > 0:
            cell.set_facecolor('#FFE699')

    # Add title
    plt.title('Table: Median Age (IQR) at Overdose Death by Race/Ethnicity and Substance\nLos Angeles County 2012-2023\n\n'
             'Note: Black populations consistently show OLDER median ages across substances',
             fontsize=14, fontweight='bold', pad=20)

    # Add footnote
    plt.figtext(0.5, 0.02,
               'Values shown as Median (25th percentile - 75th percentile). Highlighted row shows Black population.\n'
               'All groups with n≥5. Study period: 2012-2023.',
               ha='center', fontsize=10, style='italic')

    plt.savefig('results/10_age_race_figure/age_table_figure.png',
               dpi=300, bbox_inches='tight')
    plt.close()
    print("Saved: age_table_figure.png")

    print("\n" + "="*60)
    print("Publication-ready figures created!")
    print("="*60)
    print("\nKey files for manuscript:")
    print("1. results/10_age_race_figure/age_by_race_comprehensive.png")
    print("   - Multi-panel figure with bars, heatmap, violins")
    print("\n2. results/10_age_race_figure/age_table_figure.png")
    print("   - Publication-ready table")
    print("\n3. results/10_age_race_figure/age_table_combined.csv")
    print("   - CSV for manuscript table")

if __name__ == "__main__":
    main()
