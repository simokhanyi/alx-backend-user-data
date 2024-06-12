#!/usr/bin/env python3
"""Module for simple end-to-end (E2E) integration tests for `app.py`.
"""

import requests
from app import AUTH

EMAIL = "guillaume@holberton.io"
PASSWD = "b4l0u"
NEW_PASSWD = "t4rt1fl3tt3"
BASE_URL = "http://0.0.0.0:5000"


def register_user(email: str, password: str) -> None:
    """Test the registration of a user.

    Args:
        email (str): The user's email.
        password (str): The user's password.
    """
    url = f"{BASE_URL}/users"
    data = {
        "email": email,
        "password": password
    }
    response = requests.post(url, data=data)
    print("register_user response:", response.status_code, response.json())
    assert response.status_code == 200
    assert response.json() == {"email": email, "message": "user created"}

    response = requests.post(url, data=data)
    print("register_user (duplicate) response:", response.status_code,
          response.json())
    assert response.status_code == 400
    assert response.json() == {"message": "email already registered"}


def log_in_wrong_password(email: str, password: str) -> None:
    """Test logging in with wrong password.

    Args:
        email (str): The email address of the user to log in.
        password (str): The user's password.
    """
    url = f"{BASE_URL}/sessions"
    data = {
        "email": email,
        "password": password
    }
    response = requests.post(url, data=data)
    print("log_in_wrong_password response:", response.status_code)
    assert response.status_code == 401


def profile_unlogged() -> None:
    """Tests behavior of trying to retrieve profile information
    while being logged out.
    """
    url = f"{BASE_URL}/profile"
    response = requests.get(url)
    print("profile_unlogged response:", response.status_code)
    assert response.status_code == 403


def profile_logged(session_id: str) -> None:
    """Tests retrieving profile information whilst logged in.

    Args:
        session_id (str): The session ID of the logged in user.
    """
    url = f"{BASE_URL}/profile"
    cookies = {
        "session_id": session_id
    }
    response = requests.get(url, cookies=cookies)
    print("profile_logged response:", response.status_code)
    if response.status_code == 200:
        print(response.json())
        payload = response.json()
        assert "email" in payload
        user = AUTH.get_user_from_session_id(session_id)
        assert user.email == payload["email"]
    else:
        print("Failed to get profile:", response.text)


def log_out(session_id: str) -> None:
    """Tests tests the process of logging out from a session.

    Args:
        session_id (str): The session ID of the user to log out.
    """
    url = f"{BASE_URL}/sessions"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "session_id": session_id
    }
    response = requests.delete(url, headers=headers, cookies=data)
    print("log_out response:", response.status_code)
    assert response.status_code == 200


def reset_password_token(email: str) -> str:
    """Tests the process of requesting a password reset.

    Args:
        email (str): The email to request password reset for.
    """
    url = f"{BASE_URL}/reset_password"
    data = {
        "email": email
    }
    response = requests.post(url, data=data)
    print("reset_password_token response:", response.status_code)
    if response.status_code == 200:
        response_json = response.json()
        print(response_json)
        assert "email" in response_json
        assert response_json["email"] == email
        return response_json["reset_token"]
    else:
        print("Failed to get reset token:", response.text)


def update_password(email: str, reset_token: str, new_password: str) -> None:
    """Tests updating a user's password.

    Args:
        email (str): The email of the user whose password should be updated.
        reset_token (str): The reset token generated for the user.
        new_password (str): The new password to set for the user.
    """
    url = f"{BASE_URL}/reset_password"
    data = {
        "email": email,
        "reset_token": reset_token,
        "new_password": new_password
    }
    response = requests.put(url, data=data)
    print("update_password response:", response.status_code)
    if response.status_code == 200:
        response_json = response.json()
        print(response_json)
        assert response_json["message"] == "Password updated"
        assert response_json["email"] == email
    else:
        print("Failed to update password:", response.text)


def log_in(email: str, password: str) -> str:
    """Tests logging in.

    Args:
        email (str): The email address of the user to log in.
        password (str): The user's password.
    """
    url = f"{BASE_URL}/sessions"
    data = {
        "email": email,
        "password": password
    }
    response = requests.post(url, data=data)
    print("log_in response:", response.status_code)
    if response.status_code == 200:
        response_json = response.json()
        print(response_json)
        assert "email" in response_json
        assert "message" in response_json
        assert response_json["email"] == email
        return response.cookies.get("session_id")
    else:
        print("Failed to log in:", response.text)
        return "Invalid credentials"


if __name__ == "__main__":
    register_user(EMAIL, PASSWD)
    log_in_wrong_password(EMAIL, NEW_PASSWD)
    profile_unlogged()
    session_id = log_in(EMAIL, PASSWD)
    if session_id != "Invalid credentials":
        print("Logged in, session_id:", session_id)
        profile_logged(session_id)
        log_out(session_id)
        reset_token = reset_password_token(EMAIL)
        if reset_token:
            update_password(EMAIL, reset_token, NEW_PASSWD)
            log_in(EMAIL, NEW_PASSWD)
