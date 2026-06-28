import streamlit as st
from datetime import datetime
from firebase_config import db


# --------------------------
# SIGNUP
# --------------------------
def signup_user(username, password, role):

    user_ref = db.collection("app_users").document(username)

    if user_ref.get().exists:
        return False, "Username already exists."

    user_ref.set({
        "username": username,
        "password": password,
        "role": role,
        "created_at": datetime.now()
    })

    return True, "Registration successful."


# --------------------------
# LOGIN
# --------------------------
def login_user(username, password):

    user_ref = db.collection("app_users").document(username)
    user_doc = user_ref.get()

    if not user_doc.exists:
        return False, "User not registered."

    data = user_doc.to_dict()

    if data["password"] != password:
        return False, "Invalid password."

    st.session_state["logged_in"] = True
    st.session_state["username"] = username
    st.session_state["role"] = data["role"]

    return True, "Login successful."


# --------------------------
# CHECK LOGIN
# --------------------------
def check_login():

    if not st.session_state.get("logged_in", False):

        st.warning("Please login first.")
        st.stop()


# --------------------------
# GET ROLE
# --------------------------
def get_role():
    return st.session_state.get("role")


# --------------------------
# LOGOUT
# --------------------------
def logout():

    if st.session_state.get("logged_in", False):

        st.sidebar.markdown("---")

        st.sidebar.write(
            f"Logged in as: {st.session_state.get('role')}"
        )

        if st.sidebar.button("Logout"):

            st.session_state.clear()
            st.rerun()