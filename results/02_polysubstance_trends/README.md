# Polysubstance Use Trends

**Analysis Number**: 02
**Script**: `02_polysubstance_trends.py`
**Status**: ✅ Verified with actual results
**Last Updated**: 2025-11-05

## Overview
Analyzes trends in polysubstance involvement - deaths involving multiple substances simultaneously.
Examines dangerous combinations and their evolution over time.

## Outputs Generated

### Visualizations
- `age_comparison_fentanyl_meth.png`
- `dangerous_combinations.png`
- `fentanyl_meth_detailed.png`
- `polysubstance_trends.png`
- `substance_correlation_heatmap.png`
- `substance_count_distribution.png`

### Data Tables
- `age_by_fentanyl_meth_category.csv`
  - 3 rows, 7 columns
- `annual_polysubstance_stats.csv`
  - 12 rows, 5 columns
- `dangerous_combinations.csv`
  - 60 rows, 5 columns
- `fentanyl_meth_coinvolvement_annual.csv`
  - 12 rows, 10 columns
- `triple_combinations.csv`
  - 12 rows, 5 columns


## Key Findings

### Polysubstance Prevalence
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
- Document how age varies by substance combination complexity

## Methodology

- Counts number of substances per death
- Identifies specific dangerous combinations
- Calculates correlation matrices between substances
- Analyzes age distributions by polysubstance category
- Tracks temporal trends in combination patterns

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

- See `results/README.md` for complete analysis index

---

**Verification Status**: ✅ This README was generated after running the analysis
**Generated**: 2025-11-05 21:23
