import io
import pandas as pd
from infrastructure.llm.gemini_client import call_gemini

def ask_gemini_for_code(model, question: str, df: pd.DataFrame) -> str:
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

Donne UNIQUEMENT du code Python avec un print().
"""
    return call_gemini(model, prompt)


def interpret_result(model, question: str, df: pd.DataFrame, output: str) -> str:
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

Réponds clairement et de façon orientée décision.
"""
    return call_gemini(model, prompt)
