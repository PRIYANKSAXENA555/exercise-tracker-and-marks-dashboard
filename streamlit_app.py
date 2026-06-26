# ================================================================
# BAKLIWAL TUTORIALS - JEE STUDENT MARKS DASHBOARD
# With Single Sign-On (SSO) Support
# ================================================================

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import requests
import json
import re

# ================================================================
# PAGE CONFIGURATION
# ================================================================

st.set_page_config(
    page_title="Bakliwal Tutorials - Marks Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ================================================================
# GOOGLE APPS SCRIPT API CONFIGURATION
# ================================================================

# Replace with your Google Apps Script Web App URL
APPS_SCRIPT_URL = 'https://script.google.com/macros/s/YOUR_SCRIPT_ID/exec'

# ================================================================
# AUTHENTICATION FUNCTIONS
# ================================================================

def get_student_data_from_api(name, mother_name):
    """Fetch student marks from Google Apps Script API"""
    try:
        response = requests.get(APPS_SCRIPT_URL, params={
            'name': name,
            'motherName': mother_name
        }, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {'success': False, 'message': 'API request failed'}
            
    except requests.exceptions.RequestException as e:
        return {'success': False, 'message': f'Connection error: {str(e)}'}
    except Exception as e:
        return {'success': False, 'message': f'Error: {str(e)}'}

def authenticate_student(name, mother_name):
    """Authenticate student and fetch data"""
    result = get_student_data_from_api(name, mother_name)
    
    if result.get('success'):
        return result
    else:
        return None

# ================================================================
# UI RENDERING FUNCTIONS
# ================================================================

def render_login_page():
    """Render the login page"""
    st.markdown("""
    <style>
    .login-container {
        max-width: 450px;
        margin: 0 auto;
        padding: 40px;
        background: white;
        border-radius: 20px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
    }
    .login-title {
        text-align: center;
        color: #667eea;
        font-size: 28px;
        font-weight: bold;
        margin-bottom: 5px;
    }
    .login-subtitle {
        text-align: center;
        color: #666;
        margin-bottom: 30px;
    }
    .stButton button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 12px;
        font-size: 16px;
        font-weight: 600;
        border-radius: 10px;
    }
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(102,126,234,0.4);
    }
    .teacher-info {
        text-align: center;
        font-size: 12px;
        color: #666;
        margin-top: 20px;
        padding: 15px;
        background: #f8f9fa;
        border-radius: 10px;
    }
    .teacher-badge {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 4px;
        font-size: 11px;
        margin: 2px;
        color: white;
    }
    .badge-physics { background: #4299e1; }
    .badge-chemistry { background: #ed8936; }
    .badge-maths { background: #9f7aea; }
    </style>
    """, unsafe_allow_html=True)

    # Get query parameters for SSO
    query_params = st.query_params
    sso_name = query_params.get("student", [None])[0]
    sso_mother = query_params.get("mother", [None])[0]

    # Check if this is an SSO login
    if sso_name and sso_mother:
        with st.spinner("Authenticating..."):
            result = authenticate_student(sso_name, sso_mother)
            if result:
                st.session_state['student_data'] = result
                st.session_state['logged_in'] = True
                st.rerun()
            else:
                st.error("❌ SSO authentication failed. Please login manually.")

    # If not logged in, show login form
    if not st.session_state.get('logged_in', False):
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown('<div class="login-title">📊 Bakliwal Tutorials</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-subtitle">JEE 2027 - Marks Dashboard</div>', unsafe_allow_html=True)
        
        with st.form("login_form"):
            name = st.text_input("👤 Your Full Name", placeholder="Enter your full name")
            mother_name = st.text_input("👩 Mother's Name", placeholder="Enter your mother's name", type="password")
            submitted = st.form_submit_button("🔓 View My Results")
            
            if submitted:
                if not name or not mother_name:
                    st.error("Please enter both Name and Mother's Name")
                else:
                    with st.spinner("Fetching your data..."):
                        result = authenticate_student(name, mother_name)
                        if result:
                            st.session_state['student_data'] = result
                            st.session_state['logged_in'] = True
                            st.rerun()
                        else:
                            st.error("❌ Invalid Name or Mother's Name")
        
        st.markdown("""
        <div class="teacher-info">
            <strong>🔑 Teacher Logins:</strong><br>
            <span class="teacher-badge badge-physics">Physics</span> Physics Teacher / physics_teacher
            <span class="teacher-badge badge-chemistry">Chemistry</span> Chemistry Teacher / chemistry_teacher
            <span class="teacher-badge badge-maths">Mathematics</span> Maths Teacher / maths_teacher
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

def render_dashboard(data):
    """Render the main dashboard"""
    student = data['student']
    tests = data['tests']
    stats = data['stats']
    
    # Header
    st.markdown(f"""
    <style>
    .header {{
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px 30px;
        border-radius: 15px;
        margin-bottom: 25px;
    }}
    .header h1 {{
        font-size: 28px;
        margin: 0;
    }}
    .header p {{
        margin: 5px 0 0 0;
        opacity: 0.9;
        font-size: 14px;
    }}
    .logout-btn {{
        float: right;
        background: rgba(255,255,255,0.2);
        color: white;
        padding: 8px 20px;
        border: none;
        border-radius: 8px;
        cursor: pointer;
        font-weight: 600;
    }}
    .logout-btn:hover {{
        background: rgba(255,255,255,0.3);
    }}
    </style>
    <div class="header">
        <button class="logout-btn" onclick="window.location.href='?logout=true'">🚪 Logout</button>
        <h1>📊 Welcome, {student['name']}! 👋</h1>
        <p>Roll No: {student.get('rollNo', 'N/A')} | Batch: {student.get('batch', 'N/A')} | Branch: {student.get('branch', 'N/A')}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Statistics Cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📝 Tests Appeared", stats['total_tests'])
    with col2:
        st.metric("📈 Average Percentage", f"{stats['avg_percentage']}%")
    with col3:
        best_rank = stats['best_rank']
        st.metric("🏆 Best Rank", f"#{best_rank}" if best_rank != 'N/A' else 'N/A')
    with col4:
        st.metric("⭐ Highest Score", stats['highest_score'])
    
    st.markdown("---")
    
    # Charts Section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📊 Latest Test Performance")
        if tests:
            latest = tests[0]
            subjects = ['Physics', 'Chemistry', 'Maths']
            marks = [latest['physics']['marks'], latest['chemistry']['marks'], latest['maths']['marks']]
            max_marks = [latest['physics']['max'], latest['chemistry']['max'], latest['maths']['max']]
            percentages = [(m / max_m * 100) for m, max_m in zip(marks, max_marks)]
            
            fig = go.Figure(data=[
                go.Bar(
                    x=subjects,
                    y=marks,
                    text=[f"{p:.1f}%" for p in percentages],
                    textposition='outside',
                    marker_color=['#667eea', '#764ba2', '#f093fb'],
                    name='Marks',
                    width=0.6
                )
            ])
            fig.update_layout(
                yaxis_title="Marks",
                yaxis_range=[0, max(max_marks) * 1.1],
                showlegend=False,
                height=300,
                margin=dict(l=0, r=0, t=20, b=0)
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📈 Performance Trend")
        if len(tests) >= 2:
            # Show trend for last 5 tests
            trend_tests = tests[:5]
            trend_data = []
            for test in reversed(trend_tests):
                total_percent = float(test['percentage'])
                trend_data.append({
                    'Test': test['testName'][:15] + '...' if len(test['testName']) > 15 else test['testName'],
                    'Percentage': total_percent
                })
            
            df_trend = pd.DataFrame(trend_data)
            fig = px.line(
                df_trend, 
                x='Test', 
                y='Percentage',
                markers=True,
                title=None
            )
            fig.update_layout(
                yaxis_title="Percentage (%)",
                yaxis_range=[0, 100],
                height=300,
                margin=dict(l=0, r=0, t=20, b=0),
                showlegend=False
            )
            fig.update_traces(line_color='#667eea', line_width=2)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Need at least 2 tests to show trend")
    
    # Complete Test History
    st.markdown("---")
    st.subheader("📋 Complete Test History")
    
    # Prepare data for table
    table_data = []
    for test in tests:
        percent = float(test['percentage'])
        rank = test['rank']
        
        # Determine performance level
        if percent >= 75:
            performance = "🏆 Excellent"
            color = "#28a745"
        elif percent >= 60:
            performance = "✅ Good"
            color = "#17a2b8"
        elif percent >= 45:
            performance = "📖 Average"
            color = "#ffc107"
        else:
            performance = "📚 Needs Improvement"
            color = "#dc3545"
        
        table_data.append({
            "Test": test['testName'],
            "Rank": f"#{rank}" if rank != '-' else '-',
            "Physics": f"{test['physics']['marks']}/{test['physics']['max']}",
            "Chemistry": f"{test['chemistry']['marks']}/{test['chemistry']['max']}",
            "Maths": f"{test['maths']['marks']}/{test['maths']['max']}",
            "Total": f"{test['total']['marks']}/{test['total']['max']}",
            "Percentage": f"{percent:.1f}%",
            "Performance": performance
        })
    
    df_table = pd.DataFrame(table_data)
    st.dataframe(
        df_table,
        use_container_width=True,
        column_config={
            "Performance": st.column_config.Column(
                "Performance",
                help="Performance level based on percentage",
                width="medium"
            )
        },
        height=400
    )
    
    # Download option
    csv = df_table.to_csv(index=False)
    st.download_button(
        label="📥 Download Results as CSV",
        data=csv,
        file_name=f"{student['name']}_results.csv",
        mime="text/csv"
    )

def render_teacher_dashboard(data):
    """Render teacher dashboard view"""
    st.markdown("""
    <style>
    .teacher-header {
        background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
        color: white;
        padding: 20px 30px;
        border-radius: 15px;
        margin-bottom: 25px;
    }
    </style>
    <div class="teacher-header">
        <h1>👨‍🏫 Teacher Dashboard</h1>
        <p>Welcome, {name}! You can view all student data here.</p>
    </div>
    """.format(name=data['student']['name']), unsafe_allow_html=True)
    
    # Show all students data
    st.info("📊 Teacher View: Showing all student data")
    # Add teacher-specific functionality here

# ================================================================
# MAIN APP
# ================================================================

def main():
    # Handle logout
    if st.query_params.get("logout") == "true":
        st.session_state.clear()
        st.rerun()
    
    # Initialize session state
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
    
    if 'student_data' not in st.session_state:
        st.session_state['student_data'] = None
    
    # Render login or dashboard
    if not st.session_state['logged_in']:
        render_login_page()
    else:
        data = st.session_state['student_data']
        if data.get('success'):
            render_dashboard(data)
        else:
            st.error("❌ Failed to load data")
            if st.button("🔄 Try Again"):
                st.session_state.clear()
                st.rerun()

if __name__ == "__main__":
    main()