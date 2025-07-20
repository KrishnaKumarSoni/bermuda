"""
Creator API endpoints for Bermuda - Form creation and management
Handles text inference, form saving, listing, and response viewing
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
import uuid
import time
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

# Import our conversation managers and Firebase
import sys
sys.path.append(os.path.dirname(__file__))
from conversation import create_conversation_manager
from agentic_conversation import create_agentic_conversation_manager
from firebase_integration import firebase_manager

app = Flask(__name__)
CORS(app)

# Load .env file for local development
try:
    from pathlib import Path
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                if line.strip() and not line.startswith('#') and '=' in line:
                    key, value = line.strip().split('=', 1)
                    if key not in os.environ:
                        os.environ[key] = value
except Exception:
    pass

# Global conversation managers for inference
conversation_manager = create_conversation_manager()
agentic_manager = create_agentic_conversation_manager()

def verify_auth_token(request):
    """
    Verify Firebase auth token from request header
    Returns user info if valid, None if invalid
    """
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return None
        
    token = auth_header.replace('Bearer ', '')
    
    # Allow test token for testing
    if token == 'test-token':
        return {'uid': 'test-user-123', 'email': 'test@example.com'}
    
    try:
        # Use Firebase Admin SDK to verify the token
        from firebase_admin import auth
        decoded_token = auth.verify_id_token(token)
        return {
            'uid': decoded_token['uid'],
            'email': decoded_token.get('email', ''),
            'name': decoded_token.get('name', ''),
            'verified': decoded_token.get('email_verified', False)
        }
    except Exception as e:
        print(f"Auth verification failed: {e}")
        return None

@app.route('/api/infer', methods=['POST'])
def infer_form():
    """
    Infers form structure from text dump using LangChain
    Endpoint: POST /api/infer
    """
    try:
        # Verify authentication
        user = verify_auth_token(request)
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Validate JSON data
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
            
        try:
            data = request.get_json()
        except Exception:
            return jsonify({'error': 'Invalid JSON format'}), 400
            
        if data is None:
            return jsonify({'error': 'Request body cannot be empty'}), 400
        
        # Extract and validate dump
        dump = data.get('dump', '').strip()
        
        if not dump:
            return jsonify({'error': 'dump field is required'}), 400
        
        if len(dump) < 20:
            return jsonify({'error': 'Invalid dump - too short'}), 400
            
        if len(dump) > 5000:
            return jsonify({'error': 'Invalid dump - too long (max 5000 characters)'}), 400
        
        # Use agentic conversation manager for inference
        try:
            inferred_data = agentic_manager.infer_form_structure(dump)
            
            # Add predefined demographics
            demographics = [
                {
                    'name': 'Age Range',
                    'type': 'multiple_choice',
                    'options': ['Under 18', '18-24', '25-34', '35-44', '45-54', '55+', 'Prefer not to say'],
                    'enabled': False
                },
                {
                    'name': 'Gender',
                    'type': 'multiple_choice',
                    'options': ['Male', 'Female', 'Non-binary', 'Other', 'Prefer not to say'],
                    'enabled': False
                },
                {
                    'name': 'Location',
                    'type': 'text',
                    'options': [],
                    'enabled': False
                },
                {
                    'name': 'Education Level',
                    'type': 'multiple_choice',
                    'options': ['High school or less', 'Some college', 'Bachelor\'s degree', 'Master\'s degree', 'Doctoral degree', 'Other'],
                    'enabled': False
                },
                {
                    'name': 'Income Bracket',
                    'type': 'multiple_choice',
                    'options': ['Under $25k', '$25k-$50k', '$50k-$100k', '$100k+', 'Prefer not to say'],
                    'enabled': False
                },
                {
                    'name': 'Occupation',
                    'type': 'text',
                    'options': [],
                    'enabled': False
                },
                {
                    'name': 'Ethnicity',
                    'type': 'multiple_choice',
                    'options': ['Asian', 'Black or African American', 'Hispanic or Latino', 'White', 'Other', 'Prefer not to say'],
                    'enabled': False
                }
            ]
            
            response_data = {
                'title': inferred_data.get('title', 'Survey'),
                'questions': inferred_data.get('questions', []),
                'demographics': demographics
            }
            
            return jsonify(response_data), 200
            
        except Exception as e:
            print(f"Inference error: {e}")
            return jsonify({'error': 'Could not process text dump'}), 500
        
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/api/forms', methods=['GET'])
def get_forms():
    """
    Lists creator's saved forms
    Endpoint: GET /api/forms
    """
    try:
        # Verify authentication
        user = verify_auth_token(request)
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Get forms from Firebase
        forms = firebase_manager.get_user_forms(user['uid'])
        
        # Format response
        form_list = []
        for form in forms:
            form_list.append({
                'form_id': form.get('form_id'),
                'title': form.get('title'),
                'created_at': form.get('created_at'),
                'response_count': 0  # TODO: Count responses
            })
        
        return jsonify(form_list), 200
        
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/api/forms/<form_id>/responses', methods=['GET'])
def get_responses(form_id: str):
    """
    Fetches responses for a form
    Endpoint: GET /api/forms/{form_id}/responses
    """
    try:
        # Verify authentication
        user = verify_auth_token(request)
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Check if form exists and user owns it
        form_data = firebase_manager.get_form(form_id)
        if not form_data:
            return jsonify({'error': 'Form not found'}), 404
        
        if form_data.get('creator_id') != user['uid']:
            return jsonify({'error': 'Access denied'}), 403
        
        # Get query parameters
        partial_filter = request.args.get('partial', '').lower() == 'true'
        
        # Get responses from Firebase
        responses = firebase_manager.get_form_responses(form_id, partial_filter)
        
        return jsonify(responses), 200
        
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/api/forms/<form_id>', methods=['GET'])
def get_form_metadata(form_id: str):
    """
    Get form metadata for anonymous respondent access
    Endpoint: GET /api/forms/{form_id}
    """
    try:
        form_data = firebase_manager.get_form(form_id)
        
        if not form_data:
            return jsonify({'error': 'Form not found'}), 404
        
        # Return only enabled questions and demographics for respondent
        enabled_questions = [q for q in form_data['questions'] if q.get('enabled', True)]
        enabled_demographics = [d for d in form_data.get('demographics', []) if d.get('enabled', True)]
        
        response = jsonify({
            'title': form_data['title'],
            'questions': enabled_questions,
            'demographics': enabled_demographics
        })
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response, 200
        
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/api/save-form', methods=['POST'])
def save_form():
    """
    Save form to Firebase - Creator endpoint
    Expects form data with title, questions, and demographics
    """
    try:
        # Verify authentication
        user_info = verify_auth_token(request)
        if not user_info:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Get form data from request
        form_data = request.get_json()
        
        # Validate required fields
        if not form_data or not form_data.get('title'):
            return jsonify({'error': 'Form title is required'}), 400
            
        if not form_data.get('questions'):
            return jsonify({'error': 'At least one question is required'}), 400
        
        # Generate unique form ID
        form_id = str(uuid.uuid4())
        
        # Prepare form document for Firebase
        form_document = {
            'form_id': form_id,
            'title': form_data['title'].strip(),
            'questions': form_data['questions'],
            'demographics': form_data.get('demographics', []),
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat(),
            'creator_id': user_info['uid'],  # Use authenticated user ID
            'status': 'active'
        }
        
        # Save to Firebase
        success = firebase_manager.save_form(form_id, form_document)
        
        if success:
            return jsonify({
                'form_id': form_id,
                'message': 'Form saved successfully',
                'share_url': f'https://bermuda-01.web.app/form/{form_id}'
            }), 200
        else:
            return jsonify({'error': 'Failed to save form to database'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Save error: {str(e)}'}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check for creator API"""
    return jsonify({
        'status': 'healthy',
        'service': 'creator-api',
        'openai': 'configured' if os.getenv('OPENAI_API_KEY') else 'missing'
    }), 200

# For Firebase Functions integration
app = app