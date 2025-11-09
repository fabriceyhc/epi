"""
Fetch ZIP-Level Rent Data from Multiple Sources

Attempts to download ZIP/ZCTA-level median rent data for LA County
from various public sources:

1. Census ACS API (American Community Survey) - Table B25064
2. Zillow Observed Rent Index (ZORI)
3. HUD Fair Market Rents (FMR)
4. Census Data Portal

Goal: Create ZIP × Year panel for 2012-2023
"""

import pandas as pd
import numpy as np
import requests
import os
import time
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

print("=" * 80)
print("FETCHING ZIP-LEVEL RENT DATA")
print("=" * 80)
print()

output_dir = Path('data/zip_rent')
output_dir.mkdir(parents=True, exist_ok=True)

# LA County ZIP codes from our overdose data
df = pd.read_csv('data/2012-01-2024-08-overdoses.csv', low_memory=False)
df['DeathZip_Clean'] = df['DeathZip'].astype(str).str.split(',').str[0].str.strip().str.split('.').str[0]
df['DeathZip_Clean'] = pd.to_numeric(df['DeathZip_Clean'], errors='coerce')
la_zips = sorted(df[(df['DeathZip_Clean'] >= 90001) & (df['DeathZip_Clean'] <= 93599)]['DeathZip_Clean'].dropna().unique().astype(int))
print(f"Target: {len(la_zips)} LA County ZIP codes")
print()

# ============================================================================
# SOURCE 1: ZILLOW OBSERVED RENT INDEX (ZORI)
# ============================================================================

print("=" * 80)
print("SOURCE 1: Zillow Observed Rent Index (ZORI)")
print("=" * 80)
print()

print("Attempting to download Zillow ZORI data...")
print("URL: https://files.zillowstatic.com/research/public_csvs/zori/")
print()

zillow_success = False

try:
    # Zillow publishes ZORI data publicly
    # Multiple file formats available - try the ZIP code level file

    urls_to_try = [
        "https://files.zillowstatic.com/research/public_csvs/zori/Zip_ZORI_AllHomesPlusMultifamily_Smoothed.csv",
        "https://files.zillowstatic.com/research/public_csvs/zori/Zip_ZORI_AllHomes_Smoothed.csv",
    ]

    zillow_df = None

    for url in urls_to_try:
        print(f"Trying: {url}")
        try:
            zillow_df = pd.read_csv(url)
            print(f"✓ Downloaded successfully!")
            print(f"  Shape: {zillow_df.shape}")
            print(f"  Columns: {list(zillow_df.columns[:10])}...")
            break
        except Exception as e:
            print(f"  ✗ Failed: {e}")
            continue

    if zillow_df is not None:
        # Process Zillow data
        print()
        print("Processing Zillow data...")

        # Zillow format: RegionID, RegionName (ZIP), ... monthly columns
        # Filter to LA County ZIPs
        zillow_df = zillow_df[zillow_df['RegionName'].isin(la_zips)]
        print(f"  Filtered to {len(zillow_df)} LA County ZIPs")

        # Melt to long format
        id_cols = ['RegionID', 'RegionName', 'SizeRank', 'RegionType', 'StateName']
        id_cols_present = [c for c in id_cols if c in zillow_df.columns]

        date_cols = [col for col in zillow_df.columns if col not in id_cols_present]

        zillow_long = zillow_df.melt(id_vars=id_cols_present,
                                      value_vars=date_cols,
                                      var_name='Date', value_name='Rent')

        # Convert date to year
        zillow_long['Date'] = pd.to_datetime(zillow_long['Date'], errors='coerce')
        zillow_long['Year'] = zillow_long['Date'].dt.year

        # Filter to 2012-2023
        zillow_long = zillow_long[(zillow_long['Year'] >= 2012) & (zillow_long['Year'] <= 2023)]

        # Annual average
        zillow_annual = zillow_long.groupby(['RegionName', 'Year'])['Rent'].mean().reset_index()
        zillow_annual.rename(columns={'RegionName': 'ZIP', 'Rent': 'Median_Rent'}, inplace=True)
        zillow_annual['Source'] = 'Zillow_ZORI'

        print(f"  Final shape: {zillow_annual.shape}")
        print(f"  Years: {zillow_annual['Year'].min()} - {zillow_annual['Year'].max()}")
        print(f"  ZIPs with data: {zillow_annual['ZIP'].nunique()}")
        print(f"  Sample:")
        print(zillow_annual.head(10).to_string(index=False))

        # Save
        zillow_annual.to_csv(output_dir / 'zillow_rent_zip_year.csv', index=False)
        print(f"  ✓ Saved: {output_dir / 'zillow_rent_zip_year.csv'}")

        zillow_success = True

