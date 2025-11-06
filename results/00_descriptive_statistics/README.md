# Descriptive Statistics and Demographics

**Analysis Number**: 00
**Script**: `00_descriptive_table_and_plots.py`
**Status**: ✅ Verified with actual results
**Last Updated**: 2025-11-05

## Overview
Provides foundational descriptive statistics and demographic characteristics of overdose deaths.
Creates Table 1 with demographics and raincloud plots showing distributions by race and substance.

## Outputs Generated

### Visualizations
- `age_density_by_substance.png`
- `age_density_by_time_period.png`
- `age_violin_by_substance_fentanyl.png`
- `mean_age_by_substance.png`
- `race_age_substance_2012_2016.png`
- `race_age_substance_2017_2023.png`
- `race_age_substance_raincloud.png`
- `substance_proportion_by_race.png`

### Data Tables
- `Table_1_by_substance.csv`
  - 25 rows, 13 columns


## Key Findings

### Overall Statistics
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
- Time period comparisons (early vs late period)

## Methodology

- Loads and processes overdose data using shared utilities
- Applies race/ethnicity standardization
- Filters to complete years (2012-2023)
- Generates descriptive statistics tables
- Creates raincloud plots showing distributions

## Interpretation

*Add interpretation of results here after reviewing outputs.*

## Data Sources

### Overdose Data
- **Source**: LA County Medical Examiner-Coroner
- **Period**: 2012-2024 (analysis typically uses 2012-2023)
- **N**: ~18,495 deaths (2012-2023)

### Additional Data
- None (uses only overdose death records)

## Notes

- Review the visualization files for detailed findings
- Examine CSV files for exact statistics
- See main results README for context

## Related Analyses

- See `results/README.md` for complete analysis index

---

**Verification Status**: ✅ This README was generated after running the analysis
**Generated**: 2025-11-05 21:23
