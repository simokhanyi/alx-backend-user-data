#!/usr/bin/env python3
"""
Auth module
"""
from flask import request
from typing import List, TypeVar
import re


class Auth:
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

    def authorization_header(self, request=None) -> str:
        """ Method to get the authorization header """
        if request is None:
            return None
        if 'Authorization' not in request.headers:
            return None
        return request.headers['Authorization']

    def current_user(self, request=None) -> TypeVar('User'):
        """ Method to get the current user """
        return None
