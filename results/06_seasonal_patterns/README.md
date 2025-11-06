# Seasonal and Temporal Patterns

**Analysis Number**: 06
**Script**: `06_seasonal_patterns.py`
**Status**: ✅ Verified with actual results
**Last Updated**: 2025-11-05

## Overview
Examines seasonal patterns, day-of-week effects, and monthly variations in overdose deaths.

## Outputs Generated

### Visualizations
- `day_of_week_pattern.png`
- `monthly_by_year.png`
- `monthly_pattern.png`
- `monthly_timeseries.png`
- `seasonal_pattern.png`
- `substance_by_season_heatmap.png`
- `weekend_vs_weekday.png`

### Data Tables
- `day_of_week_pattern.csv`
  - 7 rows, 3 columns
- `monthly_pattern.csv`
  - 12 rows, 3 columns
- `monthly_timeseries.csv`
  - 144 rows, 3 columns
- `seasonal_pattern.csv`
  - 4 rows, 2 columns
- `substance_by_season.csv`
  - 32 rows, 4 columns
- `weekend_vs_weekday.csv`
  - 2 rows, 5 columns


## Key Findings

### Monthly Patterns
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
- Note consistency across years

## Methodology

- Extracts month, day-of-week from death dates
- Aggregates by temporal categories
- Calculates seasonal proportions
- Tests for weekend vs weekday differences
- Stratifies patterns by substance type
- Creates heatmaps and time series plots

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
**Generated**: 2025-11-05 21:24
