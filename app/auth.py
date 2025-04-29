# app/auth.py

from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
import os
from dotenv import load_dotenv
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
from google.auth.transport import requests
from app.db import SessionLocal
from app.models import UserToken

load_dotenv()

router = APIRouter()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")

SCOPES = [
    "https://www.googleapis.com/auth/forms.body",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "openid"
]

# OAuth flow init
def get_google_flow():
    return Flow.from_client_config(
        {
            "web": {
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "redirect_uris": [GOOGLE_REDIRECT_URI],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token"
            }
        },
        scopes=SCOPES,
        redirect_uri=GOOGLE_REDIRECT_URI
    )

@router.get("/login")
def login():
    flow = get_google_flow()
    auth_url, _ = flow.authorization_url(prompt="consent", access_type="offline", include_granted_scopes="true")
    return RedirectResponse(auth_url)


@router.get("/callback")
def callback(request: Request):
    flow = get_google_flow()
    flow.fetch_token(authorization_response=str(request.url))
    credentials = flow.credentials

    access_token = credentials.token
    refresh_token = credentials.refresh_token

    # Decode the ID token properly
    id_info = id_token.verify_oauth2_token(
        credentials.id_token,
        requests.Request(),
        GOOGLE_CLIENT_ID
    )

    email = id_info.get("email")

    # Now proceed saving email and tokens
    db = SessionLocal()
    user = db.query(UserToken).filter(UserToken.email == email).first()
    if user:
        user.access_token = access_token
        user.refresh_token = refresh_token
    else:
        user = UserToken(email=email, access_token=access_token, refresh_token=refresh_token)
        db.add(user)

    db.commit()
    db.close()

    return {
        "message": "Authentication successful",
        "email": email,
    }