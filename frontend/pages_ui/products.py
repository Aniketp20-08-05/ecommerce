import streamlit as st
import api_client

def show():
    st.header("Products")

    if st.session_state.get("role") == "retailer":
        with st.expander("Retailer Dashboard: Add Product"):
            cat_res_add = api_client.list_categories()
            add_categories = cat_res_add.json().get("results", []) if cat_res_add.status_code == 200 else []
            add_cat_options = {c["name"]: c["id"] for c in add_categories}
            
            if not add_cat_options:
                st.warning("Please create a category via Django admin first.")
            else:
                with st.form("add_product_form"):
                    p_name = st.text_input("Name")
                    p_desc = st.text_area("Description")
                    p_price = st.number_input("Price", min_value=0.01)
                    p_stock = st.number_input("Stock", min_value=1)
                    p_cat = st.selectbox("Category", list(add_cat_options.keys()))
                    submitted = st.form_submit_button("Add Product")
                    
                    if submitted:
                        res = api_client.create_product({
                            "name": p_name,
                            "description": p_desc,
                            "price": p_price,
                            "stock": p_stock,
                            "category": add_cat_options[p_cat]
                        })
                        if res.status_code == 201:
                            st.success("Product added!")
                            st.rerun()
                        else:
                            st.error(f"Failed: {res.text}")
    
    st.divider()

    col1, col2 = st.columns([2, 1])
    with col1:
        search = st.text_input("Search products...")
    
    with col2:
        cat_res = api_client.list_categories()
        categories = cat_res.json().get("results", []) if cat_res.status_code == 200 else []
        cat_options = {"All": ""}
        for c in categories:
            cat_options[c["name"]] = str(c["id"])
        
        selected_cat_name = st.selectbox("Category", list(cat_options.keys()))
        selected_cat_id = cat_options[selected_cat_name]
    
    if "product_page" not in st.session_state:
        st.session_state["product_page"] = 1
        
    params = {"page": st.session_state["product_page"]}
    if search:
        params["search"] = search
    if selected_cat_id:
        params["category"] = selected_cat_id
        
    with st.spinner("Loading products..."):
        prod_res = api_client.list_products(params)
        
    if prod_res.status_code != 200:
        st.error("Failed to load products.")
        return
        
    data = prod_res.json()
    products = data.get("results", [])
    
    if not products:
        st.info("No products found.")
    else:
        # Display 3-column grid
        cols = st.columns(3)
        for i, prod in enumerate(products):
            col = cols[i % 3]
            with col:
                st.subheader(prod["name"])
                st.write(prod["description"])
                st.write(f"**₹{prod['price']}**")
                
                stock = prod["stock"]
                if stock <= 0:
                    st.error("Out of stock")
                    st.button("Add to cart", key=f"add_{prod['id']}", disabled=True)
                else:
                    st.write(f"Stock: {stock}")
                    qty = st.number_input("Qty", min_value=1, max_value=stock, value=1, key=f"qty_{prod['id']}")
                    if st.button("Add to cart", key=f"add_{prod['id']}"):
                        with st.spinner("Adding..."):
                            res = api_client.add_to_cart(prod["id"], qty)
                            if res.status_code == 201:
                                st.toast(f"Added {qty} of {prod['name']} to cart!")
                            else:
                                st.error("Failed to add to cart.")
                                
    # Pagination
    p_col1, p_col2 = st.columns(2)
    with p_col1:
        if data.get("previous"):
            if st.button("Previous Page"):
                st.session_state["product_page"] -= 1
                st.rerun()
    with p_col2:
        if data.get("next"):
            if st.button("Next Page"):
                st.session_state["product_page"] += 1
                st.rerun()
