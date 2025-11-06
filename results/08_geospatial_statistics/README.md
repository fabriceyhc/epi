# Advanced Geospatial Statistical Analysis

**Analysis Number**: 08
**Script**: `08_geospatial_statistical_analysis.py`
**Status**: ✅ Verified with actual results
**Last Updated**: 2025-11-05

## Overview
Advanced spatial statistics including center of gravity, standard deviational ellipses,
DBSCAN clustering, and kernel density estimation (KDE) hotspot analysis.

## Outputs Generated

### Visualizations
- `center_of_gravity_trajectory.png`
- `dbscan_clusters.png`
- `directional_analysis.png`
- `directional_analysis_improved.png`
- `distance_from_downtown.png`
- `kde_hotspots.png`
- `movement_summary_simple.png`
- `spatial_dispersion.png`
- `standard_ellipses.png`
- `substance_centers.png`

### Data Tables
- `center_of_gravity_annual.csv`
  - 12 rows, 6 columns
- `center_of_gravity_movement.csv`
  - 12 rows, 10 columns
- `distance_from_downtown_annual.csv`
  - 12 rows, 4 columns
- `substance_centers_of_gravity.csv`
  - 8 rows, 6 columns


## Key Findings

### Center of Gravity
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
- Note statistical significance of hotspots

## Methodology

- Calculates weighted center of gravity by year
- Computes standard deviational ellipses
- Applies DBSCAN clustering algorithm
- Generates kernel density estimation (KDE) surfaces
- Analyzes distance from downtown LA
- Tracks directional trends
- Creates advanced spatial visualizations

## Interpretation

*Add interpretation of results here after reviewing outputs.*

## Data Sources

### Overdose Data
- **Source**: LA County Medical Examiner-Coroner
- **Period**: 2012-2024 (analysis typically uses 2012-2023)
- **N**: ~18,495 deaths (2012-2023)

### Additional Data
- Uses latitude/longitude coordinates from death records

## Notes

- Review the visualization files for detailed findings
- Examine CSV files for exact statistics
- See main results README for context

## Related Analyses

- See `results/README.md` for complete analysis index

---

**Verification Status**: ✅ This README was generated after running the analysis
**Generated**: 2025-11-05 21:24
