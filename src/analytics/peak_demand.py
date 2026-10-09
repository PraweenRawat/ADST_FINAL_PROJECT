"""
Peak Demand Analytics for EV Charging Demand Project.

Computes peak demand insights from actual historical charging data.
These are aggregated descriptive analytics — NOT ML predictions.
"""
import pandas as pd
import numpy as np


def compute_hourly_demand(df: pd.DataFrame) -> pd.DataFrame:
    """Average and total demand by hour of day."""
    if 'hour' not in df.columns:
        df = df.copy()
        df['hour'] = pd.to_datetime(df['StartDatetime']).dt.hour
    
    hourly = df.groupby('hour').agg(
        sessions=('Demand', 'count'),
        total_demand_kwh=('Demand', 'sum'),
        avg_demand_kwh=('Demand', 'mean'),
        median_demand_kwh=('Demand', 'median'),
        avg_duration_min=('Duration', 'mean'),
    ).reset_index()
    
    # Round for readability
    for col in ['total_demand_kwh', 'avg_demand_kwh', 'median_demand_kwh', 'avg_duration_min']:
        hourly[col] = hourly[col].round(2)
    
    return hourly


def compute_daily_demand(df: pd.DataFrame) -> pd.DataFrame:
    """Average and total demand by day of week."""
    if 'day_of_week' not in df.columns:
        df = df.copy()
        df['day_of_week'] = pd.to_datetime(df['StartDatetime']).dt.dayofweek
    
    day_names = {0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday',
                 4: 'Friday', 5: 'Saturday', 6: 'Sunday'}
    
    daily = df.groupby('day_of_week').agg(
        sessions=('Demand', 'count'),
        total_demand_kwh=('Demand', 'sum'),
        avg_demand_kwh=('Demand', 'mean'),
    ).reset_index()
    
    daily['day_name'] = daily['day_of_week'].map(day_names)
    
    for col in ['total_demand_kwh', 'avg_demand_kwh']:
        daily[col] = daily[col].round(2)
    
    return daily


def compute_monthly_demand(df: pd.DataFrame) -> pd.DataFrame:
    """Total and average demand by month."""
    dt = pd.to_datetime(df['StartDatetime'])
    df_copy = df.copy()
    df_copy['year_month'] = dt.dt.to_period('M').astype(str)
    
    monthly = df_copy.groupby('year_month').agg(
        sessions=('Demand', 'count'),
        total_demand_kwh=('Demand', 'sum'),
        avg_demand_kwh=('Demand', 'mean'),
    ).reset_index()
    
    for col in ['total_demand_kwh', 'avg_demand_kwh']:
        monthly[col] = monthly[col].round(2)
    
    return monthly


def compute_location_demand(df: pd.DataFrame) -> pd.DataFrame:
    """Demand statistics by location type."""
    location = df.groupby('Location').agg(
        sessions=('Demand', 'count'),
        total_demand_kwh=('Demand', 'sum'),
        avg_demand_kwh=('Demand', 'mean'),
        median_demand_kwh=('Demand', 'median'),
        avg_duration_min=('Duration', 'mean'),
    ).reset_index().sort_values('total_demand_kwh', ascending=False)
    
    for col in ['total_demand_kwh', 'avg_demand_kwh', 'median_demand_kwh', 'avg_duration_min']:
        location[col] = location[col].round(2)
    
    return location


def compute_charger_type_demand(df: pd.DataFrame) -> pd.DataFrame:
    """Demand statistics by charger type."""
    type_names = {0: 'Slow (AC)', 1: 'Fast (DC)'}
    
    charger = df.groupby('ChargerType').agg(
        sessions=('Demand', 'count'),
        total_demand_kwh=('Demand', 'sum'),
        avg_demand_kwh=('Demand', 'mean'),
        avg_duration_min=('Duration', 'mean'),
    ).reset_index()
    
    charger['type_name'] = charger['ChargerType'].map(type_names)
    
    for col in ['total_demand_kwh', 'avg_demand_kwh', 'avg_duration_min']:
        charger[col] = charger[col].round(2)
    
    return charger


def compute_charger_company_demand(df: pd.DataFrame) -> pd.DataFrame:
    """Demand statistics by charger company."""
    company = df.groupby('ChargerCompany').agg(
        sessions=('Demand', 'count'),
        total_demand_kwh=('Demand', 'sum'),
        avg_demand_kwh=('Demand', 'mean'),
    ).reset_index()
    
    for col in ['total_demand_kwh', 'avg_demand_kwh']:
        company[col] = company[col].round(2)
    
    return company


