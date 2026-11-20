import hashlib
import hmac
import os
import streamlit as st

ADMIN_USERNAME=os.getenv("CV_ADMIN_USERNAME","admin")
ADMIN_PASSWORD=os.getenv("CV_ADMIN_PASSWORD","admin123")

def verify_login(username,password):
    expected=hashlib.sha256(ADMIN_PASSWORD.encode()).digest()
    supplied=hashlib.sha256(password.encode()).digest()
    return hmac.compare_digest(username,ADMIN_USERNAME) and hmac.compare_digest(supplied,expected)

def login_portal():
    _,center,_=st.columns([1,1.1,1])
    with center:
        st.markdown('<div class="login-brand"><div class="login-icon">✓</div><div class="page-title">Welcome back</div><div class="page-subtitle">Sign in to manage CV evaluations</div></div>',unsafe_allow_html=True)
        with st.form("login_form"):
            username=st.text_input("Username",placeholder="Enter your username")
            password=st.text_input("Password",type="password",placeholder="Enter your password")
            submitted=st.form_submit_button("Sign in",type="primary",use_container_width=True)
    if submitted:
        if verify_login(username,password):
            st.session_state.authenticated=True; st.rerun()
        else: st.error("Invalid username or password.")

def require_login():
    if "authenticated" not in st.session_state: st.session_state.authenticated=False
    if not st.session_state.authenticated:
        login_portal(); st.stop()

def logout():
    st.session_state.authenticated=False
    st.session_state.pop("selected_evaluation",None)
    st.rerun()
