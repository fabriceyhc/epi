"""
Analysis 51c: Lead-Lag Analysis - Does Rent PRECEDE Overdose Changes?

TEMPORAL PRECEDENCE TEST:
  If rent causes overdoses, rent changes should PRECEDE overdose changes

Tests:
  1. Rent(t-1) → Overdose(t) [rent leads]
  2. Rent(t) → Overdose(t) [contemporaneous]
  3. Overdose(t-1) → Rent(t) [reverse causation test]

Similar to Analysis #53 where polysubstance complexity was strongest
as a LEADING INDICATOR (r = +0.975)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from sklearn.linear_model import LinearRegression
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

plt.style.use('default')
sns.set_palette("husl")

print("=" * 80)
print("LEAD-LAG ANALYSIS: Does Rent Change PRECEDE Overdose Changes?")
print("=" * 80)
print()

output_dir = Path('results/51_rent_spatial_panel_analysis')
output_dir.mkdir(parents=True, exist_ok=True)

# ============================================================================
# LOAD DATA
# ============================================================================

print("Loading ZIP-year panel with rent...")

panel = pd.read_csv('results/51_rent_spatial_panel_analysis/zip_year_panel_with_rent.csv')
print(f"✓ Loaded {len(panel)} ZIP-year observations")
print(f"  ZIPs: {panel['ZIP'].nunique()}, Years: {panel['Year'].min()}-{panel['Year'].max()}")
print()

# ============================================================================
# CREATE LAGGED VARIABLES
# ============================================================================

print("=" * 80)
print("CREATING LAGGED VARIABLES")
print("=" * 80)
print()

# Sort by ZIP and Year
panel = panel.sort_values(['ZIP', 'Year'])

# Create lags within each ZIP
panel['Rent_Lag1'] = panel.groupby('ZIP')['Median_Rent'].shift(1)
panel['Rate_Lag1'] = panel.groupby('ZIP')['Rate_per_100k'].shift(1)

# Create changes (first differences)
panel['Rent_Change'] = panel.groupby('ZIP')['Median_Rent'].diff()
panel['Rate_Change'] = panel.groupby('ZIP')['Rate_per_100k'].diff()

# Create lagged changes
panel['Rent_Change_Lag1'] = panel.groupby('ZIP')['Rent_Change'].shift(1)
panel['Rate_Change_Lag1'] = panel.groupby('ZIP')['Rate_Change'].shift(1)

# Remove rows with missing lags
panel_lag = panel[panel['Rent_Lag1'].notna() & panel['Rate_Lag1'].notna()].copy()

print(f"After creating lags: {len(panel_lag)} observations")
print(f"  (Lost {len(panel) - len(panel_lag)} observations due to lag structure)")
print()

# ============================================================================
# ANALYSIS 1: CONTEMPORANEOUS CORRELATION (Baseline)
# ============================================================================

print("=" * 80)
print("ANALYSIS 1: CONTEMPORANEOUS CORRELATION (Baseline)")
print("=" * 80)
print()

print("Rent(t) × Overdose(t) - Same year")
print()

r_contemp, p_contemp = stats.pearsonr(panel_lag['Median_Rent'], panel_lag['Rate_per_100k'])

print(f"Correlation: r = {r_contemp:+.3f} (p = {p_contemp:.4f})")
print()

# ============================================================================
# ANALYSIS 2: RENT LEADS OVERDOSES
# ============================================================================

print("=" * 80)
print("ANALYSIS 2: RENT LEADS OVERDOSES (Causal Direction)")
print("=" * 80)
print()

print("Rent(t-1) → Overdose(t)")
print("  Does PREVIOUS year's rent predict THIS year's overdoses?")
print()

r_rent_leads, p_rent_leads = stats.pearsonr(panel_lag['Rent_Lag1'], panel_lag['Rate_per_100k'])

print(f"Correlation: r = {r_rent_leads:+.3f} (p = {p_rent_leads:.4f})")
print()

if p_rent_leads < 0.05:
    if abs(r_rent_leads) > abs(r_contemp):
        print("✓ RENT LEADS: Lagged correlation STRONGER than contemporaneous")
        print("  → Rent changes PRECEDE overdose changes")
        print("  → Stronger evidence for causal pathway: Rent → Overdoses")
    else:
        print("✓ RENT LEADS: Significant but weaker than contemporaneous")
        print("  → Some leading effect, but immediate effects stronger")
else:
    print("✗ NO LEADING EFFECT: Previous year rent does not predict current overdoses")

print()

# ============================================================================
# ANALYSIS 3: OVERDOSES LEAD RENT (Reverse Causation Test)
# ============================================================================

print("=" * 80)
print("ANALYSIS 3: OVERDOSES LEAD RENT (Reverse Causation Test)")
print("=" * 80)
print()

print("Overdose(t-1) → Rent(t)")
print("  Do PREVIOUS year's overdoses predict THIS year's rent?")
print()

r_od_leads, p_od_leads = stats.pearsonr(panel_lag['Rate_Lag1'], panel_lag['Median_Rent'])

print(f"Correlation: r = {r_od_leads:+.3f} (p = {p_od_leads:.4f})")
print()

if p_od_leads < 0.05:
    print("⚠ REVERSE CAUSATION DETECTED")
    print("  → Overdoses may CAUSE rent changes")
    print("  → Possible mechanism: Neighborhoods with overdoses → Disinvestment → Rent changes?")
else:
    print("✓ NO REVERSE CAUSATION: Overdoses do not predict future rent")
    print("  → Supports causal direction: Rent → Overdoses (not reverse)")

print()

# ============================================================================
# ANALYSIS 4: CHANGES (First Differences)
# ============================================================================

print("=" * 80)
print("ANALYSIS 4: CHANGES ANALYSIS (First Differences)")
print("=" * 80)
print()

print("Does RENT CHANGE predict OVERDOSE CHANGE?")
print()

# Remove rows with missing changes
panel_changes = panel_lag[panel_lag['Rent_Change'].notna() & panel_lag['Rate_Change'].notna()].copy()

print(f"Observations with changes: {len(panel_changes)}")
print()

# Contemporaneous changes
r_change_contemp, p_change_contemp = stats.pearsonr(panel_changes['Rent_Change'],
                                                      panel_changes['Rate_Change'])

print(f"Rent_Change(t) × Rate_Change(t):")
print(f"  r = {r_change_contemp:+.3f} (p = {p_change_contemp:.4f})")
print()

# Lagged changes
panel_changes_lag = panel_changes[panel_changes['Rent_Change_Lag1'].notna()].copy()

r_change_lag, p_change_lag = stats.pearsonr(panel_changes_lag['Rent_Change_Lag1'],
                                              panel_changes_lag['Rate_Change'])

print(f"Rent_Change(t-1) → Rate_Change(t):")
print(f"  r = {r_change_lag:+.3f} (p = {p_change_lag:.4f})")
print()

if p_change_lag < 0.05:
    print("✓ RENT CHANGE LEADS: Previous rent increase predicts current overdose increase")
    print("  → Temporal precedence established")
else:
    print("✗ NO LAGGED EFFECT: Rent changes do not predict future overdose changes")

print()

# ============================================================================
# ANALYSIS 5: GRANGER CAUSALITY (Simplified)
# ============================================================================

print("=" * 80)
print("ANALYSIS 5: GRANGER CAUSALITY TEST (Simplified)")
print("=" * 80)
print()

print("Does Rent(t-1) predict Overdose(t) BEYOND Overdose(t-1)?")
print()

# Model 1: Overdose(t) ~ Overdose(t-1)
X1 = panel_lag[['Rate_Lag1']].values
y = panel_lag['Rate_per_100k'].values

model1 = LinearRegression()
model1.fit(X1, y)
r2_model1 = model1.score(X1, y)

print(f"Model 1 (AR only): Rate(t) = β*Rate(t-1)")
print(f"  R² = {r2_model1:.4f}")
print()

# Model 2: Overdose(t) ~ Overdose(t-1) + Rent(t-1)
X2 = panel_lag[['Rate_Lag1', 'Rent_Lag1']].values

model2 = LinearRegression()
model2.fit(X2, y)
r2_model2 = model2.score(X2, y)

print(f"Model 2 (+ Rent lag): Rate(t) = β₁*Rate(t-1) + β₂*Rent(t-1)")
print(f"  R² = {r2_model2:.4f}")
print()

# Incremental R²
r2_increment = r2_model2 - r2_model1

print(f"Incremental R² (Rent adds): {r2_increment:.4f} ({r2_increment*100:.2f}%)")
print()

if r2_increment > 0.01:  # Threshold: 1% additional variance
    print("✓ GRANGER CAUSALITY: Rent(t-1) adds predictive power")
    print("  → Rent helps predict future overdoses beyond past overdoses")
    print("  → Evidence for causal pathway: Rent → Overdoses")
else:
    print("✗ NO GRANGER CAUSALITY: Rent does not add predictive power")
    print("  → Past overdoses alone predict future overdoses")

print()

# ============================================================================
# ANALYSIS 6: OPTIMAL LAG LENGTH
# ============================================================================

print("=" * 80)
print("ANALYSIS 6: OPTIMAL LAG LENGTH")
print("=" * 80)
print()

print("Testing multiple lags to find optimal temporal relationship...")
print()

# Create multiple lags
for lag in range(1, 4):
    panel[f'Rent_Lag{lag}'] = panel.groupby('ZIP')['Median_Rent'].shift(lag)

# Test correlations at different lags
lag_results = []

for lag in range(0, 4):
    if lag == 0:
        col = 'Median_Rent'
        label = 't (contemporaneous)'
    else:
        col = f'Rent_Lag{lag}'
        label = f't-{lag}'

    panel_temp = panel[panel[col].notna()].copy()
    r, p = stats.pearsonr(panel_temp[col], panel_temp['Rate_per_100k'])

    lag_results.append({
        'Lag': label,
        'Lag_Value': lag,
        'Correlation': r,
        'P_Value': p,
        'N': len(panel_temp)
    })

lag_df = pd.DataFrame(lag_results)

print("Correlation by Lag:")
print(lag_df.to_string(index=False))
print()

# Find optimal lag
optimal_lag_idx = lag_df['Correlation'].abs().idxmax()
optimal_lag = lag_df.iloc[optimal_lag_idx]

print(f"Optimal lag: {optimal_lag['Lag']}")
print(f"  Correlation: r = {optimal_lag['Correlation']:+.3f}")
print()

# ============================================================================
# SUMMARY COMPARISON
# ============================================================================

print("=" * 80)
print("SUMMARY: LEAD-LAG RELATIONSHIPS")
print("=" * 80)
print()

summary = pd.DataFrame([
    {'Test': 'Rent(t) → Overdose(t)', 'Type': 'Contemporaneous',
     'Correlation': r_contemp, 'P_Value': p_contemp},
    {'Test': 'Rent(t-1) → Overdose(t)', 'Type': 'Rent Leads',
     'Correlation': r_rent_leads, 'P_Value': p_rent_leads},
    {'Test': 'Overdose(t-1) → Rent(t)', 'Type': 'Reverse (OD Leads)',
     'Correlation': r_od_leads, 'P_Value': p_od_leads},
])

print(summary.to_string(index=False))
print()

print("KEY FINDINGS:")
print()

# Determine verdict
if abs(r_rent_leads) > abs(r_contemp) and p_rent_leads < 0.05:
    print("✓ STRONG EVIDENCE FOR CAUSATION:")
    print("  1. Rent changes PRECEDE overdose changes (rent leads)")
    print("  2. Lagged effect STRONGER than contemporaneous")
    print("  3. Temporal precedence established")
elif p_rent_leads < 0.05 and p_od_leads > 0.05:
    print("✓ MODERATE EVIDENCE FOR CAUSATION:")
    print("  1. Rent(t-1) predicts Overdose(t) ✓")
    print("  2. No reverse causation (OD→Rent) ✓")
    print("  3. But contemporaneous effect stronger")
elif p_rent_leads < 0.05 and p_od_leads < 0.05:
    print("⚠ BIDIRECTIONAL RELATIONSHIP:")
    print("  1. Rent predicts future overdoses")
    print("  2. Overdoses predict future rent")
    print("  3. Feedback loop or confounding?")
else:
    print("✗ LIMITED EVIDENCE FOR CAUSATION:")
    print("  1. No significant lagged effects")
    print("  2. Relationship may be contemporaneous only")
    print("  3. Or driven by third variable (fentanyl supply)")

print()

# ============================================================================
# VISUALIZATION
# ============================================================================

print("Creating visualizations...")

fig = plt.figure(figsize=(18, 12))
gs = fig.add_gridspec(3, 3, hspace=0.35, wspace=0.35)

# Panel 1: Contemporaneous
ax1 = fig.add_subplot(gs[0, 0])
ax1.scatter(panel_lag['Median_Rent'], panel_lag['Rate_per_100k'],
            alpha=0.3, s=30, color='steelblue', edgecolor='none')
z = np.polyfit(panel_lag['Median_Rent'], panel_lag['Rate_per_100k'], 1)
p_plot = np.poly1d(z)
ax1.plot(panel_lag['Median_Rent'], p_plot(panel_lag['Median_Rent']),
         "r--", alpha=0.8, linewidth=2.5)
ax1.set_xlabel('Rent(t)', fontsize=11, fontweight='bold')
ax1.set_ylabel('Overdose(t)', fontsize=11, fontweight='bold')
ax1.set_title(f'CONTEMPORANEOUS\\nr = {r_contemp:.3f}',
              fontsize=12, fontweight='bold', color='steelblue')
ax1.grid(True, alpha=0.3)

# Panel 2: Rent leads
ax2 = fig.add_subplot(gs[0, 1])
ax2.scatter(panel_lag['Rent_Lag1'], panel_lag['Rate_per_100k'],
            alpha=0.3, s=30, color='darkgreen', edgecolor='none')
z = np.polyfit(panel_lag['Rent_Lag1'], panel_lag['Rate_per_100k'], 1)
p_plot = np.poly1d(z)
ax2.plot(panel_lag['Rent_Lag1'], p_plot(panel_lag['Rent_Lag1']),
         "r--", alpha=0.8, linewidth=2.5)
ax2.set_xlabel('Rent(t-1)', fontsize=11, fontweight='bold')
ax2.set_ylabel('Overdose(t)', fontsize=11, fontweight='bold')
ax2.set_title(f'RENT LEADS\\nr = {r_rent_leads:.3f}',
              fontsize=12, fontweight='bold', color='darkgreen')
ax2.grid(True, alpha=0.3)

# Panel 3: Overdose leads (reverse)
ax3 = fig.add_subplot(gs[0, 2])
ax3.scatter(panel_lag['Rate_Lag1'], panel_lag['Median_Rent'],
            alpha=0.3, s=30, color='coral', edgecolor='none')
z = np.polyfit(panel_lag['Rate_Lag1'], panel_lag['Median_Rent'], 1)
p_plot = np.poly1d(z)
ax3.plot(panel_lag['Rate_Lag1'], p_plot(panel_lag['Rate_Lag1']),
         "r--", alpha=0.8, linewidth=2.5)
ax3.set_xlabel('Overdose(t-1)', fontsize=11, fontweight='bold')
ax3.set_ylabel('Rent(t)', fontsize=11, fontweight='bold')
ax3.set_title(f'REVERSE (OD Leads)\\nr = {r_od_leads:.3f}',
              fontsize=12, fontweight='bold', color='coral')
ax3.grid(True, alpha=0.3)

# Panel 4: Lag structure
ax4 = fig.add_subplot(gs[1, :])
lags = lag_df['Lag_Value'].values
correlations = lag_df['Correlation'].values
colors_lag = ['steelblue' if lag == 0 else 'darkgreen' for lag in lags]

bars = ax4.bar(lag_df['Lag'], correlations, color=colors_lag, alpha=0.7,
               edgecolor='black', linewidth=2)
ax4.axhline(0, color='black', linestyle='-', linewidth=1)
ax4.set_xlabel('Lag', fontsize=11, fontweight='bold')
ax4.set_ylabel('Correlation (r)', fontsize=11, fontweight='bold')
ax4.set_title('Correlation by Lag: Finding Optimal Temporal Relationship',
              fontsize=12, fontweight='bold')
ax4.grid(True, alpha=0.3, axis='y')

for bar, val in zip(bars, correlations):
    ax4.text(bar.get_x() + bar.get_width()/2, val + 0.02 * np.sign(val),
             f'{val:.3f}', ha='center', va='bottom' if val > 0 else 'top',
             fontsize=10, fontweight='bold')

# Panel 5: Changes scatter
ax5 = fig.add_subplot(gs[2, 0])
ax5.scatter(panel_changes['Rent_Change'], panel_changes['Rate_Change'],
            alpha=0.4, s=40, color='purple', edgecolor='black', linewidth=0.5)
z = np.polyfit(panel_changes['Rent_Change'], panel_changes['Rate_Change'], 1)
p_plot = np.poly1d(z)
ax5.plot(panel_changes['Rent_Change'], p_plot(panel_changes['Rent_Change']),
         "r--", alpha=0.8, linewidth=2.5)
ax5.axhline(0, color='black', linestyle='-', linewidth=0.5)
ax5.axvline(0, color='black', linestyle='-', linewidth=0.5)
ax5.set_xlabel('Rent Change', fontsize=11, fontweight='bold')
ax5.set_ylabel('Rate Change', fontsize=11, fontweight='bold')
ax5.set_title(f'Changes (First Differences)\\nr = {r_change_contemp:.3f}',
              fontsize=12, fontweight='bold')
ax5.grid(True, alpha=0.3)

# Panel 6: Granger causality
ax6 = fig.add_subplot(gs[2, 1])
models = ['AR(1)\\nRate(t-1) only', 'AR(1) + Rent(t-1)\\nAdds lagged rent']
r2_values = [r2_model1, r2_model2]
colors_model = ['lightcoral', 'lightgreen']

bars = ax6.bar(models, r2_values, color=colors_model, alpha=0.7,
               edgecolor='black', linewidth=2)
ax6.set_ylabel('R² (Variance Explained)', fontsize=11, fontweight='bold')
ax6.set_title(f'Granger Causality Test\\nIncremental R² = {r2_increment:.4f}',
              fontsize=12, fontweight='bold')
ax6.set_ylim([0, 1])
ax6.grid(True, alpha=0.3, axis='y')

for bar, val in zip(bars, r2_values):
    ax6.text(bar.get_x() + bar.get_width()/2, val + 0.02,
             f'{val:.4f}', ha='center', va='bottom',
             fontsize=10, fontweight='bold')

# Panel 7: Summary
ax7 = fig.add_subplot(gs[2, 2])
ax7.axis('off')

# Determine verdict for summary
if abs(r_rent_leads) > abs(r_contemp) and p_rent_leads < 0.05:
    verdict = "✓ STRONG CAUSAL EVIDENCE"
    color_verdict = 'darkgreen'
elif p_rent_leads < 0.05 and p_od_leads > 0.05:
    verdict = "✓ MODERATE CAUSAL EVIDENCE"
    color_verdict = 'green'
else:
    verdict = "⚠ LIMITED CAUSAL EVIDENCE"
    color_verdict = 'orange'

summary_text = f"""
{verdict}

