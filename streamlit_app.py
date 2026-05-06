import streamlit as st
import os
from datetime import datetime
from openai import OpenAI

# Configure page
st.set_page_config(page_title="Vision Health Checker", page_icon="👁️", layout="wide")

# Initialize OpenAI client
@st.cache_resource
def get_openai_client():
    api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        st.error("⚠️ OpenAI API key not found. Please add it to your secrets.")
        st.stop()
    return OpenAI(api_key=api_key)

# Constants
HIGH_PRIORITY_THRESHOLD = 12
MODERATE_PRIORITY_THRESHOLD = 7
MAX_RISK_SCORE = 30

SYMPTOM_WEIGHTS = {
    "blur_distance": {"Occasionally": 1, "Frequently": 3},
    "blur_close": {"Occasionally": 1, "Frequently": 3},
    "eye_strain": {"Occasionally": 2, "Frequently": 4},
    "headaches": {"Occasionally": 1, "Frequently": 2},
    "squinting": {"Occasionally": 2, "Frequently": 3},
    "night_vision": {"Occasionally": 2, "Frequently": 3}
}

st.title("👁️ Vision Health Checker")
st.write("Assess whether you might need to see an optometrist based on common vision problems and symptoms.")

# Initialize session state
if 'responses' not in st.session_state:
    st.session_state.responses = {}
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs(["Vision Symptoms", "Eye Health", "Results", "AI Assistant"])

with tab1:
    st.header("Vision Symptoms Assessment")
    st.write("Please answer the following questions about your vision:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.session_state.blur_distance = st.radio(
            "Do you have trouble seeing things at a distance?",
            options=["No", "Occasionally", "Frequently"],
            key="blur_distance"
        )
        
        st.session_state.blur_close = st.radio(
            "Do you have trouble seeing things up close?",
            options=["No", "Occasionally", "Frequently"],
            key="blur_close"
        )
        
        st.session_state.eye_strain = st.radio(
            "Do you experience eye strain or fatigue during/after screen time?",
            options=["No", "Occasionally", "Frequently"],
            key="eye_strain"
        )
    
    with col2:
        st.session_state.headaches = st.radio(
            "Do you suffer from frequent headaches?",
            options=["No", "Occasionally", "Frequently"],
            key="headaches"
        )
        
        st.session_state.squinting = st.radio(
            "Do you find yourself squinting to see clearly?",
            options=["No", "Occasionally", "Frequently"],
            key="squinting"
        )
        
        st.session_state.night_vision = st.radio(
            "Do you have difficulty seeing at night or in low light?",
            options=["No", "Occasionally", "Frequently"],
            key="night_vision"
        )

