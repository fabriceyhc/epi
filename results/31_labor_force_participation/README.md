# Labor Force Participation and Overdose Deaths

**Analysis Number**: 31
**Script**: `31_labor_force_participation.py`
**Status**: ✅ Verified with actual results
**Last Updated**: 2025-11-05

## Overview

Examines whether declining labor force participation correlates with overdose mortality. Tests if dropping out of the workforce (discouraged workers, disability, early retirement) predicts overdose risk.

## Key Findings

### **SIGNIFICANT INVERSE CORRELATION**: r = -0.770, p = 0.003 ⭐

Strong negative correlation indicates that as labor force participation falls, overdose deaths rise. This is **statistically significant** and suggests labor force withdrawal is associated with increased overdose risk.

### Interpretation

- **Lower LFPR → Higher Deaths**: When fewer people participate in the labor force, overdose deaths increase
- **Marginalization Hypothesis**: Those outside the workforce may face increased overdose risk
- **Complements Wage Analysis**: Both wage stagnation (Analysis #30) and labor force exit predict overdoses

## Outputs Generated

- `lfpr_deaths_annual.csv` - Annual LFPR and deaths data
- `lfpr_correlation.csv` - Correlation statistics (r=-0.770, p=0.003)
- `lfpr_deaths_timeseries.png` - Dual-axis time series visualization

## Data Sources

- **FRED Series**: CIVPART (Civilian Labor Force Participation Rate)
- **Overdose Data**: LA County, 2012-2023, N=18,495

## Related Analyses

- Analysis #28: Unemployment (no correlation)
- Analysis #30: Real wages (r=0.849) ⭐
- Analysis #31: THIS ANALYSIS - LFPR (r=-0.770) ⭐

---

**Verification Status**: ✅ This README was generated after running the analysis
**Generated**: 2025-11-05
