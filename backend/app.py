from flask import Flask, request, jsonify
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, firestore, auth
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import os
import json
import uuid
from datetime import datetime
import re
from typing import Dict, List, Any
from dotenv import load_dotenv

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# Initialize Firebase
firebase_cred_path = os.path.join(os.path.dirname(__file__), '..', 'firebase-adminsdk.json')
cred = credentials.Certificate(firebase_cred_path)
firebase_admin.initialize_app(cred)
db = firestore.client()

# Initialize OpenAI with LangChain
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.7,
    max_tokens=1000,
    api_key=os.getenv('OPENAI_API_KEY')
)

# Inference Chain for form creation (exactly as specified in YAML)
inference_template = """You are an expert form inferrer. From this dump: {dump}

Output JSON: {{'title': str, 'questions': [{{'text': str, 'type': 'text'|'multiple_choice'|'yes_no'|'number'|'rating', 'options': [str] if multiple_choice/yes_no/rating (infer logical ones), 'enabled': true}}]}}

###
Chain-of-Thought:
Step 1: Summarize dump's intent.
Step 2: Derive 5-10 clear questions.
Step 3: Infer type per question (e.g., choices → multiple_choice with options; binary → yes_no; numeric → number; scale → rating; else text).
Step 4: Self-critique: Are types/options logical/non-redundant?

Few-Shot Examples:
- Dump: "Favorite color: red/blue/green?" Output: {{'title': 'Color Survey', 'questions': [{{'text': 'Favorite color?', 'type': 'multiple_choice', 'options': ['red', 'blue', 'green'], 'enabled': true}}]}}
- Dump: "How many pets? Yes or no to cats?" Output: {{'title': 'Pet Survey', 'questions': [{{'text': 'How many pets?', 'type': 'number', 'enabled': true}}, {{'text': 'Do you like cats?', 'type': 'yes_no', 'options': ['Yes', 'No'], 'enabled': true}}]}}
- Dump: "Rate service 1-5" Output: {{'questions': [{{'text': 'Rate service?', 'type': 'rating', 'options': ['1', '2', '3', '4', '5'], 'enabled': true}}]}}

Output (JSON only):"""

inference_prompt = PromptTemplate(
    input_variables=["dump"],
    template=inference_template
)

inference_chain = inference_prompt | llm | StrOutputParser()

# Helper functions
def verify_token(token):
    """Verify Firebase ID token"""
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token['uid']
    except Exception as e:
        print(f"Token verification failed: {e}")
        return None

def extract_json_from_response(response_text):
    """Extract JSON from LLM response"""
    try:
        # Try to find JSON in the response
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group()
            return json.loads(json_str)
        return None
    except Exception as e:
        print(f"JSON extraction failed: {e}")
        return None

def validate_form_data(form_data):
    """Validate form data structure"""
    if not isinstance(form_data, dict):
        return False
    
    if 'title' not in form_data or not form_data['title'].strip():
        return False
    
    if 'questions' not in form_data or not isinstance(form_data['questions'], list):
        return False
    
    enabled_questions = [q for q in form_data['questions'] if q.get('enabled', True)]
    if len(enabled_questions) == 0:
        return False
    
    for question in enabled_questions:
        if not question.get('text', '').strip():
            return False
        
        if question.get('type') in ['multiple_choice', 'yes_no', 'rating']:
            options = question.get('options', [])
            if not options or len(options) < 2:
                return False
    
    return True

# API Routes
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'firebase': 'connected',
        'openai': 'configured' if os.getenv('OPENAI_API_KEY') else 'missing'
    }), 200

