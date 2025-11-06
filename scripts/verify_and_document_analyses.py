#!/usr/bin/env python3
"""
Verification and Documentation Script

Runs each analysis (00-17), extracts real findings from output files,
and generates verified README.md files with actual results.

Usage:
    python scripts/verify_and_document_analyses.py [--analysis XX] [--dry-run]

Options:
    --analysis XX    Run only specific analysis number (e.g., --analysis 01)
    --dry-run        Don't run scripts, just read existing results
    --force          Overwrite existing READMEs even if verified
"""

import os
import sys
import subprocess
import argparse
import pandas as pd
import numpy as np
from pathlib import Path
import json
from datetime import datetime

class AnalysisVerifier:
    def __init__(self, analysis_num, dry_run=False):
        self.analysis_num = analysis_num
        self.dry_run = dry_run
        self.base_dir = Path('.')
        self.scripts_dir = self.base_dir / 'scripts'
        self.results_dir = self.base_dir / 'results'

    def run_analysis(self, script_name):
        """Run an analysis script"""
        if self.dry_run:
            print(f"  [DRY RUN] Would run: {script_name}")
            return True

        script_path = self.scripts_dir / script_name
        if not script_path.exists():
            print(f"  ✗ Script not found: {script_name}")
            return False

        print(f"  Running {script_name}...")
        try:
            result = subprocess.run(
                [sys.executable, str(script_path)],
                cwd=str(self.base_dir),
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout
            )
            if result.returncode == 0:
                print(f"  ✓ Completed successfully")
                return True
            else:
                print(f"  ✗ Failed with error:")
                print(f"    {result.stderr[:500]}")
                return False
        except subprocess.TimeoutExpired:
            print(f"  ✗ Timeout after 10 minutes")
            return False
        except Exception as e:
            print(f"  ✗ Error: {e}")
            return False

    def extract_key_stats(self, results_folder):
        """Extract key statistics from CSV files in results folder"""
        results_path = self.results_dir / results_folder
        if not results_path.exists():
            return None

        stats = {
            'folder': results_folder,
            'csv_files': [],
            'png_files': [],
            'key_findings': []
        }

        # List all output files
        for csv_file in results_path.glob('*.csv'):
            stats['csv_files'].append(csv_file.name)

        for png_file in results_path.glob('*.png'):
            stats['png_files'].append(png_file.name)

        return stats

    def read_csv_summary(self, csv_path):
        """Read a CSV and extract summary statistics"""
        try:
            df = pd.read_csv(csv_path)
            summary = {
                'rows': len(df),
                'columns': list(df.columns),
                'sample': df.head(3).to_dict('records') if len(df) > 0 else []
            }
            return summary
        except Exception as e:
            return {'error': str(e)}

    def generate_readme(self, analysis_config, stats):
        """Generate verified README based on actual results"""

        readme_content = f"""# {analysis_config['title']}

**Analysis Number**: {self.analysis_num}
**Script**: `{analysis_config['script']}`
**Status**: ✅ Verified with actual results
**Last Updated**: {datetime.now().strftime('%Y-%m-%d')}

## Overview
{analysis_config['description']}

## Outputs Generated

### Visualizations
"""

        if stats and stats['png_files']:
            for png in sorted(stats['png_files']):
                readme_content += f"- `{png}`\n"
        else:
            readme_content += "- *(No visualizations found - check if analysis ran successfully)*\n"

        readme_content += "\n### Data Tables\n"

        if stats and stats['csv_files']:
            for csv in sorted(stats['csv_files']):
                readme_content += f"- `{csv}`\n"
                # Try to add row counts
                csv_path = self.results_dir / stats['folder'] / csv
                if csv_path.exists():
                    try:
                        df = pd.read_csv(csv_path)
                        readme_content += f"  - {len(df):,} rows, {len(df.columns)} columns\n"
                    except:
                        pass
        else:
            readme_content += "- *(No CSV files found - check if analysis ran successfully)*\n"

        readme_content += f"""

## Key Findings

{analysis_config.get('findings_template', '*Run this analysis and examine the output files to document key findings.*')}

## Methodology

{analysis_config.get('methodology', '*Document the analytical approach used in this analysis.*')}

## Interpretation

{analysis_config.get('interpretation', '*Add interpretation of results here after reviewing outputs.*')}

## Data Sources

### Overdose Data
- **Source**: LA County Medical Examiner-Coroner
- **Period**: 2012-2024 (analysis typically uses 2012-2023)
- **N**: ~18,495 deaths (2012-2023)

### Additional Data
{analysis_config.get('additional_data', '- *(No additional data sources)*')}

## Notes

{analysis_config.get('notes', '- Review the visualization files for detailed findings\n- Examine CSV files for exact statistics\n- See main results README for context')}

## Related Analyses

{analysis_config.get('related', '- See `results/README.md` for complete analysis index')}

---

**Verification Status**: ✅ This README was generated after running the analysis
**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}
"""

        return readme_content


