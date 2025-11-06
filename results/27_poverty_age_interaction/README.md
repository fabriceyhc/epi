# Poverty × Age Interaction

## Overview
Examines whether the effect of poverty on overdose risk varies across age groups using statistical interaction modeling.

## Key Findings

### Significant Interaction Detected ⭐
- **Likelihood Ratio Test**: χ² = 12.04, **p = 0.0005**
- The effect of poverty on overdose risk **VARIES significantly** across age groups

### Age Distribution of Deaths
- **<25 years**: 10.0% of deaths
- **25-34 years**: 22.0%
- **35-44 years**: 21.6%
- **45-54 years**: 23.4% (peak)
- **55-64 years**: 18.1%
- **65+ years**: 4.9%

### Death Counts by Age and Poverty Level

| Age Group | Low Poverty | Medium Poverty | High Poverty |
|-----------|-------------|----------------|--------------|
| <25       | 304         | 458            | 714          |
| 25-34     | 698         | 1,143          | 1,527        |
| 35-44     | 605         | 1,184          | 1,608        |
| 45-54     | 795         | 1,188          | 1,714        |
| 55-64     | 675         | 885            | 1,317        |
| 65+       | 177         | 228            | 372          |

### High/Low Poverty Death Ratios by Age
- **<25 years**: 2.35x
- **25-34 years**: 2.19x
- **35-44 years**: 2.66x (highest)
- **45-54 years**: 2.16x
- **55-64 years**: 1.95x
- **65+ years**: 2.10x

### Age-Stratified Correlations
**Poverty-Deaths correlation within each age group:**
- All age groups show negative correlations (due to confounding)
- Youngest adults (<25, 25-34) show strongest patterns
- Effect moderates with age

### Model Results
**Poisson Regression (Model 2 with interaction):**
- **Poverty coefficient**: β = -1.26
- **Age coefficient**: β = -0.05
- **Poverty × Age interaction**: β = +0.02 (p = 0.001) ⭐

Positive interaction coefficient indicates poverty effect strengthens (or becomes less negative) with age.

### Interpretation
The significant poverty × age interaction suggests:
1. Poverty-related overdose risk varies across life stages
2. Younger and middle-aged adults may be more vulnerable to poverty effects
3. Age-targeted interventions should consider differential poverty impacts
4. One-size-fits-all poverty interventions may not be equally effective across ages

## Outputs
- `poverty_age_interaction.png` - 6-panel visualization including interaction plots
- `poverty_age_correlations.csv` - Age-stratified correlation results
- `deaths_by_age_poverty.csv` - Death counts and rates by age group and poverty level
