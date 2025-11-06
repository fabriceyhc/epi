# Cumulative Disadvantage Score

## Overview
Creates a composite index combining multiple SES indicators (poverty, income, rent burden) to measure cumulative disadvantage and its relationship with overdose deaths.

## Key Findings

### Disadvantage Score Components
Standardized z-scores (mean=0, SD=1) for:
1. **Poverty Rate** (higher = more disadvantage)
2. **Median Income** (lower = more disadvantage, inverted)
3. **Rent Burden** (higher = more disadvantage)

Final score = average of 3 z-scores

### 2023 Disadvantage Scores by Race
- **BLACK**: +0.90 (highest disadvantage)
- **LATINE**: -0.10 (moderate)
- **ASIAN**: -1.09 (low)
- **WHITE**: -1.33 (lowest disadvantage)

### Overall Relationship
- **Cumulative disadvantage ↔ Overdose rate**: r = +0.092 (p = 0.553)
- **High vs Low disadvantage**: 1.50x rate ratio
- Weak aggregate correlation, but patterns vary by component

### Individual Component Correlations
- **Poverty Rate**: r = +0.090 (p = 0.561)
- **Median Income**: r = +0.117 (p = 0.449)
- **Rent Burden**: r = +0.292 (p = 0.055) ⭐ (strongest component)

### Temporal Trends
Average disadvantage declining over time (2012: +0.40 → 2023: -0.40), suggesting improving economic conditions overall.

### Interpretation
While the composite disadvantage score shows weak correlation with overdose rates, **rent burden emerges as the most important individual component**. This suggests housing affordability may be more critical than other SES factors.

## Outputs
- `cumulative_disadvantage.png` - 6-panel visualization
- `cumulative_disadvantage_scores.csv` - Annual scores by race
- `disadvantage_overdose_rates.csv` - Merged disadvantage and overdose data
- `disadvantage_component_correlations.csv` - Individual component correlations
