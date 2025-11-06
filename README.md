# LA County Overdose Crisis: Epidemiological Analysis

Comprehensive analysis of overdose deaths in Los Angeles County (2012-2023), examining demographic patterns, socioeconomic factors, and economic determinants of the fentanyl crisis.

## Overview

This repository contains 36 analytical scripts examining the LA County overdose crisis from multiple perspectives:
- **18,495 overdose deaths** analyzed (2012-2023)
- **36 distinct analyses** covering descriptive epidemiology, spatial patterns, SES factors, and economic determinants
- **200+ visualizations** and data tables generated
- **Verified findings** with comprehensive documentation

## Key Findings

### Crisis Magnitude
- Deaths increased **461%** from 528 (2012) to 2,961 (2023)
- Fentanyl involvement rose from 1% to 60% of deaths
- Deaths **tripled** during COVID pandemic and remained elevated

### Racial Disparities
- **Black residents**: 85.4 per 100,000 (2023) - **2.9× higher than reference**
- **White residents**: 42.5 per 100,000
- **Latine residents**: 24.4 per 100,000
- **Asian residents**: 6.0 per 100,000

### Economic Determinants
- **Real wage stagnation**: Strong predictor (r=0.849, p<0.001) ⭐
- **Labor force participation**: Significant inverse relationship (r=-0.770, p=0.003) ⭐
- **Unemployment**: No correlation (r=-0.343) - short-term job loss NOT a driver
- **SES**: Does NOT explain racial disparities in expected way

### Critical Finding
**SES does not predict overdoses** as expected:
- Groups with similar poverty have vastly different outcomes (White 42.5 vs Asian 6.0 per 100k)
- Supply-side factors (fentanyl availability) dominate over economic factors
- 60% of Black excess mortality is beyond what SES explains

## Repository Structure

```
epi/
├── data/                          # Census and overdose data
├── scripts/                       # Analysis scripts (00-35)
│   ├── utils.py                  # Shared utility functions
│   ├── 00_descriptive_*.py       # Foundation analyses
│   ├── 11_population_*.py        # SES context analyses
│   ├── 18-27_census_*.py         # Advanced SES analyses
│   └── 28-35_fred_*.py           # Economic analyses (FRED data)
├── results/                       # Analysis outputs
│   ├── 00_descriptive_*/         # Each analysis has its own folder
│   ├── ...                       # with README, CSVs, and visualizations
│   ├── ANALYSIS_SUMMARIES.md     # Combined documentation (all 36 analyses)
│   └── ANALYSIS_TABLE.md         # Quick reference table
└── README.md                      # This file
```

## Analysis Categories

### Foundation (00-05)
Descriptive statistics, fentanyl timeline, polysubstance trends, demographics, homelessness, geographic distribution

### Temporal & Spatial (06-08)
Seasonal patterns, COVID impact, advanced geospatial statistics

### Race-Substance Interactions (09-10)
Interaction trends, comprehensive age-race figures

### SES Context (11-17)
Population-adjusted rates, temporal correlations, YPLL, disparity decomposition, real income analysis

### Advanced SES (18-27)
Age-standardized rates, housing burden, geographic inequality, counterfactual analysis, COVID economic shock, cumulative disadvantage, poverty-age interactions

### Economic Context (28-35) - FRED Data
Unemployment correlations, recession impact, real wages (deaths of despair), labor force participation, housing market stress, income inequality, economic precarity index, industry employment shifts

## Quick Start

### Prerequisites
```bash
# Python 3.8+
pip install pandas numpy scipy matplotlib seaborn scikit-learn
pip install fredapi  # For economic analyses (28-35)
```

### Set up FRED API (for analyses 28-35)
```bash
# Get free API key from https://fred.stlouisfed.org/docs/api/api_key.html
export FRED_API_KEY='your_key_here'
```

### Run Individual Analyses
```bash
# Run a specific analysis
python scripts/01_fentanyl_crisis_timeline.py

# Results saved to results/01_fentanyl_timeline/
```

### Run All Analyses
```bash
python scripts/run_all_analyses.py
```

## Key Scripts

- **`scripts/utils.py`**: Core data loading and processing functions
- **`scripts/run_all_analyses.py`**: Pipeline to run all 36 analyses
- **`scripts/combine_analysis_readmes.py`**: Generate combined documentation

## Documentation

Each analysis folder (`results/XX_analysis_name/`) contains:
- **README.md**: Detailed findings, methodology, interpretation
- **CSV files**: Numerical results and statistical tables
- **PNG files**: Publication-quality visualizations

**Master Documentation**:
- `results/ANALYSIS_SUMMARIES.md`: Complete documentation for all 36 analyses (100KB)
- `results/ANALYSIS_TABLE.md`: Quick reference summary table

## Notable Findings by Analysis

| Analysis | Key Finding |
|----------|-------------|
| #01 | Fentanyl rose from 1% to 60%, heroin declined from 24% to 4% |
| #04 | Homeless deaths increased from 14% to 29% of total |
| #11 | Black overdose rate 2.9× higher than reference (85.4 vs 29.4 per 100k) |
| #22 | **SES does NOT explain racial disparities** - supply-side factors dominate |
| #30 | **Real wage stagnation strongly predicts overdoses** (r=0.849) ⭐ |
| #31 | Labor force withdrawal correlates with overdoses (r=-0.770) ⭐ |
| #35 | Construction employment growth correlates with overdoses (r=0.835) ⭐ |

## Citation

If you use this analysis, please cite:

```
LA County Overdose Crisis: Epidemiological Analysis (2012-2023)
Data Source: LA County Medical Examiner-Coroner
Analysis Repository: https://github.com/[username]/epi
```

## Data Sources

### Overdose Data
- **Source**: LA County Medical Examiner-Coroner
- **Period**: 2012-2024 (analyses typically use 2012-2023)
- **Records**: 18,495 deaths (2012-2023)
- **Variables**: Demographics, substances, location, housing status

### Census Data
- **Source**: U.S. Census Bureau (American Community Survey)
- **Variables**: Population, poverty rates, income, housing costs by race
- **Years**: 2012-2023 (excluding 2020)

### Economic Data
- **Source**: Federal Reserve Economic Data (FRED)
- **Variables**: Unemployment, wages, labor force participation, housing indicators, industry employment
- **Temporal Resolution**: Monthly, aggregated to annual

## Key Methodological Notes

### Race/Ethnicity Categories
Standardized to: WHITE, BLACK, LATINE, ASIAN

### Substance Categories
Binary flags for: Fentanyl, Heroin, Cocaine, Methamphetamine, Prescription Opioids, Benzodiazepines, Alcohol

### Statistical Approaches
- Population-adjusted rates per 100,000
- Poisson regression for count data
- Linear regression for rate predictions
- Spatial statistics (DBSCAN, KDE, center of gravity)
- Time series correlation analysis
- Age-standardization using CDC methods

## License

Data usage subject to LA County Medical Examiner-Coroner data sharing agreements.

## Contact

For questions about this analysis, please open an issue on GitHub.

## Acknowledgments

Analysis conducted using data from the LA County Medical Examiner-Coroner, U.S. Census Bureau, and Federal Reserve Economic Data (FRED).

---

**Last Updated**: 2025-11-05
**Status**: All 36 analyses complete and documented
**Repository**: https://github.com/[username]/epi
