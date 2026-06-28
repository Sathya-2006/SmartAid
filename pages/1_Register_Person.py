import os
import streamlit as st
from datetime import datetime
from firebase_config import db
from auth import check_login, get_role, logout

check_login()
logout()

role = get_role()

if role not in ["Volunteer", "Admin"]:
    st.error("Access denied. Only Volunteer/Admin can access this page.")
    st.stop()


# -----------------------------
# Page Styling
# -----------------------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0f172a, #1e293b);
}

h1, h2, h3, label {
    color: white !important;
}

p, div {
    color: inherit;
}

[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stSelectbox"] div,
textarea {
    border-radius: 10px;
}

.form-card {
    background: rgba(255,255,255,0.08);
    padding: 25px;
    border-radius: 18px;
    border: 1px solid rgba(255,255,255,0.15);
    box-shadow: 0px 8px 25px rgba(0,0,0,0.25);
    margin-bottom: 20px;
}

.info-box {
    background: rgba(14,165,233,0.15);
    color: #e0f2fe;
    padding: 18px;
    border-radius: 14px;
    border-left: 6px solid #0ea5e9;
    font-weight: 600;
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)


PHOTO_FOLDER = "uploaded_photos"

if not os.path.exists(PHOTO_FOLDER):
    os.makedirs(PHOTO_FOLDER)


def get_basic_recommendation(
    skill,
    age,
    gender,
    disability,
    work_willingness,
    physical_fitness,
    family_status,
    education_status
):
    skill = skill.lower()

    if 6 <= age <= 18 or education_status == "School Student":
        return "Recommended: Enroll in government school, scholarships, mid-day meal program, and child welfare support. Job recommendation not allowed for minors."

    if education_status == "College Student":
        return "Recommended: Scholarships, skill development programs, internships, and career guidance."

    if age >= 60 and work_willingness == "No":
        return "Recommended: Old age pension scheme, healthcare support, and NGO assistance."

    if disability == "Yes" and work_willingness == "No":
        return "Recommended: Disability pension, healthcare schemes, assistive support, and NGO welfare assistance."

    if disability == "Yes" and work_willingness == "Yes":
        return "Recommended: Suitable jobs such as data entry, handicrafts, tailoring, packaging, remote work, and disability-friendly skill training."

    if gender == "Female" and family_status in ["Widowed", "Single"]:
        return "Recommended: Self-help groups, women welfare schemes, skill training, tailoring/handicraft opportunities, and financial assistance."

    if family_status == "Family":
        return "Recommended: Housing schemes, family welfare support, job opportunities, and ration/documentation assistance."

    if work_willingness == "Yes":
        if "editor" in skill:
            return "Recommended: Video editing freelance work, digital media training, and skill development program."
        if "security" in skill:
            return "Recommended: Security guard job, basic safety training, and local employment support."
        if "tailor" in skill or "tailoring" in skill:
            return "Recommended: Tailoring job, self-employment scheme, and tailoring training."
        if "clean" in skill or "cleaning" in skill:
            return "Recommended: Cleaning job, hygiene training, and municipal employment support."
        if "construction" in skill or "mason" in skill:
            return "Recommended: Construction helper job, masonry training, and labour welfare scheme."

    if work_willingness == "Yes" and physical_fitness == "Fit":
        return "Recommended: Allocate suitable jobs such as construction, cleaning, delivery, hospitality, security, or MSME jobs."

    if work_willingness == "Yes" and physical_fitness == "Need Skills":
        return "Recommended: PMKVY, skill development training, vocational training, and job-readiness support."

    return "Recommended: General welfare support, counselling, documentation assistance, and local NGO support."


st.markdown("<h1>📝 Register Person</h1>", unsafe_allow_html=True)

st.markdown("""
<div class="info-box">
Capture volunteer details, personal profile, contact details, GPS location, photo/camera image and generate AI-based support recommendation.
</div>
""", unsafe_allow_html=True)


st.subheader("Volunteer Details")
volunteer_name = st.text_input("Volunteer Name")

st.subheader("Person Details")

col1, col2 = st.columns(2)

with col1:
    name = st.text_input("Name")
    age = st.number_input("Age", min_value=1, max_value=100)
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    phone = st.text_input("Phone Number")
    email = st.text_input("Email ID")

with col2:
    skill = st.text_input("Skill")
    health_condition = st.text_input("Health Condition")
    disability = st.selectbox("Disability", ["No", "Yes"])
    work_willingness = st.selectbox("Work Willingness", ["Yes", "No"])
    physical_fitness = st.selectbox("Physical Fitness", ["Fit", "Need Skills", "Unable to Work"])

col3, col4 = st.columns(2)

with col3:
    family_status = st.selectbox("Family Status", ["Single", "Family", "Widowed"])

with col4:
    education_status = st.selectbox("Education Status", ["None", "School Student", "College Student"])

location = st.text_input("Location / Area Name")

st.subheader("GPS Location")

gps_col1, gps_col2 = st.columns(2)

with gps_col1:
    latitude = st.number_input("Latitude", value=0.0, format="%.6f")

with gps_col2:
    longitude = st.number_input("Longitude", value=0.0, format="%.6f")

st.subheader("Photo Capture / Upload")

photo_option = st.radio(
    "Choose Photo Method",
    ["Upload Photo", "Take Photo with Camera"],
    horizontal=True
)

photo = None

if photo_option == "Upload Photo":
    photo = st.file_uploader(
        "Upload Person Photo",
        type=["jpg", "jpeg", "png"]
    )

elif photo_option == "Take Photo with Camera":
    photo = st.camera_input("Take a Photo")

if photo is not None:
    st.image(photo, caption="Photo Preview", width=220)

st.write("")

if st.button("Register Person", width="stretch"):
    if volunteer_name.strip() == "":
        st.error("Please enter volunteer name.")
    elif name.strip() == "" or location.strip() == "":
        st.error("Please enter person name and location.")
    elif phone.strip() == "":
        st.error("Please enter phone number.")
    elif latitude == 0.0 or longitude == 0.0:
        st.error("Please enter valid latitude and longitude.")
    else:
        recommendation = get_basic_recommendation(
            skill,
            age,
            gender,
            disability,
            work_willingness,
            physical_fitness,
            family_status,
            education_status
        )

        photo_path = ""

        if photo is not None:
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            safe_name = name.replace(" ", "_")

            if hasattr(photo, "name") and "." in photo.name:
                file_extension = photo.name.split(".")[-1]
            else:
                file_extension = "png"

            photo_filename = f"{safe_name}_{timestamp}.{file_extension}"
            photo_path = os.path.join(PHOTO_FOLDER, photo_filename)

            with open(photo_path, "wb") as f:
                f.write(photo.getbuffer())

        person_data = {
            "volunteer_name": volunteer_name,
            "name": name,
            "age": age,
            "gender": gender,
            "phone": phone,
            "email": email,
            "skill": skill,
            "health_condition": health_condition,
            "disability": disability,
            "work_willingness": work_willingness,
            "physical_fitness": physical_fitness,
            "family_status": family_status,
            "education_status": education_status,
            "location": location,
            "latitude": latitude,
            "longitude": longitude,
            "photo_path": photo_path,
            "photo_method": photo_option,
            "ai_recommendation": recommendation,
            "status": "Pending",
            "created_at": datetime.now()
        }

        db.collection("people").add(person_data)

        st.success("Person registered successfully!")
        st.info(recommendation)

        if photo_path:
            st.success(f"Photo saved successfully: {photo_path}")