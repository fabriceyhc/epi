# Fentanyl Crisis Timeline

**Analysis Number**: 01
**Script**: `01_fentanyl_crisis_timeline.py`
**Status**: ✅ Verified with actual results
**Last Updated**: 2025-11-05

## Overview
Tracks the emergence and rise of fentanyl in overdose deaths, analyzes the decline of heroin,
and examines co-occurrence patterns of fentanyl with other substances.

## Outputs Generated

### Visualizations
- `all_substances_timeline.png`
- `fentanyl_cooccurrence.png`
- `fentanyl_heroin_comparison.png`
- `substance_composition_stacked.png`

### Data Tables
- `all_substances_annual.csv`
  - 96 rows, 3 columns
- `fentanyl_cooccurrence.csv`
  - 60 rows, 5 columns
- `fentanyl_heroin_annual.csv`
  - 12 rows, 6 columns


## Key Findings

### Fentanyl Emergence
- Check `all_substances_annual.csv` for year-by-year percentages
- Review timeline plots for visual trends
- Note the year fentanyl surpassed heroin

### Heroin Decline
- Compare heroin trends in `fentanyl_heroin_annual.csv`
- Document classic substitution pattern

### Co-occurrence Patterns
- Review `fentanyl_cooccurrence.csv` for combination patterns
- Note which substances most frequently co-occur with fentanyl
- Examine temporal changes in polysubstance use

## Methodology

- Analyzes substance involvement flags in death records
- Calculates annual percentages for each substance
- Tracks fentanyl-heroin crossover point
- Generates co-occurrence matrices
- Creates timeline visualizations

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
