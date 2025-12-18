import streamlit as st
import google.generativeai as genai

def init_gemini():
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    return genai.GenerativeModel("gemini-2.5-pro")

def get_access_code():
    return st.secrets["ACCESS_CODE"]
