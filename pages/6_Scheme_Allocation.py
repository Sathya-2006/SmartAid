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

.scheme-card{
    background:rgba(34,197,94,0.15);
    padding:18px;
    border-radius:15px;
    border-left:5px solid #22c55e;
    color:white;
    margin-bottom:12px;
}

.metric-card{
    background:linear-gradient(135deg,#7c3aed,#a855f7);
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


st.title("🏛 Government Scheme Allocation Portal")
st.caption("Assign welfare schemes, scholarships, pensions and government support programs.")


people_docs = list(db.collection("people").stream())

total_people = len(people_docs)
scheme_assigned = 0

for doc in people_docs:
    pdata = doc.to_dict()
    if pdata.get("status") == "Scheme Assigned":
        scheme_assigned += 1


col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-number">{total_people}</div>
        <div class="metric-label">Registered People</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-number">{scheme_assigned}</div>
        <div class="metric-label">Schemes Assigned</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")


people_options = {}

for doc in people_docs:
    pdata = doc.to_dict()

    label = (
        f"{pdata.get('name','Unknown')} | "
        f"Age {pdata.get('age','N/A')} | "
        f"{pdata.get('location','Unknown')}"
    )

    people_options[label] = {
        "id": doc.id,
        "data": pdata
    }


if len(people_options) == 0:
    st.warning("No registered people found.")

else:
    selected_label = st.selectbox(
        "Select Beneficiary",
        list(people_options.keys())
    )

    selected_person = people_options[selected_label]

    person_id = selected_person["id"]
    data = selected_person["data"]

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("👤 Beneficiary Profile")

        st.markdown(f"""
        <div class="profile-card">
            <b>Name:</b> {data.get("name", "N/A")}<br>
            <b>Age:</b> {data.get("age", "N/A")}<br>
            <b>Gender:</b> {data.get("gender", "N/A")}<br>
            <b>Location:</b> {data.get("location", "N/A")}<br>
            <b>Phone:</b> {data.get("phone", "Not available")}<br>
            <b>Email:</b> {data.get("email", "Not available")}<br>
            <b>Disability:</b> {data.get("disability", "N/A")}<br>
            <b>Education:</b> {data.get("education_status", "N/A")}<br>
            <b>Family Status:</b> {data.get("family_status", "N/A")}
        </div>
        """, unsafe_allow_html=True)

        st.write("")

        st.info(
            data.get(
                "ai_recommendation",
                "No recommendation generated."
            )
        )

    with col2:
        st.subheader("🏛 Assign Scheme")

        scheme_name = st.selectbox(
            "Scheme Name",
            [
                "Disability Pension",
                "Old Age Pension",
                "Housing Scheme",
                "PMAY Housing Support",
                "PMKVY Skill Training",
                "Scholarship",
                "Mid-Day Meal Support",
                "Ration Card Support",
                "Healthcare Support",
                "Women Welfare Scheme",
                "Widow Assistance Scheme",
                "Farmer Support Scheme",
                "Youth Skill Development",
                "Other"
            ]
        )

        department = st.text_input("Department / NGO Name")
        department_email = st.text_input("Department / NGO Email")
        approval_number = st.text_input("Approval Reference Number")

        benefit_amount = st.number_input(
            "Benefit Amount (₹)",
            min_value=0
        )

        notes = st.text_area("Admin Notes")

        send_email_alert = st.checkbox(
            "Send email notification to department/NGO",
            value=True
        )

        send_sms_alert = st.checkbox(
            "Send SMS notification to beneficiary",
            value=True
        )

        if st.button("✅ Assign Scheme", width="stretch"):

            if department.strip() == "":
                st.error("Department / NGO name required.")

            else:
                scheme_data = {
                    "person_id": person_id,
                    "person_name": data.get("name"),
                    "beneficiary_phone": data.get("phone", ""),
                    "beneficiary_email": data.get("email", ""),
                    "scheme_name": scheme_name,
                    "department": department,
                    "department_email": department_email,
                    "approval_number": approval_number,
                    "benefit_amount": benefit_amount,
                    "notes": notes,
                    "assigned_at": datetime.now()
                }

                db.collection("scheme_allocations").add(scheme_data)

                db.collection("people").document(person_id).update({
                    "status": "Scheme Assigned",
                    "assigned_scheme": scheme_name,
                    "scheme_department": department,
                    "department_email": department_email,
                    "benefit_amount": benefit_amount,
                    "approval_number": approval_number
                })

                st.success("Scheme assigned successfully!")

                phone = data.get("phone", "")

                if send_sms_alert:
                    if send_sms is None:
                        st.warning("SMS service not configured. Check Utility/sms_service.py.")

                    elif str(phone).strip() == "":
                        st.warning("Beneficiary phone number not available, so SMS was not sent.")

                    else:
                        sms_message = f"""
SmartAid Alert

Dear {data.get('name', 'Beneficiary')},

A welfare scheme has been assigned.

Scheme: {scheme_name}
Department: {department}
Benefit Amount: Rs.{benefit_amount}

Regards,
SmartAid
"""

                        sms_status = send_sms(phone, sms_message)

                        if sms_status:
                            st.success("SMS sent to beneficiary.")
                        else:
                            st.warning("Scheme assigned, but SMS sending failed.")

                if send_email_alert:
                    if send_email is None:
                        st.warning("Email service not configured. Check Utility/email_service.py.")

                    elif department_email.strip() == "":
                        st.warning("Department / NGO email not entered, so email notification was not sent.")

                    else:
                        subject = "SmartAid Scheme Allocation Notification"

                        email_message = f"""
Hello {department},

A beneficiary has been assigned for welfare scheme support through SmartAid.

Beneficiary Details:
Name: {data.get("name", "N/A")}
Age: {data.get("age", "N/A")}
Gender: {data.get("gender", "N/A")}
Location: {data.get("location", "N/A")}
Phone: {data.get("phone", "N/A")}
Email: {data.get("email", "N/A")}
Disability: {data.get("disability", "N/A")}
Education: {data.get("education_status", "N/A")}
Family Status: {data.get("family_status", "N/A")}

Scheme Details:
Scheme Name: {scheme_name}
Approval Reference Number: {approval_number}
Benefit Amount: Rs.{benefit_amount}

Admin Notes:
{notes}

Regards,
SmartAid Team
"""

                        email_status = send_email(
                            department_email,
                            subject,
                            email_message
                        )

                        if email_status:
                            st.success("Email notification sent to department/NGO.")
                        else:
                            st.error("Scheme assigned, but email sending failed.")

                st.rerun()


st.subheader("📋 Recent Scheme Allocations")

scheme_docs = list(db.collection("scheme_allocations").stream())

if len(scheme_docs) == 0:
    st.info("No schemes assigned yet.")

else:
    for scheme in reversed(scheme_docs[-5:]):
        scheme_data = scheme.to_dict()

        st.markdown(f"""
        <div class="scheme-card">
            👤 <b>{scheme_data.get("person_name")}</b><br>
            🏛 {scheme_data.get("scheme_name")}<br>
            🏢 {scheme_data.get("department")}<br>
            📧 {scheme_data.get("department_email", "No department email")}<br>
            📱 {scheme_data.get("beneficiary_phone", "No phone")}<br>
            💰 Rs.{scheme_data.get("benefit_amount",0)}<br>
            🔖 Ref: {scheme_data.get("approval_number", "N/A")}
        </div>
        """, unsafe_allow_html=True)