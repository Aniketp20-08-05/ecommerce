import os
import requests
import streamlit as st
from typing import Dict, Any, Optional

API_BASE_URL = os.environ.get("API_BASE_URL", "http://127.0.0.1:8000/api")

def request(method: str, path: str, **kwargs) -> requests.Response:
    """Send authenticated requests to backend with auto-refresh for JWT."""
    url = f"{API_BASE_URL.rstrip('/')}/{path.lstrip('/')}"
    headers = kwargs.get("headers", {})
    
    if "access_token" in st.session_state:
        headers["Authorization"] = f"Bearer {st.session_state['access_token']}"
    kwargs["headers"] = headers
    kwargs.setdefault("timeout", 10)
    
    try:
        response = requests.request(method, url, **kwargs)
    except requests.exceptions.RequestException as e:
        st.error("Cannot reach the server. Is the Django backend running?")
        st.stop()
        
    if response.status_code == 401 and "refresh_token" in st.session_state:
        refresh_token = st.session_state["refresh_token"]
        refresh_url = f"{API_BASE_URL.rstrip('/')}/auth/token/refresh/"
        try:
            refresh_res = requests.post(refresh_url, json={"refresh": refresh_token}, timeout=5)
            if refresh_res.status_code == 200:
                new_access = refresh_res.json().get("access")
                st.session_state["access_token"] = new_access
                headers["Authorization"] = f"Bearer {new_access}"
                kwargs["headers"] = headers
                return requests.request(method, url, **kwargs)
            else:
                for key in ["access_token", "refresh_token", "username"]:
                    st.session_state.pop(key, None)
                st.warning("Session expired. Please log in again.")
                st.rerun()
        except requests.exceptions.RequestException:
            pass
            
    return response

def register(data: Dict[str, str]) -> requests.Response:
    """Register a new user."""
    return request("POST", "/auth/register/", json=data)

def login(data: Dict[str, str]) -> requests.Response:
    """Log in and get JWT tokens."""
    return request("POST", "/auth/token/", json=data)

def list_categories() -> requests.Response:
    """Get list of categories."""
    return request("GET", "/categories/")

def list_products(params: Dict[str, Any]) -> requests.Response:
    """Get paginated list of products with optional search and category filter."""
    return request("GET", "/products/", params=params)

def create_product(data: Dict[str, Any]) -> requests.Response:
    """Create a new product (retailer only)."""
    return request("POST", "/products/", json=data)

def get_cart() -> requests.Response:
    """Get current user's cart."""
    return request("GET", "/cart/")

def add_to_cart(product_id: int, quantity: int) -> requests.Response:
    """Add a product to the cart."""
    return request("POST", "/cart/items/", json={"product_id": product_id, "quantity": quantity})

def update_cart_item(item_id: int, quantity: int) -> requests.Response:
    """Change quantity of an existing cart item."""
    return request("PATCH", f"/cart/items/{item_id}/", json={"quantity": quantity})

def remove_cart_item(item_id: int) -> requests.Response:
    """Remove an item from the cart."""
    return request("DELETE", f"/cart/items/{item_id}/")

def clear_cart() -> requests.Response:
    """Empty the entire cart."""
    return request("DELETE", "/cart/")

def checkout() -> requests.Response:
    """Turn the cart into an order."""
    return request("POST", "/orders/")

def list_orders() -> requests.Response:
    """Get user's order history."""
    return request("GET", "/orders/")

def cancel_order(order_id: int) -> requests.Response:
    """Cancel a specific order."""
    return request("POST", f"/orders/{order_id}/cancel/")
