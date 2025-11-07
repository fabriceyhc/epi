# COVID-19 Acceleration by Race

**Analysis Number**: 45
**Script**: `45_covid_acceleration_by_race.py`
**Status**: ✅ Complete
**Date**: 2025-11-06

## Overview

Quantifies the disproportionate acceleration of overdose mortality during COVID-19 by race, testing whether LA County replicates national findings (44% Black increase, 2019-2020).

## Key Findings

### Approach 1: Year-over-Year Change (2019 → 2020)

| Race | 2019 Rate | 2020 Rate | Absolute Change | Percent Change |
|------|-----------|-----------|----------------|----------------|
| **WHITE** | 24.5 | 36.4 | +11.9 | **+48.8%** |
| **LATINE** | 9.9 | 16.8 | +6.9 | **+69.2%** |
| **BLACK** | 27.9 | 57.2 | +29.3 | **+104.8%** |
| **ASIAN** | 2.2 | 5.4 | +3.2 | **+144.0%** |


**Comparison to Literature:**
- National (2019→2020): BLACK +44%
- California (2019→2020): BLACK +52.4%
- **LA County (2019→2020): BLACK +104.8%**

### Approach 2: Excess Deaths (Forecast-Based)

**2020 Excess Mortality (Observed - Expected):**

| Race | Excess Deaths | % Above Expected |
|------|--------------|-----------------|
| **WHITE** | +283 | +43.5% |
| **BLACK** | +227 | +109.0% |
| **LATINE** | +381 | +77.3% |
| **ASIAN** | +38 | +93.3% |


**Total Excess Deaths (2020-2021 combined):**

- **ASIAN**: +67 deaths
- **BLACK**: +546 deaths
- **LATINE**: +966 deaths
- **WHITE**: +767 deaths


### Approach 3: Recovery Analysis

Did rates decline post-COVID peak (2021 → 2023)?

- **WHITE**: 2021: 47.3 → 2023: 42.5 (-10.3%) - **Declined ↓**
- **BLACK**: 2021: 74.2 → 2023: 85.4 (+15.1%) - **Increased ↑**
- **LATINE**: 2021: 22.4 → 2023: 24.4 (+8.6%) - **Increased ↑**
- **ASIAN**: 2021: 5.0 → 2023: 6.0 (+19.1%) - **Increased ↑**


## Interpretation

### Validates National Trend

LA County data confirms the national finding of disproportionate COVID-era acceleration:
- Black mortality increased substantially during COVID
- Acceleration comparable to or exceeding national averages
- Consistent with syndemic theory: COVID + pre-existing vulnerabilities

### Syndemic Mechanisms

Literature identifies structural drivers:
1. **Essential worker status**: Black workers less able to work from home (19.7% vs 29.9% for White)
2. **Housing density**: Overcrowding in essential worker households prevents distancing
3. **Treatment disruption**: COVID lockdowns severed access to MOUD, SSPs, recovery support
4. **Economic stress**: Job insecurity, isolation, trauma

### Recovery Patterns

Post-2021 trajectories reveal:
- Most groups show **no recovery** (rates remain elevated or continue rising)
- Consistent with literature: "Deaths tripled during COVID and remained elevated"
- Suggests permanent supply-side shift (fentanyl saturation) rather than temporary COVID stress

## Outputs Generated

### Visualizations
- `covid_acceleration_by_race.png` - 4-panel figure showing:
  - Time series with COVID period highlighted
  - 2019→2020 percent change by race
  - 2020 excess deaths
  - Recovery trajectories 2021-2023

### Data Tables
- `2019_2020_percent_change.csv` - Year-over-year changes
- `forecast_excess_deaths.csv` - Expected vs observed for 2020-2021
- `total_excess_deaths_2020_2021.csv` - Cumulative excess by race
- `recovery_trajectories_2021_2023.csv` - Post-COVID rates

## Related Analyses

- **Analysis #07**: COVID-19 Basic Impact (initial overview)
- **Analysis #23**: COVID Economic Shock (links to economic indicators)
- **Analysis #01**: Fentanyl Timeline (shows fentanyl surge during COVID)

## Methodology

### Forecast Approach

Used simple linear regression on 2012-2019 data to forecast "expected" 2020-2021 rates assuming pre-COVID trends continued. Excess deaths = Observed - Expected.

**Assumptions:**
- Linear pre-COVID trend (reasonable approximation for most races)
- No structural changes absent COVID (counterfactual assumption)

**Limitations:**
- Fentanyl was already surging pre-COVID (some acceleration may be independent)
- Population denominator may have changed during COVID (migration)

## Data Sources

### Overdose Data
- LA County Medical Examiner-Coroner, 2012-2023
- N = {len(df):,} deaths

### Population Data
- US Census / American Community Survey
- Annual population estimates by race

---

**Verification Status**: ✅ Confirms national COVID-era racial disparities in LA County
**Generated**: 2025-11-06
