from flask import Flask, request, jsonify
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, firestore
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import os
import json
import uuid
from datetime import datetime, timezone
import re
from typing import Dict, List, Any

app = Flask(__name__)
CORS(app)

# Initialize Firebase Admin SDK
def initialize_firebase():
    if not firebase_admin._apps:
        # For Vercel deployment, we'll use environment variables
        firebase_config = {
            "type": "service_account",
            "project_id": os.getenv('FIREBASE_PROJECT_ID'),
            "private_key_id": os.getenv('FIREBASE_PRIVATE_KEY_ID'),
            "private_key": os.getenv('FIREBASE_PRIVATE_KEY').replace('\\n', '\n'),
            "client_email": os.getenv('FIREBASE_CLIENT_EMAIL'),
            "client_id": os.getenv('FIREBASE_CLIENT_ID'),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{os.getenv('FIREBASE_CLIENT_EMAIL').replace('@', '%40')}",
            "universe_domain": "googleapis.com"
        }
        
        cred = credentials.Certificate(firebase_config)
        firebase_admin.initialize_app(cred)

# Initialize Firebase
initialize_firebase()
db = firestore.client()

# Initialize OpenAI with LangChain
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.7,
    max_tokens=1000,
    api_key=os.getenv('OPENAI_API_KEY')
)

# Form inference prompt template
form_prompt = PromptTemplate(
    input_variables=["dump"],
    template="""
You are a form creation AI. Convert the following text dump into a structured form with title and questions.

Rules:
1. Create a clear, professional title
2. Generate 3-10 relevant questions based on the content
3. Use these question types only: text, multiple_choice, yes_no, number, rating
4. For multiple_choice: provide 2-7 options
5. For rating: always use ["1", "2", "3", "4", "5"] options
6. For yes_no: always use ["Yes", "No"] options
7. All questions should be enabled: true
8. Return valid JSON only

Text dump: {dump}

Return JSON in this exact format:
{{
  "title": "Form Title",
  "questions": [
    {{
      "text": "Question text?",
      "type": "question_type",
      "options": ["option1", "option2"],
      "enabled": true
    }}
  ]
}}
"""
)

# Create LangChain chain
chain = form_prompt | llm | StrOutputParser()

def validate_form_data(form_data):
    """Validate form data structure"""
    if not form_data.get('title') or not form_data.get('title').strip():
        return False
    
    questions = form_data.get('questions', [])
    if not questions:
        return False
    
    # Check if at least one question is enabled
    enabled_questions = [q for q in questions if q.get('enabled', False)]
    if not enabled_questions:
        return False
    
    return True

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'firebase': 'connected',
        'openai': 'configured'
    }), 200

@app.route('/api/infer', methods=['POST'])
def infer_form():
    """Infer form structure from text dump"""
    try:
        data = request.get_json()
        dump = data.get('dump', '').strip()
        
        # Validate input
        if len(dump) < 20:
            return jsonify({'error': 'Invalid dump - too short'}), 400
        
        if len(dump) > 5000:
            return jsonify({'error': 'Invalid dump - too long'}), 400
        
        print(f"🚀 Processing dump: {dump[:100]}...")
        
        # Use LangChain to process the dump
        response = chain.invoke({"dump": dump})
        
        print(f"📤 LLM Response: {response}")
        
        # Parse JSON response
        try:
            form_data = json.loads(response)
        except json.JSONDecodeError:
            # Try to extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                form_data = json.loads(json_match.group())
            else:
                return jsonify({'error': 'Invalid AI response format'}), 500
        
        # Clean and validate questions
        cleaned_questions = []
        for q in form_data.get('questions', []):
            if q.get('type') in ['text', 'multiple_choice', 'yes_no', 'number', 'rating']:
                cleaned_question = {
                    'text': q.get('text', '').strip(),
                    'type': q.get('type'),
                    'enabled': q.get('enabled', True)
                }
                
                # Handle options for specific question types
                if q.get('type') in ['multiple_choice', 'yes_no', 'rating']:
                    options = q.get('options', [])
                    if q.get('type') == 'yes_no':
                        options = ['Yes', 'No']
                    elif q.get('type') == 'rating':
                        options = ['1', '2', '3', '4', '5']
                    
                    cleaned_question['options'] = options
                
                cleaned_questions.append(cleaned_question)
        
        form_data['questions'] = cleaned_questions
        
        print(f"✅ Returning form data: {form_data}")
        
        return jsonify(form_data), 200
        
    except Exception as e:
        print(f"❌ Error in infer_form: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/save-form', methods=['POST'])
def save_form():
    """Save form to Firebase"""
    try:
        # Skip auth for testing
        user_id = 'test-user-123'
        
        # Get request data
        form_data = request.get_json()
        
        # Validate form data
        if not validate_form_data(form_data):
            return jsonify({'error': 'No enabled questions'}), 400
        
        # Generate form ID
        form_id = str(uuid.uuid4())
        
        # Prepare form document
        form_doc = {
            'form_id': form_id,
            'creator_id': user_id,
            'title': form_data['title'].strip(),
            'questions': form_data['questions'],
            'demographics': form_data.get('demographics', []),
            'created_at': datetime.now(timezone.utc),
            'updated_at': datetime.now(timezone.utc)
        }
        
        # Save to Firestore
        db.collection('forms').document(form_id).set(form_doc)
        
        print(f"✅ Form saved with ID: {form_id}")
        
        return jsonify({
            'form_id': form_id,
            'message': 'Form saved'
        }), 200
        
    except Exception as e:
        import traceback
        print(f"❌ Error in save_form: {str(e)}")
        print(f"❌ Full traceback: {traceback.format_exc()}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/forms', methods=['GET'])
def get_forms():
    """Get user's forms"""
    try:
        # Skip auth for testing
        user_id = 'test-user-123'
        
        # Query forms from Firestore (simplified to avoid composite index requirement)
        forms_ref = db.collection('forms').where('creator_id', '==', user_id)
        forms = []
        
        for doc in forms_ref.stream():
            form_data = doc.to_dict()
            
            # Get response count
            responses_ref = db.collection('forms').document(doc.id).collection('responses')
            response_count = len(list(responses_ref.stream()))
            
            forms.append({
                'id': doc.id,
                'title': form_data['title'],
                'created_at': form_data['created_at'],
                'response_count': response_count
            })
        
        # Sort by created_at in Python since we can't do it in Firestore without composite index
        forms.sort(key=lambda x: x['created_at'] if x['created_at'] else datetime.min, reverse=True)
        
        return jsonify(forms), 200
        
    except Exception as e:
        print(f"❌ Error in get_forms: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/forms/<form_id>', methods=['GET'])
def get_form_metadata(form_id):
    """Get anonymous form metadata by ID"""
    try:
        # Get form document from Firestore
        form_doc = db.collection('forms').document(form_id).get()
        
        if not form_doc.exists:
            return jsonify({'error': 'Form not found'}), 404
            
        form_data = form_doc.to_dict()
        
        # Return anonymous form data (no creator info)
        return jsonify({
            'title': form_data['title'],
            'questions': form_data['questions'],
            'demographics': form_data.get('demographics', [])
        }), 200
        
    except Exception as e:
        print(f"❌ Error in get_form_metadata: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

# Vercel handler
def handler(request):
    return app(request.environ, lambda status, headers: None)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)