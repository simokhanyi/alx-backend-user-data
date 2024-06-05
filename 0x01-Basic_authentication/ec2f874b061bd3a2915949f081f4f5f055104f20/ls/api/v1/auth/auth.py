#!/usr/bin/env python3
"""
Auth file
"""

from flask import request
from typing import List, TypeVar
from models.user import User


class Auth:
    def require_auth(self, path: str, excluded_paths: List[str]) -> bool:
        """ Checks if authentication is required """
        if path is None or excluded_paths is None or len(excluded_paths) == 0:
            return True

        if path.endswith('/'):
            path = path[:-1]

        for excluded_path in excluded_paths:
            if excluded_path.endswith('*'):
                if path.startswith(excluded_path[:-1]):
                    return False
            elif path == excluded_path or path == excluded_path + '/':
                return False

        return True

    def authorization_header(self, request=None) -> str:
        """ Returns the authorization header """
        if request is None or 'Authorization' not in request.headers:
            return None
        return request.headers['Authorization']

    def current_user(self, request=None) -> TypeVar('User'):
        """ Returns the current user """
        if request is None or 'Forbidden' not in request.user:
            return None
        return request.user['Forbidden']


class BasicAuth(Auth):
    def __init__(self):
        pass
