# Demographic Shifts Over Time

**Analysis Number**: 03
**Script**: `03_demographic_shifts.py`
**Status**: ✅ Verified with actual results
**Last Updated**: 2025-11-05

## Overview
Examines how the demographic profile of overdose deaths has changed over time,
including age, gender, and racial/ethnic composition.

## Outputs Generated

### Visualizations
- `age_by_substance.png`
- `age_trends_overall.png`
- `gender_trends.png`
- `race_by_substance.png`
- `race_trends.png`

### Data Tables
- `age_by_substance_annual.csv`
  - 96 rows, 3 columns
- `age_trends_annual.csv`
  - 12 rows, 4 columns
- `gender_by_substance.csv`
  - 192 rows, 4 columns
- `gender_trends_annual.csv`
  - 24 rows, 5 columns
- `race_trends_annual.csv`
  - 60 rows, 5 columns


## Key Findings

### Age Trends
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
- Check temporal evolution of racial/ethnic distribution

## Methodology

- Aggregates deaths by demographic categories annually
- Calculates proportions and medians
- Tracks compositional changes over time
- Stratifies by substance type
- Generates demographic trend visualizations

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
