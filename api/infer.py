from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
import re
import requests

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
    pass  # Silently continue if .env loading fails

app = Flask(__name__)
CORS(app)

# Optimize for Vercel cold starts
app.config['JSON_SORT_KEYS'] = False

@app.route('/api/infer', methods=['POST', 'OPTIONS'])
def infer_form():
    """Main form inference endpoint using proven requests approach"""
    # Handle CORS preflight
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        # Get request data
        data = request.get_json()
        dump = data.get('dump', '').strip()
        
        # Validate dump
        if len(dump) < 20:
            return jsonify({'error': 'Invalid dump - too short'}), 400
        
        if len(dump) > 5000:
            return jsonify({'error': 'Invalid dump - too long'}), 400
        
        # Get API key
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            return jsonify({'error': 'API key not configured'}), 500
        
        # Clean API key (remove newlines and whitespace)
        api_key = api_key.strip().replace('\n', '').replace('\r', '')
        
        # Create prompt
        prompt = f"""You are an expert form inferrer. From this dump: {dump}

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
        
        # Make direct API call to OpenAI using requests
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': 'gpt-4o-mini',
            'messages': [
                {'role': 'user', 'content': prompt}
            ],
            'temperature': 0.7,
            'max_tokens': 1000
        }
        
        # Use requests with timeout optimized for Vercel
        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers=headers,
            json=payload,
            timeout=8  # 8 second timeout
        )
        
        if response.status_code != 200:
            return jsonify({'error': f'OpenAI API error: {response.status_code} - {response.text}'}), 500
        
        # Parse OpenAI response
        openai_response = response.json()
        if 'choices' not in openai_response or not openai_response['choices']:
            return jsonify({'error': 'Invalid OpenAI response'}), 500
        
        llm_response = openai_response['choices'][0]['message']['content']
        
        # Extract JSON from response
        try:
            json_match = re.search(r'\{.*\}', llm_response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                form_data = json.loads(json_str)
            else:
                return jsonify({'error': 'Could not extract JSON from response'}), 500
        except Exception as e:
            return jsonify({'error': f'JSON parsing error: {str(e)}'}), 500
        
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
        
        return jsonify(form_data), 200
        
    except requests.exceptions.Timeout:
        return jsonify({'error': 'Request timeout - try a shorter text'}), 504
    except requests.exceptions.ConnectionError:
        return jsonify({'error': 'Connection error - please try again'}), 503
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

# For Vercel WSGI
app = app