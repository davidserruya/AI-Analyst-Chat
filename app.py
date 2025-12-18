import streamlit as st
import pandas as pd

from config.settings import *
from application.services import *
from infrastructure.execution.code_executor import *

# ======================
# AUTH
# ======================

st.set_page_config(page_title="AI Analyst", page_icon="🤖", layout="wide")

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔐 Accès restreint")
    access_code = st.text_input("Code d'accès", type="password")

    if st.button("Valider"):
        if access_code == get_access_code():
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Code incorrect")

    st.stop()

# ======================
# INIT
# ======================

model = init_gemini()

st.title("🤖 AI Analyst Chat")

if "messages" not in st.session_state:
    st.session_state.messages = []

if "df" not in st.session_state:
    st.session_state.df = None

uploaded_file = st.file_uploader("📂 Upload dataset", type=["csv", "xlsx"])

if uploaded_file:
    st.session_state.df = (
        pd.read_csv(uploaded_file)
        if uploaded_file.name.endswith(".csv")
        else pd.read_excel(uploaded_file)
    )

# Chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.text(msg["content"])

if st.session_state.df is not None:
    question = st.chat_input("Pose ta question")

    if question:
        st.session_state.messages.append({"role": "user", "content": question})

        with st.chat_message("assistant"):
            code = ask_gemini_for_code(model, question, st.session_state.df)
            output = execute_code(code, st.session_state.df)
            answer = interpret_result(model, question, st.session_state.df, output)
            st.text(answer)

        st.session_state.messages.append({"role": "assistant", "content": answer})
