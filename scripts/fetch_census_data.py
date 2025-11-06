#!/usr/bin/env python
# coding: utf-8

"""
Fetch ALL LA County Census Data from Census API
- Population by race (Table B03002)
- Poverty rates by race (Table B17001)
- Median household income by race (Table B19013)
- Median age by race (Table B01002)

Years: 2012-2023
Geography: Los Angeles County, California
Source: U.S. Census Bureau ACS 1-Year Estimates + 2020 Decennial Census
"""

import os
import requests
import pandas as pd
from dotenv import load_dotenv

# Load API key
load_dotenv()
API_KEY = os.getenv('CENSUS_API_KEY')

if not API_KEY:
    raise ValueError("CENSUS_API_KEY not found in .env file")

print("="*70)
print("FETCHING ALL LA COUNTY CENSUS DATA FROM CENSUS API")
print("="*70)
print(f"API Key loaded: {API_KEY[:10]}...")
print()

STATE_FIPS = "06"
COUNTY_FIPS = "037"

# ============================================================================
# FUNCTION: Fetch Population Data
# ============================================================================

def fetch_population_data(year):
    """
    Fetch population by race
    Table B03002: Hispanic or Latino Origin by Race
    """
    print(f"  Population data...", end=" ")

    base_url = "https://api.census.gov/data"

    # For 2020, use Decennial Census instead of ACS
    if year == 2020:
        endpoint = f"{base_url}/2020/dec/dhc"
        variables = {
            'P5_001N': 'Total',
            'P5_003N': 'WHITE',   # Not Hispanic, White alone
            'P5_004N': 'BLACK',   # Not Hispanic, Black alone
            'P5_006N': 'ASIAN',   # Not Hispanic, Asian alone
            'P5_002N': 'LATINE'   # Hispanic or Latino
        }
    else:
        endpoint = f"{base_url}/{year}/acs/acs1"
        variables = {
            'B03002_001E': 'Total',
            'B03002_003E': 'WHITE',      # Not Hispanic, White alone
            'B03002_004E': 'BLACK',      # Not Hispanic, Black alone
            'B03002_006E': 'ASIAN',      # Not Hispanic, Asian alone
            'B03002_012E': 'LATINE'      # Hispanic or Latino
        }

    var_list = ','.join(variables.keys())

    params = {
        'get': var_list,
        'for': f'county:{COUNTY_FIPS}',
        'in': f'state:{STATE_FIPS}',
        'key': API_KEY
    }

    try:
        response = requests.get(endpoint, params=params)
        response.raise_for_status()

        data = response.json()
        values = data[1]

        result = {
            'Year': year,
            'TOTAL': int(values[0]),
            'WHITE': int(values[1]),
            'BLACK': int(values[2]),
            'ASIAN': int(values[3]),
            'LATINE': int(values[4])
        }

        print(f"✓ (Total: {result['TOTAL']:,})")
        return result

    except Exception as e:
        print(f"✗ Error: {e}")
        return None

# ============================================================================
# FUNCTION: Fetch Poverty Data
# ============================================================================

def fetch_poverty_data(year):
    """
    Fetch poverty rates by race
    Table B17001: Poverty Status in the Past 12 Months
    """
    print(f"  Poverty rates...", end=" ")

    base_url = "https://api.census.gov/data"
    endpoint = f"{base_url}/{year}/acs/acs1"

    # B17001X_001E = Total population for whom poverty status is determined
    # B17001X_002E = Population below poverty level
    # H = White alone, not Hispanic
    # B = Black alone
    # I = Hispanic or Latino
    # D = Asian alone

    variables = {
        'B17001H_001E': 'WHITE_Total',
        'B17001H_002E': 'WHITE_Below_Poverty',
        'B17001B_001E': 'BLACK_Total',
        'B17001B_002E': 'BLACK_Below_Poverty',
        'B17001I_001E': 'LATINE_Total',
        'B17001I_002E': 'LATINE_Below_Poverty',
        'B17001D_001E': 'ASIAN_Total',
        'B17001D_002E': 'ASIAN_Below_Poverty'
    }

    var_list = ','.join(variables.keys())

    params = {
        'get': var_list,
        'for': f'county:{COUNTY_FIPS}',
        'in': f'state:{STATE_FIPS}',
        'key': API_KEY
    }

    try:
        response = requests.get(endpoint, params=params)
        response.raise_for_status()

        data = response.json()
        values = data[1]

        result = {
            'Year': year,
            'WHITE_Poverty_Rate': (int(values[1]) / int(values[0]) * 100) if int(values[0]) > 0 else None,
            'BLACK_Poverty_Rate': (int(values[3]) / int(values[2]) * 100) if int(values[2]) > 0 else None,
            'LATINE_Poverty_Rate': (int(values[5]) / int(values[4]) * 100) if int(values[4]) > 0 else None,
            'ASIAN_Poverty_Rate': (int(values[7]) / int(values[6]) * 100) if int(values[6]) > 0 else None,
        }

        print(f"✓ (BLACK: {result['BLACK_Poverty_Rate']:.1f}%)")
        return result

    except Exception as e:
        print(f"✗ Error: {e}")
        return None

