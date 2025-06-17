import os
import logging
from flask import Flask, render_template, request, flash, jsonify, redirect, url_for, session

# Set loggers to ERROR level
logging.getLogger("pymongo").setLevel(logging.ERROR)
logging.getLogger("urllib3").setLevel(logging.ERROR)
logging.basicConfig(level=logging.ERROR)

# Create the Flask application
app = Flask(__name__)

# Load configuration from config.py
app.config.from_pyfile('config.py')
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

# Create upload directory if it doesn't exist
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Initialize the database (MongoDB)
with app.app_context():
    from routes import register_routes
    register_routes(app)

@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors"""
    return render_template('dashboard.html', error='Page not found'), 404

@app.errorhandler(500)
def internal_server_error(e):
    """Handle 500 errors"""
    return render_template('dashboard.html', error='An internal server error occurred'), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False) 