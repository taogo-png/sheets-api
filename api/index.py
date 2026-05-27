from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import gspread
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request as GRequest
import os
from datetime import datetime
import pytz

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

def get_client():
    creds = Credentials(
        token=None,
        refresh_token=os.environ["GOOGLE_REFRESH_TOKEN"],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.environ["GOOGLE_CLIENT_ID"],
        client_secret=os.environ["GOOGLE_CLIENT_SECRET"],
        scopes=SCOPES,
    )
    creds.refresh(GRequest())
    return gspread.authorize(creds)

@app.get("/api")
def root():
    return {"status": "online", "service": "Sheets API"}

@app.post("/api/lead")
async def receber_lead(request: Request):
    try:
        data = await request.json()
        sheet_id = data.get("sheet_id")
        if not sheet_id:
            return JSONResponse({"status": "error", "message": "sheet_id obrigatorio"}, status_code=400)

        gc = get_client()
        sh = gc.open_by_key(sheet_id)
        ws = sh.sheet1

        tz = pytz.timezone("America/Sao_Paulo")
        now = datetime.now(tz).strftime("%d/%m/%Y %H:%M:%S")

        linha = [
            now,
            data.get("nome", ""),
            data.get("email", ""),
            data.get("telefone", ""),
            data.get("mensagem", ""),
            data.get("utm_source", ""),
            data.get("utm_medium", ""),
            data.get("utm_campaign", ""),
            data.get("utm_term", ""),
            data.get("utm_content", ""),
            data.get("origem", "LP"),
        ]

        ws.append_row(linha)
        return {"status": "ok"}

    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)
