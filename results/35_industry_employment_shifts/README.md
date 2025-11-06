# Industry Employment Shifts and Overdoses

**Analysis Number**: 35
**Script**: `35_industry_employment_shifts.py`
**Status**: ✅ Verified with actual results
**Last Updated**: 2025-11-05

## Overview

Examines whether job losses in specific industries (manufacturing, construction) correlate with overdose deaths, testing the "Rust Belt" deaths of despair pattern in LA County.

## Key Findings

### **CONSTRUCTION EMPLOYMENT**: r = 0.835, p = 0.0007 ⭐

**Strong positive correlation** - as construction employment increased 2012-2023, so did overdose deaths. This is somewhat paradoxical and suggests:
1. Construction workers may face high occupational overdose risk
2. Construction booms don't provide protective economic effects
3. Industry growth doesn't necessarily reduce overdose mortality

### Manufacturing Employment: r = 0.551, p = 0.064 (marginal)

Moderate positive correlation, approaching significance. Unlike Rust Belt patterns of manufacturing decline driving despair, LA shows different dynamics.

### LA County vs Rust Belt

**Key Difference**: In Rust Belt states, manufacturing *decline* predicted overdoses. In LA County:
- Manufacturing employment was relatively stable
- Construction employment *growth* correlated with increased deaths
- Suggests LA's crisis has different structural drivers than traditional industrial decline

## Outputs Generated

- `industry_employment_trends.csv` - Annual employment by industry with deaths
- `industry_correlations.csv` - Correlation statistics for each industry
- `industry_employment_indexed.png` - Indexed trends (2012=100)

## Industry Correlations Summary

| Industry | Correlation | P-Value | Significant? |
|----------|------------|---------|--------------|
| Construction | 0.835 | 0.0007 | ✓ YES ⭐ |
| Manufacturing | 0.551 | 0.064 | Marginal |
| Leisure/Hospitality | N/A | N/A | Data unavailable |

## Data Sources

- **FRED Series**: MANEMP (Manufacturing), USCONS (Construction)
- **Overdose Data**: LA County, 2012-2023, N=18,495

## Interpretation

### Not a Traditional Rust Belt Pattern

LA County's overdose crisis does NOT follow the classic "industrial decline → deaths of despair" pattern seen in Appalachia and the Rust Belt. Instead:

1. **Supply-Side Dominant**: Fentanyl availability may be primary driver
2. **Construction Paradox**: Growing construction sector correlates with rising overdoses
3. **Occupational Risk**: Certain industries (construction) may have inherent overdose risk factors beyond employment levels

### Construction Worker Vulnerability

The strong construction correlation warrants targeted interventions:
- Occupational health screening
- Workplace substance use prevention
- Pain management alternatives for injury-prone occupation

## Related Analyses

- Analysis #30: Real Wages (r=0.849) - stronger than industry effects
- Analysis #31: Labor Force Participation (r=-0.770)
- Analysis #35: THIS ANALYSIS - Industry shifts

---

**Verification Status**: ✅ This README was generated after running the analysis
**Generated**: 2025-11-05
