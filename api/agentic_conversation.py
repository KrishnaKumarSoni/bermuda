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
        """Setup LLM using direct OpenAI for Firebase compatibility"""
        if not self.api_key:
            print("No OpenAI API key - using basic fallback")
            self.llm = None
            return
            
        # Use direct OpenAI API for Firebase compatibility
        print("Setting up direct OpenAI API for conversation")
    
    def get_bot_response(self, user_message: str, conversation_history: List[Dict], 
                        form_data: Dict, demographics: List[Dict] = None, 
                        session_id: str = None) -> Tuple[str, bool]:
        """Get intelligent response using direct OpenAI API"""
        
        # Use sophisticated conversation system if API key available
        if self.api_key:
            return self._openai_conversation_response(user_message, conversation_history, form_data, demographics)
        else:
            # Only fallback if no API key
            return self._fallback_response(user_message, conversation_history, form_data)
    
    def _openai_conversation_response(self, user_message: str, conversation_history: List[Dict], 
                                    form_data: Dict, demographics: List[Dict] = None) -> Tuple[str, bool]:
        """Human-like conversation using direct OpenAI API following YAML specifications"""
        
        try:
            import requests
            
            form_title = form_data.get('title', 'Survey')
            
            # Check if this is conversation initiation (empty message) BEFORE off-topic check
            is_initiation = not user_message.strip()
            
            # Quick off-topic check first (but skip for conversation initiation)
            if not is_initiation and self._is_off_topic(user_message, form_title):
                return f"bananas... anyway, back to {form_title.lower()}?", False
            
            # Build enabled questions for the prompt
            questions = form_data.get('questions', [])
            enabled_questions = [q for q in questions if q.get('enabled', True)]
            
            # Build conversation context
            conversation_context = ""
            for msg in conversation_history[-10:]:  # Last 10 messages for memory
                role = "Bot" if msg.get('role') == 'assistant' else "User"
                conversation_context += f"{role}: {msg.get('text', '')}\n"
            
            
            # Create conversation prompt following YAML specs exactly
            if is_initiation:
                # Agent initiates conversation per respondant-chat-xp.yaml
                first_question = enabled_questions[0] if enabled_questions else None
                if first_question:
                    conversation_prompt = f"""You're a super chill, casual person starting a conversation about "{form_title}". 

PERSONALITY: Text like a friend - short, casual, authentic. Use "ur", "tbh", "ngl", lowercase, minimal punctuation.

MESSAGE STYLE:
- Keep responses SHORT (1-2 sentences max)
- Use casual texting language 
- Drop formal words, be conversational
- Add personality with casual reactions
- Ask ONE question at a time, naturally

FIRST QUESTION TO WEAVE IN: {first_question.get('text', '')} (type: {first_question.get('type', 'text')})

INITIATION EXAMPLES:
- "hey! quick chat about {form_title.lower()}? first up - [question]"
- "hi there! lets talk {form_title.lower()}. so [question]?"

RULES:
- NO long responses or formal language
- DON'T repeat what they said back in detail  
- USE lowercase, casual words, be authentic
- NEVER list multiple choice options
- Be like texting a friend

Respond naturally as the friendly bot starting the conversation:"""
                else:
                    conversation_prompt = f"""Start a friendly conversation about "{form_title}". Say hello and ask what they'd like to share about {form_title.lower()}. Be casual and use emojis."""
            else:
                # Use exact prompt from llm-prompts-and-chains.yaml with invalid response handling
                questions_json = []
                for q in enabled_questions:
                    q_dict = {
                        'text': q.get('text', ''),
                        'type': q.get('type', 'text')
                    }
                    if q.get('options'):
                        q_dict['options'] = q.get('options', [])
                    questions_json.append(q_dict)

                conversation_prompt = f"""You are a warm, friendly human conversationalist (like a curious friend) gathering info for this form: {form_title}. Act naturally—use emojis, casual language, empathy. Never sound robotic. Ask one question at a time, weave in follow-ups if needed.

Required data to collect (questions and demographics, in order): {json.dumps(questions_json, indent=2)}

Rules (STRICTLY follow):
- Be unbiased: For multiple_choice/yes_no/rating, NEVER list options upfront. Ask openly (e.g., "What's your favorite coffee type?"), let user answer freely, then handle in CoT.
- CRITICAL - Invalid responses: If user gives nonsensical/completely invalid answer (e.g., "water" for pizza toppings, "purple" for yes/no), immediately follow up with clarification like "That doesn't quite fit - could you try again?" Don't accept obviously wrong answers.
- Bucketize in CoT: Map user answers to closest option semantically (e.g., 'cappuccino' → if close to 'Latte', or 'other' if no fit). For number: Parse to numeric. For text: Extract verbatim.
- Invalid type handling: For number questions, if they give non-numeric ("many" for "how many"), ask "Could you give me a number?" For rating, if not a rating word, ask "How would you rate that?"
- All questions mandatory by default, but if user insists on skipping (e.g., "skip" or "don't want to"), acknowledge empathetically and move on—mark as skipped.
- Off-topic/gibberish/general queries (not related to form): Respond ONLY with "bananas" + gentle redirect (e.g., "bananas... anyway, back to your coffee?"). After 3 off-topics, end chat.
- Handle edges naturally: Use CoT to detect/resolve.
- End chat: If all data collected (including demographics if enabled), output friendly thanks + [END] tag. If stuck (e.g., loops), output [END].

Current conversation:
{conversation_context}

User's latest message: {user_message}

###
Chain-of-Thought (reason step-by-step, output ONLY here):
Step 1: Analyze input - Extract any answers, detect skips/conflicts/vagueness/off-topic/INVALID RESPONSES. Compare to memory for consistency (prioritize latest if conflict).
Step 2: Validate response - Check if answer makes sense for question type. If asking about pizza toppings and they say "water", mark as INVALID. If asking yes/no and they say random word, mark INVALID.
Step 3: Track progress - List collected vs. required data (e.g., Question 1: collected 'Latte' via bucketizing; Demographics: pending). Identify next gap.
Step 4: Handle edges - If INVALID: Plan clarification follow-up. If off-topic: Plan "bananas". If vague/no-fit: Plan follow-up (max 2 per question). If skip insisted: Mark [SKIP].
Step 5: Plan response - If INVALID response, ask for clarification. Else, acknowledge + next question/follow-up. If all done: Thanks + [END].
Step 6: Self-critique - Is this on-topic, natural, unbiased? Is response validation working correctly? If not, adjust.

Response (output ONLY the bot's message here, nothing else):"""

            # Call OpenAI API
            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers={
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': 'gpt-4o-mini',
                    'messages': [{'role': 'user', 'content': conversation_prompt}],
                    'temperature': 0.8,  # Higher for more natural, varied responses
                    'max_tokens': 200,
                    'presence_penalty': 0.6,  # Encourage varied language
                    'frequency_penalty': 0.3  # Reduce repetition
                },
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()['choices'][0]['message']['content'].strip()
                
                # Check for completion
                is_completed = '[END]' in result
                if is_completed:
                    result = result.replace('[END]', '').strip()
                
                return result, is_completed
            else:
                print(f"OpenAI API error: {response.status_code} - {response.text}")
                return self._fallback_response(user_message, conversation_history, form_data)
                
        except Exception as e:
            print(f"OpenAI conversation error: {e}")
            return self._fallback_response(user_message, conversation_history, form_data)
        
        try:
            # Old LangChain code (keeping for reference but won't execute)
            form_title = form_data.get('title', 'Survey')
            progress = analyze_question_progress(form_data, conversation_history)
            completeness = analyze_response_completeness(user_message)
            
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
        # NOTE: Empty messages are NOT off-topic - they're used for conversation initiation
        if len(message_lower) < 2 and len(message_lower) > 0:
            return True
            
        # Skip functionality - these are valid survey responses, not off-topic
        skip_variations = ['skip', 'skip this', 'skip that', 'pass', 'skip question', 'dont want to', 'don\'t want to', 'no thanks']
        if any(skip_phrase in message_lower for skip_phrase in skip_variations):
            return False
            
        # Common conversational responses that should not be flagged as off-topic
        conversational_responses = ['yes', 'no', 'maybe', 'sure', 'ok', 'good', 'bad', 'great', 'what\'s up', 'whats up', 'sure what\'s up', 'hi', 'hello', 'hey']
        if (message_lower.isdigit() or message_lower in conversational_responses):
            return False
        
        # Use simple local off-topic detection to be more permissive
        # (Disabled OpenAI API detection as it was too aggressive)
        
        # Be permissive - only flag obviously problematic content
        # Allow most conversational responses unless clearly off-topic
        
        # Flag only clearly off-topic patterns
        off_topic_patterns = ['weather', 'what\'s 2+2', '2+2', 'crypto', 'stock market', 'bitcoin', 'politics', 'covid', 'vaccine']
        if any(pattern in message_lower for pattern in off_topic_patterns):
            return True
            
        # Everything else is considered on-topic or conversational
        return False
    
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
        """LLM-based extraction using direct OpenAI API calls"""
        questions = form_data.get('questions', [])
        enabled_questions = [q for q in questions if q.get('enabled', True)]
        
        # Format transcript for LLM
        conversation_text = ""
        for msg in transcript:
            role = "User" if msg.get('role') == 'user' else "Bot"
            conversation_text += f"{role}: {msg.get('text', '')}\n"
        
        # Format questions for LLM
        questions_text = ""
        for q in enabled_questions:
            q_type = q.get('type', 'text')
            q_text = q.get('text', '')
            options = q.get('options', [])
            if options:
                questions_text += f"- {q_text} (type: {q_type}, options: {', '.join(options)})\n"
            else:
                questions_text += f"- {q_text} (type: {q_type})\n"
        
        # Use LLM for extraction if available
        if self.api_key:
            try:
                import requests
                extraction_prompt = f"""From this chat transcript: {conversation_text}

Map to structured form data: {questions_text}

Rules:
- Extract answers accurately, using types (e.g., parse 'three' to 3 for number).
- Bucketize MCQ/yes_no/rating without bias: Map semantically to options (e.g., 'capp' → 'Latte' if closest; 'alien brew' → 'other: alien brew' if no fit). For text: Verbatim. For number: Numeric parse.
- CRITICAL - Invalid responses: If user gave nonsensical answers (e.g., "water" for pizza toppings), mark as 'invalid_response_given' NOT as a valid answer. Only extract meaningful responses.
- Resolve edges: Prioritize latest for conflicts; mark 'skipped' if insisted; 'unclear' if vague; 'invalid_response_given' if completely nonsensical.
- Output JSON: {{"questions": {{"question_text": "extracted_answer"}}, "demographics": {{}}, "completion_status": "complete|partial", "extraction_notes": ["any issues", "invalid responses filtered"]}}

###
Chain-of-Thought:
Step 1: Scan transcript for relevant snippets per question.
Step 2: Validate responses - Check if answers make logical sense for question context. Filter out obviously invalid responses.
Step 3: Apply bucketizing/validation (list options, find best match; if no fit, note 'other'; if invalid, note 'invalid_response_given').
Step 4: Handle edges (e.g., skips → 'skipped'; multi-answers → split; nonsense → 'invalid_response_given').
Step 5: Self-critique: Is extraction complete/accurate? Are invalid responses properly filtered? If partial, flag gaps.

Output (JSON only):"""

                response = requests.post(
                    'https://api.openai.com/v1/chat/completions',
                    headers={
                        'Authorization': f'Bearer {self.api_key}',
                        'Content-Type': 'application/json'
                    },
                    json={
                        'model': 'gpt-4o-mini',
                        'messages': [{'role': 'user', 'content': extraction_prompt}],
                        'temperature': 0.3,
                        'max_tokens': 800
                    },
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()['choices'][0]['message']['content'].strip()
                    
                    # Clean and parse JSON
                    if result.startswith('```json'):
                        result = result.replace('```json', '').replace('```', '').strip()
                    elif result.startswith('```'):
                        result = result.replace('```', '').strip()
                    
                    try:
                        import json
                        extracted_data = json.loads(result)
                        return extracted_data
                    except json.JSONDecodeError:
                        print(f"LLM extraction JSON parse error: {result}")
                        # Fall back to simple extraction
                
            except Exception as e:
                print(f"LLM extraction error: {e}")
                # Fall back to simple extraction
        
        # Fallback: Simple keyword-based extraction
        user_messages = [msg.get('text', '') for msg in transcript if msg.get('role') == 'user']
        conversation_text = " ".join(user_messages).lower()
        
        extracted_questions = {}
        
        for i, question in enumerate(enabled_questions):
            question_text = question.get('text', '')
            question_type = question.get('type', 'text')
            answer = None
            
            if question_type == 'text':
                # Use positional matching for text questions
                if i < len(user_messages):
                    answer = user_messages[i].strip()
                    
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
                import re
                numbers = re.findall(r'\b[1-5]\b', conversation_text)
                if numbers:
                    answer = int(numbers[-1])
                    
            elif question_type == 'number':
                import re
                numbers = re.findall(r'\d+', conversation_text)
                if numbers:
                    answer = int(numbers[-1])
            
            if answer:
                extracted_questions[question_text] = answer
        
        total_questions = len(enabled_questions)
        answered_questions = len(extracted_questions)
        completion_status = "complete" if answered_questions >= total_questions * 0.8 else "partial"
        
        return {
            "questions": extracted_questions,
            "demographics": {},
            "completion_status": completion_status,
            "extraction_notes": [f"Simple extraction: {answered_questions}/{total_questions} questions extracted"]
        }


def create_agentic_conversation_manager() -> AgenticConversationManager:
    """Factory function to create agentic conversation manager"""
    return AgenticConversationManager()