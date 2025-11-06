# Age-Standardized Overdose Rates

## Overview
Calculates age-standardized mortality rates using direct standardization to account for differences in age distributions across racial/ethnic groups, using the 2000 U.S. Standard Population as reference.

## Key Findings

### 2023 Age-Standardized Rates
- **BLACK**: 80.4 per 100,000 (crude: 84.1)
- **WHITE**: 37.5 per 100,000 (crude: 42.2)
- **LATINE**: 23.6 per 100,000 (crude: 24.2)
- **ASIAN**: 5.8 per 100,000 (crude: 5.9)

### Impact of Age-Adjustment
- Age-standardization **increases** the Black-White disparity
- **Crude disparity**: 1.99x (Black vs White)
- **Age-standardized disparity**: 2.14x (Black vs White)
- This reveals that Black populations experience higher rates even after accounting for age structure

### Interpretation
Age-standardization provides more accurate disparity estimates by controlling for different age distributions across racial/ethnic groups. The increased disparity after age-adjustment indicates that racial disparities are even larger than crude rates suggest.

## Outputs
- `age_standardized_rates.png` - 6-panel visualization
- `age_standardized_rates.csv` - Annual ASR and crude rates by race
- `age_standardized_disparities.csv` - Disparity ratios over time
- `age_specific_rates.csv` - Age-specific rates by race and year
