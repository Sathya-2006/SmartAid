import os
import base64
import streamlit as st
from firebase_config import db
from dotenv import load_dotenv

st.set_page_config(
    page_title="SmartAid",
    page_icon="assets/smartaid_logo.png",
    layout="wide"
)

load_dotenv()

LOGO_PATH = "assets/smartaid_logo.png"
HERO_PATH = "assets/hero_banner.png"

# ── FastAPI chatbot backend URL ──────────────────────────────
CHATBOT_API_URL = os.getenv("CHATBOT_API_URL", "http://localhost:8000/ask")

# ── Session state ────────────────────────────────────────────
if "section" not in st.session_state:
    st.session_state["section"] = "home"


def image_to_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as img:
            return base64.b64encode(img.read()).decode()
    return ""


logo_base64 = image_to_base64(LOGO_PATH)

# ── Firebase stats ───────────────────────────────────────────
people_docs = list(db.collection("people").stream())
people_data = [doc.to_dict() for doc in people_docs]

total_registered      = len(people_data)
jobs_allocated        = len(list(db.collection("job_allocations").stream()))
schemes_allocated     = len(list(db.collection("scheme_allocations").stream()))
students_supported    = sum(1 for p in people_data if p.get("education_status") in ["School Student", "College Student"])
disabled_beneficiaries = sum(1 for p in people_data if p.get("disability") == "Yes")
pending_cases         = sum(1 for p in people_data if p.get("status", "Pending") == "Pending")

