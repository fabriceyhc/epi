"""
Analysis 51b: ZIP-Level Panel Regression - Within-ZIP Effects

ADDRESSING USER'S CONCERN:
  "Since both are trending variables, the correlation may be coincidental.
   Is there data for individual zip codes to show changes in rent prices
   over time vs overdoses that occurred in those zipcodes?"

NOW WE HAVE ZIP-LEVEL RENT DATA!

This analysis tests:
  1. BETWEEN-ZIP: Do high-rent ZIPs have more overdoses than low-rent ZIPs?
  2. WITHIN-ZIP: Does rent INCREASE in ZIP X predict overdose INCREASE in ZIP X?

Method: Panel regression with ZIP and year fixed effects
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
print("ZIP-LEVEL PANEL REGRESSION: Within-ZIP vs Between-ZIP Effects")
print("=" * 80)
print()

output_dir = Path('results/51_rent_spatial_panel_analysis')
output_dir.mkdir(parents=True, exist_ok=True)

# ============================================================================
# LOAD DATA
# ============================================================================

print("Loading data...")

# ZIP-level rent
rent_df = pd.read_csv('data/zip_rent_panel_clean.csv')
print(f"✓ Rent data: {len(rent_df)} ZIP-year observations")
print(f"  ZIPs: {rent_df['ZIP'].nunique()}, Years: {rent_df['Year'].nunique()}")

# Overdose deaths by ZIP-year
import sys
sys.path.append('scripts')
from utils import load_overdose_data

df = load_overdose_data()
df = df[df['Year'].between(2012, 2022)].copy()  # Match rent data years

# Clean ZIP codes
df['ZIP'] = df['DeathZip'].astype(str).str.split(',').str[0].str.strip().str.split('.').str[0]
df['ZIP'] = pd.to_numeric(df['ZIP'], errors='coerce')
df = df[(df['ZIP'] >= 90001) & (df['ZIP'] <= 93599)]

# Create ZIP-year panel
deaths_zip_year = df.groupby(['ZIP', 'Year']).size().reset_index(name='Deaths')
print(f"✓ Death data: {len(deaths_zip_year)} ZIP-year observations")

# Load population (approximate - use county-wide for now, ideally would have ZIP-level)
pop_data = pd.read_csv('data/la_county_population_census.csv')
pop_df = pop_data.melt(id_vars=['Year'], var_name='Race', value_name='Population')
county_pop = pop_df.groupby('Year')['Population'].sum().reset_index()

# Merge all data
panel = deaths_zip_year.merge(rent_df[['ZIP', 'Year', 'Median_Rent']], on=['ZIP', 'Year'], how='inner')

print(f"✓ Merged panel: {len(panel)} ZIP-year observations")
print(f"  ZIPs: {panel['ZIP'].nunique()}, Years: {panel['Year'].nunique()}")
print()

# We don't have ZIP-level population, so calculate rate using county average
# This is a limitation - ideally would have ZIP-specific population
avg_pop_per_zip = county_pop.merge(panel.groupby('Year')['ZIP'].nunique().reset_index(name='N_ZIPs'), on='Year')
avg_pop_per_zip['Avg_Pop_Per_ZIP'] = avg_pop_per_zip['Population'] / avg_pop_per_zip['N_ZIPs']

panel = panel.merge(avg_pop_per_zip[['Year', 'Avg_Pop_Per_ZIP']], on='Year')
panel['Rate_per_100k'] = (panel['Deaths'] / panel['Avg_Pop_Per_ZIP']) * 100000

print("LIMITATION: Using county-average population per ZIP")
print("  (Ideal: ZIP-specific population from Census)")
print()

# ============================================================================
# DESCRIPTIVE STATISTICS
# ============================================================================

print("=" * 80)
print("DESCRIPTIVE STATISTICS")
print("=" * 80)
print()

print("Panel structure:")
print(f"  Observations: {len(panel)}")
print(f"  ZIPs: {panel['ZIP'].nunique()}")
print(f"  Years: {panel['Year'].nunique()}")
print(f"  Avg observations per ZIP: {len(panel) / panel['ZIP'].nunique():.1f}")
print()

print("Summary statistics:")
print(panel[['Median_Rent', 'Deaths', 'Rate_per_100k']].describe().round(1))
print()

# ============================================================================
# ANALYSIS 1: AGGREGATE CORRELATION (Baseline)
# ============================================================================

print("=" * 80)
print("ANALYSIS 1: AGGREGATE CORRELATION (What We've Been Doing)")
print("=" * 80)
print()

# Aggregate by year
annual_agg = panel.groupby('Year').agg({
    'Median_Rent': 'mean',
    'Deaths': 'sum',
    'Rate_per_100k': 'mean'
}).reset_index()

r_agg, p_agg = stats.pearsonr(annual_agg['Median_Rent'], annual_agg['Rate_per_100k'])

print("Annual aggregate correlation:")
print(f"  r = {r_agg:+.3f} (p = {p_agg:.4f})")
print()
print("  THIS IS THE SPURIOUS CORRELATION USER IS CONCERNED ABOUT")
print("  (Both trending upward - could be coincidental)")
print()

# ============================================================================
# ANALYSIS 2: BETWEEN-ZIP VARIATION
# ============================================================================

print("=" * 80)
print("ANALYSIS 2: BETWEEN-ZIP VARIATION")
print("=" * 80)
print()

print("Do high-rent ZIPs have more overdoses than low-rent ZIPs?")
print()

# Calculate ZIP-level averages (across all years)
zip_avg = panel.groupby('ZIP').agg({
    'Median_Rent': 'mean',
    'Rate_per_100k': 'mean'
}).reset_index()

r_between, p_between = stats.pearsonr(zip_avg['Median_Rent'], zip_avg['Rate_per_100k'])

print(f"Between-ZIP correlation: r = {r_between:+.3f} (p = {p_between:.4f})")
print()

if p_between < 0.05:
    if r_between > 0:
        print("✓ HIGH-rent ZIPs have MORE overdoses")
    else:
        print("✓ HIGH-rent ZIPs have FEWER overdoses")
else:
    print("✗ No significant between-ZIP relationship")
print()

# ============================================================================
# ANALYSIS 3: WITHIN-ZIP VARIATION (THE KEY TEST)
# ============================================================================

print("=" * 80)
print("ANALYSIS 3: WITHIN-ZIP VARIATION (Addresses User's Concern)")
print("=" * 80)
print()

print("Does rent INCREASE in ZIP X predict overdose INCREASE in ZIP X?")
print()
print("Method: Demean by ZIP (remove ZIP-specific average)")
print("  This controls for time-invariant ZIP characteristics")
print()

# Demean by ZIP
panel['Rent_Demeaned'] = panel.groupby('ZIP')['Median_Rent'].transform(lambda x: x - x.mean())
panel['Rate_Demeaned'] = panel.groupby('ZIP')['Rate_per_100k'].transform(lambda x: x - x.mean())

# Correlation of demeaned variables
r_within, p_within = stats.pearsonr(panel['Rent_Demeaned'], panel['Rate_Demeaned'])

print(f"Within-ZIP correlation: r = {r_within:+.3f} (p = {p_within:.4f})")
print()

if p_within < 0.05:
    if r_within > 0:
        print("✓ SIGNIFICANT: Within-ZIP rent increases PREDICT overdose increases")
        print("  → Relationship is NOT entirely spurious")
        print("  → Year-to-year rent changes in a ZIP correlate with overdose changes")
    else:
        print("✓ SIGNIFICANT: Within-ZIP rent increases PREDICT overdose DECREASES")
        print("  → Negative relationship (protective effect)")
else:
    print("✗ NOT SIGNIFICANT: Within-ZIP rent changes do NOT predict overdose changes")
    print("  → SUPPORTS user's concern about spurious correlation")
    print("  → Aggregate correlation WAS driven by cross-sectional differences, not within-ZIP dynamics")
print()

# ============================================================================
# ANALYSIS 4: FIXED EFFECTS REGRESSION
# ============================================================================

print("=" * 80)
print("ANALYSIS 4: FIXED EFFECTS REGRESSION (Gold Standard)")
print("=" * 80)
print()

print("Model: Rate = β₁*Rent + ZIP_FE + Year_FE + ε")
print()
print("  ZIP_FE: Controls for time-invariant ZIP characteristics")
print("  Year_FE: Controls for county-wide time trends")
print("  β₁: Estimates within-ZIP effect of rent on overdoses")
print()

# Create dummy variables
panel_fe = panel.copy()
panel_fe['ZIP'] = panel_fe['ZIP'].astype(str)

# Dummy code (equivalent to fixed effects)
zip_dummies = pd.get_dummies(panel_fe['ZIP'], prefix='ZIP', drop_first=True)
year_dummies = pd.get_dummies(panel_fe['Year'], prefix='Year', drop_first=True)

# Combine
X_fe = pd.concat([
    panel_fe[['Median_Rent']],
    zip_dummies,
    year_dummies
], axis=1)

y_fe = panel_fe['Rate_per_100k']

# Fit model
model_fe = LinearRegression()
model_fe.fit(X_fe, y_fe)

# Extract rent coefficient
rent_coef = model_fe.coef_[0]
r2_fe = model_fe.score(X_fe, y_fe)

print(f"Results:")
print(f"  Rent coefficient (β₁): {rent_coef:+.6f}")
print(f"  R²: {r2_fe:.4f}")
print()

print("Interpretation:")
if abs(rent_coef) > 0.001:
    print(f"  A $100 rent increase → {rent_coef * 100:+.3f} change in overdose rate per 100k")
    if rent_coef > 0:
        print("  ✓ Positive effect: Higher rent → More overdoses (within ZIP)")
    else:
        print("  ✓ Negative effect: Higher rent → Fewer overdoses (within ZIP)")
else:
    print("  ✗ Effect size very small (near zero)")
    print("  ✗ Rent changes do NOT meaningfully predict overdose changes within ZIPs")
print()

# ============================================================================
# COMPARISON OF EFFECTS
# ============================================================================

print("=" * 80)
print("SUMMARY: COMPARISON OF EFFECTS")
print("=" * 80)
print()

results_df = pd.DataFrame([
    {'Analysis': 'Aggregate (Time-Series)', 'Correlation': r_agg, 'P_Value': p_agg,
     'Interpretation': 'Spurious (both trending)'},
    {'Analysis': 'Between-ZIP (Cross-Sectional)', 'Correlation': r_between, 'P_Value': p_between,
     'Interpretation': 'High-rent ZIPs vs low-rent ZIPs'},
    {'Analysis': 'Within-ZIP (Panel)', 'Correlation': r_within, 'P_Value': p_within,
     'Interpretation': 'Rent increases within same ZIP'},
])

print(results_df.to_string(index=False))
print()

print("KEY FINDING:")
print()

if abs(r_within) < abs(r_agg) * 0.3:
    print("  ✓ USER'S CONCERN VALIDATED")
    print(f"    - Aggregate correlation (r={r_agg:.3f}) was LARGELY SPURIOUS")
    print(f"    - Within-ZIP correlation (r={r_within:.3f}) is MUCH WEAKER")
    print(f"    - Reduction: {(1 - abs(r_within)/abs(r_agg))*100:.0f}%")
    print()
    print("  → Most of the correlation WAS due to shared time trends")
    print("  → Rent changes within a ZIP do NOT strongly predict overdose changes")
elif p_within > 0.05:
    print("  ✓ USER'S CONCERN VALIDATED")
    print(f"    - Aggregate correlation (r={r_agg:.3f}) was SPURIOUS")
    print(f"    - Within-ZIP correlation (r={r_within:.3f}) is NOT significant (p={p_within:.3f})")
    print()
    print("  → Rent changes within a ZIP do NOT predict overdose changes")
    print("  → Aggregate correlation driven by other factors (fentanyl supply)")
else:
    print("  ✗ USER'S CONCERN PARTIALLY ADDRESSED")
    print(f"    - Aggregate correlation: r={r_agg:.3f}")
    print(f"    - Within-ZIP correlation: r={r_within:.3f} (p={p_within:.4f})")
    print(f"    - Reduction: {(1 - abs(r_within)/abs(r_agg))*100:.0f}%")
    print()
    print("  → Part of correlation IS spurious (shared trends)")
    print("  → But within-ZIP rent changes DO predict some overdose variation")

print()

# ============================================================================
# VISUALIZATION
# ============================================================================

print("Creating visualizations...")

fig = plt.figure(figsize=(18, 12))
gs = fig.add_gridspec(3, 3, hspace=0.35, wspace=0.35)

# Panel 1: Aggregate time-series
ax1 = fig.add_subplot(gs[0, 0])
ax1.scatter(annual_agg['Median_Rent'], annual_agg['Rate_per_100k'],
            c=annual_agg['Year'], cmap='viridis', s=200, edgecolor='black', linewidth=2)
z = np.polyfit(annual_agg['Median_Rent'], annual_agg['Rate_per_100k'], 1)
p_plot = np.poly1d(z)
ax1.plot(annual_agg['Median_Rent'], p_plot(annual_agg['Median_Rent']),
         "r--", alpha=0.8, linewidth=2.5)
ax1.set_xlabel('Avg Median Rent ($)', fontsize=11, fontweight='bold')
ax1.set_ylabel('Avg Overdose Rate per 100k', fontsize=11, fontweight='bold')
ax1.set_title(f'AGGREGATE (Time-Series)\\nr = {r_agg:.3f} (SPURIOUS?)',
              fontsize=12, fontweight='bold', color='darkred')
ax1.grid(True, alpha=0.3)

# Panel 2: Between-ZIP
ax2 = fig.add_subplot(gs[0, 1])
ax2.scatter(zip_avg['Median_Rent'], zip_avg['Rate_per_100k'],
            alpha=0.5, s=50, color='steelblue', edgecolor='black', linewidth=0.5)
z = np.polyfit(zip_avg['Median_Rent'], zip_avg['Rate_per_100k'], 1)
p_plot = np.poly1d(z)
ax2.plot(zip_avg['Median_Rent'], p_plot(zip_avg['Median_Rent']),
         "r--", alpha=0.8, linewidth=2.5)
ax2.set_xlabel('Avg Median Rent ($)', fontsize=11, fontweight='bold')
ax2.set_ylabel('Avg Overdose Rate per 100k', fontsize=11, fontweight='bold')
ax2.set_title(f'BETWEEN-ZIP (Cross-Sectional)\\nr = {r_between:.3f}',
              fontsize=12, fontweight='bold', color='darkblue')
ax2.grid(True, alpha=0.3)

# Panel 3: Within-ZIP
ax3 = fig.add_subplot(gs[0, 2])
ax3.scatter(panel['Rent_Demeaned'], panel['Rate_Demeaned'],
            alpha=0.3, s=30, color='coral', edgecolor='none')
z = np.polyfit(panel['Rent_Demeaned'], panel['Rate_Demeaned'], 1)
p_plot = np.poly1d(z)
ax3.plot(panel['Rent_Demeaned'], p_plot(panel['Rent_Demeaned']),
         "r--", alpha=0.8, linewidth=2.5)
ax3.axhline(0, color='black', linestyle='-', linewidth=0.5, alpha=0.5)
ax3.axvline(0, color='black', linestyle='-', linewidth=0.5, alpha=0.5)
ax3.set_xlabel('Rent (ZIP-demeaned)', fontsize=11, fontweight='bold')
ax3.set_ylabel('Rate (ZIP-demeaned)', fontsize=11, fontweight='bold')
ax3.set_title(f'WITHIN-ZIP (Panel)\\nr = {r_within:.3f} (KEY TEST)',
              fontsize=12, fontweight='bold', color='darkgreen')
ax3.grid(True, alpha=0.3)

# Panel 4: Example ZIPs over time
ax4 = fig.add_subplot(gs[1, :])
example_zips = panel.groupby('ZIP')['Deaths'].sum().nlargest(8).index[:5]
colors_zip = plt.cm.Set2(np.linspace(0, 1, len(example_zips)))

for i, zipcode in enumerate(example_zips):
    zip_data = panel[panel['ZIP'] == zipcode].sort_values('Year')
    ax4.plot(zip_data['Median_Rent'], zip_data['Rate_per_100k'],
             'o-', linewidth=2, markersize=8, label=f'ZIP {zipcode}',
             color=colors_zip[i])

ax4.set_xlabel('Median Rent ($)', fontsize=11, fontweight='bold')
ax4.set_ylabel('Overdose Rate per 100k', fontsize=11, fontweight='bold')
ax4.set_title('Within-ZIP Trajectories (Top 5 ZIPs by deaths)\\nDoes each ZIP move along its own trendline?',
              fontsize=12, fontweight='bold')
ax4.legend(ncol=5, loc='upper left')
ax4.grid(True, alpha=0.3)

# Panel 5: Correlation comparison
ax5 = fig.add_subplot(gs[2, 0])
comparisons = ['Aggregate\\n(Spurious?)', 'Between-ZIP\\n(Cross-Section)', 'Within-ZIP\\n(Panel)']
values = [r_agg, r_between, r_within]
colors_bar = ['darkred', 'darkblue', 'darkgreen']
bars = ax5.bar(comparisons, values, color=colors_bar, alpha=0.7, edgecolor='black', linewidth=2)
ax5.axhline(0, color='black', linestyle='-', linewidth=1)
ax5.set_ylabel('Correlation (r)', fontsize=11, fontweight='bold')
ax5.set_title('Correlation Comparison', fontsize=12, fontweight='bold')
ax5.grid(True, alpha=0.3, axis='y')
for i, (bar, val) in enumerate(zip(bars, values)):
    ax5.text(bar.get_x() + bar.get_width()/2, val + 0.02 * np.sign(val),
             f'{val:.3f}', ha='center', va='bottom' if val > 0 else 'top',
             fontsize=10, fontweight='bold')

# Panel 6: Interpretation
ax6 = fig.add_subplot(gs[2, 1:])
ax6.axis('off')

if abs(r_within) < abs(r_agg) * 0.3 or p_within > 0.05:
    verdict = "✓ USER'S CONCERN VALIDATED"
    color_verdict = 'darkgreen'
    interpretation = f"""
{verdict}

