import streamlit as st
import api_client

def show():
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        st.subheader("Login")
        login_user = st.text_input("Username", key="login_user")
        login_pass = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login"):
            res = api_client.login({"username": login_user, "password": login_pass})
            if res.status_code == 200:
                data = res.json()
                st.session_state["access_token"] = data["access"]
                st.session_state["refresh_token"] = data["refresh"]
                st.session_state["username"] = login_user
                st.session_state["role"] = data.get("role", "consumer")
                st.rerun()
            elif res.status_code == 401:
                st.error("Invalid credentials.")
            else:
                st.error(f"Error: {res.text}")

    with tab2:
        st.subheader("Register")
        reg_user = st.text_input("Username", key="reg_user")
        reg_email = st.text_input("Email", key="reg_email")
        reg_pass = st.text_input("Password", type="password", key="reg_pass")
        st.write("Please select your role below:")
        reg_role = st.selectbox("Role", ["consumer", "retailer"], key="reg_role")
        if st.button("Register"):
            res = api_client.register({"username": reg_user, "email": reg_email, "password": reg_pass, "role": reg_role})
            if res.status_code == 201:
                st.success("Registered successfully! Please log in.")
            elif res.status_code == 400:
                for field, errors in res.json().items():
                    st.error(f"{field.capitalize()}: {', '.join(errors)}")
            else:
                st.error(f"Error: {res.text}")
