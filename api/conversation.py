"""
LangChain-style conversation system for Bermuda respondent chatbot.
Implements natural, human-like chat with memory and data collection using OpenAI directly.
Following all YAML specifications without requiring full LangChain package.
"""

import os
import json
import re
import uuid
import requests
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple

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

class ConversationMemory:
    """Mimics LangChain ConversationBufferWindowMemory"""
    
    def __init__(self, k=10):
        self.k = k  # Keep last k messages
        self.messages = []
    
    def add_user_message(self, message: str):
        self.messages.append({"role": "user", "content": message})
        self._trim_messages()
    
    def add_ai_message(self, message: str):
        self.messages.append({"role": "assistant", "content": message})
        self._trim_messages()
    
    def _trim_messages(self):
        if len(self.messages) > self.k:
            self.messages = self.messages[-self.k:]
    
    def get_messages(self):
        return self.messages.copy()

class ConversationManager:
    """
    Manages the full conversation lifecycle using LangChain-style patterns
    Following YAML specifications for natural, human-like conversations
    """
    
    def __init__(self):
        self.api_key = self._get_clean_api_key()
        self.conversations = {}  # session_id -> ConversationMemory
        
    def _get_clean_api_key(self) -> Optional[str]:
        """Get and clean OpenAI API key"""
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            print("Warning: OPENAI_API_KEY not configured - using mock responses")
            return None
        return api_key.strip().replace('\n', '').replace('\r', '')
    
    def _create_conversation_system_prompt(self, form_data: Dict, demographics: List[Dict] = None, conversation_history: List[Dict] = None) -> str:
        """Create system prompt following YAML specifications"""
        
        form_title = form_data.get('title', 'Survey')
        questions = form_data.get('questions', [])
        enabled_questions = [q for q in questions if q.get('enabled', True)]
        
        demographics_list = []
        if demographics:
            enabled_demographics = [d for d in demographics if d.get('enabled', True)]
            demographics_list = [d['name'] for d in enabled_demographics]
        
        # Analyze conversation history to track progress
        conversation_text = ""
        if conversation_history:
            conversation_text = " ".join([msg.get('text', '') for msg in conversation_history])
        
        question_list = []
        for i, q in enumerate(enabled_questions, 1):
            q_type = q.get('type', 'text')
            q_text = q.get('text', '')
            
            # Simple heuristic to check if question seems answered
            answered_indicator = ""
            if conversation_history and len(conversation_history) > 2:
                question_keywords = q_text.lower().split()[:3]  # First 3 words
                if any(keyword in conversation_text.lower() for keyword in question_keywords):
                    answered_indicator = " [LIKELY ANSWERED]"
            
            question_list.append(f"{i}. {q_text} (type: {q_type}){answered_indicator}")
        
        system_prompt = f"""You're a super chill, casual person having a quick chat about "{form_title}". 

PERSONALITY: Text like a Gen Z friend - short, casual, authentic. Use "ur", "tbh", "ngl", lowercase, minimal punctuation.

MESSAGE STYLE:
- Keep responses SHORT (1-2 sentences max)
- Use casual texting language 
- Drop formal words, be conversational
- Add personality with casual reactions
- Ask ONE question at a time, naturally

QUESTIONS TO ASK:
{chr(10).join(question_list)}

DEMOGRAPHICS (if needed):
{', '.join(demographics_list) if demographics_list else 'None'}

CONVERSATION EXAMPLES:
- Start: "hey! quick chat about {form_title.lower()}? first up - [question]"
- Acknowledge: "nice! anything else on that?" OR "got it! go on..." OR move to next if feels complete
- Incomplete response: "mmhm, tell me more" OR "go on..." OR "anything else?"
- Complete response: "cool! so [next question]?"
- Multiple answers: "got it! what about [next thing]?"
- Corrections: "ah gotcha, thanks"
- Skip: "no worries! [next question]?"
- End: "awesome, thanks! [END]"

HANDLING PARTIAL RESPONSES:
- If response seems incomplete/short, use: "go on...", "anything else?", "tell me more"
- If response ends mid-thought or with "but", "also", "and", etc. - wait for more
- Only move to next question when response feels complete
- Be patient, don't rush

INCOMPLETE RESPONSE SIGNALS:
- Very short answers (1-3 words) 
- Ends with "but", "also", "and", "though", "however"
- Seems rushed or incomplete
- No clear conclusion to their thought

COMPLETE RESPONSE SIGNALS:
- Full sentences with clear opinion
- Multiple details given
- Natural conclusion 
- Feels like they're done talking about it

RULES:
- NO long responses or formal language
- DON'T repeat what they said back in detail  
- BE PATIENT - don't rush to next question if they might have more to say
- USE lowercase, casual words, be authentic
- NEVER list multiple choice options
- ADD [END] when done

Be like texting a friend who lets you finish your thoughts."""
        
        return system_prompt
    
    def get_bot_response(self, user_message: str, conversation_history: List[Dict], 
                        form_data: Dict, demographics: List[Dict] = None, session_id: str = None) -> Tuple[str, bool]:
        """
        Generate bot response using OpenAI with conversation memory
        Returns (response, is_completed)
        """
        
        if not self.api_key:
            # Mock response for testing
            if self.handle_off_topic_message(user_message):
                return "bananas... anyway, back to the survey?", False
            return "Thanks for sharing! What else would you like to tell me?", False
        
        # Check for off-topic message first
        form_title = form_data.get('title', 'survey')
        if self.handle_off_topic_message(user_message, form_title):
            return "bananas... anyway, back to the survey?", False
        
        try:
            # Create or get conversation memory for this session
            if session_id not in self.conversations:
                self.conversations[session_id] = ConversationMemory(k=10)
            
            memory = self.conversations[session_id]
            
            # Add conversation history to memory
            for msg in conversation_history[-10:]:  # Last 10 messages
                if msg['role'] == 'user':
                    memory.add_user_message(msg['text'])
                elif msg['role'] == 'assistant':
                    memory.add_ai_message(msg['text'])
            
            # Add current user message
            memory.add_user_message(user_message)
            
            # Create system prompt with progress tracking
            system_prompt = self._create_conversation_system_prompt(form_data, demographics, conversation_history)
            
            # Prepare messages for OpenAI
            messages = [{"role": "system", "content": system_prompt}]
            messages.extend(memory.get_messages())
            
            # Call OpenAI API
            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers={
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': 'gpt-4o-mini',
                    'messages': messages,
                    'temperature': 0.7,
                    'max_tokens': 200
                },
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                bot_response = result['choices'][0]['message']['content'].strip()
                
                # Add bot response to memory
                memory.add_ai_message(bot_response)
                
                # Check if conversation is complete
                is_completed = '[END]' in bot_response
                if is_completed:
                    bot_response = bot_response.replace('[END]', '').strip()
                
                return bot_response, is_completed
            else:
                raise Exception(f"OpenAI API error: {response.status_code}")
                
        except Exception as e:
            print(f"Conversation error: {e}")
            return "Sorry, I'm having trouble understanding. Could you rephrase that?", False
    
    def infer_form_structure(self, text_dump: str) -> Dict[str, Any]:
        """
        Infer form structure from text dump using OpenAI
        Returns dict with title, questions array
        """
        
        if not self.api_key:
            # Mock response for testing
            return {
                "title": "Survey",
                "questions": [
                    {
                        "text": "What is your opinion?",
                        "type": "text",
                        "enabled": True
                    }
                ]
            }
        
        inference_prompt = f"""You are an expert form designer. Given the text dump below, infer a conversational form structure.

Extract:
1. A clear, engaging form title (max 200 chars)
2. 3-8 questions that capture the key information
3. Use these question types only: text, multiple_choice, yes_no, number, rating

Question type guidelines:
- text: Open-ended responses
- multiple_choice: When there are clear categorical options (provide 2-8 options)
- yes_no: Binary questions (provide options: ["Yes", "No"])
- number: Numeric responses
- rating: 1-5 scale questions (provide options: ["1", "2", "3", "4", "5"])

Return ONLY a JSON object with this exact structure:
{{
    "title": "Form Title Here",
    "questions": [
        {{
            "text": "Question text here?",
            "type": "text|multiple_choice|yes_no|number|rating",
            "options": ["option1", "option2"],
            "enabled": true
        }}
    ]
}}

Text dump:
{text_dump}

JSON:"""

        try:
            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers={
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': 'gpt-4o-mini',
                    'messages': [
                        {
                            'role': 'system',
                            'content': 'You are a helpful form design assistant. Always return valid JSON only.'
                        },
                        {
                            'role': 'user',
                            'content': inference_prompt
                        }
                    ],
                    'temperature': 0.3,
                    'max_tokens': 1000
                },
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content'].strip()
                
                # Clean and parse JSON
                if content.startswith('```json'):
                    content = content.replace('```json', '').replace('```', '').strip()
                
                try:
                    inferred_data = json.loads(content)
                    
                    # Validate and clean structure
                    if 'questions' in inferred_data:
                        for q in inferred_data['questions']:
                            if 'enabled' not in q:
                                q['enabled'] = True
                    
                    return inferred_data
                    
                except json.JSONDecodeError:
                    # Fallback response
                    return {
                        "title": "Survey from Text",
                        "questions": [
                            {
                                "text": "Please share your thoughts on the topic mentioned",
                                "type": "text",
                                "enabled": True
                            }
                        ]
                    }
            else:
                raise Exception(f"OpenAI API error: {response.status_code}")
                
        except Exception as e:
            print(f"Form inference error: {e}")
            # Return fallback structure
            return {
                "title": "Survey",
                "questions": [
                    {
                        "text": "What are your thoughts on this topic?",
                        "type": "text",
                        "enabled": True
                    }
                ]
            }
    
    def extract_structured_data(self, transcript: List[Dict], form_data: Dict, 
                               demographics: List[Dict] = None) -> Dict[str, Any]:
        """
        Extract structured data from conversation transcript using OpenAI
        Returns extracted data with completion status
        """
        
        if not self.api_key:
            # Mock extraction for testing
            return {
                "questions": {},
                "demographics": {},
                "completion_status": "partial",
                "extraction_notes": ["Mock extraction - OpenAI not available"]
            }
        
        try:
            # Format transcript for extraction
            transcript_text = ""
            for msg in transcript:
                role = "User" if msg['role'] == 'user' else "Bot"
                transcript_text += f"{role}: {msg['text']}\n"
            
            # Format questions
            questions_text = ""
            for q in form_data.get('questions', []):
                if q.get('enabled', True):
                    q_type = q.get('type', 'text')
                    q_text = q.get('text', '')
                    options = q.get('options', [])
                    if options:
                        questions_text += f"- {q_text} (type: {q_type}, options: {', '.join(options)})\n"
                    else:
                        questions_text += f"- {q_text} (type: {q_type})\n"
            
            # Format demographics
            demographics_text = ""
            if demographics:
                for d in demographics:
                    if d.get('enabled', True):
                        d_name = d.get('name', '')
                        d_type = d.get('type', 'text')
                        demographics_text += f"- {d_name} (type: {d_type})\n"
            
            extraction_template = f"""You are a data extraction expert. Extract structured data from this chat transcript.

Form Questions:
{questions_text}

Demographics:
{demographics_text}

Chat Transcript:
{transcript_text}

Extract responses and map them to the questions. Use these rules:
- text: Extract verbatim user response
- multiple_choice: Match to closest option or "other"
- yes_no: Map to Yes/No/Unsure
- number: Parse natural language to numbers
- rating: Map sentiment to 1-5 scale
- For conflicts, use the latest response
- Mark completion status based on coverage

Return ONLY this JSON structure:
{{
    "questions": {{"question_text": "extracted_answer"}},
    "demographics": {{"demo_name": "extracted_answer"}},
    "completion_status": "complete|partial",
    "extraction_notes": ["note1", "note2"]
}}

JSON:"""
            
            # Use OpenAI for extraction
            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers={
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': 'gpt-4o-mini',
                    'messages': [
                        {
                            'role': 'system',
                            'content': 'You are a data extraction expert. Always return valid JSON only.'
                        },
                        {
                            'role': 'user',
                            'content': extraction_template
                        }
                    ],
                    'temperature': 0.3,
                    'max_tokens': 800
                },
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content'].strip()
                
                # Clean and parse JSON
                if content.startswith('```json'):
                    content = content.replace('```json', '').replace('```', '').strip()
                
                try:
                    extracted_data = json.loads(content)
                    return extracted_data
                    
                except json.JSONDecodeError as e:
                    # Fallback: return partial structure
                    return {
                        "questions": {},
                        "demographics": {},
                        "completion_status": "partial",
                        "extraction_notes": [f"JSON parsing error: {str(e)}"]
                    }
            else:
                raise Exception(f"OpenAI API error: {response.status_code}")
                
        except Exception as e:
            print(f"Extraction error: {e}")
            return {
                "questions": {},
                "demographics": {},
                "completion_status": "partial",
                "extraction_notes": [f"Extraction error: {str(e)}"]
            }
    
    def handle_off_topic_message(self, message: str, form_title: str = "") -> bool:
        """
        Use LLM to detect if message is off-topic for the survey
        Returns True if message appears to be off-topic
        """
        
        # Skip LLM call for obviously valid short answers
        message_lower = message.lower().strip()
        # Empty messages are for conversation initiation, NOT off-topic
        if len(message_lower) == 0:
            return False
        if len(message_lower) < 2:  # Single characters are suspicious
            return True
            
        # Quick check for obvious valid answers - be more permissive
        if (message_lower.isdigit() or 
            message_lower in ['yes', 'no', 'maybe', 'sure', 'nope', 'ok', 'okay', 'good', 'bad', 'great']):
            return False
            
        # Check for survey-related content - be permissive for survey responses
        survey_keywords = ['pizza', 'food', 'like', 'love', 'prefer', 'favorite', 'think', 'feel', 'opinion', 'pineapple', 'bananas']
        if any(keyword in message_lower for keyword in survey_keywords):
            return False
            
        # Allow single word answers that could be valid responses
        if len(message_lower.split()) == 1 and len(message_lower) > 2:
            return False
        
        # Use LLM for smarter detection
        if not self.api_key:
            # Fallback to simple detection without API - only flag obvious spam
            spam_indicators = ['asdfgh', 'qwerty', 'weather today', 'what\'s 2+2', 'crypto price', 'stock market']
            return any(indicator in message_lower for indicator in spam_indicators)
        
        try:
            off_topic_prompt = f"""Is this message off-topic for a survey about "{form_title}"?

Message: "{message}"

Consider:
- Survey responses (ratings, opinions, feedback) = ON TOPIC
- Questions about the survey itself = ON TOPIC  
- Corrections, clarifications, partial answers = ON TOPIC
- Random unrelated topics (weather, math, news) = OFF TOPIC
- Gibberish or spam = OFF TOPIC

Answer only "YES" if clearly off-topic, "NO" if related to survey."""

            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers={
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': 'gpt-4o-mini',
                    'messages': [
                        {'role': 'user', 'content': off_topic_prompt}
                    ],
                    'temperature': 0.1,
                    'max_tokens': 5
                },
                timeout=3
            )
            
            if response.status_code == 200:
                result = response.json()
                answer = result['choices'][0]['message']['content'].strip().upper()
                return answer.startswith('YES')
            
        except Exception as e:
            print(f"Off-topic detection error: {e}")
        
        # Default to allowing the message if detection fails
        return False


def create_conversation_manager() -> ConversationManager:
    """Factory function to create conversation manager"""
    return ConversationManager()