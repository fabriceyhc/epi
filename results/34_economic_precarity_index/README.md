# Economic Precarity Index (Composite)

**Analysis Number**: 34
**Script**: `34_economic_precarity_index.py`
**Status**: ✅ Verified with actual results
**Last Updated**: 2025-11-05

## Overview

Creates a comprehensive economic vulnerability measure combining multiple indicators (unemployment, labor force participation) to test whether composite precarity predicts overdoses better than single indicators.

## Key Findings

### Composite Index Correlation: r = 0.205, p = 0.524 (not significant)

- Composite index shows weak positive correlation
- Does NOT outperform individual strong predictors (wages r=0.849, LFPR r=-0.770)
- Suggests specific economic mechanisms matter more than aggregate vulnerability

### Comparison to Individual Indicators

**Strongest Individual Predictors**:
1. Real Wages: r=0.849, p<0.001 ⭐
2. Labor Force Participation: r=-0.770, p=0.003 ⭐
3. Unemployment: r=-0.343 (not significant)

**Composite Index**: r=0.205 (not significant)

**Conclusion**: Simple composite averaging dilutes the strong signals from wages and LFPR. Mechanism-specific analyses are more informative than aggregate indices.

## Outputs Generated

- `precarity_index.csv` - Annual composite index with component indicators
- `precarity_correlation.csv` - Correlation statistics
- `precarity_index_timeseries.png` - Dual-axis visualization

## Data Sources

- **FRED Series**: UNRATE, CIVPART
- **Overdose Data**: LA County, 2012-2023

## Methodology

- Normalized each indicator to 0-100 scale
- Inverted protective factors (higher LFPR = lower precarity)
- Simple average of normalized components
- Compared composite to individual indicators

---

**Verification Status**: ✅ This README was generated after running the analysis
**Generated**: 2025-11-05