# ============================================================================
# FUNCTION: Fetch Income Data
# ============================================================================

def fetch_income_data(year):
    """
    Fetch median household income by race
    Table B19013: Median Household Income in the Past 12 Months
    """
    print(f"  Median income...", end=" ")

    base_url = "https://api.census.gov/data"
    endpoint = f"{base_url}/{year}/acs/acs1"

    variables = {
        'B19013H_001E': 'WHITE_Median_Income',
        'B19013B_001E': 'BLACK_Median_Income',
        'B19013I_001E': 'LATINE_Median_Income',
        'B19013D_001E': 'ASIAN_Median_Income'
    }

    var_list = ','.join(variables.keys())

    params = {
        'get': var_list,
        'for': f'county:{COUNTY_FIPS}',
        'in': f'state:{STATE_FIPS}',
        'key': API_KEY
    }

    try:
        response = requests.get(endpoint, params=params)
        response.raise_for_status()

        data = response.json()
        values = data[1]

        result = {
            'Year': year,
            'WHITE_Median_Income': int(values[0]) if values[0] not in ['-', None] else None,
            'BLACK_Median_Income': int(values[1]) if values[1] not in ['-', None] else None,
            'LATINE_Median_Income': int(values[2]) if values[2] not in ['-', None] else None,
            'ASIAN_Median_Income': int(values[3]) if values[3] not in ['-', None] else None,
        }

        print(f"✓ (BLACK: ${result['BLACK_Median_Income']:,})")
        return result

    except Exception as e:
        print(f"✗ Error: {e}")
        return None

# ============================================================================
# FUNCTION: Fetch Age Distribution
# ============================================================================

