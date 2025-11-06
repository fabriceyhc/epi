#!/usr/bin/env python3
"""
Update all analysis scripts to save outputs to standardized numbered folders
"""

import re
from pathlib import Path

# Mapping of scripts to their new output directories
script_updates = {
    '00_descriptive_table_and_plots.py': {
        'old_patterns': [
            r'results/descriptive',
            r'results/raincloud_plots',
            r'output_dir\s*=\s*["\']results/descriptive["\']',
            r'output_dir\s*=\s*["\']results/raincloud_plots["\']',
        ],
        'new_dir': 'results/00_descriptive_statistics'
    },
    '01_fentanyl_crisis_timeline.py': {
        'old_patterns': [
            r'results/fentanyl_timeline',
        ],
        'new_dir': 'results/01_fentanyl_timeline'
    },
    '02_polysubstance_trends.py': {
        'old_patterns': [
            r'results/polysubstance',
        ],
        'new_dir': 'results/02_polysubstance_trends'
    },
    '03_demographic_shifts.py': {
        'old_patterns': [
            r'results/demographics',
        ],
        'new_dir': 'results/03_demographic_shifts'
    },
    '04_homelessness_analysis.py': {
        'old_patterns': [
            r'results/homelessness',
        ],
        'new_dir': 'results/04_homelessness_analysis'
    },
    '05_geographic_analysis.py': {
        'old_patterns': [
            r'results/geographic',
        ],
        'new_dir': 'results/05_geographic_analysis'
    },
    '06_seasonal_patterns.py': {
        'old_patterns': [
            r'results/seasonal',
        ],
        'new_dir': 'results/06_seasonal_patterns'
    },
    '07_covid_impact.py': {
        'old_patterns': [
            r'results/covid_impact',
        ],
        'new_dir': 'results/07_covid_impact'
    },
    '08_geospatial_statistical_analysis.py': {
        'old_patterns': [
            r'results/geospatial_stats',
        ],
        'new_dir': 'results/08_geospatial_statistics'
    },
    '09_race_substance_trends.py': {
        'old_patterns': [
            r'results/race_substance_trends',
        ],
        'new_dir': 'results/09_race_substance_trends'
    },
    '10_age_race_figure.py': {
        'old_patterns': [
            r'results/race_substance_trends',
        ],
        'new_dir': 'results/10_age_race_figure'
    },
    '11_population_adjusted_rates.py': {
        'old_patterns': [
            r'results/population_rates',
        ],
        'new_dir': 'results/11_population_adjusted_rates'
    },
    '12_ses_context_figure.py': {
        'old_patterns': [
            r'results/population_rates',
        ],
        'new_dir': 'results/12_ses_context_figure'
    },
    '13_temporal_correlation_analysis.py': {
        'old_patterns': [
            r'results/population_rates',
        ],
        'new_dir': 'results/13_temporal_correlation'
    },
    '14_years_potential_life_lost.py': {
        'old_patterns': [
            r'results/population_rates',
        ],
        'new_dir': 'results/14_ypll_analysis'
    },
    '15_disparity_decomposition.py': {
        'old_patterns': [
            r'results/population_rates',
        ],
        'new_dir': 'results/15_disparity_decomposition'
    },
    '16_comprehensive_publication_figure.py': {
        'old_patterns': [
            r'results/population_rates',
        ],
        'new_dir': 'results/16_comprehensive_publication'
    },
    '17_real_income_cost_of_living.py': {
        'old_patterns': [
            r'results/population_rates',
        ],
        'new_dir': 'results/17_real_income_analysis'
    },
    '18_age_standardized_rates.py': {
        'old_patterns': [
            r'results/population_rates',
        ],
        'new_dir': 'results/18_age_standardized_rates'
    },
    '19_substance_specific_ses_patterns.py': {
        'old_patterns': [
            r'results/population_rates',
        ],
        'new_dir': 'results/19_substance_specific_ses'
    },
    '20_housing_homelessness_pipeline.py': {
        'old_patterns': [
            r'results/population_rates',
        ],
        'new_dir': 'results/20_housing_homelessness'
    },
    '21_geographic_ses_inequality.py': {
        'old_patterns': [
            r'results/population_rates',
        ],
        'new_dir': 'results/21_geographic_ses_inequality'
    },
    '22_counterfactual_ses_matching.py': {
        'old_patterns': [
            r'results/population_rates',
        ],
        'new_dir': 'results/22_counterfactual_ses_matching'
    },
    '23_covid_economic_shock.py': {
        'old_patterns': [
            r'results/population_rates',
        ],
        'new_dir': 'results/23_covid_economic_shock'
    },
    '24_cumulative_disadvantage.py': {
        'old_patterns': [
            r'results/population_rates',
        ],
        'new_dir': 'results/24_cumulative_disadvantage'
    },
    '25_housing_costs_analysis.py': {
        'old_patterns': [
            r'results/population_rates',
        ],
        'new_dir': 'results/25_housing_costs'
    },
    '26_income_volatility.py': {
        'old_patterns': [
            r'results/population_rates',
        ],
        'new_dir': 'results/26_income_volatility'
    },
    '27_poverty_age_interaction.py': {
        'old_patterns': [
            r'results/population_rates',
        ],
        'new_dir': 'results/27_poverty_age_interaction'
    },
}

print("=" * 70)
print("UPDATING ANALYSIS SCRIPTS TO USE NEW FOLDER STRUCTURE")
print("=" * 70)
print()

scripts_dir = Path('scripts')
updated_count = 0
error_count = 0

for script_name, config in sorted(script_updates.items()):
    script_path = scripts_dir / script_name

    if not script_path.exists():
        print(f"⚠️  {script_name}: File not found, skipping")
        error_count += 1
        continue

    print(f"Processing {script_name}...")

    # Read the script
    with open(script_path, 'r') as f:
        content = f.read()

    # Track if any changes were made
    original_content = content
    changes_made = 0

    # Replace all old patterns with new directory
    for old_pattern in config['old_patterns']:
        # Find all occurrences
        matches = re.findall(old_pattern, content)
        if matches:
            # Replace the pattern
            content = re.sub(old_pattern, config['new_dir'], content)
            changes_made += len(matches)

    if changes_made > 0:
        # Write back the updated script
        with open(script_path, 'w') as f:
            f.write(content)
        print(f"  ✓ Updated {changes_made} path reference(s) to {config['new_dir']}")
        updated_count += 1
    else:
        print(f"  - No changes needed")

print()
print("=" * 70)
print("UPDATE COMPLETE")
print("=" * 70)
print(f"\nScripts updated: {updated_count}")
print(f"Scripts skipped (not found): {error_count}")
print(f"Total processed: {len(script_updates)}")
print()
print("All analysis scripts now save to standardized numbered folders!")
print()
print("Example structure:")
print("  results/00_descriptive_statistics/")
print("  results/01_fentanyl_timeline/")
print("  results/02_polysubstance_trends/")
print("  ...")
print("  results/27_poverty_age_interaction/")
