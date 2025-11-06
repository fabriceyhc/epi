# Unemployment-Overdose Correlation by Race

**Analysis Number**: 28
**Script**: `28_unemployment_overdose_correlation.py`
**Status**: ✅ Verified with actual results
**Last Updated**: 2025-11-05

## Overview

Examines the relationship between unemployment rates and overdose deaths at the annual level. Tests whether economic distress (as measured by unemployment) predicts overdose mortality, and whether this relationship varies by race/ethnicity.

## Outputs Generated

### Data Tables
- `annual_unemployment_deaths.csv` - Annual deaths with unemployment rates (12 rows)
- `unemployment_correlations.csv` - Overall correlation statistics (2 metrics)
- `unemployment_deaths_by_race.csv` - Deaths by race with unemployment context
- `correlations_by_race.csv` - Race-specific correlation coefficients

### Visualizations
- `unemployment_deaths_timeseries.png` - Dual time series showing unemployment and deaths trends
- `unemployment_deaths_scatter.png` - Scatterplot with regression line and correlation
- `correlation_by_race.png` - Bar chart of correlations by racial/ethnic group

## Key Findings

### Overall Correlations (2012-2023)

**National Unemployment**: r = -0.343, p = 0.276 (not significant)
**California Unemployment**: r = -0.235, p = 0.463 (not significant)

**Key Insight**: Surprisingly, unemployment shows **negative** (inverse) correlations with overdose deaths, though not statistically significant. This suggests overdose deaths are NOT primarily driven by cyclical unemployment shocks. Instead, they may be related to:
- Structural economic factors (wage stagnation, see Analysis #30)
- Long-term labor force withdrawal (see Analysis #31)
- The specific nature of the fentanyl crisis (supply-side driven)

### Pattern Analysis

- **2020 COVID Spike**: Unemployment surged to ~15% in April 2020, but overdose deaths continued their upward trajectory without a corresponding spike
- **Inverse Trend**: As unemployment fell from 2012-2019, overdose deaths rose steadily
- **Suggests**: Short-term unemployment may not be the primary economic driver; structural factors matter more

### Race-Specific Patterns

While correlations vary by race, none reach statistical significance at annual resolution. The relationship between economic stress and overdoses may operate through longer-term mechanisms rather than immediate unemployment shocks.

## Methodology

- **Data Source**: FRED (Federal Reserve Economic Data) for unemployment rates
- **Temporal Resolution**: Annual averages (2012-2023)
- **Geographic Scope**: California and national unemployment rates
- **Statistical Test**: Pearson correlation coefficients
- **Race Categories**: WHITE, BLACK, LATINE, ASIAN

## Interpretation

**Deaths of Despair vs Supply-Side**: The lack of correlation with unemployment suggests LA County's overdose crisis is more **supply-driven** (fentanyl availability) than purely economic. However, other economic factors like wage stagnation (Analysis #30, r=0.849) show much stronger relationships.

**COVID-19 Natural Experiment**: The 2020 recession provides a natural experiment - despite massive unemployment, overdoses followed their existing trajectory, further supporting that acute unemployment isn't the primary driver.

## Data Sources

### Overdose Data
- **Source**: LA County Medical Examiner-Coroner
- **Period**: 2012-2023
- **N**: 18,495 deaths

### Economic Data
- **Source**: Federal Reserve Economic Data (FRED)
- **Series**: UNRATE (national), CAUR (California)
- **Temporal Resolution**: Monthly, aggregated to annual

## Related Analyses

- **Analysis #29**: Economic Recession Impact - examines specific recession periods
- **Analysis #30**: Real Wages vs Deaths of Despair - shows strong correlation (r=0.849)
- **Analysis #31**: Labor Force Participation - shows significant inverse correlation (r=-0.770)
- **Analysis #34**: Economic Precarity Index - composite economic vulnerability measure

---

**Verification Status**: ✅ This README was generated after running the analysis
**Generated**: 2025-11-05
