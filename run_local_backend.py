#!/usr/bin/env python3
"""
Local development server for Bermuda API with proper CORS setup
"""

import os
import sys
from pathlib import Path

# Add the API directory to Python path
api_dir = Path(__file__).parent / 'api'
sys.path.insert(0, str(api_dir))

# Load environment variables from .env
def load_env():
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                if line.strip() and not line.startswith('#') and '=' in line:
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value.strip('"\'')

# Load environment variables
load_env()

# Set Flask environment for local development
os.environ['FLASK_ENV'] = 'development'
os.environ['FLASK_DEBUG'] = 'True'

# Now import and configure the Flask app
from flask import Flask
from flask_cors import CORS
import json

# Import the respondent module
try:
    import respondent
    app = respondent.app
except ImportError as e:
    print(f"❌ Error importing respondent module: {e}")
    sys.exit(1)

# Override CORS for local development
CORS(app, 
     origins=['http://localhost:3000', 'http://127.0.0.1:3000', 'http://localhost:5173', 'http://127.0.0.1:5173'],
     allow_headers=['Content-Type', 'Authorization'],
     methods=['GET', 'POST', 'OPTIONS'],
     supports_credentials=True)

# Add a health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'message': 'Bermuda API is running locally',
        'timestamp': str(os.environ.get('FLASK_ENV', 'production')),
        'cors_enabled': True
    })

# Add a simple test endpoint
@app.route('/api/test', methods=['GET'])
def test_endpoint():
    return jsonify({
        'message': 'Local backend is working!',
        'environment': os.environ.get('FLASK_ENV', 'production'),
        'cors_origins': ['http://localhost:3000', 'http://127.0.0.1:3000', 'http://localhost:5173']
    })

if __name__ == '__main__':
    print("🚀 Starting Bermuda Local Development Server")
    print("=" * 50)
    print(f"📍 Server URL: http://127.0.0.1:5000")
    print(f"📍 Health Check: http://127.0.0.1:5000/api/health")
    print(f"📍 Test Endpoint: http://127.0.0.1:5000/api/test")
    print(f"📍 Environment: {os.environ.get('FLASK_ENV', 'production')}")
    print(f"🔐 OpenAI API Key: {'✅ Set' if os.environ.get('OPENAI_API_KEY') else '❌ Missing'}")
    print("=" * 50)
    print("💡 Use Ctrl+C to stop the server")
    print("🌐 CORS enabled for local development")
    print()
    
    try:
        app.run(
            host='127.0.0.1',
            port=5000,
            debug=True,
            use_reloader=True
        )
    except Exception as e:
        print(f"❌ Server failed to start: {e}")
        sys.exit(1)