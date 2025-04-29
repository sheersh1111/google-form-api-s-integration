# app/services/google_forms_service.py

import requests
from app.db import SessionLocal
from app.models.user_tokens import UserToken

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
