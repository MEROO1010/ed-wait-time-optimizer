import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import pickle
import os
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

def validate_data(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Validate emergency department data for quality and completeness
    
    Returns:
        Dictionary with validation results
    """
    validation_results = {
        "status": "PASS",
        "total_records": len(df),
        "missing_values": {},
        "invalid_values": {},
        "data_quality_score": 0,
        "warnings": [],
        "errors": []
    }
    
    # Check for missing values
    missing_counts = df.isnull().sum()
    validation_results["missing_values"] = missing_counts[missing_counts > 0].to_dict()
    
    # Check data types
    expected_dtypes = {
        'patient_id': 'object',
        'age': 'int64',
        'wait_time_minutes': 'float64',
        'treatment_time_minutes': 'float64',
        'arrival_time': 'datetime64[ns]'
    }
    
    for col, expected_type in expected_dtypes.items():
        if col in df.columns:
            actual_type = str(df[col].dtype)
            if expected_type not in actual_type:
                validation_results["warnings"].append(
                    f"Column '{col}' has dtype {actual_type}, expected {expected_type}"
                )
    
    # Validate numeric ranges
    if 'age' in df.columns:
        invalid_ages = df[(df['age'] < 0) | (df['age'] > 120)]
        if len(invalid_ages) > 0:
            validation_results["invalid_values"]["age"] = len(invalid_ages)
            validation_results["errors"].append(
                f"Found {len(invalid_ages)} records with invalid age values"
            )
    
    if 'wait_time_minutes' in df.columns:
        invalid_wait = df[df['wait_time_minutes'] < 0]
        if len(invalid_wait) > 0:
            validation_results["invalid_values"]["wait_time_minutes"] = len(invalid_wait)
    
    # Check for duplicates
    duplicate_count = df.duplicated(subset=['patient_id', 'arrival_time']).sum()
    if duplicate_count > 0:
        validation_results["warnings"].append(
            f"Found {duplicate_count} potential duplicate records"
        )
    
    # Calculate data quality score (0-100)
    total_cells = df.shape[0] * df.shape[1]
    missing_cells = df.isnull().sum().sum()
    quality_score = 100 * (1 - missing_cells / total_cells)
    validation_results["data_quality_score"] = round(quality_score, 2)
    
    # Update status based on findings
    if validation_results["errors"]:
        validation_results["status"] = "FAIL"
    elif validation_results["warnings"]:
        validation_results["status"] = "WARNING"
    
    return validation_results

def calculate_performance_metrics(df: pd.DataFrame) -> Dict[str, float]:
    """
    Calculate standard ED performance metrics
    
    Returns:
        Dictionary with performance metrics
    """
    metrics = {}
    
    # Time-based metrics
    if 'wait_time_minutes' in df.columns:
        metrics['avg_wait_time'] = df['wait_time_minutes'].mean()
        metrics['median_wait_time'] = df['wait_time_minutes'].median()
        metrics['p90_wait_time'] = df['wait_time_minutes'].quantile(0.9)
    
    if 'treatment_time_minutes' in df.columns:
        metrics['avg_treatment_time'] = df['treatment_time_minutes'].mean()
        metrics['total_ed_time'] = (df['wait_time_minutes'] + df['treatment_time_minutes']).mean()
    
    # Outcome metrics
    if 'outcome' in df.columns:
        metrics['admission_rate'] = (df['outcome'] == 'Admitted').mean()
        metrics['lwot_rate'] = (df['outcome'] == 'Left without treatment').mean()
        metrics['discharge_rate'] = (df['outcome'] == 'Discharged').mean()
    
    # Triage metrics
    if 'triage_level' in df.columns:
        triage_dist = df['triage_level'].value_counts(normalize=True)
        for level, rate in triage_dist.items():
            metrics[f'triage_{level.lower().replace(" ", "_")}_rate'] = rate
    
    # Department metrics
    if 'department' in df.columns:
        metrics['department_count'] = df['department'].nunique()
        dept_volume = df['department'].value_counts().to_dict()
        metrics['busiest_department'] = max(dept_volume, key=dept_volume.get)
    
    # Round numeric values
    for key in metrics:
        if isinstance(metrics[key], float):
            metrics[key] = round(metrics[key], 3)
    
    return metrics

def export_data(df: pd.DataFrame, format: str = 'csv', 
                filename: str = None, **kwargs) -> str:
    """
    Export DataFrame to various formats
    
    Args:
        df: DataFrame to export
        format: Export format ('csv', 'excel', 'json', 'parquet')
        filename: Output filename (optional)
        **kwargs: Additional arguments for the export function
    
    Returns:
        Path to exported file
    """
    if filename is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"ed_data_export_{timestamp}"
    
    if format.lower() == 'csv':
        filepath = f"{filename}.csv"
        df.to_csv(filepath, index=False, **kwargs)
    
    elif format.lower() == 'excel':
        filepath = f"{filename}.xlsx"
        df.to_excel(filepath, index=False, **kwargs)
    
    elif format.lower() == 'json':
        filepath = f"{filename}.json"
        df.to_json(filepath, orient='records', date_format='iso', **kwargs)
    
    elif format.lower() == 'parquet':
        filepath = f"{filename}.parquet"
        df.to_parquet(filepath, index=False, **kwargs)
    
    else:
        raise ValueError(f"Unsupported format: {format}")
    
    logger.info(f"Exported data to {filepath}")
    return filepath

def detect_anomalies(df: pd.DataFrame, column: str, 
                     method: str = 'iqr', threshold: float = 1.5) -> pd.DataFrame:
    """
    Detect anomalies in a column using statistical methods
    
    Args:
        df: Input DataFrame
        column: Column to analyze
        method: Detection method ('iqr', 'zscore', 'percentile')
        threshold: Detection threshold
    
    Returns:
        DataFrame with anomaly flags
    """
    df_result = df.copy()
    
    if method == 'iqr':
        Q1 = df[column].quantile(0.25)
        Q3 = df[column].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - threshold * IQR
        upper_bound = Q3 + threshold * IQR
        
        df_result['is_anomaly'] = ~df[column].between(lower_bound, upper_bound)
        df_result['anomaly_reason'] = np.where(
            df[column] < lower_bound, f'Below {lower_bound:.2f}',
            np.where(df[column] > upper_bound, f'Above {upper_bound:.2f}', 'Normal')
        )
    
    elif method == 'zscore':
        mean = df[column].mean()
        std = df[column].std()
        df_result['zscore'] = (df[column] - mean) / std
        df_result['is_anomaly'] = abs(df_result['zscore']) > threshold
        df_result['anomaly_reason'] = np.where(
            df_result['is_anomaly'], f'Z-score: {df_result["zscore"]:.2f}', 'Normal'
        )
    
    elif method == 'percentile':
        lower = df[column].quantile(threshold / 2 / 100)
        upper = df[column].quantile(1 - threshold / 2 / 100)
        df_result['is_anomaly'] = ~df[column].between(lower, upper)
        df_result['anomaly_reason'] = np.where(
            df[column] < lower, f'Below {threshold/2}th percentile',
            np.where(df[column] > upper, f'Above {100-threshold/2}th percentile', 'Normal')
        )
    
    return df_result

def generate_summary_statistics(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Generate comprehensive summary statistics for the dataset
    
    Returns:
        Dictionary with summary statistics
    """
    summary = {
        "dataset_info": {
            "shape": df.shape,
            "columns": df.columns.tolist(),
            "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "memory_usage_mb": df.memory_usage(deep=True).sum() / 1024**2
        },
        "numeric_summary": {},
        "categorical_summary": {},
        "temporal_summary": {}
    }
    
    # Numeric columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        summary["numeric_summary"][col] = {
            "count": int(df[col].count()),
            "mean": float(df[col].mean()),
            "std": float(df[col].std()),
            "min": float(df[col].min()),
            "25%": float(df[col].quantile(0.25)),
            "50%": float(df[col].median()),
            "75%": float(df[col].quantile(0.75)),
            "max": float(df[col].max()),
            "missing": int(df[col].isnull().sum())
        }
    
    # Categorical columns
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns
    for col in categorical_cols:
        value_counts = df[col].value_counts()
        summary["categorical_summary"][col] = {
            "unique_values": int(df[col].nunique()),
            "top_value": value_counts.index[0] if len(value_counts) > 0 else None,
            "top_frequency": int(value_counts.iloc[0]) if len(value_counts) > 0 else None,
            "missing": int(df[col].isnull().sum())
        }
    
    # Temporal columns
    temporal_cols = df.select_dtypes(include=['datetime64']).columns
    for col in temporal_cols:
        summary["temporal_summary"][col] = {
            "min": df[col].min().isoformat() if pd.notnull(df[col].min()) else None,
            "max": df[col].max().isoformat() if pd.notnull(df[col].max()) else None,
            "range_days": (df[col].max() - df[col].min()).days if len(df[col].dropna()) > 1 else None,
            "missing": int(df[col].isnull().sum())
        }
    
    return summary

