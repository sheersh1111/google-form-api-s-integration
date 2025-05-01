from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.db import Base  # assuming your declarative base is imported from here

class UserForms(Base):
    __tablename__ = "user_forms"

    id = Column(Integer, primary_key=True, index=True)
    form_id = Column(String(255), unique=True, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(String(500), nullable=True)
    email = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