AGGREGATE correlation: r = {r_agg:+.3f} (SPURIOUS)
WITHIN-ZIP correlation: r = {r_within:+.3f} (p = {p_within:.3f})

{"NOT significant" if p_within > 0.05 else f"Reduction: {(1 - abs(r_within)/abs(r_agg))*100:.0f}%"}

CONCLUSION:
• Most/all of aggregate correlation WAS spurious
• Due to shared upward time trends
• Rent changes within a ZIP do NOT predict
  overdose changes in that ZIP
• Fentanyl supply is the primary driver
  (Analysis #49: Supply explains 98.9%)

RECOMMENDATION:
• Do NOT interpret rent-overdose correlation
  as evidence of causation
• Focus on supply-side interventions
• Economic factors may modulate vulnerability
  but do NOT drive exposure
"""
else:
    verdict = "⚠ PARTIAL VALIDATION"
    color_verdict = 'darkorange'
    interpretation = f"""
{verdict}

AGGREGATE correlation: r = {r_agg:+.3f}
WITHIN-ZIP correlation: r = {r_within:+.3f} (p = {p_within:.4f})
Reduction: {(1 - abs(r_within)/abs(r_agg))*100:.0f}%

CONCLUSION:
• PART of aggregate correlation is spurious
  (shared time trends)
• But within-ZIP rent changes DO predict
  some overdose variation
• Relationship exists but is WEAKER than
  aggregate correlation suggests

CONTEXT:
• Fentanyl supply still explains MORE variance
  (Analysis #49: Supply 98.9% vs Demand 93.4%)
• Rent may modulate vulnerability to
  fentanyl exposure
"""

ax6.text(0.05, 0.95, interpretation, transform=ax6.transAxes,
         fontsize=10, verticalalignment='top', fontfamily='monospace',
         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))

plt.suptitle('ZIP-Level Panel Analysis: Addressing Spurious Correlation Concern\\n"Is the rent-overdose correlation coincidental?"',
             fontsize=14, fontweight='bold', y=0.995)

plt.savefig(output_dir / 'zip_panel_regression.png', dpi=300, bbox_inches='tight')
print(f"✓ Saved: {output_dir / 'zip_panel_regression.png'}")
print()

# ============================================================================
# SAVE RESULTS
# ============================================================================

print("Saving results...")

# Save comparison
results_df.to_csv(output_dir / 'panel_regression_results.csv', index=False)
print(f"✓ Saved: {output_dir / 'panel_regression_results.csv'}")

# Save panel data
panel.to_csv(output_dir / 'zip_year_panel_with_rent.csv', index=False)
print(f"✓ Saved: {output_dir / 'zip_year_panel_with_rent.csv'}")

print()
print("=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)
