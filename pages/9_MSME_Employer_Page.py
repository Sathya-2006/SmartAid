import os
import streamlit as st
from datetime import datetime
from firebase_config import db
from auth import check_login, get_role, logout

check_login()
logout()

role = get_role()

if role not in ["MSME", "Admin"]:
    st.error("Access denied. MSME/Admin only.")
    st.stop()

# -----------------------------
# Theme
# -----------------------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #020617, #0f172a, #1e293b);
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #020617, #0f172a);
}

section[data-testid="stSidebar"] * {
    color: white !important;
}

h1, h2, h3, h4, label, p {
    color: white !important;
}

.page-title {
    font-size: 44px;
    font-weight: 900;
    color: white;
    margin-bottom: 5px;
}

.page-subtitle {
    color: #cbd5e1;
    font-size: 17px;
    margin-bottom: 25px;
}

.kpi-card {
    padding: 22px;
    border-radius: 20px;
    color: white;
    box-shadow: 0px 10px 25px rgba(0,0,0,0.30);
    min-height: 125px;
    text-align: center;
}

.kpi-number {
    font-size: 36px;
    font-weight: 900;
}

.kpi-label {
    font-size: 15px;
    font-weight: 700;
}

.card-blue { background: linear-gradient(135deg, #2563eb, #06b6d4); }
.card-green { background: linear-gradient(135deg, #059669, #22c55e); }
.card-purple { background: linear-gradient(135deg, #7c3aed, #a855f7); }
.card-orange { background: linear-gradient(135deg, #ea580c, #facc15); }

.glass-card {
    background: rgba(255,255,255,0.08);
    padding: 24px;
    border-radius: 22px;
    border: 1px solid rgba(255,255,255,0.12);
    box-shadow: 0px 10px 30px rgba(0,0,0,0.25);
    margin-bottom: 20px;
}

.job-card {
    background: rgba(14,165,233,0.15);
    padding: 18px;
    border-radius: 15px;
    border-left: 5px solid #0ea5e9;
    color: white;
    margin-bottom: 12px;
    line-height: 1.7;
}

.candidate-card {
    background: rgba(34,197,94,0.14);
    padding: 18px;
    border-radius: 15px;
    border-left: 5px solid #22c55e;
    color: #dcfce7;
    margin-bottom: 12px;
    line-height: 1.7;
}

.hire-card {
    background: rgba(250,204,21,0.14);
    padding: 18px;
    border-radius: 15px;
    border-left: 5px solid #facc15;
    color: #fef3c7;
    margin-bottom: 12px;
    line-height: 1.7;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="page-title">🏭 MSME Employment Portal</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="page-subtitle">Post jobs, view open requirements, match suitable candidates and assign employment opportunities.</div>',
    unsafe_allow_html=True
)

# -----------------------------
# Load data for KPIs
# -----------------------------
job_docs_all = list(db.collection("msme_jobs").stream())
people_docs_all = list(db.collection("people").stream())
allocation_docs_all = list(db.collection("job_allocations").stream())

total_jobs = len(job_docs_all)
open_jobs_count = sum(1 for j in job_docs_all if j.to_dict().get("status", "Open") == "Open")
total_candidates = sum(
    1 for p in people_docs_all
    if p.to_dict().get("age", 0) >= 18 and p.to_dict().get("work_willingness") == "Yes"
)
jobs_filled = len(allocation_docs_all)

k1, k2, k3, k4 = st.columns(4)

with k1:
    st.markdown(f"""
    <div class="kpi-card card-blue">
        <div class="kpi-number">{total_jobs}</div>
        <div class="kpi-label">📌 Jobs Posted</div>
    </div>
    """, unsafe_allow_html=True)

with k2:
    st.markdown(f"""
    <div class="kpi-card card-green">
        <div class="kpi-number">{open_jobs_count}</div>
        <div class="kpi-label">🟢 Open Jobs</div>
    </div>
    """, unsafe_allow_html=True)

with k3:
    st.markdown(f"""
    <div class="kpi-card card-purple">
        <div class="kpi-number">{total_candidates}</div>
        <div class="kpi-label">👥 Work-ready Candidates</div>
    </div>
    """, unsafe_allow_html=True)

with k4:
    st.markdown(f"""
    <div class="kpi-card card-orange">
        <div class="kpi-number">{jobs_filled}</div>
        <div class="kpi-label">✅ Jobs Assigned</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

tab1, tab2, tab3, tab4 = st.tabs(
    ["➕ Post Job", "📋 View Jobs", "🔍 Find Candidates", "🎉 Recent Hires"]
)

# -----------------------------
# Tab 1: Post Job
# -----------------------------
with tab1:
    
    st.subheader("➕ Post a Job Requirement")

    col1, col2 = st.columns(2)

    with col1:
        employer_name = st.text_input("Employer / MSME Name")
        contact_person = st.text_input("Contact Person")
        phone = st.text_input("Phone Number")
        job_location = st.text_input("Job Location")

    with col2:
        job_type = st.selectbox(
            "Job Type",
            [
                "Security",
                "Cleaning",
                "Tailoring",
                "Delivery",
                "Construction",
                "Packaging",
                "Data Entry",
                "Hospitality",
                "Warehouse",
                "Retail",
                "Driver",
                "Other"
            ]
        )

        vacancies = st.number_input("Number of Vacancies", min_value=1, max_value=100)
        salary = st.number_input("Monthly Salary (₹)", min_value=0)
        required_skills = st.text_input("Required Skills")

    requirements = st.text_area("Job Requirements / Description")

    if st.button("Post Job", use_container_width=True):
        if employer_name.strip() == "" or job_location.strip() == "":
            st.error("Please enter employer name and job location.")
        else:
            job_data = {
                "employer_name": employer_name,
                "contact_person": contact_person,
                "phone": phone,
                "job_type": job_type,
                "job_location": job_location,
                "vacancies": vacancies,
                "salary": salary,
                "required_skills": required_skills,
                "requirements": requirements,
                "status": "Open",
                "created_at": datetime.now()
            }

            db.collection("msme_jobs").add(job_data)

            st.success("Job posted successfully!")

    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# Tab 2: View Job Posts
# -----------------------------
with tab2:
    st.subheader("📋 Posted Jobs")

    job_docs = list(db.collection("msme_jobs").stream())

    if len(job_docs) == 0:
        st.warning("No jobs posted yet.")
    else:
        for job in reversed(job_docs):
            data = job.to_dict()

            st.markdown(f"""
            <div class="job-card">
            <b>🏢 Employer:</b> {data.get("employer_name")}<br>
            <b>👤 Contact:</b> {data.get("contact_person")}<br>
            <b>📞 Phone:</b> {data.get("phone")}<br>
            <b>💼 Job Type:</b> {data.get("job_type")}<br>
            <b>📍 Location:</b> {data.get("job_location")}<br>
            <b>👥 Vacancies:</b> {data.get("vacancies")}<br>
            <b>💰 Salary:</b> ₹{data.get("salary")}<br>
            <b>🛠 Required Skills:</b> {data.get("required_skills", "Not specified")}<br>
            <b>📌 Status:</b> {data.get("status", "Open")}<br>
            <b>📝 Requirements:</b> {data.get("requirements")}
            </div>
            """, unsafe_allow_html=True)

# -----------------------------
# Tab 3: Find Candidates
# -----------------------------
with tab3:
    st.subheader("🔍 Find Suitable Candidates")

    job_docs = list(db.collection("msme_jobs").stream())
    people_docs = list(db.collection("people").stream())

    open_jobs = {}

    for job in job_docs:
        data = job.to_dict()

        if data.get("status", "Open") == "Open":
            label = (
                f"{data.get('job_type')} | "
                f"{data.get('employer_name')} | "
                f"{data.get('job_location')}"
            )

            open_jobs[label] = {
                "id": job.id,
                "data": data
            }

    if len(open_jobs) == 0:
        st.warning("No open jobs found.")
    else:
        selected_job_label = st.selectbox("Select Job", list(open_jobs.keys()))

        selected_job = open_jobs[selected_job_label]
        job_id = selected_job["id"]
        job_data = selected_job["data"]

        st.markdown(f"""
        <div class="job-card">
        <b>Selected Job:</b> {job_data.get("job_type")}<br>
        <b>Employer:</b> {job_data.get("employer_name")}<br>
        <b>Location:</b> {job_data.get("job_location")}<br>
        <b>Salary:</b> ₹{job_data.get("salary")}<br>
        <b>Vacancies:</b> {job_data.get("vacancies")}
        </div>
        """, unsafe_allow_html=True)

        matched_candidates = {}

        for person in people_docs:
            pdata = person.to_dict()

            age = pdata.get("age", 0)
            work_willingness = pdata.get("work_willingness", "")
            skill = str(pdata.get("skill", "")).lower()
            person_location = str(pdata.get("location", "")).lower()
            job_type = str(job_data.get("job_type", "")).lower()
            job_location = str(job_data.get("job_location", "")).lower()
            required_skills = str(job_data.get("required_skills", "")).lower()

            if age >= 18 and work_willingness == "Yes":
                match_score = 0

                if job_type in skill or skill in job_type:
                    match_score += 50

                if required_skills and required_skills in skill:
                    match_score += 20

                if person_location == job_location:
                    match_score += 20

                if pdata.get("physical_fitness") == "Fit":
                    match_score += 10

                if job_type == "other":
                    match_score += 40

                if match_score > 0:
                    label = (
                        f"{pdata.get('name')} | "
                        f"{pdata.get('skill')} | "
                        f"{pdata.get('location')} | "
                        f"Match {match_score}%"
                    )

                    matched_candidates[label] = {
                        "id": person.id,
                        "data": pdata,
                        "match_score": match_score
                    }

        if len(matched_candidates) == 0:
            st.info("No exact match found. Showing all work-willing candidates.")

            for person in people_docs:
                pdata = person.to_dict()

                if pdata.get("age", 0) >= 18 and pdata.get("work_willingness") == "Yes":
                    label = (
                        f"{pdata.get('name')} | "
                        f"{pdata.get('skill')} | "
                        f"{pdata.get('location')} | "
                        f"Match 50%"
                    )

                    matched_candidates[label] = {
                        "id": person.id,
                        "data": pdata,
                        "match_score": 50
                    }

        if len(matched_candidates) == 0:
            st.warning("No eligible candidates found.")
        else:
            selected_candidate_label = st.selectbox(
                "Select Candidate",
                list(matched_candidates.keys())
            )

            selected_candidate = matched_candidates[selected_candidate_label]
            person_id = selected_candidate["id"]
            pdata = selected_candidate["data"]
            match_score = selected_candidate["match_score"]

            col1, col2 = st.columns([1, 1.5])

            with col1:
                photo_path = pdata.get("photo_path", "")

                if photo_path and os.path.exists(photo_path):
                    st.image(photo_path, width=220, caption="Candidate Photo")
                else:
                    st.info("No candidate photo available.")

                st.metric("Match Score", f"{match_score}%")

            with col2:
                st.markdown(f"""
                <div class="candidate-card">
                <b>👤 Name:</b> {pdata.get("name")}<br>
                <b>🎂 Age:</b> {pdata.get("age")}<br>
                <b>🛠 Skill:</b> {pdata.get("skill")}<br>
                <b>📍 Location:</b> {pdata.get("location")}<br>
                <b>♿ Disability:</b> {pdata.get("disability")}<br>
                <b>💪 Fitness:</b> {pdata.get("physical_fitness")}<br>
                <b>🤖 AI Recommendation:</b><br>
                {pdata.get("ai_recommendation")}
                </div>
                """, unsafe_allow_html=True)

                if st.button("✅ Assign Candidate to Job", use_container_width=True):
                    assignment_data = {
                        "job_id": job_id,
                        "person_id": person_id,
                        "person_name": pdata.get("name"),
                        "employer_name": job_data.get("employer_name"),
                        "job_type": job_data.get("job_type"),
                        "job_location": job_data.get("job_location"),
                        "salary": job_data.get("salary"),
                        "match_score": match_score,
                        "assigned_at": datetime.now()
                    }

                    db.collection("job_allocations").add(assignment_data)

                    db.collection("people").document(person_id).update({
                        "status": "Job Assigned",
                        "assigned_job": job_data.get("job_type"),
                        "employer_name": job_data.get("employer_name"),
                        "job_location": job_data.get("job_location"),
                        "salary": job_data.get("salary")
                    })

                    st.success("Candidate assigned to job successfully!")

# -----------------------------
# Tab 4: Recent Hires
# -----------------------------
with tab4:
    st.subheader("🎉 Recent Job Allocations")

    recent_jobs = list(db.collection("job_allocations").stream())

    if len(recent_jobs) == 0:
        st.info("No job allocations yet.")
    else:
        for job in reversed(recent_jobs[-10:]):
            data = job.to_dict()

            st.markdown(f"""
            <div class="hire-card">
            👤 <b>{data.get("person_name")}</b><br>
            🏢 Employer: <b>{data.get("employer_name")}</b><br>
            💼 Job: <b>{data.get("job_type")}</b><br>
            📍 Location: <b>{data.get("job_location")}</b><br>
            💰 Salary: <b>₹{data.get("salary", "N/A")}</b><br>
            🎯 Match Score: <b>{data.get("match_score", "N/A")}%</b>
            </div>
            """, unsafe_allow_html=True)