# ── Global CSS ───────────────────────────────────────────────
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #050505, #111827, #1e293b);
}
.block-container { padding-top: 1.3rem !important; }
section[data-testid="stSidebar"] { background: #050505; }
section[data-testid="stSidebar"] * { color: white !important; }

.logo-area { display:flex;align-items:center;gap:18px;text-decoration:none !important; }
.logo-area img { width:95px; }
.logo-area span { font-size:38px;font-weight:900;color:white; }

.hero-card {
    background: linear-gradient(135deg, #020617, #0f172a, #1d4ed8);
    padding: 55px; border-radius: 26px;
    border: 1px solid rgba(255,255,255,0.16); min-height: 460px;
}
.hero-title  { color:white;font-size:54px;font-weight:900;line-height:1.15; }
.hero-tagline{ color:#facc15;font-size:24px;font-weight:800;margin-top:20px; }
.hero-desc   { color:#f8fafc;font-size:18px;line-height:1.8;margin-top:22px; }

.section-title    { color:white;font-size:38px;font-weight:900;text-align:center;margin-top:50px; }
.section-subtitle { color:#cbd5e1;text-align:center;font-size:18px;margin-bottom:30px; }

.stat-card {
    background:rgba(255,255,255,0.09);border:1px solid rgba(255,255,255,0.15);
    border-radius:18px;padding:24px 14px;text-align:center;color:white;
    min-height:165px;height:165px;box-shadow:0 10px 28px rgba(0,0,0,0.3);
}
.stat-number { color:#facc15;font-size:34px;font-weight:900; }
.stat-label  { font-weight:800;font-size:14px;line-height:1.3; }

.info-card {
    background:rgba(255,255,255,0.09);border:1px solid rgba(255,255,255,0.15);
    border-radius:18px;padding:22px;color:white;height:210px;
    box-shadow:0 10px 28px rgba(0,0,0,0.28);overflow:hidden;
}
.info-card h3 { color:#93c5fd !important;font-size:22px;line-height:1.25; }
.info-card p,.info-card li { color:#e5e7eb;font-size:15px;line-height:1.6; }

.problem-card {
    background:rgba(0,0,0,0.35);padding:35px;border-radius:24px;
    border:1px solid rgba(255,255,255,0.15);color:white;margin-top:40px;
}
.highlight {
    background:rgba(250,204,21,0.15);border-left:6px solid #facc15;
    padding:18px;border-radius:14px;color:#fef3c7;font-weight:800;
}
.footer {
    background:#050505;color:white;padding:35px;text-align:center;
    border-radius:22px 22px 0 0;margin-top:50px;
}
div[data-testid="stButton"] button {
    background:#111827;color:white;border:1px solid rgba(255,255,255,0.25);
    border-radius:10px;font-weight:800;
}
div[data-testid="stButton"] button:hover {
    background:#2563eb;color:white;border:1px solid #facc15;
}
h1,h2,h3 { color:white !important; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ──────────────────────────────────────────────────
if os.path.exists(LOGO_PATH):
    st.sidebar.image(LOGO_PATH, width=150)
st.sidebar.markdown("<h2 style='text-align:center;color:white;'>SmartAid</h2>", unsafe_allow_html=True)
if st.session_state.get("logged_in", False):
    st.sidebar.success(f"Logged in as {st.session_state.get('role', 'Guest')}")
else:
    st.sidebar.info("Guest Mode")

# ── Top nav ──────────────────────────────────────────────────
logo_html = f"""
<a class="logo-area" href="/">
    <img src="data:image/png;base64,{logo_base64}">
    <span>SmartAid</span>
</a>"""

logo_col, h1, h2, h3, h4, h5, h6, h7 = st.columns([2.6, 1, 1, 1, 1, 1, 1, 1])
with logo_col: st.markdown(logo_html, unsafe_allow_html=True)
with h1:
    if st.button("Home"):       st.session_state["section"] = "home"
with h2:
    if st.button("About Us"):   st.session_state["section"] = "about"
with h3:
    if st.button("Services"):   st.session_state["section"] = "services"
with h4:
    if st.button("Useful Links"):st.session_state["section"] = "links"
with h5:
    if st.button("Contact Us"): st.session_state["section"] = "contact"
with h6:
    if st.button("Login"):      st.switch_page("pages/15_Login.py")
with h7:
    if st.button("Register"):   st.switch_page("pages/16_Register.py")

st.write("")

section = st.session_state.get("section", "home")

# ── Sections ─────────────────────────────────────────────────
if section == "home":
    left, right = st.columns([1.35, 1])
    with left:
        st.markdown("""
        <div class="hero-card">
            <div class="hero-title">SmartAid – AI-Powered<br>Social Inclusion Platform</div>
            <div class="hero-tagline">Making the Invisible Visible, Employable, and Empowered</div>
            <div class="hero-desc">
                Millions of homeless and unskilled individuals remain excluded from jobs,
                welfare schemes, and opportunities due to the lack of a centralized
                identification system. SmartAid uses AI, GPS, and digital registration
                to connect vulnerable communities with employment, training, and
                government support.
            </div>
        </div>""", unsafe_allow_html=True)
    with right:
        if os.path.exists(HERO_PATH):
            st.image(HERO_PATH, width="stretch")

    st.markdown('<div class="section-title">Making an Impact</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Live SmartAid statistics from Firebase.</div>', unsafe_allow_html=True)

    cols = st.columns(6)
    stats = [
        ("📊", total_registered,       "Total Registered"),
        ("💼", jobs_allocated,          "Jobs Allocated"),
        ("🎓", students_supported,      "Students Supported"),
        ("♿", disabled_beneficiaries,  "Disabled Beneficiaries"),
        ("🏛", schemes_allocated,       "Schemes Assigned"),
        ("⚠️", pending_cases,          "Pending Cases"),
    ]
    for col, stat in zip(cols, stats):
        with col:
            st.markdown(f"""
            <div class="stat-card">
                <h2>{stat[0]}</h2>
                <div class="stat-number">{stat[1]}</div>
                <div class="stat-label">{stat[2]}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-title">Why SmartAid?</div>', unsafe_allow_html=True)
    why_cols = st.columns(5)
    why_items = [
        ("✅ AI Recommendations", "Fast support decisions using AI-based matching."),
        ("✅ GPS Heatmaps",        "Identify priority areas and field hotspots."),
        ("✅ Live Dashboard",      "Track people, schemes, jobs and outcomes."),
        ("✅ Job Matching",        "Connect work-ready people with employers."),
        ("✅ Scheme Access",       "Help beneficiaries receive welfare support."),
    ]
    for col, item in zip(why_cols, why_items):
        with col:
            st.markdown(f"""
            <div class="info-card">
                <h3>{item[0]}</h3>
                <p>{item[1]}</p>
            </div>""", unsafe_allow_html=True)

elif section == "about":
    st.markdown("""
    <div class="problem-card">
    <h2>⚠️ The Challenge We Address</h2>
    <p>Millions of homeless, migrant, and unskilled adults remain invisible to government systems and employment opportunities.</p>
    <ul>
      <li>Manual and outdated surveys</li>
      <li>No centralized database</li>
      <li>Lack of real-time tracking</li>
      <li>Difficulty identifying vulnerable individuals</li>
      <li>Poor coordination between NGOs, Government, and MSMEs</li>
      <li>Limited access to jobs, education, and welfare schemes</li>
    </ul>
    <div class="highlight">
      Without data, people remain invisible. Without visibility, opportunities never reach them.
    </div>
    </div>""", unsafe_allow_html=True)

elif section == "services":
    st.markdown('<div class="section-title">Services</div>', unsafe_allow_html=True)
    service_cols = st.columns(3)
    services = [
        ("💼 Employment Assistance", "Construction, tailoring, cleaning, delivery, hospitality."),
        ("🎓 Skill Development",     "PMKVY, vocational training, digital skills, and job readiness."),
        ("🏛 Welfare Support",       "Pension, disability support, housing, healthcare, and scholarships."),
    ]
    for col, service in zip(service_cols, services):
        with col:
            st.markdown(f"""
            <div class="info-card">
                <h3>{service[0]}</h3>
                <p>{service[1]}</p>
            </div>""", unsafe_allow_html=True)

elif section == "links":
    st.markdown('<div class="section-title">Useful Links</div>', unsafe_allow_html=True)
    link_cols = st.columns(4)
    links = [
        ("👥 Register Person",    "Open sidebar → Register Person"),
        ("🤖 AI Recommendation",  "Open sidebar → AI Recommendations"),
        ("🏭 MSME Portal",        "Open sidebar → MSME Employer Page"),
        ("📊 Reports",            "Open sidebar → Reports"),
    ]
    for col, link in zip(link_cols, links):
        with col:
            st.markdown(f"""
            <div class="info-card">
                <h3>{link[0]}</h3>
                <p>{link[1]}</p>
            </div>""", unsafe_allow_html=True)

elif section == "contact":
    st.markdown('<div class="section-title">Contact Us</div>', unsafe_allow_html=True)
    contact_left, contact_right = st.columns([1, 1])
    with contact_left:
        st.markdown("""
        <div class="info-card">
            <h3>Let's Build an Inclusive Future Together</h3>
            <p>📧 Email: support@smartaid.org</p>
            <p>📞 Phone: +91 XXXXX XXXXX</p>
            <p>📍 Location: Chennai, Tamil Nadu, India</p>
        </div>""", unsafe_allow_html=True)
    with contact_right:
        st.text_input("Name")
        st.text_input("Email")
        st.text_input("Organization")
        st.text_area("Message")
        st.button("Send Message")

# ── Platform capabilities ─────────────────────────────────────
st.markdown('<div class="section-title">Platform Capabilities</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-subtitle">SmartAid connects identification, AI decision support, employment, welfare schemes, and impact tracking in one platform.</div>',
    unsafe_allow_html=True
)
cap_cols = st.columns(6)
capabilities = [
    ("🧾", "Smart ID"), ("📍", "GPS Mapping"), ("🤖", "AI Recommend"),
    ("💼", "Job Matching"), ("📊", "Analytics"), ("🤝", "Inclusion"),
]
for col, cap in zip(cap_cols, capabilities):
    with col:
        st.markdown(f"""
        <div class="stat-card">
            <h2>{cap[0]}</h2>
            <div class="stat-label">{cap[1]}</div>
        </div>""", unsafe_allow_html=True)

# ── Floating AI Chatbot (calls FastAPI /ask) ──────────────────
import streamlit.components.v1 as _components

_chatbot_html = f"""
<script>
(function() {{
    var API_URL = "{CHATBOT_API_URL}";
    var chatHistory = [];   // {{role, content}}

    // ── Styles ──────────────────────────────────────────────
    var style = window.parent.document.createElement("style");
    style.textContent = [
        "#sa-fab{{position:fixed;bottom:28px;right:28px;width:62px;height:62px;border-radius:50%;background:linear-gradient(135deg,#6d28d9,#2563eb);box-shadow:0 6px 24px rgba(99,102,241,.55);display:flex;align-items:center;justify-content:center;cursor:pointer;z-index:99999;font-size:28px;border:none;transition:transform .2s;}}",
        "#sa-fab:hover{{transform:scale(1.1);}}",
        "#sa-chat{{position:fixed;bottom:102px;right:28px;width:380px;max-height:520px;background:#0f172a;border:1px solid rgba(255,255,255,.18);border-radius:20px;box-shadow:0 16px 48px rgba(0,0,0,.7);display:none;flex-direction:column;z-index:99998;overflow:hidden;font-family:sans-serif;}}",
        "#sa-chat.open{{display:flex;}}",
        ".sa-hdr{{background:linear-gradient(135deg,#6d28d9,#2563eb);padding:13px 16px;display:flex;align-items:center;justify-content:space-between;color:#fff;font-weight:800;font-size:14px;flex-shrink:0;}}",
        ".sa-close{{cursor:pointer;font-size:18px;opacity:.8;}}",
        ".sa-msgs{{flex:1;overflow-y:auto;padding:12px;display:flex;flex-direction:column;gap:8px;}}",
        ".sa-bbl{{max-width:86%;padding:9px 13px;border-radius:14px;font-size:13px;line-height:1.55;white-space:pre-wrap;word-break:break-word;}}",
        ".sa-bot{{background:rgba(255,255,255,.1);color:#e2e8f0;align-self:flex-start;border-bottom-left-radius:3px;}}",
        ".sa-usr{{background:linear-gradient(135deg,#6d28d9,#2563eb);color:#fff;align-self:flex-end;border-bottom-right-radius:3px;}}",
        ".sa-dim{{opacity:.55;font-style:italic;}}",
        ".sa-inp{{display:flex;gap:8px;padding:10px 12px;border-top:1px solid rgba(255,255,255,.1);background:#0f172a;flex-shrink:0;}}",
        ".sa-inp textarea{{flex:1;background:rgba(255,255,255,.07);border:1px solid rgba(255,255,255,.15);border-radius:10px;color:#fff;font-size:13px;padding:8px 11px;resize:none;outline:none;font-family:inherit;line-height:1.4;}}",
        ".sa-inp textarea::placeholder{{color:#64748b;}}",
        ".sa-send{{width:40px;height:40px;border-radius:50%;background:linear-gradient(135deg,#6d28d9,#2563eb);border:none;color:#fff;font-size:16px;cursor:pointer;flex-shrink:0;align-self:flex-end;}}"
    ].join("");
    window.parent.document.head.appendChild(style);

    // ── DOM ──────────────────────────────────────────────────
    var pd = window.parent.document;

    var fab = pd.createElement("button");
    fab.id = "sa-fab";
    fab.innerHTML = "&#10024;";
    pd.body.appendChild(fab);

    var chat = pd.createElement("div");
    chat.id = "sa-chat";
    chat.innerHTML = [
        '<div class="sa-hdr"><span>&#10024; SmartAid AI Assistant</span><span class="sa-close" id="sa-close">&#10005;</span></div>',
        '<div class="sa-msgs" id="sa-msgs"><div class="sa-bbl sa-bot">Hello! I am SmartAid AI. Ask me about job schemes, welfare, or skill training!</div></div>',
        '<div class="sa-inp"><textarea id="sa-ta" rows="2" placeholder="Ask SmartAid AI..."></textarea><button class="sa-send" id="sa-send">&#10148;</button></div>'
    ].join("");
    pd.body.appendChild(chat);

    // ── Events ───────────────────────────────────────────────
    pd.getElementById("sa-fab").addEventListener("click", function() {{
        pd.getElementById("sa-chat").classList.toggle("open");
    }});
    pd.getElementById("sa-close").addEventListener("click", function() {{
        pd.getElementById("sa-chat").classList.remove("open");
    }});
    pd.getElementById("sa-send").addEventListener("click", sendMsg);
    pd.getElementById("sa-ta").addEventListener("keydown", function(e) {{
        if (e.key === "Enter" && !e.shiftKey) {{ e.preventDefault(); sendMsg(); }}
    }});

    // ── Helpers ──────────────────────────────────────────────
    function addBubble(text, cls) {{
        var msgs = pd.getElementById("sa-msgs");
        var d = pd.createElement("div");
        d.className = "sa-bbl " + cls;
        d.textContent = text;
        msgs.appendChild(d);
        msgs.scrollTop = msgs.scrollHeight;
        return d;
    }}

    // ── Send ─────────────────────────────────────────────────
    function sendMsg() {{
        var ta = pd.getElementById("sa-ta");
        var q  = ta.value.trim();
        if (!q) return;
        ta.value = "";

        addBubble(q, "sa-usr");
        var typing = addBubble("Thinking...", "sa-bot sa-dim");

        // Append user turn to local history
        chatHistory.push({{ role: "user", content: q }});

        fetch(API_URL, {{
            method: "POST",
            headers: {{ "Content-Type": "application/json" }},
            body: JSON.stringify({{
                question: q,
                history: chatHistory.slice(0, -1)   // history before this turn
            }})
        }})
        .then(function(r) {{ return r.json(); }})
        .then(function(data) {{
            typing.remove();
            var ans = data.answer || "No response.";
            addBubble(ans, "sa-bot");
            // Append model reply to local history
            chatHistory.push({{ role: "assistant", content: ans }});
            // Keep history bounded (last 20 turns)
            if (chatHistory.length > 20) chatHistory = chatHistory.slice(-20);
        }})
        .catch(function(err) {{
            typing.remove();
            addBubble("⚠️ Could not reach SmartAid AI. Is the backend running?", "sa-bot");
            chatHistory.pop();   // remove failed user turn
        }});
    }}
}})();
</script>
"""

_components.html(_chatbot_html, height=0)

# ── Footer ────────────────────────────────────────────────────
st.markdown("""
<div class="footer">
    <h2>"Empowering People. Strengthening Communities. Building a Better India."</h2>
    <p>© 2026 SmartAid | support@smartaid.org | Chennai, Tamil Nadu</p>
</div>
""", unsafe_allow_html=True)

if st.session_state.get("logged_in", False):
    st.success(f"Logged in as {st.session_state.get('role')}. Use sidebar to access modules.")
else:
    st.info("Please register first, then login to access SmartAid modules.")