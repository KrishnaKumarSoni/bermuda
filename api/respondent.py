"""
Complete respondent chat API implementing all YAML specifications:
- Anonymous form access
- Live chat with conversation memory
- Data extraction and Firebase storage
- Device fingerprinting and security
- Real-time chat sync
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
import uuid
import time
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
import hashlib
import requests

# Import our conversation managers and Firebase
import sys
sys.path.append(os.path.dirname(__file__))
from conversation import create_conversation_manager
from agentic_conversation import create_agentic_conversation_manager
from langchain_manager import get_langchain_manager
from firebase_integration import firebase_manager

app = Flask(__name__)
CORS(app)

# Global conversation managers
conversation_manager = create_conversation_manager()
agentic_manager = create_agentic_conversation_manager()
langchain_manager = get_langchain_manager()

# In-memory storage for sessions (use Firebase Realtime DB in production)
active_sessions: Dict[str, Dict] = {}
conversation_history: Dict[str, List[Dict]] = {}

# Track off-topic messages per session
off_topic_counters: Dict[str, int] = {}

def get_firebase_mock():
    """
    Mock Firebase integration - replace with actual Firebase in production
    For now, stores in memory for testing
    """
    return {
        'forms': {},
        'responses': {},
        'chats': {}
    }

firebase_mock = get_firebase_mock()

def generate_device_id(request_data: Dict) -> str:
    """
    Generate device fingerprint hash from browser characteristics
    Enhanced with additional fingerprinting data
    """
    user_agent = request.headers.get('User-Agent', '')
    accept_language = request.headers.get('Accept-Language', '')
    accept_encoding = request.headers.get('Accept-Encoding', '')
    
    # Get IP address from various headers
    ip_address = (
        request.headers.get('X-Forwarded-For', '').split(',')[0].strip() or
        request.headers.get('X-Real-IP', '') or
        request.environ.get('REMOTE_ADDR', '')
    )
    
    # Collect browser fingerprint data from request_data if available
    screen_resolution = request_data.get('screen_resolution', '')
    timezone_offset = request_data.get('timezone_offset', '')
    platform = request_data.get('platform', '')
    canvas_fingerprint = request_data.get('canvas_fingerprint', '')
    webgl_renderer = request_data.get('webgl_renderer', '')
    
    # Create comprehensive fingerprint
    fingerprint_data = f"{user_agent}:{ip_address}:{accept_language}:{accept_encoding}:{screen_resolution}:{timezone_offset}:{platform}:{canvas_fingerprint}:{webgl_renderer}"
    device_hash = hashlib.sha256(fingerprint_data.encode()).hexdigest()[:16]
    
    return f"device_{device_hash}"

def get_location_from_request() -> Dict[str, str]:
    """
    Get coarse location from request IP address
    Uses ipapi.co service for geolocation
    """
    try:
        # Get IP address from headers
        ip_address = (
            request.headers.get('X-Forwarded-For', '').split(',')[0].strip() or
            request.headers.get('X-Real-IP', '') or
            request.environ.get('REMOTE_ADDR', '')
        )
        
        # Skip localhost/private IPs
        if not ip_address or ip_address.startswith(('127.', '192.168.', '10.', '172.')):
            return {"country": "Unknown", "city": "Unknown", "ip": "private"}
        
        # Try to get location from IP
        import requests as req
        response = req.get(f"http://ipapi.co/{ip_address}/json/", timeout=2)
        
        if response.status_code == 200:
            data = response.json()
            return {
                "country": data.get("country_name", "Unknown"),
                "city": data.get("city", "Unknown"),
                "region": data.get("region", "Unknown"),
                "postal": data.get("postal", "Unknown"),
                "timezone": data.get("timezone", "Unknown"),
                "ip": ip_address
            }
    except Exception as e:
        print(f"Location lookup failed: {e}")
    
    # Fallback to unknown location
    return {
        "country": "Unknown",
        "city": "Unknown",
        "ip": "unknown"
    }

def validate_form_exists(form_id: str) -> Optional[Dict]:
    """
    Validate form exists and return form data from Firebase
    """
    return firebase_manager.get_form(form_id)

def save_to_firebase(collection: str, document_id: str, data: Dict):
    """
    Save data to Firebase - mock implementation
    In production, use Firebase Admin SDK
    """
    if collection not in firebase_mock:
        firebase_mock[collection] = {}
    firebase_mock[collection][document_id] = data

def save_response_to_firebase(form_id: str, session_id: str, response_data: Dict):
    """
    Save response to Firebase responses subcollection
    """
    response_doc = {
        'session_id': session_id,
        'data': response_data.get('questions', {}),
        'demographics': response_data.get('demographics', {}),
        'transcript': conversation_history.get(session_id, []),
        'partial': response_data.get('completion_status') != 'complete',
        'status': response_data.get('completion_status', 'partial'),
        'device_id': active_sessions.get(session_id, {}).get('device_id'),
        'location': active_sessions.get(session_id, {}).get('location'),
        'notes': response_data.get('extraction_notes', [])
    }
    
    # Save to Firebase Firestore
    firebase_manager.save_response(form_id, session_id, response_doc)
    
    # Also save to mock for backward compatibility
    if 'responses' not in firebase_mock:
        firebase_mock['responses'] = {}
    if form_id not in firebase_mock['responses']:
        firebase_mock['responses'][form_id] = {}
    firebase_mock['responses'][form_id][session_id] = response_doc

@app.route('/api/forms/<form_id>', methods=['GET'])
def get_form_metadata(form_id: str):
    """
    Get form metadata for anonymous respondent access
    Endpoint: GET /api/forms/{form_id}
    """
    try:
        form_data = validate_form_exists(form_id)
        
        if not form_data:
            return jsonify({'error': 'Form not found'}), 404
        
        # Return only enabled questions and demographics for respondent
        enabled_questions = [q for q in form_data['questions'] if q.get('enabled', True)]
        enabled_demographics = [d for d in form_data.get('demographics', []) if d.get('enabled', True)]
        
        return jsonify({
            'title': form_data['title'],
            'questions': enabled_questions,
            'demographics': enabled_demographics
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/api/chat-message', methods=['POST', 'OPTIONS'])
def chat_message():
    """
    Process user message and generate bot response
    Endpoint: POST /api/chat-message
    """
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        # Validate JSON data
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
        
        # Check payload size (max 10MB)
        if request.content_length and request.content_length > 10 * 1024 * 1024:
            return jsonify({'error': 'Payload too large (max 10MB)'}), 413
            
        try:
            data = request.get_json()
        except Exception:
            return jsonify({'error': 'Invalid JSON format'}), 400
            
        if data is None:
            return jsonify({'error': 'Request body cannot be empty'}), 400
        
        # Extract required fields
        session_id = data.get('session_id')
        form_id = data.get('form_id')
        user_message = data.get('message', '').strip()
        
        # Validate required fields
        if not all([session_id, form_id, user_message]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        if len(user_message) > 1000:
            return jsonify({'error': 'Message too long (max 1000 characters)'}), 400
        
        # Validate form exists
        form_data = validate_form_exists(form_id)
        if not form_data:
            return jsonify({'error': 'Form not found'}), 404
        
        # Initialize session if new
        if session_id not in active_sessions:
            # Extract device data from request
            device_data = data.get('device_data', {})
            
            active_sessions[session_id] = {
                'form_id': form_id,
                'device_id': data.get('device_id') or generate_device_id(device_data),
                'location': data.get('location') or get_location_from_request(),
                'device_fingerprint': device_data,  # Store full fingerprint data
                'started_at': time.time(),
                'message_count': 0
            }
            conversation_history[session_id] = []
            off_topic_counters[session_id] = 0
        
        session = active_sessions[session_id]
        history = conversation_history[session_id]
        
        # Check for off-topic message
        form_title = form_data.get('title', 'survey')
        is_off_topic = conversation_manager.handle_off_topic_message(user_message, form_title)
        
        if is_off_topic:
            off_topic_counters[session_id] += 1
            if off_topic_counters[session_id] >= 3:
                # Force completion after 3 off-topic messages
                bot_response = "bananas... I think we're done here! Thanks for your time. 😊"
                is_completed = True
            else:
                bot_response = "bananas... anyway, let's get back to the survey?"
                is_completed = False
        else:
            # Reset off-topic counter on valid message
            off_topic_counters[session_id] = 0
            
            # Get bot response using LangChain manager (with fallback to agentic)
            try:
                # Prepare questions JSON for LangChain
                questions = form_data.get('questions', [])
                enabled_questions = [q for q in questions if q.get('enabled', True)]
                questions_json = json.dumps(enabled_questions)
                
                bot_response, is_completed = langchain_manager.get_bot_response(
                    user_message=user_message,
                    session_id=session_id,
                    form_title=form_data.get('title', 'Survey'),
                    questions_json=questions_json
                )
                
                # Fallback to agentic manager if LangChain fails
                if not bot_response or bot_response.startswith("thanks for sharing"):
                    bot_response, is_completed = agentic_manager.get_bot_response(
                        user_message=user_message,
                        conversation_history=history,
                        form_data=form_data,
                        demographics=form_data.get('demographics', []),
                        session_id=session_id
                    )
            except Exception as e:
                print(f"LangChain conversation error: {e}")
                # Fallback to agentic manager
                bot_response, is_completed = agentic_manager.get_bot_response(
                    user_message=user_message,
                    conversation_history=history,
                    form_data=form_data,
                    demographics=form_data.get('demographics', []),
                    session_id=session_id
                )
        
        # Add messages to conversation history
        timestamp = datetime.now(timezone.utc).isoformat()
        
        user_msg = {
            'role': 'user',
            'text': user_message,
            'timestamp': timestamp
        }
        
        bot_msg = {
            'role': 'assistant',
            'text': bot_response,
            'timestamp': timestamp
        }
        
        history.append(user_msg)
        history.append(bot_msg)
        
        # Save to Firebase Realtime DB for live sync
        firebase_manager.save_chat_message(session_id, form_id, 'user', user_message)
        firebase_manager.save_chat_message(session_id, form_id, 'assistant', bot_response)
        
        # Update message count
        session['message_count'] += 2
        
        # Check for periodic extraction (every 5 total messages)
        should_extract = (session['message_count'] % 5 == 0) or is_completed
        
        if should_extract:
            try:
                # Extract structured data using LangChain manager (with fallback)
                try:
                    # Prepare questions JSON for LangChain
                    questions = form_data.get('questions', [])
                    enabled_questions = [q for q in questions if q.get('enabled', True)]
                    questions_json = json.dumps(enabled_questions)
                    
                    extracted_data = langchain_manager.extract_structured_data(
                        transcript=history,
                        questions_json=questions_json
                    )
                    
                    # Fallback to agentic manager if LangChain extraction is poor
                    if not extracted_data.get('questions') or extracted_data.get('partial', True):
                        fallback_data = agentic_manager.extract_structured_data(
                            transcript=history,
                            form_data=form_data,
                            demographics=form_data.get('demographics', [])
                        )
                        # Use fallback if it has more data
                        if len(fallback_data.get('questions', {})) > len(extracted_data.get('questions', {})):
                            extracted_data = fallback_data
                            
                except Exception as e:
                    print(f"LangChain extraction error: {e}")
                    # Fallback to agentic manager
                    extracted_data = agentic_manager.extract_structured_data(
                        transcript=history,
                        form_data=form_data,
                        demographics=form_data.get('demographics', [])
                    )
                
                # Save to Firebase
                save_response_to_firebase(form_id, session_id, extracted_data)
                
            except Exception as e:
                print(f"Extraction error: {e}")
                # Continue without failing the chat
        
        # Check for completion or force completion conditions
        if is_completed or session['message_count'] > 60:  # Force end after 30 exchanges
            # Mark session as inactive
            if session_id in active_sessions:
                active_sessions[session_id]['completed_at'] = time.time()
            
            # End chat session in Firebase
            firebase_manager.end_chat_session(session_id)
        
        # Prepare response
        response_data = {
            'response': bot_response,
            'tag': '[END]' if is_completed else None
        }
        
        return jsonify(response_data), 200
        
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/api/extract', methods=['POST'])
def extract_data():
    """
    Extract structured data from transcript (internal/triggered)
    Endpoint: POST /api/extract
    """
    try:
        # Validate JSON data
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
        
        # Check payload size (max 10MB)
        if request.content_length and request.content_length > 10 * 1024 * 1024:
            return jsonify({'error': 'Payload too large (max 10MB)'}), 413
            
        try:
            data = request.get_json()
        except Exception:
            return jsonify({'error': 'Invalid JSON format'}), 400
            
        if data is None:
            return jsonify({'error': 'Request body cannot be empty'}), 400
        
        session_id = data.get('session_id')
        transcript = data.get('transcript', [])
        questions_json = data.get('questions_json', {})
        
        if not session_id or not transcript:
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Validate questions_json format
        if not isinstance(questions_json, dict):
            return jsonify({'error': 'questions_json must be a valid object'}), 400
        
        # Mock form data for extraction
        form_data = {
            'questions': questions_json.get('questions', []),
            'demographics': questions_json.get('demographics', [])
        }
        
        # Extract structured data using LangChain manager (with fallback)
        try:
            # Prepare questions JSON for LangChain
            questions = questions_json.get('questions', [])
            questions_json_str = json.dumps(questions)
            
            extracted_data = langchain_manager.extract_structured_data(
                transcript=transcript,
                questions_json=questions_json_str
            )
            
            # Fallback to agentic manager if LangChain extraction is poor
            if not extracted_data.get('questions') or extracted_data.get('partial', True):
                fallback_data = agentic_manager.extract_structured_data(
                    transcript=transcript,
                    form_data=form_data,
                    demographics=form_data.get('demographics', [])
                )
                # Use fallback if it has more data
                if len(fallback_data.get('questions', {})) > len(extracted_data.get('questions', {})):
                    extracted_data = fallback_data
                    
        except Exception as e:
            print(f"LangChain extraction error: {e}")
            # Fallback to agentic manager
            extracted_data = agentic_manager.extract_structured_data(
                transcript=transcript,
                form_data=form_data,
                demographics=form_data.get('demographics', [])
            )
        
        return jsonify(extracted_data), 200
        
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/api/debug/sessions', methods=['GET'])
def debug_sessions():
    """
    Debug endpoint to view active sessions (remove in production)
    """
    return jsonify({
        'active_sessions': active_sessions,
        'conversation_history': conversation_history,
        'firebase_mock': firebase_mock
    }), 200

@app.route('/api/debug/test-chat', methods=['POST'])
def debug_test_chat():
    """
    Debug endpoint for testing chat flow
    """
    try:
        # Validate JSON data
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
        
        # Check payload size (max 10MB)
        if request.content_length and request.content_length > 10 * 1024 * 1024:
            return jsonify({'error': 'Payload too large (max 10MB)'}), 413
            
        try:
            data = request.get_json()
        except Exception:
            return jsonify({'error': 'Invalid JSON format'}), 400
            
        if data is None:
            return jsonify({'error': 'Request body cannot be empty'}), 400
        
        # Generate unique session ID unless specifically provided
        # This ensures session isolation while allowing conversation flow when needed
        session_id = data.get('session_id', f'debug-{str(uuid.uuid4())[:8]}')
        form_id = 'test-form-123'
        
        # Simulate chat message
        test_message = data.get('message', 'Hello, I want to start the survey')
        
        # Call chat message endpoint internally
        test_data = {
            'session_id': session_id,
            'form_id': form_id,
            'message': test_message
        }
        
        # Get form data
        form_data = validate_form_exists(form_id)
        
        if not form_data:
            return jsonify({'error': 'Test form not found'}), 404
        
        # Initialize session
        active_sessions[session_id] = {
            'form_id': form_id,
            'device_id': f'test_device_{uuid.uuid4().hex[:8]}',
            'location': {'country': 'Test', 'city': 'Test'},
            'started_at': time.time(),
            'message_count': 0
        }
        conversation_history[session_id] = []
        off_topic_counters[session_id] = 0
        
        # Get bot response using agentic manager
        bot_response, is_completed = agentic_manager.get_bot_response(
            user_message=test_message,
            conversation_history=[],
            form_data=form_data,
            demographics=form_data.get('demographics', []),
            session_id=session_id
        )
        
        return jsonify({
            'session_id': session_id,
            'user_message': test_message,
            'bot_response': bot_response,
            'is_completed': is_completed,
            'form_data': form_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Test error: {str(e)}'}), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check for respondent API"""
    return jsonify({
        'status': 'healthy',
        'service': 'respondent-chat-api',
        'openai': 'configured' if os.getenv('OPENAI_API_KEY') else 'missing',
        'active_sessions': len(active_sessions)
    }), 200

# For Vercel WSGI
app = app