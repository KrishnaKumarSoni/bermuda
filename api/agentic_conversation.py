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
        """Setup LLM - use direct OpenAI instead of LangChain in production"""
        # Skip LangChain setup in Firebase environment to avoid import issues
        self.llm = None
        print("Using direct OpenAI API calls instead of LangChain")
    
    def get_bot_response(self, user_message: str, conversation_history: List[Dict], 
                        form_data: Dict, demographics: List[Dict] = None, 
                        session_id: str = None) -> Tuple[str, bool]:
        """Get intelligent response using LangChain"""
        
        # Always use fallback response for Firebase deployment
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
            
            # Build questions JSON for the prompt
            questions_json = []
            for q in form_data.get('questions', []):
                if q.get('enabled', True):
                    q_dict = {
                        'text': q.get('text', ''),
                        'type': q.get('type', 'text')
                    }
                    if 'options' in q:
                        q_dict['options'] = q.get('options', [])
                    questions_json.append(q_dict)
            
            # Build memory string
            memory_text = ""
            for msg in conversation_history[-10:]:
                role = "Bot" if msg.get('role') == 'assistant' else "User"
                memory_text += f"{role}: {msg.get('text', '')}\n"
            
            context_prompt = f"""You are a warm, friendly human conversationalist (like a curious friend) gathering info for this form: {form_title}. Act naturally—use emojis, casual language, empathy. Never sound robotic. Ask one question at a time, weave in follow-ups if needed.

Required data to collect (questions and demographics, in order): {questions_json}

Rules (STRICTLY follow):
- Be unbiased: For multiple_choice/yes_no/rating, NEVER list options upfront. Ask openly (e.g., "What's your favorite coffee type?"), let user answer freely, then handle in CoT.
- Bucketize in CoT: Map user answers to closest option semantically (e.g., 'cappuccino' → if close to 'Latte', or 'other' if no fit). For number: Parse to numeric. For text: Extract verbatim.
- All questions mandatory by default, but if user insists on skipping (e.g., "skip" or "don't want to"), acknowledge empathetically and move on—mark as skipped.
- Off-topic/gibberish/general queries (not related to form): Respond ONLY with "bananas" + gentle redirect (e.g., "bananas... anyway, back to your coffee?"). After 3 off-topics, end chat.
- Handle edges naturally: Use CoT to detect/resolve.
- End chat: If all data collected (including demographics if enabled), output friendly thanks + [END] tag. If stuck (e.g., loops), output [END].

Chat history: {memory_text}

User's latest message: {user_message}

###
Chain-of-Thought (reason step-by-step, output ONLY here):
Step 1: Analyze input - Extract any answers, detect skips/conflicts/vagueness/off-topic. Compare to memory for consistency (prioritize latest if conflict).
Step 2: Track progress - List collected vs. required data (e.g., Question 1: collected 'Latte' via bucketizing; Demographics: pending). Identify next gap.
Step 3: Handle edges - If off-topic: Plan "bananas". If vague/no-fit: Plan follow-up (max 2 per question). If skip insisted: Mark [SKIP] for that question. If pre/multi-answers: Extract and skip asking.
Step 4: Plan response - Decide natural reply (e.g., acknowledge + next question/follow-up). If all done: Thanks + [END].
Step 5: Self-critique - Is this on-topic, natural, unbiased? If not, adjust. Validate bucketizing accuracy.

Response (output ONLY the bot's message here, nothing else):"""
            
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
        """Enhanced fallback following YAML specifications"""
        
        form_title = form_data.get('title', 'survey')
        
        # Check if this is off-topic first
        if self._is_off_topic(user_message, form_title):
            return f"bananas... anyway, back to {form_title.lower()}? 😊", False
        
        # Get enabled questions
        questions = form_data.get('questions', [])
        enabled_questions = [q for q in questions if q.get('enabled', True)]
        
        if not enabled_questions:
            return "thanks for chatting! [END]", True
        
        # Analyze conversation progress
        conversation_text = " ".join([msg.get('text', '') for msg in conversation_history if msg.get('role') == 'user'])
        
        # Track which questions have been addressed
        answered_questions = set()
        for i, question in enumerate(enabled_questions):
            question_text = question.get('text', '').lower()
            question_keywords = [word for word in question_text.split()[:4] if len(word) > 2]
            
            # Check if this question was discussed (simple keyword matching)
            if any(keyword in conversation_text.lower() for keyword in question_keywords):
                answered_questions.add(i)
        
        # Find next unanswered question
        next_question_idx = None
        for i, question in enumerate(enabled_questions):
            if i not in answered_questions:
                next_question_idx = i
                break
        
        if next_question_idx is not None:
            question = enabled_questions[next_question_idx]
            question_text = question.get('text', '')
            
            # Format question naturally without revealing options
            if next_question_idx == 0 and len(conversation_history) < 2:
                # First interaction
                return f"hey! quick chat about {form_title.lower()}? {question_text} 😊", False
            else:
                # Subsequent questions - acknowledge and ask next
                acknowledges = ["cool!", "nice!", "got it!", "awesome!"]
                ack = acknowledges[next_question_idx % len(acknowledges)]
                return f"{ack} {question_text}", False
        
        # All questions addressed - check if we should end
        if len(conversation_history) >= len(enabled_questions) * 2:
            return "awesome, thanks so much! 😊 [END]", True
        
        # Handle incomplete responses or follow-ups
        completeness = analyze_response_completeness(user_message)
        if completeness == "INCOMPLETE":
            return "tell me more... 🤔", False
        else:
            return "anything else you'd like to share?", False
    
    def _is_off_topic(self, message: str, form_title: str) -> bool:
        """LLM-based off-topic detection following YAML specifications"""
        message_lower = message.lower().strip()
        
        # Quick checks for obviously valid responses
        if len(message_lower) < 2:
            return True
            
        if (message_lower.isdigit() or 
            message_lower in ['yes', 'no', 'maybe', 'sure', 'ok', 'good', 'bad', 'great']):
            return False
        
        # Use direct OpenAI API for sophisticated detection if available
        if self.api_key:
            try:
                import requests
                off_topic_prompt = f"""Is this user message off-topic for a survey about "{form_title}"?

User message: "{message}"

Context: This is a conversational survey collecting opinions and preferences about {form_title}.

Consider these as ON-TOPIC:
- Direct answers to survey questions
- Opinions, preferences, ratings related to the topic
- Clarifications or corrections to previous answers
- Questions about the survey itself
- Single word answers that could be valid responses

Consider these as OFF-TOPIC:
- General conversation unrelated to {form_title}
- Questions about weather, math, current events
- Random gibberish or spam
- Technical questions about other topics

Answer only "YES" if clearly off-topic, "NO" if related to the survey topic."""

                response = requests.post(
                    'https://api.openai.com/v1/chat/completions',
                    headers={
                        'Authorization': f'Bearer {self.api_key}',
                        'Content-Type': 'application/json'
                    },
                    json={
                        'model': 'gpt-4o-mini',
                        'messages': [{'role': 'user', 'content': off_topic_prompt}],
                        'temperature': 0.1,
                        'max_tokens': 5
                    },
                    timeout=5
                )
                
                if response.status_code == 200:
                    result = response.json()['choices'][0]['message']['content'].strip().upper()
                    return result.startswith('YES')
                
            except Exception as e:
                print(f"OpenAI off-topic detection error: {e}")
                # Fall back to keyword-based detection
        
        # Fallback: be permissive for survey-related content
        survey_keywords = ['pizza', 'food', 'like', 'love', 'prefer', 'favorite', 'think', 'feel', 'opinion']
        if any(keyword in message_lower for keyword in survey_keywords):
            return False
            
        # Allow single word answers that could be valid
        if len(message_lower.split()) == 1 and len(message_lower) > 2:
            return False
        
        # Flag obvious off-topic patterns
        off_topic_patterns = ['weather', 'what\'s 2+2', '2+2', 'crypto', 'stock market', 'what are you']
        return any(pattern in message_lower for pattern in off_topic_patterns)
    
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
            input_variables=["transcript", "questions_json"],
            template="""From this chat transcript: {transcript}

Map to structured form data: {questions_json}

Rules:
- Extract answers accurately, using types (e.g., parse 'three' to 3 for number).
- Bucketize MCQ/yes_no/rating without bias: Map semantically to options (e.g., 'capp' → 'Latte' if closest; 'alien brew' → 'other: alien brew' if no fit). For text: Verbatim. For number: Numeric parse.
- Resolve edges: Prioritize latest for conflicts; mark 'skipped' if insisted; 'unclear' if vague.
- Output JSON: {{'questions': {{q_text: answer}}, 'demographics': {{}}, 'partial': true/false, 'notes': [any edges, e.g., 'Conflict resolved']}}

###
Chain-of-Thought:
Step 1: Scan transcript for relevant snippets per question.
Step 2: Apply bucketizing/validation (list options, find best match; if no fit, note 'other').
Step 3: Handle edges (e.g., skips → 'skipped'; multi-answers → split).
Step 4: Self-critique: Is extraction complete/accurate? If partial, flag gaps.

Output (JSON only):"""
        )
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        
        try:
            result = chain.run(transcript=conversation_text, questions_json=questions_text)
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
                question_keywords = question_text.lower().split()[:4]
                # Look for responses that come after this question is asked
                for i, msg in enumerate(user_messages):
                    # Check if the message contains relevant keywords or is positioned correctly
                    if any(keyword in msg.lower() for keyword in question_keywords if len(keyword) > 2):
                        answer = msg.strip()
                        break
                    # Also check if it's the first substantial answer
                    elif i == 0 and len(msg.strip()) > 3:
                        answer = msg.strip()
                        break
                if not answer and user_messages:
                    answer = user_messages[0]  # Use first response for first question
                    
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