def compute_peak_periods(df: pd.DataFrame) -> dict:
    """
    Identify peak demand periods using data-driven methodology.
    
    Peak identification method:
    - Peak hour: hour with highest average demand per session
    - Peak day: day of week with highest average demand per session
    - Peak month: month with highest total demand
    - Peak date: specific date with highest total demand
    - Busiest hour: hour with most sessions
    - Top 10 chargers: by total demand
    """
    dt = pd.to_datetime(df['StartDatetime'])
    
    # Peak hour by average demand
    hourly_avg = df.groupby(dt.dt.hour)['Demand'].mean()
    peak_hour_avg = int(hourly_avg.idxmax())
    
    # Busiest hour by session count
    hourly_count = df.groupby(dt.dt.hour)['Demand'].count()
    busiest_hour = int(hourly_count.idxmax())
    
    # Peak hour by total demand
    hourly_total = df.groupby(dt.dt.hour)['Demand'].sum()
    peak_hour_total = int(hourly_total.idxmax())
    
    # Peak day of week
    day_names = {0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday',
                 4: 'Friday', 5: 'Saturday', 6: 'Sunday'}
    daily_avg = df.groupby(dt.dt.dayofweek)['Demand'].mean()
    peak_dow = int(daily_avg.idxmax())
    
    # Peak month (total)
    monthly_total = df.groupby(dt.dt.to_period('M'))['Demand'].sum()
    peak_month = str(monthly_total.idxmax())
    
    # Peak specific date (total)
    daily_total = df.groupby(dt.dt.date)['Demand'].sum()
    peak_date = str(daily_total.idxmax())
    peak_date_demand = round(float(daily_total.max()), 2)
    
    # Lowest demand date
    lowest_date = str(daily_total.idxmin())
    lowest_date_demand = round(float(daily_total.min()), 2)
    
    # Top 10 chargers by total demand
    charger_total = df.groupby('ChargerID')['Demand'].sum().sort_values(ascending=False)
    top_chargers = {int(k): round(float(v), 2) for k, v in charger_total.head(10).items()}
    
    # Top 10 locations by total demand
    loc_total = df.groupby('Location')['Demand'].sum().sort_values(ascending=False)
    top_locations = {str(k): round(float(v), 2) for k, v in loc_total.items()}
    
    # Weekday vs weekend
    is_weekend = dt.dt.dayofweek >= 5
    weekday_avg = round(float(df[~is_weekend]['Demand'].mean()), 2)
    weekend_avg = round(float(df[is_weekend]['Demand'].mean()), 2)
    
    # Hour x DayOfWeek heatmap data
    heatmap_data = df.groupby([dt.dt.dayofweek, dt.dt.hour])['Demand'].mean().round(2)
    heatmap_dict = {f"{dow}_{h}": float(v) for (dow, h), v in heatmap_data.items()}
    
    return {
        'peak_hour_by_avg_demand': peak_hour_avg,
        'peak_hour_by_avg_demand_kwh': round(float(hourly_avg.max()), 2),
        'peak_hour_by_total_demand': peak_hour_total,
        'peak_hour_by_total_demand_kwh': round(float(hourly_total.max()), 2),
        'busiest_hour_by_sessions': busiest_hour,
        'busiest_hour_sessions_count': int(hourly_count.max()),
        'peak_day_of_week': day_names[peak_dow],
        'peak_day_avg_demand_kwh': round(float(daily_avg.max()), 2),
        'peak_month': peak_month,
        'peak_month_total_kwh': round(float(monthly_total.max()), 2),
        'peak_date': peak_date,
        'peak_date_total_kwh': peak_date_demand,
        'lowest_demand_date': lowest_date,
        'lowest_demand_date_total_kwh': lowest_date_demand,
        'top_10_chargers_by_demand': top_chargers,
        'locations_by_total_demand': top_locations,
        'weekday_avg_demand_kwh': weekday_avg,
        'weekend_avg_demand_kwh': weekend_avg,
        'hour_dayofweek_heatmap': heatmap_dict,
    }


def compute_summary_stats(df: pd.DataFrame) -> dict:
    """Compute overall summary statistics for the dashboard."""
    return {
        'total_sessions': int(len(df)),
        'total_demand_kwh': round(float(df['Demand'].sum()), 2),
        'avg_demand_kwh': round(float(df['Demand'].mean()), 2),
        'median_demand_kwh': round(float(df['Demand'].median()), 2),
        'max_demand_kwh': round(float(df['Demand'].max()), 2),
        'min_demand_kwh': round(float(df['Demand'].min()), 2),
        'std_demand_kwh': round(float(df['Demand'].std()), 2),
        'avg_duration_min': round(float(df['Duration'].mean()), 2),
        'unique_chargers': int(df['ChargerID'].nunique()),
        'unique_users': int(df['UserID'].nunique()),
        'unique_locations': int(df['Location'].nunique()),
        'date_range_start': str(pd.to_datetime(df['StartDatetime']).min().date()),
        'date_range_end': str(pd.to_datetime(df['StartDatetime']).max().date()),
        'slow_charger_sessions': int((df['ChargerType'] == 0).sum()),
        'fast_charger_sessions': int((df['ChargerType'] == 1).sum()),
    }


def run_full_analytics(df: pd.DataFrame) -> dict:
    """Run all analytics and return complete results."""
    return {
        'summary': compute_summary_stats(df),
        'hourly_demand': compute_hourly_demand(df).to_dict(orient='records'),
        'daily_demand': compute_daily_demand(df).to_dict(orient='records'),
        'monthly_demand': compute_monthly_demand(df).to_dict(orient='records'),
        'location_demand': compute_location_demand(df).to_dict(orient='records'),
        'charger_type_demand': compute_charger_type_demand(df).to_dict(orient='records'),
        'charger_company_demand': compute_charger_company_demand(df).to_dict(orient='records'),
        'peak_demand': compute_peak_periods(df),
    }
