"""
Feature Engineering for EV Charging Demand Project.

Per dataset_audit_v2.md:
- Only features available at session start time
- Excluded: UserID, ChargerID (raw), Duration, EndDay, EndTime, EndDatetime
- Included: hour, day_of_week, month, is_weekend, Location, ChargerType, ChargerCompany
- Chronological train/val/test split by date boundaries
"""
import pandas as pd
import numpy as np
from typing import Optional


# Date boundaries from audit v2
TRAIN_END = '2022-07-16'
VAL_START = '2022-07-17'
VAL_END = '2022-08-13'
TEST_START = '2022-08-14'
# Test ends at the last record in the dataset


# Baseline feature columns
NUMERICAL_FEATURES = ['hour', 'day_of_week', 'month', 'is_weekend', 'ChargerType', 'ChargerCompany']
CATEGORICAL_FEATURES = ['Location']
ALL_FEATURES = NUMERICAL_FEATURES + CATEGORICAL_FEATURES
TARGET = 'Demand'

# Features excluded and reasons
EXCLUDED_FEATURES = {
    'UserID': 'High cardinality (2337), 43% anonymous, memorization risk, marginal predictive value (1.5 kWh diff)',
    'ChargerID': 'High cardinality (2119), 250 single-session chargers, excluded from baseline',
    'Duration': 'Only known after session ends — temporal leakage',
    'EndDay': 'Only known after session ends — temporal leakage',
    'EndTime': 'Only known after session ends — temporal leakage',
    'EndDatetime': 'Only known after session ends — temporal leakage',
    'StartDay': 'Raw string; replaced by extracted temporal features (month, day_of_week, is_weekend)',
    'StartTime': 'Raw string; replaced by extracted hour feature',
    'StartDatetime': 'Used as temporal key for splitting; not a model feature',
    'EndDatetime_parsed': 'Derived; excluded (leakage)',
    'StartDatetime_parsed': 'Used for splitting/feature extraction; not passed to model',
    'StartDay_parsed': 'Derived; used for splitting; not passed to model',
}


def extract_temporal_features(df: pd.DataFrame) -> pd.DataFrame:
    """Extract temporal features from parsed StartDatetime."""
    df = df.copy()
    
    # Ensure datetime is parsed
    if 'StartDatetime_parsed' not in df.columns:
        df['StartDatetime_parsed'] = pd.to_datetime(df['StartDatetime'], errors='coerce')
    
    dt = df['StartDatetime_parsed']
    df['hour'] = dt.dt.hour
    df['day_of_week'] = dt.dt.dayofweek  # 0=Monday, 6=Sunday
    df['month'] = dt.dt.month
    df['is_weekend'] = (dt.dt.dayofweek >= 5).astype(int)
    
    return df


def chronological_split(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Split dataset chronologically by date boundaries.
    
    Train: start → 2022-07-16
    Validation: 2022-07-17 → 2022-08-13
    Test: 2022-08-14 → end
    """
    if 'StartDatetime_parsed' not in df.columns:
        df['StartDatetime_parsed'] = pd.to_datetime(df['StartDatetime'], errors='coerce')
    
    # Sort by start datetime to ensure chronological order
    df = df.sort_values('StartDatetime_parsed').reset_index(drop=True)
    
    train_mask = df['StartDatetime_parsed'] <= pd.Timestamp(TRAIN_END + ' 23:59:59')
    val_mask = (df['StartDatetime_parsed'] >= pd.Timestamp(VAL_START)) & \
               (df['StartDatetime_parsed'] <= pd.Timestamp(VAL_END + ' 23:59:59'))
    test_mask = df['StartDatetime_parsed'] >= pd.Timestamp(TEST_START)
    
    train = df[train_mask].copy()
    val = df[val_mask].copy()
    test = df[test_mask].copy()
    
    return train, val, test


def prepare_features_target(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """
    Extract the feature matrix X and target vector y.
    Uses only the approved baseline features.
    """
    X = df[ALL_FEATURES].copy()
    y = df[TARGET].copy()
    return X, y


def get_feature_info() -> dict:
    """Return metadata about the feature set."""
    return {
        'numerical_features': NUMERICAL_FEATURES,
        'categorical_features': CATEGORICAL_FEATURES,
        'all_features': ALL_FEATURES,
        'target': TARGET,
        'excluded_features': EXCLUDED_FEATURES,
        'split_boundaries': {
            'train_end': TRAIN_END,
            'val_start': VAL_START,
            'val_end': VAL_END,
            'test_start': TEST_START,
        }
    }
