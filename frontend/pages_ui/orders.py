import streamlit as st
import api_client

def show():
    st.header("Order History")
    
    with st.spinner("Loading orders..."):
        res = api_client.list_orders()
        
    if res.status_code != 200:
        st.error("Failed to load orders.")
        return
        
    orders = res.json()
    if not orders:
        st.info("You have no orders.")
        return
        
    for order in orders:
        created_at = order["created_at"][:10]  # simple date formatting
        status = order["status"]
        status_color = "green" if status == "placed" else "red"
        
        with st.expander(f"Order #{order['id']} - {created_at} - :{status_color}[{status.upper()}] - ₹{order['total']}"):
            for item in order["items"]:
                st.write(f"- {item['product_name']} x {item['quantity']} @ ₹{item['unit_price']}")
            
            if status == "placed":
                if st.button("Cancel Order", key=f"cancel_{order['id']}"):
                    with st.spinner("Cancelling..."):
                        cancel_res = api_client.cancel_order(order["id"])
                        if cancel_res.status_code == 200:
                            st.success("Order cancelled.")
                            st.rerun()
                        else:
                            st.error(cancel_res.json().get("detail", "Failed to cancel."))
