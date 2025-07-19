#!/usr/bin/env python3
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
import uuid
from datetime import datetime
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore, auth

# Load environment variables
load_dotenv('../.env')

app = Flask(__name__)
CORS(app)

# Initialize Firebase
try:
    firebase_cred_path = os.path.join(os.path.dirname(__file__), '..', 'firebase-adminsdk.json')
    cred = credentials.Certificate(firebase_cred_path)
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("✓ Firebase initialized successfully")
except Exception as e:
    print(f"✗ Firebase initialization failed: {e}")
    db = None

def verify_token(token):
    """Verify Firebase ID token"""
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token['uid']
    except:
        return None

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'firebase': 'connected' if db else 'disconnected',
        'openai': 'configured' if os.getenv('OPENAI_API_KEY') else 'missing'
    }), 200

@app.route('/api/infer', methods=['POST'])
def infer_form():
    """Mock infer endpoint for testing"""
    try:
        # Verify authentication
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Missing or invalid token'}), 401
        
        token = auth_header.split(' ')[1]
        user_id = verify_token(token)
        if not user_id:
            return jsonify({'error': 'Invalid token'}), 401
        
        # Get request data
        data = request.get_json()
        dump = data.get('dump', '').strip()
        
        # Validate dump
        if len(dump) < 20:
            return jsonify({'error': 'Invalid dump - too short'}), 400
        
        # Mock response for testing
        mock_response = {
            'title': 'Customer Feedback Survey',
            'questions': [
                {
                    'text': 'What is your favorite coffee type?',
                    'type': 'multiple_choice',
                    'options': ['Espresso', 'Latte', 'Cappuccino', 'Americano', 'Other'],
                    'enabled': True
                },
                {
                    'text': 'How often do you visit coffee shops?',
                    'type': 'multiple_choice',
                    'options': ['Daily', 'Weekly', 'Monthly', 'Rarely'],
                    'enabled': True
                },
                {
                    'text': 'Do you have any dietary restrictions?',
                    'type': 'yes_no',
                    'options': ['Yes', 'No'],
                    'enabled': True
                }
            ]
        }
        
        return jsonify(mock_response), 200
        
    except Exception as e:
        print(f"Error in infer_form: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/save-form', methods=['POST'])
def save_form():
    """Save form to Firebase"""
    try:
        # Verify authentication
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Missing or invalid token'}), 401
        
        token = auth_header.split(' ')[1]
        user_id = verify_token(token)
        if not user_id:
            return jsonify({'error': 'Invalid token'}), 401
        
        # Get request data
        form_data = request.get_json()
        
        # Basic validation
        if not form_data.get('title', '').strip():
            return jsonify({'error': 'Title is required'}), 400
        
        enabled_questions = [q for q in form_data.get('questions', []) if q.get('enabled', True)]
        if len(enabled_questions) == 0:
            return jsonify({'error': 'At least one question must be enabled'}), 400
        
        # Generate form ID
        form_id = str(uuid.uuid4())
        
        # Save to Firestore (if available)
        if db:
            form_doc = {
                'form_id': form_id,
                'creator_id': user_id,
                'title': form_data['title'].strip(),
                'questions': form_data['questions'],
                'demographics': form_data.get('demographics', []),
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            db.collection('forms').document(form_id).set(form_doc)
        
        return jsonify({
            'form_id': form_id,
            'message': 'Form saved successfully'
        }), 200
        
    except Exception as e:
        print(f"Error in save_form: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/forms', methods=['GET'])
def get_forms():
    """Get user's forms"""
    try:
        # Verify authentication
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Missing or invalid token'}), 401
        
        token = auth_header.split(' ')[1]
        user_id = verify_token(token)
        if not user_id:
            return jsonify({'error': 'Invalid token'}), 401
        
        # Mock response for testing
        mock_forms = [
            {
                'id': 'form-1',
                'title': 'Customer Feedback Survey',
                'created_at': datetime.utcnow(),
                'response_count': 5
            }
        ]
        
        return jsonify(mock_forms), 200
        
    except Exception as e:
        print(f"Error in get_forms: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/forms/<form_id>', methods=['GET'])
def get_form_metadata(form_id):
    """Get form metadata for anonymous access"""
    try:
        # Mock response for testing
        mock_form = {
            'title': 'Customer Feedback Survey',
            'questions': [
                {
                    'text': 'What is your favorite coffee type?',
                    'type': 'multiple_choice',
                    'options': ['Espresso', 'Latte', 'Cappuccino', 'Americano', 'Other'],
                    'enabled': True
                }
            ],
            'demographics': []
        }
        
        return jsonify(mock_form), 200
        
    except Exception as e:
        print(f"Error in get_form_metadata: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/chat-message', methods=['POST'])
def chat_message():
    """Process chat message"""
    try:
        data = request.get_json()
        
        # Mock response for testing
        mock_response = {
            'response': 'Hey! Thanks for taking our survey. What\'s your favorite coffee type? ☕',
            'tag': ''
        }
        
        return jsonify(mock_response), 200
        
    except Exception as e:
        print(f"Error in chat_message: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("🚀 Starting Bermuda backend server...")
    print(f"📧 OpenAI API Key: {'✓ Set' if os.getenv('OPENAI_API_KEY') else '✗ Missing'}")
    print(f"🔥 Firebase Project ID: {os.getenv('FIREBASE_PROJECT_ID', 'Not set')}")
    print("🌐 Server will be available at: http://localhost:5000")
    print("🔄 CORS enabled for all origins")
    print("=" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5000)