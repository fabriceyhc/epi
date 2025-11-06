# Economic Recession Impact Analysis

**Analysis Number**: 29
**Script**: `29_economic_recession_impact.py`
**Status**: ✅ Verified with actual results
**Last Updated**: 2025-11-05

## Overview

Compares overdose death patterns across three periods: Pre-Pandemic (2012-2019), Pandemic (2020-2021), and Post-Pandemic (2022-2023). Examines how the COVID-19 economic shock affected overdose mortality.

## Key Findings

### Period Comparison

**Pre-Pandemic (2012-2019)**:
- Mean annual deaths: ~880/year
- Gradual increase phase

**Pandemic (2020-2021)**:
- Mean annual deaths: ~2,655/year (**+202% from pre-pandemic**)
- Rapid acceleration during economic shock

**Post-Pandemic (2022-2023)**:
- Mean annual deaths: ~3,073/year (**+249% from pre-pandemic**)
- Deaths remained elevated despite economic recovery

### Key Insight

Overdose deaths **tripled** from pre-pandemic baseline and remained elevated even after economic recovery, suggesting the pandemic triggered a **permanent shift** in overdose risk rather than a temporary spike.

## Outputs Generated

- `period_comparison.csv` - Statistical summary by period
- `recession_impact_by_race.csv` - Race-stratified period analysis
- `recession_period_comparison.png` - Visualization by period and race

## Data Sources

- LA County Medical Examiner-Coroner, 2012-2023, N=18,495

## Related Analyses

- Analysis #07: COVID-19 Impact (Basic)
- Analysis #23: COVID Economic Shock (with SES breakdown)
- Analysis #28: Unemployment correlation

---

**Verification Status**: ✅ This README was generated after running the analysis
**Generated**: 2025-11-05
