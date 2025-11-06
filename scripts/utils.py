#!/usr/bin/env python
# coding: utf-8

"""
Shared utility functions for data processing across all scripts
Standardizes race/ethnicity recoding, age grouping, substance columns, etc.
"""

import pandas as pd
import numpy as np

# Standard substance columns used across all analyses
SUBSTANCE_COLS = [
    'Heroin', 'Fentanyl', 'Prescription.opioids',
    'Methamphetamine', 'Cocaine', 'Benzodiazepines',
    'Alcohol', 'Others'
]

# Race/ethnicity categories
RACE_CATEGORIES = ['WHITE', 'LATINE', 'BLACK', 'ASIAN', 'OTHER', 'UNKNOWN']

# Standard year range for analyses
YEAR_START = 2012
YEAR_END = 2023

def load_overdose_data(file_path='data/2012-01-2024-08-overdoses.csv'):
    """
    Load and perform basic processing on overdose data

    Parameters:
    -----------
    file_path : str
        Path to the CSV file

    Returns:
    --------
    pd.DataFrame
        Loaded dataframe with basic date processing
    """
    df = pd.read_csv(file_path, low_memory=False)

    # Process dates
    df['Date of Death'] = pd.to_datetime(df['DeathDate'], errors='coerce')
    if 'DateofDeath' in df.columns:
        df['Date of Death'] = df['Date of Death'].fillna(
            pd.to_datetime(df['DateofDeath'], errors='coerce')
        )

    df['Year'] = df['Date of Death'].dt.year

    return df


def standardize_race(df, race_col='Race', output_col='Race_Ethnicity_Cleaned'):
    """
    Standardize race/ethnicity categories

    Parameters:
    -----------
    df : pd.DataFrame
        Input dataframe
    race_col : str
        Name of the race column to process
    output_col : str
        Name of the output column

    Returns:
    --------
    pd.DataFrame
        Dataframe with standardized race column
    """
    conditions = [
        df[race_col].isin(["CAUCASIAN", "WHITE", "White/Caucasian"]),
        df[race_col].isin(["LATINE", "HISPANIC/LATIN AMERICAN", "Hispanic/Latino"]) |
            df[race_col].str.contains("Hispanic", na=False),
        df[race_col].isin(["BLACK", "Black"]),
        df[race_col].isin(["ASIAN", "Asian", "CHINESE", "FILIPINO", "JAPANESE",
                           "KOREAN", "VIETNAMESE", "THAI", "CAMBODIAN"]),
        df[race_col].str.contains(r"White.*Hispanic|Hispanic.*White", na=False, case=True),
        df[race_col].str.contains(r"White.*Asian|Asian.*White", na=False, case=True),
        df[race_col].str.contains(r"Black.*Hispanic|Hispanic.*Black", na=False, case=True),
        df[race_col].str.contains(r"Black.*Asian|Asian.*Black", na=False, case=True),
        df[race_col].isin(["UNKNOWN", "Unknown/Other"]) | df[race_col].isna()
    ]

    choices = [
        "WHITE", "LATINE", "BLACK", "ASIAN",
        "LATINE", "ASIAN", "LATINE", "ASIAN", "UNKNOWN"
    ]

    df[output_col] = np.select(conditions, choices, default="OTHER")

    # Set as categorical
    df[output_col] = pd.Categorical(
        df[output_col],
        categories=RACE_CATEGORIES,
        ordered=True
    )

    return df


def process_age(df, age_col='Age'):
    """
    Process age column - convert to numeric and create age groups

    Parameters:
    -----------
    df : pd.DataFrame
        Input dataframe
    age_col : str
        Name of the age column

    Returns:
    --------
    pd.DataFrame
        Dataframe with processed age, age groups, and age binary
    """
    # Convert Age to numeric
    if df[age_col].dtype == 'object':
        df[age_col] = df[age_col].str.extract(r"(\d+\.?\d*)")[0].astype(float)
    else:
        df[age_col] = pd.to_numeric(df[age_col], errors='coerce')

    # Set age < 1 to 0
    df.loc[df[age_col] < 1, age_col] = 0

    # Create age groups
    bins = [-float('inf'), 0, 9, 19, 29, 39, 49, 59, 69, float('inf')]
    labels = ["0", "1-9 years", "10-19 years", "20-29 years", "30-39 years",
              "40-49 years", "50-59 years", "60-69 years", "≥70 years"]
    df['Age_Group'] = pd.cut(df[age_col], bins=bins, labels=labels, right=True)

    # Create binary age cut
    df['Age_Binary'] = np.where(df[age_col] < 40, "<40 years", "≥40 years")

    return df