except Exception as e:
    print(f"✗ Zillow download failed: {e}")

print()

# ============================================================================
# SOURCE 2: CENSUS ACS API
# ============================================================================

print("=" * 80)
print("SOURCE 2: Census American Community Survey (ACS)")
print("=" * 80)
print()

print("Table: B25064 - Median Gross Rent")
print("Geography: ZCTAs (ZIP Code Tabulation Areas)")
print()

census_success = False

try:
    # Check for Census API key
    census_api_key = os.getenv('CENSUS_API_KEY')

    if not census_api_key:
        print("⚠ No CENSUS_API_KEY found in environment")
        print("  Get free key at: https://api.census.gov/data/key_signup.html")
        print()
        raise ValueError("No Census API key")

    print(f"✓ Found Census API key: {census_api_key[:8]}...")
    print()

    # ACS 5-Year Estimates available for:
    # 2012 (2008-2012), 2013 (2009-2013), ..., 2022 (2018-2022)
    # 2023 not yet available

    acs_years = range(2012, 2023)  # 2012-2022

    all_acs_data = []

    for year in acs_years:
        print(f"Fetching ACS {year} (5-year estimates)...")

        # API endpoint
        base_url = f"https://api.census.gov/data/{year}/acs/acs5"

        # Parameters
        params = {
            'get': 'NAME,B25064_001E',  # ZCTA name, Median Gross Rent
            'for': 'zip code tabulation area:*',  # All ZCTAs
            'key': census_api_key
        }

        try:
            response = requests.get(base_url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()

            # Convert to DataFrame
            df_year = pd.DataFrame(data[1:], columns=data[0])
            df_year['Year'] = year
            df_year.rename(columns={
                'B25064_001E': 'Median_Rent',
                'zip code tabulation area': 'ZCTA'
            }, inplace=True)

            # Convert to numeric
            df_year['ZCTA'] = pd.to_numeric(df_year['ZCTA'], errors='coerce')
            df_year['Median_Rent'] = pd.to_numeric(df_year['Median_Rent'], errors='coerce')

            # Filter to LA County ZCTAs (approximate match to ZIPs)
            df_year = df_year[df_year['ZCTA'].isin(la_zips)]

            all_acs_data.append(df_year)

            print(f"  ✓ {len(df_year)} LA County ZCTAs")

            time.sleep(0.5)  # Rate limiting

        except Exception as e:
            print(f"  ✗ Failed for {year}: {e}")
            continue

    if all_acs_data:
        acs_df = pd.concat(all_acs_data, ignore_index=True)
        acs_df = acs_df[['ZCTA', 'Year', 'Median_Rent']].copy()
        acs_df.rename(columns={'ZCTA': 'ZIP'}, inplace=True)
        acs_df['Source'] = 'Census_ACS5'

        print()
        print(f"CENSUS ACS SUMMARY:")
        print(f"  Total records: {len(acs_df)}")
        print(f"  Years: {acs_df['Year'].min()} - {acs_df['Year'].max()}")
        print(f"  ZCTAs with data: {acs_df['ZIP'].nunique()}")
        print(f"  Sample:")
        print(acs_df.head(10).to_string(index=False))

        # Save
        acs_df.to_csv(output_dir / 'census_acs_rent_zip_year.csv', index=False)
        print(f"  ✓ Saved: {output_dir / 'census_acs_rent_zip_year.csv'}")

        census_success = True

except Exception as e:
    print(f"✗ Census ACS download failed: {e}")

print()

# ============================================================================
# SOURCE 3: HUD Fair Market Rents (FMR)
# ============================================================================

print("=" * 80)
print("SOURCE 3: HUD Fair Market Rents (FMR)")
print("=" * 80)
print()

print("HUD publishes FMR by ZIP code annually")
print("URL: https://www.huduser.gov/portal/datasets/fmr.html")
print()

hud_success = False

try:
    print("Attempting to download HUD FMR data...")

    # HUD provides ZIP-level FMR data
    # Historical data available by year

    # Example URL format (varies by year)
    # This is challenging because HUD changes formats

    print("⚠ HUD FMR data requires manual download")
    print("  Reason: No stable API, format changes by year")
    print("  Manual process:")
    print("    1. Visit: https://www.huduser.gov/portal/datasets/fmr.html")
    print("    2. Download ZIP-level FMR for each year 2012-2023")
    print("    3. Place in data/hud_fmr/ directory")
    print()

    # Check if manual downloads exist
    hud_dir = Path('data/hud_fmr')
    if hud_dir.exists():
        hud_files = list(hud_dir.glob('*.csv'))
        if hud_files:
            print(f"✓ Found {len(hud_files)} HUD files in data/hud_fmr/")
            # Could process them here
        else:
            print("✗ No CSV files found in data/hud_fmr/")
    else:
        print("✗ Directory data/hud_fmr/ does not exist")

except Exception as e:
    print(f"✗ HUD FMR processing failed: {e}")

print()

# ============================================================================
# COMBINE SOURCES
# ============================================================================

print("=" * 80)
print("COMBINING DATA SOURCES")
print("=" * 80)
print()

combined_data = []

if zillow_success:
    zillow_annual = pd.read_csv(output_dir / 'zillow_rent_zip_year.csv')
    combined_data.append(zillow_annual)
    print(f"✓ Zillow: {len(zillow_annual)} records")

if census_success:
    acs_df = pd.read_csv(output_dir / 'census_acs_rent_zip_year.csv')
    combined_data.append(acs_df)
    print(f"✓ Census ACS: {len(acs_df)} records")

if combined_data:
    combined = pd.concat(combined_data, ignore_index=True)

    print()
    print(f"COMBINED DATASET:")
    print(f"  Total records: {len(combined)}")
    print(f"  Sources: {combined['Source'].unique()}")
    print(f"  ZIPs: {combined['ZIP'].nunique()}")
    print(f"  Years: {combined['Year'].min()} - {combined['Year'].max()}")
    print()

    # Create a "best estimate" by source priority
    # Priority: Zillow > Census ACS (Zillow more granular/recent)

    combined['Source_Priority'] = combined['Source'].map({
        'Zillow_ZORI': 1,
        'Census_ACS5': 2
    })

    combined_dedup = combined.sort_values('Source_Priority').groupby(['ZIP', 'Year']).first().reset_index()

    print(f"DEDUPLICATED (best source per ZIP-year):")
    print(f"  Records: {len(combined_dedup)}")
    print(f"  ZIP-Year coverage: {len(combined_dedup)} / {len(la_zips) * 12} possible ({len(combined_dedup) / (len(la_zips) * 12) * 100:.1f}%)")
    print()

    # Summary statistics
    print("Summary by Year:")
    year_summary = combined_dedup.groupby('Year').agg({
        'ZIP': 'count',
        'Median_Rent': ['mean', 'median', 'std']
    }).round(0)
    print(year_summary)
    print()

    # Save combined
    combined_dedup.to_csv(output_dir / 'zip_rent_combined.csv', index=False)
    print(f"✓ Saved: {output_dir / 'zip_rent_combined.csv'}")
    print()

    # Also save in main data directory for easy access
    combined_dedup.to_csv('data/zip_rent_panel.csv', index=False)
    print(f"✓ Saved: data/zip_rent_panel.csv")

else:
    print("✗ No data sources succeeded")

print()
print("=" * 80)
print("DOWNLOAD COMPLETE")
print("=" * 80)
print()

if zillow_success or census_success:
    print("✓ SUCCESS - ZIP-level rent data acquired!")
    print()
    print("Next steps:")
    print("  1. Run Analysis 51 again with ZIP-level data")
    print("  2. Test within-ZIP correlation (panel regression)")
    print("  3. Compare within-ZIP vs between-ZIP effects")
else:
    print("✗ FAILED - Could not acquire ZIP-level rent data")
    print()
    print("Manual alternatives:")
    print("  1. Get Census API key: https://api.census.gov/data/key_signup.html")
    print("  2. Download Zillow data manually")
    print("  3. Download HUD FMR data manually")
