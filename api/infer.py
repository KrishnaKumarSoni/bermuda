from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
import re

app = Flask(__name__)
CORS(app)

# Global variables to cache imports and models
_llm = None
_inference_chain = None

def get_inference_chain():
    global _llm, _inference_chain
    
    if _inference_chain is None:
        # Import OpenAI directly for better control
        from openai import OpenAI
        
        # Initialize OpenAI client with minimal config
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
            
        client = OpenAI(
            api_key=api_key,
            timeout=30.0,  # 30 second timeout for API calls
            max_retries=2
        )
        
        # Store client globally
        _llm = client
        _inference_chain = True  # Flag that it's initialized
    
    return _llm

def extract_json_from_response(response_text):
    """Extract JSON from LLM response"""
    try:
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group()
            return json.loads(json_str)
        return None
    except Exception as e:
        return None

@app.route('/api/infer', methods=['POST', 'OPTIONS'])
def infer_form():
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
        
        # Get the OpenAI client
        try:
            openai_client = get_inference_chain()
        except Exception as e:
            return jsonify({'error': f'OpenAI setup error: {str(e)}'}), 500
        
        # Create the prompt
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
        
        # Run inference with direct OpenAI API
        try:
            response = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=1000
            )
            llm_response = response.choices[0].message.content
        except Exception as e:
            return jsonify({'error': f'OpenAI API error: {str(e)}'}), 500
        
        # Extract JSON from response
        form_data = extract_json_from_response(llm_response)
        if not form_data:
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
        
        return jsonify(form_data), 200
        
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

# For Vercel WSGI
app = app