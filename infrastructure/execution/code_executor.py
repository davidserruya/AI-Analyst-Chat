import io
import sys
import pandas as pd

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