def fetch_age_distribution(year):
    """
    Fetch median age by race
    Table B01002: Median Age by Sex
    """
    print(f"  Median age...", end=" ")

    base_url = "https://api.census.gov/data"
    endpoint = f"{base_url}/{year}/acs/acs1"

    variables = {
        'B01002H_001E': 'WHITE_Median_Age',
        'B01002B_001E': 'BLACK_Median_Age',
        'B01002I_001E': 'LATINE_Median_Age',
        'B01002D_001E': 'ASIAN_Median_Age'
    }

    var_list = ','.join(variables.keys())

    params = {
        'get': var_list,
        'for': f'county:{COUNTY_FIPS}',
        'in': f'state:{STATE_FIPS}',
        'key': API_KEY
    }

    try:
        response = requests.get(endpoint, params=params)
        response.raise_for_status()

        data = response.json()
        values = data[1]

        result = {
            'Year': year,
            'WHITE_Median_Age': float(values[0]) if values[0] not in ['-', None] else None,
            'BLACK_Median_Age': float(values[1]) if values[1] not in ['-', None] else None,
            'LATINE_Median_Age': float(values[2]) if values[2] not in ['-', None] else None,
            'ASIAN_Median_Age': float(values[3]) if values[3] not in ['-', None] else None,
        }

        print(f"✓ (BLACK: {result['BLACK_Median_Age']:.1f} yrs)")
        return result

    except Exception as e:
        print(f"✗ Error: {e}")
        return None

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    years = range(2012, 2024)

    # Initialize data collectors
    population_data = []
    poverty_data = []
    income_data = []
    age_data = []

    for year in years:
        print(f"\n{'='*70}")
        print(f"YEAR {year}")
        print(f"{'='*70}")

        if year == 2020:
            print("Note: 2020 uses Decennial Census for population; no ACS 1-Year data for SES")
            print()

        # Population (works for 2020 via Decennial Census)
        pop = fetch_population_data(year)
        if pop:
            population_data.append(pop)

        # SES data (skip 2020 - no ACS 1-Year)
        if year != 2020:
            pov = fetch_poverty_data(year)
            if pov:
                poverty_data.append(pov)

            inc = fetch_income_data(year)
            if inc:
                income_data.append(inc)

            age = fetch_age_distribution(year)
            if age:
                age_data.append(age)

    # ========================================================================
    # SAVE ALL DATASETS
    # ========================================================================

    print("\n" + "="*70)
    print("SAVING DATA TO FILES")
    print("="*70)

    # 1. Population
    if population_data:
        df_pop = pd.DataFrame(population_data)
        df_pop.to_csv('data/la_county_population_census.csv', index=False)
        print(f"✓ Saved population data: {len(df_pop)} years")

        # Also save as Python dictionary
        with open('data/la_county_population_dict.py', 'w') as f:
            f.write("# Official LA County Population Data from Census Bureau\n")
            f.write("# Source: U.S. Census Bureau, ACS 1-Year + 2020 Decennial Census\n")
            f.write("# Table B03002: Hispanic or Latino Origin by Race\n\n")
            f.write("LA_COUNTY_POPULATION = {\n")
            for _, row in df_pop.iterrows():
                year = int(row['Year'])
                f.write(f"    {year}: {{\n")
                f.write(f"        'WHITE': {int(row['WHITE'])},\n")
                f.write(f"        'LATINE': {int(row['LATINE'])},\n")
                f.write(f"        'BLACK': {int(row['BLACK'])},\n")
                f.write(f"        'ASIAN': {int(row['ASIAN'])},\n")
                f.write(f"        'TOTAL': {int(row['TOTAL'])}\n")
                f.write(f"    }},\n")
            f.write("}\n")
        print(f"✓ Saved Python dictionary: data/la_county_population_dict.py")

    # 2. Poverty
    if poverty_data:
        df_pov = pd.DataFrame(poverty_data)
        df_pov.to_csv('data/la_county_poverty_by_race.csv', index=False)
        print(f"✓ Saved poverty data: {len(df_pov)} years")

    # 3. Income
    if income_data:
        df_inc = pd.DataFrame(income_data)
        df_inc.to_csv('data/la_county_income_by_race.csv', index=False)
        print(f"✓ Saved income data: {len(df_inc)} years")

    # 4. Age
    if age_data:
        df_age = pd.DataFrame(age_data)
        df_age.to_csv('data/la_county_age_by_race.csv', index=False)
        print(f"✓ Saved age data: {len(df_age)} years")

    # ========================================================================
    # DISPLAY SUMMARY
    # ========================================================================

    print("\n" + "="*70)
    print("2023 SUMMARY STATISTICS")
    print("="*70)

    if population_data:
        latest = population_data[-1]
        print("\nPOPULATION (2023):")
        print(f"  Total LA County: {latest['TOTAL']:>10,}")
        print(f"  WHITE:           {latest['WHITE']:>10,} ({latest['WHITE']/latest['TOTAL']*100:>5.1f}%)")
        print(f"  LATINE:          {latest['LATINE']:>10,} ({latest['LATINE']/latest['TOTAL']*100:>5.1f}%)")
        print(f"  BLACK:           {latest['BLACK']:>10,} ({latest['BLACK']/latest['TOTAL']*100:>5.1f}%)")
        print(f"  ASIAN:           {latest['ASIAN']:>10,} ({latest['ASIAN']/latest['TOTAL']*100:>5.1f}%)")

    if poverty_data:
        latest = poverty_data[-1]
        print("\nPOVERTY RATES (2023):")
        for key, val in latest.items():
            if key != 'Year' and val is not None:
                print(f"  {key}: {val:.1f}%")

    if income_data:
        latest = income_data[-1]
        print("\nMEDIAN HOUSEHOLD INCOME (2023):")
        for key, val in latest.items():
            if key != 'Year' and val is not None:
                print(f"  {key}: ${val:,}")

    if age_data:
        latest = age_data[-1]
        print("\nMEDIAN AGE BY RACE (2023):")
        for key, val in latest.items():
            if key != 'Year' and val is not None:
                print(f"  {key}: {val:.1f} years")

    # ========================================================================
    # POPULATION CHANGES
    # ========================================================================

    if population_data and len(population_data) > 1:
        print("\n" + "="*70)
        print("POPULATION CHANGES (2012-2023)")
        print("="*70)

        first_year = population_data[0]
        last_year = population_data[-1]

        for race in ['WHITE', 'LATINE', 'BLACK', 'ASIAN']:
            start_pop = int(first_year[race])
            end_pop = int(last_year[race])
            change = end_pop - start_pop
            pct_change = (change / start_pop * 100) if start_pop > 0 else 0

            start_pct = (start_pop / first_year['TOTAL'] * 100)
            end_pct = (end_pop / last_year['TOTAL'] * 100)

            print(f"\n{race}:")
            print(f"  2012: {start_pop:>10,} ({start_pct:>5.2f}% of LA County)")
            print(f"  2023: {end_pop:>10,} ({end_pct:>5.2f}% of LA County)")

            arrow = "⬆" if pct_change > 0 else "⬇" if pct_change < 0 else "↔"
            print(f"  Change: {change:>10,} ({pct_change:+6.2f}%) {arrow}")

    print("\n" + "="*70)
    print("NEXT STEPS")
    print("="*70)
    print("\n1. Run population-adjusted rate analysis:")
    print("   python scripts/11_population_adjusted_rates.py")
    print("\n2. Create SES context figure:")
    print("   python scripts/12_ses_context_figure.py")
    print("\n" + "="*70)
    print("DONE!")
    print("="*70)

if __name__ == "__main__":
    main()