@app.route('/api/infer', methods=['POST'])
def infer_form():
    """Infer form structure from text dump using actual LangChain"""
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
        
        if len(dump) > 5000:
            return jsonify({'error': 'Invalid dump - too long'}), 400
        
        print(f"Processing dump: {dump[:100]}...")
        
        # Run inference using actual LangChain
        response = inference_chain.invoke({"dump": dump})
        
        print(f"LLM Response: {response}")
        
        # Extract JSON from response
        form_data = extract_json_from_response(response)
        if not form_data:
            print("Failed to extract JSON from response")
            return jsonify({'error': 'Could not process your text. Please try again with clearer content.'}), 500
        
        # Ensure title exists
        if 'title' not in form_data or not form_data['title'].strip():
            form_data['title'] = 'Untitled Form'
        
        # Ensure questions exist
        if 'questions' not in form_data or not form_data['questions']:
            form_data['questions'] = []
        
        # Validate and clean questions
        cleaned_questions = []
        for question in form_data['questions']:
            if isinstance(question, dict) and question.get('text', '').strip():
                cleaned_question = {
                    'text': question['text'].strip(),
                    'type': question.get('type', 'text'),
                    'enabled': question.get('enabled', True)
                }
                
                # Add options for choice-based questions
                if cleaned_question['type'] in ['multiple_choice', 'yes_no', 'rating']:
                    options = question.get('options', [])
                    if cleaned_question['type'] == 'yes_no' and not options:
                        options = ['Yes', 'No']
                    elif cleaned_question['type'] == 'rating' and not options:
                        options = ['1', '2', '3', '4', '5']
                    
                    cleaned_question['options'] = options
                
                cleaned_questions.append(cleaned_question)
        
        form_data['questions'] = cleaned_questions
        
        print(f"Returning form data: {form_data}")
        
        return jsonify(form_data), 200
        
    except Exception as e:
        print(f"Error in infer_form: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/save-form', methods=['POST'])
def save_form():
    """Save form to Firebase (exactly as specified in YAML)"""
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
        
        # Validate form data
        if not validate_form_data(form_data):
            return jsonify({'error': 'No enabled questions'}), 400
        
        # Generate form ID (UUID as specified)
        form_id = str(uuid.uuid4())
        
        # Prepare form document (exactly as specified in data-models.yaml)
        form_doc = {
            'form_id': form_id,
            'creator_id': user_id,
            'title': form_data['title'].strip(),
            'questions': form_data['questions'],
            'demographics': form_data.get('demographics', []),
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        # Save to Firestore /forms collection
        db.collection('forms').document(form_id).set(form_doc)
        
        print(f"Form saved with ID: {form_id}")
        
        return jsonify({
            'form_id': form_id,
            'message': 'Form saved'
        }), 200
        
    except Exception as e:
        print(f"Error in save_form: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/forms', methods=['GET'])
def get_forms():
    """Get user's forms (exactly as specified in YAML)"""
    try:
        # Verify authentication
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Missing or invalid token'}), 401
        
        token = auth_header.split(' ')[1]
        user_id = verify_token(token)
        if not user_id:
            return jsonify({'error': 'Invalid token'}), 401
        
        # Query forms from Firestore
        forms_ref = db.collection('forms').where('creator_id', '==', user_id).order_by('created_at', direction=firestore.Query.DESCENDING)
        forms = []
        
        for doc in forms_ref.stream():
            form_data = doc.to_dict()
            
            # Get response count from subcollection
            responses_ref = db.collection('forms').document(doc.id).collection('responses')
            response_count = len(list(responses_ref.stream()))
            
            forms.append({
                'id': doc.id,
                'title': form_data['title'],
                'created_at': form_data['created_at'],
                'response_count': response_count
            })
        
        return jsonify(forms), 200
        
    except Exception as e:
        print(f"Error in get_forms: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/forms/<form_id>', methods=['GET'])
def get_form_metadata(form_id):
    """Get form metadata for anonymous access (exactly as specified in YAML)"""
    try:
        # Get form document
        form_doc = db.collection('forms').document(form_id).get()
        
        if not form_doc.exists:
            return jsonify({'error': 'Form not found'}), 404
        
        form_data = form_doc.to_dict()
        
        # Return only enabled questions and demographics
        enabled_questions = [q for q in form_data['questions'] if q.get('enabled', True)]
        enabled_demographics = [d for d in form_data.get('demographics', []) if d.get('enabled', True)]
        
        return jsonify({
            'title': form_data['title'],
            'questions': enabled_questions,
            'demographics': enabled_demographics
        }), 200
        
    except Exception as e:
        print(f"Error in get_form_metadata: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("🚀 Starting Bermuda backend server...")
    print(f"📧 OpenAI API Key: {'✓ Set' if os.getenv('OPENAI_API_KEY') else '✗ Missing'}")
    print(f"🔥 Firebase Project ID: {os.getenv('FIREBASE_PROJECT_ID', 'Not set')}")
    print("🌐 Server will be available at: http://localhost:5000")
    print("=" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5000)