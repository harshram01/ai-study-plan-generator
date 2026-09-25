import streamlit as st
import matplotlib.pyplot as plt
from typing import Dict

from models import StudentProfile, SubjectScore, StudyRecommendation
from engine import generate_study_plan
from visuals import plot_performance_gap, plot_hours_allocation
from pdf_generator import create_study_plan_pdf

# --- Page Configuration ---
st.set_page_config(
    page_title="AI Study Recommender",
    page_icon="📚",
    layout="wide"
)

st.title("📚 Student Performance & Study Recommendation System")
st.caption("Personalized Academic Analytics & Timetable Generator powered by LangChain & Groq")

# --- Initialize Session State ---
if "subjects_data" not in st.session_state:
    st.session_state.subjects_data = {
        "Data Structures": {"current": 54.0, "target": 75.0, "weak": "Dynamic Programming, Trees"},
        "Databases": {"current": 78.0, "target": 80.0, "weak": "Indexing, Transactions"},
        "Networks": {"current": 62.0, "target": 70.0, "weak": "Subnetting, TCP"}
    }

if "recommendation_result" not in st.session_state:
    st.session_state.recommendation_result = None

if "last_profile" not in st.session_state:
    st.session_state.last_profile = None

# --- Sidebar Configuration ---
with st.sidebar:
    st.header("Student Profile Settings")
    student_id = st.text_input("Student ID", value="STD-18048")
    hours = st.slider("Available Study Hours / Week", min_value=2, max_value=40, value=12, step=1)
    
    st.divider()
    st.subheader("Add New Subject")
    new_sub_name = st.text_input("Subject Name")
    if st.button("➕ Add Subject") and new_sub_name:
        clean_name = new_sub_name.strip()
        if clean_name and clean_name not in st.session_state.subjects_data:
            st.session_state.subjects_data[clean_name] = {
                "current": 50.0,
                "target": 75.0,
                "weak": ""
            }
            st.rerun()

# --- Subject Performance Inputs ---
st.subheader("Academic Performance Input")

subject_entries: Dict[str, SubjectScore] = {}
num_subjects = len(st.session_state.subjects_data)

if num_subjects > 0:
    cols = st.columns(min(num_subjects, 3))
    for idx, (sub_name, sub_info) in enumerate(st.session_state.subjects_data.items()):
        with cols[idx % 3]:
            st.markdown(f"### {sub_name}")
            curr = st.number_input(
                f"Current Score (%)",
                min_value=0.0,
                max_value=100.0,
                value=float(sub_info["current"]),
                key=f"score_curr_{idx}"
            )
            target = st.number_input(
                f"Target Score (%)",
                min_value=0.0,
                max_value=100.0,
                value=float(sub_info["target"]),
                key=f"score_targ_{idx}"
            )
            weak_str = st.text_area(
                "Identified Weak Areas (comma-separated)",
                value=str(sub_info["weak"]),
                key=f"weak_areas_{idx}"
            )
            
            weak_list = [w.strip() for w in weak_str.split(",") if w.strip()]
            subject_entries[sub_name] = SubjectScore(
                current_score=curr,
                target_score=target,
                weak_areas=weak_list
            )
else:
    st.info("No subjects added yet. Please use the sidebar to add a subject.")

st.divider()

# --- Visual Performance Gap Chart ---
if subject_entries:
    st.subheader("📊 Performance Gap Overview")
    fig_gap = plot_performance_gap(subject_entries)
    st.pyplot(fig_gap)
    plt.close(fig_gap)

# --- Plan Generation Trigger ---
if st.button("🚀 Generate Personalized Study Plan", type="primary", use_container_width=True):
    if not subject_entries:
        st.warning("Please configure at least one subject before generating a plan.")
    else:
        profile = StudentProfile(
            student_id=student_id,
            available_hours_per_week=float(hours),
            subjects=subject_entries
        )
        
        with st.spinner("Analyzing score gaps, identifying priority topics, and generating schedule..."):
            try:
                result = generate_study_plan(profile)
                st.session_state.recommendation_result = result
                st.session_state.last_profile = profile
            except Exception as e:
                st.error(f"Failed to generate study plan: {e}")

# --- Render Plan & PDF Download ---
if st.session_state.recommendation_result and st.session_state.last_profile:
    plan = st.session_state.recommendation_result
    profile_data = st.session_state.last_profile

    st.divider()

    # Verify type-safe response structure
    if hasattr(plan, "diagnostic_summary") and hasattr(plan, "weekly_schedule"):
        # PDF Export Action
        pdf_bytes = create_study_plan_pdf(profile_data, plan)
        st.download_button(
            label="📥 Download Timetable Report as PDF",
            data=pdf_bytes,
            file_name=f"Study_Plan_{profile_data.student_id}.pdf",
            mime="application/pdf"
        )

        col_diag, col_chart = st.columns([1, 1])

       # --- Render Plan & PDF Download ---
plan = st.session_state.get("recommendation_result")
profile_data = st.session_state.get("last_profile")

if plan is not None and profile_data is not None:
    if hasattr(plan, "diagnostic_summary") and hasattr(plan, "weekly_schedule"):
        # PDF Export
        pdf_bytes = create_study_plan_pdf(profile_data, plan)
        st.download_button(
            label="📥 Download Timetable Report as PDF",
            data=pdf_bytes,
            file_name=f"Study_Plan_{getattr(profile_data, 'student_id', 'plan')}.pdf",
            mime="application/pdf"
        )

        col_diag, col_chart = st.columns([1, 1])

        with col_diag:
            st.subheader("1. Diagnostic Summary")
            st.info(getattr(plan, "diagnostic_summary", ""))

            st.subheader("2. Priority Remediation Topics")
            for topic in getattr(plan, "priority_topics", []):
                st.warning(f"⚠️ {topic}")

        with col_chart:
            st.subheader("Time Allocation Breakdown")
            fig_alloc = plot_hours_allocation(getattr(plan, "weekly_schedule", []))
            st.pyplot(fig_alloc)
            plt.close(fig_alloc)

        # Weekly Schedule Table
        st.subheader("3. Recommended Weekly Timetable")
        schedule_table = [
            {
                "Day": getattr(item, "day", ""),
                "Subject": getattr(item, "subject", ""),
                "Topic": getattr(item, "topic", ""),
                "Hours": f"{getattr(item, 'duration_hours', '')} hrs",
                "Action Task": getattr(item, "recommended_action", "")
            }
            for item in getattr(plan, "weekly_schedule", [])
        ]
        st.dataframe(schedule_table, use_container_width=True)

        # Pedagogical Tips
        tips = getattr(plan, "study_tips", [])
        if isinstance(tips, list) and tips:
            st.subheader("4. Pedagogical Strategies & Tips")
            for tip in tips:
                st.write(f"• {tip}")