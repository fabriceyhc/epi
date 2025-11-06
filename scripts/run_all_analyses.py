#!/usr/bin/env python
# coding: utf-8

"""
Master Analysis Pipeline
Runs all analyses in the correct order

Usage:
    python scripts/run_all_analyses.py [--skip-census] [--skip-plots]

Options:
    --skip-census    Skip Census data fetching (use existing data)
    --skip-plots     Skip plot generation (faster for testing)
    --basic-only     Run only basic analyses (01-08)
    --advanced-only  Run only advanced analyses (09-17)
"""

import os
import sys
import subprocess
import argparse
from datetime import datetime

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))

# Define analysis pipeline
PIPELINE = {
    'census': {
        'name': 'Census Data Fetching',
        'script': 'fetch_census_data.py',
        'required': True,
        'description': 'Fetch population and SES data from Census API'
    },
    'descriptive': {
        'name': 'Descriptive Statistics',
        'script': '00_descriptive_table_and_plots.py',
        'required': False,
        'description': 'Create Table 1 and raincloud plots'
    },
    'data_quality': {
        'name': 'Data Quality Report',
        'script': '00_data_quality_report.py',
        'required': False,
        'description': 'Sample derivation and data completeness'
    },
    'basic_analyses': [
        {
            'name': 'Fentanyl Timeline',
            'script': '01_fentanyl_crisis_timeline.py',
            'description': 'Fentanyl emergence and co-occurrence patterns'
        },
        {
            'name': 'Polysubstance Trends',
            'script': '02_polysubstance_trends.py',
            'description': 'Polysubstance involvement and combinations'
        },
        {
            'name': 'Demographics',
            'script': '03_demographic_shifts.py',
            'description': 'Age, race, and gender trends'
        },
        {
            'name': 'Homelessness',
            'script': '04_homelessness_analysis.py',
            'description': 'Housing status and substance patterns'
        },
        {
            'name': 'Geographic Analysis',
            'script': '05_geographic_analysis.py',
            'description': 'ZIP code and spatial analysis'
        },
        {
            'name': 'Seasonal Patterns',
            'script': '06_seasonal_patterns.py',
            'description': 'Monthly and day-of-week patterns'
        },
        {
            'name': 'COVID Impact',
            'script': '07_covid_impact.py',
            'description': 'Pre/during/post COVID comparisons'
        },
        {
            'name': 'Geospatial Statistics',
            'script': '08_geospatial_statistical_analysis.py',
            'description': 'Center of gravity and clustering'
        }
    ],
    'advanced_analyses': [
        {
            'name': 'Race-Stratified Trends',
            'script': '09_race_substance_trends.py',
            'description': 'Substance trends by race/ethnicity'
        },
        {
            'name': 'Age-Race Analysis',
            'script': '10_age_race_figure.py',
            'description': 'Age patterns by race (addresses reviewer concern)'
        },
        {
            'name': 'Population-Adjusted Rates',
            'script': '11_population_adjusted_rates.py',
            'description': 'Overdose rates per 100k with disparity ratios'
        },
        {
            'name': 'SES Context Figure',
            'script': '12_ses_context_figure.py',
            'description': 'Poverty, income, and age context'
        },
        {
            'name': 'Temporal Correlations',
            'script': '13_temporal_correlation_analysis.py',
            'description': 'SES changes vs overdose rate changes'
        },
        {
            'name': 'YPLL Analysis',
            'script': '14_years_potential_life_lost.py',
            'description': 'Years of potential life lost by race'
        },
        {
            'name': 'Disparity Decomposition',
            'script': '15_disparity_decomposition.py',
            'description': 'SES-explained vs structural factors'
        },
        {
            'name': 'Comprehensive Figure',
            'script': '16_comprehensive_publication_figure.py',
            'description': 'Combined publication figure'
        },
        {
            'name': 'Real Income Analysis',
            'script': '17_real_income_cost_of_living.py',
            'description': 'Inflation-adjusted income and housing costs'
        }
    ]
}