def calculate_polysubstance(df, substance_cols=None):
    """
    Calculate polysubstance indicators

    Parameters:
    -----------
    df : pd.DataFrame
        Input dataframe
    substance_cols : list
        List of substance column names (defaults to SUBSTANCE_COLS)

    Returns:
    --------
    pd.DataFrame
        Dataframe with polysubstance indicators
    """
    if substance_cols is None:
        substance_cols = SUBSTANCE_COLS

    df['Number_Substances'] = df[substance_cols].sum(axis=1)
    df['Polysubstance'] = np.where(df['Number_Substances'] > 1, 1, 0)

    return df


def filter_to_study_period(df, year_col='Year', start=YEAR_START, end=YEAR_END):
    """
    Filter dataframe to study period

    Parameters:
    -----------
    df : pd.DataFrame
        Input dataframe
    year_col : str
        Name of the year column
    start : int
        Start year (inclusive)
    end : int
        End year (inclusive)

    Returns:
    --------
    pd.DataFrame
        Filtered dataframe
    """
    return df[df[year_col].between(start, end)].copy()


def full_data_processing(file_path='data/2012-01-2024-08-overdoses.csv',
                         filter_years=True):
    """
    Perform complete standard data processing pipeline

    Parameters:
    -----------
    file_path : str
        Path to the CSV file
    filter_years : bool
        Whether to filter to standard study period (2012-2023)

    Returns:
    --------
    pd.DataFrame
        Fully processed dataframe
    """
    # Load data
    df = load_overdose_data(file_path)

    # Filter years if requested
    if filter_years:
        df = filter_to_study_period(df)

    # Standardize race
    df = standardize_race(df)

    # Process age
    df = process_age(df)

    # Calculate polysubstance
    df = calculate_polysubstance(df)

    return df


def get_race_labels(format='long'):
    """
    Get standardized race labels

    Parameters:
    -----------
    format : str
        'long' for "White (NH)" or 'short' for "WHITE"

    Returns:
    --------
    dict
        Dictionary mapping race codes to labels
    """
    if format == 'long':
        return {
            'WHITE': 'White (NH)',
            'BLACK': 'Black (NH)',
            'LATINE': 'Latine',
            'ASIAN': 'Asian (NH)',
            'OTHER': 'Other',
            'UNKNOWN': 'Unknown'
        }
    else:
        return {k: k for k in RACE_CATEGORIES}


def get_substance_labels(format='standard'):
    """
    Get standardized substance labels

    Parameters:
    -----------
    format : str
        'standard' for normal labels, 'display' for plot-friendly labels

    Returns:
    --------
    dict or list
        Dictionary or list of substance labels
    """
    if format == 'display':
        return {
            'Prescription.opioids': 'Prescription\nOpioids',
            'Heroin': 'Heroin',
            'Fentanyl': 'Fentanyl',
            'Methamphetamine': 'Methamphetamine',
            'Cocaine': 'Cocaine',
            'Benzodiazepines': 'Benzodiazepines',
            'Alcohol': 'Alcohol',
            'Others': 'Others'
        }
    else:
        return SUBSTANCE_COLS


# Color palettes
RACE_COLORS = {
    'WHITE': '#4472C4',
    'BLACK': '#ED7D31',
    'LATINE': '#A5A5A5',
    'ASIAN': '#FFC000'
}

LANCET_COLORS = ['#00468B', '#ED0000', '#42B540', '#0099B4',
                 '#925E9F', '#FDAF91', '#AD002A', '#ADB6B6']
