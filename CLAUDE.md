# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Epidemiological analysis of the LA County overdose crisis (2012-2023), examining 18,495 overdose deaths across 36 analytical perspectives including demographic patterns, socioeconomic factors, and economic determinants.

## Development Commands

### Environment Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Set up Census API key (for Census data fetching)
echo "CENSUS_API_KEY=your_key_here" > .env

# Set up FRED API key (for economic analyses 28-35)
echo "FRED_API_KEY=your_key_here" >> .env
# Get free API key from: https://fred.stlouisfed.org/docs/api/api_key.html
```

### Running Analyses

```bash
# Run a single analysis script
python scripts/01_fentanyl_crisis_timeline.py
# Output: results/01_fentanyl_timeline/ (README.md, CSVs, PNGs)

# Run all analyses in sequence
python scripts/run_all_analyses.py

# Run with options
python scripts/run_all_analyses.py --skip-census        # Use existing Census data
python scripts/run_all_analyses.py --basic-only         # Run only analyses 01-08
python scripts/run_all_analyses.py --advanced-only      # Run only analyses 09-17
python scripts/run_all_analyses.py --continue-on-error  # Don't stop on failures
```

### Utility Scripts
```bash
# Fetch Census data (population, poverty, income, age by race)
python scripts/fetch_census_data.py

# Combine all analysis READMEs into master documentation
python scripts/combine_analysis_readmes.py

# Verify all analyses and generate documentation table
python scripts/verify_and_document_analyses.py

# Reorganize results into numbered folders
python scripts/organize_analysis_results.py
```

## Code Architecture

### Data Flow
1. **Raw data** (data/2012-01-2024-08-overdoses.csv): 18,495 overdose death records
2. **Census data** (data/*.csv): Population, poverty, income fetched via Census API
3. **Processing** (scripts/utils.py): Standardized data cleaning pipeline
4. **Analysis scripts** (scripts/NN_*.py): 36 independent analysis scripts
5. **Results** (results/NN_*/): Each analysis generates its own output folder

### Core Utility Module (scripts/utils.py)

**Critical for maintaining consistency across all analyses.** Provides:

- `full_data_processing()`: Complete standardized processing pipeline
- `standardize_race()`: Converts raw race codes to: WHITE, BLACK, LATINE, ASIAN, OTHER, UNKNOWN
- `process_age()`: Creates age groups and binary age categories
- `calculate_polysubstance()`: Computes polysubstance involvement
- `SUBSTANCE_COLS`: Standard substance list (Heroin, Fentanyl, Prescription.opioids, Methamphetamine, Cocaine, Benzodiazepines, Alcohol, Others)
- `RACE_CATEGORIES`: Standard race list
- `RACE_COLORS`: Consistent color palette for visualizations
- `YEAR_START`, `YEAR_END`: Standard study period (2012-2023)

**When modifying any analysis script, always use utils.py functions to ensure consistency.**

### Analysis Script Structure

All analysis scripts follow this pattern:
```python
#!/usr/bin/env python
# coding: utf-8

"""Script description and methodology"""

import pandas as pd
import sys
sys.path.append('scripts')
from utils import full_data_processing, SUBSTANCE_COLS, RACE_COLORS

# 1. Load and process data
df = full_data_processing()

# 2. Perform analysis (create tables, run models)
# ...

# 3. Generate visualizations
# ...

# 4. Save results to results/NN_analysis_name/
os.makedirs('results/NN_analysis_name', exist_ok=True)
table.to_csv('results/NN_analysis_name/table.csv')
fig.savefig('results/NN_analysis_name/figure.png', dpi=300, bbox_inches='tight')