with tab2:
    st.header("Eye Health Factors")
    st.write("Tell us about your eye health history and habits:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.session_state.last_exam = st.selectbox(
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
        
        st.session_state.family_history = st.checkbox(
            "Do you have family history of vision problems (myopia, hyperopia, astigmatism)?",
            key="family_history"
        )
        
        st.session_state.screen_time = st.slider(
            "Average daily screen time (hours):",
            min_value=0,
            max_value=16,
            value=8,
            key="screen_time"
        )
    
    with col2:
        st.session_state.floaters = st.checkbox(
            "Do you see floaters or spots in your vision?",
            key="floaters"
        )
        
        st.session_state.flashes = st.checkbox(
            "Do you see flashes of light?",
            key="flashes"
        )
        
        st.session_state.dry_eyes = st.checkbox(
            "Do you experience dry or irritated eyes?",
            key="dry_eyes"
        )
        
        st.session_state.contact_wearer = st.checkbox(
            "Are you a contact lens wearer?",
            key="contact_wearer"
        )

with tab3:
    st.header("Vision Assessment Results")
    
    if st.button("Generate Report", type="primary"):
        # Calculate risk score
        risk_score = 0
        risk_factors = []
        symptoms_details = []
        
        # Symptoms scoring
        for key, weights in SYMPTOM_WEIGHTS.items():
            response = st.session_state.get(key, "No")
            if response in weights:
                risk_score += weights[response]
                if response != "No":
                    risk_factors.append(f"{key.replace('_', ' ').title()}: {response}")
                    symptoms_details.append({"symptom": key, "severity": response})
        
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
        if risk_score >= HIGH_PRIORITY_THRESHOLD:
            recommendation = "🔴 HIGH PRIORITY"
            advice = "You should schedule an eye examination with an optometrist as soon as possible."
            priority_level = "high"
        elif risk_score >= MODERATE_PRIORITY_THRESHOLD:
            recommendation = "🟡 MODERATE PRIORITY"
            advice = "Consider scheduling an eye exam in the near future."
            priority_level = "moderate"
        else:
            recommendation = "🟢 LOW PRIORITY"
            advice = "Your symptoms suggest you may not urgently need an eye exam."
            priority_level = "low"
        
        # Display results
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.metric("Risk Score", f"{risk_score}/{MAX_RISK_SCORE}")
        
        with col2:
            st.markdown(f"### {recommendation}")
        
        st.info(advice)
        
        if risk_factors:
            st.subheader("Key Factors Identified:")
            for i, factor in enumerate(risk_factors, 1):
                st.write(f"{i}. {factor}")
        
        st.divider()
        
        # AI-Powered Personalized Insights
        st.subheader("🤖 AI-Powered Personalized Insights")
        
        with st.spinner("Generating personalized analysis..."):
            try:
                client = get_openai_client()
                
                # Create comprehensive prompt
                prompt = f"""Based on the following vision health assessment data, provide a comprehensive personalized analysis:

Risk Score: {risk_score}/30 (Priority: {priority_level})
Identified Factors: {', '.join(risk_factors)}
Screen Time: {st.session_state.get('screen_time', 0)} hours/day
Last Eye Exam: {st.session_state.get('last_exam', 'Unknown')}
Family History: {'Yes' if st.session_state.get('family_history', False) else 'No'}
Contact Lens Wearer: {'Yes' if st.session_state.get('contact_wearer', False) else 'No'}

Please provide:
1. A brief personalized summary of their vision health status
2. Specific explanations for their identified risk factors
3. Customized lifestyle recommendations based on their symptoms
4. When they should see a professional (specific timeline)
5. Preventive measures they can take immediately

Keep the tone professional yet approachable. Make it specific to their situation, not generic."""

                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    max_tokens=800
                )
                
                ai_insights = response.choices[0].message.content
                st.write(ai_insights)
                
                # Store for chat assistant
                st.session_state.last_assessment = {
                    "risk_score": risk_score,
                    "factors": risk_factors,
                    "priority": priority_level,
                    "insights": ai_insights
                }
                
            except Exception as e:
                st.error(f"Error generating AI insights: {str(e)}")
        
        st.divider()
        
        st.subheader("📋 Standard Recommendations:")
        
        if risk_score >= HIGH_PRIORITY_THRESHOLD:
            st.write("""
            - **Schedule an appointment immediately** with a local optometrist or ophthalmologist
            - If you cannot get an appointment soon, consider visiting an urgent care center
            - Keep a symptom diary noting when symptoms occur and their severity
            - Avoid activities that strain your eyes until evaluated
            """)
        elif risk_score >= MODERATE_PRIORITY_THRESHOLD:
            st.write("""
            - Schedule an eye exam within 1-2 months
            - Take regular breaks from screens (20-20-20 rule: every 20 min, look 20 ft away for 20 sec)
            - Ensure proper lighting when reading or working
            - Use artificial tears if experiencing dry eyes
            """)
        else:
            st.write("""
            - Schedule regular eye exams every 1-2 years
            - Follow the 20-20-20 rule for screen time
            - Maintain good eye hygiene
            - Wear UV protection sunglasses outdoors
            - If new symptoms develop, seek professional advice
            """)
        
        st.divider()
        st.caption(f"Assessment completed on {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        st.caption("⚠️ **Disclaimer**: This tool is for informational purposes only and not a substitute for professional medical advice. Always consult with a qualified eye care professional for medical diagnosis and treatment recommendations.")

with tab4:
    st.header("💬 Vision Health AI Assistant")
    st.write("Ask questions about vision health, symptoms, or recommendations based on your assessment.")
    
    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Chat input
    user_input = st.chat_input("Ask your vision health question...")
    
    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        with st.chat_message("user"):
            st.write(user_input)
        
        # Generate AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    client = get_openai_client()
                    
                    # Context from assessment if available
                    context = ""
                    if 'last_assessment' in st.session_state:
                        context = f"\nUser's Recent Assessment: Risk Level: {st.session_state.last_assessment['priority']}, Risk Factors: {', '.join(st.session_state.last_assessment['factors'])}"
                    
                    system_prompt = """You are a knowledgeable vision health assistant with expertise in optometry and eye care. 
                    Provide accurate, helpful information about vision problems, symptoms, and eye health practices.
                    Always remind users to consult with a professional eye care provider for medical advice.
                    Keep responses concise but informative."""
                    
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": system_prompt + context},
                            {"role": "user", "content": user_input}
                        ],
                        temperature=0.7,
                        max_tokens=500
                    )
                    
                    assistant_message = response.choices[0].message.content
                    st.write(assistant_message)
                    st.session_state.chat_history.append({"role": "assistant", "content": assistant_message})
                    
                except Exception as e:
                    st.error(f"Error: {str(e)}")
