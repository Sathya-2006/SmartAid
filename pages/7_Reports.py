import streamlit as st
import pandas as pd
import plotly.express as px
from firebase_config import db
from collections import Counter
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

.report-title {
    font-size: 44px;
    font-weight: 900;
    color: white;
    margin-bottom: 5px;
}

.report-subtitle {
    color: #cbd5e1;
    font-size: 17px;
    margin-bottom: 25px;
}

.kpi-card {
    padding: 22px;
    border-radius: 20px;
    color: white;
    box-shadow: 0px 10px 25px rgba(0,0,0,0.30);
    min-height: 130px;
    text-align: center;
}

.kpi-number {
    font-size: 38px;
    font-weight: 900;
}

.kpi-label {
    font-size: 16px;
    font-weight: 700;
}

.card-blue { background: linear-gradient(135deg, #2563eb, #06b6d4); }
.card-green { background: linear-gradient(135deg, #059669, #22c55e); }
.card-purple { background: linear-gradient(135deg, #7c3aed, #a855f7); }
.card-orange { background: linear-gradient(135deg, #ea580c, #facc15); }
.card-red { background: linear-gradient(135deg, #dc2626, #f97316); }
.card-gray { background: linear-gradient(135deg, #334155, #64748b); }

.glass-card {
    background: rgba(255,255,255,0.08);
    padding: 24px;
    border-radius: 22px;
    border: 1px solid rgba(255,255,255,0.12);
    box-shadow: 0px 10px 30px rgba(0,0,0,0.25);
    margin-bottom: 20px;
}

.export-card {
    background: rgba(34,197,94,0.14);
    padding: 20px;
    border-radius: 18px;
    border-left: 6px solid #22c55e;
    color: #dcfce7;
    font-weight: 600;
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

# -----------------------
# Header
# -----------------------
st.markdown('<div class="report-title">📑 Reports & Analytics</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="report-subtitle">Generate welfare, employment, scheme and beneficiary analytics reports for SmartAid operations.</div>',
    unsafe_allow_html=True
)

# -----------------------
# Load Data
# -----------------------
people_docs = list(db.collection("people").stream())
people_data = [doc.to_dict() for doc in people_docs]

if len(people_data) == 0:
    st.warning("No data available.")
else:
    total_registered = len(people_data)
    job_assigned = sum(1 for p in people_data if p.get("status") == "Job Assigned")
    scheme_assigned = sum(1 for p in people_data if p.get("status") == "Scheme Assigned")
    pending = sum(1 for p in people_data if p.get("status", "Pending") == "Pending")
    disabled = sum(1 for p in people_data if p.get("disability") == "Yes")
    students = sum(
        1 for p in people_data
        if p.get("education_status") in ["School Student", "College Student"]
    )

    # -----------------------
    # KPI Cards
    # -----------------------
    c1, c2, c3, c4, c5, c6 = st.columns(6)

    with c1:
        st.markdown(f"""
        <div class="kpi-card card-blue">
            <div class="kpi-number">{total_registered}</div>
            <div class="kpi-label">👥 Total</div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="kpi-card card-green">
            <div class="kpi-number">{job_assigned}</div>
            <div class="kpi-label">💼 Jobs</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="kpi-card card-purple">
            <div class="kpi-number">{scheme_assigned}</div>
            <div class="kpi-label">🏛 Schemes</div>
        </div>
        """, unsafe_allow_html=True)

    with c4:
        st.markdown(f"""
        <div class="kpi-card card-red">
            <div class="kpi-number">{pending}</div>
            <div class="kpi-label">⚠ Pending</div>
        </div>
        """, unsafe_allow_html=True)

    with c5:
        st.markdown(f"""
        <div class="kpi-card card-orange">
            <div class="kpi-number">{disabled}</div>
            <div class="kpi-label">♿ Disabled</div>
        </div>
        """, unsafe_allow_html=True)

    with c6:
        st.markdown(f"""
        <div class="kpi-card card-gray">
            <div class="kpi-number">{students}</div>
            <div class="kpi-label">🎓 Students</div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")

    # -----------------------
    # Charts
    # -----------------------
    chart1, chart2 = st.columns(2)

    with chart1:
        
        st.subheader("📌 Status Summary")

        status_count = Counter([p.get("status", "Pending") for p in people_data])

        df_status = pd.DataFrame({
            "Status": list(status_count.keys()),
            "Count": list(status_count.values())
        })

        fig_status = px.bar(
            df_status,
            x="Status",
            y="Count",
            text="Count",
            color="Status"
        )

        fig_status.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="white",
            height=360,
            showlegend=False
        )

        st.plotly_chart(fig_status, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with chart2:
        
        st.subheader("📍 Location Summary")

        location_count = Counter([p.get("location", "Unknown") for p in people_data])

        df_location = pd.DataFrame({
            "Location": list(location_count.keys()),
            "Count": list(location_count.values())
        })

        fig_location = px.pie(
            df_location,
            names="Location",
            values="Count",
            hole=0.45
        )

        fig_location.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="white",
            height=360
        )

        st.plotly_chart(fig_location, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # -----------------------
    # Skill Summary
    # -----------------------
    
    st.subheader("🛠 Skill Summary")

    skill_count = Counter([p.get("skill", "Unknown") for p in people_data])

    df_skill = pd.DataFrame({
        "Skill": list(skill_count.keys()),
        "Count": list(skill_count.values())
    })

    fig_skill = px.bar(
        df_skill,
        x="Skill",
        y="Count",
        text="Count",
        color="Count",
        color_continuous_scale="teal"
    )

    fig_skill.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="white",
        height=360
    )

    st.plotly_chart(fig_skill, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # -----------------------
    # Full Report Table
    # -----------------------
    st.subheader("📋 Full Report Table")

    report_rows = []

    for p in people_data:
        report_rows.append({
            "Name": p.get("name"),
            "Age": p.get("age"),
            "Gender": p.get("gender"),
            "Skill": p.get("skill"),
            "Disability": p.get("disability"),
            "Education": p.get("education_status"),
            "Location": p.get("location"),
            "Volunteer": p.get("volunteer_name", "Unknown"),
            "Status": p.get("status", "Pending"),
            "Assigned Job": p.get("assigned_job", ""),
            "Assigned Scheme": p.get("assigned_scheme", ""),
            "AI Recommendation": p.get("ai_recommendation", "")
        })

    df = pd.DataFrame(report_rows)

    st.dataframe(df, use_container_width=True)

    csv = df.to_csv(index=False).encode("utf-8")

    st.markdown("""
    <div class="export-card">
    📥 Export the complete SmartAid operational report as CSV for NGO/Government submission.
    </div>
    """, unsafe_allow_html=True)

    st.download_button(
        label="Download Report as CSV",
        data=csv,
        file_name="smartaid_report.csv",
        mime="text/csv",
        use_container_width=True
    )