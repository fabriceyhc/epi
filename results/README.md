# LA County Overdose Analysis Results

This directory contains **28 comprehensive analyses** of overdose deaths in Los Angeles County (2012-2023), examining temporal trends, demographic patterns, geographic distributions, and socioeconomic determinants.

## Quick Navigation

### 📊 Foundational Analyses (00-05)
- [**00_descriptive_statistics**](00_descriptive_statistics/) - Demographics, Table 1, raincloud plots
- [**01_fentanyl_timeline**](01_fentanyl_timeline/) - Rise of fentanyl, decline of heroin
- [**02_polysubstance_trends**](02_polysubstance_trends/) - Multiple substance involvement patterns
- [**03_demographic_shifts**](03_demographic_shifts/) - Age, gender, race/ethnicity changes
- [**04_homelessness_analysis**](04_homelessness_analysis/) - Unhoused population vulnerability
- [**05_geographic_analysis**](05_geographic_analysis/) - ZIP code hotspots and spatial patterns

### 📅 Temporal & Seasonal Patterns (06-07)
- [**06_seasonal_patterns**](06_seasonal_patterns/) - Monthly, weekly, seasonal variations
- [**07_covid_impact**](07_covid_impact/) - Basic COVID-19 pandemic impact

### 🗺️ Advanced Geospatial Analysis (08)
- [**08_geospatial_statistics**](08_geospatial_statistics/) - Center of gravity, clustering, KDE hotspots

### 👥 Race & Substance Interactions (09-10)
- [**09_race_substance_trends**](09_race_substance_trends/) - Race-substance-specific patterns
- [**10_age_race_figure**](10_age_race_figure/) - Comprehensive age-race visualization

### 📈 Population-Adjusted & SES Analyses (11-17)
- [**11_population_adjusted_rates**](11_population_adjusted_rates/) - Rates per 100,000 by race
- [**12_ses_context_figure**](12_ses_context_figure/) - Socioeconomic context visualization
- [**13_temporal_correlation**](13_temporal_correlation/) - SES-overdose temporal correlations
- [**14_ypll_analysis**](14_ypll_analysis/) - Years of Potential Life Lost (YPLL)
- [**15_disparity_decomposition**](15_disparity_decomposition/) - Racial disparity components
- [**16_comprehensive_publication**](16_comprehensive_publication/) - Master publication figure
- [**17_real_income_analysis**](17_real_income_analysis/) - Inflation-adjusted income trends

### 🏠 Advanced SES & Economic Analyses (18-27)
- [**18_age_standardized_rates**](18_age_standardized_rates/) - Age-adjusted disparity measures
- [**19_substance_specific_ses**](19_substance_specific_ses/) - SES patterns by drug type
- [**20_housing_homelessness**](20_housing_homelessness/) - Housing crisis pipeline ⭐
- [**21_geographic_ses_inequality**](21_geographic_ses_inequality/) - ZIP-level SES patterns ⭐
- [**22_counterfactual_ses_matching**](22_counterfactual_ses_matching/) - SES disparity decomposition ⚠️
- [**23_covid_economic_shock**](23_covid_economic_shock/) - Comprehensive COVID impact ⭐
- [**24_cumulative_disadvantage**](24_cumulative_disadvantage/) - Composite SES score
- [**25_housing_costs**](25_housing_costs/) - Housing costs correlation ⭐⭐⭐ **r=0.953**
- [**26_income_volatility**](26_income_volatility/) - Economic instability patterns
- [**27_poverty_age_interaction**](27_poverty_age_interaction/) - Poverty × age effects ⭐

## Top Findings Across All Analyses

