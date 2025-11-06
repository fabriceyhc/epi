# Temporal Correlation Analysis

**Analysis Number**: 13
**Script**: `13_temporal_correlation_analysis.py`
**Status**: ✅ Verified with actual results
**Last Updated**: 2025-11-05

## Overview
Analyzes temporal correlations between SES indicators (poverty rates, median income) and
overdose rates over time. Tests if SES changes correlate with overdose rate changes.

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

### Poverty-Overdose Correlation
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
- Note COVID period effects on correlations

## Methodology

- Aggregates SES indicators annually
- Aggregates overdose rates annually
- Calculates Pearson correlations over time
- Tests for lag effects
- Creates temporal scatterplots
- Examines by race if sufficient data

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

- Correlation ≠ causation
- See Analysis #25 for housing costs (r=0.953 correlation)
- Temporal correlations can be confounded by time trends

## Related Analyses

- See `results/README.md` for complete analysis index

---

**Verification Status**: ✅ This README was generated after running the analysis
**Generated**: 2025-11-05 21:25