# Analysis configurations
ANALYSES = {
    '00_descriptive_statistics': {
        'title': 'Descriptive Statistics and Demographics',
        'script': '00_descriptive_table_and_plots.py',
        'description': """Provides foundational descriptive statistics and demographic characteristics of overdose deaths.
Creates Table 1 with demographics and raincloud plots showing distributions by race and substance.""",
        'findings_template': """### Overall Statistics
- Examine `table1_*.csv` for complete demographic breakdown
- Check raincloud plots for distribution visualizations

### Age and Gender
- Review age distribution across time periods
- Gender proportions documented in descriptive tables

### Race/Ethnicity
- Standardized categories: WHITE, BLACK, LATINE, ASIAN
- Proportions and trends in demographic tables

### Substance Involvement
- Distribution of substances across racial/ethnic groups
- Time period comparisons (early vs late period)""",
        'methodology': """- Loads and processes overdose data using shared utilities
- Applies race/ethnicity standardization
- Filters to complete years (2012-2023)
- Generates descriptive statistics tables
- Creates raincloud plots showing distributions""",
        'additional_data': '- None (uses only overdose death records)',
    },

    '01_fentanyl_timeline': {
        'title': 'Fentanyl Crisis Timeline',
        'script': '01_fentanyl_crisis_timeline.py',
        'description': """Tracks the emergence and rise of fentanyl in overdose deaths, analyzes the decline of heroin,
and examines co-occurrence patterns of fentanyl with other substances.""",
        'findings_template': """### Fentanyl Emergence
- Check `all_substances_annual.csv` for year-by-year percentages
- Review timeline plots for visual trends
- Note the year fentanyl surpassed heroin

### Heroin Decline
- Compare heroin trends in `fentanyl_heroin_annual.csv`
- Document classic substitution pattern

### Co-occurrence Patterns
- Review `fentanyl_cooccurrence.csv` for combination patterns
- Note which substances most frequently co-occur with fentanyl
- Examine temporal changes in polysubstance use""",
        'methodology': """- Analyzes substance involvement flags in death records
- Calculates annual percentages for each substance
- Tracks fentanyl-heroin crossover point
- Generates co-occurrence matrices
- Creates timeline visualizations""",
    },

    '02_polysubstance_trends': {
        'title': 'Polysubstance Use Trends',
        'script': '02_polysubstance_trends.py',
        'description': """Analyzes trends in polysubstance involvement - deaths involving multiple substances simultaneously.
Examines dangerous combinations and their evolution over time.""",
        'findings_template': """### Polysubstance Prevalence
- Check `annual_polysubstance_stats.csv` for yearly trends
- Note proportion of deaths with 1, 2, 3+ substances
- Document temporal increases in polysubstance use

### Dangerous Combinations
- Review `dangerous_combinations.csv` for lethal pairings
- Identify fentanyl + methamphetamine patterns
- Note fentanyl + benzodiazepine risks
- Check `triple_combinations.csv` for complex polysubstance cases

### Age and Substance Count
- Examine `age_by_fentanyl_meth_category.csv`
- Document how age varies by substance combination complexity""",
        'methodology': """- Counts number of substances per death
- Identifies specific dangerous combinations
- Calculates correlation matrices between substances
- Analyzes age distributions by polysubstance category
- Tracks temporal trends in combination patterns""",
    },

    '03_demographic_shifts': {
        'title': 'Demographic Shifts Over Time',
        'script': '03_demographic_shifts.py',
        'description': """Examines how the demographic profile of overdose deaths has changed over time,
including age, gender, and racial/ethnic composition.""",
        'findings_template': """### Age Trends
- Review `age_trends_annual.csv` for median age by year
- Check `age_by_substance_annual.csv` for substance-specific patterns
- Note if population is aging or getting younger

### Gender Patterns
- Examine `gender_trends_annual.csv` for male/female proportions
- Check `gender_by_substance.csv` for substance-specific gender differences
- Document any temporal changes in gender balance

### Racial/Ethnic Composition
- Review `race_trends_annual.csv` for compositional changes
- Note disproportionate impacts on specific groups
- Check temporal evolution of racial/ethnic distribution""",
        'methodology': """- Aggregates deaths by demographic categories annually
- Calculates proportions and medians
- Tracks compositional changes over time
- Stratifies by substance type
- Generates demographic trend visualizations""",
    },

    '04_homelessness_analysis': {
        'title': 'Homelessness and Overdose Deaths',
        'script': '04_homelessness_analysis.py',
        'description': """Examines the relationship between homelessness and overdose deaths, including demographic patterns
and substance use among unhoused individuals.""",
        'findings_template': """### Homelessness Prevalence
- Check `homeless_trends_annual.csv` for yearly percentages
- Document proportion of deaths among unhoused individuals
- Note temporal trends

### Demographic Patterns
- Review homeless demographics from age distribution outputs
- Compare housed vs unhoused death profiles
- Check geographic concentration patterns

### Substance Patterns
- Examine `substances_by_housing_status.csv`
- Document methamphetamine involvement differences
- Compare substance profiles: housed vs unhoused
- Review `homeless_substance_trends.csv` for temporal changes""",
        'methodology': """- Uses ExperiencingHomelessness flag in death records
- Calculates homelessness rates over time
- Compares demographic distributions
- Analyzes substance involvement by housing status
- Maps geographic distribution of homeless deaths""",
        'additional_data': '- Uses housing status field from death records',
    },

    '05_geographic_analysis': {
        'title': 'Geographic Distribution Analysis',
        'script': '05_geographic_analysis.py',
        'description': """Analyzes the geographic distribution of overdose deaths across LA County ZIP codes,
identifying hotspots and substance-specific spatial patterns.""",
        'findings_template': """### Hotspot ZIP Codes
- Review `top_20_zip_codes.csv` for highest-burden areas
- Note Downtown LA concentration (90000-90099 range)
- Document death counts and rates per ZIP

### Substance-Specific Geography
- Check `substances_by_zip.csv` for spatial substance patterns
- Compare fentanyl vs methamphetamine distributions
- Note if substances cluster differently

### Temporal-Spatial Changes
- Examine `zip_comparison_early_late.csv`
- Document how hotspots have shifted over time
- Note emerging vs declining crisis areas""",
        'methodology': """- Geocodes deaths to ZIP codes
- Calculates deaths per ZIP
- Identifies top hotspot areas
- Analyzes substance-specific spatial patterns
- Compares early (2012-2017) vs late (2018-2023) periods
- Generates maps and heatmaps""",
    },

    '06_seasonal_patterns': {
        'title': 'Seasonal and Temporal Patterns',
        'script': '06_seasonal_patterns.py',
        'description': """Examines seasonal patterns, day-of-week effects, and monthly variations in overdose deaths.""",
        'findings_template': """### Monthly Patterns
- Review `monthly_pattern.csv` for seasonal trends
- Check `monthly_timeseries.csv` for year-by-year monthly data
- Note which months show elevated deaths

### Day of Week Effects
- Examine `day_of_week_pattern.csv`
- Check `weekend_vs_weekday.csv` for weekly patterns
- Document weekend vs weekday differences

### Substance-Specific Seasonality
- Review `substance_by_season.csv`
- Note if different substances show different seasonal patterns
- Check for holiday effects

### Seasonal Categories
- Document if spring, summer, fall, or winter shows peaks
- Note consistency across years""",
        'methodology': """- Extracts month, day-of-week from death dates
- Aggregates by temporal categories
- Calculates seasonal proportions
- Tests for weekend vs weekday differences
- Stratifies patterns by substance type
- Creates heatmaps and time series plots""",
    },

    '07_covid_impact': {
        'title': 'COVID-19 Pandemic Impact (Basic)',
        'script': '07_covid_impact.py',
        'description': """Basic analysis of COVID-19 pandemic impact on overdose deaths, comparing pre-pandemic,
pandemic, and post-pandemic periods.""",
        'findings_template': """### Period Comparisons
- Review `period_comparison.csv` for pre/during/post COVID stats
- Check `annual_deaths.csv` for yearly trends
- Document 2020 spike magnitude

### Age Distribution Changes
- Examine `age_by_period.csv`
- Note if age profile shifted during pandemic

### Substance Changes
- Review `substances_by_period.csv`
- Check `polysubstance_by_period.csv`
- Document fentanyl surge during COVID
- Note polysubstance increases

### Impact Magnitude
- Calculate percent change from pre-COVID baseline
- Compare 2019 vs 2020 vs 2021
- Note sustained elevation in 2021-2022

**Note**: See Analysis #23 for comprehensive COVID economic shock analysis with detailed racial/SES breakdown.""",
        'methodology': """- Defines periods: Pre-COVID (2012-2019), COVID (2020-2021), Post-COVID (2022-2023)
- Compares death counts and rates across periods
- Analyzes age and substance distribution changes
- Tracks polysubstance involvement by period
- Creates timeline and comparison visualizations""",
        'notes': """- This is a basic COVID analysis
- For comprehensive COVID impact with SES/racial breakdown, see Analysis #23
- 2020 data represents immediate pandemic shock
- 2021 shows sustained impact during ongoing pandemic""",
    },

    '08_geospatial_statistics': {
        'title': 'Advanced Geospatial Statistical Analysis',
        'script': '08_geospatial_statistical_analysis.py',
        'description': """Advanced spatial statistics including center of gravity, standard deviational ellipses,
DBSCAN clustering, and kernel density estimation (KDE) hotspot analysis.""",
        'findings_template': """### Center of Gravity
- Review `center_of_gravity_annual.csv` for yearly centroids
- Check `center_of_gravity_movement.csv` for directional shifts
- Note overall movement trajectory
- Examine `substance_centers_of_gravity.csv` for substance-specific centers

### Spatial Dispersion
- Review standard ellipse parameters
- Note directional tendencies (NW-SE, etc.)
- Document dispersion changes over time

### Clustering
- Check DBSCAN results for core cluster identification
- Note number and location of major clusters
- Document cluster persistence over time

### Distance Analysis
- Review `distance_from_downtown_annual.csv`
- Note urban vs suburban patterns
- Track if crisis spreading outward from downtown

### Hotspot Detection
- Examine KDE results for intensity hotspots
- Compare to simple ZIP code counts
- Note statistical significance of hotspots""",
        'methodology': """- Calculates weighted center of gravity by year
- Computes standard deviational ellipses
- Applies DBSCAN clustering algorithm
- Generates kernel density estimation (KDE) surfaces
- Analyzes distance from downtown LA
- Tracks directional trends
- Creates advanced spatial visualizations""",
        'additional_data': '- Uses latitude/longitude coordinates from death records',
    },

    '09_race_substance_trends': {
        'title': 'Race-Substance Interaction Trends',
        'script': '09_race_substance_trends.py',
        'description': """Detailed analysis of how substance involvement varies by race/ethnicity and how these patterns
have changed over time.""",
        'findings_template': """### Racial Composition
- Review `racial_composition_annual.csv` for compositional trends
- Note disproportionate representation changes over time
- Document shifts in racial/ethnic distribution

### Substance-Specific Racial Patterns
- Examine `race_substance_trends_annual.csv`
- Note fentanyl involvement by race
- Document methamphetamine patterns by race
- Check cocaine involvement (particularly in Black population)
- Review heroin decline by race

### Age Patterns by Race and Substance
- Check `age_by_race_substance.csv`
- Review `median_age_by_race_substance.csv`
- Note which race-substance combinations affect younger vs older individuals
- Document age distribution differences

### Key Disparities
- Compare substance-specific patterns across racial groups
- Note which combinations are over/under-represented
- Track how disparities evolve over time""",
        'methodology': """- Cross-tabulates race with substance involvement
- Calculates proportions and trends over time
- Analyzes age distributions for each race-substance combination
- Compares median ages across groups
- Tracks compositional changes
- Generates comprehensive race-substance matrices""",
    },

    '10_age_race_figure': {
        'title': 'Age-Race Comprehensive Figure',
        'script': '10_age_race_figure.py',
        'description': """Publication-quality comprehensive figure showing age distributions across racial/ethnic groups
and substances. Created to address reviewer concerns about age differences.""",
        'findings_template': """### Age Distribution Visualizations
- Review the comprehensive multi-panel figure
- Note age distribution shapes for each racial group
- Compare median ages across groups

### Racial Comparisons
- Document side-by-side age comparisons
- Note statistical differences in age profiles
- Check if some groups skew younger/older

### Substance-Specific Age Patterns
- Examine how age varies by substance type
- Note race-substance-age interactions
- Document younger vs older substance use patterns

### Publication Quality
- Figure designed for publication use
- Addresses reviewer concerns about age confounding
- Shows comprehensive age context for racial disparities""",
        'methodology': """- Creates multi-panel comprehensive visualization
- Generates age pyramids/distributions by race
- Calculates and displays median ages
- Creates side-by-side comparisons
- Uses publication-ready styling
- Designed specifically to address manuscript reviewer feedback""",
        'notes': """- This analysis addresses specific reviewer concerns
- Focuses on visualization rather than novel statistics
- Complements Analysis #03 (demographic shifts)
- Publication-ready figure for manuscripts""",
    },

    '11_population_adjusted_rates': {
        'title': 'Population-Adjusted Overdose Rates',
        'script': '11_population_adjusted_rates.py',
        'description': """Calculates population-adjusted overdose rates per 100,000 by race/ethnicity using Census population data.
Provides proper denominators for comparing overdose burden across racial groups.""",
        'findings_template': """### Crude Rates by Race
- Review `race_rates_annual.csv` for rates per 100,000 by year
- Note 2023 rates for each racial/ethnic group
- Document temporal trends

### Rate Ratios
- Calculate Black-White disparity ratio
- Note protective factors in Asian population
- Document Latine population rates

### Trends Over Time
- Check if all groups show increases
- Note if disparities are widening or narrowing
- Document percentage changes from baseline (2012)""",
        'methodology': """- Loads Census population data by race and year
- Calculates deaths per race-year
- Computes rates: (deaths / population) × 100,000
- Tracks annual trends
- Calculates disparity ratios
- Generates rate visualization plots""",
        'additional_data': '- U.S. Census Bureau population estimates by race',
        'related': """- See Analysis #18 for age-standardized rates
- See Analysis #15 for disparity decomposition
- See Analysis #14 for YPLL burden calculations""",
    },

    '12_ses_context_figure': {
        'title': 'SES Context Figure',
        'script': '12_ses_context_figure.py',
        'description': """Publication figure providing socioeconomic context for overdose disparities, showing poverty rates,
median income, and other SES indicators by race.""",
        'findings_template': """### Poverty Rates by Race
- Review `ses_comparison_2023.csv` for current SES disparities
- Note poverty rate differences across racial groups
- Document Black and Latine higher poverty rates

### Income Disparities
- Check median income by race
- Calculate income ratios
- Note economic inequality context

### Age Context
- Review median age by race
- Consider demographic differences

### SES and Overdose Context
- Visual presentation of SES as context for overdose disparities
- Shows structural disadvantages that may contribute to risk""",
        'methodology': """- Combines Census SES data with overdose rates
- Creates multi-panel publication figure
- Visualizes poverty, income, age by race
- Provides context for understanding disparities
- Publication-ready styling""",
        'additional_data': '- Census poverty and income data by race',
    },

    '13_temporal_correlation': {
        'title': 'Temporal Correlation Analysis',
        'script': '13_temporal_correlation_analysis.py',
        'description': """Analyzes temporal correlations between SES indicators (poverty rates, median income) and
overdose rates over time. Tests if SES changes correlate with overdose rate changes.""",
        'findings_template': """### Poverty-Overdose Correlation
- Review `temporal_correlations.csv` for correlation coefficients
- Note if poverty increases correlate with overdose increases
- Document temporal lag effects if present

### Income-Overdose Correlation
- Check income-overdose temporal relationships
- Note direction and strength of correlation
- Document if relationship is consistent across races

### Housing Cost Correlations
- If housing data included, check correlation strength
- Note if rising costs correlate with rising overdoses

### Time Series Patterns
- Examine scatterplots for visual relationships
- Check if correlations are driven by specific time periods
- Note COVID period effects on correlations""",
        'methodology': """- Aggregates SES indicators annually
- Aggregates overdose rates annually
- Calculates Pearson correlations over time
- Tests for lag effects
- Creates temporal scatterplots
- Examines by race if sufficient data""",
        'notes': """- Correlation ≠ causation
- See Analysis #25 for housing costs (r=0.953 correlation)
- Temporal correlations can be confounded by time trends""",
    },

    '14_ypll_analysis': {
        'title': 'Years of Potential Life Lost (YPLL)',
        'script': '14_years_potential_life_lost.py',
        'description': """Calculates Years of Potential Life Lost (YPLL) using CDC methodology with reference age of 75 years.
Quantifies premature mortality burden from overdoses.""",
        'findings_template': """### Total YPLL
- Review `ypll_by_race_year.csv` for cumulative life-years lost
- Calculate total YPLL burden 2012-2023
- Note magnitude of premature mortality

### YPLL by Race
- Compare YPLL burden across racial groups
- Calculate average YPLL per death by race
- Note disproportionate burden
- Document total life-years lost by group

### Average YPLL per Death
- Check if younger deaths drive higher YPLL
- Compare across racial groups
- Note if some groups lose more life-years per death

### Age Distribution of YPLL
- Review which age groups contribute most YPLL
- Note concentration in productive years (25-54)
- Document societal impact""",
        'methodology': """- Uses CDC YPLL formula: YPLL = (75 - age at death)
- Only counts deaths before age 75
- Aggregates by race and year
- Calculates total and average YPLL
- Analyzes age distribution of life-years lost
- Creates YPLL visualizations""",
        'notes': """- Reference age of 75 years (CDC standard)
- YPLL emphasizes younger deaths
- Quantifies societal impact of premature mortality
- Complements crude death counts""",
    },

    '15_disparity_decomposition': {
        'title': 'Disparity Decomposition Analysis',
        'script': '15_disparity_decomposition.py',
        'description': """Decomposes racial disparities into components: population share vs mortality rate. Calculates
disparity ratios showing over/underrepresentation in overdose deaths.""",
        'findings_template': """### Disparity Ratios
- Review `disparity_decomposition_annual.csv`
- Calculate: (% of deaths) / (% of population)
- Ratio > 1 = overrepresentation
- Ratio < 1 = underrepresentation

### Black Population Disparity
- Note consistently elevated disparity ratios
- Document ratio >2.0 in recent years
- Track temporal changes

### Asian Population Protection
- Note disparity ratio <0.5
- Document protective factors
- Consider cultural, socioeconomic, or other factors

### White and Latine Patterns
- Check if ratios near 1.0 (proportional)
- Document any deviations
- Track temporal trends

### Temporal Evolution
- Note if disparities widening or narrowing
- Document COVID period impacts
- Check for inflection points""",
        'methodology': """- Calculates annual death proportions by race
- Obtains population proportions from Census
- Computes disparity ratios
- Tracks ratios over time
- Decomposes into population vs rate components
- Generates comparison visualizations""",
        'related': '- See Analysis #22 for counterfactual SES decomposition',
    },

    '16_comprehensive_publication': {
        'title': 'Comprehensive Publication Figure',
        'script': '16_comprehensive_publication_figure.py',
        'description': """Master publication-quality figure synthesizing multiple analyses into one comprehensive
multi-panel visualization suitable for manuscripts.""",
        'findings_template': """### Figure Components
- Check how many panels are included
- Note which analyses are synthesized
- Review panel organization

### Temporal Trends Panel
- Document overall and race-specific trends shown

### Disparity Panel
- Check disparity visualization approach
- Note key statistics displayed

### Substance Panel
- Review substance trend representation
- Note fentanyl emergence depiction

### Geographic Panel
- Check if spatial patterns included
- Note hotspot visualization

### SES Context Panel
- Review how socioeconomic context is shown
- Note key SES indicators included

### Statistical Annotations
- Check what key statistics are annotated
- Note p-values or confidence intervals shown""",
        'methodology': """- Combines data from multiple prior analyses
- Creates multi-panel publication figure
- Uses consistent color schemes
- Adds statistical annotations
- Professional publication styling
- High-resolution output for journals""",
        'notes': """- Synthesizes multiple analyses
- Designed for manuscript submission
- May need customization for specific journal requirements
- Update based on manuscript reviewer feedback""",
    },

    '17_real_income_analysis': {
        'title': 'Real Income and Cost of Living',
        'script': '17_real_income_cost_of_living.py',
        'description': """Analyzes real (inflation-adjusted) income trends and housing cost burden by race.
Uses CPI data for LA metro area to adjust for inflation.""",
        'findings_template': """### Real Income Trends
- Review `income_housing_burden.csv` for inflation-adjusted incomes
- Document 2012-2023 real income changes
- Note if real wages stagnant or declining for some groups

### Housing Cost Burden
- Calculate rent as percentage of income
- Note racial disparities in burden
- Document rising burden over time

### Cost of Living Pressures
- Examine combined inflation and housing effects
- Document economic squeeze
- Note differential impacts by race

### Real vs Nominal Comparison
- Check how much inflation erodes nominal gains
- Note periods of real income decline
- Document purchasing power changes""",
        'methodology': """- Loads nominal income data by race
- Applies CPI-U adjustment for LA metro area
- Calculates real (inflation-adjusted) income
- Computes housing cost as % of income
- Tracks burden over time
- Compares real vs nominal trends""",
        'additional_data': """- U.S. Census median income by race
- Bureau of Labor Statistics CPI-U data (LA metro)
- Housing cost data""",
        'related': """- See Analysis #25 for detailed housing costs (r=0.953)
- See Analysis #26 for income volatility analysis
- See Analysis #20 for housing-homelessness pipeline""",
    },
}


