import io
import pandas as pd
from infrastructure.llm.gemini_client import call_gemini

def ask_gemini_for_code(model, question: str, df: pd.DataFrame) -> str:
    buffer = io.StringIO()
    df.info(buf=buffer)
    df_info = buffer.getvalue()
    print(df_info)
    prompt = f"""
Tu es un consultant Data.

Tu disposes d'un DataFrame pandas nommé df.

Structure du DataFrame :
{df_info}

Question utilisateur :
"{question}"
    
JUSTE LE CODE
1. INTERDIT DE COMMENCER PAR  ```python tu retournes juste le code sans rien avant
2. **INTERDIT :** N'ajoutez AUCUN commentaire, aucune introduction, aucune conclusion. 
3. **OBLIGATOIRE :** Le code doit contenir une instruction 'print()' affichant clairement le résultat de l'analyse (utiliser .to_markdown() ou .to_string() pour les DataFrames/Series).
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
