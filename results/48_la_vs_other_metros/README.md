# LA vs Other Metro Areas - Comparative Analysis

**Analysis Number**: 48
**Script**: `48_la_vs_other_metros.py`
**Status**: ✅ Complete
**Date**: 2025-11-06

## Overview

Places LA County overdose mortality data in national context by comparing to other major US metropolitan areas from the literature review.

## Key Findings

### Comparative Table (2020 data)

| Metro Area | Black Rate | White Rate | Ratio (B/W) |
|-----------|-----------|-----------|------------|
| New York, NY | 38.2 | 32.7 | **1.17x** |
| California (state) | 41.1 | 31.2 | **1.32x** |
| National (US) | 69.0 | 45.0 | **1.53x** |
| Los Angeles County, CA | 57.2 | 36.4 | **1.57x** **← LA COUNTY** |
| Chicago, IL | 56.0 | 16.0 | **3.50x** |
| Philadelphia, PA | N/A | N/A | **5.00x** |
| Washington, D.C. | N/A | N/A | **6.00x** |
| Baltimore, MD | 118.8 | 17.0 | **6.99x** |


### LA County Position

- **Disparity Ranking**: 8 of 8 metros (1 = lowest disparity)
- **LA Ratio**: 1.57x
- **California State Ratio**: 1.32x
- **National Ratio**: 1.53x (2022 data)

### Interpretation

**Comparison to State:**
- LA County disparity (1.57x) is 19% **HIGHER** than California average (1.32x)


**Comparison to National:**
- LA County disparity is 3% **HIGHER** than national average (1.53x)


**Regional Variation:**
- Smallest disparity: New York, NY (1.17x)
- Largest disparity: Baltimore, MD (6.99x)
- **Range**: 1.17x to 6.99x

LA County falls in the **upper** half of this distribution.

### Why Disparities Vary Across Cities

Literature suggests city-level variation driven by:

1. **Fentanyl supply penetration**: Cities where fentanyl entered Black communities early (via cocaine adulteration) show higher disparities
2. **Historical drug market structure**: Legacy cocaine markets vs heroin markets
3. **Harm reduction infrastructure**: Access to naloxone, MOUD, SSPs varies by city
4. **Segregation patterns**: Residential segregation concentrates or disperses risk
5. **Economic structure**: City-specific wage stagnation, housing costs affect vulnerability

### Implications for LA

LA's moderate disparity (relative to East Coast cities like Baltimore, D.C.) may reflect:
- Later fentanyl arrival compared to East Coast
- Different drug market structure (less concentrated Black cocaine markets?)
- California's stronger harm reduction policy environment
- However, still higher than state average suggests LA-specific risk factors

## Outputs Generated

### Visualizations
- `la_vs_other_metros.png` - 2-panel figure:
  - Horizontal bar chart of disparity ratios
  - Scatter plot of Black vs White rates

### Data Tables
- `metro_comparison_table.csv` - Full comparison data
- `la_summary.csv` - LA-specific summary statistics

## Related Analyses

- **Analysis #11**: Population-Adjusted Rates (LA data used here)
- **Analysis #18**: Age-Standardized Rates (could repeat this comparison with age-adjusted rates)
- **Analysis #45**: COVID Acceleration (compares LA COVID impact to national)

## Data Sources

### LA County
- This study: Medical Examiner-Coroner data, 2012-2023
- 2020 rates calculated from original data

### Other Cities
- Literature Review (Part 1.1), Table 1
- Sources: City health departments, published studies
- Most data from 2020 (peak COVID year)

## Methodological Note

**Caution on Direct Comparison:**
- Different data sources (ME-C, vital statistics, surveillance systems)
- Different definitions (opioid-only vs all drug overdoses)
- Some cities report opioid-specific rates (Chicago, Baltimore), others all drugs (NYC)
- Age-standardization not applied uniformly across cities
- Year differences (some 2020, National is 2022)

Results should be interpreted as **approximate comparative context** rather than precise rankings.

---

**Verification Status**: ✅ LA County positioned in national context
**Generated**: 2025-11-06
