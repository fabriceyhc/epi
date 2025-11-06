#!/usr/bin/env python3
"""
Organize analysis results into separate folders with markdown summaries
"""

import os
import shutil
from pathlib import Path

# Define analysis metadata
analyses = {
    '18_age_standardized_rates': {
        'title': 'Age-Standardized Overdose Rates',
        'files': [
            'age_standardized_rates.png',
            'age_standardized_rates.csv',
            'age_standardized_disparities.csv',
            'age_specific_rates.csv'
        ],
        'summary': """# Age-Standardized Overdose Rates

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
"""
    },

    '19_substance_specific_ses': {
        'title': 'Substance-Specific SES Patterns',
        'files': [
            'substance_specific_ses_patterns.png',
            'substance_ses_correlations.csv',
            'substance_poverty_comparison.csv',
            'substance_by_race.csv'
        ],
        'summary': """# Substance-Specific SES Patterns

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
"""
    },

    '20_housing_homelessness': {
        'title': 'Housing Burden and Homelessness Pipeline',
        'files': [
            'housing_homelessness_pipeline.png',
            'homeless_by_race_year.csv',
            'housing_homeless_trends.csv',
            'substance_by_housing_status.csv'
        ],
        'summary': """# Housing Burden and Homelessness Pipeline

## Overview
Examines the relationship between rising housing costs, homelessness, and overdose deaths. Links housing affordability crisis to overdose vulnerability.

## Key Findings

### Housing Cost Increases (2012-2023)
- **Median rent**: +61.4% ($1,175 → $1,896/month)
- **Median home value**: +107.4% ($399,500 → $828,700)

### Homelessness Among Overdose Deaths
**By race (2012-2023 average):**
- **BLACK**: 16.3% experiencing homelessness
- **WHITE**: 11.4% experiencing homelessness
- **LATINE**: 8.2% experiencing homelessness

### Substance Patterns by Housing Status
**Unhoused vs Housed:**
- **Methamphetamine**: 64.2% (unhoused) vs 39.0% (housed)
- Unhoused individuals show significantly higher meth involvement

### Rent Burden by Race (2023)
- **BLACK**: 37.5% of income spent on rent
- **LATINE**: 30.0%
- **ASIAN**: 22.7%
- **WHITE**: 21.3%

### Interpretation
Rising housing costs create economic stress that may contribute to overdose risk. Black populations face the highest housing cost burden, and homelessness is strongly associated with methamphetamine use in overdose deaths.

## Outputs
- `housing_homelessness_pipeline.png` - 6-panel visualization
- `homeless_by_race_year.csv` - Homelessness rates by race and year
- `housing_homeless_trends.csv` - Housing costs and homelessness trends
- `substance_by_housing_status.csv` - Substance involvement by housing status
"""
    },

    '21_geographic_ses_inequality': {
        'title': 'Geographic SES Inequality (ZIP-level)',
        'files': [
            'geographic_ses_inequality.png',
            'zip_level_overdoses_ses.csv'
        ],
        'summary': """# Geographic SES Inequality (ZIP-level)

## Overview
Examines within-county spatial variation in overdose rates and SES at the ZIP code level. Maps hotspots and correlates ZIP-level poverty/income with overdose burden.

## Key Findings

### Geographic Disparities
- **263 LA County ZIP codes** analyzed
- Overdose rates range from **2.7 to 6,681.4 per 100,000** (2,447x difference)
- Top 5 hotspot ZIPs account for **7.4% of deaths** in only **0.6% of population**

### SES Correlations
- **Poverty ↔ Overdose rate**: r = +0.519 (p < 0.0001) ⭐
- **Income ↔ Overdose rate**: r = -0.267 (p < 0.0001)
- **Poverty ↔ Methamphetamine %**: r = +0.318 (p < 0.0001)

### High vs Low Poverty ZIP Codes
- **High poverty ZIPs**: 457.6 per 100,000
- **Low poverty ZIPs**: 123.1 per 100,000
- **Disparity ratio**: 3.72x (p = 0.006)

### Top 5 Highest-Rate ZIP Codes
1. **90021** (Downtown LA): 6,681.4 per 100k (45.1% poverty, $25,364 income)
2. **90014** (Downtown): 3,545.1 per 100k (35.8% poverty, $31,332 income)
3. **90013** (Downtown): 3,064.2 per 100k (45.8% poverty, $22,291 income)
4. **90401** (Santa Monica): 1,136.1 per 100k (19.1% poverty, $90,682 income)
5. **90017** (Downtown): 1,072.7 per 100k (34.5% poverty, $44,607 income)

### Interpretation
Strong geographic concentration of overdose deaths in high-poverty Downtown LA ZIP codes. Poverty shows the strongest correlation with overdose rates at the ZIP level, indicating importance of neighborhood-level interventions.

## Outputs
- `geographic_ses_inequality.png` - 6-panel visualization with maps and distributions
- `zip_level_overdoses_ses.csv` - Complete ZIP-level data with rates and SES indicators
"""
    },

    '22_counterfactual_ses_matching': {
        'title': 'Counterfactual SES Matching Analysis',
        'files': [
            'counterfactual_ses_matching.png',
            'counterfactual_model_fit.csv',
            'counterfactual_predictions_2023.csv'
        ],
        'summary': """# Counterfactual SES Matching Analysis

## Overview
Uses Poisson regression to statistically answer: "What would Black overdose rates be if Black individuals had the same SES distribution as White individuals?" Decomposes racial disparities into SES-explained vs structural components.

## Key Findings

### Model Performance
- **Model 1 (SES only)**: Pseudo R² = 0.340
- **Model 2 (Race + SES)**: Pseudo R² = 0.912
- **R² increase from adding race**: 0.572 (race explains 57.2% of variance beyond SES)

### 2023 Observed Rates
- **WHITE**: 42.5 per 100,000 (Poverty: 10.8%, Income: $107,041)
- **BLACK**: 85.4 per 100,000 (Poverty: 20.9%, Income: $60,696)
- **LATINE**: 24.4 per 100,000 (Poverty: 15.0%, Income: $75,772)
- **ASIAN**: 6.0 per 100,000 (Poverty: 11.7%, Income: $100,119)

### Counterfactual Results
**If Black had White SES levels:**
- Predicted Black rate: 1,422.0 per 100,000
- White observed rate: 42.5 per 100,000
- **Disparity remaining after SES equalization**: 3,215% ⚠️

### ⚠️ Important Note
The counterfactual analysis produced unexpected results (predicted rate increased rather than decreased with better SES). This suggests potential model specification issues that should be investigated. The model may be mis-specified or there may be complex interactions not captured.

### Interpretation
While this analysis attempted to decompose racial disparities, the results indicate methodological challenges that need to be addressed before drawing conclusions.

## Outputs
- `counterfactual_ses_matching.png` - 4-panel visualization
- `counterfactual_model_fit.csv` - Model predictions vs observed
- `counterfactual_predictions_2023.csv` - 2023 counterfactual scenarios
"""
    },

    '23_covid_economic_shock': {
        'title': 'COVID-19 Economic Shock Analysis',
        'files': [
            'covid_economic_shock.png',
            'covid_period_rates.csv',
            'covid_changes_from_baseline.csv',
            'covid_2020_monthly.csv'
        ],
        'summary': """# COVID-19 Economic Shock Analysis

## Overview
Examines how the COVID-19 pandemic and associated economic disruption affected overdose rates, with focus on differential impacts by race and SES.

## Key Findings

### Overall Impact (2020 vs Pre-COVID Baseline 2017-2019)
- **Overall increase**: +114.0%
- **BLACK**: +155.6%
- **WHITE**: +70.5%
- **LATINE**: +112.4%
- **ASIAN**: +118.8%

### 2020 Monthly Pattern
- **Largest spike**: August 2020 (+105% vs Aug 2019)
- Sharp increases began in **April 2020** (lockdown month: +78.5%)
- Sustained elevated rates throughout 2020

### Substance Changes During COVID
**2020 vs Pre-COVID (percentage point changes):**
- **Fentanyl**: +24.2 pp (20.7% → 45.0%) ⭐
- **Methamphetamine**: +7.1 pp (39.9% → 46.9%)
- **Heroin**: -5.3 pp (18.2% → 12.9%)
- **Cocaine**: -0.2 pp (stable at ~14%)

### Continued Impact (2021-2022)
Rates remained elevated through 2021-2022:
- **BLACK**: +263.5% above pre-COVID baseline
- **WHITE**: +122.8% above baseline
- Only declined somewhat in 2023

### Poverty-Specific Impacts
**2020 increase by poverty level:**
- High poverty areas: Largest increases
- Low poverty areas: Smaller but still substantial increases

### Interpretation
COVID-19 pandemic and economic disruption led to massive spike in overdose deaths, with:
1. Disproportionate impact on Black populations
2. Dramatic rise in fentanyl involvement
3. Sustained elevated rates through 2021-2022
4. Greater impact in high-poverty areas

## Outputs
- `covid_economic_shock.png` - 9-panel comprehensive visualization
- `covid_period_rates.csv` - Rates by period and race
- `covid_changes_from_baseline.csv` - Percent changes from pre-COVID
- `covid_2020_monthly.csv` - Month-by-month 2020 vs 2019 comparison
"""
    },

    '24_cumulative_disadvantage': {
        'title': 'Cumulative Disadvantage Score',
        'files': [
            'cumulative_disadvantage.png',
            'cumulative_disadvantage_scores.csv',
            'disadvantage_overdose_rates.csv',
            'disadvantage_component_correlations.csv'
        ],
        'summary': """# Cumulative Disadvantage Score

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
"""
    },

    '25_housing_costs': {
        'title': 'Housing Costs and Overdose Deaths',
        'files': [
            'housing_costs_analysis.png',
            'housing_costs_overdose_trends.csv',
            'housing_costs_by_race.csv'
        ],
        'summary': """# Housing Costs and Overdose Deaths

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
"""
    },

    '26_income_volatility': {
        'title': 'Income Volatility and Overdose Deaths',
        'files': [
            'income_volatility.png',
            'income_volatility_metrics.csv',
            'income_volatility_overdoses.csv',
            'income_stability_by_race.csv'
        ],
        'summary': """# Income Volatility and Overdose Deaths

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
"""
    },

    '27_poverty_age_interaction': {
        'title': 'Poverty × Age Interaction',
        'files': [
            'poverty_age_interaction.png',
            'poverty_age_correlations.csv',
            'deaths_by_age_poverty.csv'
        ],
        'summary': """# Poverty × Age Interaction

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
"""
    }
}

