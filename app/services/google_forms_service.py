# app/services/google_forms_service.py

import requests
from app.db import SessionLocal
from sqlalchemy.orm import Session
from app.models.user_tokens import UserToken
from app.models.form_model import UserForms
from datetime import datetime


FORMS_API_BASE_URL = "https://forms.googleapis.com/v1/forms"


def get_access_token(email: str):
    db = SessionLocal()
    user = db.query(UserToken).filter(UserToken.email == email).first()
    db.close()
    if not user:
        raise Exception("User not found or not authorized")
    return user.access_token

def create_form(email: str, title: str):
    access_token = get_access_token(email)
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    data = {
        "info": {
            "title": title
        }
    }
    response = requests.post(FORMS_API_BASE_URL, headers=headers, json=data)
    if response.status_code != 200:
        raise Exception(f"Failed to create form: {response.text}")

    return response.json()

def add_mcq_to_form(email: str, form_id: str, question_title: str, question_options: list):
    access_token = get_access_token(email)

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    url = f"{FORMS_API_BASE_URL}/{form_id}:batchUpdate"

    data = {
        "requests": [
            {
                "createItem": {
                    "item": {
                        "title": question_title,
                        "questionItem": {
                            "question": {
                                "required": True,
                                "choiceQuestion": {
                                    "type": "RADIO",  # You can change to CHECKBOX or DROP_DOWN
                                    "options": [{"value": option} for option in question_options],
                                    "shuffle": False
                                }
                            }
                        }
                    },
                    "location": {
                        "index": 0  # Add at the top, you can adjust index
                    }
                }
            }
        ]
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code != 200:
        raise Exception(f"Failed to add question: {response.text}")

    return response.json()

def add_short_answer_to_form(email: str, form_id: str, question_title: str):
    access_token = get_access_token(email)

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    url = f"{FORMS_API_BASE_URL}/{form_id}:batchUpdate"

    data = {
        "requests": [
            {
                "createItem": {
                    "item": {
                        "title": question_title,
                        "questionItem": {
                            "question": {
                                "required": True,
                                "textQuestion": {
                                    "paragraph": False
                                }
                            }
                        }
                    },
                    "location": {"index": 0}
                }
            }
        ]
    }

    response = requests.post(url, headers=headers, json=data)
    if response.status_code != 200:
        raise Exception(f"Failed to add short answer question: {response.text}")
    return response.json()


def add_paragraph_to_form(email: str, form_id: str, question_title: str):
    access_token = get_access_token(email)

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    url = f"{FORMS_API_BASE_URL}/{form_id}:batchUpdate"

    data = {
        "requests": [
            {
                "createItem": {
                    "item": {
                        "title": question_title,
                        "questionItem": {
                            "question": {
                                "required": True,
                                "textQuestion": {
                                    "paragraph": True
                                }
                            }
                        }
                    },
                    "location": {"index": 0}
                }
            }
        ]
    }

    response = requests.post(url, headers=headers, json=data)
    if response.status_code != 200:
        raise Exception(f"Failed to add paragraph question: {response.text}")
    return response.json()

def add_checkbox_to_form(email: str, form_id: str, question_title: str, question_options: list):
    access_token = get_access_token(email)

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    url = f"{FORMS_API_BASE_URL}/{form_id}:batchUpdate"

    data = {
        "requests": [
            {
                "createItem": {
                    "item": {
                        "title": question_title,
                        "questionItem": {
                            "question": {
                                "required": True,
                                "choiceQuestion": {
                                    "type": "CHECKBOX",  # This defines a checkbox type question
                                    "options": [{"value": option} for option in question_options],
                                    "shuffle": False
                                }
                            }
                        }
                    },
                    "location": {
                        "index": 0  # Add at the top; adjust index as needed
                    }
                }
            }
        ]
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code != 200:
        raise Exception(f"Failed to add checkbox question: {response.text}")

    return response.json()

def add_dropdown_to_form(email: str, form_id: str, question_title: str, question_options: list):
    access_token = get_access_token(email)

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    url = f"{FORMS_API_BASE_URL}/{form_id}:batchUpdate"

    data = {
        "requests": [
            {
                "createItem": {
                    "item": {
                        "title": question_title,
                        "questionItem": {
                            "question": {
                                "required": True,
                                "choiceQuestion": {
                                    "type": "DROP_DOWN",  # This defines a dropdown type question
                                    "options": [{"value": option} for option in question_options],
                                    "shuffle": False
                                }
                            }
                        }
                    },
                    "location": {
                        "index": 0  # Add at the top; adjust index as needed
                    }
                }
            }
        ]
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code != 200:
        raise Exception(f"Failed to add dropdown question: {response.text}")

    return response.json()

def list_form_questions(email: str, form_id: str):
    access_token = get_access_token(email)

    headers = {
        "Authorization": f"Bearer {access_token}",
    }

    url = f"{FORMS_API_BASE_URL}/{form_id}"

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise Exception(f"Failed to fetch form questions: {response.text}")

    form_data = response.json()

    questions = []

    if "items" in form_data:
        for item in form_data["items"]:
            question_info = {
                "id": item.get("itemId"),
                "title": item.get("title"),
                "type": None
            }
            if "questionItem" in item:
                if "question" in item["questionItem"]:
                    if "choiceQuestion" in item["questionItem"]["question"]:
                        choice_type = item["questionItem"]["question"]["choiceQuestion"]["type"]
                        question_info["type"] = choice_type
                    else:
                        question_info["type"] = "TEXT"  # fallback if it's a text question
            questions.append(question_info)

    return questions

def delete_question_from_form(email: str, form_id: str, index: int):
    access_token = get_access_token(email)

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    url = f"{FORMS_API_BASE_URL}/{form_id}:batchUpdate"

    data = {
        "requests": [
            {
                "deleteItem": {
                    "location": {
                        "index": index
                    }
                }
            }
        ]
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code != 200:
        raise Exception(f"Failed to delete question: {response.text}")

    return response.json()


def get_form(email: str, form_id: str):
    access_token = get_access_token(email)
    headers = {
        "Authorization": f"Bearer {access_token}",
    }

    url = f"{FORMS_API_BASE_URL}/{form_id}"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch form: {response.text}")

    return response.json()

def clone_form(email: str, source_form_id: str, new_form_title: str):
    access_token = get_access_token(email)

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    # Step 1: Get the source form
    get_url = f"{FORMS_API_BASE_URL}/{source_form_id}"
    source_response = requests.get(get_url, headers=headers)

    if source_response.status_code != 200:
        raise Exception(f"Failed to fetch source form: {source_response.text}")

    source_form_data = source_response.json()

    # Step 2: Create a new form with the same structure
    create_url = FORMS_API_BASE_URL
    create_data = {
        "info": {
            "title": new_form_title
        }
    }

    create_response = requests.post(create_url, headers=headers, json=create_data)

    if create_response.status_code != 200:
        raise Exception(f"Failed to create new form: {create_response.text}")

    new_form_id = create_response.json()["formId"]

    # Step 3: Copy items from the original form
    items = source_form_data.get("items", [])
    batch_update_url = f"{FORMS_API_BASE_URL}/{new_form_id}:batchUpdate"
    batch_data = {
        "requests": []
    }

    for i, item in enumerate(items):
        batch_data["requests"].append({
            "createItem": {
                "item": item,
                "location": {"index": i}
            }
        })

    batch_response = requests.post(batch_update_url, headers=headers, json=batch_data)

    if batch_response.status_code != 200:
        raise Exception(f"Failed to copy questions: {batch_response.text}")

    return {
        "new_form_id": new_form_id,
        "title": new_form_title
    }

def save_form_metadata(form_id: str, title: str, description: str, email: str):

    db = SessionLocal()
    """
    Saves form metadata (ID, title, description, email) to the database.
    
    Args:
    - form_id (str): Google form ID
    - title (str): Google form title
    - description (str): Google form description
    - email (str): Email of the user who created the form
    - db (Session): SQLAlchemy session object

    Returns:
    - form (UserForms): The created UserForms object
    """
    try:
        # Create a new entry for the form metadata
        form = UserForms(
            form_id=form_id,
            title=title,
            email=email,
            description=description,
            created_at=datetime.utcnow()  # Store the creation timestamp
        )
        
        # Add and commit the entry to the database
        db.add(form)
        db.commit()
        db.refresh(form)

        return form

    except Exception as e:
        db.rollback()  # Rollback in case of any error
        raise Exception(f"Failed to save form metadata: {str(e)}")
    db.close()

def batch_update_form(email: str, form_id: str, requests_payload: list):
    access_token = get_access_token(email)
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    url = f"{FORMS_API_BASE_URL}/{form_id}:batchUpdate"
    payload = {
        "requests": requests_payload
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 200:
        raise Exception(f"Failed to update form: {response.text}")

    return response.json()

def list_forms_placeholder():
    # Placeholder because Google Forms API currently DOES NOT support listing forms
    # We need to use Google Drive API later to find forms created by user
    pass
