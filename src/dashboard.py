import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
import sys
import warnings
warnings.filterwarnings('ignore')

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.generate_ed_data import EDDataGenerator
from src.data_analysis import EDAnalytics
from config.settings import *

# Page configuration
st.set_page_config(
    page_title=DASHBOARD_TITLE,
    page_icon="🏥",
    layout=DASHBOARD_LAYOUT,
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #2c3e50;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #3498db;
        padding-bottom: 0.5rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1rem;
        border-left: 5px solid #3498db;
        margin-bottom: 1rem;
    }
    .warning-card {
        background-color: #fff3cd;
        border-radius: 10px;
        padding: 1rem;
        border-left: 5px solid #ffc107;
        margin-bottom: 1rem;
    }
    .success-card {
        background-color: #d4edda;
        border-radius: 10px;
        padding: 1rem;
        border-left: 5px solid #28a745;
        margin-bottom: 1rem;
    }
    .stDataFrame {
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_or_generate_data():
    """Load existing data or generate new data"""
    data_path = os.path.join(DATA_PATH, "emergency_department_data.csv")
    
    if not os.path.exists(data_path):
        st.info("📊 Generating emergency department data... This may take a moment.")
        generator = EDDataGenerator()
        df = generator.generate_full_dataset(n_patients=DEFAULT_N_PATIENTS, start_date=START_DATE)
        csv_path, _ = generator.save_dataset(df)
        return df
    else:
        df = pd.read_csv(data_path)
        df['arrival_time'] = pd.to_datetime(df['arrival_time'])
        return df

@st.cache_resource
def initialize_analytics(df):
    """Initialize analytics engine"""
    return EDAnalytics(df)

def create_kpi_metrics(analytics):
    """Create KPI metrics display"""
    kpis = analytics.calculate_kpis()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Patients",
            value=f"{kpis['total_patients']:,}",
            delta=None
        )
    
    with col2:
        st.metric(
            label="Avg Wait Time",
            value=f"{kpis['avg_wait_time']} min",
            delta=f"{kpis['wait_time_exceed_rate']:.1%} exceed"
        )
    
    with col3:
        st.metric(
            label="Admission Rate",
            value=f"{kpis['admission_rate']:.1%}",
            delta=None
        )
    
    with col4:
        st.metric(
            label="Avg Cost",
            value=f"${kpis['avg_cost']:,.0f}",
            delta=None
        )
    
    # Additional metrics row
    col5, col6, col7, col8 = st.columns(4)
    
    with col5:
        st.metric(
            label="Avg Treatment Time",
            value=f"{kpis['avg_treatment_time']} min"
        )
    
    with col6:
        st.metric(
            label="Left Without Treatment",
            value=f"{kpis['left_without_treatment']:.1%}"
        )
    
    with col7:
        st.metric(
            label="Avg Pain Level",
            value=f"{kpis['avg_pain_level']}/10"
        )
    
    with col8:
        st.metric(
            label="Total Time in ED",
            value=f"{kpis['avg_total_time']} min"
        )

def display_bottlenecks(analytics):
    """Display identified bottlenecks"""
    bottlenecks = analytics.identify_bottlenecks()
    
    if bottlenecks:
        st.markdown('<div class="sub-header">⚠️ Identified Bottlenecks</div>', unsafe_allow_html=True)
        
        for bottleneck in bottlenecks:
            if bottleneck['type'] == 'Wait Time':
                st.warning(
                    f"**{bottleneck['triage_level']} patients**: "
                    f"{bottleneck['exceed_rate']}% exceed {bottleneck['threshold']}-minute wait target"
                )
            elif bottleneck['type'] == 'Peak Volume':
                st.info(
                    f"**Peak hour {bottleneck['hour']:02d}:00**: "
                    f"{bottleneck['patient_count']} patients with avg wait {bottleneck['avg_wait_time']:.0f} min"
                )

