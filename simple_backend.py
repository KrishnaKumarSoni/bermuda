#!/usr/bin/env python3
"""
Simplified Bermuda Backend Server for Development
"""

import os
import json
import uuid
import time
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS

# Load environment variables
def load_env():
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                if line.strip() and not line.startswith('#') and '=' in line:
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value.strip('"\' ')

load_env()

app = Flask(__name__)

# Enable CORS for local development
CORS(app, 
     origins=['http://localhost:3000', 'http://127.0.0.1:3000', 'http://localhost:5173', 'http://127.0.0.1:5173'],
     allow_headers=['Content-Type', 'Authorization'],
     methods=['GET', 'POST', 'OPTIONS'],
     supports_credentials=True)

# Add explicit OPTIONS handling
@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = jsonify({})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', "*")
        response.headers.add('Access-Control-Allow-Methods', "*")
        return response

# Simple in-memory storage for demo
forms_db = {}
responses_db = {}
chat_sessions = {}

# Sample form data
sample_form = {
    "form_id": "test-form-coffee",
    "title": "Coffee Shop Feedback Survey",
    "questions": [
        {
            "id": "q1",
            "text": "How often do you visit coffee shops?",
            "type": "multiple_choice",
            "options": ["Daily", "Weekly", "Monthly", "Rarely"],
            "required": True,
            "enabled": True
        },
        {
            "id": "q2", 
            "text": "What's your favorite coffee drink?",
            "type": "text",
            "required": True,
            "enabled": True
        },
        {
            "id": "q3",
            "text": "How would you rate our service?",
            "type": "rating",
            "required": True,
            "enabled": True
        }
    ],
    "demographics": ["Age", "Location"],
    "created_at": "2024-01-01T00:00:00Z",
    "creator_id": "demo-user",
    "response_count": 5,
    "is_active": True
}

forms_db["test-form-coffee"] = sample_form

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'message': 'Simple Bermuda API is running',
        'timestamp': datetime.now().isoformat(),
        'openai_configured': bool(os.environ.get('OPENAI_API_KEY'))
    })

@app.route('/api/test', methods=['GET'])
def test_endpoint():
    return jsonify({
        'message': 'Backend is working!',
        'cors_enabled': True,
        'environment': 'development'
    })

@app.route('/api/forms/<form_id>', methods=['GET'])
def get_form(form_id):
    """Get form data (anonymous access)"""
    if form_id not in forms_db:
        return jsonify({'error': 'Form not found'}), 404
    
    return jsonify(forms_db[form_id])

@app.route('/api/forms', methods=['GET'])
def get_forms():
    """Get all forms for authenticated user (mock)"""
    # For demo, return all forms
    return jsonify({'forms': list(forms_db.values())})

@app.route('/api/infer', methods=['POST'])
def infer_form():
    """AI form generation from text dump"""
    print(f"🔥 Received infer request: {request.method} {request.url}")
    print(f"🔥 Headers: {dict(request.headers)}")
    
    try:
        data = request.get_json()
        print(f"🔥 Request data: {data}")
        text_dump = data.get('dump', '') if data else ''
        
        if not text_dump:
            print("❌ No text provided")
            return jsonify({'error': 'No text provided'}), 400
    
        # Simple mock response - in real app, this would use OpenAI
        mock_form = {
            "title": f"Generated Survey: {text_dump[:50]}...",
            "questions": [
                {
                    "id": "q1",
                    "text": "What is your main feedback?",
                    "type": "text",
                    "required": True,
                    "enabled": True
                },
                {
                    "id": "q2",
                    "text": "How satisfied are you?",
                    "type": "rating",
                    "required": True,
                    "enabled": True
                }
            ]
        }
        
        print(f"✅ Returning mock form: {mock_form}")
        return jsonify(mock_form)
        
    except Exception as e:
        print(f"❌ Error in infer_form: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/save-form', methods=['POST'])
def save_form():
    """Save a form"""
    data = request.get_json()
    form_id = str(uuid.uuid4())
    
    form_data = {
        'form_id': form_id,
        'created_at': datetime.now().isoformat(),
        **data
    }
    
    forms_db[form_id] = form_data
    return jsonify({'form_id': form_id})

@app.route('/api/chat-message', methods=['POST'])
def chat_message():
    """Handle chat messages"""
    data = request.get_json()
    message = data.get('message', '')
    session_id = data.get('session_id', '')
    form_id = data.get('form_id', '')
    
    if not session_id:
        session_id = str(uuid.uuid4())
    
    # Initialize session if needed
    if session_id not in chat_sessions:
        chat_sessions[session_id] = {
            'messages': [],
            'form_id': form_id,
            'created_at': datetime.now().isoformat()
        }
    
    # Add user message
    chat_sessions[session_id]['messages'].append({
        'text': message,
        'sender': 'user',
        'timestamp': int(time.time() * 1000)
    })
    
    # Generate bot response (mock)
    bot_responses = [
        "That's interesting! Can you tell me more?",
        "Thanks for sharing that with me.",
        "I understand. What else would you like to add?",
        "Great! Is there anything else you'd like to mention?",
        "Perfect! Thank you for your feedback."
    ]
    
    import random
    bot_response = random.choice(bot_responses)
    
    # Add bot message
    chat_sessions[session_id]['messages'].append({
        'text': bot_response,
        'sender': 'bot',
        'timestamp': int(time.time() * 1000) + 1000
    })
    
    return jsonify({
        'message': bot_response,
        'session_id': session_id
    })

@app.route('/api/forms/<form_id>/responses', methods=['GET'])
def get_responses(form_id):
    """Get responses for a form"""
    # Mock response data
    mock_responses = [
        {
            'response_id': 'resp1',
            'created_at': '2024-01-01T10:00:00Z',
            'responses': {'q1': 'Daily', 'q2': 'Latte', 'q3': 5},
            'demographics': {'Age': '25-34', 'Location': 'New York'}
        },
        {
            'response_id': 'resp2', 
            'created_at': '2024-01-01T11:00:00Z',
            'responses': {'q1': 'Weekly', 'q2': 'Cappuccino', 'q3': 4},
            'demographics': {'Age': '35-44', 'Location': 'California'}
        }
    ]
    
    return jsonify({'responses': mock_responses})

@app.route('/api/extract', methods=['POST'])
def extract_data():
    """Extract structured data from chat"""
    data = request.get_json()
    session_id = data.get('session_id', '')
    
    # Mock extraction
    mock_extraction = {
        'response_id': str(uuid.uuid4()),
        'responses': {
            'q1': 'Daily',
            'q2': 'Espresso',
            'q3': 5
        },
        'demographics': {
            'Age': '25-34',
            'Location': 'San Francisco'
        },
        'created_at': datetime.now().isoformat()
    }
    
    return jsonify(mock_extraction)

if __name__ == '__main__':
    print("🚀 Starting Simple Bermuda Backend")
    print("=" * 50)
    print(f"📍 Server URL: http://127.0.0.1:5000")
    print(f"📍 Health Check: http://127.0.0.1:5000/api/health")
    print(f"📍 Sample Form: http://127.0.0.1:5000/api/forms/test-form-coffee")
    print(f"🔐 OpenAI API Key: {'✅ Set' if os.environ.get('OPENAI_API_KEY') else '❌ Missing'}")
    print("=" * 50)
    print("💡 Press Ctrl+C to stop")
    print("🌐 CORS enabled for localhost:3000 and localhost:5173")
    print()
    
    try:
        app.run(host='127.0.0.1', port=5000, debug=True)
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
    except Exception as e:
        print(f"❌ Server error: {e}")