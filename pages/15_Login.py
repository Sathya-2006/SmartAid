import random
import os
import base64
import streamlit as st
from auth import login_user

st.set_page_config(
    page_title="SmartAid Login",
    page_icon="assets/smartaid_logo.png",
    layout="centered"
)

LOGO_PATH = "assets/smartaid_logo.png"


def image_to_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as img:
            return base64.b64encode(img.read()).decode()
    return ""


logo_base64 = image_to_base64(LOGO_PATH)

# -------------------------
# CSS
# -------------------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #050505, #111827, #7f1d1d);
}

.block-container {
    max-width: 520px !important;
    padding-top: 1.4rem !important;
}

.brand-box {
    text-align: center;
    margin-bottom: 16px;
}

.brand-logo {
    width: 125px;
    cursor: pointer;
}

.brand-title {
    font-size: 42px;
    font-weight: 900;
    color: white;
    margin-top: -4px;
}

.brand-subtitle {
    font-size: 15px;
    font-weight: 700;
    color: #facc15;
    margin-bottom: 12px;
}

.login-card {
    background: rgba(255,255,255,0.08);
    padding: 28px;
    border-radius: 24px;
    border: 1px solid rgba(255,255,255,0.18);
    box-shadow: 0 15px 40px rgba(0,0,0,0.45);
}

.captcha-box {
    background: rgba(250,204,21,0.16);
    color: #fef3c7;
    padding: 14px;
    border-radius: 12px;
    font-weight: 900;
    text-align: center;
    border: 1px solid #facc15;
    margin-bottom: 10px;
}

h1, h2, h3, label {
    color: white !important;
}

div[data-testid="stButton"] button {
    background: #dc2626;
    color: white;
    border-radius: 10px;
    font-weight: 800;
    border: 1px solid #facc15;
}

div[data-testid="stButton"] button:hover {
    background: #b91c1c;
}
</style>
""", unsafe_allow_html=True)


# -------------------------
# Captcha
# -------------------------
def generate_captcha():
    a = random.randint(1, 9)
    b = random.randint(1, 9)
    st.session_state["captcha_question"] = f"{a} + {b}"
    st.session_state["captcha_answer"] = a + b


if "captcha_answer" not in st.session_state:
    generate_captcha()


# -------------------------
# Brand / Clickable Logo
# -------------------------
st.markdown(
    f"""
    <div class="brand-box">
        <a href="/" target="_self">
            <img class="brand-logo" src="data:image/png;base64,{logo_base64}">
        </a>
        <div class="brand-title">SmartAid</div>
        <div class="brand-subtitle">Secure Login Portal</div>
    </div>
    """,
    unsafe_allow_html=True
)


# -------------------------
# Login Card
# -------------------------
st.markdown('<div class="login-card">', unsafe_allow_html=True)

st.subheader("🔐 Login")

username = st.text_input("Username")
password = st.text_input("Password", type="password")

st.markdown(
    f"""
    <div class="captcha-box">
    Captcha: {st.session_state["captcha_question"]} = ?
    </div>
    """,
    unsafe_allow_html=True
)

captcha_input = st.number_input(
    "Enter Captcha Answer",
    min_value=0,
    step=1
)

if st.button("Login", width="stretch"):
    if captcha_input != st.session_state["captcha_answer"]:
        st.error("Invalid captcha.")
        generate_captcha()
        st.rerun()
    else:
        success, message = login_user(username, password)

        if success:
            st.session_state["logged_in"] = True
            role = st.session_state.get("role", "")

            st.success(message)

            if role == "Admin":
                st.switch_page("pages/2_Admin_Dashboard.py")
            elif role == "Volunteer":
                st.switch_page("pages/1_Register_Person.py")
            elif role == "MSME":
                st.switch_page("pages/9_MSME_Employer_Page.py")
            else:
                st.switch_page("app.py")
        else:
            st.error(message)
            generate_captcha()

if st.button("Create New Account", width="stretch"):
    st.switch_page("pages/16_Register.py")

st.markdown("</div>", unsafe_allow_html=True)