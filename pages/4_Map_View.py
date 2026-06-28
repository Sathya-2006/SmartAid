import streamlit as st
import pandas as pd
from firebase_config import db
from collections import Counter
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

.card-blue {
    background: linear-gradient(135deg, #2563eb, #06b6d4);
}

.card-green {
    background: linear-gradient(135deg, #059669, #22c55e);
}

.card-orange {
    background: linear-gradient(135deg, #ea580c, #facc15);
}

.glass-card {
    background: rgba(255,255,255,0.08);
    padding: 24px;
    border-radius: 22px;
    border: 1px solid rgba(255,255,255,0.12);
    box-shadow: 0px 10px 30px rgba(0,0,0,0.25);
    margin-bottom: 20px;
}

.hotspot-high {
    background: rgba(220,38,38,0.18);
    border-left: 6px solid #dc2626;
    padding: 15px;
    border-radius: 14px;
    margin-bottom: 10px;
    color: #fecaca;
}

.hotspot-medium {
    background: rgba(250,204,21,0.18);
    border-left: 6px solid #facc15;
    padding: 15px;
    border-radius: 14px;
    margin-bottom: 10px;
    color: #fef3c7;
}

.hotspot-low {
    background: rgba(34,197,94,0.18);
    border-left: 6px solid #22c55e;
    padding: 15px;
    border-radius: 14px;
    margin-bottom: 10px;
    color: #dcfce7;
}
</style>
""", unsafe_allow_html=True)


st.markdown('<div class="page-title">🗺 Map View & Location Monitoring</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="page-subtitle">Track registered people using GPS data and identify high-priority outreach areas.</div>',
    unsafe_allow_html=True
)

people_docs = list(db.collection("people").stream())

map_data = []
locations = []

for doc in people_docs:
    data = doc.to_dict()

    latitude = data.get("latitude")
    longitude = data.get("longitude")

    if latitude is not None and longitude is not None:
        map_data.append({
            "lat": latitude,
            "lon": longitude,
            "name": data.get("name", "Unknown"),
            "skill": data.get("skill", "Unknown"),
            "location": data.get("location", "Unknown"),
            "status": data.get("status", "Pending")
        })

        locations.append(data.get("location", "Unknown"))

if len(map_data) == 0:
    st.warning("No GPS data found. Register people with latitude and longitude first.")
else:
    df = pd.DataFrame(map_data)
    location_count = Counter(locations)

    total_gps = len(map_data)
    total_locations = len(location_count)
    high_risk_count = sum(1 for _, count in location_count.items() if count >= 5)

    k1, k2, k3 = st.columns(3)

    with k1:
        st.markdown(f"""
        <div class="kpi-card card-blue">
            <div class="kpi-number">{total_gps}</div>
            <div class="kpi-label">📍 GPS Records</div>
        </div>
        """, unsafe_allow_html=True)

    with k2:
        st.markdown(f"""
        <div class="kpi-card card-green">
            <div class="kpi-number">{total_locations}</div>
            <div class="kpi-label">🌍 Locations Covered</div>
        </div>
        """, unsafe_allow_html=True)

    with k3:
        st.markdown(f"""
        <div class="kpi-card card-orange">
            <div class="kpi-number">{high_risk_count}</div>
            <div class="kpi-label">🔥 High-Risk Areas</div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")

    
    st.subheader("🌍 Registered People Map")
    st.map(df[["lat", "lon"]])
    st.markdown("</div>", unsafe_allow_html=True)

    
    st.subheader("🔥 Location Hotspot Count")

    for location, count in location_count.items():
        if count >= 5:
            risk = "High"
            css_class = "hotspot-high"
            icon = "🔴"
        elif count >= 3:
            risk = "Medium"
            css_class = "hotspot-medium"
            icon = "🟡"
        else:
            risk = "Low"
            css_class = "hotspot-low"
            icon = "🟢"

        st.markdown(f"""
        <div class="{css_class}">
            {icon} <b>{location}</b><br>
            Registered People: <b>{count}</b><br>
            Risk Level: <b>{risk}</b>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    
    st.subheader("📋 People with GPS Data")
    st.dataframe(df, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)