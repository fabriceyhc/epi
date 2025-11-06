# Disparity Decomposition Analysis

**Analysis Number**: 15
**Script**: `15_disparity_decomposition.py`
**Status**: ✅ Verified with actual results
**Last Updated**: 2025-11-05

## Overview
Decomposes racial disparities into components: population share vs mortality rate. Calculates
disparity ratios showing over/underrepresentation in overdose deaths.

## Outputs Generated

### Visualizations
- `COMPREHENSIVE_PUBLICATION_FIGURE.png`
- `age_standardized_rates.png`
- `counterfactual_ses_matching.png`
- `covid_economic_shock.png`
- `cumulative_disadvantage.png`
- `disparity_comparison.png`
- `disparity_decomposition.png`
- `geographic_ses_inequality.png`
- `housing_costs_analysis.png`
- `housing_homelessness_pipeline.png`
- `income_volatility.png`
- `population_adjusted_rates.png`
- `poverty_age_interaction.png`
- `real_income_cost_of_living.png`
- `ses_context_figure.png`
- `substance_specific_ses_patterns.png`
- `temporal_correlation_scatterplots.png`
- `ypll_age_distribution.png`
- `ypll_analysis.png`

### Data Tables
- `age_specific_rates.csv`
  - 432 rows, 7 columns
- `age_standardized_disparities.csv`
  - 36 rows, 4 columns
- `age_standardized_rates.csv`
  - 48 rows, 6 columns
- `counterfactual_model_fit.csv`
  - 2 rows, 3 columns
- `counterfactual_predictions_2023.csv`
  - 4 rows, 4 columns
- `covid_2020_monthly.csv`
  - 12 rows, 4 columns
- `covid_changes_from_baseline.csv`
  - 12 rows, 6 columns
- `covid_period_rates.csv`
  - 28 rows, 7 columns
- `cumulative_disadvantage_scores.csv`
  - 44 rows, 11 columns
- `deaths_by_age_poverty.csv`
  - 18 rows, 5 columns
- `disadvantage_component_correlations.csv`
  - 3 rows, 3 columns
- `disadvantage_overdose_rates.csv`
  - 44 rows, 16 columns
- `disparity_decomposition_annual.csv`
  - 11 rows, 7 columns
- `homeless_by_race_year.csv`
  - 72 rows, 5 columns
- `housing_costs_by_race.csv`
  - 72 rows, 11 columns
- `housing_costs_overdose_trends.csv`
  - 12 rows, 6 columns
- `housing_homeless_trends.csv`
  - 12 rows, 9 columns
- `income_housing_burden.csv`
  - 11 rows, 15 columns
- `income_stability_by_race.csv`
  - 4 rows, 4 columns
- `income_volatility_metrics.csv`
  - 44 rows, 5 columns
- `income_volatility_overdoses.csv`
  - 44 rows, 10 columns
- `poverty_age_correlations.csv`
  - 6 rows, 4 columns
- `race_rates_annual.csv`
  - 48 rows, 10 columns
- `ses_comparison_2023.csv`
  - 4 rows, 10 columns
- `substance_by_race.csv`
  - 20 rows, 4 columns
- `substance_poverty_comparison.csv`
  - 5 rows, 4 columns
- `substance_ses_correlations.csv`
  - 5 rows, 6 columns
- `temporal_correlations.csv`
  - 8 rows, 7 columns
- `ypll_by_race_year.csv`
  - 48 rows, 10 columns
- `zip_level_overdoses_ses.csv`
  - 263 rows, 9 columns


## Key Findings

### Disparity Ratios
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
- Check for inflection points

## Methodology

- Calculates annual death proportions by race
- Obtains population proportions from Census
- Computes disparity ratios
- Tracks ratios over time
- Decomposes into population vs rate components
- Generates comparison visualizations

## Interpretation

*Add interpretation of results here after reviewing outputs.*

## Data Sources

### Overdose Data
- **Source**: LA County Medical Examiner-Coroner
- **Period**: 2012-2024 (analysis typically uses 2012-2023)
- **N**: ~18,495 deaths (2012-2023)

### Additional Data
- *(No additional data sources)*

## Notes

- Review the visualization files for detailed findings
- Examine CSV files for exact statistics
- See main results README for context

## Related Analyses

- See Analysis #22 for counterfactual SES decomposition

---

**Verification Status**: ✅ This README was generated after running the analysis
**Generated**: 2025-11-05 21:25
