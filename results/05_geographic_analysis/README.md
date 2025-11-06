# Geographic Distribution Analysis

**Analysis Number**: 05
**Script**: `05_geographic_analysis.py`
**Status**: ✅ Verified with actual results
**Last Updated**: 2025-11-05

## Overview
Analyzes the geographic distribution of overdose deaths across LA County ZIP codes,
identifying hotspots and substance-specific spatial patterns.

## Outputs Generated

### Visualizations
- `all_overdoses_map.png`
- `death_locations.png`
- `fentanyl_vs_meth_geography.png`
- `substance_by_zip_heatmap.png`
- `substance_specific_maps.png`
- `temporal_spatial_comparison.png`
- `top_zip_codes.png`
- `zip_temporal_comparison.png`

### Data Tables
- `substances_by_zip.csv`
  - 80 rows, 4 columns
- `top_20_zip_codes.csv`
  - 20 rows, 2 columns
- `zip_comparison_early_late.csv`
  - 15 rows, 4 columns


## Key Findings

### Hotspot ZIP Codes
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
- Note emerging vs declining crisis areas

## Methodology

- Geocodes deaths to ZIP codes
- Calculates deaths per ZIP
- Identifies top hotspot areas
- Analyzes substance-specific spatial patterns
- Compares early (2012-2017) vs late (2018-2023) periods
- Generates maps and heatmaps

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
