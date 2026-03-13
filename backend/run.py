"""Run the Flask application."""
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

from app import create_app, db

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()
    
    # Run the application on port 5001
    app.run(host='0.0.0.0', port=5001, debug=True)
