import streamlit as st
import pandas as pd
import plotly.express as px
from collections import Counter
from firebase_config import db
from auth import check_login, get_role, logout

check_login()
logout()

role = get_role()

if role != "Admin":
    st.error("Access denied. Admin only.")
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

.dashboard-title {
    font-size: 46px;
    font-weight: 900;
    color: white;
    margin-bottom: 5px;
}

.dashboard-subtitle {
    color: #cbd5e1;
    font-size: 17px;
    margin-bottom: 25px;
}

.kpi-card {
    padding: 24px;
    border-radius: 22px;
    color: white;
    box-shadow: 0px 12px 30px rgba(0,0,0,0.30);
    min-height: 150px;
}

.kpi-number {
    font-size: 44px;
    font-weight: 900;
}

.kpi-label {
    font-size: 17px;
    font-weight: 700;
}

.card-blue {
    background: linear-gradient(135deg, #2563eb, #06b6d4);
}

.card-green {
    background: linear-gradient(135deg, #059669, #22c55e);
}

.card-purple {
    background: linear-gradient(135deg, #7c3aed, #a855f7);
}

.card-orange {
    background: linear-gradient(135deg, #ea580c, #facc15);
}

.card-red {
    background: linear-gradient(135deg, #dc2626, #f97316);
}

.glass-card {
    background: rgba(255,255,255,0.08);
    padding: 24px;
    border-radius: 22px;
    border: 1px solid rgba(255,255,255,0.12);
    box-shadow: 0px 10px 30px rgba(0,0,0,0.25);
    margin-bottom: 20px;
}

.insight-card {
    background: rgba(34,197,94,0.13);
    color: #dcfce7;
    padding: 20px;
    border-radius: 18px;
    border-left: 6px solid #22c55e;
    font-size: 16px;
    line-height: 1.8;
}

.warning-card {
    background: rgba(250,204,21,0.14);
    color: #fef3c7;
    padding: 20px;
    border-radius: 18px;
    border-left: 6px solid #facc15;
    font-size: 16px;
    line-height: 1.8;
}

.activity-card {
    background: rgba(255,255,255,0.07);
    padding: 15px;
    border-radius: 15px;
    border: 1px solid rgba(255,255,255,0.10);
    margin-bottom: 10px;
}

.small-text {
    color: #cbd5e1;
    font-size: 14px;
}
</style>
""", unsafe_allow_html=True)

# -----------------------
# Load Data
# -----------------------
people_docs = list(db.collection("people").stream())
people_data = [doc.to_dict() for doc in people_docs]

total_people = len(people_data)
work_willing = sum(1 for p in people_data if p.get("work_willingness") == "Yes")
disabled = sum(1 for p in people_data if p.get("disability") == "Yes")
minors = sum(1 for p in people_data if p.get("age", 0) < 18)
job_assigned = sum(1 for p in people_data if p.get("status") == "Job Assigned")
scheme_assigned = sum(1 for p in people_data if p.get("status") == "Scheme Assigned")
pending = sum(1 for p in people_data if p.get("status", "Pending") == "Pending")
employed = sum(1 for p in people_data if p.get("status") == "Employed")

# -----------------------
# Header
# -----------------------
st.markdown('<div class="dashboard-title">📊 SmartAid Command Center</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="dashboard-subtitle">Real-time welfare registration, workforce allocation, scheme support and social inclusion monitoring.</div>',
    unsafe_allow_html=True
)

# -----------------------
# KPI Cards
# -----------------------
k1, k2, k3, k4, k5 = st.columns(5)

with k1:
    st.markdown(f"""
    <div class="kpi-card card-blue">
        <div class="kpi-number">{total_people}</div>
        <div class="kpi-label">👥 Total Registered</div>
        <div class="small-text">All beneficiaries</div>
    </div>
    """, unsafe_allow_html=True)

with k2:
    st.markdown(f"""
    <div class="kpi-card card-green">
        <div class="kpi-number">{work_willing}</div>
        <div class="kpi-label">💼 Work Ready</div>
        <div class="small-text">Ready for employment</div>
    </div>
    """, unsafe_allow_html=True)

with k3:
    st.markdown(f"""
    <div class="kpi-card card-purple">
        <div class="kpi-number">{scheme_assigned}</div>
        <div class="kpi-label">🏛 Schemes</div>
        <div class="small-text">Scheme assigned</div>
    </div>
    """, unsafe_allow_html=True)

with k4:
    st.markdown(f"""
    <div class="kpi-card card-orange">
        <div class="kpi-number">{minors}</div>
        <div class="kpi-label">🧒 Students</div>
        <div class="small-text">Education support</div>
    </div>
    """, unsafe_allow_html=True)

with k5:
    st.markdown(f"""
    <div class="kpi-card card-red">
        <div class="kpi-number">{pending}</div>
        <div class="kpi-label">⚠ Pending</div>
        <div class="small-text">Need action</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

if total_people == 0:
    st.warning("No registered people found.")
else:
    locations = [p.get("location", "Unknown") for p in people_data]
    skills = [p.get("skill", "Unknown") for p in people_data]
    statuses = [p.get("status", "Pending") for p in people_data]

    location_count = Counter(locations)
    skill_count = Counter(skills)
    status_count = Counter(statuses)

    # -----------------------
    # Charts Row
    # -----------------------
    c1, c2 = st.columns([1.2, 1])

    with c1:
        
        st.subheader("📍 Location Distribution")

        df_location = pd.DataFrame({
            "Location": list(location_count.keys()),
            "Count": list(location_count.values())
        })

        fig_location = px.bar(
            df_location,
            x="Location",
            y="Count",
            text="Count",
            color="Count",
            color_continuous_scale="teal"
        )

        fig_location.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="white",
            height=380,
            margin=dict(l=20, r=20, t=30, b=20)
        )

        st.plotly_chart(fig_location, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        
        st.subheader("🛠 Skill Distribution")

        df_skill = pd.DataFrame({
            "Skill": list(skill_count.keys()),
            "Count": list(skill_count.values())
        })

        fig_skill = px.pie(
            df_skill,
            names="Skill",
            values="Count",
            hole=0.45
        )

        fig_skill.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="white",
            height=380,
            margin=dict(l=20, r=20, t=30, b=20)
        )

        st.plotly_chart(fig_skill, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # -----------------------
    # Status + AI Insight Row
    # -----------------------
    s1, s2 = st.columns([1.2, 1])

    with s1:
        
        st.subheader("📌 Support Progress")

        df_status = pd.DataFrame({
            "Status": list(status_count.keys()),
            "Count": list(status_count.values())
        })

        fig_status = px.bar(
            df_status,
            x="Count",
            y="Status",
            orientation="h",
            text="Count",
            color="Status"
        )

        fig_status.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="white",
            height=350,
            margin=dict(l=20, r=20, t=30, b=20),
            showlegend=False
        )

        st.plotly_chart(fig_status, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with s2:
        top_location = max(location_count, key=location_count.get)
        top_skill = max(skill_count, key=skill_count.get)

        st.subheader("🤖 AI Operational Insights")

        st.markdown(f"""
        <div class="insight-card">
        ✅ Highest concentration area: <b>{top_location}</b><br>
        ✅ Most common skill group: <b>{top_skill}</b><br>
        ✅ Work-ready beneficiaries: <b>{work_willing}</b><br>
        ✅ Job assigned cases: <b>{job_assigned}</b><br>
        ✅ Scheme assigned cases: <b>{scheme_assigned}</b>
        </div>
        """, unsafe_allow_html=True)

        st.write("")

        st.markdown(f"""
        <div class="warning-card">
        ⚠ Pending cases requiring field verification: <b>{pending}</b><br>
        🧒 Children requiring education support: <b>{minors}</b><br>
        ♿ Disabled beneficiaries requiring assistance: <b>{disabled}</b>
        </div>
        """, unsafe_allow_html=True)

    # -----------------------
    # Live Map
    # -----------------------
    
    st.subheader("🌍 Live Registration Map")

    map_rows = []

    for p in people_data:
        lat = p.get("latitude")
        lon = p.get("longitude")

        if lat is not None and lon is not None:
            map_rows.append({
                "lat": lat,
                "lon": lon
            })

    if len(map_rows) > 0:
        map_df = pd.DataFrame(map_rows)
        st.map(map_df)
    else:
        st.info("No GPS coordinates available.")

    st.markdown("</div>", unsafe_allow_html=True)

    # -----------------------
    # Impact Summary
    # -----------------------
    st.subheader("🌟 SmartAid Impact Summary")

    i1, i2, i3, i4 = st.columns(4)

    with i1:
        st.metric("Jobs Assigned", job_assigned)

    with i2:
        st.metric("Schemes Assigned", scheme_assigned)

    with i3:
        st.metric("Employed", employed)

    with i4:
        st.metric("Pending Follow-up", pending)

    # -----------------------
    # Recent Activity Cards
    # -----------------------
    st.subheader("🕒 Recent Registrations")

    recent_people = people_data[-5:]

    for p in reversed(recent_people):
        st.markdown(f"""
        <div class="activity-card">
        <b>👤 {p.get("name", "Unknown")}</b><br>
        📍 {p.get("location", "Unknown")} |
        🛠 {p.get("skill", "Unknown")} |
        📌 Status: <b>{p.get("status", "Pending")}</b>
        </div>
        """, unsafe_allow_html=True)

    # -----------------------
    # Full Table
    # -----------------------
    st.subheader("📋 Full Beneficiary Records")

    table_data = []

    for p in people_data:
        table_data.append({
            "Name": p.get("name"),
            "Age": p.get("age"),
            "Gender": p.get("gender"),
            "Skill": p.get("skill"),
            "Location": p.get("location"),
            "Volunteer": p.get("volunteer_name", "Unknown"),
            "Status": p.get("status", "Pending"),
            "AI Recommendation": p.get("ai_recommendation", "Not generated")
        })

    df_people = pd.DataFrame(table_data)

    st.dataframe(df_people, use_container_width=True)