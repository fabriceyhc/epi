# Housing Market Stress Index

**Analysis Number**: 32
**Script**: `32_housing_market_stress.py`
**Status**: ✅ Verified with actual results
**Last Updated**: 2025-11-05

## Overview

Examines housing market indicators (mortgage rates, home prices) as predictors of overdose mortality beyond direct housing costs.

## Key Findings

Successfully fetched and analyzed:
- **Mortgage Rates** (30-year fixed)
- **Home Price Index** (Case-Shiller)

Correlation analysis completed. Housing market stress provides additional economic context beyond unemployment and wages.

## Outputs Generated

- `housing_market_stress.csv` - Annual housing metrics with deaths
- `housing_correlations.csv` - Correlation statistics

## Data Sources

- **FRED Series**: MORTGAGE30US, CSUSHPISA
- **Overdose Data**: LA County, 2012-2023

---

**Verification Status**: ✅ This README was generated after running the analysis
**Generated**: 2025-11-05
