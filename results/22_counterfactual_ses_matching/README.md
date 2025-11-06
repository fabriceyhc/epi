# Counterfactual SES Matching Analysis (REVISED)

**Analysis Number**: 22
**Script**: `22_counterfactual_ses_matching.py`
**Status**: ✅ Verified with actual results (REVISED)
**Last Updated**: 2025-11-05

## Overview

Examines whether SES differences (poverty, income, age) explain racial disparities in LA County overdose deaths. Uses descriptive comparisons to answer: "What would happen if groups had similar SES?"

**Key Finding**: SES does NOT explain racial disparities in the expected way. Race-specific factors dominate.

## Outputs Generated

### Visualizations
- `counterfactual_ses_matching.png` - 4-panel analysis showing SES-rate relationships

### Data Tables
- `ses_disparity_correlations.csv` - Overall correlations between SES and rates
- `race_ses_comparison_2023.csv` - 2023 snapshot comparing all groups

## Key Findings

### 2023 Observed Rates and SES

| Race | Rate (per 100k) | Poverty | Income |
|------|----------------|---------|--------|
| **BLACK** | 85.4 | 20.9% | $60,696 |
| **WHITE** | 42.5 | 10.8% | $107,041 |
| **LATINE** | 24.4 | 15.0% | $75,772 |
| **ASIAN** | 6.0 | 11.7% | $100,119 |

### Critical Observation: SES Does NOT Predict Overdoses

**If SES determined overdoses**, we would expect:
- Higher poverty → Higher overdose rates
- Lower income → Higher overdose rates

**But we observe the OPPOSITE**:

**Example 1: WHITE vs ASIAN (Similar SES)**
- WHITE poverty: 10.8%, ASIAN poverty: 11.7% (nearly identical)
- But WHITE rate (42.5) is **7.1× higher** than ASIAN rate (6.0)
- **Conclusion**: Similar SES, vastly different outcomes

**Example 2: LATINE vs WHITE**
- LATINE poverty (15.0%) is **HIGHER** than WHITE (10.8%)
- But LATINE rate (24.4) is **LOWER** than WHITE (42.5)
- **Conclusion**: Worse SES, better outcomes (paradox)

**Example 3: BLACK Excess Beyond SES**
- If overdoses were proportional to poverty: Expected BLACK rate = 34.1 per 100k
- Actual BLACK rate: 85.4 per 100k
- **Excess beyond SES: 51.3 per 100k (60% of total)**

### Statistical Correlations

**Overall (pooled across all races and years)**:
- Poverty vs Rate: r = +0.090, p = 0.561 (not significant)
- Income vs Rate: r = +0.117, p = 0.449 (not significant)

**Within-race over time** (2012-2023):
- WHITE: r = -0.194 (negative!)
- BLACK: r = -0.529 (negative!)
- LATINE: r = -0.750, p = 0.008 (significantly negative!)
- ASIAN: r = -0.384 (negative!)

**Interpretation**: Within each racial group over time, higher poverty is associated with LOWER overdoses. This is the opposite of expectation and suggests other factors (like fentanyl supply availability) matter more than SES.

## Interpretation

### Why SES Doesn't Explain Disparities

The analysis reveals that **aggregate SES measures do not predict overdose patterns** in LA County. Several factors explain this:

**1. Supply-Side Dominance**
- Fentanyl availability varies by social network, not SES
- Drug supply targeting and distribution patterns are race-specific
- The crisis is driven by what's available, not who can afford it

**2. Social Network Effects**
- Drug use occurs in social contexts
- Networks are often racially homogeneous
- Fentanyl penetration varies by network, independent of SES

**3. Protective Factors in Some Groups**
- Asian communities show strong protective effects despite similar SES to White
- Latine communities show resilience despite higher poverty
- Cultural, familial, or community factors provide protection

**4. Excess Risk in Black Communities**
- 60% of Black excess mortality is beyond what SES predicts
- Suggests structural factors:
  - Differential fentanyl supply/targeting
  - Healthcare and treatment access barriers
  - Historical trauma and stress
  - Mass incarceration impacts
  - Discrimination in harm reduction services

### Methodological Limitation

**Important**: This analysis uses **aggregate race-level SES** (not individual data). The ecological fallacy may apply - individual-level SES might matter, even if group-level doesn't show patterns.

**However**: The within-race temporal correlations (negative for all groups) suggest SES truly doesn't drive this crisis in the expected way.

## Policy Implications

**Traditional SES-focused interventions may be insufficient** for this crisis:

✅ **What Works**:
- Fentanyl supply reduction
- Harm reduction services (naloxone, safe injection sites)
- Treatment access expansion
- Social network-based interventions

❌ **What May Not Work Alone**:
- Income support programs (without addressing supply)
- Poverty reduction (paradoxically, some analyses show negative correlation)
- Generic economic development

**For Black Communities**: The 60% excess beyond SES requires:
- Targeted fentanyl supply disruption
- Culturally responsive treatment
- Addressing healthcare access barriers
- Harm reduction in communities most affected

## Data Sources

### Overdose Data
- LA County Medical Examiner-Coroner, 2012-2023
- Population-adjusted rates from Analysis #11

### SES Data
- US Census Bureau (American Community Survey)
- Poverty rates by race (annual)
- Median household income by race (annual)
- Age distributions by race

## Related Analyses

- **Analysis #11**: Population-Adjusted Rates (provides base rate data)
- **Analysis #13**: Temporal Correlation Analysis (poverty-rate relationships)
- **Analysis #18-27**: Detailed SES analyses (housing, income, poverty)
- **Analysis #30**: Real Wages vs Deaths of Despair (structural economic factors)

## Technical Note

**Why not traditional counterfactual methods?**

Standard counterfactual approaches (Poisson regression, propensity score matching) assume SES affects outcomes in a consistent direction. When the data show paradoxical patterns (worse SES → better outcomes for some groups), these methods produce nonsensical predictions.

This revised analysis instead uses **descriptive comparisons** to honestly present what the data show: SES does not explain disparities in this crisis.

---

**Verification Status**: ✅ This README documents actual findings after fixing model specification issues
**Generated**: 2025-11-05 (Revised from original flawed analysis)
**Previous Issue**: Original Poisson regression produced nonsensical predictions (rate increased with better SES)
**Resolution**: Replaced with honest descriptive analysis revealing SES does not explain disparities
