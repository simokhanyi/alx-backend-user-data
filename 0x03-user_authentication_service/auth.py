#!/usr/bin/env python3
"""Module for authentication.
"""

import logging
from typing import Union
from uuid import uuid4

import bcrypt
from sqlalchemy.orm.exc import NoResultFound

from db import DB
from user import User

logging.disable(logging.WARNING)


def _hash_password(password: str) -> bytes:
    """Hashes a password and returns bytes.

    Args:
        password (str): The password to be hashed.

    Returns:
        bytes: The hashed password.
    """
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())


def _generate_uuid() -> str:
    """Generates a uuid.

    Returns:
        str: string representation of a new UUID.
    """
    return str(uuid4())


class Auth:
    """Auth class to interact with the authentication database.
    """

    def __init__(self):
        self._db = DB()

    def register_user(self, email: str, password: str) -> User:
        """Registers a new user with the given email and password.

        Args:
            email (str): The email of the new user.
            password (str): The password of the new user.

        Returns:
            User: A User object representing the newly created user.

        Raises:
            ValueError: If a user with the given email already exists.
        """
        try:
            self._db.find_user_by(email=email)
            raise ValueError(f"User {email} already exists")
        except NoResultFound:
            hashed_password = _hash_password(password)
            user = self._db.add_user(email, hashed_password)
            return user

    def valid_login(self, email: str, password: str) -> bool:
        """Validate user login credentials.

        Args:
            email (str): The email of the user.
            password (str): The password to validate.

        Returns:
            bool: True if the login is valid, False otherwise.
        """
        try:
            user = DB().find_user_by(email=email)
            if user:
                pwd_valid = bcrypt.checkpw(password.encode("utf-8"),
                                           user.hashed_password.encode("utf-8"))
                if pwd_valid:
                    return True
            return False
        except NoResultFound:
            return False

    def create_session(self, email: str) -> Union[str, None]:
        """Creates a session and returns the session ID as a string.

        Args:
            email (str): Email of user to create session for.

        Returns:
            Union[str, None]: Session ID if the user is found, otherwise None.
        """
        try:
            user = self._db.find_user_by(email=email)
            session_id = _generate_uuid()
            self._db.update_user(user.id, session_id=session_id)
            return session_id
        except NoResultFound:
            return None

    def get_user_from_session_id(self, session_id: str) -> Union[User, None]:
        """Retrieve a User object from a session ID.

        Args:
            session_id (str): The ID of the session to retrieve the user from.

        Returns:
            Union[User, None]: A User object corresponding to the session ID if
                               one exists, otherwise None.
        """
        if not session_id:
            return None
        try:
            user = self._db.find_user_by(session_id=session_id)
            return user
        except NoResultFound:
            return None

    def destroy_session(self, user_id: int) -> None:
        """Destroys the session associated with a user.

        Args:
            user_id (int): The ID of the user whose session is to be destroyed.
        """
        if user_id:
            self._db.update_user(user_id, session_id=None)

    def get_reset_password_token(self, email: str) -> str:
        """Generates a password reset token for a user.

        Args:
            email (str): A string representing the email address of the user to
                         generate a password reset token for.

        Raises:
            ValueError: If no user with the specified email address is found.

        Returns:
            str: A string representing the password reset token generated for
                 the user.
        """
        try:
            user = self._db.find_user_by(email=email)
            reset_token = _generate_uuid()
            self._db.update_user(user.id, reset_token=reset_token)
            return reset_token
        except NoResultFound:
            raise ValueError(f"User with email {email} does not exist")

    def update_password(self, reset_token: str, password: str) -> None:
        """Updates a user's password using a reset token.

        Args:
            reset_token (str): The reset token associated with the user.
            password (str): The new password to set.

        Raises:
            ValueError: If the reset token is invalid (i.e., not associated
                        with a user).
        """
        try:
            user = self._db.find_user_by(reset_token=reset_token)
            hashed_password = _hash_password(password)
            self._db.update_user(
                user.id, hashed_password=hashed_password, reset_token=None
            )
        except NoResultFound:
            raise ValueError("Invalid reset token")