def create_dashboard():
    """Main dashboard function"""
    # Header
    st.markdown('<div class="main-header">🏥 Emergency Department Analytics Dashboard</div>', 
                unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 🔧 Controls")
        
        # Date range filter
        st.markdown("#### Date Range")
        min_date = df['arrival_time'].min().date()
        max_date = df['arrival_time'].max().date()
        
        date_range = st.date_input(
            "Select date range:",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
        
        # Department filter
        st.markdown("#### Department Filter")
        all_departments = df['department'].unique().tolist()
        selected_depts = st.multiselect(
            "Select departments:",
            options=all_departments,
            default=all_departments
        )
        
        # Triage filter
        st.markdown("#### Triage Filter")
        all_triage = df['triage_level'].unique().tolist()
        selected_triage = st.multiselect(
            "Select triage levels:",
            options=all_triage,
            default=all_triage
        )
        
        # Data refresh
        st.markdown("---")
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.cache_data.clear()
            st.cache_resource.clear()
            st.rerun()
        
        # Data export
        st.markdown("---")
        st.markdown("### 📤 Export Data")
        export_format = st.selectbox("Format:", ["CSV", "Excel", "JSON"])
        
        if st.button("💾 Download Data", use_container_width=True):
            filtered_df = filter_data(df, date_range, selected_depts, selected_triage)
            
            if export_format == "CSV":
                csv = filtered_df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name="ed_data_export.csv",
                    mime="text/csv"
                )
            elif export_format == "Excel":
                excel_path = "temp_export.xlsx"
                filtered_df.to_excel(excel_path, index=False)
                with open(excel_path, "rb") as f:
                    st.download_button(
                        label="Download Excel",
                        data=f,
                        file_name="ed_data_export.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                os.remove(excel_path)
            else:  # JSON
                json_str = filtered_df.to_json(orient='records', date_format='iso')
                st.download_button(
                    label="Download JSON",
                    data=json_str,
                    file_name="ed_data_export.json",
                    mime="application/json"
                )
        
        # Statistics
        st.markdown("---")
        st.markdown("### 📊 Quick Stats")
        st.info(f"**Total Records:** {len(df):,}")
        st.info(f"**Date Range:** {min_date} to {max_date}")
        st.info(f"**Departments:** {len(all_departments)}")

    # Apply filters
    filtered_df = filter_data(df, date_range, selected_depts, selected_triage)
    analytics = initialize_analytics(filtered_df)
    
    # Main dashboard content
    st.markdown('<div class="sub-header">📈 Key Performance Indicators</div>', 
                unsafe_allow_html=True)
    create_kpi_metrics(analytics)
    
    # Bottleneck alerts
    display_bottlenecks(analytics)
    
    # Charts section
    st.markdown('<div class="sub-header">📊 Visual Analytics</div>', 
                unsafe_allow_html=True)
    
    # Row 1: Patient flow
    col1, col2 = st.columns(2)
    
    with col1:
        # Hourly volume heatmap
        st.plotly_chart(
            analytics.create_visualizations()['heatmap'],
            use_container_width=True
        )
    
    with col2:
        # Triage distribution
        st.plotly_chart(
            analytics.create_visualizations()['triage_dist'],
            use_container_width=True
        )
    
    # Row 2: Performance metrics
    col3, col4 = st.columns(2)
    
    with col3:
        # Wait time by department
        st.plotly_chart(
            analytics.create_visualizations()['wait_time_box'],
            use_container_width=True
        )
    
    with col4:
        # Patient outcomes
        st.plotly_chart(
            analytics.create_visualizations()['outcomes'],
            use_container_width=True
        )
    
    # Row 3: Trends and patterns
    st.markdown('<div class="sub-header">📅 Trends & Patterns</div>', 
                unsafe_allow_html=True)
    
    col5, col6 = st.columns(2)
    
    with col5:
        # Time series of patient volume
        st.plotly_chart(
            analytics.create_visualizations()['volume_trend'],
            use_container_width=True
        )
    
    with col6:
        # Scatter plot
        st.plotly_chart(
            analytics.create_visualizations()['scatter'],
            use_container_width=True
        )
    
    # Department analysis
    st.markdown('<div class="sub-header">🏥 Department Analysis</div>', 
                unsafe_allow_html=True)
    
    dept_metrics = analytics.get_department_metrics()
    st.dataframe(
        dept_metrics.style.format({
            'wait_time_minutes': '{:.1f} min',
            'treatment_time_minutes': '{:.1f} min',
            'total_time_minutes': '{:.1f} min',
            'admission_rate': '{:.1%}',
            'estimated_cost_usd': '${:,.0f}',
            'pain_level': '{:.1f}'
        }).background_gradient(subset=['wait_time_minutes'], cmap='Reds')
        .background_gradient(subset=['admission_rate'], cmap='Blues')
        .background_gradient(subset=['estimated_cost_usd'], cmap='Greens'),
        use_container_width=True
    )
    
    # Top complaints
    st.markdown('<div class="sub-header">🤒 Top Chief Complaints</div>', 
                unsafe_allow_html=True)
    
    top_complaints = analytics.get_top_complaints(15)
    fig_complaints = px.bar(
        top_complaints,
        x='complaint',
        y='count',
        title='Top 15 Chief Complaints',
        color='count',
        color_continuous_scale='Viridis'
    )
    st.plotly_chart(fig_complaints, use_container_width=True)
    
    # Patient demographics
    st.markdown('<div class="sub-header">👥 Patient Demographics</div>', 
                unsafe_allow_html=True)
    
    col7, col8, col9 = st.columns(3)
    
    with col7:
        demographics = analytics.get_patient_demographics()
        age_data = demographics['age_groups'].reset_index()
        age_data.columns = ['Age Group', 'Count']
        fig_age = px.pie(age_data, values='Count', names='Age Group', 
                         title='Age Distribution')
        st.plotly_chart(fig_age, use_container_width=True)
    
    with col8:
        gender_data = demographics['gender_dist'].reset_index()
        gender_data.columns = ['Gender', 'Count']
        fig_gender = px.pie(gender_data, values='Count', names='Gender',
                           title='Gender Distribution')
        st.plotly_chart(fig_gender, use_container_width=True)
    
    with col9:
        insurance_data = demographics['insurance_dist'].reset_index()
        insurance_data.columns = ['Insurance', 'Count']
        fig_insurance = px.bar(insurance_data, x='Insurance', y='Count',
                              title='Insurance Distribution', color='Insurance')
        st.plotly_chart(fig_insurance, use_container_width=True)
    
    # Raw data view
    st.markdown('<div class="sub-header">📋 Raw Data Preview</div>', 
                unsafe_allow_html=True)
    
    show_columns = st.multiselect(
        "Select columns to display:",
        options=filtered_df.columns.tolist(),
        default=['arrival_time', 'triage_level', 'department', 'chief_complaint', 
                'wait_time_minutes', 'outcome', 'doctor_assigned']
    )
    
    if show_columns:
        st.dataframe(
            filtered_df[show_columns].head(100),
            use_container_width=True,
            height=400
        )

def filter_data(df, date_range, departments, triage_levels):
    """Apply filters to the dataframe"""
    filtered = df.copy()
    
    # Date filter
    if len(date_range) == 2:
        start_date, end_date = date_range
        filtered = filtered[
            (filtered['arrival_time'].dt.date >= start_date) & 
            (filtered['arrival_time'].dt.date <= end_date)
        ]
    
    # Department filter
    if departments:
        filtered = filtered[filtered['department'].isin(departments)]
    
    # Triage filter
    if triage_levels:
        filtered = filtered[filtered['triage_level'].isin(triage_levels)]
    
    return filtered

def main():
    """Main function"""
    try:
        global df
        df = load_or_generate_data()
        create_dashboard()
        
        # Footer
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.caption(f"📅 Data range: {df['arrival_time'].min().date()} to {df['arrival_time'].max().date()}")
        
        with col2:
            st.caption(f"📊 Total records: {len(df):,}")
        
        with col3:
            st.caption(f"🕐 Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.info("Try refreshing the page or regenerating the data.")

if __name__ == "__main__":
    main()