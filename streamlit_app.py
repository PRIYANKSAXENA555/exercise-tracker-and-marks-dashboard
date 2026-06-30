# ================================================================
# BAKLIWAL TUTORIALS - JEE STUDENT MARKS DASHBOARD
# With Dropdown for Student Names & Lowercase Password
# ================================================================

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import requests
import json
import re

# ================================================================
# PAGE CONFIGURATION
# ================================================================

st.set_page_config(
    page_title="Bakliwal Tutorials - JEE Marks Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ================================================================
# GOOGLE APPS SCRIPT API CONFIGURATION
# ================================================================

APPS_SCRIPT_URL = 'https://script.google.com/macros/s/AKfycbw065HYIQAUcsAbV3mUklMWneWu33Z_cD8dlMzWbBwpgHs1NCZ9-q3c-DoeHziCK6cwHA/exec'

# ================================================================
# AUTHENTICATION FUNCTIONS
# ================================================================

@st.cache_data(ttl=300)
def get_student_names_from_api():
    """Fetch all student names from Google Sheet for dropdown"""
    try:
        response = requests.get(APPS_SCRIPT_URL, params={
            'action': 'getNames'
        }, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                return data.get('names', [])
        return []
            
    except requests.exceptions.RequestException as e:
        st.error(f"⚠️ Connection error: {str(e)}")
        return []
    except Exception as e:
        st.error(f"⚠️ Error: {str(e)}")
        return []

def get_student_data_from_api(name, mother_name):
    """Fetch student marks from Google Apps Script API"""
    try:
        # Convert mother name to lowercase for authentication
        mother_name_lower = mother_name.lower().strip()
        
        response = requests.get(APPS_SCRIPT_URL, params={
            'name': name,
            'motherName': mother_name_lower
        }, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {'success': False, 'message': f'API request failed: {response.status_code}'}
            
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
        st.error(f"❌ {result.get('message', 'Authentication failed')}")
        return None

# ================================================================
# UI RENDERING FUNCTIONS
# ================================================================

def render_login_page():
    """Render the login page with dropdown for student names"""
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
    .stSelectbox label {
        font-weight: 500;
        color: #333;
    }
    .stTextInput label {
        font-weight: 500;
        color: #333;
    }
    .note {
        font-size: 12px;
        color: #888;
        text-align: center;
        margin-top: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

    # Get query parameters for SSO
    query_params = st.query_params
    sso_name = query_params.get("student", [None])[0]
    sso_mother = query_params.get("mother", [None])[0]

    # Check if this is an SSO login
    if sso_name and sso_mother:
        with st.spinner("🔐 Authenticating..."):
            # Convert mother name to lowercase for SSO
            sso_mother_lower = sso_mother.lower().strip()
            result = authenticate_student(sso_name, sso_mother_lower)
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
        
        # Fetch student names for dropdown
        student_names = get_student_names_from_api()
        
        with st.form("login_form"):
            if student_names:
                # Dropdown for student names
                name = st.selectbox(
                    "👤 Select Your Name",
                    options=student_names,
                    placeholder="Select your name from the list"
                )
            else:
                # Fallback to text input if API fails
                st.warning("⚠️ Could not load student list. Please enter your name manually.")
                name = st.text_input("👤 Your Full Name", placeholder="Enter your full name as in records")
            
            # Mother's name as password (will be converted to lowercase)
            mother_name = st.text_input(
                "👩 Mother's Name (Password)",
                placeholder="Enter your mother's name (case insensitive)",
                type="password"
            )
            
            st.markdown('<p class="note">💡 Mother\'s name is case-insensitive (converted to lowercase automatically)</p>', unsafe_allow_html=True)
            
            submitted = st.form_submit_button("🔓 View My Results")
            
            if submitted:
                if not name or not mother_name:
                    st.error("⚠️ Please select your name and enter mother's name")
                else:
                    with st.spinner("📊 Fetching your data..."):
                        # Convert mother name to lowercase
                        mother_name_lower = mother_name.lower().strip()
                        result = authenticate_student(name, mother_name_lower)
                        if result:
                            st.session_state['student_data'] = result
                            st.session_state['logged_in'] = True
                            st.rerun()
                        else:
                            st.error("❌ Invalid Name or Mother's Name. Please check and try again.")
        
        st.markdown("""
        <div class="teacher-info">
            <strong>🔑 Teacher Logins:</strong><br>
            <span class="teacher-badge badge-physics">Physics</span> Physics Teacher / physics_teacher
            <span class="teacher-badge badge-chemistry">Chemistry</span> Chemistry Teacher / chemistry_teacher
            <span class="teacher-badge badge-maths">Mathematics</span> Maths Teacher / maths_teacher
            <br><br>
            <strong>👨‍🎓 Students:</strong> Select your name from dropdown, then enter Mother's Name
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

def render_dashboard(data):
    """Render the main dashboard"""
    student = data['student']
    tests = data['tests']
    stats = data['stats']
    
    # Header with student info
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
                height=350,
                margin=dict(l=0, r=0, t=20, b=0)
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📈 Performance Trend")
        if len(tests) >= 2:
            trend_tests = tests[:5]
            trend_data = []
            for test in reversed(trend_tests):
                total_percent = float(test['percentage'])
                test_name = test['testName']
                if len(test_name) > 15:
                    test_name = test_name[:15] + '...'
                trend_data.append({
                    'Test': test_name,
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
                height=350,
                margin=dict(l=0, r=0, t=20, b=0),
                showlegend=False
            )
            fig.update_traces(line_color='#667eea', line_width=2)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("📊 Need at least 2 tests to show trend")
    
    # Complete Test History
    st.markdown("---")
    st.subheader("📋 Complete Test History")
    
    table_data = []
    for test in tests:
        percent = float(test['percentage'])
        rank = test['rank']
        
        if percent >= 75:
            performance = "🏆 Excellent"
        elif percent >= 60:
            performance = "✅ Good"
        elif percent >= 45:
            performance = "📖 Average"
        else:
            performance = "📚 Needs Improvement"
        
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
        height=400
    )
    
    csv = df_table.to_csv(index=False)
    st.download_button(
        label="📥 Download Results as CSV",
        data=csv,
        file_name=f"{student['name']}_results.csv",
        mime="text/csv",
        use_container_width=True
    )

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
        if data and data.get('success'):
            render_dashboard(data)
        else:
            st.error("❌ Failed to load data")
            if st.button("🔄 Try Again"):
                st.session_state.clear()
                st.rerun()

if __name__ == "__main__":
    main()
