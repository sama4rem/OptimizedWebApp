from flask import Flask
import os

from .routes import app_routes

def create_app():
    app = Flask(__name__)

    # Set the secret key (use an environment variable for security)
    app.secret_key = os.environ.get("SECRET_KEY", "112233")  # Set it here

    @app.route("/")
    def home():
        return "Welcome to the Web App! Go to /students to see the student page."

    app.register_blueprint(app_routes)

    return app
