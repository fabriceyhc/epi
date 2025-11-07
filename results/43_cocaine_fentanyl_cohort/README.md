# Cocaine + Fentanyl: "Collision of Epidemics" Cohort Analysis

**Analysis Number**: 43
**Script**: `43_cocaine_fentanyl_cohort.py`
**Status**: ✅ Complete
**Date**: 2025-11-06

## Overview

Tests the Penn State "collision of two epidemics" theory:
1. **Epidemic 1**: Legacy cohort of older, urban, Black individuals using cocaine since 1980s/90s
2. **Epidemic 2**: Recent fentanyl proliferation adulterating cocaine supply

**Prediction**: These cohorts should be OLDER and more common in BLACK populations.

## Key Findings

### Prediction 1: Age (CONFIRMED ✅)

**Median Ages:**
- Cocaine+Fentanyl: **40.0 years**
- Fentanyl-only: **36.0 years**
- Difference: **+4.0 years**

Mann-Whitney U test: p = 0.000000 ✅ Significant

**Interpretation**: Cocaine+fentanyl deaths are significantly OLDER, supporting the 'legacy cohort' hypothesis.

### Prediction 2: Racial Distribution (CONFIRMED ✅)

**% of deaths involving Cocaine+Fentanyl:**

- **BLACK**: 13.0% (414/3,177 deaths)
- **ASIAN**: 5.2% (28/538 deaths)
- **LATINE**: 5.0% (324/6,539 deaths)
- **WHITE**: 4.4% (336/7,688 deaths)


Highest proportion: **BLACK**  ✅

### Prediction 3: Temporal Surge (CONFIRMED ✅)

**Pre-2016 average**: 1.0 deaths/year
**Post-2016 average**: 143.2 deaths/year
**Increase**: **+14225%**

Maximum acceleration: 2016 (+900.0% year-over-year growth)

## Interpretation

### Validates "Collision of Epidemics" Theory

All three predictions confirmed:
1. ✅ Older age distribution (legacy users)
2. ✅ Higher prevalence in BLACK population
3. ✅ Rapid surge post-2015 (when fentanyl adulterates supply)

### Mechanism

**Not intentional co-use**: Literature suggests these individuals:
- Were using cocaine for years (legacy behavior)
- Did NOT seek out fentanyl
- Deaths result from **unintentional exposure** to adulterated supply
- May not have known they were using an opioid

Quote: "They may have been using cocaine for years, but now it is leading to overdoses because of the presence of fentanyl"

### Age Profile by Race

**Median age for Cocaine+Fentanyl deaths:**

- **WHITE**: 36.0 years (N=336)
- **BLACK**: 54.0 years (N=414)
- **LATINE**: 31.0 years (N=324)
- **ASIAN**: 31.5 years (N=28)


## Policy & Harm Reduction Implications

### Critical Gaps in Current Interventions

1. **Naloxone Access**
   - Legacy cocaine users may not identify as "opioid users"
   - Therefore unlikely to carry naloxone or know they're at risk
   - Literature: "if people who use cocaine do not know they are using opioids... then they may not feel the need to carry naloxone"

2. **MOUD Engagement**
   - Medications for Opioid Use Disorder (buprenorphine, methadone) designed for heroin/opioid users
   - Cocaine users do NOT seek MOUD
   - Yet this cohort is dying from fentanyl (an opioid)
   - **Gap**: Treatment model doesn't fit this population

3. **Testing & Awareness**
   - **Fentanyl test strips** are the most critical tool
   - Must be distributed wherever cocaine is used (not just SSPs)
   - Broader distribution to older Black adults specifically

### Recommended Interventions

1. **Saturate naloxone in cocaine-using communities**
   - Community centers, barbershops, churches
   - Target ages 40-60 (peak risk for this cohort)
   - Culturally responsive messaging

2. **Fentanyl test strip distribution**
   - Make available wherever stimulants are used
   - Train on use for cocaine/crack cocaine testing

3. **Harm reduction outreach**
   - Must overcome "racialized criminalization" and mistrust
   - Peer-led, community-based models
   - Explicitly address that cocaine supply is now contaminated

## Outputs Generated

### Visualizations
- `cocaine_fentanyl_cohort.png` - 6-panel figure:
  - Age distributions (Cocaine+Fentanyl vs Fentanyl-only)
  - Racial distribution (% of deaths)
  - Temporal surge (2012-2023)
  - Age by race (box plots)
  - Growth rate over time
  - Comparison table

### Data Tables
- `cocaine_fentanyl_by_race.csv` - Prevalence by race
- `cocaine_fentanyl_temporal_trend.csv` - Annual counts and growth rates
- `substance_profile_comparison.csv` - Cocaine+Fentanyl vs Fentanyl-only vs Cocaine-only

## Related Analyses

- **Analysis #09**: Race-Substance Trends (baseline patterns)
- **Analysis #37**: Age-Risk Curves (shows older Black mortality peaks)
- **Analysis #52**: Heroin-to-Fentanyl Transition (shows BLACK fentanyl came via cocaine, not heroin)
- **Analysis #53**: Polysubstance Complexity (adulteration index)

## Methodology

**Substance Groups (mutually exclusive)**:
- **Cocaine+Fentanyl**: Both detected, no heroin (the "collision" pattern)
- **Fentanyl-only**: Fentanyl detected, no cocaine, no heroin
- **Cocaine-only**: Cocaine detected, no fentanyl (legacy users pre-2015)

**Statistical Tests**:
- Mann-Whitney U test (age comparison, one-tailed)
- Year-over-year growth rates (percent change)

---

**Verification Status**: ✅ Confirms "collision of epidemics" theory in LA County
**Generated**: 2025-11-06
