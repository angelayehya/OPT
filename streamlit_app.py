import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Vision Health Checker", page_icon="👁️", layout="wide")

st.title("👁️ Vision Health Checker")
st.write("Assess whether you might need to see an optometrist based on common vision problems and symptoms.")

# Initialize session state for tracking responses
if 'responses' not in st.session_state:
    st.session_state.responses = {}

# Create tabs for different assessment sections
tab1, tab2, tab3 = st.tabs(["Vision Symptoms", "Eye Health", "Results"])

with tab1:
    st.header("Vision Symptoms Assessment")
    st.write("Please answer the following questions about your vision:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        blur_distance = st.radio(
            "Do you have trouble seeing things at a distance?",
            options=["No", "Occasionally", "Frequently"],
            key="blur_distance"
        )
        
        blur_close = st.radio(
            "Do you have trouble seeing things up close?",
            options=["No", "Occasionally", "Frequently"],
            key="blur_close"
        )
        
        eye_strain = st.radio(
            "Do you experience eye strain or fatigue during/after screen time?",
            options=["No", "Occasionally", "Frequently"],
            key="eye_strain"
        )
    
    with col2:
        headaches = st.radio(
            "Do you suffer from frequent headaches?",
            options=["No", "Occasionally", "Frequently"],
            key="headaches"
        )
        
        squinting = st.radio(
            "Do you find yourself squinting to see clearly?",
            options=["No", "Occasionally", "Frequently"],
            key="squinting"
        )
        
        night_vision = st.radio(
            "Do you have difficulty seeing at night or in low light?",
            options=["No", "Occasionally", "Frequently"],
            key="night_vision"
        )

with tab2:
    st.header("Eye Health Factors")
    st.write("Tell us about your eye health history and habits:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        last_exam = st.selectbox(
            "When was your last eye exam?",
            options=[
                "Never had one",
                "More than 5 years ago",
                "2-5 years ago",
                "1-2 years ago",
                "Within the last year"
            ],
            key="last_exam"
        )
        
        family_history = st.checkbox(
            "Do you have family history of vision problems (myopia, hyperopia, astigmatism)?",
            key="family_history"
        )
        
        screen_time = st.slider(
            "Average daily screen time (hours):",
            min_value=0,
            max_value=16,
            value=8,
            key="screen_time"
        )
    
    with col2:
        floaters = st.checkbox(
            "Do you see floaters or spots in your vision?",
            key="floaters"
        )
        
        flashes = st.checkbox(
            "Do you see flashes of light?",
            key="flashes"
        )
        
        dry_eyes = st.checkbox(
            "Do you experience dry or irritated eyes?",
            key="dry_eyes"
        )
        
        contact_wearer = st.checkbox(
            "Are you a contact lens wearer?",
            key="contact_wearer"
        )

with tab3:
    st.header("Vision Assessment Results")
    
    if st.button("Generate Report", type="primary"):
        # Calculate risk score
        risk_score = 0
        risk_factors = []
        
        # Symptoms scoring
        symptom_weights = {
            "blur_distance": {"Occasionally": 1, "Frequently": 3},
            "blur_close": {"Occasionally": 1, "Frequently": 3},
            "eye_strain": {"Occasionally": 2, "Frequently": 4},
            "headaches": {"Occasionally": 1, "Frequently": 2},
            "squinting": {"Occasionally": 2, "Frequently": 3},
            "night_vision": {"Occasionally": 2, "Frequently": 3}
        }
        
        for key, weights in symptom_weights.items():
            response = st.session_state.get(key, "No")
            if response in weights:
                risk_score += weights[response]
                if response != "No":
                    risk_factors.append(f"{key.replace('_', ' ').title()}: {response}")
        
        # Health factors scoring
        if st.session_state.get("last_exam", "") in ["Never had one", "More than 5 years ago"]:
            risk_score += 2
            risk_factors.append("No recent eye exam")
        
        if st.session_state.get("family_history", False):
            risk_score += 2
            risk_factors.append("Family history of vision problems")
        
        if st.session_state.get("screen_time", 0) > 8:
            risk_score += 1
            risk_factors.append(f"High screen time: {st.session_state.get('screen_time')} hours/day")
        
        if st.session_state.get("floaters", False) or st.session_state.get("flashes", False):
            risk_score += 3
            risk_factors.append("Floaters or flashes observed")
        
        if st.session_state.get("dry_eyes", False):
            risk_score += 1
            risk_factors.append("Dry eyes")
        
        # Determine recommendation
        if risk_score >= 12:
            recommendation = "🔴 HIGH PRIORITY"
            advice = "You should schedule an eye examination with an optometrist as soon as possible. Several symptoms suggest you may benefit from professional vision correction or evaluation."
            color = "#ff4444"
        elif risk_score >= 7:
            recommendation = "🟡 MODERATE PRIORITY"
            advice = "Consider scheduling an eye exam in the near future. While your symptoms are not urgent, professional evaluation would be beneficial."
            color = "#ffaa00"
        else:
            recommendation = "🟢 LOW PRIORITY"
            advice = "Your current symptoms suggest you may not urgently need an eye exam, but regular check-ups (every 1-2 years) are still recommended for eye health maintenance."
            color = "#44aa44"
        
        # Display results
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.metric("Risk Score", f"{risk_score}/30")
        
        with col2:
            st.markdown(f"### {recommendation}")
        
        st.info(advice)
        
        if risk_factors:
            st.subheader("Key Factors Identified:")
            for i, factor in enumerate(risk_factors, 1):
                st.write(f"{i}. {factor}")
        
        st.divider()
        
        st.subheader("📋 Recommendations:")
        
        if risk_score >= 12:
            st.write("""
            - **Schedule an appointment immediately** with a local optometrist or ophthalmologist
            - If you cannot get an appointment soon, consider visiting an urgent care center
            - Keep a symptom diary noting when symptoms occur and their severity
            - Avoid activities that strain your eyes until evaluated
            """)
        elif risk_score >= 7:
            st.write("""
            - Schedule an eye exam within 1-2 months
            - In the meantime, take regular breaks from screens (20-20-20 rule: every 20 min, look 20 ft away for 20 sec)
            - Ensure proper lighting when reading or working
            - Use artificial tears if experiencing dry eyes
            """)
        else:
            st.write("""
            - Schedule regular eye exams every 1-2 years
            - Follow the 20-20-20 rule for screen time
            - Maintain good eye hygiene
            - Wear UV protection sunglasses outdoors
            - If new symptoms develop, don't wait for your next scheduled exam
            """)
        
        st.divider()
        st.caption(f"Assessment completed on {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        st.caption("⚠️ **Disclaimer**: This tool is for informational purposes only and not a substitute for professional medical advice. Always consult with a qualified eye care professional for diagnosis and treatment.")
