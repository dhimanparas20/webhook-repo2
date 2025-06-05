from app.webhook.routes import webhook
from flask import Flask, render_template, make_response, request, session, redirect, url_for, current_app, jsonify
from flask_restful import Api, Resource
from dotenv import load_dotenv
from os import getenv,path,remove
import logging

# Load environment variables from .env if present
load_dotenv()


# Creating our flask app
def create_app():

    app = Flask(__name__)
    app.secret_key = getenv("FLASK_SECRET_KEY", "your_secret_key_here")

    log_file = 'app.log'
    debug_mode = getenv("DEBUG", True) == "true"

    # If in debug mode, remove the old log file before starting
    if debug_mode and path.exists(log_file):
        remove(log_file)

    # Set up logging to file
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO if debug_mode else logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    # registering all the blueprints
    app.register_blueprint(webhook)

    return app