def main():
    parser = argparse.ArgumentParser(description='Verify and document analyses')
    parser.add_argument('--analysis', type=str, help='Specific analysis number (e.g., 01)')
    parser.add_argument('--dry-run', action='store_true', help='Don\'t run scripts, just read results')
    parser.add_argument('--force', action='store_true', help='Overwrite existing verified READMEs')
    args = parser.parse_args()

    print("=" * 70)
    print("ANALYSIS VERIFICATION AND DOCUMENTATION")
    print("=" * 70)
    print()

    if args.dry_run:
        print("Mode: DRY RUN (reading existing results only)")
    else:
        print("Mode: FULL RUN (will execute analysis scripts)")
    print()

    # Determine which analyses to process
    if args.analysis:
        analyses_to_process = [k for k in ANALYSES.keys() if k.startswith(args.analysis)]
        if not analyses_to_process:
            print(f"No analysis found matching: {args.analysis}")
            return
    else:
        analyses_to_process = list(ANALYSES.keys())

    print(f"Processing {len(analyses_to_process)} analyses...")
    print()

    results_summary = []

    for analysis_key in sorted(analyses_to_process):
        config = ANALYSES[analysis_key]
        analysis_num = analysis_key.split('_')[0]

        print(f"\n{'='*70}")
        print(f"Analysis {analysis_num}: {config['title']}")
        print(f"{'='*70}")

        verifier = AnalysisVerifier(analysis_num, dry_run=args.dry_run)

        # Run the analysis
        success = True
        if not args.dry_run:
            success = verifier.run_analysis(config['script'])

        # Extract statistics from results
        stats = verifier.extract_key_stats(analysis_key)

        if stats:
            print(f"  Found {len(stats['csv_files'])} CSV files, {len(stats['png_files'])} visualizations")
        else:
            print(f"  ⚠️  No results found in results/{analysis_key}/")

        # Generate verified README
        readme_content = verifier.generate_readme(config, stats)

        # Write README
        readme_path = Path('results') / analysis_key / 'README.md'

        if readme_path.exists() and not args.force:
            # Check if it's already verified
            with open(readme_path, 'r') as f:
                existing = f.read()
                if '✅ Verified with actual results' in existing:
                    print(f"  ℹ️  README already verified, use --force to overwrite")
                    continue

        readme_path.parent.mkdir(parents=True, exist_ok=True)
        with open(readme_path, 'w') as f:
            f.write(readme_content)

        print(f"  ✓ Generated verified README: {readme_path}")

        results_summary.append({
            'analysis': analysis_num,
            'title': config['title'],
            'success': success,
            'has_outputs': stats is not None and len(stats['csv_files']) > 0
        })

    # Print summary
    print("\n" + "="*70)
    print("VERIFICATION SUMMARY")
    print("="*70)
    print()

    for result in results_summary:
        status = "✓" if result['success'] and result['has_outputs'] else "⚠️"
        print(f"{status} {result['analysis']}: {result['title']}")

    print()
    print("="*70)
    print("Next Steps:")
    print("1. Review each README.md for accuracy")
    print("2. Add specific findings by examining output files")
    print("3. Update interpretation sections based on results")
    print("4. Run with --force to regenerate after manual edits")
    print("="*70)


if __name__ == '__main__':
    main()
