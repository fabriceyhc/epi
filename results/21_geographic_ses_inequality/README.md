# Geographic SES Inequality (ZIP-level)

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