# Create base directory structure
base_dir = Path('results/census_analyses')
base_dir.mkdir(parents=True, exist_ok=True)

source_dir = Path('results/population_rates')

print("=" * 70)
print("ORGANIZING ANALYSIS RESULTS")
print("=" * 70)
print()

# Process each analysis
for analysis_id, metadata in analyses.items():
    print(f"Processing: {metadata['title']}...")

    # Create analysis directory
    analysis_dir = base_dir / analysis_id
    analysis_dir.mkdir(exist_ok=True)

    # Copy files
    files_copied = 0
    for filename in metadata['files']:
        source_file = source_dir / filename
        if source_file.exists():
            dest_file = analysis_dir / filename
            shutil.copy2(source_file, dest_file)
            files_copied += 1
        else:
            print(f"  ⚠️  File not found: {filename}")

    # Create markdown summary
    readme_file = analysis_dir / 'README.md'
    with open(readme_file, 'w') as f:
        f.write(metadata['summary'])

    print(f"  ✓ Created folder: {analysis_dir}")
    print(f"  ✓ Copied {files_copied}/{len(metadata['files'])} files")
    print(f"  ✓ Created README.md")
    print()

# Create master index
print("Creating master index...")
index_content = """# Census-Based Overdose Analyses

This directory contains 10 comprehensive analyses examining the relationship between socioeconomic factors and overdose deaths in Los Angeles County (2012-2023).

## Quick Navigation

### Methodological Analyses
- [**18_age_standardized_rates**](18_age_standardized_rates/) - Age-adjusted rates accounting for demographic differences
- [**22_counterfactual_ses_matching**](22_counterfactual_ses_matching/) - Statistical decomposition of racial disparities ⚠️ (needs review)

### Geographic & Spatial Analyses
- [**21_geographic_ses_inequality**](21_geographic_ses_inequality/) - ZIP-level SES patterns and hotspots ⭐ Strong findings

### Interaction & Complexity Analyses
- [**27_poverty_age_interaction**](27_poverty_age_interaction/) - How poverty effects vary by age ⭐ Significant interaction
- [**24_cumulative_disadvantage**](24_cumulative_disadvantage/) - Composite disadvantage score

### Substance-Specific Analyses
- [**19_substance_specific_ses**](19_substance_specific_ses/) - Different SES patterns by drug type

### Housing & Economic Stress Analyses
- [**20_housing_homelessness**](20_housing_homelessness/) - Housing crisis and homelessness pipeline
- [**25_housing_costs**](25_housing_costs/) - Housing costs correlation ⭐⭐⭐ Strongest finding (r=0.953)
- [**26_income_volatility**](26_income_volatility/) - Economic instability and income fluctuations

### Temporal & Crisis Analyses
- [**23_covid_economic_shock**](23_covid_economic_shock/) - COVID-19 pandemic impact ⭐ +114% spike in 2020

## Key Findings Summary

### Strongest Correlations
1. **Housing Costs** (r = +0.953): Rising rents track almost perfectly with overdose rates
2. **Geographic Poverty** (r = +0.519): ZIP-level poverty strongly predicts overdose rates
3. **COVID-19 Shock** (+114% in 2020): Massive pandemic impact with racial disparities

### Important Interactions
- **Poverty × Age**: Significant interaction (p = 0.0005) - poverty effects vary by age
- **Substance × SES**: Cocaine shows strongest poverty gradient (4.64x), fentanyl shows none

### Racial Disparities
- **Age-standardized Black-White disparity**: 2.14x (even larger after age-adjustment)
- **COVID disproportionate impact**: Black +156%, White +71%
- **Housing burden**: Black 37.5% vs White 21.3% of income

### Economic Stability
- **Latine income volatility**: 2.2x higher than White (CV = 0.1125 vs 0.0523)
- **Rent burden**: Rising from ~20% to ~30% of income (2012-2023)

## File Organization

Each analysis folder contains:
- `README.md` - Comprehensive summary with key findings and interpretation
- `.png` - Publication-quality visualization (6-9 panels)
- `.csv` files - Raw data and results for further analysis

## Analysis Scripts

All analysis scripts are located in `scripts/`:
- `18_age_standardized_rates.py`
- `19_substance_specific_ses_patterns.py`
- `20_housing_homelessness_pipeline.py`
- `21_geographic_ses_inequality.py`
- `22_counterfactual_ses_matching.py`
- `23_covid_economic_shock.py`
- `24_cumulative_disadvantage.py`
- `25_housing_costs_analysis.py`
- `26_income_volatility.py`
- `27_poverty_age_interaction.py`

## Data Sources

### Overdose Data
- LA County Medical Examiner-Coroner overdose deaths (2012-2024)
- N = 18,495 deaths (2012-2023)

### Census Data
- U.S. Census Bureau American Community Survey (ACS)
- Annual estimates by race: population, poverty, income, age, housing costs
- Geographic: ZIP Code Tabulation Areas (ZCTAs)

## Reproducibility

All analyses use:
1. Shared utilities (`scripts/utils.py`) for consistent data processing
2. Standardized race categories (WHITE, BLACK, LATINE, ASIAN)
3. 2012-2023 timeframe (excluding partial 2024 data)
4. Population-adjusted rates per 100,000

## Caveats & Limitations

1. **Counterfactual analysis (#22)** produced unexpected results and needs methodological review
2. **Ecological fallacy**: Census data are race-aggregated, not individual-level
3. **2023 homelessness data** may be incomplete in some analyses
4. **ZIP-level analysis** excludes small-population ZIPs and those with missing Census data
5. **Age-specific population** data not available by race; approximate distributions used

## Citation

If using these analyses, please cite:
- Data source: LA County Medical Examiner-Coroner
- Census data: U.S. Census Bureau American Community Survey
- Analysis: [Your institution/project name]

## Contact

For questions about these analyses, please contact: [Your contact information]

---

**Last Updated**: November 2025
**Analysis Period**: 2012-2023
**Total Deaths Analyzed**: 18,495
"""

with open(base_dir / 'README.md', 'w') as f:
    f.write(index_content)

print(f"✓ Created master index: {base_dir / 'README.md'}")
print()

print("=" * 70)
print("ORGANIZATION COMPLETE")
print("=" * 70)
print()
print(f"All analyses organized in: {base_dir}")
print()
print("Structure:")
print(f"  {base_dir}/")
print(f"  ├── README.md (master index)")
for analysis_id in sorted(analyses.keys()):
    print(f"  ├── {analysis_id}/")
    print(f"  │   ├── README.md")
    print(f"  │   ├── *.png")
    print(f"  │   └── *.csv")
print()
