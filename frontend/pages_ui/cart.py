import streamlit as st
import api_client

def show():
    st.header("Your Cart")
    
    with st.spinner("Loading cart..."):
        res = api_client.get_cart()
        
    if res.status_code == 404:
        st.info("Your cart is empty.")
        return
    elif res.status_code != 200:
        st.error("Failed to load cart.")
        return
        
    cart_data = res.json()
    items = cart_data.get("items", [])
    
    if not items:
        st.info("Your cart is empty.")
        return
        
    for item in items:
        col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 2, 1])
        with col1:
            st.write(f"**{item['product_name']}**")
        with col2:
            st.write(f"₹{item['unit_price']}")
        with col3:
            new_qty = st.number_input("Qty", min_value=1, value=item["quantity"], key=f"cart_qty_{item['id']}")
            if new_qty != item["quantity"]:
                with st.spinner("Updating..."):
                    up_res = api_client.update_cart_item(item["id"], new_qty)
                    if up_res.status_code == 200:
                        st.rerun()
                    else:
                        st.error("Failed to update.")
        with col4:
            st.write(f"**Total: ₹{item['line_total']}**")
        with col5:
            if st.button("Remove", key=f"rm_{item['id']}"):
                with st.spinner("Removing..."):
                    if api_client.remove_cart_item(item["id"]).status_code == 204:
                        st.rerun()
                        
    st.divider()
    st.subheader(f"Total: ₹{cart_data['total']}")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Clear Cart"):
            with st.spinner("Clearing..."):
                if api_client.clear_cart().status_code == 204:
                    st.rerun()
    with col2:
        if st.button("Place Order", type="primary"):
            with st.spinner("Placing order..."):
                order_res = api_client.checkout()
                if order_res.status_code == 201:
                    order_data = order_res.json()
                    st.success(f"Order placed successfully! Order ID: {order_data['id']}, Total: ₹{order_data['total']}")
                    st.balloons()
                else:
                    st.error(order_res.json().get("detail", "Failed to place order."))
