# Housing Costs and Overdose Deaths

## Overview
Examines the relationship between housing costs (rent and home values) and overdose mortality patterns over time.

## Key Findings

### Housing Cost Trends (2012-2023)
- **Median rent**: +61.4% ($1,175 → $1,896/month)
- **Median home value**: +107.4% ($399,500 → $828,700)

### Extremely Strong Correlations ⭐⭐⭐
- **Rent ↔ Overdose rate**: r = +0.953 (p < 0.0001)
- **Home value ↔ Overdose rate**: r = +0.931 (p < 0.0001)

These are among the **strongest correlations observed in the entire study**.

### 2023 Rent Burden by Race
Percentage of income spent on rent:
- **BLACK**: 37.5% (Income: $60,696, Rent: $1,896)
- **LATINE**: 30.0% (Income: $75,772, Rent: $1,896)
- **ASIAN**: 22.7% (Income: $100,119, Rent: $1,896)
- **WHITE**: 21.3% (Income: $107,041, Rent: $1,896)

### Race-Specific Rent Burden Correlations
- **WHITE**: r = +0.908 (p = 0.0001)
- **BLACK**: r = +0.577 (p = 0.063)
- **LATINE**: r = -0.818 (p = 0.002) (negative correlation)
- **ASIAN**: r = +0.536 (p = 0.089)

### Years with Largest Rent Increases
1. **2021**: +8.5% (post-COVID surge)
2. **2019**: +6.6%
3. **2022**: +5.5%

### Interpretation
The housing affordability crisis shows the **strongest temporal correlation with overdose deaths** of any factor examined. Rising rents track almost perfectly with rising overdose rates (r=0.953). This suggests:
1. Housing costs may be a critical driver of overdose vulnerability
2. Economic stress from housing burden contributes to crisis
3. Black populations face highest burden (37.5% of income)

## Outputs
- `housing_costs_analysis.png` - 6-panel visualization with dual-axis plots
- `housing_costs_overdose_trends.csv` - Annual housing costs and overdose rates
- `housing_costs_by_race.csv` - Race-specific rent burden and rates
