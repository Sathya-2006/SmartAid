import os
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from collections import Counter
from firebase_config import db
from auth import check_login, get_role, logout

check_login()
logout()

role = get_role()

if role != "Admin":
    st.error("Access denied. Admin only.")
    st.stop()

# ---------------------------------------------------
# THEME
# ---------------------------------------------------
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

.kpi-card {
    padding: 18px;
    border-radius: 18px;
    color: white;
    text-align: center;
    box-shadow: 0px 8px 25px rgba(0,0,0,0.30);
    min-height: 120px;
}

.kpi-card h2 {
    margin-bottom: 4px;
}

.blue {
    background: linear-gradient(135deg, #2563eb, #06b6d4);
}

.green {
    background: linear-gradient(135deg, #16a34a, #22c55e);
}

.orange {
    background: linear-gradient(135deg, #ea580c, #facc15);
}

.purple {
    background: linear-gradient(135deg, #7c3aed, #a855f7);
}

.glass {
    background: rgba(255,255,255,0.08);
    padding: 20px;
    border-radius: 18px;
    border: 1px solid rgba(255,255,255,0.1);
    margin-bottom: 15px;
}

.volunteer-card {
    background: rgba(14,165,233,0.14);
    padding: 15px;
    border-left: 5px solid #0ea5e9;
    border-radius: 12px;
    margin-bottom: 10px;
    color: white;
}

.rank-card {
    background: rgba(34,197,94,0.14);
    padding: 15px;
    border-left: 5px solid #22c55e;
    border-radius: 12px;
    margin-bottom: 10px;
    color: white;
}

/* Center Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 16px;
    justify-content: center;
    width: fit-content;
    margin: auto;
    background: rgba(255,255,255,0.06);
    padding: 8px;
    border-radius: 16px;
}

/* Individual Tabs */
.stTabs [data-baseweb="tab"] {
    height: 46px;
    padding: 0px 24px;
    border-radius: 12px;
    color: white !important;
    font-weight: 700;
    background: transparent;
}

/* Active Tab */
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #2563eb, #06b6d4) !important;
    color: white !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown(
    '<div class="page-title">🙋 Volunteer Operations Center</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Manage volunteers, monitor field performance and outreach activities.</div>',
    unsafe_allow_html=True
)

# ---------------------------------------------------
# KPI DASHBOARD
# ---------------------------------------------------
volunteer_docs = list(db.collection("volunteers").stream())
volunteers = [v.to_dict() for v in volunteer_docs]

total_volunteers = len(volunteers)

active_count = sum(
    1 for v in volunteers
    if v.get("status", "Active") == "Active"
)

inactive_count = total_volunteers - active_count

people_docs = list(db.collection("people").stream())
people_data = [p.to_dict() for p in people_docs]

total_registrations = len(people_data)

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""
    <div class="kpi-card blue">
        <h2>{total_volunteers}</h2>
        <b>Volunteers</b>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="kpi-card green">
        <h2>{active_count}</h2>
        <b>Active</b>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="kpi-card orange">
        <h2>{inactive_count}</h2>
        <b>Inactive</b>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class="kpi-card purple">
        <h2>{total_registrations}</h2>
        <b>Registrations</b>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(
    [
        "➕ Add Volunteer",
        "👥 Volunteers",
        "📈 Performance"
    ]
)

# ---------------------------------------------------
# TAB 1
# ---------------------------------------------------
with tab1:
    

    st.subheader("Add New Volunteer")

    volunteer_name = st.text_input("Volunteer Name")
    phone = st.text_input("Phone Number")
    email = st.text_input("Email")
    assigned_area = st.text_input("Assigned Area")
    organization = st.text_input("NGO / Organization")

    photo = st.file_uploader(
        "Volunteer Photo",
        type=["jpg", "jpeg", "png"]
    )

    if st.button("Add Volunteer", width="stretch"):
        if volunteer_name.strip() == "":
            st.error("Enter volunteer name.")
        else:
            photo_path = ""

            if photo:
                if not os.path.exists("volunteer_photos"):
                    os.makedirs("volunteer_photos")

                safe_name = volunteer_name.replace(" ", "_")
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                photo_path = f"volunteer_photos/{safe_name}_{timestamp}.png"

                with open(photo_path, "wb") as f:
                    f.write(photo.getbuffer())

            db.collection("volunteers").add({
                "volunteer_name": volunteer_name,
                "phone": phone,
                "email": email,
                "assigned_area": assigned_area,
                "organization": organization,
                "photo_path": photo_path,
                "status": "Active",
                "created_at": datetime.now()
            })

            st.success("Volunteer added successfully.")

    st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------
# TAB 2
# ---------------------------------------------------
with tab2:
    st.subheader("Volunteer Directory")

    if len(volunteer_docs) == 0:
        st.warning("No volunteers available.")
    else:
        for v in volunteer_docs:
            data = v.to_dict()

            st.markdown('<div class="glass">', unsafe_allow_html=True)

            col1, col2 = st.columns([1, 3])

            with col1:
                photo_path = data.get("photo_path", "")

                if photo_path and os.path.exists(photo_path):
                    st.image(photo_path, width=120)
                else:
                    st.info("No photo")

            with col2:
                st.markdown(f"""
                <div class="volunteer-card">
                    <b>Name:</b> {data.get('volunteer_name')}<br>
                    <b>Phone:</b> {data.get('phone')}<br>
                    <b>Email:</b> {data.get('email')}<br>
                    <b>Area:</b> {data.get('assigned_area')}<br>
                    <b>Organization:</b> {data.get('organization')}<br>
                    <b>Status:</b> {data.get('status', 'Active')}
                </div>
                """, unsafe_allow_html=True)

                current_status = data.get("status", "Active")

                status_options = ["Active", "Inactive"]

                new_status = st.selectbox(
                    "Update Status",
                    status_options,
                    index=status_options.index(current_status) if current_status in status_options else 0,
                    key=f"status_{v.id}"
                )

                if st.button(
                    f"Update {data.get('volunteer_name')}",
                    key=f"btn_{v.id}",
                    width="stretch"
                ):
                    db.collection("volunteers").document(v.id).update({
                        "status": new_status
                    })

                    st.success("Volunteer status updated.")

            st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------
# TAB 3
# ---------------------------------------------------
with tab3:
    st.subheader("Volunteer Performance Dashboard")

    volunteer_names = [
        p.get("volunteer_name", "Unknown")
        for p in people_data
    ]

    volunteer_count = Counter(volunteer_names)

    if len(volunteer_count) == 0:
        st.warning("No registrations found.")
    else:
        ranking_df = pd.DataFrame({
            "Volunteer": list(volunteer_count.keys()),
            "Registrations": list(volunteer_count.values())
        })

        ranking_df = ranking_df.sort_values(
            "Registrations",
            ascending=False
        )

        col1, col2 = st.columns([1, 1.2])

        with col1:
            st.subheader("🏆 Leaderboard")

            for _, row in ranking_df.iterrows():
                st.markdown(f"""
                <div class="rank-card">
                    🏅 <b>{row['Volunteer']}</b><br>
                    Registrations: <b>{row['Registrations']}</b>
                </div>
                """, unsafe_allow_html=True)

        with col2:
            st.subheader("📊 Registration Chart")

            fig = px.bar(
                ranking_df,
                x="Volunteer",
                y="Registrations",
                text="Registrations",
                color="Registrations"
            )

            fig.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font_color="white",
                height=380,
                margin=dict(l=20, r=20, t=30, b=20)
            )

            st.plotly_chart(fig, width="stretch")

        st.subheader("📍 Area Coverage")

        area_list = [
            v.get("assigned_area", "Unknown")
            for v in volunteers
        ]

        area_count = Counter(area_list)

        area_df = pd.DataFrame({
            "Area": list(area_count.keys()),
            "Count": list(area_count.values())
        })

        st.dataframe(area_df, width="stretch")