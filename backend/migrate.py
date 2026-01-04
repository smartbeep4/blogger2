#!/usr/bin/env python3
"""Script to run database migrations."""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from app import create_app
from flask_migrate import upgrade

# Create the application
app = create_app()

# Run migrations within app context
with app.app_context():
    upgrade()

print("Database migrations completed successfully!")
