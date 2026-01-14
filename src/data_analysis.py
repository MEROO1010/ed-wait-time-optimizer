import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import logging
from config.settings import WAIT_TIME_THRESHOLDS

logger = logging.getLogger(__name__)

class EDAnalytics:
    """Emergency Department analytics engine"""
    
    def __init__(self, df):
        """Initialize with DataFrame"""
        self.df = df.copy()
        self.df['arrival_time'] = pd.to_datetime(self.df['arrival_time'])
        self.df['arrival_hour'] = self.df['arrival_time'].dt.hour
        self.df['arrival_day'] = self.df['arrival_time'].dt.day_name()
        self.df['arrival_month'] = self.df['arrival_time'].dt.month_name()
        self.df['arrival_date'] = self.df['arrival_time'].dt.date
        
        # Calculate performance metrics
        self.df['wait_time_exceeds'] = self.df.apply(
            lambda row: row['wait_time_minutes'] > WAIT_TIME_THRESHOLDS.get(row['triage_level'], 120),
            axis=1
        )
        
    def calculate_kpis(self):
        """Calculate Key Performance Indicators"""
        kpis = {
            "total_patients": len(self.df),
            "avg_wait_time": self.df['wait_time_minutes'].mean(),
            "avg_treatment_time": self.df['treatment_time_minutes'].mean(),
            "avg_total_time": self.df['total_time_minutes'].mean(),
            "admission_rate": (self.df['outcome'] == 'Admitted').mean(),
            "left_without_treatment": (self.df['outcome'] == 'Left without treatment').mean(),
            "avg_pain_level": self.df['pain_level'].mean(),
            "wait_time_exceed_rate": self.df['wait_time_exceeds'].mean(),
            "avg_cost": self.df['estimated_cost_usd'].mean()
        }
        
        # Round numeric values
        for key in kpis:
            if isinstance(kpis[key], float):
                kpis[key] = round(kpis[key], 2)
        
        return kpis
    
    def get_department_metrics(self):
        """Calculate metrics by department"""
        dept_metrics = self.df.groupby('department').agg({
            'record_id': 'count',
            'wait_time_minutes': 'mean',
            'treatment_time_minutes': 'mean',
            'total_time_minutes': 'mean',
            'outcome': lambda x: (x == 'Admitted').mean(),
            'estimated_cost_usd': 'mean',
            'pain_level': 'mean'
        }).round(2)
        
        dept_metrics = dept_metrics.rename(columns={
            'record_id': 'patient_count',
            'outcome': 'admission_rate'
        })
        
        return dept_metrics.reset_index()
    
    def get_triage_metrics(self):
        """Calculate metrics by triage level"""
        triage_metrics = self.df.groupby('triage_level').agg({
            'record_id': 'count',
            'wait_time_minutes': ['mean', 'median', 'max'],
            'treatment_time_minutes': 'mean',
            'admission_ward': lambda x: (x != '').mean(),
            'estimated_cost_usd': 'mean'
        }).round(2)
        
        triage_metrics.columns = ['_'.join(col).strip() for col in triage_metrics.columns.values]
        triage_metrics = triage_metrics.rename(columns={
            'record_id_count': 'patient_count',
            'wait_time_minutes_mean': 'avg_wait_time',
            'wait_time_minutes_median': 'median_wait_time',
            'wait_time_minutes_max': 'max_wait_time'
        })
        
        return triage_metrics.reset_index()
    
    def get_hourly_volume(self):
        """Calculate patient volume by hour"""
        hourly = self.df.groupby('arrival_hour').agg({
            'record_id': 'count',
            'wait_time_minutes': 'mean',
            'triage_level': lambda x: (x == 'Resuscitation').mean()
        }).round(2)
        
        hourly = hourly.rename(columns={
            'record_id': 'patient_count',
            'triage_level': 'resuscitation_rate'
        })
        
        return hourly.reset_index()
    
    def get_time_series_analysis(self, freq='D'):
        """Get time series data for trend analysis"""
        df_copy = self.df.copy()
        df_copy.set_index('arrival_time', inplace=True)
        
        time_series = df_copy.resample(freq).agg({
            'record_id': 'count',
            'wait_time_minutes': 'mean',
            'treatment_time_minutes': 'mean',
            'outcome': lambda x: (x == 'Admitted').mean(),
            'estimated_cost_usd': 'sum'
        }).round(2)
        
        time_series = time_series.rename(columns={
            'record_id': 'daily_patients',
            'outcome': 'admission_rate'
        })
        
        return time_series.reset_index()
    
    def get_patient_demographics(self):
        """Analyze patient demographics"""
        demographics = {
            "age_groups": pd.cut(self.df['age'], 
                                 bins=[0, 18, 40, 65, 100],
                                 labels=['Pediatric', 'Young Adult', 'Adult', 'Senior']).value_counts(),
            "gender_dist": self.df['gender'].value_counts(),
            "insurance_dist": self.df['insurance'].value_counts(),
            "arrival_mode": self.df['arrival_mode'].value_counts()
        }
        
        return demographics
    
    def get_top_complaints(self, n=10):
        """Get top chief complaints"""
        complaints = self.df['chief_complaint'].value_counts().head(n)
        return complaints.reset_index().rename(columns={'index': 'complaint', 'chief_complaint': 'count'})
    
    def get_resource_utilization(self):
        """Analyze resource utilization"""
        utilization = {
            "lab_tests_requested": self.df['needs_lab_tests'].sum(),
            "imaging_requested": self.df['needs_imaging'].sum(),
            "avg_prior_visits": self.df['prior_ed_visits'].mean(),
            "doctors_used": self.df['doctor_assigned'].nunique()
        }
        
        return utilization
    
    def identify_bottlenecks(self):
        """Identify potential bottlenecks in ED flow"""
        bottlenecks = []
        
        # Check wait time thresholds
        exceed_by_triage = self.df.groupby('triage_level')['wait_time_exceeds'].mean()
        for triage, rate in exceed_by_triage.items():
            if rate > 0.1:  # More than 10% exceed threshold
                bottlenecks.append({
                    'type': 'Wait Time',
                    'triage_level': triage,
                    'exceed_rate': round(rate * 100, 1),
                    'threshold': WAIT_TIME_THRESHOLDS[triage]
                })
        
        # Check peak hours with high volume
        hourly_volume = self.get_hourly_volume()
        peak_hours = hourly_volume[hourly_volume['patient_count'] > hourly_volume['patient_count'].quantile(0.75)]
        
        for _, row in peak_hours.iterrows():
            bottlenecks.append({
                'type': 'Peak Volume',
                'hour': int(row['arrival_hour']),
                'patient_count': int(row['patient_count']),
                'avg_wait_time': row['wait_time_minutes']
            })
        
        return bottlenecks
    
    def generate_performance_report(self):
        """Generate comprehensive performance report"""
        report = {
            "summary": self.calculate_kpis(),
            "department_analysis": self.get_department_metrics().to_dict('records'),
            "triage_analysis": self.get_triage_metrics().to_dict('records'),
            "hourly_patterns": self.get_hourly_volume().to_dict('records'),
            "demographics": {k: v.to_dict() for k, v in self.get_patient_demographics().items()},
            "top_complaints": self.get_top_complaints(15).to_dict('records'),
            "resource_utilization": self.get_resource_utilization(),
            "bottlenecks": self.identify_bottlenecks(),
            "generated_at": datetime.now().isoformat(),
            "data_range": {
                "start": self.df['arrival_time'].min().isoformat(),
                "end": self.df['arrival_time'].max().isoformat()
            }
        }
        
        return report
    
    def create_visualizations(self):
        """Create standard visualizations for dashboard"""
        plots = {}
        
        # 1. Hourly volume heatmap
        df_heatmap = self.df.copy()
        df_heatmap['day_of_week'] = df_heatmap['arrival_time'].dt.dayofweek
        df_heatmap['hour_of_day'] = df_heatmap['arrival_time'].dt.hour
        
        heatmap_data = df_heatmap.groupby(['day_of_week', 'hour_of_day']).size().unstack()
        
        fig_heatmap = px.imshow(
            heatmap_data,
            labels=dict(x="Hour of Day", y="Day of Week", color="Patient Count"),
            x=[f"{h:02d}:00" for h in range(24)],
            y=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
            title="Patient Arrivals by Day and Hour"
        )
        plots['heatmap'] = fig_heatmap
        
        # 2. Triage distribution
        triage_counts = self.df['triage_level'].value_counts().reset_index()
        triage_counts.columns = ['triage_level', 'count']
        
        fig_triage = px.pie(
            triage_counts,
            values='count',
            names='triage_level',
            title='Distribution by Triage Level',
            color='triage_level',
            color_discrete_sequence=px.colors.sequential.RdBu
        )
        plots['triage_dist'] = fig_triage
        
        # 3. Wait time by department
        fig_wait = px.box(
            self.df,
            x='department',
            y='wait_time_minutes',
            title='Wait Time Distribution by Department',
            points=False
        )
        plots['wait_time_box'] = fig_wait
        
        # 4. Time series of patient volume
        time_series = self.get_time_series_analysis('D')
        fig_volume = px.line(
            time_series,
            x='arrival_time',
            y='daily_patients',
            title='Daily Patient Volume',
            markers=True
        )
        plots['volume_trend'] = fig_volume
        
        # 5. Outcome distribution
        outcome_counts = self.df['outcome'].value_counts().reset_index()
        outcome_counts.columns = ['outcome', 'count']
        
        fig_outcome = px.bar(
            outcome_counts,
            x='outcome',
            y='count',
            title='Patient Outcomes',
            color='outcome',
            text='count'
        )
        plots['outcomes'] = fig_outcome
        
        # 6. Scatter plot: Wait time vs Treatment time
        fig_scatter = px.scatter(
            self.df.sample(min(1000, len(self.df))),
            x='wait_time_minutes',
            y='treatment_time_minutes',
            color='triage_level',
            size='pain_level',
            hover_data=['chief_complaint', 'department'],
            title='Wait Time vs Treatment Time'
        )
        plots['scatter'] = fig_scatter
        
        return plots