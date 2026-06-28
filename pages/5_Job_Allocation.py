import streamlit as st
from datetime import datetime
from firebase_config import db
from auth import check_login, get_role, logout

try:
    from Utility.email_service import send_email
except Exception:
    send_email = None

try:
    from Utility.sms_service import send_sms
except Exception:
    send_sms = None


check_login()
logout()

role = get_role()

if role != "Admin":
    st.error("Access denied. Admin only.")
    st.stop()


# -----------------------------------
# Styling
# -----------------------------------
st.markdown("""
<style>

.stApp{
    background: linear-gradient(135deg,#020617,#0f172a,#1e293b);
}

section[data-testid="stSidebar"] {
    background: #020617;
}

section[data-testid="stSidebar"] * {
    color: white !important;
}

h1,h2,h3,label,p{
    color:white !important;
}

.profile-card{
    background:rgba(14,165,233,0.15);
    padding:18px;
    border-radius:15px;
    border-left:5px solid #0ea5e9;
    color:white;
}

.job-card{
    background:rgba(34,197,94,0.15);
    padding:18px;
    border-radius:15px;
    border-left:5px solid #22c55e;
    color:white;
    margin-bottom:12px;
}

.metric-card{
    background:linear-gradient(135deg,#2563eb,#06b6d4);
    padding:20px;
    border-radius:18px;
    text-align:center;
    color:white;
    box-shadow:0 8px 25px rgba(0,0,0,0.25);
}

.metric-number{
    font-size:35px;
    font-weight:900;
}

.metric-label{
    font-size:15px;
    font-weight:700;
}

</style>
""", unsafe_allow_html=True)


# -----------------------------------
# Title
# -----------------------------------
st.title("💼 Job Allocation Portal")

st.caption(
    "Assign suitable jobs to work-ready beneficiaries and notify employers/beneficiaries."
)


# -----------------------------------
# Data
# -----------------------------------
people_docs = list(db.collection("people").stream())

eligible_count = 0
job_assigned_count = 0

for doc in people_docs:
    pdata = doc.to_dict()

    if pdata.get("work_willingness") == "Yes" and pdata.get("age", 0) >= 18:
        eligible_count += 1

    if pdata.get("status") == "Job Assigned":
        job_assigned_count += 1


# -----------------------------------
# Statistics
# -----------------------------------
col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-number">{eligible_count}</div>
        <div class="metric-label">Eligible Candidates</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-number">{job_assigned_count}</div>
        <div class="metric-label">Jobs Assigned</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")


# -----------------------------------
# Eligible People
# -----------------------------------
eligible_people = {}

for doc in people_docs:
    pdata = doc.to_dict()

    if pdata.get("work_willingness") == "Yes" and pdata.get("age", 0) >= 18:
        label = (
            f"{pdata.get('name','Unknown')} | "
            f"{pdata.get('skill','No Skill')} | "
            f"{pdata.get('location','Unknown')}"
        )

        eligible_people[label] = {
            "id": doc.id,
            "data": pdata
        }


if len(eligible_people) == 0:
    st.warning("No eligible candidates found.")

