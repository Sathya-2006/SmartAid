import os
import streamlit as st
from firebase_config import db
from auth import check_login, get_role, logout

check_login()
logout()

role = get_role()

if role not in ["Admin", "Volunteer"]:
    st.error("Access denied. Admin/Volunteer only.")
    st.stop()

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
    font-size: 46px;
    font-weight: 900;
    color: white;
    margin-bottom: 5px;
}

.page-subtitle {
    color: #cbd5e1;
    font-size: 17px;
    margin-bottom: 25px;
}

.profile-card {
    background: rgba(255,255,255,0.08);
    padding: 24px;
    border-radius: 22px;
    border: 1px solid rgba(255,255,255,0.12);
    box-shadow: 0px 10px 30px rgba(0,0,0,0.25);
    margin-bottom: 20px;
}

.ai-card {
    background: rgba(14,165,233,0.16);
    padding: 22px;
    border-radius: 18px;
    border-left: 6px solid #0ea5e9;
    color: #e0f2fe;
    font-size: 16px;
    line-height: 1.7;
}

.rag-card {
    background: rgba(34,197,94,0.14);
    padding: 22px;
    border-radius: 18px;
    border-left: 6px solid #22c55e;
    color: #dcfce7;
    font-size: 16px;
    line-height: 1.7;
}

.status-card {
    background: rgba(250,204,21,0.14);
    padding: 22px;
    border-radius: 18px;
    border-left: 6px solid #facc15;
    color: #fef3c7;
    font-size: 16px;
    line-height: 1.7;
}

.detail-row {
    background: rgba(255,255,255,0.06);
    padding: 12px;
    border-radius: 12px;
    margin-bottom: 8px;
    color: white;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="page-title">🤖 AI Recommendations</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="page-subtitle">View beneficiary profile, AI recommendation, RAG scheme recommendation and update support status.</div>',
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
            f"{data.get('name', 'Unknown')} - "
            f"{data.get('skill', 'No Skill')} - "
            f"{data.get('location', 'No Location')}"
        )

        people_options[label] = {
            "id": doc.id,
            "data": data
        }

    selected_label = st.selectbox("Select Person", list(people_options.keys()))

    selected_person = people_options[selected_label]
    person_id = selected_person["id"]
    data = selected_person["data"]

    col1, col2 = st.columns([1, 1.3])

    # -----------------------
    # LEFT SIDE
    # -----------------------
    with col1:
        
        st.subheader("👤 Person Profile")

        photo_path = data.get("photo_path", "")

        if photo_path and os.path.exists(photo_path):
            st.image(photo_path, caption="Person Photo", width=220)
        elif photo_path:
            st.warning("Photo path found, but image file is missing locally.")
        else:
            st.info("No photo uploaded.")

        st.markdown(f"""
        <div class="detail-row"><b>Name:</b> {data.get("name", "N/A")}</div>
        <div class="detail-row"><b>Age:</b> {data.get("age", "N/A")}</div>
        <div class="detail-row"><b>Gender:</b> {data.get("gender", "N/A")}</div>
        <div class="detail-row"><b>Skill:</b> {data.get("skill", "N/A")}</div>
        <div class="detail-row"><b>Health:</b> {data.get("health_condition", "N/A")}</div>
        <div class="detail-row"><b>Disability:</b> {data.get("disability", "N/A")}</div>
        <div class="detail-row"><b>Work Willingness:</b> {data.get("work_willingness", "N/A")}</div>
        <div class="detail-row"><b>Physical Fitness:</b> {data.get("physical_fitness", "N/A")}</div>
        <div class="detail-row"><b>Family Status:</b> {data.get("family_status", "N/A")}</div>
        <div class="detail-row"><b>Education Status:</b> {data.get("education_status", "N/A")}</div>
        <div class="detail-row"><b>Location:</b> {data.get("location", "N/A")}</div>
        <div class="detail-row"><b>Current Status:</b> {data.get("status", "Pending")}</div>
        """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        
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
            "Status Notes",
            value=data.get("status_notes", "")
        )

        if st.button("Update Status", width="stretch"):
            db.collection("people").document(person_id).update({
                "status": new_status,
                "status_notes": admin_notes
            })

            st.success("Status updated successfully!")

        st.markdown("</div>", unsafe_allow_html=True)

    # -----------------------
    # RIGHT SIDE
    # -----------------------
    with col2:
        

        st.subheader("🧠 Basic AI Recommendation")

        ai_recommendation = data.get(
            "ai_recommendation",
            "No recommendation generated."
        )

        st.markdown(f"""
        <div class="ai-card">
        {ai_recommendation}
        </div>
        """, unsafe_allow_html=True)

        rag_recommendation = data.get("rag_recommendation", "")

        st.write("")

        st.subheader("📚 RAG Scheme Recommendation")

        if rag_recommendation:
            st.markdown(f"""
            <div class="rag-card">
            {rag_recommendation}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="status-card">
            No RAG recommendation generated yet.  
            Go to RAG Scheme Advisor page and generate recommendation for this person.
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)