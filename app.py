import streamlit as st
import google.generativeai as genai
import pandas as pd
import io
import sys

# ======================
# CONFIG GEMINI
# ======================

client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
MODEL_NAME = "gemini-2.5-pro"

def call_gemini(prompt: str) -> str:
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )
    return response.text.strip()


# ======================
# GEMINI → CODE
# ======================

def ask_gemini_for_code(question: str, df: pd.DataFrame) -> str:
    buffer = io.StringIO()
    df.info(buf=buffer)
    df_info = buffer.getvalue()

    prompt = f"""
Tu es un consultant Data.

Tu disposes d'un DataFrame pandas nommé df.

Structure du DataFrame :
{df_info}

Question utilisateur :
"{question}"

Donnez-moi UNIQUEMENT le code Python (avec une instruction 'print()') pour obtenir l'information demandée. 
Tu peux donner d'autres requete pour avoir du contexte et pour comparer si nécessaire. 
1. **INTERDIT :** N'ajoutez AUCUN commentaire, aucune introduction, aucune conclusion. 
2. **INTERDIT :** N'ajoutez AUCUN bloc de code Markdown (c'est-à-dire pas de ```python mais JAMAIS)
3. **OBLIGATOIRE :** Le code doit contenir une instruction 'print()' affichant clairement le résultat de l'analyse (utiliser .to_markdown() ou .to_string() pour les DataFrames/Series).
"""
    return call_gemini(prompt)


# ======================
# EXECUTION DU CODE
# ======================

def execute_code(code: str, df: pd.DataFrame) -> str:
    local_vars = {"df": df, "pd": pd}

    buffer = io.StringIO()
    old_stdout = sys.stdout
    sys.stdout = buffer

    try:
        exec(code, {}, local_vars)
        return buffer.getvalue()
    finally:
        sys.stdout = old_stdout


# ======================
# GEMINI → INTERPRÉTATION
# ======================

def interpret_result(question: str, df: pd.DataFrame, output: str) -> str:
    buffer = io.StringIO()
    df.info(buf=buffer)
    df_info = buffer.getvalue()

    prompt = f"""
Tu es un consultant data senior.

Structure du DataFrame :
{df_info}

Question utilisateur :
"{question}"

Résultat obtenu :
{output}

Réponds à l'utilisateur comme dans un chat :
- ton professionnel
- clair
- orienté décision
"""
    return call_gemini(prompt)


# ======================
# STREAMLIT CHAT UI
# ======================
st.set_page_config(
    page_title="AI Analyst",
    page_icon="🤖",
    layout="wide"
)

st.set_page_config(page_title="AI Analyst Chat", layout="wide")
st.title("🤖 AI Analyst Chat")

# Session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "df" not in st.session_state:
    st.session_state.df = None

# Upload fichier
uploaded_file = st.file_uploader(
    "📂 Upload ton dataset (CSV ou Excel)",
    type=["csv", "xlsx"]
)

if uploaded_file:
    if uploaded_file.name.endswith(".csv"):
        st.session_state.df = pd.read_csv(uploaded_file)
    else:
        st.session_state.df = pd.read_excel(uploaded_file)

    st.success("Dataset chargé avec succès")

    with st.expander("👀 Aperçu du dataset"):
        st.dataframe(st.session_state.df.head())

# Chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Input utilisateur
if st.session_state.df is not None:
    question = st.chat_input("Pose ta question ...")

    if question:
        # Message utilisateur
        st.session_state.messages.append({
            "role": "user",
            "content": question
        })

        with st.chat_message("user"):
            st.write(question)

        # Réponse IA
        with st.chat_message("assistant"):
            with st.spinner("Analyse en cours..."):
                code = ask_gemini_for_code(question, st.session_state.df)
                output = execute_code(code, st.session_state.df)
                answer = interpret_result(question, st.session_state.df, output)

                st.write(answer)

        st.session_state.messages.append({
            "role": "assistant",
            "content": answer
        })

else:
    st.info("Veuillez uploader un fichier pour commencer.")
