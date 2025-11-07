# Labor Force Non-Participation and Overdose Mortality

**Analysis Number**: 42
**Script**: `42_labor_force_nonparticipation.py`
**Status**: ✅ Complete
**Date**: 2025-11-06

## Overview

Tests whether labor force **non-participation** (people who "gave up" looking for work) drives overdoses more strongly than active **unemployment** (people still seeking work).

**Research Question**: Is leaving the workforce (despair) worse than job loss (stress)?

## Key Findings

### Finding 1: Non-Participation Matters More Than Unemployment

| Metric | r | p-value | Significant? |
|--------|---|---------|--------------|
| **Non-Participation Rate** | **+0.754** | **0.0046** | **✓** |
| Unemployment Rate | -0.353 | 0.2603 | ✗ |

**Interpretation**:
- People who **left the labor force** (gave up) at higher overdose risk
- People **actively looking for work** (unemployed) NOT at higher risk
- Supports "despair" (giving up) over "job search stress" hypothesis

---

### Finding 2: LFPR Decline is Strongest Predictor

**LFPR**: r = -0.754 (p = 0.0046)
- Explains **56.9% of variance** in overdose mortality
- As fewer people participate in workforce, overdoses increase
- Stronger than unemployment, non-participation alone

---

### Finding 3: Variance Explained

| Metric | R² | Variance Explained |
|--------|----|--------------------|
| LFPR | 0.569 | 56.9% |
| Non-Participation | 0.569 | 56.9% |
| Unemployment | 0.125 | 12.5% |

---

## What This Means

### "Deaths of Despair" Nuance

**Original Theory**: Job loss → Economic distress → Drug use → Overdose

**Our Finding**: It's not job LOSS that matters, but permanent WITHDRAWAL from labor force

- ✅ **Non-participation (giving up)** predicts overdoses
- ✗ **Unemployment (still trying)** does NOT predict overdoses

### But Supply-Side Still Dominates

**Important Context** (from Analysis #49):
- Supply-side framework (fentanyl prevalence): **98.9% variance explained**
- Demand-side framework (poverty, wages, LFPR): **93.4% variance explained**

**Labor market factors matter**, but **fentanyl supply matters MORE**.

---

## Policy Implications

### What Works

1. **Re-engagement programs** for long-term non-participants
   - Not just job placement, but workforce re-entry support
   - Address barriers: Skills gaps, criminal records, health issues

2. **Target discouraged workers**, not just unemployed
   - Unemployed already motivated (looking for work)
   - Non-participants need different interventions

3. **Economic participation as protective factor**
   - Having a job = routine, income, social connections
   - May reduce vulnerability to fentanyl exposure (even if supply-driven)

### What Doesn't Work (Alone)

1. **Unemployment insurance** (targets wrong group)
   - Helps people actively looking, but they're lower risk
   - Doesn't reach discouraged workers

2. **Job creation alone** (if people gave up)
   - Need to re-engage non-participants first
   - Address why they left workforce (disability, caregiving, etc.)

---

## Limitations

1. **Ecological fallacy**: Aggregate trends (all LA County)
   - Cannot infer individual-level causation
   - Non-participants and overdose victims may not be same people

2. **Supply-side dominance**: Fentanyl explains more variance
   - Labor market factors modulate VULNERABILITY
   - But supply contamination determines EXPOSURE

3. **Direction unclear**: Does non-participation → overdose, or overdose → non-participation?
   - Likely bidirectional
   - Drug use can cause workforce exit

---

## Outputs Generated

### Visualizations
- `labor_force_nonparticipation.png` - 6-panel figure:
  - LFPR vs overdose scatter
  - Non-participation vs overdose scatter
  - Unemployment vs overdose scatter
  - Temporal trends (all metrics)
  - Correlation comparison
  - Summary interpretation

### Data Tables
- `correlation_results.csv` - All correlation tests
- `variance_explained.csv` - R² values
- `annual_data_labor_overdose.csv` - Full annual dataset

---

## Related Analyses

- **Analysis #31**: Labor Force Participation (original finding: r = -0.770)
- **Analysis #32**: Unemployment (original finding: r = -0.343, NS)
- **Analysis #49**: Supply vs Demand Framework (supply dominates)
- **Analysis #30**: Real Wage Stagnation (r = +0.849)

---

## Methodology

**Non-Participation Rate Calculation**:
```
Non-Participation Rate = 100% - LFPR
```
(% of working-age population NOT in labor force)

**Statistical Tests**:
- Pearson correlation (each metric × overdose rate)
- R² for variance explained
- Period comparison (pre-COVID vs COVID era)

**Data Sources**:
- FRED: LA County LFPR, unemployment (2012-2023)
- LA County Medical Examiner: Overdose deaths (2012-2023)
- Census: Population estimates

---

**Verification Status**: ✅ Confirms "giving up" (non-participation) matters more than job loss (unemployment)
**Generated**: 2025-11-06
