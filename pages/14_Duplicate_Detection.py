import os
import tempfile
from datetime import datetime

import streamlit as st
from deepface import DeepFace
from firebase_config import db
from auth import check_login, get_role, logout

check_login()
logout()

role = get_role()

if role != "Admin":
    st.error("Access denied. Admin only.")
    st.stop()

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #020617, #0f172a, #1e293b);
}

section[data-testid="stSidebar"] {
    background: #020617;
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
}

.subtitle {
    color: #cbd5e1;
    margin-bottom: 20px;
}

.glass-card {
    background: rgba(255,255,255,0.08);
    padding: 20px;
    border-radius: 18px;
    border: 1px solid rgba(255,255,255,0.1);
    margin-bottom: 15px;
}

.duplicate-card {
    background: rgba(220,38,38,0.15);
    padding: 18px;
    border-left: 6px solid #dc2626;
    border-radius: 15px;
    color: #fecaca;
    margin-bottom: 15px;
}

.safe-card {
    background: rgba(34,197,94,0.15);
    padding: 18px;
    border-left: 6px solid #22c55e;
    border-radius: 15px;
    color: #dcfce7;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="page-title">🧬 Face-Based Duplicate Detection</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Detect duplicate beneficiary registrations using face verification and image comparison.</div>',
    unsafe_allow_html=True
)

people_docs = list(db.collection("people").stream())

people_data = []

for doc in people_docs:
    data = doc.to_dict()
    data["doc_id"] = doc.id
    people_data.append(data)


def compare_faces(img1_path, img2_path):
    try:
        result = DeepFace.verify(
            img1_path=img1_path,
            img2_path=img2_path,
            model_name="Facenet512",
            enforce_detection=False
        )

        verified = result.get("verified", False)
        distance = round(result.get("distance", 999), 3)

        return verified, distance

    except Exception:
        return False, 999


def get_risk_level(distance):
    if distance < 0.25:
        return "High"
    elif distance < 0.40:
        return "Medium"
    else:
        return "Low"


photo_count = sum(
    1 for p in people_data
    if p.get("photo_path") and os.path.exists(p.get("photo_path"))
)

duplicate_alerts = list(db.collection("duplicate_alerts").stream())

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Registered People", len(people_data))

with col2:
    st.metric("Photos Available", photo_count)

with col3:
    st.metric("Duplicate Alerts", len(duplicate_alerts))

tab1, tab2 = st.tabs(["Check New Photo", "Auto Scan Database"])

with tab1:

    st.subheader("Upload Photo to Check Duplicate")

    uploaded_photo = st.file_uploader(
        "Upload beneficiary photo",
        type=["jpg", "jpeg", "png"]
    )

    if uploaded_photo is not None:
        st.image(uploaded_photo, caption="Photo to Check", width=220)

        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        temp_file.write(uploaded_photo.getbuffer())
        temp_file.close()

        if st.button("Check Duplicate", use_container_width=True):
            matches = []

            for person in people_data:
                photo_path = person.get("photo_path", "")

                if photo_path and os.path.exists(photo_path):
                    verified, distance = compare_faces(
                        temp_file.name,
                        photo_path
                    )

                    if verified:
                        matches.append({
                            "person": person,
                            "distance": distance,
                            "risk": get_risk_level(distance)
                        })

            if len(matches) == 0:
                st.markdown("""
                <div class="safe-card">
                ✅ No duplicate face found.
                </div>
                """, unsafe_allow_html=True)

            else:
                st.error("Possible duplicate face found!")

                for match in matches:
                    person = match["person"]
                    distance = match["distance"]
                    risk = match["risk"]

                    db.collection("duplicate_alerts").add({
                        "matched_person_name": person.get("name"),
                        "matched_person_id": person.get("doc_id"),
                        "distance": distance,
                        "risk": risk,
                        "created_at": datetime.now()
                    })

                    st.markdown(f"""
                    <div class="duplicate-card">
                    <b>⚠ Duplicate Risk:</b> {risk}<br>
                    <b>Similarity Distance:</b> {distance}<br>
                    <b>Name:</b> {person.get("name")}<br>
                    <b>Age:</b> {person.get("age")}<br>
                    <b>Location:</b> {person.get("location")}<br>
                    <b>Status:</b> {person.get("status", "Pending")}
                    </div>
                    """, unsafe_allow_html=True)

                    existing_photo = person.get("photo_path", "")

                    c1, c2 = st.columns(2)

                    with c1:
                        st.image(temp_file.name, caption="Uploaded Photo", width=220)

                    with c2:
                        if existing_photo and os.path.exists(existing_photo):
                            st.image(existing_photo, caption="Existing Photo", width=220)

    st.markdown("</div>", unsafe_allow_html=True)

with tab2:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("Auto Scan Existing Beneficiary Photos")

    st.warning("This may take time if many photos are stored.")

    if st.button("Scan Existing Photos", use_container_width=True):
        duplicates = []

        for i in range(len(people_data)):
            for j in range(i + 1, len(people_data)):
                p1 = people_data[i]
                p2 = people_data[j]

                path1 = p1.get("photo_path", "")
                path2 = p2.get("photo_path", "")

                if path1 and path2 and os.path.exists(path1) and os.path.exists(path2):
                    verified, distance = compare_faces(path1, path2)

                    if verified:
                        risk = get_risk_level(distance)

                        duplicates.append({
                            "p1": p1,
                            "p2": p2,
                            "distance": distance,
                            "risk": risk
                        })

                        db.collection("duplicate_alerts").add({
                            "person1": p1.get("name"),
                            "person2": p2.get("name"),
                            "person1_id": p1.get("doc_id"),
                            "person2_id": p2.get("doc_id"),
                            "distance": distance,
                            "risk": risk,
                            "created_at": datetime.now()
                        })

        if len(duplicates) == 0:
            st.markdown("""
            <div class="safe-card">
            ✅ No duplicate faces found in database.
            </div>
            """, unsafe_allow_html=True)

        else:
            st.error(f"{len(duplicates)} possible duplicate pair(s) found.")

            for item in duplicates:
                p1 = item["p1"]
                p2 = item["p2"]

                st.markdown(f"""
                <div class="duplicate-card">
                <b>Risk:</b> {item["risk"]}<br>
                <b>Distance:</b> {item["distance"]}<br>
                <b>Person 1:</b> {p1.get("name")} - {p1.get("location")}<br>
                <b>Person 2:</b> {p2.get("name")} - {p2.get("location")}
                </div>
                """, unsafe_allow_html=True)

                c1, c2 = st.columns(2)

                with c1:
                    if os.path.exists(p1.get("photo_path", "")):
                        st.image(p1.get("photo_path"), caption=p1.get("name"), width=220)

                with c2:
                    if os.path.exists(p2.get("photo_path", "")):
                        st.image(p2.get("photo_path"), caption=p2.get("name"), width=220)

    st.markdown("</div>", unsafe_allow_html=True)