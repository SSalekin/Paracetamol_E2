import streamlit as st
import requests

API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="Team Paracetamol",
    page_icon="💊",
)

st.title("💊 Team Paracetamol")

st.write("Hello from Streamlit!")

if st.button("Call FastAPI"):
    try:
        response = requests.get(API_URL)
        response.raise_for_status()

        data = response.json()

        st.success("Backend responded!")
        st.json(data)

    except Exception as e:
        st.error(f"Failed to reach backend: {e}")