print("Analysis complete!")
```

### Analysis Categories

**Foundation (00-08)**: Basic descriptive epidemiology, geographic and temporal patterns
- Scripts run independently with minimal dependencies
- Establish baseline statistics and trends

**SES Context (09-27)**: Socioeconomic analyses requiring Census data
- **Dependency**: Must run `fetch_census_data.py` first
- Census data cached in `data/la_county_*.csv` files
- Analyses examine poverty, income, housing burden, geographic inequality

**Economic Context (28-35)**: Macroeconomic analyses requiring FRED data
- **Dependency**: Requires FRED_API_KEY in .env
- Uses fredapi package to fetch unemployment, wages, labor market indicators
- Examines structural economic determinants of overdose crisis

### Output Structure

Each analysis generates a folder in `results/`:
```
results/NN_analysis_name/
├── README.md                 # Detailed findings and interpretation
├── table.csv                 # Primary statistical results
├── supplemental_*.csv        # Additional data tables
└── figure*.png               # Publication-quality visualizations (300 DPI)
```

Master documentation:
- `results/ANALYSIS_SUMMARIES.md`: Combined documentation (~100KB)
- `results/ANALYSIS_TABLE.md`: Quick reference table of all analyses

## Key Technical Details

### Race/Ethnicity Standardization
Raw data contains inconsistent race codes. `standardize_race()` in utils.py handles:
- CAUCASIAN, WHITE → WHITE
- HISPANIC/LATIN AMERICAN, Hispanic → LATINE
- BLACK → BLACK
- ASIAN, CHINESE, FILIPINO, etc. → ASIAN
- Mixed race individuals assigned to non-White category
- Output: Categorical variable with ordering: WHITE, LATINE, BLACK, ASIAN, OTHER, UNKNOWN

### Age Processing
- Age < 1 set to 0
- Age groups: 0, 1-9, 10-19, 20-29, 30-39, 40-49, 50-59, 60-69, ≥70 years
- Age binary: <40 vs ≥40 years

### Substance Columns
Binary flags (0/1) for each substance:
- Heroin, Fentanyl, Prescription.opioids (note the dot)
- Methamphetamine, Cocaine, Benzodiazepines, Alcohol, Others
- `Number_Substances`: Sum of all substance flags
- `Polysubstance`: Binary flag (>1 substance)

### Study Period
- Standard: 2012-2023 (12 years)
- Census data unavailable for 2020 (pandemic; ACS 1-year not released)
- Some scripts analyze through 2024-08 for recent trends

### Statistical Approaches
- **Population-adjusted rates**: Per 100,000 using Census denominators
- **Poisson regression**: For count outcomes with offset for population
- **Linear regression**: For rate trends over time
- **Spatial statistics**: DBSCAN clustering, KDE, center of gravity
- **Age-standardization**: CDC 2000 standard population

## Common Development Patterns

### Adding a New Analysis

1. Create script: `scripts/NN_analysis_name.py`
2. Use `full_data_processing()` for data loading
3. Follow standard output structure (README + CSV + PNG)
4. Add to `run_all_analyses.py` pipeline
5. Run `verify_and_document_analyses.py` to update master docs

### Modifying an Existing Analysis

1. Read the script and its corresponding `results/NN_*/README.md`
2. Preserve output file names and formats (other scripts may depend on them)
3. Use utils.py functions for any data processing
4. Regenerate outputs by running the script from repo root: `python scripts/NN_analysis.py`

### Working with Census Data

Census data is fetched once and cached. If you need to refetch:
```bash
# Remove cached files
rm data/la_county_*.csv

# Refetch from Census API
python scripts/fetch_census_data.py
```

Census data structure:
- `la_county_population_census.csv`: Total + by race (WHITE, BLACK, ASIAN, LATINE)
- `la_county_poverty_by_race.csv`: Poverty rates by year and race
- `la_county_income_by_race.csv`: Median household income by race
- `la_county_age_by_race.csv`: Median age by race

### Working with FRED Data

Economic analyses (28-35) fetch FRED data on-the-fly. Each script handles its own FRED API calls and caching. If an analysis fails due to FRED API issues:
1. Check FRED_API_KEY is set in .env
2. Check FRED API rate limits (120 requests/minute)
3. Verify series IDs are still valid (FRED occasionally deprecates series)

## Project Context

### Key Findings
- Fentanyl involvement: 1% (2012) → 60% (2023)
- Deaths increased 461%: 528 (2012) → 2,961 (2023)
- Tripled during COVID pandemic and remained elevated
- Black residents: 85.4 per 100k (2.9× higher than reference 29.4)
- **Critical finding**: SES does NOT explain racial disparities as expected
- Real wage stagnation strongly predicts overdoses (r=0.849, p<0.001)

### Data Sources
- **Overdose data**: LA County Medical Examiner-Coroner (2012-2024)
- **Census data**: U.S. Census Bureau ACS 1-year estimates (except 2020)
- **Economic data**: Federal Reserve Economic Data (FRED)

### Analysis Philosophy
Scripts are designed to be:
- **Independent**: Each can run standalone after data fetching
- **Reproducible**: Fixed random seeds, deterministic processing
- **Documented**: Every analysis generates comprehensive README
- **Consistent**: All use utils.py standardization
