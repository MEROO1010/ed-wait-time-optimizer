import unittest
import pandas as pd
import numpy as np
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.generate_data import EDDataGenerator
from src.data_analysis import EDAnalytics
from src.utils import validate_data, calculate_performance_metrics

class TestEDDataGeneration(unittest.TestCase):
    """Test cases for data generation"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.generator = EDDataGenerator(seed=123)
        self.df = self.generator.generate_full_dataset(n_patients=100)
    
    def test_dataframe_structure(self):
        """Test DataFrame has correct structure"""
        self.assertIsInstance(self.df, pd.DataFrame)
        self.assertGreater(len(self.df), 0)
        
        # Check required columns
        required_columns = [
            'patient_id', 'arrival_time', 'triage_level', 'department',
            'wait_time_minutes', 'treatment_time_minutes', 'outcome'
        ]
        
        for col in required_columns:
            self.assertIn(col, self.df.columns)
    
    def test_patient_ids_unique(self):
        """Test patient IDs are unique"""
        self.assertEqual(len(self.df['patient_id'].unique()), len(self.df))
    
    def test_data_ranges(self):
        """Test data values are within reasonable ranges"""
        # Age between 0 and 120
        self.assertTrue(self.df['age'].between(0, 120).all())
        
        # Wait time positive
        self.assertTrue((self.df['wait_time_minutes'] >= 0).all())
        
        # Treatment time positive
        self.assertTrue((self.df['treatment_time_minutes'] >= 0).all())
    
    def test_triage_levels_valid(self):
        """Test triage levels are valid"""
        valid_triage = ["Resuscitation", "Emergency", "Urgent", "Less Urgent", "Non-Urgent"]
        self.assertTrue(self.df['triage_level'].isin(valid_triage).all())
    
    def test_datetime_format(self):
        """Test arrival_time is datetime"""
        self.assertEqual(str(self.df['arrival_time'].dtype), 'datetime64[ns]')

class TestEDAnalytics(unittest.TestCase):
    """Test cases for analytics functions"""
    
    def setUp(self):
        """Set up test fixtures"""
        generator = EDDataGenerator(seed=123)
        self.df = generator.generate_full_dataset(n_patients=100)
        self.analytics = EDAnalytics(self.df)
    
    def test_kpi_calculation(self):
        """Test KPI calculation"""
        kpis = self.analytics.calculate_kpis()
        
        self.assertIn('total_patients', kpis)
        self.assertIn('avg_wait_time', kpis)
        self.assertIn('admission_rate', kpis)
        
        # Check types
        self.assertIsInstance(kpis['total_patients'], int)
        self.assertIsInstance(kpis['avg_wait_time'], float)
        self.assertIsInstance(kpis['admission_rate'], float)
        
        # Check values are reasonable
        self.assertGreater(kpis['total_patients'], 0)
        self.assertGreaterEqual(kpis['avg_wait_time'], 0)
        self.assertGreaterEqual(kpis['admission_rate'], 0)
        self.assertLessEqual(kpis['admission_rate'], 1)
    
    def test_department_metrics(self):
        """Test department metrics calculation"""
        dept_metrics = self.analytics.get_department_metrics()
        
        self.assertGreater(len(dept_metrics), 0)
        self.assertIn('department', dept_metrics.columns)
        self.assertIn('patient_count', dept_metrics.columns)
        
        # Check all departments have metrics
        unique_depts = self.df['department'].unique()
        self.assertEqual(len(dept_metrics), len(unique_depts))
    
    def test_hourly_volume(self):
        """Test hourly volume calculation"""
        hourly = self.analytics.get_hourly_volume()
        
        self.assertEqual(len(hourly), 24)  # 24 hours
        self.assertIn('arrival_hour', hourly.columns)
        self.assertIn('patient_count', hourly.columns)
        
        # Check hours are 0-23
        self.assertTrue(hourly['arrival_hour'].between(0, 23).all())
    
    def test_visualizations(self):
        """Test visualization generation"""
        plots = self.analytics.create_visualizations()
        
        expected_plots = ['heatmap', 'triage_dist', 'wait_time_box', 
                         'volume_trend', 'outcomes', 'scatter']
        
        for plot_name in expected_plots:
            self.assertIn(plot_name, plots)

class TestUtils(unittest.TestCase):
    """Test cases for utility functions"""
    
    def setUp(self):
        """Set up test fixtures"""
        generator = EDDataGenerator(seed=123)
        self.df = generator.generate_full_dataset(n_patients=100)
    
    def test_validate_data(self):
        """Test data validation"""
        validation = validate_data(self.df)
        
        self.assertIn('status', validation)
        self.assertIn('data_quality_score', validation)
        self.assertIn('missing_values', validation)
        
        # Quality score should be between 0 and 100
        self.assertGreaterEqual(validation['data_quality_score'], 0)
        self.assertLessEqual(validation['data_quality_score'], 100)
    
    def test_performance_metrics(self):
        """Test performance metrics calculation"""
        metrics = calculate_performance_metrics(self.df)
        
        self.assertIn('avg_wait_time', metrics)
        self.assertIn('admission_rate', metrics)
        self.assertIn('discharge_rate', metrics)
        
        # Admission rate should be reasonable
        self.assertGreaterEqual(metrics['admission_rate'], 0)
        self.assertLessEqual(metrics['admission_rate'], 1)
    
    def test_anomaly_detection(self):
        """Test anomaly detection"""
        from src.utils import detect_anomalies
        
        # Add some extreme values for testing
        test_df = self.df.copy()
        test_df.loc[0, 'wait_time_minutes'] = 1000  # Extreme value
        
        anomalies = detect_anomalies(test_df, 'wait_time_minutes', method='iqr')
        
        self.assertIn('is_anomaly', anomalies.columns)
        self.assertIn('anomaly_reason', anomalies.columns)
        
        # Should detect the extreme value
        self.assertTrue(anomalies.loc[0, 'is_anomaly'])

def run_tests():
    """Run all tests"""
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestEDDataGeneration)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestEDAnalytics))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestUtils))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result

if __name__ == '__main__':
    # Run tests
    print("Running Emergency Department Analytics Tests...")
    print("=" * 60)
    
    result = run_tests()
    
    print("\n" + "=" * 60)
    if result.wasSuccessful():
        print("✅ All tests passed!")
    else:
        print(f"❌ Tests failed: {len(result.failures)} failures, {len(result.errors)} errors")
    
    # Exit with appropriate code
    exit(0 if result.wasSuccessful() else 1)