import os
import io
import streamlit as st
import pandas as pd
from datetime import datetime
from firebase_config import db
from auth import check_login, get_role, logout

check_login()
logout()

role = get_role()

if role != "Admin":
    st.error("Access denied. Admin only.")
    st.stop()

try:
    from reportlab.pdfgen import canvas
    REPORTLAB_AVAILABLE = True
except Exception:
    REPORTLAB_AVAILABLE = False


# -----------------------
# Theme
# -----------------------
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

.glass-card {
    background: rgba(255,255,255,0.08);
    padding: 24px;
    border-radius: 22px;
    border: 1px solid rgba(255,255,255,0.12);
    box-shadow: 0px 10px 30px rgba(0,0,0,0.25);
    margin-bottom: 20px;
}

.profile-card {
    background: rgba(14,165,233,0.15);
    padding: 18px;
    border-radius: 15px;
    border-left: 5px solid #0ea5e9;
    color: white;
    line-height: 1.8;
}

.ai-card {
    background: rgba(34,197,94,0.14);
    padding: 18px;
    border-radius: 15px;
    border-left: 5px solid #22c55e;
    color: #dcfce7;
    line-height: 1.8;
}

.rag-card {
    background: rgba(250,204,21,0.14);
    padding: 18px;
    border-radius: 15px;
    border-left: 5px solid #facc15;
    color: #fef3c7;
    line-height: 1.8;
}

.job-card {
    background: rgba(124,58,237,0.16);
    padding: 18px;
    border-radius: 15px;
    border-left: 5px solid #a855f7;
    color: white;
    line-height: 1.8;
}

.scheme-card {
    background: rgba(59,130,246,0.16);
    padding: 18px;
    border-radius: 15px;
    border-left: 5px solid #3b82f6;
    color: white;
    line-height: 1.8;
}

.timeline-card {
    background: rgba(255,255,255,0.07);
    padding: 14px;
    border-radius: 14px;
    border-left: 5px solid #22c55e;
    margin-bottom: 10px;
    color: white;
}

