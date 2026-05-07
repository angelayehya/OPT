import streamlit as st
import os
import pandas as pd
from datetime import datetime
from fpdf import FPDF
import io

# Configure page
st.set_page_config(page_title="Vision Health Checker", page_icon="👁️", layout="wide")

# Eye Care Providers Database
EYE_CARE_PROVIDERS = {
    "Beirut": [
        {"Name": "Beirut Eye & ENT Specialist Hospital", "Type": "Eye Hospital", "Specialty": "Surgical / General Ophthalmology"},
        {"Name": "Dr Rabih Saneh Eye Clinic", "Type": "Ophthalmology Clinic", "Specialty": "LASIK / Retina"},
        {"Name": "Eye Care Center Beirut", "Type": "Ophthalmology Clinic", "Specialty": "General Eye Care"},
        {"Name": "Dr Ama Sadaka Clinic", "Type": "Ophthalmology Clinic", "Specialty": "General Ophthalmology"},
        {"Name": "Visique Optometrists", "Type": "Optometry Center", "Specialty": "Vision Testing / Glasses"},
        {"Name": "XENA OPTIC", "Type": "Optometry Center", "Specialty": "Optical / Vision Care"},
        {"Name": "Coté Vue Beirut", "Type": "Optical Center", "Specialty": "Eyewear / Optometry"},
    ],
    "Aley": [
        {"Name": "Aley Eye Center", "Type": "Eye Care Center", "Specialty": "General Ophthalmology"},
        {"Name": "Optique et Vision Aley", "Type": "Optometry Center", "Specialty": "Vision Testing"},
        {"Name": "Eye Wise Optical", "Type": "Optical Center", "Specialty": "Optical / Vision Care"},
        {"Name": "Sharafedin Optic", "Type": "Optical Center", "Specialty": "Glasses / Vision Care"},
    ],
    "Tripoli": [
        {"Name": "Dr Samir G. Farah Clinic", "Type": "Ophthalmology Clinic", "Specialty": "LASIK / Refractive Surgery"},
        {"Name": "Dr Mohamad Nadim Safi Clinic", "Type": "Ophthalmology Clinic", "Specialty": "General Ophthalmology"},
        {"Name": "Nawfal Clinics Tripoli", "Type": "Medical Clinic", "Specialty": "Eye Care / General Medicine"},
    ],
    "Jounieh": [
        {"Name": "Dr Khalil Khalil Eye Clinic", "Type": "Ophthalmology Clinic", "Specialty": "General Ophthalmology"},
        {"Name": "Eye & Ear Hospital International", "Type": "Specialized Hospital", "Specialty": "Eye Surgery / ENT"},
        {"Name": "Nawfal Clinics Jounieh", "Type": "Medical Clinic", "Specialty": "Eye Care / General Medicine"},
    ],
    "Zahle": [
        {"Name": "Clinique Ophtaderm", "Type": "Ophthalmology Clinic", "Specialty": "Ophthalmology / Retina"},
    ],
    "Jbeil": [
        {"Name": "Eye & Ear Hospital International", "Type": "Specialized Hospital", "Specialty": "Eye Surgery / ENT"},
        {"Name": "Dr Khalil Khalil Eye Clinic", "Type": "Ophthalmology Clinic", "Specialty": "General Ophthalmology"},
    ],
    "Nabatieh": [
        {"Name": "Nabatieh Eye Care Center", "Type": "Eye Care Center", "Specialty": "General Eye Care"},
        {"Name": "Al Basar Optical Center", "Type": "Optical Center", "Specialty": "Vision Care"},
        {"Name": "Nabatieh Specialty Clinic", "Type": "Ophthalmology Clinic", "Specialty": "General Ophthalmology"},
    ],
    "Baalbek": [
        {"Name": "Baalbek Eye Clinic", "Type": "Ophthalmology Clinic", "Specialty": "General Eye Care"},
        {"Name": "Bekaa Vision Center", "Type": "Optical Center", "Specialty": "Vision Testing"},
        {"Name": "Dar Al Amal Eye Unit", "Type": "Hospital Department", "Specialty": "Ophthalmology"},
    ],
}

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

