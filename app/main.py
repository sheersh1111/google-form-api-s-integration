# app/main.py

from fastapi import FastAPI
from app.auth import router as auth_router
from app.survey import router as survey_router
import os

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"


from app.db import engine
from app.models.user_tokens import UserToken

# Create tables
UserToken.metadata.create_all(bind=engine)

app = FastAPI()

# Include routes
app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(survey_router, prefix="/surveys", tags=["Surveys"])

@app.get("/")
def read_root():
    return {"message": "Welcome to Atlas AI Backend"}
