# frontend/api_client.py

import requests

API_BASE_URL = "http://127.0.0.1:5000/api"
TOKEN = None
USER_ROLE = None

def set_auth(token, role):
    global TOKEN, USER_ROLE
    TOKEN = token
    USER_ROLE = (role or "").strip().lower()

def get_headers():
    headers = {"Content-Type": "application/json"}
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    return headers

def login_user(email, password):
    url = f"{API_BASE_URL}/auth/login"
    data = {"email": email, "password": password}
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            result = response.json()
            set_auth(result['token'], result['role'])
            return result
        return {"error": response.json().get('error', 'Login failed.')}
    except requests.exceptions.RequestException as e:
        return {"error": f"Network error: {e}"}

def signup_user(name, email, password, role="student"):
    url = f"{API_BASE_URL}/auth/signup"
    data = {"name": name, "email": email, "password": password, "role": role}
    try:
        response = requests.post(url, json=data)
        if response.status_code == 201:
            return response.json()
        return {"error": response.json().get('error', 'Signup failed.')}
    except requests.exceptions.RequestException as e:
        return {"error": f"Network error: {e}"}

def get_items(status=None, search=None, include_resolved=False):
    url = f"{API_BASE_URL}/items"
    params = []
    if status:
        params.append(f"status={status}")
    if search:
        params.append(f"search={search}")
    if include_resolved:
        params.append("include_resolved=true")
    if params:
        url += "?" + "&".join(params)
    try:
        response = requests.get(url, headers=get_headers())
        if response.status_code == 200:
            return response.json()
        return []
    except requests.exceptions.RequestException:
        return []

def claim_item_api(item_id, verification_details):
    url = f"{API_BASE_URL}/items/{item_id}/claim"
    data = {"verification_details": verification_details}
    try:
        response = requests.post(url, json=data, headers=get_headers())
        if response.status_code == 201:
            return response.json()
        return {"error": response.json().get('error', 'Claim failed.')}
    except requests.exceptions.RequestException as e:
        return {"error": f"Network error: {e}"}

def get_categories():
    # Attempt to fetch categories from backend; return an empty list if unavailable
    url = f"{API_BASE_URL}/categories"
    try:
        response = requests.get(url, headers=get_headers())
        if response.status_code == 200:
            return response.json()
        return []
    except requests.exceptions.RequestException:
        return []

def report_item_api(report_data):
    url = f"{API_BASE_URL}/items"
    try:
        response = requests.post(url, json=report_data, headers=get_headers())
        if response.status_code == 201:
            return response.json()
        return {"error": response.json().get('error', 'Report failed.')}
    except requests.exceptions.RequestException:
        return {"error": "Network error or API offline."}


def forgot_password_api(email):
    url = f"{API_BASE_URL}/auth/forgot-password"
    try:
        response = requests.post(url, json={"email": email})
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"Network error: {e}"}


def reset_password_api(email, otp, new_password):
    url = f"{API_BASE_URL}/auth/reset-password"
    data = {"email": email, "otp": otp, "new_password": new_password}
    try:
        response = requests.post(url, json=data)
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"Network error: {e}"}