SYMPTOM_LABELS = {
    "blur_distance": "Trouble seeing at a distance",
    "blur_close": "Trouble seeing up close",
    "eye_strain": "Eye strain / fatigue",
    "headaches": "Frequent headaches",
    "squinting": "Squinting to see clearly",
    "night_vision": "Difficulty seeing at night",
}


def generate_pdf(risk_score, recommendation, advice, priority_level, risk_factors, symptoms_details, recommendations_text, timestamp):
    pdf = FPDF()
    pdf.add_page()

    # Header
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_fill_color(30, 80, 160)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 14, "Vision Health Checker", fill=True, ln=True, align="C")
    pdf.set_text_color(0, 0, 0)
    pdf.ln(4)

    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 6, f"Assessment Report  |  {timestamp}", ln=True, align="C")
    pdf.set_text_color(0, 0, 0)
    pdf.ln(6)

    # Risk score box
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 8, "Assessment Summary", ln=True)
    pdf.set_draw_color(200, 200, 200)
    pdf.set_line_width(0.4)

    if priority_level == "high":
        pdf.set_fill_color(255, 220, 220)
    elif priority_level == "moderate":
        pdf.set_fill_color(255, 245, 200)
    else:
        pdf.set_fill_color(220, 245, 220)

    pdf.rect(10, pdf.get_y(), 190, 22, style="FD")
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(95, 11, f"Risk Score: {risk_score} / {MAX_RISK_SCORE}", ln=False, align="C")
    priority_label = recommendation.replace("🔴 ", "").replace("🟡 ", "").replace("🟢 ", "")
    pdf.cell(95, 11, f"Priority: {priority_label}", ln=True, align="C")
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 11, advice, ln=True, align="C")
    pdf.ln(6)

    # Key factors
    if risk_factors:
        pdf.set_font("Helvetica", "B", 13)
        pdf.cell(0, 8, "Key Factors Identified", ln=True)
        pdf.set_font("Helvetica", "", 11)
        for i, factor in enumerate(risk_factors, 1):
            pdf.cell(0, 7, f"  {i}. {factor}", ln=True)
        pdf.ln(4)

    # Symptom responses
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 8, "Symptom Responses", ln=True)
    pdf.set_font("Helvetica", "", 11)
    for item in symptoms_details:
        label = SYMPTOM_LABELS.get(item["symptom"], item["symptom"].replace("_", " ").title())
        pdf.cell(0, 7, f"  - {label}: {item['severity']}", ln=True)
    pdf.ln(4)

    # Recommendations
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 8, "Recommendations", ln=True)
    pdf.set_font("Helvetica", "", 11)
    for line in recommendations_text:
        clean = line.strip().lstrip("- ").replace("**", "")
        if clean:
            pdf.multi_cell(0, 7, f"  - {clean}")
    pdf.ln(4)

    # Disclaimer
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(120, 120, 120)
    pdf.multi_cell(0, 6, "Disclaimer: This report is for informational purposes only and is not a substitute for professional medical advice. Always consult with a qualified eye care professional.")

    return bytes(pdf.output())


st.title("👁️ Vision Health Checker")
st.write("Assess whether you might need to see an optometrist based on common vision problems and symptoms.")

# Initialize session state
if 'responses' not in st.session_state:
    st.session_state.responses = {}
if 'selected_location' not in st.session_state:
    st.session_state.selected_location = None

# Location Selection at the top (outside tabs)
st.subheader("📍 Select Your Location in Lebanon")
st.write("Choose your location to get insights about the nearest eye care clinics:")

col1, col2 = st.columns([2, 2])

with col1:
    st.selectbox(
        "Select your location:",
        options=["Select a location"] + list(EYE_CARE_PROVIDERS.keys()),
        key="location_select_main"
    )

# Show nearby clinics based on location selection
if st.session_state.get("location_select_main") and st.session_state.get("location_select_main") != "Select a location":
    with col2:
        providers = EYE_CARE_PROVIDERS[st.session_state.get("location_select_main")]
        st.metric(f"Available Clinics in {st.session_state.get('location_select_main')}", len(providers))

    st.divider()

    st.subheader(f"🏥 Nearby Clinics in {st.session_state.get('location_select_main')}")

    for idx, provider in enumerate(providers, 1):
        with st.container():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**{idx}. {provider['Name']}**")
                st.caption(f"📋 Type: {provider['Type']} | 🎯 Specialty: {provider['Specialty']}")
            with col2:
                if provider["Type"] in ["Eye Hospital", "Specialized Hospital"]:
                    st.badge("Hospital")
                elif provider["Type"] == "Ophthalmology Clinic":
                    st.badge("Clinic")
                else:
                    st.badge("Optical Center")
            st.divider()

    st.divider()

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs(["Vision Symptoms", "Eye Health", "Results", "Find Providers"])

