# Homelessness and Overdose Deaths

**Analysis Number**: 04
**Script**: `04_homelessness_analysis.py`
**Status**: ✅ Verified with actual results
**Last Updated**: 2025-11-05

## Overview
Examines the relationship between homelessness and overdose deaths, including demographic patterns
and substance use among unhoused individuals.

## Outputs Generated

### Visualizations
- `homeless_demographics_age.png`
- `homeless_geographic_distribution.png`
- `homeless_substance_trends.png`
- `homeless_trends.png`
- `substances_by_housing.png`

### Data Tables
- `homeless_substance_trends.csv`
  - 96 rows, 4 columns
- `homeless_trends_annual.csv`
  - 24 rows, 5 columns
- `substances_by_housing_status.csv`
  - 16 rows, 5 columns


## Key Findings

### Homelessness Prevalence
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
- Review `homeless_substance_trends.csv` for temporal changes

## Methodology

- Uses ExperiencingHomelessness flag in death records
- Calculates homelessness rates over time
- Compares demographic distributions
- Analyzes substance involvement by housing status
- Maps geographic distribution of homeless deaths

## Interpretation

*Add interpretation of results here after reviewing outputs.*

## Data Sources

### Overdose Data
- **Source**: LA County Medical Examiner-Coroner
- **Period**: 2012-2024 (analysis typically uses 2012-2023)
- **N**: ~18,495 deaths (2012-2023)

### Additional Data
- Uses housing status field from death records

## Notes

- Review the visualization files for detailed findings
- Examine CSV files for exact statistics
- See main results README for context

## Related Analyses

- See `results/README.md` for complete analysis index

---

**Verification Status**: ✅ This README was generated after running the analysis
**Generated**: 2025-11-05 21:23