TEMPORAL PRECEDENCE:
• Rent(t-1) → OD(t): r={r_rent_leads:.3f} {'✓' if p_rent_leads < 0.05 else '✗'}
• OD(t-1) → Rent(t): r={r_od_leads:.3f} {'✓' if p_od_leads < 0.05 else '✗'}

GRANGER TEST:
• Incremental R²: {r2_increment:.4f}
• {'✓ Adds predictive power' if r2_increment > 0.01 else '✗ No added value'}

OPTIMAL LAG: {optimal_lag['Lag']}
• r = {optimal_lag['Correlation']:.3f}

INTERPRETATION:
{'Rent changes PRECEDE overdoses' if abs(r_rent_leads) > abs(r_contemp) else 'Contemporaneous > Lagged'}
{'No reverse causation' if p_od_leads > 0.05 else 'Bidirectional relationship'}

CONTEXT:
• Fentanyl supply explains 98.9%
• Rent may modulate vulnerability
  but NOT primary driver
"""

ax7.text(0.05, 0.95, summary_text, transform=ax7.transAxes,
         fontsize=9, verticalalignment='top', fontfamily='monospace',
         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))

plt.suptitle('Lead-Lag Analysis: Does Rent Change PRECEDE Overdose Changes?\\nTesting Temporal Precedence for Causation',
             fontsize=14, fontweight='bold', y=0.998)

plt.savefig(output_dir / 'lead_lag_analysis.png', dpi=300, bbox_inches='tight')
print(f"✓ Saved: {output_dir / 'lead_lag_analysis.png'}")
print()

# ============================================================================
# SAVE RESULTS
# ============================================================================

print("Saving results...")

summary.to_csv(output_dir / 'lead_lag_results.csv', index=False)
print(f"✓ Saved: {output_dir / 'lead_lag_results.csv'}")

lag_df.to_csv(output_dir / 'optimal_lag_analysis.csv', index=False)
print(f"✓ Saved: {output_dir / 'optimal_lag_analysis.csv'}")

print()
print("=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)
