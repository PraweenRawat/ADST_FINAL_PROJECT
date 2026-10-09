"""
Data Cleaning Pipeline for EV Charging Demand Project.

Decisions documented in dataset_audit_v2.md:
- Remove 17 rows with negative Duration (EndDatetime < StartDatetime)
- Remove rows where Duration==0 AND StartDatetime==EndDatetime (failed sessions)
- Remove 13 exact duplicate rows (keep first of each pair)
- Parse datetime columns
- Preserve raw CSV untouched
"""
import pandas as pd
import numpy as np
from pathlib import Path


def load_raw_data(raw_path: str) -> pd.DataFrame:
    """Load the raw CSV dataset without modification."""
    df = pd.read_csv(raw_path)
    return df


def parse_datetimes(df: pd.DataFrame) -> pd.DataFrame:
    """Parse string datetime columns into proper datetime objects."""
    df = df.copy()
    df['StartDatetime_parsed'] = pd.to_datetime(df['StartDatetime'], errors='coerce')
    df['EndDatetime_parsed'] = pd.to_datetime(df['EndDatetime'], errors='coerce')
    df['StartDay_parsed'] = pd.to_datetime(df['StartDay'], errors='coerce')
    return df


def remove_negative_duration(df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    """Remove rows where Duration < 0 (EndDatetime precedes StartDatetime)."""
    mask = df['Duration'] < 0
    removed = mask.sum()
    return df[~mask].copy(), removed


def remove_true_zero_duration(df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    """
    Remove rows where Duration==0 AND StartDatetime equals EndDatetime.
    These are failed/trivial sessions with essentially no charging.
    """
    mask = (df['Duration'] == 0) & (df['StartDatetime'] == df['EndDatetime'])
    removed = mask.sum()
    return df[~mask].copy(), removed


def remove_exact_duplicates(df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    """Remove exact duplicate rows, keeping the first occurrence."""
    before = len(df)
    df = df.drop_duplicates(keep='first')
    removed = before - len(df)
    return df, removed


def validate_demand(df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    """Remove rows with non-positive Demand (physically impossible)."""
    mask = df['Demand'] <= 0
    removed = mask.sum()
    return df[~mask].copy(), removed


def run_cleaning_pipeline(raw_path: str, processed_path: str) -> dict:
    """
    Execute the full cleaning pipeline.
    
    Returns a dictionary with cleaning statistics.
    """
    stats = {}
    
    # Load
    df = load_raw_data(raw_path)
    stats['raw_rows'] = len(df)
    stats['raw_columns'] = len(df.columns)
    
    # Parse datetimes
    df = parse_datetimes(df)
    
    # Step 1: Remove negative duration
    df, n_neg = remove_negative_duration(df)
    stats['removed_negative_duration'] = n_neg
    
    # Step 2: Remove true zero duration (Start==End, Dur==0)
    df, n_zero = remove_true_zero_duration(df)
    stats['removed_true_zero_duration'] = n_zero
    
    # Step 3: Remove exact duplicates
    df, n_dup = remove_exact_duplicates(df)
    stats['removed_exact_duplicates'] = n_dup
    
    # Step 4: Validate demand (should be > 0; already confirmed in audit but safety check)
    df, n_demand = validate_demand(df)
    stats['removed_invalid_demand'] = n_demand
    
    # Reset index
    df = df.reset_index(drop=True)
    
    stats['cleaned_rows'] = len(df)
    stats['total_removed'] = stats['raw_rows'] - stats['cleaned_rows']
    stats['removal_pct'] = round(stats['total_removed'] / stats['raw_rows'] * 100, 3)
    
    # Save cleaned dataset
    Path(processed_path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(processed_path, index=False)
    stats['output_path'] = processed_path
    
    return df, stats


if __name__ == '__main__':
    import json
    RAW = 'data/raw/ChargingRecords.csv'
    PROCESSED = 'data/processed/ChargingRecords_cleaned.csv'
    df, stats = run_cleaning_pipeline(RAW, PROCESSED)
    print(json.dumps(stats, indent=2))
