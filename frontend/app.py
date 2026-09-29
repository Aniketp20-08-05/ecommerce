import streamlit as st
import pages_ui.auth as auth
import pages_ui.products as products
import pages_ui.cart as cart
import pages_ui.orders as orders

st.set_page_config(page_title="E-Commerce Store", layout="wide")

def main():
    st.sidebar.title("E-Commerce Store")
    
    if "access_token" not in st.session_state:
        st.sidebar.info("Please log in or register to continue.")
        auth.show()
    else:
        st.sidebar.write(f"Logged in as: **{st.session_state.get('username')}**")
        
        if st.sidebar.button("Logout"):
            for key in ["access_token", "refresh_token", "username"]:
                st.session_state.pop(key, None)
            st.rerun()
            
        st.sidebar.divider()
        
        page = st.sidebar.radio("Navigation", ["Products", "Cart", "Orders"])
        
        if page == "Products":
            products.show()
        elif page == "Cart":
            cart.show()
        elif page == "Orders":
            orders.show()

if __name__ == "__main__":
    main()
