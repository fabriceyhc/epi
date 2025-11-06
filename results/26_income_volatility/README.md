# Income Volatility and Overdose Deaths

## Overview
Examines the relationship between income instability (year-to-year fluctuations) and overdose mortality using real (inflation-adjusted) income data.

## Key Findings

### Income Stability Rankings (Coefficient of Variation)
**Lower CV = More stable income**
1. **WHITE**: 0.0523 (most stable)
2. **BLACK**: 0.0662
3. **ASIAN**: 0.0736
4. **LATINE**: 0.1125 (least stable) ⭐

Latine populations show **2.2x higher income volatility** than White populations.

### Mean Real Income (2012-2023, 2023 dollars)
- **WHITE**: $101,862 (SD: $5,328)
- **ASIAN**: $92,698 (SD: $6,819)
- **LATINE**: $65,832 (SD: $7,407)
- **BLACK**: $56,280 (SD: $3,725)

### Largest Income Declines
1. **2021 BLACK**: -5.7% (likely COVID-related)
2. **2021 WHITE**: -2.3%
3. **2014 BLACK**: -2.1%

### Correlations with Overdose Rates
- **Overall income YoY change**: r = -0.225 (p = 0.164)
- **Rolling volatility (3-year)**: r = -0.130 (p = 0.449)

**By race (income change ↔ overdose):**
- **WHITE**: r = -0.460 (p = 0.181)
- **ASIAN**: r = -0.410 (p = 0.240)
- **LATINE**: r = -0.295 (p = 0.407)
- **BLACK**: r = -0.205 (p = 0.571)

All negative correlations suggest income declines may be associated with higher overdose rates, though relationships are not statistically significant.

### Interpretation
While Latine populations experience the highest income volatility (economic instability), the relationship between income volatility and overdose rates is weak. This suggests:
1. Absolute income levels may matter more than volatility
2. Other factors (housing, poverty) may be more important
3. Economic shocks (like 2021) show sudden income drops that may contribute to overdose risk

## Outputs
- `income_volatility.png` - 6-panel visualization showing trends and volatility
- `income_volatility_metrics.csv` - Annual volatility metrics by race
- `income_volatility_overdoses.csv` - Merged income and overdose data
- `income_stability_by_race.csv` - Coefficient of variation summary
