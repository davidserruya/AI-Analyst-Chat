import streamlit as st
import google.generativeai as genai
import pandas as pd
import io
import sys

# ======================================================
# 🔐 CONFIG PAGE + AUTH
# ======================================================

st.set_page_config(
    page_title="AI Analyst",
    page_icon="🤖",
    layout="wide"
)

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔐 Accès restreint")
    st.caption("Veuillez entrer le code d'accès pour continuer")

    access_code = st.text_input("Code d'accès", type="password")

    if st.button("Valider"):
        if access_code == st.secrets["ACCESS_CODE"]:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Code incorrect")

    st.stop()

# ======================================================
# 🤖 CONFIG GEMINI
# ======================================================

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-2.5-pro")

def call_gemini(prompt: str) -> str:
    response = model.generate_content(prompt)
    return response.text.strip()

# ======================================================
# 🧠 GEMINI → CODE
# ======================================================

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

Donne UNIQUEMENT du code Python.
- Aucun commentaire
- Aucun markdown
- Le code DOIT contenir un print()
"""
    return call_gemini(prompt)

# ======================================================
# ⚙️ EXECUTION DU CODE
# ======================================================

def execute_code(code: str, df: pd.DataFrame) -> str:
    buffer = io.StringIO()
    old_stdout = sys.stdout
    sys.stdout = buffer

    try:
        exec(
            code,
            {
                "__builtins__": __builtins__,
                "pd": pd,
                "df": df
            }
        )
        return buffer.getvalue()
    except Exception as e:
        return f"Erreur lors de l'exécution du code : {e}"
    finally:
        sys.stdout = old_stdout

# ======================================================
# 💡 GEMINI → INTERPRÉTATION
# ======================================================

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

Réponds comme dans un chat :
- ton professionnel
- clair
- orienté décision
"""
    return call_gemini(prompt)

# ======================================================
# 💬 UI CHAT
# ======================================================

st.title("🤖 AI Analyst Chat")
st.caption("Discute avec ton dataset comme avec un data analyst professionnel")

# Session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "df" not in st.session_state:
    st.session_state.df = None

# Upload dataset
uploaded_file = st.file_uploader(
    "📂 Upload ton dataset (CSV ou Excel)",
    type=["csv", "xlsx"]
)

if uploaded_file:
    st.session_state.df = (
        pd.read_csv(uploaded_file)
        if uploaded_file.name.endswith(".csv")
        else pd.read_excel(uploaded_file)
    )

    st.success("Dataset chargé avec succès")

    with st.expander("👀 Aperçu du dataset"):
        st.dataframe(st.session_state.df.head())

# ======================================================
# 💬 AFFICHAGE HISTORIQUE
# ======================================================

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ======================================================
# ⌨️ INPUT UTILISATEUR
# ======================================================

if st.session_state.df is not None:
    question = st.chat_input("Pose ta question d’analyse…")

    # 1️⃣ Ajout du message user + rerun
    if question:
        st.session_state.messages.append({
            "role": "user",
            "content": question
        })
        st.rerun()

    # 2️⃣ Si dernier message = user → assistant répond
    if (
        st.session_state.messages
        and st.session_state.messages[-1]["role"] == "user"
    ):
        question = st.session_state.messages[-1]["content"]

        with st.chat_message("assistant"):
            placeholder = st.empty()

            # Étape 1
            placeholder.markdown("🤔 **L’analyste réfléchit…**")
            code = ask_gemini_for_code(question, st.session_state.df)

            st.write('DAVID')
            st.text(code)
            st.write('DAVID')

            # Étape 2
            placeholder.markdown("🧠 **Analyse des données…**")
            output = execute_code(code, st.session_state.df)

            st.write('DAVID')
            st.write(output)
            st.write('DAVID')

            # Étape 3
            placeholder.markdown("📊 **Interprétation des résultats…**")
            answer = interpret_result(question, st.session_state.df, output)

            # Résultat final
            placeholder.empty()
            placeholder.write(answer)

        st.session_state.messages.append({
            "role": "assistant",
            "content": answer
        })

else:
    st.info("Veuillez uploader un fichier pour commencer.")
