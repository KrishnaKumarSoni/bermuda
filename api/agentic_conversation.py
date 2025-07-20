"""
LangChain Agentic Architecture for Bermuda Conversational Forms
Implements intelligent agents with tools for natural survey conversations
"""

import os
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timezone

# LangChain imports - lazy loading to avoid initialization timeout
def get_langchain_imports():
    """Lazy import LangChain to avoid initialization timeout"""
    try:
        from langchain.memory import ConversationBufferWindowMemory
        from langchain_openai import ChatOpenAI
        from langchain.schema import HumanMessage, AIMessage
        from langchain.prompts import PromptTemplate
        from langchain.chains import LLMChain
        return {
            'ConversationBufferWindowMemory': ConversationBufferWindowMemory,
            'ChatOpenAI': ChatOpenAI,
            'HumanMessage': HumanMessage,
            'AIMessage': AIMessage,
            'PromptTemplate': PromptTemplate,
            'LLMChain': LLMChain
        }
    except ImportError:
        return None

# Global cache for imports
_langchain_cache = None

# Load environment
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


def analyze_question_progress(form_data: Dict, conversation_history: List[Dict]) -> str:
    """Analyze which questions have been answered"""
    questions = form_data.get('questions', [])
    enabled_questions = [q for q in questions if q.get('enabled', True)]
    
    conversation_text = " ".join([msg.get('text', '') for msg in conversation_history])
    
    answered = []
    remaining = []
    
    for i, q in enumerate(enabled_questions):
        question_text = q.get('text', '').lower()
        question_keywords = question_text.split()[:3]  # First 3 words
        
        # Check if this question seems addressed
        if any(keyword in conversation_text.lower() for keyword in question_keywords):
            answered.append(f"{i+1}. {q.get('text')}")
        else:
            remaining.append(f"{i+1}. {q.get('text')}")
    
    return f"ANSWERED: {len(answered)}, REMAINING: {len(remaining)}"

def analyze_response_completeness(message: str) -> str:
    """Check if response seems complete"""
    message = message.lower().strip()
    
    incomplete_signals = [
        len(message) < 5,
        message.endswith(('but', 'and', 'also', 'however', 'though')),
        message.endswith(','),
        message in ['hmm', 'uh', 'well', 'so', 'actually'],
        '...' in message
    ]
    
    complete_signals = [
        message.endswith(('.', '!', '?')),
        len(message) > 20,
        message.startswith(('yes', 'no', 'definitely', 'absolutely')),
        any(word in message for word in ['because', 'since', 'overall'])
    ]
    
    if any(incomplete_signals):
        return "INCOMPLETE"
    elif any(complete_signals):
        return "COMPLETE"
    else:
        return "UNCLEAR"