with tab1:
    st.header("Vision Symptoms Assessment")
    st.write("Please answer the following questions about your vision:")

    col1, col2 = st.columns(2)

    with col1:
        st.radio(
            "Do you have trouble seeing things at a distance?",
            options=["No", "Occasionally", "Frequently"],
            key="blur_distance"
        )
        st.radio(
            "Do you have trouble seeing things up close?",
            options=["No", "Occasionally", "Frequently"],
            key="blur_close"
        )
        st.radio(
            "Do you experience eye strain or fatigue during/after screen time?",
            options=["No", "Occasionally", "Frequently"],
            key="eye_strain"
        )

    with col2:
        st.radio(
            "Do you suffer from frequent headaches?",
            options=["No", "Occasionally", "Frequently"],
            key="headaches"
        )
        st.radio(
            "Do you find yourself squinting to see clearly?",
            options=["No", "Occasionally", "Frequently"],
            key="squinting"
        )
        st.radio(
            "Do you have difficulty seeing at night or in low light?",
            options=["No", "Occasionally", "Frequently"],
            key="night_vision"
        )

with tab2:
    st.header("Eye Health Factors")
    st.write("Tell us about your eye health history and habits:")

    col1, col2 = st.columns(2)

    with col1:
        st.selectbox(
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
        st.checkbox(
            "Do you have family history of vision problems (myopia, hyperopia, astigmatism)?",
            key="family_history"
        )
        st.slider(
            "Average daily screen time (hours):",
            min_value=0,
            max_value=16,
            value=8,
            key="screen_time"
        )

    with col2:
        st.checkbox(
            "Do you see floaters or spots in your vision?",
            key="floaters"
        )
        st.checkbox(
            "Do you see flashes of light?",
            key="flashes"
        )
        st.checkbox(
            "Do you experience dry or irritated eyes?",
            key="dry_eyes"
        )
        st.checkbox(
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

        for key, weights in SYMPTOM_WEIGHTS.items():
            response = st.session_state.get(key, "No")
            if response in weights:
                risk_score += weights[response]
                if response != "No":
                    risk_factors.append(f"{SYMPTOM_LABELS.get(key, key.replace('_', ' ').title())}: {response}")
                    symptoms_details.append({"symptom": key, "severity": response})

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
            recommendations_text = [
                "Schedule an appointment immediately with a local optometrist or ophthalmologist",
                "If you cannot get an appointment soon, consider visiting an urgent care center",
                "Keep a symptom diary noting when symptoms occur and their severity",
                "Avoid activities that strain your eyes until evaluated",
            ]
        elif risk_score >= MODERATE_PRIORITY_THRESHOLD:
            recommendation = "🟡 MODERATE PRIORITY"
            advice = "Consider scheduling an eye exam in the near future."
            priority_level = "moderate"
            recommendations_text = [
                "Schedule an eye exam within 1-2 months",
                "Take regular breaks from screens (20-20-20 rule: every 20 min, look 20 ft away for 20 sec)",
                "Ensure proper lighting when reading or working",
                "Use artificial tears if experiencing dry eyes",
            ]
        else:
            recommendation = "🟢 LOW PRIORITY"
            advice = "Your symptoms suggest you may not urgently need an eye exam."
            priority_level = "low"
            recommendations_text = [
                "Schedule regular eye exams every 1-2 years",
                "Follow the 20-20-20 rule for screen time",
                "Maintain good eye hygiene",
                "Wear UV protection sunglasses outdoors",
                "If new symptoms develop, seek professional advice",
            ]

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

        # Store in session state for PDF generation
        st.session_state.last_report = {
            "risk_score": risk_score,
            "recommendation": recommendation,
            "advice": advice,
            "priority_level": priority_level,
            "risk_factors": risk_factors,
            "symptoms_details": symptoms_details,
            "recommendations_text": recommendations_text,
            "timestamp": timestamp,
        }

    if "last_report" in st.session_state:
        r = st.session_state.last_report

        col1, col2 = st.columns([1, 2])
        with col1:
            st.metric("Risk Score", f"{r['risk_score']}/{MAX_RISK_SCORE}")
        with col2:
            st.markdown(f"### {r['recommendation']}")

        st.info(r["advice"])

        if r["risk_factors"]:
            st.subheader("Key Factors Identified:")
            for i, factor in enumerate(r["risk_factors"], 1):
                st.write(f"{i}. {factor}")

        st.divider()

        st.subheader("📋 Recommendations:")
        for item in r["recommendations_text"]:
            st.write(f"- {item}")

        st.divider()

        # PDF Export
        st.subheader("📄 Export Report")
        pdf_bytes = generate_pdf(
            r["risk_score"], r["recommendation"], r["advice"],
            r["priority_level"], r["risk_factors"], r["symptoms_details"],
            r["recommendations_text"], r["timestamp"]
        )
        st.download_button(
            label="⬇️ Download PDF Report",
            data=pdf_bytes,
            file_name=f"vision_health_report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
            mime="application/pdf",
            type="primary"
        )

        st.divider()
        st.caption(f"Assessment completed on {r['timestamp']}")
        st.caption("⚠️ **Disclaimer**: This tool is for informational purposes only and not a substitute for professional medical advice. Always consult with a qualified eye care professional.")

with tab4:
    st.header("🏥 Find Eye Care Providers Near You")
    st.write("Based on your assessment and selected location, find recommended eye care providers in Lebanon.")

    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("📍 Select Location")
        location = st.selectbox(
            "Choose your area:",
            options=list(EYE_CARE_PROVIDERS.keys()),
            key="provider_location_select"
        )

    with col2:
        if "last_report" in st.session_state:
            st.subheader("📊 Your Assessment")
            st.metric("Risk Level", st.session_state.last_report["priority_level"].upper())
        else:
            st.info("💡 Complete the assessment first to get personalized recommendations")

    st.divider()

    if location:
        st.subheader(f"👁️ Eye Care Providers in {location}")

        providers = EYE_CARE_PROVIDERS[location]

        if "last_report" in st.session_state:
            priority = st.session_state.last_report["priority_level"]

            if priority == "high":
                st.warning("🔴 **HIGH PRIORITY** - We recommend hospitals or specialized ophthalmology clinics for urgent care")
                filtered_providers = [p for p in providers if p["Type"] in ["Eye Hospital", "Specialized Hospital", "Ophthalmology Clinic"]]
            elif priority == "moderate":
                st.info("🟡 **MODERATE PRIORITY** - Both ophthalmology clinics and optometry centers are suitable")
                filtered_providers = providers
            else:
                st.success("🟢 **LOW PRIORITY** - Optometry centers and optical shops are sufficient for routine checks")
                filtered_providers = providers
        else:
            filtered_providers = providers

        for idx, provider in enumerate(filtered_providers, 1):
            with st.container():
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.write(f"**{idx}. {provider['Name']}**")
                    st.caption(f"📋 Type: {provider['Type']}")
                    st.caption(f"🎯 Specialty: {provider['Specialty']}")
                with col2:
                    if provider["Type"] in ["Eye Hospital", "Specialized Hospital"]:
                        st.success("🏥 Hospital")
                    elif provider["Type"] == "Ophthalmology Clinic":
                        st.info("🔬 Clinic")
                    else:
                        st.write("🔍 Center")
                with col3:
                    st.write("")
                st.divider()

        if not filtered_providers:
            st.warning("No providers match your priority level in this location.")
            st.info("Showing all available providers:")
            for idx, provider in enumerate(providers, 1):
                st.write(f"**{idx}. {provider['Name']}** - {provider['Specialty']}")

        st.subheader(f"📊 Provider Statistics for {location}")
        col1, col2, col3 = st.columns(3)

        with col1:
            hospitals = len([p for p in providers if p["Type"] in ["Eye Hospital", "Specialized Hospital"]])
            st.metric("Hospitals", hospitals)
        with col2:
            clinics = len([p for p in providers if "Clinic" in p["Type"]])
            st.metric("Clinics", clinics)
        with col3:
            centers = len([p for p in providers if "Center" in p["Type"] or "Optical" in p["Type"]])
            st.metric("Optometry/Optical", centers)
