import json
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
import streamlit as st

def log_to_gsheet(question, code, answer, dataset_name):
    creds_info = json.loads(st.secrets["GSERVICE_ACCOUNT"])

    creds = Credentials.from_service_account_info(
        creds_info,
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
    )

    client = gspread.authorize(creds)
    sheet = client.open_by_key(st.secrets["GSHEET_ID"]).sheet1

    sheet.append_row([
        datetime.utcnow().isoformat(),
        question,
        code,
        answer,
        dataset_name
    ])
