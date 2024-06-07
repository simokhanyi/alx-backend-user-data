#!/usr/bin/env python3
"""
SessionAuth module
"""
from api.v1.auth.auth import Auth
import uuid
from typing import List


class SessionAuth:
    """Class for managing session authentication."""

    user_id_by_session_id = {}

    def create_session(self, user_id: str = None) -> str:
        """
        Create a session for a given user ID.

        Args:
            user_id (str): The ID of the user.

        Returns:
            str: The session ID generated for the user.

        """
        if user_id is None or not isinstance(user_id, str):
            return None
        session_id = str(uuid.uuid4())
        self.user_id_by_session_id[session_id] = user_id
        return session_id

    def user_id_for_session_id(self, session_id: str = None) -> str:
        """
        Retrieve the user ID associated with a session ID.

        Args:
            session_id (str): The session ID to retrieve the user ID for.

        Returns:
            str: The user ID associated with the session ID, or None.

        """
        if session_id is None or not isinstance(session_id, str):
            return None
        return self.user_id_by_session_id.get(session_id)

    def require_auth(self, path: str, excluded_paths: List[str]) -> bool:
        """ Method to check if authentication is required """
        if path is None:
            return True
        if excluded_paths is None or len(excluded_paths) == 0:
            return True

        # Ensure path ends with a slash for comparison
        if not path.endswith('/'):
            path += '/'

        for excluded_path in excluded_paths:
            # Convert the excluded path to a regular expression
            if excluded_path.endswith('*'):
                pattern = re.escape(excluded_path[:-1]) + '.*'
            else:
                pattern = re.escape(excluded_path) + '/?'

            if re.match(pattern, path):
                return False

        return True


if __name__ == "__main__":
    sa = SessionAuth()

    print("{} => {}: {}".format(user_id, session, sa.user_id_by_session_id))

    user_id = None
    session = sa.create_session(user_id)
    print("{} => {}: {}".format(user_id, session, sa.user_id_by_session_id))

    user_id = 89
    session = sa.create_session(user_id)
    print("{} => {}: {}".format(user_id, session, sa.user_id_by_session_id))

    user_id = "abcde"
    session = sa.create_session(user_id)
    print("{} => {}: {}".format(user_id, session, sa.user_id_by_session_id))

    user_id = "fghij"
    session = sa.create_session(user_id)
    print("{} => {}: {}".format(user_id, session, sa.user_id_by_session_id))

    user_id = "abcde"
    session = sa.create_session(user_id)
    print("{} => {}: {}".format(user_id, session, sa.user_id_by_session_id))
