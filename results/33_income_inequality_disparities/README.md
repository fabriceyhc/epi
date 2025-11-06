# Income Inequality and Overdose Disparities

**Analysis Number**: 33
**Script**: `33_income_inequality_disparities.py`
**Status**: ✅ Verified with actual results
**Last Updated**: 2025-11-05

## Overview

Tests whether rising income inequality (Gini coefficient) correlates with widening Black-White overdose disparities.

## Key Findings

### Gini-Disparity Correlation: r = -0.176, p = 0.584 (not significant)

- Rising inequality does NOT significantly predict widening racial disparities
- Black-White disparity ratio tracked independently over time
- Suggests racial disparities driven by factors beyond aggregate inequality

### Disparity Trend

Black/White overdose rate ratios calculated from population-adjusted rates show evolution over 2012-2023 period, with disparities widening dramatically (see Analysis #11 for detailed rates).

## Outputs Generated

- `inequality_disparity_trends.csv` - Gini index and disparity ratios by year
- `inequality_disparity_correlation.csv` - Correlation statistics
- `disparity_trend.png` - Visualization of disparity evolution

## Data Sources

- **FRED Series**: SIPOVGINIUSA (Gini Index)
- **Population Rates**: From Analysis #11
- **Overdose Data**: LA County, 2012-2023

---

**Verification Status**: ✅ This README was generated after running the analysis
**Generated**: 2025-11-05