.danger-card {
    background: rgba(220,38,38,0.16);
    padding: 18px;
    border-radius: 15px;
    border-left: 5px solid #dc2626;
    color: #fecaca;
}
</style>
""", unsafe_allow_html=True)


def generate_pdf(data):
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer)

    pdf.setTitle("SmartAid Beneficiary Report")

    y = 800

    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(50, y, "SmartAid Beneficiary Report")

    y -= 40

    pdf.setFont("Helvetica", 11)

    fields = [
        ("Name", data.get("name")),
        ("Age", data.get("age")),
        ("Gender", data.get("gender")),
        ("Skill", data.get("skill")),
        ("Health Condition", data.get("health_condition")),
        ("Disability", data.get("disability")),
        ("Work Willingness", data.get("work_willingness")),
        ("Physical Fitness", data.get("physical_fitness")),
        ("Family Status", data.get("family_status")),
        ("Education Status", data.get("education_status")),
        ("Location", data.get("location")),
        ("Status", data.get("status", "Pending")),
        ("Assigned Job", data.get("assigned_job", "Not assigned")),
        ("Employer", data.get("employer_name", "Not assigned")),
        ("Assigned Scheme", data.get("assigned_scheme", "Not assigned")),
        ("Scheme Department", data.get("scheme_department", "Not assigned")),
    ]

    for label, value in fields:
        pdf.drawString(50, y, f"{label}: {value}")
        y -= 20

    y -= 10

    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, y, "AI Recommendation:")
    y -= 18

    pdf.setFont("Helvetica", 10)
    ai_text = str(data.get("ai_recommendation", "Not generated"))

    for line in ai_text.split("\n"):
        if y < 60:
            pdf.showPage()
            y = 800
        pdf.drawString(50, y, line[:90])
        y -= 15

    y -= 10

    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, y, "RAG Recommendation:")
    y -= 18

    pdf.setFont("Helvetica", 10)
    rag_text = str(data.get("rag_recommendation", "Not generated"))

    for line in rag_text.split("\n"):
        if y < 60:
            pdf.showPage()
            y = 800
        pdf.drawString(50, y, line[:90])
        y -= 15

    pdf.save()
    buffer.seek(0)
    return buffer


st.markdown('<div class="page-title">👤 Person Profile Manager</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="page-subtitle">Complete case-management view for beneficiary profile, AI/RAG recommendations, job, scheme, status timeline and reports.</div>',
    unsafe_allow_html=True
)

people_docs = list(db.collection("people").stream())

if len(people_docs) == 0:
    st.warning("No registered people found.")
else:
    people_options = {}

    for doc in people_docs:
        data = doc.to_dict()
        label = (
            f"{data.get('name', 'Unknown')} | "
            f"Age {data.get('age', 'N/A')} | "
            f"{data.get('location', 'No Location')}"
        )

        people_options[label] = {
            "id": doc.id,
            "data": data
        }

    selected_label = st.selectbox("Select Person", list(people_options.keys()))

    selected = people_options[selected_label]
    person_id = selected["id"]
    data = selected["data"]

    fields_for_completion = [
        "name",
        "age",
        "gender",
        "skill",
        "location",
        "photo_path",
        "ai_recommendation"
    ]

    filled = sum(1 for field in fields_for_completion if data.get(field))
    completion = int((filled / len(fields_for_completion)) * 100)

    col1, col2 = st.columns([1, 1.5])

    # -----------------------
    # Left Profile Card
    # -----------------------
    with col1:
        
        st.subheader("📌 Profile Summary")

        photo_path = data.get("photo_path", "")

        if photo_path and os.path.exists(photo_path):
            st.image(photo_path, caption="Person Photo", width=240)
        elif photo_path:
            st.warning("Photo path found, but image file is missing locally.")
        else:
            st.info("No photo uploaded.")

        st.metric("Profile Completion", f"{completion}%")
        st.progress(completion / 100)

        st.markdown(f"""
        <div class="profile-card">
        <b>Name:</b> {data.get("name", "N/A")}<br>
        <b>Age:</b> {data.get("age", "N/A")}<br>
        <b>Gender:</b> {data.get("gender", "N/A")}<br>
        <b>Skill:</b> {data.get("skill", "N/A")}<br>
        <b>Health:</b> {data.get("health_condition", "N/A")}<br>
        <b>Disability:</b> {data.get("disability", "N/A")}<br>
        <b>Work Willingness:</b> {data.get("work_willingness", "N/A")}<br>
        <b>Physical Fitness:</b> {data.get("physical_fitness", "N/A")}<br>
        <b>Family Status:</b> {data.get("family_status", "N/A")}<br>
        <b>Education:</b> {data.get("education_status", "N/A")}<br>
        <b>Location:</b> {data.get("location", "N/A")}<br>
        <b>Current Status:</b> {data.get("status", "Pending")}
        </div>
        """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("📍 GPS Location")

        lat = data.get("latitude")
        lon = data.get("longitude")

        if lat is not None and lon is not None:
            map_df = pd.DataFrame([{"lat": lat, "lon": lon}])
            st.map(map_df)
        else:
            st.info("No GPS data available.")

        st.markdown("</div>", unsafe_allow_html=True)

    # -----------------------
    # Right Tabs
    # -----------------------
    with col2:
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "🤖 AI/RAG",
            "💼 Job",
            "🏛 Scheme",
            "📝 Status",
            "📄 Export/Delete"
        ])

        with tab1:
            st.subheader("🤖 Basic AI Recommendation")
            st.markdown(f"""
            <div class="ai-card">
            {data.get("ai_recommendation", "No basic AI recommendation available.")}
            </div>
            """, unsafe_allow_html=True)

            st.write("")

            st.subheader("📚 RAG Scheme Recommendation")
            st.markdown(f"""
            <div class="rag-card">
            {data.get("rag_recommendation", "No RAG recommendation generated yet.")}
            </div>
            """, unsafe_allow_html=True)

        with tab2:
            st.subheader("💼 Job Information")
            st.markdown(f"""
            <div class="job-card">
            <b>Assigned Job:</b> {data.get("assigned_job", "Not assigned")}<br>
            <b>Employer Name:</b> {data.get("employer_name", "Not assigned")}<br>
            <b>Job Location:</b> {data.get("job_location", "Not assigned")}<br>
            <b>Salary:</b> ₹{data.get("salary", "Not assigned")}
            </div>
            """, unsafe_allow_html=True)

        with tab3:
            st.subheader("🏛 Scheme Information")
            st.markdown(f"""
            <div class="scheme-card">
            <b>Assigned Scheme:</b> {data.get("assigned_scheme", "Not assigned")}<br>
            <b>Scheme Department:</b> {data.get("scheme_department", "Not assigned")}<br>
            <b>Benefit Amount:</b> ₹{data.get("benefit_amount", "Not assigned")}
            </div>
            """, unsafe_allow_html=True)

        with tab4:
            st.subheader("📌 Update Support Status")

            status_options = [
                "Pending",
                "Verified",
                "Training Assigned",
                "Job Assigned",
                "Scheme Assigned",
                "Employed",
                "Support Completed"
            ]

            current_status = data.get("status", "Pending")

            new_status = st.selectbox(
                "Status",
                status_options,
                index=status_options.index(current_status) if current_status in status_options else 0
            )

            admin_notes = st.text_area(
                "Admin Notes",
                value=data.get("admin_notes", "")
            )

            if st.button("Update Profile Status", use_container_width=True):
                status_history = data.get("status_history", [])

                status_history.append({
                    "status": new_status,
                    "notes": admin_notes,
                    "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })

                db.collection("people").document(person_id).update({
                    "status": new_status,
                    "admin_notes": admin_notes,
                    "status_history": status_history
                })

                st.success("Profile updated successfully!")

            st.write("")
            st.subheader("📈 Case Timeline")

            history = data.get("status_history", [])

            if len(history) == 0:
                st.info("No status history available.")
            else:
                for item in reversed(history):
                    st.markdown(f"""
                    <div class="timeline-card">
                    <b>Status:</b> {item.get("status")}<br>
                    <b>Notes:</b> {item.get("notes", "")}<br>
                    <b>Updated At:</b> {item.get("updated_at")}
                    </div>
                    """, unsafe_allow_html=True)

        with tab5:
            st.subheader("📄 Beneficiary Report")

            if REPORTLAB_AVAILABLE:
                pdf_buffer = generate_pdf(data)

                st.download_button(
                    label="Download Beneficiary PDF Report",
                    data=pdf_buffer,
                    file_name=f"{data.get('name', 'beneficiary')}_report.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            else:
                st.warning("PDF export requires reportlab. Install using: pip install reportlab")

            st.write("")
            st.subheader("🗑 Danger Zone")

            st.markdown("""
            <div class="danger-card">
            Deleting a person record is permanent. Please confirm carefully before deleting.
            </div>
            """, unsafe_allow_html=True)

            confirm_delete = st.checkbox("I understand this action cannot be undone.")

            if st.button("Delete Person Record", use_container_width=True):
                if confirm_delete:
                    db.collection("people").document(person_id).delete()
                    st.error("Person record deleted. Refresh the page.")
                else:
                    st.warning("Please confirm deletion before proceeding.")