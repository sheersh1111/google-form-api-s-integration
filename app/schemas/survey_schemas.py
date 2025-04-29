from pydantic import BaseModel

class CreateSurveyRequest(BaseModel):
    email: str
    title: str
    description: str = ""

from pydantic import BaseModel
from typing import List

class AddQuestionRequest(BaseModel):
    email: str
    form_id: str
    question_title: str
    question_options: List[str]

class AddShortAnswerRequest(BaseModel):
    email: str
    form_id: str
    question_title: str

class AddParagraphRequest(BaseModel):
    email: str
    form_id: str
    question_title: str
