#!/usr/bin/env python3
"""
App file
"""

from flask import Flask, request, jsonify, abort
from os import getenv
from flask_cors import CORS
from api.v1.views import app_views
from api.v1.auth.auth import Auth, BasicAuth
from models.user import User

app = Flask(__name__)
CORS(app)

auth = None
if getenv("AUTH_TYPE") == "basic_auth":
    auth = BasicAuth()
else:
    auth = Auth()


@app.before_request
def before_request():
    """ Method to handle before request """
    if auth is None:
        return
    excluded_paths = ['/api/v1/status/', '/api/v1/unauthorized/',
                      '/api/v1/forbidden/']
    if not auth.require_auth(request.path, excluded_paths):
        return
    if auth.authorization_header(request) is None:
        abort(401)
    if auth.current_user(request) is None:
        abort(403)


@app.errorhandler(401)
def unauthorized(error):
    return jsonify({"error": "Unauthorized"}), 401


@app.errorhandler(403)
def forbidden(error):
    return jsonify({"error": "Forbidden"}), 403


@app.route('/api/v1/status', methods=['GET'], strict_slashes=False)
def status():
    """ Returns the status of the API """
    return jsonify({"status": "OK"})


@app.route('/api/v1/users', methods=['GET'], strict_slashes=False)
def users():
    """ Returns the list of all users """
    users = storage.all(User).values()
    users_list = [user.to_dict() for user in users]
    return jsonify(users_list)


if __name__ == "__main__":
    host = getenv("API_HOST", "0.0.0.0")
    port = getenv("API_PORT", "5000")
    app.run(host=host, port=port)
