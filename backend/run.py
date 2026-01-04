"""Application entry point."""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from app import create_app

# Create the application
app = create_app()

if __name__ == '__main__':
    # Run the development server
    app.run(host='0.0.0.0', port=5000, debug=True)