class AgenticConversationManager:
    """Smart conversation manager using LangChain components"""
    
    def __init__(self):
        self.api_key = self._get_openai_key()
        self.llm = None
        self.memory = {}  # Memory per session
        self._setup_llm()
    
    def _get_openai_key(self) -> Optional[str]:
        """Get OpenAI API key"""
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            print("Warning: OPENAI_API_KEY not configured")
            return None
        return api_key.strip().replace('\n', '').replace('\r', '')
    
    def _setup_llm(self):
        """Setup LangChain LLM"""
        global _langchain_cache
        if self.api_key and not _langchain_cache:
            _langchain_cache = get_langchain_imports()
        
        if self.api_key and _langchain_cache:
            try:
                ChatOpenAI = _langchain_cache['ChatOpenAI']
                self.llm = ChatOpenAI(
                    model="gpt-4o-mini",
                    temperature=0.7,
                    openai_api_key=self.api_key,
                    max_tokens=150
                )
            except Exception as e:
                print(f"LLM setup error: {e}")
                self.llm = None
    
    def get_bot_response(self, user_message: str, conversation_history: List[Dict], 
                        form_data: Dict, demographics: List[Dict] = None, 
                        session_id: str = None) -> Tuple[str, bool]:
        """Get intelligent response using LangChain"""
        
        if not self.llm or not _langchain_cache:
            # Enhanced fallback without LangChain
            return self._fallback_response(user_message, conversation_history, form_data)
        
        try:
            # Analyze context
            form_title = form_data.get('title', 'Survey')
            progress = analyze_question_progress(form_data, conversation_history)
            completeness = analyze_response_completeness(user_message)
            
            # Check off-topic
            if self._is_off_topic(user_message, form_title):
                return "bananas... anyway, back to the survey?", False
            
            # Create conversation prompt
            HumanMessage = _langchain_cache['HumanMessage']
            
            context_prompt = f"""You're having a casual chat about "{form_title}".

ANALYSIS:
- Question Progress: {progress}
- Last Response: {completeness}

PERSONALITY: Super casual, short responses (1-2 sentences max). Use lowercase.

RULES:
- If INCOMPLETE response: ask "go on..." or "anything else?"
- If COMPLETE response and questions remaining: acknowledge briefly, ask next question
- If most questions answered: move toward completion
- Be like texting a friend: "nice!", "got it!", "cool!"

User said: "{user_message}"

Respond casually:"""
            
            # Get response
            response = self.llm.invoke([HumanMessage(content=context_prompt)])
            bot_response = response.content.strip()
            
            # Check for completion
            is_completed = False
            if 'thanks!' in bot_response.lower() or '[END]' in bot_response:
                is_completed = True
                bot_response = bot_response.replace('[END]', '').strip()
            
            return bot_response, is_completed
            
        except Exception as e:
            print(f"LangChain error: {e}")
            return self._fallback_response(user_message, conversation_history, form_data)
    
    def _fallback_response(self, user_message: str, conversation_history: List[Dict], form_data: Dict) -> Tuple[str, bool]:
        """Enhanced fallback that asks proper survey questions"""
        
        # Check if this is off-topic first
        form_title = form_data.get('title', 'survey')
        if self._is_off_topic(user_message, form_title):
            return "bananas... anyway, back to the survey?", False
        
        # Get enabled questions
        questions = form_data.get('questions', [])
        enabled_questions = [q for q in questions if q.get('enabled', True)]
        
        if not enabled_questions:
            return "thanks for chatting!", True
        
        # Analyze which questions have been asked/answered
        conversation_text = " ".join([msg.get('text', '') for msg in conversation_history])
        
        # Find first unanswered question
        for i, question in enumerate(enabled_questions):
            question_text = question.get('text', '')
            question_keywords = question_text.lower().split()[:3]
            
            # Check if this question was already discussed
            already_asked = any(keyword in conversation_text.lower() for keyword in question_keywords if len(keyword) > 2)
            
            if not already_asked:
                # Ask this question naturally
                if i == 0:  # First question
                    return f"hey! quick chat about {form_title.lower()}? {question_text.lower()}", False
                else:
                    return f"cool! so {question_text.lower()}", False
        
        # All questions seem covered, check completeness of current response
        completeness = analyze_response_completeness(user_message)
        
        if completeness == "INCOMPLETE":
            return "tell me more...", False
        elif len(conversation_history) < 4:  # Still early in conversation
            return "anything else you'd like to share?", False
        else:
            return "awesome, thanks!", True
    
    def _is_off_topic(self, message: str, form_title: str) -> bool:
        """Simple off-topic detection - be permissive for survey responses"""
        message_lower = message.lower().strip()
        
        if len(message_lower) < 2:
            return True
            
        if (message_lower.isdigit() or 
            message_lower in ['yes', 'no', 'maybe', 'sure', 'ok', 'good', 'bad']):
            return False
            
        # Check for survey-related content - be permissive
        survey_keywords = ['pizza', 'food', 'like', 'love', 'prefer', 'favorite', 'think', 'feel', 'opinion', 'pineapple', 'bananas']
        if any(keyword in message_lower for keyword in survey_keywords):
            return False
            
        # Allow single word food items that could be toppings/preferences
        if len(message_lower.split()) == 1 and len(message_lower) > 2:
            return False
        
        # Only flag obvious spam/off-topic
        spam_indicators = ['weather today', 'what\'s 2+2', 'crypto price', 'stock market', 'asdfgh']
        return any(indicator in message_lower for indicator in spam_indicators)
    
    def infer_form_structure(self, text_dump: str) -> Dict:
        """Use LangChain for form inference"""
        if not self.llm:
            return {
                "title": "Survey",
                "questions": [{"text": "What do you think?", "type": "text", "enabled": True}]
            }
        
        prompt = PromptTemplate(
            input_variables=["text_dump"],
            template="""Extract survey questions from this text. Return JSON only.

Text: {text_dump}

Create 3-8 questions using types: text, multiple_choice, yes_no, number, rating

JSON format:
{{
    "title": "Clear Survey Title",
    "questions": [
        {{
            "text": "Question text?",
            "type": "text|multiple_choice|yes_no|number|rating",
            "options": ["option1", "option2"] if multiple_choice/yes_no/rating,
            "enabled": true
        }}
    ]
}}

JSON:"""
        )
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        
        try:
            result = chain.run(text_dump=text_dump)
            # Parse JSON from result
            result = result.strip()
            if result.startswith('```json'):
                result = result.split('```json')[1].split('```')[0]
            elif result.startswith('```'):
                result = result.split('```')[1].split('```')[0]
            
            return json.loads(result)
        except Exception as e:
            print(f"Inference error: {e}")
            return {
                "title": "Survey",
                "questions": [{"text": "What are your thoughts?", "type": "text", "enabled": True}]
            }
    
    def extract_structured_data(self, transcript: List[Dict], form_data: Dict, 
                               demographics: List[Dict] = None) -> Dict:
        """Use LangChain for data extraction or fallback extraction"""
        if not self.llm or not _langchain_cache:
            return self._fallback_extraction(transcript, form_data, demographics)
        
        # Create extraction prompt
        questions = form_data.get('questions', [])
        enabled_questions = [q for q in questions if q.get('enabled', True)]
        
        conversation_text = "\n".join([
            f"{msg['role']}: {msg['text']}" for msg in transcript
        ])
        
        questions_text = "\n".join([
            f"- {q['text']} (type: {q.get('type', 'text')})"
            for q in enabled_questions
        ])
        
        prompt = PromptTemplate(
            input_variables=["conversation", "questions"],
            template="""Extract answers from this conversation. Return JSON only.

Questions to extract:
{questions}

Conversation:
{conversation}

Extract what you can, use "not provided" for missing answers.

JSON format:
{{
    "questions": {{"Question text": "extracted answer"}},
    "demographics": {{"field": "value"}},
    "completion_status": "complete|partial",
    "extraction_notes": ["any issues"]
}}

JSON:"""
        )
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        
        try:
            result = chain.run(conversation=conversation_text, questions=questions_text)
            result = result.strip()
            if result.startswith('```json'):
                result = result.split('```json')[1].split('```')[0]
            elif result.startswith('```'):
                result = result.split('```')[1].split('```')[0]
            
            return json.loads(result)
        except Exception as e:
            print(f"Extraction error: {e}")
            return {
                "completion_status": "partial",
                "questions": {},
                "demographics": {},
                "extraction_notes": [f"Extraction error: {str(e)}"]
            }
    
    def _fallback_extraction(self, transcript: List[Dict], form_data: Dict, demographics: List[Dict] = None) -> Dict:
        """Simple extraction without LangChain"""
        questions = form_data.get('questions', [])
        enabled_questions = [q for q in questions if q.get('enabled', True)]
        
        # Build conversation text from transcript
        user_messages = [msg.get('text', '') for msg in transcript if msg.get('role') == 'user']
        conversation_text = " ".join(user_messages).lower()
        
        extracted_questions = {}
        
        for question in enabled_questions:
            question_text = question.get('text', '')
            question_type = question.get('type', 'text')
            
            # Simple keyword-based extraction
            answer = None
            
            if question_type == 'text':
                # For text questions, find the most relevant user response
                question_keywords = question_text.lower().split()[:3]
                for msg in user_messages:
                    if any(keyword in msg.lower() for keyword in question_keywords if len(keyword) > 2):
                        answer = msg.strip()
                        break
                if not answer and user_messages:
                    answer = user_messages[-1]  # Use last response if no match
                    
            elif question_type == 'multiple_choice':
                options = question.get('options', [])
                for option in options:
                    if option.lower() in conversation_text:
                        answer = option
                        break
                        
            elif question_type == 'yes_no':
                if any(word in conversation_text for word in ['yes', 'yeah', 'definitely', 'sure', 'absolutely']):
                    answer = 'Yes'
                elif any(word in conversation_text for word in ['no', 'nope', 'not really', 'never']):
                    answer = 'No'
                    
            elif question_type == 'rating':
                # Look for numbers 1-5
                import re
                numbers = re.findall(r'\b[1-5]\b', conversation_text)
                if numbers:
                    answer = int(numbers[-1])  # Use last rating found
                    
            elif question_type == 'number':
                # Extract any numbers
                import re
                numbers = re.findall(r'\d+', conversation_text)
                if numbers:
                    answer = int(numbers[-1])  # Use last number found
            
            if answer:
                extracted_questions[question_text] = answer
        
        # Determine completion status
        total_questions = len(enabled_questions)
        answered_questions = len(extracted_questions)
        completion_status = "complete" if answered_questions >= total_questions * 0.8 else "partial"
        
        return {
            "questions": extracted_questions,
            "demographics": {},  # Could add demographics extraction here
            "completion_status": completion_status,
            "extraction_notes": [f"Fallback extraction: {answered_questions}/{total_questions} questions extracted"]
        }


def create_agentic_conversation_manager() -> AgenticConversationManager:
    """Factory function to create agentic conversation manager"""
    return AgenticConversationManager()