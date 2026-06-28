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
.card-orange { background: linear-gradient(135deg, #ea580c, #facc15); }
.card-red { background: linear-gradient(135deg, #dc2626, #f97316); }

.glass-card {
    background: rgba(255,255,255,0.08);
    padding: 24px;
    border-radius: 22px;
    border: 1px solid rgba(255,255,255,0.12);
    box-shadow: 0px 10px 30px rgba(0,0,0,0.25);
    margin-bottom: 20px;
}

.high-card {
    background: rgba(220,38,38,0.18);
    border-left: 6px solid #dc2626;
    padding: 16px;
    border-radius: 15px;
    color: #fecaca;
    margin-bottom: 10px;
}

.medium-card {
    background: rgba(250,204,21,0.18);
    border-left: 6px solid #facc15;
    padding: 16px;
    border-radius: 15px;
    color: #fef3c7;
    margin-bottom: 10px;
}

.low-card {
    background: rgba(34,197,94,0.18);
    border-left: 6px solid #22c55e;
    padding: 16px;
    border-radius: 15px;
    color: #dcfce7;
    margin-bottom: 10px;
}

.ai-card {
    background: rgba(14,165,233,0.15);
    border-left: 6px solid #0ea5e9;
    padding: 20px;
    border-radius: 18px;
    color: #e0f2fe;
    line-height: 1.8;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="page-title">🔥 Heatmap Analytics</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="page-subtitle">Identify high-priority areas, outreach hotspots and location-wise beneficiary concentration.</div>',
    unsafe_allow_html=True
)

people_docs = list(db.collection("people").stream())
people_data = [doc.to_dict() for doc in people_docs]

if len(people_data) == 0:
    st.warning("No registered people found.")
else:
    map_rows = []

    for p in people_data:
        lat = p.get("latitude")
        lon = p.get("longitude")

        if lat is not None and lon is not None:
            map_rows.append({
                "lat": lat,
                "lon": lon,
                "name": p.get("name", "Unknown"),
                "location": p.get("location", "Unknown"),
                "status": p.get("status", "Pending")
            })

    location_count = Counter([p.get("location", "Unknown") for p in people_data])
    total_people = len(people_data)
    total_locations = len(location_count)

    hotspot_rows = []

    for location, count in location_count.items():
        if count >= 10:
            risk = "High"
        elif count >= 5:
            risk = "Medium"
        else:
            risk = "Low"

        hotspot_rows.append({
            "Location": location,
            "Registered People": count,
            "Risk Level": risk
        })

    hotspot_df = pd.DataFrame(hotspot_rows)

    high_count = len(hotspot_df[hotspot_df["Risk Level"] == "High"])
    medium_count = len(hotspot_df[hotspot_df["Risk Level"] == "Medium"])
    low_count = len(hotspot_df[hotspot_df["Risk Level"] == "Low"])

    # -----------------------
    # KPI Cards
    # -----------------------
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(f"""
        <div class="kpi-card card-blue">
            <div class="kpi-number">{total_people}</div>
            <div class="kpi-label">👥 Total People</div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="kpi-card card-green">
            <div class="kpi-number">{total_locations}</div>
            <div class="kpi-label">🌍 Locations</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="kpi-card card-red">
            <div class="kpi-number">{high_count}</div>
            <div class="kpi-label">🔴 High Risk Areas</div>
        </div>
        """, unsafe_allow_html=True)

    with c4:
        st.markdown(f"""
        <div class="kpi-card card-orange">
            <div class="kpi-number">{medium_count}</div>
            <div class="kpi-label">🟡 Medium Risk Areas</div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")

    if len(map_rows) == 0:
        st.warning("No GPS data found.")
    else:
        df = pd.DataFrame(map_rows)

        # -----------------------
        # Map
        # -----------------------
        
        st.subheader("🗺 People Location Map")
        st.map(df[["lat", "lon"]])
        st.markdown("</div>", unsafe_allow_html=True)

        # -----------------------
        # Charts
        # -----------------------
        col1, col2 = st.columns([1.2, 1])

        with col1:
            
            st.subheader("📊 Area-wise Hotspot Chart")

            fig = px.bar(
                hotspot_df,
                x="Location",
                y="Registered People",
                color="Risk Level",
                text="Registered People",
                title="Location Risk Distribution"
            )

            fig.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font_color="white",
                height=380
            )

            st.plotly_chart(fig, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with col2:
            
            st.subheader("🎯 Risk Level Split")

            risk_count = Counter(hotspot_df["Risk Level"])

            risk_df = pd.DataFrame({
                "Risk Level": list(risk_count.keys()),
                "Count": list(risk_count.values())
            })

            fig2 = px.pie(
                risk_df,
                names="Risk Level",
                values="Count",
                hole=0.45
            )

            fig2.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                font_color="white",
                height=380
            )

            st.plotly_chart(fig2, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        # -----------------------
        # Hotspot Cards
        # -----------------------
        st.subheader("🔥 Area-wise Hotspot Risk")

        for _, row in hotspot_df.iterrows():
            location = row["Location"]
            count = row["Registered People"]
            risk = row["Risk Level"]

            if risk == "High":
                css_class = "high-card"
                icon = "🔴"
            elif risk == "Medium":
                css_class = "medium-card"
                icon = "🟡"
            else:
                css_class = "low-card"
                icon = "🟢"

            st.markdown(f"""
            <div class="{css_class}">
            {icon} <b>{location}</b><br>
            Registered People: <b>{count}</b><br>
            Risk Level: <b>{risk}</b>
            </div>
            """, unsafe_allow_html=True)

        # -----------------------
        # AI Insight
        # -----------------------
        st.subheader("🤖 AI Insight")

        max_location = max(location_count, key=location_count.get)
        max_count = location_count[max_location]

        st.markdown(f"""
        <div class="ai-card">
        SmartAid has identified <b>{total_people}</b> registered people across
        <b>{total_locations}</b> locations.<br><br>

        The highest concentration is in <b>{max_location}</b> with
        <b>{max_count}</b> registered people.<br><br>

        Recommended action:<br>
        ✅ Prioritize NGO outreach in high-concentration areas.<br>
        ✅ Conduct job allocation camps in work-ready zones.<br>
        ✅ Conduct healthcare and welfare verification camps.<br>
        ✅ Use this data for future homeless hotspot prediction.
        </div>
        """, unsafe_allow_html=True)

        # -----------------------
        # Table
        # -----------------------
        st.subheader("📋 Hotspot Data Table")
        st.dataframe(hotspot_df, use_container_width=True)