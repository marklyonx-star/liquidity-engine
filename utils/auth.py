"""
Shared authentication for all pages
"""
import streamlit as st

def check_password():
    """Returns True if the user has entered the correct password."""
    
    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == st.secrets.get("password", "lyon2026"):
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.markdown("## 🔐 Liquidity Engine")
        st.text_input(
            "Enter password", 
            type="password", 
            on_change=password_entered, 
            key="password"
        )
        st.caption("Contact Mark for access")
        return False
    
    if st.session_state["password_correct"]:
        return True
    
    st.markdown("## 🔐 Liquidity Engine")
    st.text_input(
        "Enter password", 
        type="password", 
        on_change=password_entered, 
        key="password"
    )
    st.error("😕 Incorrect password")
    return False

def require_auth():
    """Call this at the top of each page to require authentication."""
    if not check_password():
        st.stop()
