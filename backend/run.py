#!/usr/bin/env python3
"""
Development server runner for Bermuda backend
"""
import os
from dotenv import load_dotenv
from app import app

# Load environment variables
load_dotenv('../.env')

if __name__ == '__main__':
    # Set environment variables
    os.environ['FLASK_ENV'] = 'development'
    os.environ['FLASK_DEBUG'] = 'True'
    
    print("Starting Bermuda backend server...")
    print(f"OpenAI API Key: {'✓ Set' if os.getenv('OPENAI_API_KEY') else '✗ Missing'}")
    print(f"Firebase Project ID: {os.getenv('FIREBASE_PROJECT_ID', 'Not set')}")
    print("Server will be available at: http://localhost:5000")
    
    app.run(
        debug=True,
        host='0.0.0.0',
        port=5000,
        use_reloader=True
    )