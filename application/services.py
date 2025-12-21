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

JE VEUX UNIQUEMENT LE CODE POUR L'ÉXÉCUTER DE MON CÔTÉ SANS ```PYTHON, JUSTE LE CODE EN MODE CODE
INTERDIT :
- créer un DataFrame
- définir des données fictives
- utiliser data = {...}
- redéfinir df
"""
    return call_gemini(model, prompt)


def interpret_result(model, question: str, df: pd.DataFrame, output: str) -> str:
    buffer = io.StringIO()
    df.info(buf=buffer)
    df_info = buffer.getvalue()

    prompt = f"""
Tu es un consultant Data.

Structure du DataFrame :
{df_info}

Question utilisateur :
"{question}"

Résultat obtenu :
{output}

Réponds à la question de l'utilisateur avec le résultat obtenu, interprete ce résultat. Ne vas pas trop loin
"""
    return call_gemini(model, prompt)