def run_script(script_name, description):
    """
    Run a single analysis script

    Parameters:
    -----------
    script_name : str
        Name of the script file
    description : str
        Description of what the script does

    Returns:
    --------
    bool
        True if successful, False otherwise
    """
    script_path = os.path.join(SCRIPTS_DIR, script_name)

    print("\n" + "="*70)
    print(f"RUNNING: {description}")
    print(f"Script: {script_name}")
    print("="*70)

    try:
        result = subprocess.run(
            [sys.executable, script_path],
            cwd=os.path.dirname(SCRIPTS_DIR),  # Run from repo root
            check=True,
            capture_output=True,
            text=True
        )

        # Print output
        if result.stdout:
            print(result.stdout)

        print(f"✓ {description} completed successfully")
        return True

    except subprocess.CalledProcessError as e:
        print(f"✗ ERROR running {script_name}")
        print(f"\nStdout:\n{e.stdout}")
        print(f"\nStderr:\n{e.stderr}")
        return False

    except FileNotFoundError:
        print(f"✗ ERROR: Script not found: {script_path}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Run LA County overdose analysis pipeline',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('--skip-census', action='store_true',
                        help='Skip Census data fetching (use existing data)')
    parser.add_argument('--skip-plots', action='store_true',
                        help='Skip plot generation (for testing)')
    parser.add_argument('--basic-only', action='store_true',
                        help='Run only basic analyses (01-08)')
    parser.add_argument('--advanced-only', action='store_true',
                        help='Run only advanced analyses (09-17)')
    parser.add_argument('--continue-on-error', action='store_true',
                        help='Continue running even if a script fails')

    args = parser.parse_args()

    print("="*70)
    print("LA COUNTY OVERDOSE ANALYSIS PIPELINE")
    print("="*70)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    results = []
    failed_scripts = []

    # 1. Census data (if not skipped and not advanced-only)
    if not args.skip_census and not args.advanced_only:
        success = run_script(
            PIPELINE['census']['script'],
            PIPELINE['census']['name']
        )
        results.append((PIPELINE['census']['name'], success))
        if not success:
            failed_scripts.append(PIPELINE['census']['name'])
            if not args.continue_on_error:
                print("\n✗ Census data fetch failed. Stopping pipeline.")
                print("  Use --skip-census to use existing data.")
                sys.exit(1)

    # 2. Descriptive statistics (if not advanced-only)
    if not args.advanced_only:
        success = run_script(
            PIPELINE['descriptive']['script'],
            PIPELINE['descriptive']['name']
        )
        results.append((PIPELINE['descriptive']['name'], success))
        if not success:
            failed_scripts.append(PIPELINE['descriptive']['name'])

        success = run_script(
            PIPELINE['data_quality']['script'],
            PIPELINE['data_quality']['name']
        )
        results.append((PIPELINE['data_quality']['name'], success))
        if not success:
            failed_scripts.append(PIPELINE['data_quality']['name'])

    # 3. Basic analyses (if not advanced-only)
    if not args.advanced_only:
        for analysis in PIPELINE['basic_analyses']:
            success = run_script(analysis['script'], analysis['name'])
            results.append((analysis['name'], success))
            if not success:
                failed_scripts.append(analysis['name'])
                if not args.continue_on_error:
                    print(f"\n✗ {analysis['name']} failed. Stopping pipeline.")
                    sys.exit(1)

    # 4. Advanced analyses (if not basic-only)
    if not args.basic_only:
        for analysis in PIPELINE['advanced_analyses']:
            success = run_script(analysis['script'], analysis['name'])
            results.append((analysis['name'], success))
            if not success:
                failed_scripts.append(analysis['name'])
                if not args.continue_on_error:
                    print(f"\n✗ {analysis['name']} failed. Stopping pipeline.")
                    sys.exit(1)

    # Summary
    print("\n" + "="*70)
    print("PIPELINE SUMMARY")
    print("="*70)
    print(f"\nEnd time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    successful = sum(1 for _, success in results if success)
    total = len(results)

    print(f"Completed: {successful}/{total} analyses")
    print()

    if failed_scripts:
        print("FAILED:")
        for script in failed_scripts:
            print(f"  ✗ {script}")
    else:
        print("✓ All analyses completed successfully!")

    print("\n" + "="*70)

    # Exit with error code if any failed
    sys.exit(0 if not failed_scripts else 1)


if __name__ == "__main__":
    main()
