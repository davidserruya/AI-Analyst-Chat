import io
import sys
import pandas as pd

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