else:
    selected_label = st.selectbox(
        "Select Candidate",
        list(eligible_people.keys())
    )

    selected_person = eligible_people[selected_label]

    person_id = selected_person["id"]
    data = selected_person["data"]

    col1, col2 = st.columns(2)

    # -----------------------------------
    # Candidate Profile
    # -----------------------------------
    with col1:
        st.subheader("👤 Candidate Profile")

        st.markdown(f"""
        <div class="profile-card">
            <b>Name:</b> {data.get("name", "N/A")}<br>
            <b>Age:</b> {data.get("age", "N/A")}<br>
            <b>Gender:</b> {data.get("gender", "N/A")}<br>
            <b>Skill:</b> {data.get("skill", "N/A")}<br>
            <b>Location:</b> {data.get("location", "N/A")}<br>
            <b>Phone:</b> {data.get("phone", "Not available")}<br>
            <b>Email:</b> {data.get("email", "Not available")}<br>
            <b>Disability:</b> {data.get("disability", "N/A")}<br>
            <b>Physical Fitness:</b> {data.get("physical_fitness", "N/A")}
        </div>
        """, unsafe_allow_html=True)

        st.write("")

        st.info(
            data.get(
                "ai_recommendation",
                "No AI recommendation available."
            )
        )

    # -----------------------------------
    # Job Assignment
    # -----------------------------------
    with col2:
        st.subheader("🏢 Assign Job")

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

        employer_name = st.text_input("Employer / MSME Name")
        employer_email = st.text_input("Employer Email")
        job_location = st.text_input("Job Location")

        salary = st.number_input(
            "Monthly Salary",
            min_value=0
        )

        joining_date = st.date_input("Expected Joining Date")

        notes = st.text_area("Admin Notes")

        send_email_alert = st.checkbox(
            "Send email notification to employer",
            value=True
        )

        send_sms_alert = st.checkbox(
            "Send SMS notification to beneficiary",
            value=True
        )

        if st.button("✅ Assign Job", width="stretch"):

            if employer_name.strip() == "" or job_location.strip() == "":
                st.error("Employer and location are required.")

            else:
                job_data = {
                    "person_id": person_id,
                    "person_name": data.get("name"),
                    "candidate_phone": data.get("phone", ""),
                    "candidate_email": data.get("email", ""),
                    "job_type": job_type,
                    "employer_name": employer_name,
                    "employer_email": employer_email,
                    "job_location": job_location,
                    "salary": salary,
                    "joining_date": str(joining_date),
                    "notes": notes,
                    "assigned_at": datetime.now()
                }

                db.collection("job_allocations").add(job_data)

                db.collection("people").document(person_id).update({
                    "status": "Job Assigned",
                    "assigned_job": job_type,
                    "employer_name": employer_name,
                    "employer_email": employer_email,
                    "job_location": job_location,
                    "salary": salary,
                    "joining_date": str(joining_date)
                })

                st.success("Job assigned successfully!")

                # -------------------------------
                # SMS Notification to Beneficiary
                # -------------------------------
                phone = data.get("phone", "")

                if send_sms_alert:
                    if send_sms is None:
                        st.warning(
                            "SMS service not configured. Check Utility/sms_service.py."
                        )

                    elif str(phone).strip() == "":
                        st.warning(
                            "Beneficiary phone number not available, so SMS was not sent."
                        )

                    else:
                        sms_message = f"""
SmartAid Alert

Dear {data.get('name', 'Beneficiary')},

You have been assigned a job.

Job: {job_type}
Employer: {employer_name}
Location: {job_location}
Salary: Rs.{salary}
Joining Date: {joining_date}

Regards,
SmartAid
"""

                        sms_status = send_sms(phone, sms_message)

                        if sms_status:
                            st.success("SMS sent to beneficiary.")
                        else:
                            st.warning("Job assigned, but SMS sending failed.")

                # -------------------------------
                # Email Notification to Employer
                # -------------------------------
                if send_email_alert:
                    if send_email is None:
                        st.warning(
                            "Email service not configured. Check Utility/email_service.py."
                        )

                    elif employer_email.strip() == "":
                        st.warning(
                            "Employer email not entered, so email notification was not sent."
                        )

                    else:
                        subject = "SmartAid Candidate Assigned for Job"

                        email_message = f"""
Hello {employer_name},

A candidate has been assigned for your job requirement through SmartAid.

Candidate Details:
Name: {data.get("name", "N/A")}
Age: {data.get("age", "N/A")}
Gender: {data.get("gender", "N/A")}
Skill: {data.get("skill", "N/A")}
Location: {data.get("location", "N/A")}
Phone: {data.get("phone", "N/A")}
Email: {data.get("email", "N/A")}
Disability: {data.get("disability", "N/A")}
Physical Fitness: {data.get("physical_fitness", "N/A")}

Job Details:
Job Type: {job_type}
Job Location: {job_location}
Monthly Salary: Rs.{salary}
Expected Joining Date: {joining_date}

Admin Notes:
{notes}

Regards,
SmartAid Team
"""

                        email_status = send_email(
                            employer_email,
                            subject,
                            email_message
                        )

                        if email_status:
                            st.success("Email notification sent to employer.")
                        else:
                            st.error("Job assigned, but email sending failed.")

                st.rerun()


# -----------------------------------
# Recent Assignments
# -----------------------------------
st.subheader("📋 Recent Job Allocations")

jobs = list(db.collection("job_allocations").stream())

if len(jobs) == 0:
    st.info("No jobs assigned yet.")

else:
    for job in reversed(jobs[-5:]):
        job_data = job.to_dict()

        st.markdown(f"""
        <div class="job-card">
            👤 <b>{job_data.get("person_name")}</b><br>
            💼 {job_data.get("job_type")}<br>
            🏢 {job_data.get("employer_name")}<br>
            📧 {job_data.get("employer_email", "No employer email")}<br>
            📱 {job_data.get("candidate_phone", "No phone")}<br>
            📍 {job_data.get("job_location")}<br>
            💰 Rs.{job_data.get("salary")}<br>
            📅 Joining: {job_data.get("joining_date", "N/A")}
        </div>
        """, unsafe_allow_html=True)