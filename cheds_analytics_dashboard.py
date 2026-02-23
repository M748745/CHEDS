"""
CHEDS Analytics Dashboard

A comprehensive analytics dashboard for visualizing 41 CHEDS Business Data Products
across 7 domains in UAE Higher Education.

Features:
- Interactive data visualization
- Multi-domain analytics
- Real-time filtering
- Export capabilities

Usage:
1. Run: streamlit run cheds_analytics_dashboard.py
2. Click "Auto-Load All CSV Files" or upload files manually
3. Explore different domain tabs
4. Use filters to analyze data

Created: 2026-02-23
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from pathlib import Path
from datetime import datetime
import os

# Page configuration
st.set_page_config(
    page_title="CHEDS Analytics Dashboard",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - Same theme as reference application
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    :root {
        --primary: #6366f1;
        --secondary: #10b981;
        --warning: #f59e0b;
        --danger: #ef4444;
        --info: #3b82f6;
    }

    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
    }

    h1 {
        background: linear-gradient(135deg, #818cf8, #34d399);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.2rem !important;
        font-family: 'Inter', sans-serif;
        font-weight: 700;
    }

    h2 {
        color: #818cf8 !important;
        font-size: 1.5rem !important;
        font-family: 'Inter', sans-serif;
        font-weight: 600;
    }

    h3 {
        color: #a5b4fc !important;
        font-size: 1.2rem !important;
        font-family: 'Inter', sans-serif;
        font-weight: 600;
    }

    [data-testid="stMetricValue"] {
        background: linear-gradient(135deg, #818cf8, #34d399);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2rem;
        font-weight: 700;
        letter-spacing: -0.02em;
    }

    [data-testid="stMetricLabel"] {
        color: #cbd5e1 !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.02em;
    }

    /* Make body text clearer */
    p, div, span {
        color: #e2e8f0 !important;
        font-size: 1.05rem;
        line-height: 1.7;
    }

    /* Make table text clearer */
    [data-testid="stDataFrame"] {
        font-size: 1.05rem !important;
    }

    /* Make markdown text clearer */
    .stMarkdown {
        font-size: 1.05rem !important;
        line-height: 1.7 !important;
    }

    .stSidebar label {
        color: white !important;
        font-weight: 500 !important;
        font-size: 0.95rem !important;
    }

    .stSelectbox select,
    .stMultiSelect div[data-baseweb="select"] div,
    div[data-baseweb="select"] input,
    div[data-baseweb="select"] > div {
        color: #e2e8f0 !important;
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%) !important;
        border: 1px solid #334155 !important;
    }

    .stTextInput input {
        color: #e2e8f0 !important;
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%) !important;
        border: 1px solid #334155 !important;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(30, 41, 59, 0.5);
        padding: 10px;
        border-radius: 10px;
    }

    .stTabs [data-baseweb="tab"] {
        background: rgba(99, 102, 241, 0.1);
        border-radius: 8px;
        color: #a5b4fc;
        font-weight: 600;
        padding: 12px 20px;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        color: white;
    }

    div[data-testid="stExpander"] {
        background: rgba(30, 41, 59, 0.5);
        border: 1px solid #334155;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
if 'datasets' not in st.session_state:
    st.session_state.datasets = {}
if 'auto_load_attempted' not in st.session_state:
    st.session_state.auto_load_attempted = False

# Auto-load CSV files immediately on startup
if not st.session_state.auto_load_attempted:
    st.session_state.auto_load_attempted = True
    csv_dir = Path("csv_files")
    # Try multiple path locations
    if not csv_dir.exists():
        csv_dir = Path(__file__).parent / "csv_files"
    if not csv_dir.exists():
        csv_dir = Path(os.getcwd()) / "csv_files"
    if not csv_dir.exists():
        csv_dir = Path("D:/exalio_work/RFP/Ankbut/MVP/CHEDS/csv_files")

    if csv_dir.exists():
        csv_files = list(csv_dir.glob("*.csv"))
        if csv_files and not st.session_state.data_loaded:
            datasets = {}
            for file_path in csv_files:
                try:
                    df = pd.read_csv(file_path, encoding='utf-8-sig')
                    product_id = file_path.stem.split('_')[0]
                    datasets[product_id] = {
                        'data': df,
                        'filename': file_path.name,
                        'rows': len(df),
                        'columns': len(df.columns)
                    }
                except Exception as e:
                    pass
            if datasets:
                st.session_state.datasets = datasets
                st.session_state.data_loaded = True

# Product categorization
PRODUCT_CATEGORIES = {
    'Learning and Teaching': [
        'CHEDS-LT-01', 'CHEDS-LT-02', 'CHEDS-LT-03', 'CHEDS-LT-04', 'CHEDS-LT-05',
        'CHEDS-LT-06', 'CHEDS-LT-07', 'CHEDS-LT-08', 'CHEDS-LT-09', 'CHEDS-LT-10',
        'CHEDS-LT-11', 'CHEDS-LT-12', 'CHEDS-LT-13', 'CHEDS-LT-14', 'CHEDS-LT-15',
        'CHEDS-LT-16', 'CHEDS-LT-17', 'CHEDS-LT-18', 'CHEDS-LT-19', 'CHEDS-LT-20'
    ],
    'Human Resource Management': [
        'CHEDS-HR-21', 'CHEDS-HR-22', 'CHEDS-HR-23', 'CHEDS-HR-24'
    ],
    'Financial Management': [
        'CHEDS-FIN-25'
    ],
    'Research': [
        'CHEDS-RES-26', 'CHEDS-RES-27', 'CHEDS-RES-28', 'CHEDS-RES-29',
        'CHEDS-RES-30', 'CHEDS-RES-31', 'CHEDS-RES-32'
    ],
    'Facilities & Estate Management': [
        'CHEDS-FAC-33', 'CHEDS-FAC-34'
    ],
    'Supporting Services': [
        'CHEDS-SUP-35', 'CHEDS-SUP-36', 'CHEDS-SUP-40', 'CHEDS-SUP-41'
    ],
    'Advancement Management': [
        'CHEDS-ADV-37', 'CHEDS-ADV-38', 'CHEDS-ADV-39'
    ]
}

def auto_load_csv_files(show_progress=True):
    """Automatically load all CSV files from csv_files directory"""
    csv_dir = Path("csv_files")
    # Try multiple path locations
    if not csv_dir.exists():
        csv_dir = Path(__file__).parent / "csv_files"
    if not csv_dir.exists():
        csv_dir = Path(os.getcwd()) / "csv_files"
    if not csv_dir.exists():
        csv_dir = Path("D:/exalio_work/RFP/Ankbut/MVP/CHEDS/csv_files")

    if csv_dir.exists():
        csv_files = list(csv_dir.glob("*.csv"))
        if csv_files:
            datasets = {}

            if show_progress:
                progress_bar = st.progress(0)
                status_text = st.empty()

            for idx, file_path in enumerate(csv_files):
                if show_progress:
                    status_text.text(f"Loading {file_path.name}...")
                df = pd.read_csv(file_path, encoding='utf-8-sig')
                product_id = file_path.stem.split('_')[0]
                datasets[product_id] = {
                    'data': df,
                    'filename': file_path.name,
                    'rows': len(df),
                    'columns': len(df.columns)
                }
                if show_progress:
                    progress_bar.progress((idx + 1) / len(csv_files))

            if show_progress:
                progress_bar.empty()
                status_text.empty()

            st.session_state.datasets = datasets
            st.session_state.data_loaded = True
            return True
    return False

def create_chart(df, chart_type, x_col, y_col, title, color_col=None):
    """Create a plotly chart with consistent styling"""
    if chart_type == 'bar':
        fig = px.bar(df, x=x_col, y=y_col, title=title, color=color_col or y_col,
                     color_continuous_scale='Blues')
    elif chart_type == 'pie':
        fig = px.pie(df, values=y_col, names=x_col, title=title)
    elif chart_type == 'line':
        fig = px.line(df, x=x_col, y=y_col, title=title)
    elif chart_type == 'scatter':
        fig = px.scatter(df, x=x_col, y=y_col, title=title, color=color_col)
    elif chart_type == 'histogram':
        fig = px.histogram(df, x=x_col, title=title, nbins=30)
    else:
        fig = px.bar(df, x=x_col, y=y_col, title=title)

    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e2e8f0'),
        xaxis=dict(tickangle=-45)
    )
    return fig

def display_overview():
    """Display enhanced overview dashboard"""
    st.title("🎓 CHEDS Analytics Dashboard")

    if not st.session_state.data_loaded:
        st.info("📊 No data loaded. Please load CSV files from the sidebar.")
        return

    # Enhanced Summary metrics with delta indicators
    col1, col2, col3, col4, col5 = st.columns(5)

    total_products = len(st.session_state.datasets)
    total_rows = sum(ds['rows'] for ds in st.session_state.datasets.values())
    total_columns = sum(ds['columns'] for ds in st.session_state.datasets.values())
    avg_records_per_product = total_rows // total_products if total_products > 0 else 0

    with col1:
        st.metric("Total Products", total_products, delta=f"{(total_products/41)*100:.0f}% of 41")
    with col2:
        st.metric("Total Records", f"{total_rows:,}")
    with col3:
        st.metric("Avg Records/Product", f"{avg_records_per_product:,}")
    with col4:
        st.metric("Total Columns", f"{total_columns:,}")
    with col5:
        st.metric("Active Domains", f"{len(PRODUCT_CATEGORIES)}/7")

    st.markdown("---")

    # Domain overview with enhanced visualizations
    st.subheader("📊 Domain Analytics")

    domain_data = []
    for domain, products in PRODUCT_CATEGORIES.items():
        loaded_products = [p for p in products if p in st.session_state.datasets]
        total_records = sum(st.session_state.datasets[p]['rows'] for p in loaded_products if p in st.session_state.datasets)
        avg_cols = sum(st.session_state.datasets[p]['columns'] for p in loaded_products) / len(loaded_products) if loaded_products else 0
        domain_data.append({
            'Domain': domain,
            'Products': len(loaded_products),
            'Total Products': len(products),
            'Records': total_records,
            'Avg Columns': avg_cols,
            'Coverage %': (len(loaded_products) / len(products) * 100) if products else 0
        })

    domain_df = pd.DataFrame(domain_data)

    # Row 1: Products and Records
    col1, col2 = st.columns(2)

    with col1:
        fig = px.bar(domain_df, x='Domain', y='Products', title='📦 Products per Domain',
                     color='Products', color_continuous_scale='Viridis',
                     text='Products')
        fig.update_traces(textposition='outside')
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e2e8f0'),
            xaxis=dict(tickangle=-45),
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.pie(domain_df, values='Records', names='Domain',
                     title='📊 Records Distribution by Domain',
                     hole=0.4)
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e2e8f0'),
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)

    # Row 2: Coverage and Comparison
    col1, col2 = st.columns(2)

    with col1:
        fig = go.Figure()
        fig.add_trace(go.Bar(
            name='Loaded',
            x=domain_df['Domain'],
            y=domain_df['Products'],
            marker_color='#6366f1'
        ))
        fig.add_trace(go.Bar(
            name='Total Available',
            x=domain_df['Domain'],
            y=domain_df['Total Products'],
            marker_color='#94a3b8'
        ))
        fig.update_layout(
            title='📈 Data Coverage by Domain',
            barmode='group',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e2e8f0'),
            xaxis=dict(tickangle=-45),
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.bar(domain_df, x='Domain', y='Coverage %', title='✅ Coverage Percentage',
                     color='Coverage %', color_continuous_scale='RdYlGn',
                     range_color=[0, 100], text='Coverage %')
        fig.update_traces(texttemplate='%{text:.0f}%', textposition='outside')
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e2e8f0'),
            xaxis=dict(tickangle=-45),
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Detailed domain statistics table
    st.subheader("📋 Domain Statistics")
    display_df = domain_df[['Domain', 'Products', 'Total Products', 'Records', 'Coverage %']].copy()
    display_df['Coverage %'] = display_df['Coverage %'].apply(lambda x: f"{x:.1f}%")
    display_df['Records'] = display_df['Records'].apply(lambda x: f"{x:,}")
    st.dataframe(display_df, use_container_width=True, height=300)

    st.markdown("---")

    # Loaded products with enhanced display
    st.subheader("📋 Loaded Data Products")

    for domain, products in PRODUCT_CATEGORIES.items():
        loaded = [p for p in products if p in st.session_state.datasets]
        if loaded:
            with st.expander(f"**{domain}** - {len(loaded)}/{len(products)} products loaded ({len(loaded)/len(products)*100:.0f}%)"):
                for product_id in loaded:
                    ds = st.session_state.datasets[product_id]
                    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                    with col1:
                        st.write(f"**{product_id}** - {ds['filename']}")
                    with col2:
                        st.write(f"📊 {ds['rows']:,} rows")
                    with col3:
                        st.write(f"📈 {ds['columns']} cols")
                    with col4:
                        st.write(f"💾 {(ds['rows'] * ds['columns']):,} cells")

def display_learning_teaching():
    """Display enriched Learning and Teaching analytics"""
    st.title("📚 Learning and Teaching Analytics")
    st.markdown("**Comprehensive analysis of student lifecycle: applications, enrollment, progression, and graduation**")

    available = {k: v for k, v in st.session_state.datasets.items() if k in PRODUCT_CATEGORIES['Learning and Teaching']}
    if not available:
        st.warning("⚠️ No Learning & Teaching data available. Please load CSV files from the sidebar.")
        return

    # Enhanced Key metrics
    st.subheader("📊 Key Performance Indicators")
    cols = st.columns(5)

    total_applicants = 0
    total_enrolled = 0
    total_graduates = 0
    total_courses = 0
    total_programs = 0

    if 'CHEDS-LT-01' in available:
        df = available['CHEDS-LT-01']['data']
        total_applicants = df['App_Applicants'].sum() if 'App_Applicants' in df.columns else len(df)
        with cols[0]:
            st.metric("📝 Total Applicants", f"{int(total_applicants):,}")

    if 'CHEDS-LT-03' in available:
        df = available['CHEDS-LT-03']['data']
        total_enrolled = len(df)
        with cols[1]:
            st.metric("👨‍🎓 Enrolled Students", f"{total_enrolled:,}")

    if 'CHEDS-LT-09' in available:
        df = available['CHEDS-LT-09']['data']
        total_graduates = len(df)
        with cols[2]:
            st.metric("🎓 Graduates", f"{total_graduates:,}")

    if 'CHEDS-LT-11' in available:
        df = available['CHEDS-LT-11']['data']
        total_courses = len(df)
        with cols[3]:
            st.metric("📚 Total Courses", f"{total_courses:,}")

    if 'CHEDS-LT-12' in available:
        df = available['CHEDS-LT-12']['data']
        total_programs = len(df)
        with cols[4]:
            st.metric("🎯 Programs", f"{total_programs:,}")

    # Conversion metrics
    if total_applicants > 0 and total_enrolled > 0:
        st.markdown("---")
        st.subheader("📈 Conversion Metrics")
        conv_cols = st.columns(3)
        with conv_cols[0]:
            acceptance_rate = (total_enrolled / total_applicants) * 100 if total_applicants > 0 else 0
            st.metric("Acceptance Rate", f"{acceptance_rate:.1f}%", delta="Enrolled/Applied")
        with conv_cols[1]:
            graduation_rate = (total_graduates / total_enrolled) * 100 if total_enrolled > 0 else 0
            st.metric("Graduation Rate", f"{graduation_rate:.1f}%", delta="Graduated/Enrolled")
        with conv_cols[2]:
            students_per_course = total_enrolled / total_courses if total_courses > 0 else 0
            st.metric("Students per Course", f"{students_per_course:.1f}", delta="Average")

    st.markdown("---")

    # Applicants Analysis
    if 'CHEDS-LT-01' in available:
        st.subheader("📝 Applicants Analysis")
        df = available['CHEDS-LT-01']['data']

        col1, col2 = st.columns(2)

        with col1:
            if 'App_Institution_Name' in df.columns and 'App_Applicants' in df.columns:
                inst_data = df.groupby('App_Institution_Name')['App_Applicants'].sum().reset_index()
                inst_data = inst_data.sort_values('App_Applicants', ascending=False).head(10)
                fig = px.bar(inst_data, x='App_Applicants', y='App_Institution_Name',
                            title='🏛️ Top 10 Institutions by Applications',
                            orientation='h', color='App_Applicants',
                            color_continuous_scale='Blues', text='App_Applicants')
                fig.update_traces(texttemplate='%{text:,}', textposition='outside')
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    height=400,
                    yaxis={'categoryorder': 'total ascending'}
                )
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            if 'App_Degrees' in df.columns and 'App_Applicants' in df.columns:
                degree_data = df.groupby('App_Degrees')['App_Applicants'].sum().reset_index()
                fig = px.pie(degree_data, values='App_Applicants', names='App_Degrees',
                            title='🎓 Applications by Degree Level',
                            hole=0.4, color_discrete_sequence=px.colors.sequential.Viridis)
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)

        # Additional applicant insights
        col1, col2 = st.columns(2)
        with col1:
            if 'App_Gender' in df.columns:
                gender_data = df.groupby('App_Gender')['App_Applicants'].sum().reset_index()
                fig = px.pie(gender_data, values='App_Applicants', names='App_Gender',
                            title='👥 Applicants by Gender',
                            color_discrete_map={'M': '#6366f1', 'F': '#ec4899'})
                fig.update_traces(textposition='inside', textinfo='percent+value')
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    height=350
                )
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            if 'App_Nationality' in df.columns:
                nat_data = df.groupby('App_Nationality')['App_Applicants'].sum().reset_index()
                nat_data = nat_data.sort_values('App_Applicants', ascending=False).head(10)
                fig = px.bar(nat_data, x='App_Nationality', y='App_Applicants',
                            title='🌍 Top 10 Nationalities (Applicants)',
                            color='App_Applicants', color_continuous_scale='Teal')
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    xaxis=dict(tickangle=-45),
                    height=350
                )
                st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Student Enrollment Analysis
    if 'CHEDS-LT-03' in available:
        st.subheader("👨‍🎓 Student Enrollment Analysis")
        df = available['CHEDS-LT-03']['data']

        col1, col2 = st.columns(2)

        with col1:
            # Use correct column names: Enroll_Gender
            gender_col = 'Enroll_Gender' if 'Enroll_Gender' in df.columns else 'Stu_Gender'
            if gender_col in df.columns:
                gender_counts = df[gender_col].value_counts()
                fig = px.pie(values=gender_counts.values, names=gender_counts.index,
                            title='👥 Gender Distribution (Enrolled Students)',
                            hole=0.5, color_discrete_map={'M': '#6366f1', 'F': '#ec4899'})
                fig.update_traces(textposition='inside', textinfo='percent+label+value',
                                texttemplate='%{label}<br>%{value:,}<br>(%{percent})')
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Use correct column names: Enroll_Nationality
            nat_col = 'Enroll_Nationality' if 'Enroll_Nationality' in df.columns else 'Stu_Nationality'
            if nat_col in df.columns:
                nat_counts = df[nat_col].value_counts().head(10)
                fig = px.bar(x=nat_counts.values, y=nat_counts.index,
                            title='🌍 Top 10 Nationalities (Enrolled)',
                            orientation='h', color=nat_counts.values,
                            color_continuous_scale='Viridis', labels={'x': 'Students', 'y': 'Nationality'})
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    height=400,
                    yaxis={'categoryorder': 'total ascending'}
                )
                st.plotly_chart(fig, use_container_width=True)

        # Additional enrollment metrics
        col1, col2 = st.columns(2)
        with col1:
            # Use correct column names: Enroll_Institution_Name
            inst_col = 'Enroll_Institution_Name' if 'Enroll_Institution_Name' in df.columns else 'Stu_Institution_Name'
            if inst_col in df.columns:
                inst_counts = df[inst_col].value_counts().head(10)
                fig = px.bar(x=inst_counts.index, y=inst_counts.values,
                            title='🏛️ Enrollment by Institution (Top 10)',
                            color=inst_counts.values, color_continuous_scale='Blues',
                            labels={'x': 'Institution', 'y': 'Enrolled Students'})
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    xaxis=dict(tickangle=-45),
                    height=350
                )
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Use correct column names: Enroll_Student_Degree
            degree_col = 'Enroll_Student_Degree' if 'Enroll_Student_Degree' in df.columns else 'Stu_Degree'
            if degree_col in df.columns:
                degree_counts = df[degree_col].value_counts()
                fig = px.pie(values=degree_counts.values, names=degree_counts.index,
                            title='🎓 Enrollment by Degree Level',
                            color_discrete_sequence=px.colors.sequential.Plasma)
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    height=350
                )
                st.plotly_chart(fig, use_container_width=True)

        # Additional enrollment visualizations
        col1, col2 = st.columns(2)
        with col1:
            # Student Type distribution
            if 'Enroll_Student_Type' in df.columns:
                type_counts = df['Enroll_Student_Type'].value_counts()
                fig = px.bar(x=type_counts.index, y=type_counts.values,
                            title='📋 Student Type Distribution',
                            color=type_counts.values, color_continuous_scale='Teal')
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    xaxis=dict(tickangle=-45),
                    height=350
                )
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Study mode distribution
            if 'Enroll_Mode_of_Study' in df.columns:
                mode_counts = df['Enroll_Mode_of_Study'].value_counts()
                fig = px.pie(values=mode_counts.values, names=mode_counts.index,
                            title='🎯 Mode of Study',
                            color_discrete_sequence=px.colors.sequential.Greens)
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    height=350
                )
                st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Graduates Analysis
    if 'CHEDS-LT-09' in available:
        st.subheader("🎓 Graduate Outcomes")
        df = available['CHEDS-LT-09']['data']

        col1, col2 = st.columns(2)
        with col1:
            # Use correct column names: Grad_Institution_Name
            inst_col = 'Grad_Institution_Name' if 'Grad_Institution_Name' in df.columns else 'Gra_Institution_Name'
            if inst_col in df.columns:
                inst_grad = df[inst_col].value_counts().head(10)
                fig = px.bar(x=inst_grad.values, y=inst_grad.index,
                            title='🏆 Graduates by Institution (Top 10)',
                            orientation='h', color=inst_grad.values,
                            color_continuous_scale='Greens')
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    height=400,
                    yaxis={'categoryorder': 'total ascending'}
                )
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Use correct column names: Grad_Student_Degree
            degree_col = 'Grad_Student_Degree' if 'Grad_Student_Degree' in df.columns else 'Gra_Degree'
            if degree_col in df.columns:
                degree_grad = df[degree_col].value_counts()
                fig = px.pie(values=degree_grad.values, names=degree_grad.index,
                            title='📜 Graduates by Degree Level',
                            hole=0.4, color_discrete_sequence=px.colors.sequential.Greens)
                fig.update_traces(textposition='inside', textinfo='percent+label+value')
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)

        # Additional graduate visualizations
        col1, col2 = st.columns(2)
        with col1:
            # Graduates by gender
            if 'Grad_Gender' in df.columns:
                gender_grad = df['Grad_Gender'].value_counts()
                fig = px.pie(values=gender_grad.values, names=gender_grad.index,
                            title='👥 Graduates by Gender',
                            color_discrete_map={'M': '#6366f1', 'F': '#ec4899'})
                fig.update_traces(textposition='inside', textinfo='percent+label+value')
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Graduates by nationality
            if 'Grad_Nationality' in df.columns:
                nat_grad = df['Grad_Nationality'].value_counts().head(10)
                fig = px.bar(x=nat_grad.index, y=nat_grad.values,
                            title='🌍 Top 10 Nationalities (Graduates)',
                            color=nat_grad.values, color_continuous_scale='Teal')
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    xaxis=dict(tickangle=-45),
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)

        # GPA Analysis
        col1, col2 = st.columns(2)
        with col1:
            if 'Grad_GPA_Cumulative' in df.columns:
                # GPA distribution
                fig = px.histogram(df, x='Grad_GPA_Cumulative', nbins=20,
                                  title='📊 GPA Distribution',
                                  color_discrete_sequence=['#10b981'])
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    xaxis_title='Cumulative GPA',
                    yaxis_title='Number of Graduates',
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            if 'Grad_GPA_Cumulative' in df.columns:
                # GPA box plot
                fig = px.box(df, y='Grad_GPA_Cumulative',
                            title='📦 GPA Statistics',
                            color_discrete_sequence=['#6366f1'])
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    yaxis_title='Cumulative GPA',
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)

def display_human_resources():
    """Display enriched HR analytics"""
    st.title("👥 Human Resource Management Analytics")
    st.markdown("**Comprehensive workforce analytics: demographics, compensation, performance, and development**")

    available = {k: v for k, v in st.session_state.datasets.items() if k in PRODUCT_CATEGORIES['Human Resource Management']}
    if not available:
        st.warning("⚠️ No HR data available. Please load CSV files from the sidebar.")
        return

    # Enhanced Employee Overview
    if 'CHEDS-HR-21' in available:
        st.subheader("📊 Workforce Overview")
        df = available['CHEDS-HR-21']['data']

        cols = st.columns(5)
        total_employees = len(df)
        male_count = (df['Emp_Gender'] == 'M').sum() if 'Emp_Gender' in df.columns else 0
        female_count = (df['Emp_Gender'] == 'F').sum() if 'Emp_Gender' in df.columns else 0
        uae_nationals = (df['Emp_Nationality'] == 'AE').sum() if 'Emp_Nationality' in df.columns else 0

        with cols[0]:
            st.metric("👥 Total Employees", f"{total_employees:,}")
        with cols[1]:
            st.metric("👨 Male", f"{male_count:,}", delta=f"{(male_count/total_employees*100):.1f}%")
        with cols[2]:
            st.metric("👩 Female", f"{female_count:,}", delta=f"{(female_count/total_employees*100):.1f}%")
        with cols[3]:
            st.metric("🇦🇪 UAE Nationals", f"{uae_nationals:,}", delta=f"{(uae_nationals/total_employees*100):.1f}%")
        with cols[4]:
            expats = total_employees - uae_nationals
            st.metric("🌍 Expatriates", f"{expats:,}", delta=f"{(expats/total_employees*100):.1f}%")

        st.markdown("---")

        # Visualizations Row 1
        col1, col2 = st.columns(2)

        with col1:
            if 'Emp_Gender' in df.columns:
                gender_counts = df['Emp_Gender'].value_counts()
                fig = px.pie(values=gender_counts.values, names=gender_counts.index,
                            title='👥 Gender Distribution',
                            hole=0.5, color_discrete_map={'M': '#6366f1', 'F': '#ec4899'})
                fig.update_traces(textposition='inside', textinfo='percent+label+value',
                                texttemplate='%{label}<br>%{value:,}<br>(%{percent})')
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            if 'Emp_Nationality' in df.columns:
                nat_counts = df['Emp_Nationality'].value_counts().head(10)
                fig = px.bar(x=nat_counts.values, y=nat_counts.index,
                            title='🌍 Top 10 Nationalities',
                            orientation='h', color=nat_counts.values,
                            color_continuous_scale='Viridis')
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    height=400,
                    yaxis={'categoryorder': 'total ascending'}
                )
                st.plotly_chart(fig, use_container_width=True)

        # Visualizations Row 2
        col1, col2 = st.columns(2)

        with col1:
            if 'Emp_Institution_Name' in df.columns:
                inst_counts = df['Emp_Institution_Name'].value_counts().head(10)
                fig = px.bar(x=inst_counts.index, y=inst_counts.values,
                            title='🏛️ Employees by Institution (Top 10)',
                            color=inst_counts.values, color_continuous_scale='Blues')
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    xaxis=dict(tickangle=-45),
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            if 'Emp_Position' in df.columns:
                pos_counts = df['Emp_Position'].value_counts().head(10)
                fig = px.pie(values=pos_counts.values, names=pos_counts.index,
                            title='💼 Top 10 Positions',
                            color_discrete_sequence=px.colors.sequential.Plasma)
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)

    # Program Learning Outcomes Analysis (HR-23)
    if 'CHEDS-HR-23' in available:
        st.markdown("---")
        st.subheader("📋 Program Learning Outcomes")
        df = available['CHEDS-HR-23']['data']

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📚 Total Programs", f"{df['PLO_Program_code'].nunique():,}")
        with col2:
            st.metric("🎯 Total PLOs", f"{len(df):,}")
        with col3:
            st.metric("🏛️ Institutions", f"{df['PLO_Institution_Name'].nunique():,}")

        col1, col2 = st.columns(2)
        with col1:
            # PLOs by institution
            inst_plo = df['PLO_Institution_Name'].value_counts().head(10)
            fig = px.bar(x=inst_plo.values, y=inst_plo.index,
                        title='🏛️ PLOs by Institution (Top 10)',
                        orientation='h', color=inst_plo.values,
                        color_continuous_scale='Teal')
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e2e8f0'),
                height=400,
                yaxis={'categoryorder': 'total ascending'}
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Programs by institution
            prog_inst = df.groupby('PLO_Institution_Name')['PLO_Program_code'].nunique().sort_values(ascending=False).head(10)
            fig = px.bar(x=prog_inst.index, y=prog_inst.values,
                        title='📚 Programs by Institution (Top 10)',
                        color=prog_inst.values, color_continuous_scale='Blues')
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e2e8f0'),
                xaxis=dict(tickangle=-45),
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)

    # Employee Workload Analysis (HR-22)
    if 'CHEDS-HR-22' in available:
        st.markdown("---")
        st.subheader("📊 Employee Workload Analysis")
        df = available['CHEDS-HR-22']['data']

        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("👥 Total Records", f"{len(df):,}")
        with col2:
            if 'Load_Teaching_Workload' in df.columns:
                avg_teaching = pd.to_numeric(df['Load_Teaching_Workload'], errors='coerce').mean()
                st.metric("📚 Avg Teaching Load", f"{avg_teaching:.1f}")
        with col3:
            if 'Load_Research_Workload' in df.columns:
                avg_research = pd.to_numeric(df['Load_Research_Workload'], errors='coerce').mean()
                st.metric("🔬 Avg Research Load", f"{avg_research:.1f}")
        with col4:
            if 'Load_Maximum_Workload' in df.columns:
                avg_max = pd.to_numeric(df['Load_Maximum_Workload'], errors='coerce').mean()
                st.metric("📊 Avg Max Workload", f"{avg_max:.1f}")

        col1, col2 = st.columns(2)
        with col1:
            # Workload by institution
            if 'Load_Institution_name' in df.columns:
                inst_wload = df['Load_Institution_name'].value_counts().head(10)
                fig = px.bar(x=inst_wload.values, y=inst_wload.index,
                            title='🏛️ Workload Records by Institution (Top 10)',
                            orientation='h', color=inst_wload.values,
                            color_continuous_scale='Greens')
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    height=400,
                    yaxis={'categoryorder': 'total ascending'}
                )
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Workload by period
            if 'Load_Academic_Period' in df.columns:
                period_wload = df['Load_Academic_Period'].value_counts()
                fig = px.pie(values=period_wload.values, names=period_wload.index,
                            title='📅 Workload by Academic Period',
                            color_discrete_sequence=px.colors.sequential.Plasma)
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)

        # Additional workload visualizations
        col1, col2 = st.columns(2)
        with col1:
            # Employee category distribution
            if 'Load_Employee_Category' in df.columns:
                cat_dist = df['Load_Employee_Category'].value_counts()
                fig = px.bar(x=cat_dist.index, y=cat_dist.values,
                            title='👔 Employee Category Distribution',
                            color=cat_dist.values, color_continuous_scale='Blues')
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    xaxis=dict(tickangle=-45),
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Full-time vs Part-time
            if 'Load_Full_Part_Time' in df.columns:
                ft_pt = df['Load_Full_Part_Time'].value_counts()
                fig = px.pie(values=ft_pt.values, names=ft_pt.index,
                            title='⏰ Full-Time vs Part-Time',
                            color_discrete_sequence=px.colors.sequential.Teal)
                fig.update_traces(textposition='inside', textinfo='percent+label+value')
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)

        # Workload comparison
        col1, col2 = st.columns(2)
        with col1:
            # Teaching vs Research workload
            if 'Load_Teaching_Workload' in df.columns and 'Load_Research_Workload' in df.columns:
                workload_comp = pd.DataFrame({
                    'Type': ['Teaching', 'Research'],
                    'Average Workload': [
                        pd.to_numeric(df['Load_Teaching_Workload'], errors='coerce').mean(),
                        pd.to_numeric(df['Load_Research_Workload'], errors='coerce').mean()
                    ]
                })
                fig = px.bar(workload_comp, x='Type', y='Average Workload',
                            title='📊 Teaching vs Research Workload',
                            color='Average Workload', color_continuous_scale='Viridis')
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Department distribution
            if 'Load_Department_name' in df.columns:
                dept_dist = df['Load_Department_name'].value_counts().head(10)
                fig = px.bar(x=dept_dist.index, y=dept_dist.values,
                            title='🏢 Top 10 Departments by Workload Records',
                            color=dept_dist.values, color_continuous_scale='Oranges')
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    xaxis=dict(tickangle=-45),
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)


def display_financial():
    """Display enriched Financial analytics"""
    st.title("💰 Financial Management Analytics")
    st.markdown("**Complete financial oversight: budget, revenue, expenses, and capital investments**")

    available = {k: v for k, v in st.session_state.datasets.items() if k in PRODUCT_CATEGORIES['Financial Management']}
    if not available:
        st.warning("⚠️ No Financial data available. Please load CSV files from the sidebar.")
        return

    if 'CHEDS-FIN-25' in available:
        df = available['CHEDS-FIN-25']['data']

        st.subheader("📊 Financial Overview")

        # Calculate main financial metrics
        capex_cols = [c for c in df.columns if 'Finance_Capex_' in c and c != 'Finance_Capex_Indirect_Research_Percent']
        opex_cols = [c for c in df.columns if 'Finance_Opex_' in c and c != 'Finance_Opex_Indirect_Research_Percent']
        revenue_cols = [c for c in df.columns if 'Finance_Revenue_' in c]
        salary_cols = [c for c in df.columns if 'Finance_Salaries_' in c and c != 'Finance_Salaries_Indirect_Research_Percent']
        research_fund_cols = [c for c in df.columns if 'Finance_Research_Fund_' in c and c != 'Finance_Research_Fund_Total']

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            total_capex = sum(pd.to_numeric(df[col], errors='coerce').sum() for col in capex_cols)
            st.metric("🏗️ Total CAPEX", f"AED {int(total_capex):,}")

        with col2:
            total_opex = sum(pd.to_numeric(df[col], errors='coerce').sum() for col in opex_cols)
            st.metric("⚙️ Total OPEX", f"AED {int(total_opex):,}")

        with col3:
            total_revenue = pd.to_numeric(df['Finance_Total_Revenue'], errors='coerce').sum() if 'Finance_Total_Revenue' in df.columns else 0
            st.metric("💵 Total Revenue", f"AED {int(total_revenue):,}")

        with col4:
            total_expenses = pd.to_numeric(df['Finance_Total_Expenses'], errors='coerce').sum() if 'Finance_Total_Expenses' in df.columns else 0
            st.metric("💸 Total Expenses", f"AED {int(total_expenses):,}")

        st.markdown("---")

        # CAPEX Analysis
        st.subheader("🏗️ Capital Expenditure (CAPEX) Analysis")

        col1, col2 = st.columns(2)

        with col1:
            # CAPEX breakdown by category
            capex_categories = {
                'Academic': pd.to_numeric(df['Finance_Capex_Academic'], errors='coerce').sum(),
                'Administrative': pd.to_numeric(df['Finance_Capex_Administrative'], errors='coerce').sum(),
                'Infrastructure': pd.to_numeric(df['Finance_Capex_Infra'], errors='coerce').sum(),
                'Library': pd.to_numeric(df['Finance_Capex_Library'], errors='coerce').sum(),
                'Research': pd.to_numeric(df['Finance_Capex_Research'], errors='coerce').sum(),
                'Student Welfare': pd.to_numeric(df['Finance_Capex_Student'], errors='coerce').sum(),
                'Other': pd.to_numeric(df['Finance_Capex_Other'], errors='coerce').sum()
            }
            capex_df = pd.DataFrame(list(capex_categories.items()), columns=['Category', 'Amount'])
            capex_df = capex_df[capex_df['Amount'] > 0].sort_values('Amount', ascending=False)

            fig = px.pie(capex_df, values='Amount', names='Category',
                        title='🏗️ CAPEX Distribution by Category',
                        hole=0.4, color_discrete_sequence=px.colors.sequential.Blues)
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e2e8f0'),
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # CAPEX by institution
            if 'Finance_Institution_Name' in df.columns:
                df_capex = df.copy()
                for col in capex_cols:
                    df_capex[col] = pd.to_numeric(df_capex[col], errors='coerce')
                df_capex['Total_CAPEX'] = df_capex[capex_cols].sum(axis=1)
                inst_capex = df_capex.groupby('Finance_Institution_Name')['Total_CAPEX'].sum().sort_values(ascending=False).head(10)

                fig = px.bar(x=inst_capex.values, y=inst_capex.index,
                            title='🏛️ CAPEX by Institution (Top 10)',
                            orientation='h', color=inst_capex.values,
                            color_continuous_scale='Greens')
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    xaxis_title='CAPEX (AED)',
                    yaxis={'categoryorder': 'total ascending'},
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)

        # OPEX Analysis
        st.markdown("---")
        st.subheader("⚙️ Operational Expenditure (OPEX) Analysis")

        col1, col2 = st.columns(2)

        with col1:
            # OPEX breakdown by category
            opex_categories = {
                'Academic': pd.to_numeric(df['Finance_Opex_Academic'], errors='coerce').sum(),
                'Administrative': pd.to_numeric(df['Finance_Opex_Administrative'], errors='coerce').sum(),
                'Infrastructure': pd.to_numeric(df['Finance_Opex_Infra'], errors='coerce').sum(),
                'Library': pd.to_numeric(df['Finance_Opex_Library'], errors='coerce').sum(),
                'Research': pd.to_numeric(df['Finance_Opex_Research'], errors='coerce').sum(),
                'IP': pd.to_numeric(df['Finance_Opex_Intellect_Property'], errors='coerce').sum(),
                'Student Welfare': pd.to_numeric(df['Finance_Opex_Student'], errors='coerce').sum(),
                'Other': pd.to_numeric(df['Finance_Opex_Other'], errors='coerce').sum()
            }
            opex_df = pd.DataFrame(list(opex_categories.items()), columns=['Category', 'Amount'])
            opex_df = opex_df[opex_df['Amount'] > 0].sort_values('Amount', ascending=True)

            fig = px.bar(opex_df, x='Amount', y='Category',
                        title='⚙️ OPEX Distribution by Category',
                        orientation='h', color='Amount',
                        color_continuous_scale='Oranges')
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e2e8f0'),
                xaxis_title='OPEX (AED)',
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # OPEX by institution
            if 'Finance_Institution_Name' in df.columns:
                df_opex = df.copy()
                for col in opex_cols:
                    df_opex[col] = pd.to_numeric(df_opex[col], errors='coerce')
                df_opex['Total_OPEX'] = df_opex[opex_cols].sum(axis=1)
                inst_opex = df_opex.groupby('Finance_Institution_Name')['Total_OPEX'].sum().sort_values(ascending=False).head(10)

                fig = px.bar(x=inst_opex.index, y=inst_opex.values,
                            title='🏛️ OPEX by Institution (Top 10)',
                            color=inst_opex.values, color_continuous_scale='Reds')
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    xaxis=dict(tickangle=-45),
                    yaxis_title='OPEX (AED)',
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)

        # Revenue Analysis
        st.markdown("---")
        st.subheader("💵 Revenue Analysis")

        col1, col2 = st.columns(2)

        with col1:
            # Revenue breakdown by source
            revenue_sources = {
                'UG Credit Tuition': pd.to_numeric(df['Finance_Revenue_TuitionFees_UG_Credit_Course'], errors='coerce').sum(),
                'UG Non-Credit Tuition': pd.to_numeric(df['Finance_Revenue_TuitionFees_UG_Noncredit_Course'], errors='coerce').sum(),
                'Graduate Tuition': pd.to_numeric(df['Finance_Revenue_TuitionFees_Graduate_Program'], errors='coerce').sum(),
                'Private Donations': pd.to_numeric(df['Finance_Revenue_Private_Donation'], errors='coerce').sum(),
                'Local Gov': pd.to_numeric(df['Finance_Revenue_Local_Gov'], errors='coerce').sum(),
                'Federal Gov': pd.to_numeric(df['Finance_Revenue_Federal_Gov'], errors='coerce').sum(),
                'Research Grants': pd.to_numeric(df['Finance_Revenue_External_Research_Grants'], errors='coerce').sum(),
                'Consulting': pd.to_numeric(df['Finance_Revenue_Consult_Service'], errors='coerce').sum(),
                'Other Internal': pd.to_numeric(df['Finance_Revenue_Internal_Other'], errors='coerce').sum(),
                'Other External': pd.to_numeric(df['Finance_Revenue_External_Other'], errors='coerce').sum()
            }
            revenue_df = pd.DataFrame(list(revenue_sources.items()), columns=['Source', 'Amount'])
            revenue_df = revenue_df[revenue_df['Amount'] > 0].sort_values('Amount', ascending=False)

            fig = px.bar(revenue_df, x='Source', y='Amount',
                        title='💰 Revenue by Source',
                        color='Amount', color_continuous_scale='Greens')
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e2e8f0'),
                xaxis=dict(tickangle=-45),
                yaxis_title='Revenue (AED)',
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Revenue by institution
            if 'Finance_Institution_Name' in df.columns and 'Finance_Total_Revenue' in df.columns:
                inst_revenue = df.groupby('Finance_Institution_Name')['Finance_Total_Revenue'].apply(
                    lambda x: pd.to_numeric(x, errors='coerce').sum()
                ).sort_values(ascending=False).head(10)

                fig = px.bar(x=inst_revenue.values, y=inst_revenue.index,
                            title='🏛️ Revenue by Institution (Top 10)',
                            orientation='h', color=inst_revenue.values,
                            color_continuous_scale='Teal')
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    xaxis_title='Revenue (AED)',
                    yaxis={'categoryorder': 'total ascending'},
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)

        # Salary Analysis
        st.markdown("---")
        st.subheader("👥 Salary & Compensation Analysis")

        col1, col2 = st.columns(2)

        with col1:
            # Salary breakdown by category
            salary_categories = {
                'Academic': pd.to_numeric(df['Finance_Salaries_Academic'], errors='coerce').sum(),
                'Administrative': pd.to_numeric(df['Finance_Salaries_Administrative'], errors='coerce').sum(),
                'Faculty FT': pd.to_numeric(df['Finance_Salaries_Faculty_FT'], errors='coerce').sum(),
                'Faculty PT': pd.to_numeric(df['Finance_Salaries_Faculty_PT_FT'], errors='coerce').sum(),
                'Faculty Research': pd.to_numeric(df['Finance_Salaries_Faculty_FT_Research'], errors='coerce').sum(),
                'Student Services': pd.to_numeric(df['Finance_Salaries_Student_Services'], errors='coerce').sum()
            }
            salary_df = pd.DataFrame(list(salary_categories.items()), columns=['Category', 'Amount'])
            salary_df = salary_df[salary_df['Amount'] > 0].sort_values('Amount', ascending=False)

            fig = px.pie(salary_df, values='Amount', names='Category',
                        title='👥 Salary Distribution by Category',
                        color_discrete_sequence=px.colors.sequential.Purples)
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e2e8f0'),
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Total salary by institution
            if 'Finance_Institution_Name' in df.columns:
                df_salary = df.copy()
                for col in salary_cols:
                    df_salary[col] = pd.to_numeric(df_salary[col], errors='coerce')
                df_salary['Total_Salary'] = df_salary[salary_cols].sum(axis=1)
                inst_salary = df_salary.groupby('Finance_Institution_Name')['Total_Salary'].sum().sort_values(ascending=False).head(10)

                fig = px.bar(x=inst_salary.index, y=inst_salary.values,
                            title='🏛️ Total Salaries by Institution (Top 10)',
                            color=inst_salary.values, color_continuous_scale='Viridis')
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    xaxis=dict(tickangle=-45),
                    yaxis_title='Salaries (AED)',
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)

        # Research Funding Analysis
        st.markdown("---")
        st.subheader("🔬 Research Funding Analysis")

        col1, col2 = st.columns(2)

        with col1:
            # Research funding by source
            research_sources = {
                'Institution': pd.to_numeric(df['Finance_Research_Fund_Institution'], errors='coerce').sum(),
                'Federal': pd.to_numeric(df['Finance_Research_Fund_Federal'], errors='coerce').sum(),
                'Local': pd.to_numeric(df['Finance_Research_Fund_Local'], errors='coerce').sum(),
                'Private UAE': pd.to_numeric(df['Finance_Research_Fund_Private_UAE'], errors='coerce').sum(),
                'UAE Nonprofit': pd.to_numeric(df['Finance_Research_Fund_Private_UAE_Nonprofit'], errors='coerce').sum(),
                'Foreign': pd.to_numeric(df['Finance_Research_Fund_Foreign'], errors='coerce').sum(),
                'Other': pd.to_numeric(df['Finance_Research_Fund_Other'], errors='coerce').sum()
            }
            research_df = pd.DataFrame(list(research_sources.items()), columns=['Source', 'Amount'])
            research_df = research_df[research_df['Amount'] > 0].sort_values('Amount', ascending=True)

            fig = px.bar(research_df, x='Amount', y='Source',
                        title='🔬 Research Funding by Source',
                        orientation='h', color='Amount',
                        color_continuous_scale='Blues')
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e2e8f0'),
                xaxis_title='Funding (AED)',
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Research funding by institution
            if 'Finance_Institution_Name' in df.columns and 'Finance_Research_Fund_Total' in df.columns:
                inst_research = df.groupby('Finance_Institution_Name')['Finance_Research_Fund_Total'].apply(
                    lambda x: pd.to_numeric(x, errors='coerce').sum()
                ).sort_values(ascending=False).head(10)

                fig = px.bar(x=inst_research.index, y=inst_research.values,
                            title='🏛️ Research Funding by Institution (Top 10)',
                            color=inst_research.values, color_continuous_scale='Greens')
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    xaxis=dict(tickangle=-45),
                    yaxis_title='Research Funding (AED)',
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)

        # Financial Health Analysis
        st.markdown("---")
        st.subheader("📊 Financial Health Indicators")

        col1, col2 = st.columns(2)

        with col1:
            # Revenue vs Expenses comparison
            if 'Finance_Institution_Name' in df.columns:
                df_health = df.copy()
                df_health['Revenue'] = pd.to_numeric(df_health['Finance_Total_Revenue'], errors='coerce')
                df_health['Expenses'] = pd.to_numeric(df_health['Finance_Total_Expenses'], errors='coerce')
                health_data = df_health.groupby('Finance_Institution_Name')[['Revenue', 'Expenses']].sum().reset_index()
                health_data = health_data.nlargest(10, 'Revenue')

                fig = go.Figure()
                fig.add_trace(go.Bar(x=health_data['Finance_Institution_Name'], y=health_data['Revenue'],
                                    name='Revenue', marker_color='#10b981'))
                fig.add_trace(go.Bar(x=health_data['Finance_Institution_Name'], y=health_data['Expenses'],
                                    name='Expenses', marker_color='#ef4444'))
                fig.update_layout(
                    title='💰 Revenue vs Expenses by Institution',
                    barmode='group',
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    xaxis=dict(tickangle=-45),
                    yaxis_title='Amount (AED)',
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Year-wise financial trend
            if 'Finance_Year' in df.columns:
                df_trend = df.copy()
                df_trend['Revenue'] = pd.to_numeric(df_trend['Finance_Total_Revenue'], errors='coerce')
                df_trend['Expenses'] = pd.to_numeric(df_trend['Finance_Total_Expenses'], errors='coerce')
                trend_data = df_trend.groupby('Finance_Year')[['Revenue', 'Expenses']].sum().reset_index()

                fig = go.Figure()
                fig.add_trace(go.Scatter(x=trend_data['Finance_Year'], y=trend_data['Revenue'],
                                        mode='lines+markers', name='Revenue',
                                        line=dict(color='#10b981', width=3),
                                        marker=dict(size=10)))
                fig.add_trace(go.Scatter(x=trend_data['Finance_Year'], y=trend_data['Expenses'],
                                        mode='lines+markers', name='Expenses',
                                        line=dict(color='#ef4444', width=3),
                                        marker=dict(size=10)))
                fig.update_layout(
                    title='📅 Financial Trends Over Years',
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    xaxis_title='Year',
                    yaxis_title='Amount (AED)',
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)


def display_research():
    """Display enriched Research analytics"""
    st.title("🔬 Research Analytics")
    st.markdown("**Research ecosystem analysis: projects, publications, patents, and innovation**")

    available = {k: v for k, v in st.session_state.datasets.items() if k in PRODUCT_CATEGORIES['Research']}
    if not available:
        st.warning("⚠️ No Research data available. Please load CSV files from the sidebar.")
        return

    # KPIs
    st.subheader("📊 Research Performance Indicators")
    cols = st.columns(5)

    if 'CHEDS-RES-26' in available:
        with cols[0]:
            count = len(available['CHEDS-RES-26']['data'])
            st.metric("🔬 Research Projects", f"{count:,}")

    if 'CHEDS-RES-27' in available:
        with cols[1]:
            count = len(available['CHEDS-RES-27']['data'])
            st.metric("📄 Publications", f"{count:,}")

    if 'CHEDS-RES-28' in available:
        with cols[2]:
            count = len(available['CHEDS-RES-28']['data'])
            st.metric("💡 Patents", f"{count:,}")

    if 'CHEDS-RES-30' in available:
        with cols[3]:
            count = len(available['CHEDS-RES-30']['data'])
            st.metric("📚 Citations", f"{count:,}")

    if 'CHEDS-RES-31' in available:
        with cols[4]:
            count = len(available['CHEDS-RES-31']['data'])
            st.metric("🏢 Research Units", f"{count:,}")

    st.markdown("---")

    # Research Projects Analysis
    if 'CHEDS-RES-26' in available:
        st.subheader("🔬 Research Projects Analysis")
        df = available['CHEDS-RES-26']['data']

        col1, col2 = st.columns(2)

        with col1:
            if 'Institution_Name' in df.columns:
                inst_counts = df['Institution_Name'].value_counts().head(10)
                fig = px.bar(x=inst_counts.values, y=inst_counts.index,
                            title='🏛️ Projects by Institution (Top 10)',
                            orientation='h', color=inst_counts.values,
                            color_continuous_scale='Blues')
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    height=400,
                    yaxis={'categoryorder': 'total ascending'}
                )
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            if 'Research_Department' in df.columns:
                dept_counts = df['Research_Department'].value_counts().head(10)
                fig = px.pie(values=dept_counts.values, names=dept_counts.index,
                            title='🎯 Projects by Department (Top 10)',
                            color_discrete_sequence=px.colors.sequential.Viridis)
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)

    # Publications Analysis
    if 'CHEDS-RES-27' in available:
        st.markdown("---")
        st.subheader("📄 Publications Analysis")
        df = available['CHEDS-RES-27']['data']

        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📚 Total Publications", f"{len(df):,}")
        with col2:
            if 'Pub_Total_Citations' in df.columns:
                total_citations = pd.to_numeric(df['Pub_Total_Citations'], errors='coerce').sum()
                st.metric("📊 Total Citations", f"{int(total_citations):,}")
        with col3:
            if 'Pub_scopus_Indicator' in df.columns:
                # Count publications with scopus indicator (1 or 'Y' or similar)
                scopus_count = df['Pub_scopus_Indicator'].astype(str).str.upper().str.startswith('Y').sum()
                st.metric("🔬 Scopus Indexed", f"{scopus_count:,}")
        with col4:
            st.metric("🏛️ Institutions", f"{df['Pub_Institution'].nunique():,}")

        col1, col2 = st.columns(2)

        with col1:
            # Use correct column name: Pub_Institution
            if 'Pub_Institution' in df.columns:
                pub_inst = df['Pub_Institution'].value_counts().head(10)
                fig = px.bar(x=pub_inst.values, y=pub_inst.index,
                            title='📚 Publications by Institution (Top 10)',
                            orientation='h', color=pub_inst.values,
                            color_continuous_scale='Teal')
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    height=400,
                    yaxis={'categoryorder': 'total ascending'}
                )
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Use correct column name: Pub_Publication_Type
            if 'Pub_Publication_Type' in df.columns:
                pub_type = df['Pub_Publication_Type'].value_counts()
                fig = px.pie(values=pub_type.values, names=pub_type.index,
                            title='📊 Publication Types',
                            hole=0.4, color_discrete_sequence=px.colors.sequential.Greens)
                fig.update_traces(textposition='inside', textinfo='percent+label+value')
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)

        # Additional publication visualizations
        col1, col2 = st.columns(2)
        with col1:
            # Publications by year
            if 'Pub_Year_Publication' in df.columns:
                year_pub = df['Pub_Year_Publication'].value_counts().sort_index()
                fig = px.line(x=year_pub.index, y=year_pub.values,
                            title='📈 Publications Trend by Year',
                            markers=True)
                fig.update_traces(line_color='#6366f1', marker=dict(size=8))
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    xaxis_title='Year',
                    yaxis_title='Number of Publications',
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Publication areas
            if 'Pub_Publication_Area' in df.columns:
                pub_area = df['Pub_Publication_Area'].value_counts().head(10)
                fig = px.bar(x=pub_area.index, y=pub_area.values,
                            title='🎯 Top 10 Publication Areas',
                            color=pub_area.values, color_continuous_scale='Viridis')
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    xaxis=dict(tickangle=-45),
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)

        # Citations analysis
        col1, col2 = st.columns(2)
        with col1:
            if 'Pub_Total_Citations' in df.columns:
                # Convert citations to numeric and handle errors
                df_citations = df.copy()
                df_citations['Pub_Total_Citations_Numeric'] = pd.to_numeric(df_citations['Pub_Total_Citations'], errors='coerce').fillna(0)

                # Top cited publications by institution
                top_cited = df_citations.groupby('Pub_Institution')['Pub_Total_Citations_Numeric'].sum().sort_values(ascending=False).head(10)
                fig = px.bar(x=top_cited.values, y=top_cited.index,
                            title='🏆 Top Cited Institutions',
                            orientation='h', color=top_cited.values,
                            color_continuous_scale='Oranges')
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    height=400,
                    yaxis={'categoryorder': 'total ascending'}
                )
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            if 'Pub_Researcher_Type' in df.columns:
                researcher_type = df['Pub_Researcher_Type'].value_counts()
                fig = px.pie(values=researcher_type.values, names=researcher_type.index,
                            title='👥 Publications by Researcher Type',
                            color_discrete_sequence=px.colors.sequential.Blues)
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)


def display_facilities():
    """Display enriched Facilities analytics"""
    st.title("🏢 Facilities & Estate Management Analytics")
    st.markdown("**Infrastructure and operations: space utilization, maintenance, and capacity planning**")

    available = {k: v for k, v in st.session_state.datasets.items() if k in PRODUCT_CATEGORIES['Facilities & Estate Management']}
    if not available:
        st.warning("⚠️ No Facilities data available. Please load CSV files from the sidebar.")
        return

    # Operations Analysis
    if 'CHEDS-FAC-33' in available:
        st.subheader("⚙️ Operations Metrics")
        df = available['CHEDS-FAC-33']['data']

        # Key metrics
        cols = st.columns(4)

        with cols[0]:
            if 'Operations_Average_Class_Size' in df.columns:
                avg = pd.to_numeric(df['Operations_Average_Class_Size'], errors='coerce').mean()
                st.metric("📚 Avg Class Size", f"{avg:.1f}")

        with cols[1]:
            if 'Operations_Average_Lab_Size' in df.columns:
                avg = pd.to_numeric(df['Operations_Average_Lab_Size'], errors='coerce').mean()
                st.metric("🔬 Avg Lab Size", f"{avg:.1f}")

        with cols[2]:
            st.metric("🏛️ Institutions", f"{df['Operations_Institution_Name'].nunique():,}")

        with cols[3]:
            if 'Operations_Degree' in df.columns:
                st.metric("🎓 Degree Programs", f"{df['Operations_Degree'].nunique():,}")

        st.markdown("---")

        # Visualizations
        col1, col2 = st.columns(2)

        with col1:
            if 'Operations_Institution_Name' in df.columns and 'Operations_Average_Class_Size' in df.columns:
                inst_class = df.groupby('Operations_Institution_Name')['Operations_Average_Class_Size'].apply(
                    lambda x: pd.to_numeric(x, errors='coerce').mean()
                ).sort_values(ascending=False).head(10)

                fig = px.bar(x=inst_class.index, y=inst_class.values,
                            title='📊 Average Class Size by Institution (Top 10)',
                            color=inst_class.values,
                            color_continuous_scale='Blues')
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    xaxis=dict(tickangle=-45),
                    yaxis_title='Avg Class Size',
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            if 'Operations_Institution_Name' in df.columns and 'Operations_Average_Lab_Size' in df.columns:
                inst_lab = df.groupby('Operations_Institution_Name')['Operations_Average_Lab_Size'].apply(
                    lambda x: pd.to_numeric(x, errors='coerce').mean()
                ).sort_values(ascending=False).head(10)

                fig = px.bar(x=inst_lab.index, y=inst_lab.values,
                            title='🔬 Average Lab Size by Institution (Top 10)',
                            color=inst_lab.values,
                            color_continuous_scale='Greens')
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    xaxis=dict(tickangle=-45),
                    yaxis_title='Avg Lab Size',
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)

        col1, col2 = st.columns(2)

        with col1:
            if 'Operations_Degree' in df.columns:
                degree_dist = df['Operations_Degree'].value_counts()
                fig = px.pie(values=degree_dist.values, names=degree_dist.index,
                            title='🎓 Programs by Degree Level',
                            hole=0.4,
                            color_discrete_sequence=px.colors.sequential.Viridis)
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            if 'Operations_Area_of_Specialization' in df.columns:
                spec_dist = df['Operations_Area_of_Specialization'].value_counts().head(10)
                fig = px.bar(x=spec_dist.values, y=spec_dist.index,
                            title='📚 Top 10 Areas of Specialization',
                            orientation='h', color=spec_dist.values,
                            color_continuous_scale='Purples')
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    yaxis={'categoryorder': 'total ascending'},
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)

    # Facility Overview
    if 'CHEDS-FAC-34' in available:
        st.markdown("---")
        st.subheader("🏛️ Facility Infrastructure Overview")
        df = available['CHEDS-FAC-34']['data']

        # Key facility metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if 'Overview_Room_Count' in df.columns:
                total_rooms = pd.to_numeric(df['Overview_Room_Count'], errors='coerce').sum()
                st.metric("🚪 Total Rooms", f"{int(total_rooms):,}")

        with col2:
            if 'Overview_Lab_Count' in df.columns:
                total_labs = pd.to_numeric(df['Overview_Lab_Count'], errors='coerce').sum()
                st.metric("🧪 Total Labs", f"{int(total_labs):,}")

        with col3:
            if 'Overview_Facilities_Area' in df.columns:
                total_area = pd.to_numeric(df['Overview_Facilities_Area'], errors='coerce').sum()
                st.metric("📐 Total Area (sq m)", f"{int(total_area):,}")

        with col4:
            if 'Overview_Books' in df.columns:
                total_books = pd.to_numeric(df['Overview_Books'], errors='coerce').sum()
                st.metric("📚 Library Books", f"{int(total_books):,}")

        # Institution characteristics
        st.markdown("### 🏛️ Institution Characteristics")
        col1, col2 = st.columns(2)

        with col1:
            if 'Overview_Institution_Type' in df.columns:
                type_dist = df['Overview_Institution_Type'].value_counts()
                fig = px.pie(values=type_dist.values, names=type_dist.index,
                            title='🏢 Institution Types',
                            hole=0.4,
                            color_discrete_sequence=px.colors.sequential.Blues)
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            if 'Overview_Ownership' in df.columns:
                ownership_dist = df['Overview_Ownership'].value_counts()
                fig = px.pie(values=ownership_dist.values, names=ownership_dist.index,
                            title='🏛️ Ownership Distribution',
                            color_discrete_sequence=px.colors.sequential.Greens)
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)

        # Facility breakdown
        st.markdown("### 🏗️ Facility Types & Capacity")
        col1, col2 = st.columns(2)

        with col1:
            # Facility types breakdown
            facility_types = {
                'Classrooms': pd.to_numeric(df['Overview_Facilities_Classrooms'], errors='coerce').sum(),
                'Labs': pd.to_numeric(df['Overview_Facilities_Labs'], errors='coerce').sum(),
                'Libraries': pd.to_numeric(df['Overview_Facilities_Libraries'], errors='coerce').sum(),
                'Residential': pd.to_numeric(df['Overview_Facilities_Residential'], errors='coerce').sum(),
                'Student Services': pd.to_numeric(df['Overview_Facilities_Student Services'], errors='coerce').sum(),
                'Administration': pd.to_numeric(df['Overview_Facilities_Administration'], errors='coerce').sum()
            }
            facility_df = pd.DataFrame(list(facility_types.items()), columns=['Type', 'Count'])
            facility_df = facility_df[facility_df['Count'] > 0].sort_values('Count', ascending=True)

            fig = px.bar(facility_df, x='Count', y='Type',
                        title='🏢 Facility Types Distribution',
                        orientation='h', color='Count',
                        color_continuous_scale='Teal')
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e2e8f0'),
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Rooms and Labs by institution
            if 'Overview_Institution_Name' in df.columns:
                df_capacity = df.copy()
                df_capacity['Total_Rooms'] = pd.to_numeric(df_capacity['Overview_Room_Count'], errors='coerce')
                inst_capacity = df_capacity.groupby('Overview_Institution_Name')['Total_Rooms'].sum().sort_values(ascending=False).head(10)

                fig = px.bar(x=inst_capacity.index, y=inst_capacity.values,
                            title='🏛️ Room Count by Institution (Top 10)',
                            color=inst_capacity.values, color_continuous_scale='Blues')
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    xaxis=dict(tickangle=-45),
                    yaxis_title='Number of Rooms',
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)

        # Student metrics
        st.markdown("### 👥 Student & Faculty Metrics")
        col1, col2 = st.columns(2)

        with col1:
            if 'Overview_Student_Faculty_Ratio' in df.columns:
                df_ratio = df.copy()
                df_ratio['Ratio'] = pd.to_numeric(df_ratio['Overview_Student_Faculty_Ratio'], errors='coerce')
                inst_ratio = df_ratio.groupby('Overview_Institution_Name')['Ratio'].mean().sort_values(ascending=False).head(10)

                fig = px.bar(x=inst_ratio.index, y=inst_ratio.values,
                            title='👨‍🏫 Student-Faculty Ratio by Institution (Top 10)',
                            color=inst_ratio.values, color_continuous_scale='Oranges')
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    xaxis=dict(tickangle=-45),
                    yaxis_title='Student-Faculty Ratio',
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            if 'Overview_Student_Dropout_Rate' in df.columns:
                df_dropout = df.copy()
                df_dropout['Dropout'] = pd.to_numeric(df_dropout['Overview_Student_Dropout_Rate'], errors='coerce')
                inst_dropout = df_dropout.groupby('Overview_Institution_Name')['Dropout'].mean().sort_values(ascending=False).head(10)

                fig = px.bar(x=inst_dropout.index, y=inst_dropout.values,
                            title='📉 Student Dropout Rate by Institution (Top 10)',
                            color=inst_dropout.values, color_continuous_scale='Reds')
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    xaxis=dict(tickangle=-45),
                    yaxis_title='Dropout Rate (%)',
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)

        # Library resources
        st.markdown("### 📚 Library Resources")
        col1, col2 = st.columns(2)

        with col1:
            # Library resources breakdown
            library_resources = {
                'Books': pd.to_numeric(df['Overview_Books'], errors='coerce').sum(),
                'E-books': pd.to_numeric(df['Overview_Ebooks'], errors='coerce').sum(),
                'Journals': pd.to_numeric(df['Overview_Journals'], errors='coerce').sum(),
                'E-serials': pd.to_numeric(df['Overview_Eserial'], errors='coerce').sum(),
                'Computers': pd.to_numeric(df['Overview_Computers'], errors='coerce').sum(),
                'Textbooks': pd.to_numeric(df['Overview_Textbooks'], errors='coerce').sum()
            }
            library_df = pd.DataFrame(list(library_resources.items()), columns=['Resource', 'Count'])
            library_df = library_df[library_df['Count'] > 0].sort_values('Count', ascending=False)

            fig = px.bar(library_df, x='Resource', y='Count',
                        title='📚 Library Resources Inventory',
                        color='Count', color_continuous_scale='Purples')
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e2e8f0'),
                xaxis=dict(tickangle=-45),
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Books by institution
            if 'Overview_Institution_Name' in df.columns and 'Overview_Books' in df.columns:
                inst_books = df.groupby('Overview_Institution_Name')['Overview_Books'].apply(
                    lambda x: pd.to_numeric(x, errors='coerce').sum()
                ).sort_values(ascending=False).head(10)

                fig = px.bar(x=inst_books.values, y=inst_books.index,
                            title='📚 Library Books by Institution (Top 10)',
                            orientation='h', color=inst_books.values,
                            color_continuous_scale='Greens')
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    yaxis={'categoryorder': 'total ascending'},
                    xaxis_title='Number of Books',
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)

        # Special facilities
        st.markdown("### 🎯 Special Facilities & Amenities")
        col1, col2 = st.columns(2)

        with col1:
            # Amenities availability
            amenities = {
                'Accommodations': (df['Overview_Accomodations'] == 'Yes').sum() if 'Overview_Accomodations' in df.columns else 0,
                'Activities Center': (df['Overview_Activities_Center'] == 'Yes').sum() if 'Overview_Activities_Center' in df.columns else 0,
                'Career Center': (df['Overview_Career_Center'] == 'Yes').sum() if 'Overview_Career_Center' in df.columns else 0,
                'Sports Facilities': (df['Overview_Sports_Facilities'] == 'Yes').sum() if 'Overview_Sports_Facilities' in df.columns else 0,
                'Parking': (df['Overview_Parking'] == 'Yes').sum() if 'Overview_Parking' in df.columns else 0,
                'Transport': (df['Overview_Transport'] == 'Yes').sum() if 'Overview_Transport' in df.columns else 0,
                'Special Needs': (df['Overview_Special_Needs_Availability'] == 'Yes').sum() if 'Overview_Special_Needs_Availability' in df.columns else 0
            }
            amenities_df = pd.DataFrame(list(amenities.items()), columns=['Amenity', 'Institutions'])
            amenities_df = amenities_df[amenities_df['Institutions'] > 0].sort_values('Institutions', ascending=True)

            fig = px.bar(amenities_df, x='Institutions', y='Amenity',
                        title='🏢 Amenities Availability Across Institutions',
                        orientation='h', color='Institutions',
                        color_continuous_scale='Blues')
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e2e8f0'),
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Accreditation
            if 'Overview_Accreditation_Body' in df.columns:
                accred_dist = df['Overview_Accreditation_Body'].value_counts().head(10)
                fig = px.bar(x=accred_dist.index, y=accred_dist.values,
                            title='🏅 Accreditation Bodies (Top 10)',
                            color=accred_dist.values, color_continuous_scale='Greens')
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    xaxis=dict(tickangle=-45),
                    yaxis_title='Number of Institutions',
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)


def display_support():
    """Display enriched Support Services analytics"""
    st.title("🎯 Supporting Services Analytics")
    st.markdown("**Student support and engagement: events, surveys, counseling, and services**")

    available = {k: v for k, v in st.session_state.datasets.items() if k in PRODUCT_CATEGORIES['Supporting Services']}
    if not available:
        st.warning("⚠️ No Support Services data available. Please load CSV files from the sidebar.")
        return

    # KPIs
    st.subheader("📊 Support Services Overview")
    cols = st.columns(4)

    if 'CHEDS-SUP-35' in available:
        with cols[0]:
            count = len(available['CHEDS-SUP-35']['data'])
            st.metric("🎪 Events", f"{count:,}")

    if 'CHEDS-SUP-36' in available:
        with cols[1]:
            count = len(available['CHEDS-SUP-36']['data'])
            st.metric("📋 Surveys", f"{count:,}")

    if 'CHEDS-SUP-40' in available:
        with cols[2]:
            count = len(available['CHEDS-SUP-40']['data'])
            st.metric("💬 Counseling Sessions", f"{count:,}")

    if 'CHEDS-SUP-41' in available:
        with cols[3]:
            count = len(available['CHEDS-SUP-41']['data'])
            st.metric("🎯 Services", f"{count:,}")

    st.markdown("---")

    # Events Analysis
    if 'CHEDS-SUP-35' in available:
        st.subheader("🎪 Events Analysis")
        df = available['CHEDS-SUP-35']['data']

        # Event metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📊 Total Events", f"{len(df):,}")
        with col2:
            if 'Event_Attendees' in df.columns:
                total_attendees = pd.to_numeric(df['Event_Attendees'], errors='coerce').sum()
                st.metric("👥 Total Attendees", f"{int(total_attendees):,}")
        with col3:
            if 'Event_Budget' in df.columns:
                total_budget = pd.to_numeric(df['Event_Budget'], errors='coerce').sum()
                st.metric("💰 Total Budget", f"AED {int(total_budget):,}")
        with col4:
            if 'Events_InstName' in df.columns:
                st.metric("🏛️ Institutions", f"{df['Events_InstName'].nunique():,}")

        col1, col2 = st.columns(2)

        with col1:
            if 'Events_InstName' in df.columns:
                event_inst = df['Events_InstName'].value_counts().head(10)
                fig = px.bar(x=event_inst.values, y=event_inst.index,
                            title='🏛️ Events by Institution (Top 10)',
                            orientation='h', color=event_inst.values,
                            color_continuous_scale='Viridis')
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    height=400,
                    yaxis={'categoryorder': 'total ascending'}
                )
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            if 'Event_Type' in df.columns:
                event_type = df['Event_Type'].value_counts()
                fig = px.pie(values=event_type.values, names=event_type.index,
                            title='🎭 Event Types',
                            color_discrete_sequence=px.colors.sequential.Plasma)
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)

        col1, col2 = st.columns(2)

        with col1:
            if 'Event_Category' in df.columns:
                event_cat = df['Event_Category'].value_counts().head(10)
                fig = px.bar(x=event_cat.index, y=event_cat.values,
                            title='📂 Event Categories (Top 10)',
                            color=event_cat.values, color_continuous_scale='Teal')
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    xaxis=dict(tickangle=-45),
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            if 'Event_Scope' in df.columns:
                scope_dist = df['Event_Scope'].value_counts()
                fig = px.pie(values=scope_dist.values, names=scope_dist.index,
                            title='🌍 Event Scope Distribution',
                            hole=0.4,
                            color_discrete_sequence=px.colors.sequential.Sunset)
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)

        col1, col2 = st.columns(2)

        with col1:
            if 'Event_Audience' in df.columns:
                audience_dist = df['Event_Audience'].value_counts().head(8)
                fig = px.bar(x=audience_dist.values, y=audience_dist.index,
                            title='👥 Target Audience (Top 8)',
                            orientation='h', color=audience_dist.values,
                            color_continuous_scale='Blues')
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    height=400,
                    yaxis={'categoryorder': 'total ascending'}
                )
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            if 'Event_Frequency' in df.columns:
                freq_dist = df['Event_Frequency'].value_counts()
                fig = px.pie(values=freq_dist.values, names=freq_dist.index,
                            title='🔄 Event Frequency',
                            color_discrete_sequence=px.colors.sequential.Viridis)
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)

        col1, col2 = st.columns(2)

        with col1:
            if 'Event_Department' in df.columns:
                dept_events = df['Event_Department'].value_counts().head(10)
                fig = px.bar(x=dept_events.index, y=dept_events.values,
                            title='🏢 Events by Department (Top 10)',
                            color=dept_events.values, color_continuous_scale='Purples')
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    xaxis=dict(tickangle=-45),
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            if 'Event_Attendees' in df.columns and 'Event_Type' in df.columns:
                df_attend = df.copy()
                df_attend['Event_Attendees_Numeric'] = pd.to_numeric(df_attend['Event_Attendees'], errors='coerce')
                avg_attend = df_attend.groupby('Event_Type')['Event_Attendees_Numeric'].mean().sort_values(ascending=False).head(8)
                fig = px.bar(x=avg_attend.index, y=avg_attend.values,
                            title='📊 Average Attendance by Event Type',
                            color=avg_attend.values, color_continuous_scale='Greens')
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    xaxis=dict(tickangle=-45),
                    yaxis_title='Avg Attendees',
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)

    # Surveys Analysis
    if 'CHEDS-SUP-36' in available:
        st.markdown("---")
        st.subheader("📋 Surveys Analysis")
        df = available['CHEDS-SUP-36']['data']

        # Survey metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📊 Total Surveys", f"{len(df):,}")
        with col2:
            if 'Survey_Number_Faculty_Respondents' in df.columns:
                total_faculty = pd.to_numeric(df['Survey_Number_Faculty_Respondents'], errors='coerce').sum()
                st.metric("👨‍🏫 Faculty Responses", f"{int(total_faculty):,}")
        with col3:
            if 'Survey_Number_Staff_Respondents' in df.columns:
                total_staff = pd.to_numeric(df['Survey_Number_Staff_Respondents'], errors='coerce').sum()
                st.metric("👥 Staff Responses", f"{int(total_staff):,}")
        with col4:
            if 'Survey_Institution_Name' in df.columns:
                st.metric("🏛️ Institutions", f"{df['Survey_Institution_Name'].nunique():,}")

        col1, col2 = st.columns(2)

        with col1:
            if 'Survey_Institution_Name' in df.columns:
                survey_inst = df['Survey_Institution_Name'].value_counts().head(10)
                fig = px.bar(x=survey_inst.index, y=survey_inst.values,
                            title='📊 Surveys by Institution (Top 10)',
                            color=survey_inst.values, color_continuous_scale='Teal')
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    xaxis=dict(tickangle=-45),
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            if 'Survey_Academic_Year' in df.columns:
                year_dist = df['Survey_Academic_Year'].value_counts().sort_index()
                fig = px.line(x=year_dist.index, y=year_dist.values,
                             title='📅 Survey Trends by Academic Year',
                             markers=True)
                fig.update_traces(line_color='#10b981', marker=dict(size=10))
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    xaxis_title='Academic Year',
                    yaxis_title='Number of Surveys',
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)

        # Faculty Survey Ratings
        st.markdown("### 👨‍🏫 Faculty Survey Ratings")
        col1, col2 = st.columns(2)

        faculty_cols = ['Survey_Faculty_Library', 'Survey_Faculty_Promotion',
                       'Survey_Faculty_Research_Facilities', 'Survey_Faculty_Teaching',
                       'Survey_Faculty_Work_Environment']

        faculty_avgs = {}
        for col in faculty_cols:
            if col in df.columns:
                avg_val = pd.to_numeric(df[col], errors='coerce').mean()
                faculty_avgs[col.replace('Survey_Faculty_', '')] = avg_val

        with col1:
            if faculty_avgs:
                fig = px.bar(x=list(faculty_avgs.values()), y=list(faculty_avgs.keys()),
                            title='📊 Faculty Survey Average Ratings',
                            orientation='h', color=list(faculty_avgs.values()),
                            color_continuous_scale='Blues')
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    xaxis_title='Average Rating',
                    yaxis={'categoryorder': 'total ascending'},
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)

        # Staff Survey Ratings
        staff_cols = ['Survey_Staff_Development', 'Survey_Staff_Appreciation',
                     'Survey_Staff_Manager', 'Survey_Staff_Promotion',
                     'Survey_Staff_Work_Condition']

        staff_avgs = {}
        for col in staff_cols:
            if col in df.columns:
                avg_val = pd.to_numeric(df[col], errors='coerce').mean()
                staff_avgs[col.replace('Survey_Staff_', '')] = avg_val

        with col2:
            if staff_avgs:
                fig = px.bar(x=list(staff_avgs.values()), y=list(staff_avgs.keys()),
                            title='📊 Staff Survey Average Ratings',
                            orientation='h', color=list(staff_avgs.values()),
                            color_continuous_scale='Greens')
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    xaxis_title='Average Rating',
                    yaxis={'categoryorder': 'total ascending'},
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)

        # Department Analysis
        col1, col2 = st.columns(2)

        with col1:
            if 'Survey_Department' in df.columns:
                dept_surveys = df['Survey_Department'].value_counts().head(10)
                fig = px.bar(x=dept_surveys.values, y=dept_surveys.index,
                            title='🏢 Surveys by Department (Top 10)',
                            orientation='h', color=dept_surveys.values,
                            color_continuous_scale='Purples')
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    yaxis={'categoryorder': 'total ascending'},
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            if 'Survey_Academic_Policies' in df.columns:
                policy_avg = pd.to_numeric(df['Survey_Academic_Policies'], errors='coerce').mean()
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=policy_avg,
                    title={'text': "Academic Policies Rating"},
                    gauge={'axis': {'range': [None, 5]},
                          'bar': {'color': "#6366f1"},
                          'steps': [
                              {'range': [0, 2], 'color': "#ef4444"},
                              {'range': [2, 3.5], 'color': "#f59e0b"},
                              {'range': [3.5, 5], 'color': "#10b981"}],
                          'threshold': {'line': {'color': "white", 'width': 4}, 'thickness': 0.75, 'value': policy_avg}}))
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)


def display_advancement():
    """Display enriched Advancement analytics"""
    st.title("🤝 Advancement Management Analytics")
    st.markdown("**External engagement: partnerships, employer relations, and startup ecosystem**")

    available = {k: v for k, v in st.session_state.datasets.items() if k in PRODUCT_CATEGORIES['Advancement Management']}
    if not available:
        st.warning("⚠️ No Advancement data available. Please load CSV files from the sidebar.")
        return

    # KPIs
    st.subheader("📊 Advancement Metrics")
    cols = st.columns(3)

    if 'CHEDS-ADV-37' in available:
        with cols[0]:
            count = len(available['CHEDS-ADV-37']['data'])
            st.metric("🤝 Partnerships", f"{count:,}")

    if 'CHEDS-ADV-38' in available:
        with cols[1]:
            count = len(available['CHEDS-ADV-38']['data'])
            st.metric("📚 PLO Records", f"{count:,}")

    if 'CHEDS-ADV-39' in available:
        with cols[2]:
            count = len(available['CHEDS-ADV-39']['data'])
            st.metric("🚀 Startups/Spinoffs", f"{count:,}")

    st.markdown("---")

    # Partnerships Analysis
    if 'CHEDS-ADV-37' in available:
        st.subheader("🤝 Partnerships Analysis")
        df = available['CHEDS-ADV-37']['data']

        # Partnership metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📊 Total Partnerships", f"{len(df):,}")
        with col2:
            if 'Partner_Name' in df.columns:
                st.metric("🏢 Unique Partners", f"{df['Partner_Name'].nunique():,}")
        with col3:
            if 'Partnership_value' in df.columns:
                total_value = pd.to_numeric(df['Partnership_value'], errors='coerce').sum()
                st.metric("💰 Total Value", f"AED {int(total_value):,}")
        with col4:
            if 'Partner_Country' in df.columns:
                st.metric("🌍 Countries", f"{df['Partner_Country'].nunique():,}")

        col1, col2 = st.columns(2)

        with col1:
            if 'Institution_Name' in df.columns:
                partner_inst = df['Institution_Name'].value_counts().head(10)
                fig = px.bar(x=partner_inst.values, y=partner_inst.index,
                            title='🏛️ Partnerships by Institution (Top 10)',
                            orientation='h', color=partner_inst.values,
                            color_continuous_scale='Blues')
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    height=400,
                    yaxis={'categoryorder': 'total ascending'}
                )
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            if 'Partnership_Type' in df.columns:
                partner_type = df['Partnership_Type'].value_counts()
                fig = px.pie(values=partner_type.values, names=partner_type.index,
                            title='🎯 Partnership Types',
                            hole=0.4, color_discrete_sequence=px.colors.sequential.Viridis)
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)

        col1, col2 = st.columns(2)

        with col1:
            if 'Partner_Type' in df.columns:
                partner_cat = df['Partner_Type'].value_counts().head(8)
                fig = px.bar(x=partner_cat.index, y=partner_cat.values,
                            title='🏢 Partner Types (Top 8)',
                            color=partner_cat.values, color_continuous_scale='Teal')
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    xaxis=dict(tickangle=-45),
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            if 'Partner_Category' in df.columns:
                partner_category = df['Partner_Category'].value_counts()
                fig = px.pie(values=partner_category.values, names=partner_category.index,
                            title='📂 Partner Categories',
                            color_discrete_sequence=px.colors.sequential.Plasma)
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)

        col1, col2 = st.columns(2)

        with col1:
            if 'Partner_Industry' in df.columns:
                industry_dist = df['Partner_Industry'].value_counts().head(10)
                fig = px.bar(x=industry_dist.values, y=industry_dist.index,
                            title='🏭 Partner Industries (Top 10)',
                            orientation='h', color=industry_dist.values,
                            color_continuous_scale='Greens')
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    yaxis={'categoryorder': 'total ascending'},
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            if 'Partner_Country' in df.columns:
                country_dist = df['Partner_Country'].value_counts().head(10)
                fig = px.bar(x=country_dist.index, y=country_dist.values,
                            title='🌍 Partner Countries (Top 10)',
                            color=country_dist.values, color_continuous_scale='Purples')
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    xaxis=dict(tickangle=-45),
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)

        col1, col2 = st.columns(2)

        with col1:
            if 'Partnership_Year' in df.columns:
                year_trend = df['Partnership_Year'].value_counts().sort_index()
                fig = px.line(x=year_trend.index, y=year_trend.values,
                             title='📅 Partnership Trends by Year',
                             markers=True)
                fig.update_traces(line_color='#6366f1', marker=dict(size=10))
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    xaxis_title='Year',
                    yaxis_title='Number of Partnerships',
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            if 'Partnership_Department' in df.columns:
                dept_partner = df['Partnership_Department'].value_counts().head(10)
                fig = px.bar(x=dept_partner.index, y=dept_partner.values,
                            title='🏢 Partnerships by Department (Top 10)',
                            color=dept_partner.values, color_continuous_scale='Blues')
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    xaxis=dict(tickangle=-45),
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)

        col1, col2 = st.columns(2)

        with col1:
            if 'Partnership_College' in df.columns:
                college_partner = df['Partnership_College'].value_counts().head(8)
                fig = px.bar(x=college_partner.values, y=college_partner.index,
                            title='🎓 Partnerships by College (Top 8)',
                            orientation='h', color=college_partner.values,
                            color_continuous_scale='Oranges')
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    yaxis={'categoryorder': 'total ascending'},
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            if 'Partnership_value' in df.columns and 'Partnership_Type' in df.columns:
                df_value = df.copy()
                df_value['Partnership_value_Numeric'] = pd.to_numeric(df_value['Partnership_value'], errors='coerce')
                avg_value = df_value.groupby('Partnership_Type')['Partnership_value_Numeric'].mean().sort_values(ascending=False).head(8)
                fig = px.bar(x=avg_value.index, y=avg_value.values,
                            title='💰 Average Value by Partnership Type',
                            color=avg_value.values, color_continuous_scale='Greens')
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    xaxis=dict(tickangle=-45),
                    yaxis_title='Avg Value (AED)',
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)

    # PLO Analysis (ADV-38 is actually PLO data, not Employers)
    if 'CHEDS-ADV-38' in available:
        st.markdown("---")
        st.subheader("📚 Program Learning Outcomes (PLO)")
        df = available['CHEDS-ADV-38']['data']

        # PLO metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📊 Total PLOs", f"{len(df):,}")
        with col2:
            if 'PLO_Institution_Name' in df.columns:
                st.metric("🏛️ Institutions", f"{df['PLO_Institution_Name'].nunique():,}")
        with col3:
            if 'PLO_Program_name' in df.columns:
                st.metric("📚 Programs", f"{df['PLO_Program_name'].nunique():,}")
        with col4:
            if 'PLO_Period' in df.columns:
                st.metric("📅 Periods", f"{df['PLO_Period'].nunique():,}")

        col1, col2 = st.columns(2)

        with col1:
            if 'PLO_Institution_Name' in df.columns:
                plo_inst = df['PLO_Institution_Name'].value_counts().head(10)
                fig = px.bar(x=plo_inst.index, y=plo_inst.values,
                            title='📊 PLOs by Institution (Top 10)',
                            color=plo_inst.values, color_continuous_scale='Teal')
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    xaxis=dict(tickangle=-45),
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            if 'PLO_Program_name' in df.columns:
                program_dist = df['PLO_Program_name'].value_counts().head(10)
                fig = px.bar(x=program_dist.values, y=program_dist.index,
                            title='📚 PLOs by Program (Top 10)',
                            orientation='h', color=program_dist.values,
                            color_continuous_scale='Blues')
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    yaxis={'categoryorder': 'total ascending'},
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)

        col1, col2 = st.columns(2)

        with col1:
            if 'PLO_Period' in df.columns:
                period_dist = df['PLO_Period'].value_counts().sort_index()
                fig = px.line(x=period_dist.index, y=period_dist.values,
                             title='📅 PLO Trends by Period',
                             markers=True)
                fig.update_traces(line_color='#10b981', marker=dict(size=10))
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    xaxis_title='Period',
                    yaxis_title='Number of PLOs',
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            if 'PLO_code' in df.columns:
                plo_code_dist = df['PLO_code'].value_counts().head(10)
                fig = px.bar(x=plo_code_dist.index, y=plo_code_dist.values,
                            title='🔢 Most Common PLO Codes (Top 10)',
                            color=plo_code_dist.values, color_continuous_scale='Purples')
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    xaxis=dict(tickangle=-45),
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)

    # Startups Analysis
    if 'CHEDS-ADV-39' in available:
        st.markdown("---")
        st.subheader("🚀 Startup Ecosystem")
        df = available['CHEDS-ADV-39']['data']

        # Startup metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📊 Total Startups", f"{len(df):,}")
        with col2:
            if 'Startup_Institution_Name' in df.columns:
                st.metric("🏛️ Institutions", f"{df['Startup_Institution_Name'].nunique():,}")
        with col3:
            if 'Startup_Status' in df.columns:
                active_count = df['Startup_Status'].value_counts().get('Active', 0)
                st.metric("✅ Active Startups", f"{active_count:,}")
        with col4:
            if 'Startup_Academic_Year' in df.columns:
                st.metric("📅 Academic Years", f"{df['Startup_Academic_Year'].nunique():,}")

        col1, col2 = st.columns(2)

        with col1:
            if 'Startup_Institution_Name' in df.columns:
                startup_inst = df['Startup_Institution_Name'].value_counts()
                fig = px.pie(values=startup_inst.values, names=startup_inst.index,
                            title='🏛️ Startups by Institution',
                            color_discrete_sequence=px.colors.sequential.Greens)
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            if 'Startup_Status' in df.columns:
                status_dist = df['Startup_Status'].value_counts()
                fig = px.pie(values=status_dist.values, names=status_dist.index,
                            title='📊 Startup Status Distribution',
                            hole=0.4,
                            color_discrete_sequence=px.colors.sequential.Viridis)
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)

        col1, col2 = st.columns(2)

        with col1:
            if 'Startup_Year' in df.columns:
                year_trend = df['Startup_Year'].value_counts().sort_index()
                fig = px.line(x=year_trend.index, y=year_trend.values,
                             title='📅 Startup Launch Trends by Year',
                             markers=True)
                fig.update_traces(line_color='#f59e0b', marker=dict(size=10))
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    xaxis_title='Year',
                    yaxis_title='Number of Startups',
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            if 'Startup_Academic_Year' in df.columns:
                acad_year_dist = df['Startup_Academic_Year'].value_counts().sort_index()
                fig = px.bar(x=acad_year_dist.index, y=acad_year_dist.values,
                            title='📚 Startups by Academic Year',
                            color=acad_year_dist.values, color_continuous_scale='Blues')
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    xaxis=dict(tickangle=-45),
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)


def display_data_explorer():
    """Interactive data explorer for any uploaded file"""
    st.header("🔍 Data Explorer")

    if not st.session_state.datasets:
        st.warning("⚠️ No data loaded. Please load CSV files first.")
        return

    # File selector
    file_options = {f"{product_id}: {info['filename']}" for product_id, info in st.session_state.datasets.items()}
    selected_file = st.selectbox(
        "Select a file to explore:",
        sorted(file_options),
        help="Choose which dataset you want to explore in detail"
    )

    if selected_file:
        product_id = selected_file.split(':')[0]
        dataset_info = st.session_state.datasets[product_id]
        df = dataset_info['data']

        st.markdown("---")

        # Dataset overview
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Rows", f"{len(df):,}")
        with col2:
            st.metric("Total Columns", len(df.columns))
        with col3:
            st.metric("File Name", dataset_info['filename'])
        with col4:
            st.metric("Product ID", product_id)

        st.markdown("---")

        # Column selector and filters
        st.subheader("📋 Data Preview & Filters")

        col_left, col_right = st.columns([2, 1])

        with col_left:
            # Column selection
            all_columns = list(df.columns)
            selected_columns = st.multiselect(
                "Select columns to display:",
                all_columns,
                default=all_columns[:10] if len(all_columns) > 10 else all_columns,
                help="Choose which columns to show in the data table"
            )

        with col_right:
            # Row limit
            row_limit = st.slider("Number of rows to display:", 5, min(100, len(df)), 20)

        # Column-based filters
        st.markdown("### 🎛️ Filters")
        filter_cols = st.columns(3)

        filtered_df = df.copy()

        # Allow filtering on up to 3 columns
        for idx, filter_col in enumerate(filter_cols):
            with filter_col:
                filter_column = st.selectbox(
                    f"Filter Column {idx + 1}",
                    ["None"] + all_columns,
                    key=f"filter_col_{idx}"
                )

                if filter_column != "None":
                    unique_values = filtered_df[filter_column].dropna().unique()

                    if len(unique_values) <= 50:  # Dropdown for small number of unique values
                        filter_values = st.multiselect(
                            f"Select values:",
                            sorted(unique_values.tolist()),
                            key=f"filter_val_{idx}"
                        )
                        if filter_values:
                            filtered_df = filtered_df[filtered_df[filter_column].isin(filter_values)]
                    else:  # Text search for large number of unique values
                        filter_text = st.text_input(
                            f"Search text:",
                            key=f"filter_text_{idx}"
                        )
                        if filter_text:
                            filtered_df = filtered_df[
                                filtered_df[filter_column].astype(str).str.contains(filter_text, case=False, na=False)
                            ]

        st.markdown("---")

        # Display filtered data
        display_df = filtered_df[selected_columns] if selected_columns else filtered_df

        st.subheader(f"📊 Data Table ({len(filtered_df):,} rows after filtering)")
        st.dataframe(
            display_df.head(row_limit),
            use_container_width=True,
            height=400
        )

        # Download filtered data
        csv_data = display_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Filtered Data as CSV",
            data=csv_data,
            file_name=f"{product_id}_filtered.csv",
            mime="text/csv",
            use_container_width=True
        )

        st.markdown("---")

        # Statistical summary
        st.subheader("📈 Statistical Summary")

        # Numeric columns summary
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if numeric_cols:
            st.markdown("**Numeric Columns:**")
            st.dataframe(df[numeric_cols].describe(), use_container_width=True)

        # Categorical columns summary
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        if categorical_cols and len(categorical_cols) <= 10:
            st.markdown("**Categorical Columns (Value Counts):**")
            cat_col = st.selectbox("Select a categorical column:", categorical_cols)
            if cat_col:
                value_counts = df[cat_col].value_counts().head(20)

                col1, col2 = st.columns([1, 2])
                with col1:
                    st.dataframe(
                        pd.DataFrame({
                            'Value': value_counts.index,
                            'Count': value_counts.values
                        }),
                        use_container_width=True
                    )
                with col2:
                    fig = px.bar(
                        x=value_counts.values,
                        y=value_counts.index,
                        orientation='h',
                        title=f"Top 20 Values in {cat_col}",
                        labels={'x': 'Count', 'y': cat_col}
                    )
                    fig.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='#e2e8f0'),
                        height=400
                    )
                    st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        # Data quality check
        st.subheader("🔍 Data Quality")

        quality_cols = st.columns(3)
        with quality_cols[0]:
            missing_data = df.isnull().sum()
            missing_pct = (missing_data / len(df) * 100).round(2)
            missing_df = pd.DataFrame({
                'Column': missing_data.index,
                'Missing Count': missing_data.values,
                'Missing %': missing_pct.values
            })
            missing_df = missing_df[missing_df['Missing Count'] > 0].sort_values('Missing Count', ascending=False)

            if len(missing_df) > 0:
                st.warning(f"⚠️ {len(missing_df)} columns have missing values")
                st.dataframe(missing_df, use_container_width=True, height=300)
            else:
                st.success("✅ No missing values detected!")

        with quality_cols[1]:
            duplicate_rows = df.duplicated().sum()
            st.metric("Duplicate Rows", duplicate_rows)
            if duplicate_rows > 0:
                st.warning(f"⚠️ {duplicate_rows} duplicate rows found")
            else:
                st.success("✅ No duplicates")

        with quality_cols[2]:
            data_types = df.dtypes.value_counts()
            st.markdown("**Column Types:**")
            for dtype, count in data_types.items():
                st.write(f"**{dtype}:** {count}")

def main():
    # Header
    st.markdown('<h1 style="text-align: center;">🎓 CHEDS Analytics Dashboard</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #94a3b8;">UAE Higher Education Data Analytics</p>', unsafe_allow_html=True)
    st.markdown("---")

    # Sidebar
    with st.sidebar:
        st.title("⚙️ Dashboard Controls")

        st.markdown("### 📂 Load Data")

        if st.session_state.data_loaded:
            st.success(f"✅ Auto-loaded {len(st.session_state.datasets)} CSV files")

        if st.button("🔄 Reload All CSV Files", use_container_width=True):
            with st.spinner("Reloading..."):
                if auto_load_csv_files():
                    st.success(f"✅ Reloaded {len(st.session_state.datasets)} files!")
                    st.rerun()
                else:
                    st.error("❌ csv_files directory not found!")

        st.markdown("### 📤 Upload Files")
        uploaded_files = st.file_uploader("Upload CSV files", type=['csv'], accept_multiple_files=True)

        if uploaded_files:
            for file in uploaded_files:
                df = pd.read_csv(file, encoding='utf-8-sig')
                product_id = file.name.split('_')[0]
                st.session_state.datasets[product_id] = {
                    'data': df,
                    'filename': file.name,
                    'rows': len(df),
                    'columns': len(df.columns)
                }
            st.session_state.data_loaded = True
            st.success(f"✅ Uploaded {len(uploaded_files)} files!")

        if st.session_state.data_loaded:
            st.markdown("---")
            st.markdown("### 📊 Status")
            st.info(f"**Products:** {len(st.session_state.datasets)}")
            st.info(f"**Records:** {sum(ds['rows'] for ds in st.session_state.datasets.values()):,}")

    # Main content
    if st.session_state.data_loaded:
        tabs = st.tabs([
            "📊 Overview",
            "🔍 Data Explorer",
            "📚 Learning & Teaching",
            "👥 HR",
            "💰 Financial",
            "🔬 Research",
            "🏢 Facilities",
            "🎯 Support",
            "🤝 Advancement"
        ])

        with tabs[0]:
            display_overview()
        with tabs[1]:
            display_data_explorer()
        with tabs[2]:
            display_learning_teaching()
        with tabs[3]:
            display_human_resources()
        with tabs[4]:
            display_financial()
        with tabs[5]:
            display_research()
        with tabs[6]:
            display_facilities()
        with tabs[7]:
            display_support()
        with tabs[8]:
            display_advancement()
    else:
        display_overview()

if __name__ == "__main__":
    main()