def save_model(model, filename: str):
    """
    Save trained model to disk
    
    Args:
        model: Trained model object
        filename: Output filename
    """
    with open(filename, 'wb') as f:
        pickle.dump(model, f)
    logger.info(f"Model saved to {filename}")

def load_model(filename: str):
    """
    Load trained model from disk
    
    Args:
        filename: Model filename
    
    Returns:
        Loaded model object
    """
    with open(filename, 'rb') as f:
        model = pickle.load(f)
    logger.info(f"Model loaded from {filename}")
    return model

def format_timedelta(minutes: float) -> str:
    """
    Format minutes into human-readable time string
    
    Args:
        minutes: Time in minutes
    
    Returns:
        Formatted time string (e.g., "2h 30m")
    """
    hours = int(minutes // 60)
    mins = int(minutes % 60)
    
    if hours > 0:
        return f"{hours}h {mins}m"
    else:
        return f"{mins}m"

def create_report_template() -> str:
    """
    Create HTML report template for ED analytics
    
    Returns:
        HTML template string
    """
    template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Emergency Department Analytics Report</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .header { background-color: #1f77b4; color: white; padding: 20px; border-radius: 10px; }
            .section { margin: 30px 0; border-left: 5px solid #3498db; padding-left: 15px; }
            .metric { display: inline-block; background-color: #f8f9fa; padding: 15px; margin: 10px; 
                     border-radius: 5px; min-width: 200px; }
            .metric-value { font-size: 24px; font-weight: bold; color: #2c3e50; }
            .metric-label { color: #7f8c8d; font-size: 14px; }
            .warning { background-color: #fff3cd; border-left: 5px solid #ffc107; padding: 10px; }
            .success { background-color: #d4edda; border-left: 5px solid #28a745; padding: 10px; }
            table { border-collapse: collapse; width: 100%; margin: 20px 0; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Emergency Department Analytics Report</h1>
            <p>Generated on: {{generation_date}}</p>
            <p>Data period: {{data_period}}</p>
        </div>
        
        <div class="section">
            <h2>Executive Summary</h2>
            {{executive_summary}}
        </div>
        
        <div class="section">
            <h2>Key Performance Indicators</h2>
            {{kpi_metrics}}
        </div>
        
        <div class="section">
            <h2>Performance Analysis</h2>
            {{performance_analysis}}
        </div>
        
        <div class="section">
            <h2>Recommendations</h2>
            {{recommendations}}
        </div>
    </body>
    </html>
    """
    return template