### 🔴 Strongest Correlations
1. **Housing Costs** (#25): r = 0.953 with overdose rates - strongest finding
2. **Geographic Poverty** (#21): r = 0.519 at ZIP level - strong spatial pattern
3. **COVID-19 Shock** (#23): +114% spike in 2020, Black +156%

### 💊 Substance Evolution
- **Fentanyl** (#01): Replaced heroin as dominant opioid by 2018
- **Methamphetamine** (#04, #20): 64.2% involvement among unhoused vs 39% housed
- **Cocaine** (#19): Strongest poverty gradient (4.64x in high-poverty areas)

### 👥 Racial Disparities
- **Age-standardized Black-White disparity** (#18): 2.14x (increases after age adjustment)
- **Disparity decomposition** (#15): Persistent overrepresentation in Black population
- **COVID differential impact** (#23): Black +156%, White +71%, Latine +112%

### 🏠 Housing & Economic Factors
- **Rent burden** (#20, #25): Black 37.5% vs White 21.3% of income
- **Rent increase** (#25): +61.4% from 2012-2023
- **Income volatility** (#26): Latine 2.2x higher than White

### 🌍 Geographic Patterns
- **Downtown LA hotspots** (#21): ZIPs 90021, 90014, 90013 >3,000 per 100k
- **High-poverty ZIP disparity** (#21): 3.72x higher rates than low-poverty
- **Spatial clustering** (#08): DBSCAN clusters identify core crisis areas

### ⚡ Statistical Interactions
- **Poverty × Age** (#27): Significant interaction (p=0.0005)
- **Substance × SES** (#19): Effects vary dramatically by drug type

## Data Sources

### Overdose Data
- **Source**: LA County Medical Examiner-Coroner
- **Period**: 2012-2024 (analysis uses 2012-2023)
- **N**: 18,495 deaths in analysis period
- **Variables**: Demographics, substances, location, housing status

### Census Data
- **Source**: U.S. Census Bureau American Community Survey (ACS)
- **Annual estimates**: Population, poverty, income, age, housing costs
- **Geographic**: County-level and ZIP Code Tabulation Areas (ZCTAs)
- **Race/Ethnicity**: WHITE, BLACK, LATINE, ASIAN categories

## Folder Structure

Each analysis folder contains:
```
XX_analysis_name/
├── README.md           # Key findings and interpretation
├── *.png              # Visualizations (typically 6-9 panels)
└── *.csv              # Data tables and results
```

## Analysis Scripts

All scripts are in `scripts/` and follow standardized structure:
- Shared utilities in `scripts/utils.py`
- Consistent data processing and filtering
- Outputs to `results/XX_analysis_name/`

To run any analysis:
```bash
python scripts/XX_analysis_name.py
```

## Key Methodological Notes

### Race/Ethnicity Standardization
All analyses use standardized categories:
- **WHITE**: Non-Hispanic White
- **BLACK**: Non-Hispanic Black/African American
- **LATINE**: Hispanic/Latino (any race)
- **ASIAN**: Non-Hispanic Asian/Pacific Islander

### Time Period
- **Primary period**: 2012-2023 (complete years)
- **Excluded**: Partial 2024 data
- **COVID period**: 2020-2021 designated as pandemic period

### Rate Calculations
- **Crude rates**: Deaths per 100,000 population
- **Age-standardized rates** (#18): Using 2000 U.S. Standard Population
- **Population data**: Annual Census estimates

### Statistical Methods
- **Correlations**: Pearson or Spearman depending on distribution
- **Modeling**: Poisson regression for count data (#22, #27)
- **Spatial**: DBSCAN, KDE, center of gravity (#08)
- **Standardization**: Direct age standardization (#18)

## Important Caveats

### Data Limitations
1. **Ecological fallacy**: Census data are aggregated, not individual-level
2. **2023 data completeness**: Some analyses note incomplete 2023 homelessness data
3. **Missing data**: Not all deaths have complete location or housing status information

### Methodological Caveats
1. **Counterfactual analysis** (#22): Produced unexpected results, needs review ⚠️
2. **Age-specific population**: Not available by race; approximate distributions used
3. **ZIP-level analysis** (#21): Excludes very small population ZIPs (<500)
4. **Temporal correlation** (#13, #25): High correlation ≠ causation

### Geographic Notes
1. **LA County only**: Results not generalizable to other counties
2. **ZIP codes**: Some deaths lack precise ZIP code information
3. **Homeless deaths**: Location may be event location, not residence

## Publication & Citation

### Using These Analyses
If using these analyses or figures in publications:
1. **Cite data source**: LA County Medical Examiner-Coroner
2. **Cite Census data**: U.S. Census Bureau ACS
3. **Include time period**: 2012-2023
4. **Note analysis**: [Your institution/project]

### High-Impact Findings for Publication
Analyses marked with ⭐ contain particularly strong or novel findings:
- #25 (Housing costs): r=0.953 - exceptional correlation
- #21 (ZIP-level): Strong geographic SES gradient
- #23 (COVID): Comprehensive pandemic impact with racial disparities
- #27 (Poverty×Age): Significant statistical interaction
- #20 (Homelessness): Housing-overdose pipeline evidence

## Related Documentation

- `scripts/utils.py` - Shared data processing functions
- `scripts/run_all_analyses.py` - Master pipeline to run all analyses
- `REPO_STRUCTURE.md` - Repository organization guide
- `data/` - Raw data files (not in repo for privacy)

## Analysis Summaries

### Foundation & Descriptive (00-05)
Establish baseline patterns, temporal trends, and spatial distributions. Critical context for all subsequent analyses.

### Temporal & Seasonal (06-07)
Identify time-based patterns including pandemic impacts, seasonal variations, and day-of-week effects.

### Advanced Spatial (08)
Sophisticated geospatial statistics including clustering, hotspots, and directional trends.

### Race-Substance Interactions (09-10)
Detailed examination of how substance involvement varies across racial/ethnic groups.

### SES Context & Disparities (11-17)
Population-adjusted rates, socioeconomic context, disparity decomposition, and burden quantification (YPLL).

### Advanced SES & Economic (18-27)
Deep dive into socioeconomic determinants including housing, poverty, income, and their interactions with demographics.

## Contact & Support

For questions about:
- **Data access**: LA County Medical Examiner-Coroner
- **Methodology**: [Analysis team contact]
- **Code issues**: File issue in repository
- **Collaborations**: [PI contact]

---

**Analysis Period**: 2012-2023
**Total Deaths Analyzed**: 18,495
**Total Analyses**: 28
**Last Updated**: November 2025
