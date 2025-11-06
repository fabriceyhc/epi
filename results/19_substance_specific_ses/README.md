# Substance-Specific SES Patterns

## Overview
Examines whether the relationship between socioeconomic status (SES) and overdose deaths varies by substance type (methamphetamine, fentanyl, heroin, cocaine, prescription opioids).

## Key Findings

### SES Correlations by Substance
1. **Cocaine**: Strongest poverty correlation (r = +0.337, p = 0.025)
   - 4.64x higher rates in high-poverty vs low-poverty areas
2. **Heroin**: Weak negative correlation (r = -0.268, p = 0.079)
3. **Methamphetamine**: No significant correlation (r = +0.057, p = 0.713)
4. **Fentanyl**: No significant correlation (r = +0.052, p = 0.736)
5. **Prescription opioids**: No significant correlation (r = -0.198, p = 0.197)

### Substance Use Patterns by Race
**Most common substance by race (% of deaths):**
- **WHITE**: Methamphetamine (44.3%), Fentanyl (36.7%)
- **BLACK**: Methamphetamine (45.2%), Fentanyl (41.3%), **Cocaine (35.2%)**
- **LATINE**: Methamphetamine (43.5%), Fentanyl (39.2%)
- **ASIAN**: Methamphetamine (44.4%), Fentanyl (32.7%)

### Interpretation
Different substances show distinct SES patterns:
- **Cocaine** shows the strongest poverty gradient, concentrated in high-poverty areas
- **Fentanyl and methamphetamine** are more evenly distributed across SES levels
- This suggests different social determinants and distribution networks for different drug types

## Outputs
- `substance_specific_ses_patterns.png` - 9-panel visualization including scatterplots and heatmap
- `substance_ses_correlations.csv` - Correlation coefficients for each substance
- `substance_poverty_comparison.csv` - High vs low poverty rate comparisons
- `substance_by_race.csv` - Substance involvement percentages by race
