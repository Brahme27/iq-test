"""
MISIC Web Application
=====================
Malin's Intelligence Scale for Indian Children
A medical-grade psychometric testing application.

Run with: streamlit run app.py
"""

import streamlit as st
from streamlit_autorefresh import st_autorefresh
from datetime import date, datetime
from typing import Optional, Dict
import time
import os

from models import (
    PatientProfile, TestSession, SubtestResult, SubtestType, TestStage,
    VERBAL_SUBTESTS, PERFORMANCE_SUBTESTS, IQClassification
)
from calculator import TQLookup, AgeCalculator, IQCalculator, check_discontinue
from subtests import (
    get_subtest_definition, get_verbal_subtests, get_performance_subtests,
    SubtestDefinition, SubtestItem
)
from ai_grader import create_grader, AIGraderConfig
from report_generator import ReportGenerator


# ==========================================
# Page Configuration
# ==========================================

st.set_page_config(
    page_title="MISIC Assessment",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ==========================================
# Custom CSS - Dark Mode Compatible
# ==========================================

st.markdown("""
<style>
    /* Force dark theme consistency */
    .stApp {
        background-color: #0e1117;
    }
    
    /* Main headers - bright colors for visibility */
    .main-header {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        margin-bottom: 0.5rem;
        padding: 1rem 0;
    }
    
    .sub-header {
        font-size: 1.1rem;
        color: #a0aec0;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    /* IQ Score boxes with gradients */
    .score-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 16px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
    }
    
    .score-value {
        font-size: 2.5rem;
        font-weight: 800;
        color: #ffffff;
    }
    
    .score-label {
        font-size: 0.95rem;
        color: rgba(255, 255, 255, 0.9);
        margin-top: 0.25rem;
    }
    
    /* Question card - dark themed, NO white */
    .question-card {
        background: linear-gradient(135deg, #1a1f35 0%, #252b48 100%);
        padding: 1.5rem 2rem;
        border-radius: 16px;
        border: 1px solid rgba(102, 126, 234, 0.3);
        margin: 1rem 0;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }
    
    /* Question text - BRIGHT and readable */
    .question-text {
        font-size: 1.4rem;
        font-weight: 600;
        color: #f0f4ff;
        margin: 0.5rem 0;
        line-height: 1.6;
        text-shadow: 0 1px 2px rgba(0,0,0,0.3);
    }
    
    /* Timer display - high contrast */
    .timer-display {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1a1a2e;
        text-align: center;
        padding: 1rem 2rem;
        background: linear-gradient(135deg, #ffeaa7 0%, #fdcb6e 100%);
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(253, 203, 110, 0.4);
    }
    
    /* AI suggestion box */
    .ai-suggestion {
        background: linear-gradient(135deg, #0984e3 0%, #74b9ff 100%);
        padding: 1.25rem;
        border-radius: 12px;
        color: white;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(9, 132, 227, 0.4);
    }
    
    /* Progress indicator */
    .progress-indicator {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 20px;
        padding: 0.4rem 1.2rem;
        font-size: 0.9rem;
        font-weight: 600;
        display: inline-block;
        box-shadow: 0 2px 10px rgba(102, 126, 234, 0.4);
    }
    
    /* Section headers */
    .section-header {
        color: #a78bfa;
        font-size: 1.1rem;
        font-weight: 600;
        margin: 1.5rem 0 0.75rem 0;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Override Streamlit's default input styling for dark mode */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background-color: #1e2433 !important;
        color: #f0f4ff !important;
        border: 1px solid #3d4663 !important;
        border-radius: 8px !important;
    }
    
    .stTextInput > div > div > input::placeholder,
    .stTextArea > div > div > textarea::placeholder {
        color: #6b7280 !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.3) !important;
    }
    
    /* Radio buttons and labels */
    .stRadio > label {
        color: #e2e8f0 !important;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: #1a1f35 !important;
        color: #a78bfa !important;
        border-radius: 8px !important;
    }
    
    /* Button styling */
    .stButton > button {
        border-radius: 10px !important;
        font-weight: 600 !important;
        padding: 0.6rem 1.5rem !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4) !important;
    }
    
    /* Primary button override */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        border: none !important;
        color: white !important;
    }
    
    /* Metric labels */
    [data-testid="stMetricLabel"] {
        color: #a0aec0 !important;
    }
    
    [data-testid="stMetricValue"] {
        color: #f0f4ff !important;
    }
    
    /* Table styling for dark mode */
    .stTable {
        background-color: #1a1f35 !important;
    }
    
    /* Markdown text visibility */
    .stMarkdown p, .stMarkdown li {
        color: #e2e8f0;
    }
    
    /* Success/Warning/Error messages */
    .stSuccess, .stWarning, .stError, .stInfo {
        border-radius: 10px !important;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1f35 0%, #0e1117 100%) !important;
    }
    
    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] .stMarkdown h2 {
        color: #e2e8f0 !important;
    }
    
    /* Progress bar */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%) !important;
    }
    
    /* Hide white backgrounds in expanders */
    .streamlit-expanderContent {
        background-color: #1a1f35 !important;
        border: 1px solid #3d4663 !important;
        border-radius: 0 0 8px 8px !important;
    }
</style>
""", unsafe_allow_html=True)


# ==========================================
# Session State Initialization
# ==========================================

def init_session_state():
    """Initialize session state variables."""
    if 'stage' not in st.session_state:
        st.session_state.stage = TestStage.REGISTRATION
    if 'patient' not in st.session_state:
        st.session_state.patient = None
    if 'session' not in st.session_state:
        st.session_state.session = None
    if 'current_subtest_index' not in st.session_state:
        st.session_state.current_subtest_index = 0
    if 'current_item_index' not in st.session_state:
        st.session_state.current_item_index = 0
    if 'item_scores' not in st.session_state:
        st.session_state.item_scores = {}
    if 'timer_start' not in st.session_state:
        st.session_state.timer_start = None
    if 'api_key' not in st.session_state:
        st.session_state.api_key = ""
    if 'tq_lookup' not in st.session_state:
        st.session_state.tq_lookup = TQLookup()
    if 'ai_grader' not in st.session_state:
        st.session_state.ai_grader = None
    if 'show_ai_suggestion' not in st.session_state:
        st.session_state.show_ai_suggestion = False
    if 'current_ai_response' not in st.session_state:
        st.session_state.current_ai_response = None
    if 'subtest_complete' not in st.session_state:
        st.session_state.subtest_complete = False
    if 'discontinue_reason' not in st.session_state:
        st.session_state.discontinue_reason = None


init_session_state()


# ==========================================
# Sidebar Configuration
# ==========================================

def render_sidebar():
    """Render the sidebar with configuration and progress."""
    with st.sidebar:
        st.markdown("## ⚙️ Configuration")
        
        # API Key input
        api_key = st.text_input(
            "Gemini API Key (for AI Grader)",
            value=st.session_state.api_key,
            type="password",
            help="Optional: Enter your Google Gemini API key to enable AI-assisted scoring"
        )
        
        if api_key != st.session_state.api_key:
            st.session_state.api_key = api_key
            if api_key:
                st.session_state.ai_grader = create_grader(api_key)
                st.success("✓ AI Grader configured")
            else:
                st.session_state.ai_grader = None
        
        st.markdown("---")
        
        # Progress display
        st.markdown("## 📊 Progress")
        
        stage_names = {
            TestStage.REGISTRATION: "1. Registration",
            TestStage.VERBAL: "2. Verbal Scale",
            TestStage.PERFORMANCE: "3. Performance Scale",
            TestStage.REPORT: "4. Report"
        }
        
        current_stage = st.session_state.stage
        for stage, name in stage_names.items():
            if stage == current_stage:
                st.markdown(f"**→ {name}**")
            elif stage.value < current_stage.value:
                st.markdown(f"✓ {name}")
            else:
                st.markdown(f"○ {name}")
        
        st.markdown("---")
        
        # Patient info (if registered)
        if st.session_state.patient:
            st.markdown("## 👤 Patient")
            p = st.session_state.patient
            st.markdown(f"**{p.name}**")
            st.markdown(f"Age: {p.age_display}")
            st.markdown(f"Table Age: {p.table_age} years")
        
        st.markdown("---")
        
        # Reset button
        if st.button("🔄 Start New Session", width="stretch"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()


# ==========================================
# Registration Page
# ==========================================

def render_registration():
    """Render the patient registration form."""
    st.markdown('<h1 class="main-header">🧠 MISIC Assessment</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Malin\'s Intelligence Scale for Indian Children</p>', unsafe_allow_html=True)
    
    st.markdown("### Patient Registration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        patient_id = st.text_input("Patient ID *", placeholder="e.g., PAT001")
        name = st.text_input("Full Name *", placeholder="Enter patient's full name")
        dob = st.date_input(
            "Date of Birth *",
            min_value=date(2005, 1, 1),
            max_value=date.today(),
            value=date(2015, 1, 1)
        )
        gender = st.selectbox("Gender", ["", "Male", "Female", "Other"])
    
    with col2:
        test_date = st.date_input("Test Date *", value=date.today())
        education = st.text_input("Education/Grade", placeholder="e.g., Class 5")
        examiner = st.text_input("Examiner Name", placeholder="Your name")
        notes = st.text_area("Additional Notes", placeholder="Any relevant observations...")
    
    # Age calculation preview
    if dob and test_date:
        age_display = AgeCalculator.format_age(dob, test_date)
        table_age = AgeCalculator.get_table_age(dob, test_date)
        is_valid = AgeCalculator.is_valid_age(dob, test_date)
        
        st.markdown("---")
        st.markdown("### Age Calculation Preview")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Chronological Age", age_display)
        with col2:
            st.metric("Table Age (for scoring)", f"{table_age} years")
        with col3:
            if is_valid:
                st.success("✓ Valid age range (6-15)")
            else:
                st.error("✗ Outside valid range (6-15)")
    
    st.markdown("---")
    
    # Submit button
    if st.button("Begin Assessment →", type="primary", width="stretch"):
        if not patient_id or not name:
            st.error("Please fill in all required fields (marked with *)")
        elif not AgeCalculator.is_valid_age(dob, test_date):
            st.error("Patient age must be between 6 and 15 years")
        else:
            # Create patient and session
            patient = PatientProfile(
                patient_id=patient_id,
                name=name,
                date_of_birth=dob,
                test_date=test_date,
                gender=gender if gender else None,
                education=education if education else None,
                examiner_name=examiner if examiner else None,
                notes=notes if notes else None
            )
            
            session = TestSession(patient=patient)
            
            st.session_state.patient = patient
            st.session_state.session = session
            st.session_state.stage = TestStage.VERBAL
            st.session_state.current_subtest_index = 0
            st.session_state.current_item_index = 0
            st.session_state.item_scores = {}
            
            st.rerun()


# ==========================================
# Subtest Administration
# ==========================================

def render_verbal_subtests():
    """Render the verbal subtest administration."""
    session = st.session_state.session
    patient = st.session_state.patient
    
    verbal_defs = get_verbal_subtests()
    current_idx = st.session_state.current_subtest_index
    
    if current_idx >= len(verbal_defs):
        # Move to performance subtests
        st.session_state.stage = TestStage.PERFORMANCE
        st.session_state.current_subtest_index = 0
        st.session_state.current_item_index = 0
        st.session_state.item_scores = {}
        st.rerun()
        return
    
    subtest_def = verbal_defs[current_idx]
    render_subtest(subtest_def, is_verbal=True)


def render_performance_subtests():
    """Render the performance subtest administration."""
    session = st.session_state.session
    patient = st.session_state.patient
    
    perf_defs = get_performance_subtests()
    current_idx = st.session_state.current_subtest_index
    
    if current_idx >= len(perf_defs):
        # Move to report
        st.session_state.stage = TestStage.REPORT
        st.rerun()
        return
    
    subtest_def = perf_defs[current_idx]
    render_subtest(subtest_def, is_verbal=False)


def render_subtest(subtest_def: SubtestDefinition, is_verbal: bool):
    """Render a single subtest."""
    session = st.session_state.session
    patient = st.session_state.patient
    
    # Header
    scale_name = "Verbal" if is_verbal else "Performance"
    st.markdown(f"### {scale_name} Scale: {subtest_def.name}")
    
    # Progress
    items = subtest_def.items
    current_item_idx = st.session_state.current_item_index
    
    progress = (current_item_idx) / len(items)
    st.progress(progress)
    st.markdown(f'<span class="progress-indicator">Item {current_item_idx + 1} of {len(items)}</span>', 
                unsafe_allow_html=True)
    
    # Instructions (collapsible)
    with st.expander("📋 Administration Instructions"):
        st.markdown(subtest_def.instructions)
    
    st.markdown("---")
    
    # Check if subtest is marked as complete (from discontinuation or all items done)
    if st.session_state.subtest_complete:
        finalize_subtest(subtest_def, is_verbal)
    elif current_item_idx < len(items):
        item = items[current_item_idx]
        render_item(subtest_def, item, is_verbal)
    else:
        # All items completed naturally
        st.session_state.subtest_complete = True
        st.rerun()


def generate_picture_completion_image(item_notes: str, item_number: int) -> str:
    """Generate a prompt for Picture Completion images."""
    # Extract the missing part description
    return f"""Create a simple, clear educational illustration for a children's intelligence test.
Show: {item_notes}
Requirements:
- Clean, colorful cartoon-style drawing
- Suitable for children aged 6-15 years
- The missing part should be obviously absent from the picture
- White or light background
- No text or labels in the image
- High quality, child-friendly illustration"""


def render_item(subtest_def: SubtestDefinition, item: SubtestItem, is_verbal: bool):
    """Render a single test item."""
    
    # Special handling for Picture Completion - show the image
    if subtest_def.subtest_type == SubtestType.PICTURE_COMPLETION:
        # Display question asking what's missing
        st.markdown(f'''
        <div class="question-card">
            <p class="question-text">Q{item.number}: Look at this picture. What important part is missing?</p>
        </div>
        ''', unsafe_allow_html=True)
        
        # Map item numbers to image filenames
        image_map = {
            1: "comb.png",
            2: "door.png",
            3: "eyebros.png",
            4: "legmiss.png",
            5: "withoutears.png",
            6: "clock.png",
            7: "scissor.png",
            8: "nose.png",
            9: "shoes.png",
            10: "cat.png",
            11: "umbrella.png",
            12: "nopedals.png",
            13: "peacock.png",
            14: "telephone.png",
            15: "leaf.png",
            16: "fish.png",
            17: "staircase.png",
            18: "elephant.png",
            19: "carwithoutheadlights.png",
            20: "thermometer.png"
        }
        
        if item.number in image_map:
            import os
            img_path = os.path.join("images", image_map[item.number])
            if os.path.exists(img_path):
                st.image(img_path, caption=f"Picture {item.number}", width="stretch")
            else:
                st.error(f"Image not found: {img_path}")
                st.info(f"**Description:** {item.notes}")
        else:
            st.warning(f"No image mapping for item {item.number}")
            st.info(f"**Description:** {item.notes}")

    else:
        # Regular question display for non-picture items
        st.markdown(f'''
        <div class="question-card">
            <p class="question-text">Q{item.number}: {item.question}</p>
        </div>
        ''', unsafe_allow_html=True)
    
    # Show scoring criteria
    with st.expander("📋 Scoring Criteria"):
        for score, criteria in item.score_criteria.items():
            st.markdown(f"**Score {score}:** {criteria}")
    
    # Timer for timed items
    if item.time_limit:
        render_timer(item.time_limit)
    
    # AI Grader for verbal subtests
    if is_verbal and st.session_state.ai_grader and item.max_score > 0:
        render_ai_grader(subtest_def, item)
    
    # Response input section
    st.markdown('<p class="section-header">📝 Record Response</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        response = st.text_area(
            "Child's Response (optional)",
            placeholder="Type the child's verbal response here...",
            key=f"response_{item.number}"
        )
    
    with col2:
        score_options = list(range(item.max_score + 1))
        score = st.radio(
            "Score",
            options=score_options,
            key=f"score_{item.number}",
            horizontal=True
        )
    
    
    # Navigation buttons
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.session_state.current_item_index > 0:
            if st.button("← Previous", width="stretch"):
                st.session_state.current_item_index -= 1
                st.rerun()
    
    with col2:
        if st.button("Skip Item", width="stretch"):
            st.session_state.item_scores[item.number] = 0
            st.session_state.current_item_index += 1
            st.rerun()
    
    with col3:
        if st.button("Next →", type="primary", width="stretch"):
            st.session_state.item_scores[item.number] = score
            
            # Check discontinuation rule
            scores_list = [st.session_state.item_scores.get(i, 0) 
                          for i in range(1, item.number + 1)]
            should_stop, reason = check_discontinue(subtest_def.subtest_type, scores_list)
            
            if should_stop:
                # Mark subtest as complete and store discontinuation reason
                st.session_state.subtest_complete = True
                st.session_state.discontinue_reason = reason
                st.rerun()
            else:
                st.session_state.current_item_index += 1
                st.rerun()


def render_timer(time_limit: int):
    """Render a live countdown timer with smooth auto-refresh."""
    timer_key = f"timer_{st.session_state.current_item_index}"
    
    if st.session_state.timer_start is None:
        # Show start button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("⏱️ Start Timer", key=f"start_{timer_key}", width="stretch"):
                st.session_state.timer_start = time.time()
                st.rerun()
    else:
        # Use smooth auto-refresh (updates every 1000ms without blinking)
        st_autorefresh(interval=1000, limit=time_limit + 10, key=f"autorefresh_{timer_key}")
        
        elapsed = time.time() - st.session_state.timer_start
        remaining = max(0, time_limit - int(elapsed))
        
        if remaining > 0:
            mins, secs = divmod(remaining, 60)
            
            # Color changes as time runs out
            if remaining <= 10:
                bg_color = "linear-gradient(135deg, #e74c3c 0%, #c0392b 100%)"
                text_color = "white"
                shadow = "rgba(231, 76, 60, 0.5)"
            elif remaining <= 30:
                bg_color = "linear-gradient(135deg, #f39c12 0%, #e67e22 100%)"
                text_color = "#1a1a2e"
                shadow = "rgba(243, 156, 18, 0.4)"
            else:
                bg_color = "linear-gradient(135deg, #ffeaa7 0%, #fdcb6e 100%)"
                text_color = "#1a1a2e"
                shadow = "rgba(253, 203, 110, 0.4)"
            
            st.markdown(f'''
            <div style="
                background: {bg_color};
                padding: 1.2rem 2rem;
                border-radius: 12px;
                text-align: center;
                margin: 1rem 0;
                box-shadow: 0 4px 15px {shadow};
            ">
                <span style="font-size: 2.5rem; font-weight: 700; color: {text_color};">
                    ⏱️ {mins:02d}:{secs:02d}
                </span>
            </div>
            ''', unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("⏹️ Stop Timer", key=f"stop_{timer_key}", width="stretch"):
                    st.session_state.timer_start = None
                    st.rerun()
            
        else:
            # Time is up!
            st.markdown('''
            <div style="
                background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
                padding: 1.2rem 2rem;
                border-radius: 12px;
                text-align: center;
                margin: 1rem 0;
                box-shadow: 0 4px 15px rgba(231, 76, 60, 0.5);
                animation: pulse 1s infinite;
            ">
                <span style="font-size: 2.5rem; font-weight: 700; color: white;">
                    🔔 TIME UP!
                </span>
            </div>
            <style>
                @keyframes pulse {
                    0%, 100% { transform: scale(1); }
                    50% { transform: scale(1.02); }
                }
            </style>
            ''', unsafe_allow_html=True)
            
            # Auto-reset timer
            st.session_state.timer_start = None


def render_ai_grader(subtest_def: SubtestDefinition, item: SubtestItem):
    """Render the AI grader suggestion panel."""
    with st.expander("🤖 AI Grader Assistant (Advisory Only)"):
        response_key = f"ai_response_{item.number}"
        child_response = st.text_input(
            "Enter child's response for AI analysis:",
            key=response_key
        )
        
        if st.button("Get AI Suggestion", key=f"ai_btn_{item.number}"):
            if child_response:
                grader = st.session_state.ai_grader
                
                # Get scoring criteria
                score_0 = item.score_criteria.get(0, "Incorrect")
                score_1 = item.score_criteria.get(1, "Correct")
                score_2 = item.score_criteria.get(2) if item.max_score >= 2 else None
                
                with st.spinner("Analyzing response..."):
                    result = grader.grade_response(
                        subtest_name=subtest_def.name,
                        item_number=item.number,
                        question=item.question,
                        response=child_response,
                        score_0=score_0,
                        score_1=score_1,
                        score_2=score_2
                    )
                
                st.markdown(f"""
                <div class="ai-suggestion">
                    <strong>Suggested Score: {result.suggested_score}</strong><br>
                    <em>Confidence: {result.confidence}</em><br><br>
                    {result.rationale}
                </div>
                """, unsafe_allow_html=True)
                
                st.info("⚠️ This is a suggestion only. Please confirm the final score based on your clinical judgment.")
            else:
                st.warning("Please enter the child's response first.")


def finalize_subtest(subtest_def: SubtestDefinition, is_verbal: bool):
    """Finalize the current subtest and save results."""
    session = st.session_state.session
    patient = st.session_state.patient
    
    # Show discontinuation reason if applicable
    if st.session_state.discontinue_reason:
        st.warning(f"⚠️ Discontinuation rule met: {st.session_state.discontinue_reason}")
    
    # Calculate raw score
    raw_score = sum(st.session_state.item_scores.values())
    
    # Get TQ
    tq_lookup = st.session_state.tq_lookup
    tq = tq_lookup.get_tq(patient.table_age, subtest_def.subtest_type, raw_score)
    
    # Create result (only if not already saved)
    if subtest_def.subtest_type not in (session.verbal_results if is_verbal else session.performance_results):
        result = SubtestResult(
            subtest_type=subtest_def.subtest_type,
            raw_score=raw_score,
            test_quotient=tq,
            items_attempted=len(st.session_state.item_scores),
            items_correct=sum(1 for s in st.session_state.item_scores.values() if s > 0),
            item_scores=st.session_state.item_scores.copy()
        )
        
        # Save to session
        if is_verbal:
            session.verbal_results[subtest_def.subtest_type] = result
        else:
            session.performance_results[subtest_def.subtest_type] = result
    
    # Show summary
    st.success(f"✓ {subtest_def.name} completed!")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Raw Score", raw_score)
    with col2:
        st.metric("Test Quotient (TQ)", tq if tq else 'N/A')
    
    st.markdown("---")
    
    # Move to next subtest button
    if st.button("Continue to Next Subtest →", type="primary", width="stretch"):
        # Reset state for next subtest
        st.session_state.current_subtest_index += 1
        st.session_state.current_item_index = 0
        st.session_state.item_scores = {}
        st.session_state.subtest_complete = False
        st.session_state.discontinue_reason = None
        st.rerun()


# ==========================================
# Report Page
# ==========================================

def render_report():
    """Render the final report page."""
    session = st.session_state.session
    patient = st.session_state.patient
    tq_lookup = st.session_state.tq_lookup
    
    st.markdown('<h1 class="main-header">📊 Assessment Report</h1>', unsafe_allow_html=True)
    
    # Calculate all scores
    all_raw_scores = {}
    all_tqs = {}
    
    for st_type, result in session.verbal_results.items():
        all_raw_scores[st_type] = result.raw_score
        all_tqs[st_type] = result.test_quotient
    
    for st_type, result in session.performance_results.items():
        all_raw_scores[st_type] = result.raw_score
        all_tqs[st_type] = result.test_quotient
    
    # Calculate IQs
    calculator = IQCalculator(tq_lookup)
    verbal_iq = calculator.calculate_verbal_iq(all_tqs)
    performance_iq = calculator.calculate_performance_iq(all_tqs)
    full_scale_iq = calculator.calculate_full_scale_iq(all_tqs)
    
    # IQ Summary boxes
    st.markdown("### IQ Summary")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="score-box" style="background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);">
            <div class="score-value">{verbal_iq:.1f if verbal_iq else 'N/A'}</div>
            <div class="score-label">Verbal IQ</div>
            <div class="score-label">{IQClassification.classify(verbal_iq) if verbal_iq else ''}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="score-box" style="background: linear-gradient(135deg, #9b59b6 0%, #8e44ad 100%);">
            <div class="score-value">{performance_iq:.1f if performance_iq else 'N/A'}</div>
            <div class="score-label">Performance IQ</div>
            <div class="score-label">{IQClassification.classify(performance_iq) if performance_iq else ''}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="score-box" style="background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%);">
            <div class="score-value">{full_scale_iq:.1f if full_scale_iq else 'N/A'}</div>
            <div class="score-label">Full Scale IQ</div>
            <div class="score-label">{IQClassification.classify(full_scale_iq) if full_scale_iq else ''}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Disparity analysis
    if verbal_iq and performance_iq:
        disparity = verbal_iq - performance_iq
        st.markdown("---")
        st.markdown("### Verbal-Performance Disparity")
        st.metric("Disparity", f"{disparity:+.1f} points")
        
        if abs(disparity) >= 15:
            if disparity > 0:
                st.warning("""
                ⚠️ **Significant Disparity Detected** (Verbal > Performance by 15+ points)
                
                This pattern is common in Indian children and may reflect cultural emphasis on 
                verbal/academic skills. Interpret within the child's educational and cultural context.
                """)
            else:
                st.warning("""
                ⚠️ **Significant Disparity Detected** (Performance > Verbal by 15+ points)
                
                This may indicate stronger visual-spatial abilities relative to verbal skills.
                Consider language background and educational exposure.
                """)
    
    # TQ Chart
    st.markdown("---")
    st.markdown("### Test Quotient Profile")
    
    report_gen = ReportGenerator()
    chart_bytes = report_gen.create_tq_chart(all_tqs)
    st.image(chart_bytes)
    
    # Detailed scores table
    st.markdown("---")
    st.markdown("### Detailed Scores")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Verbal Scale**")
        verbal_data = []
        for st_type in VERBAL_SUBTESTS:
            result = session.verbal_results.get(st_type)
            verbal_data.append({
                "Subtest": st_type.value.replace('_', ' ').title(),
                "Raw Score": result.raw_score if result else 0,
                "TQ": result.test_quotient if result else None
            })
        st.table(verbal_data)
    
    with col2:
        st.markdown("**Performance Scale**")
        perf_data = []
        for st_type in PERFORMANCE_SUBTESTS:
            result = session.performance_results.get(st_type)
            perf_data.append({
                "Subtest": st_type.value.replace('_', ' ').title(),
                "Raw Score": result.raw_score if result else 0,
                "TQ": result.test_quotient if result else None
            })
        st.table(perf_data)
    
    # PDF Export
    st.markdown("---")
    st.markdown("### Export Report")
    
    if st.button("📄 Generate PDF Report", type="primary", width="stretch"):
        try:
            output_path = f"MISIC_Report_{patient.patient_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            
            report_gen.generate_pdf_report(
                session=session,
                tqs=all_tqs,
                verbal_iq=verbal_iq or 0,
                performance_iq=performance_iq or 0,
                full_scale_iq=full_scale_iq or 0,
                output_path=output_path
            )
            
            with open(output_path, 'rb') as f:
                st.download_button(
                    label="⬇️ Download PDF",
                    data=f,
                    file_name=output_path,
                    mime="application/pdf"
                )
            
            st.success(f"✓ Report generated: {output_path}")
            
        except Exception as e:
            st.error(f"Error generating PDF: {str(e)}")


# ==========================================
# Main Application
# ==========================================

def main():
    """Main application entry point."""
    render_sidebar()
    
    stage = st.session_state.stage
    
    if stage == TestStage.REGISTRATION:
        render_registration()
    elif stage == TestStage.VERBAL:
        render_verbal_subtests()
    elif stage == TestStage.PERFORMANCE:
        render_performance_subtests()
    elif stage == TestStage.REPORT:
        render_report()


if __name__ == "__main__":
    main()
