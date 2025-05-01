# app/survey.py

from fastapi import APIRouter, Depends, HTTPException
from app.services import google_forms_service
from app.schemas.survey_schemas import CreateSurveyRequest, AddQuestionRequest, AddShortAnswerRequest, AddParagraphRequest, CloneFormRequest
from pydantic import BaseModel
from app.db import get_db
from sqlalchemy.orm import Session
from app.models.user_tokens import UserToken
from app.models.form_model import UserForms

router = APIRouter()

@router.get("/user/forms")
def get_user_forms(email: str, db: Session = Depends(get_db)):
    try:
        forms = db.query(UserForms).filter(UserForms.email == email).all()
        return [
            {
                "id": form.id,
                "formId": form.form_id,
                "title": form.title,
                "description": form.description,
                "created_at": form.created_at,
                "editLink": f"https://docs.google.com/forms/d/{form.form_id}/edit",
                "publicLink": f"https://docs.google.com/forms/d/{form.form_id}/viewform"
            }
            for form in forms
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch user forms: {str(e)}")

@router.post("/create")
def create_survey(request: CreateSurveyRequest):
    data= google_forms_service.create_form(request.email, request.title)
    # after form creation
    google_forms_service.save_form_metadata(
        form_id=data["formId"],
        title=data["info"]["title"],
        description=data["info"].get("description", ""),
        email=request.email
    )
    return data

@router.get("/get/{form_id}")
def get_survey(email: str, form_id: str):
    return google_forms_service.get_form(email, form_id)

@router.post("/add-mcq")
def add_mcq(
    request: AddQuestionRequest,
    db: Session = Depends(get_db)
):
    user = db.query(UserToken).filter(UserToken.email == request.email).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not authorized")

    try:
        response = google_forms_service.add_mcq_to_form(
            email=request.email,
            form_id=request.form_id,
            question_title=request.question_title,
            question_options=request.question_options
        )
        return {"message": "Question added successfully", "response": response}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/add-short-answer")
def add_short_answer(
    request: AddShortAnswerRequest,
    db: Session = Depends(get_db)
):
    user = db.query(UserToken).filter(UserToken.email == request.email).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not authorized")

    try:
        response = google_forms_service.add_short_answer_to_form(
            email=request.email,
            form_id=request.form_id,
            question_title=request.question_title
        )
        return {"message": "Short answer question added successfully", "response": response}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/add-paragraph")
def add_paragraph(
    request: AddParagraphRequest,
    db: Session = Depends(get_db)
):
    user = db.query(UserToken).filter(UserToken.email == request.email).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not authorized")

    try:
        response = google_forms_service.add_paragraph_to_form(
            email=request.email,
            form_id=request.form_id,
            question_title=request.question_title
        )
        return {"message": "Paragraph question added successfully", "response": response}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/add-checkbox")
def add_checkbox(
    request: AddQuestionRequest,
    db: Session = Depends(get_db)
):
    user = db.query(UserToken).filter(UserToken.email == request.email).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not authorized")

    try:
        response = google_forms_service.add_checkbox_to_form(
            email=request.email,
            form_id=request.form_id,
            question_title=request.question_title,
            question_options=request.question_options
        )
        return {"message": "Checkbox question added successfully", "response": response}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/add-dropdown")
def add_dropdown(
    request: AddQuestionRequest,
    db: Session = Depends(get_db)
):
    user = db.query(UserToken).filter(UserToken.email == request.email).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not authorized")

    try:
        response = google_forms_service.add_dropdown_to_form(
            email=request.email,
            form_id=request.form_id,
            question_title=request.question_title,
            question_options=request.question_options
        )
        return {"message": "Dropdown question added successfully", "response": response}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/list-questions/{email}/{form_id}")
def list_questions(
    email: str,
    form_id: str,
    db: Session = Depends(get_db)
):
    user = db.query(UserToken).filter(UserToken.email == email).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not authorized")

    try:
        questions = google_forms_service.list_form_questions(email=email, form_id=form_id)
        return {"questions": questions}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/delete-question/{email}/{form_id}/{index}")
def delete_question(email: str, form_id: str, index: int, db: Session = Depends(get_db)):
    user = db.query(UserToken).filter(UserToken.email == email).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not authorized")

    try:
        response = google_forms_service.delete_question_from_form(email=email, form_id=form_id, index=index)
        return {"message": "Question deleted successfully", "response": response}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/clone-form")
def clone_form(request: CloneFormRequest, db: Session = Depends(get_db)):
    try:
        result = google_forms_service.clone_form(
            email=request.email,
            source_form_id=request.source_form_id,
            new_form_title=request.new_form_title
        )
        # after form creation
        google_forms_service.save_form_metadata(
            form_id=result["new_form_id"],
            title=result["title"],
            description=result.get("description", ""),
            email=request.email
        )
        return {"message": "Form cloned successfully", "data": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to clone form: {str(e)}")

@router.post("/update/{form_id}")
def update_survey(email: str, form_id: str, requests_payload: list):
    return google_forms_service.batch_update_form(email, form_id, requests_payload)

@router.post("/clone")
def clone_survey():
    return {"message": "Clone a template survey"}

@router.get("/import")
def import_surveys():
    return {"message": "Import existing surveys"}
