"""
Natural Conversation Manager using LangChain
Focuses on organic conversation flow rather than structured form questions
"""

import os
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timezone

# LangChain imports
try:
    from langchain_openai import ChatOpenAI
    from langchain.memory import ConversationBufferWindowMemory
    from langchain.chains import ConversationChain
    from langchain.prompts import PromptTemplate
    from langchain.schema import HumanMessage, AIMessage
    LANGCHAIN_AVAILABLE = True
except ImportError as e:
    print(f"LangChain not available: {e}")
    LANGCHAIN_AVAILABLE = False


class ContextualMemory:
    """Enhanced memory system that tracks conversation context and follow-ups"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.conversation_memory = None
        self.topic_mentions = {}  # Track when topics were mentioned
        self.response_quality = {}  # Track quality of responses per topic
        self.last_topic_explored = None
        self.follow_up_history = []  # Track follow-up attempts
        
        if LANGCHAIN_AVAILABLE:
            try:
                self.conversation_memory = ConversationBufferWindowMemory(
                    k=8,  # Keep last 8 exchanges
                    return_messages=False,
                    memory_key="history"
                )
            except Exception as e:
                print(f"Memory initialization error: {e}")
    
    def add_exchange(self, user_message: str, bot_response: str, topic_discussed: str = None):
        """Add conversation exchange to memory"""
        if self.conversation_memory:
            try:
                self.conversation_memory.save_context(
                    {"input": user_message},
                    {"output": bot_response}
                )
            except Exception as e:
                print(f"Memory save error: {e}")
        
        # Track topic mentions
        if topic_discussed:
            self.topic_mentions[topic_discussed] = {
                'last_mentioned': datetime.now(),
                'mention_count': self.topic_mentions.get(topic_discussed, {}).get('mention_count', 0) + 1
            }
            self.last_topic_explored = topic_discussed
    
    def assess_response_quality(self, user_message: str, topic: str) -> float:
        """Assess the quality/completeness of a user response"""
        message_lower = user_message.lower().strip()
        
        # Basic quality indicators
        quality_score = 0.5  # Base score
        
        # Length indicator
        word_count = len(message_lower.split())
        if word_count >= 3:
            quality_score += 0.2
        if word_count >= 8:
            quality_score += 0.2
        
        # Specificity indicators
        if any(word in message_lower for word in ['because', 'since', 'usually', 'sometimes', 'often', 'really', 'definitely']):
            quality_score += 0.2
        
        # Enthusiasm indicators
        if any(word in message_lower for word in ['love', 'favorite', 'amazing', 'great', 'awesome', 'perfect']):
            quality_score += 0.1
        
        # Completeness indicators (ends with period, complete sentences)
        if message_lower.endswith(('.', '!')) or ',' in message_lower:
            quality_score += 0.1
        
        # Store for context
        self.response_quality[topic] = quality_score
        return min(1.0, quality_score)
    
    def should_follow_up(self, topic: str, current_response: str) -> bool:
        """Determine if we should follow up on this topic"""
        quality = self.assess_response_quality(current_response, topic)
        
        # Don't follow up if high quality response
        if quality >= 0.8:
            return False
        
        # Check if we've already followed up too much on this topic
        follow_ups_for_topic = [f for f in self.follow_up_history if f.get('topic') == topic]
        if len(follow_ups_for_topic) >= 2:
            return False
        
        return quality < 0.7
    
    def get_conversation_context(self) -> str:
        """Get formatted conversation context for prompts"""
        if self.conversation_memory:
            try:
                return self.conversation_memory.buffer
            except:
                return ""
        return ""
    
    def record_follow_up(self, topic: str, follow_up_type: str):
        """Record that we did a follow-up"""
        self.follow_up_history.append({
            'topic': topic,
            'type': follow_up_type,
            'timestamp': datetime.now()
        })


class ConversationContext:
    """Track conversation context and information needs"""
    
    def __init__(self, form_data: Dict, session_id: str):
        self.session_id = session_id
        self.form_data = form_data
        self.information_needed = self._parse_information_needs(form_data)
        self.collected_information = {}
        self.off_topic_count = 0
        self.memory = ContextualMemory(session_id)  # Use enhanced memory system
        self.current_topic_being_explored = None
        
    def _parse_information_needs(self, form_data: Dict) -> Dict[str, Dict]:
        """Parse form questions into information needs for natural conversation"""
        needs = {}
        questions = form_data.get('questions', [])
        
        for i, q in enumerate(questions):
            if not q.get('enabled', True):
                continue
                
            # Convert form question to conversation topic
            topic_key = f"topic_{i}"
            needs[topic_key] = {
                'original_question': q.get('text', ''),
                'type': q.get('type', 'text'),
                'options': q.get('options', []),
                'priority': i + 1,  # Order matters
                'natural_topic': self._convert_to_natural_topic(q),
                'collected': False,
                'value': None,
                'follow_up_prompts': self._generate_follow_up_prompts(q)
            }
        return needs
    
    def _convert_to_natural_topic(self, question: Dict) -> str:
        """Convert structured question to natural conversation topic"""
        q_text = question.get('text', '').lower()
        q_type = question.get('type', 'text')
        
        # Extract the core topic from the question
        if 'favorite' in q_text and 'pizza' in q_text and 'topping' in q_text:
            return "pizza_topping_preferences"
        elif 'often' in q_text and 'pizza' in q_text:
            return "pizza_consumption_frequency"
        elif 'crust' in q_text:
            return "pizza_crust_preferences"
        elif 'rate' in q_text and 'pizza' in q_text:
            return "pizza_satisfaction_rating"
        elif 'favorite' in q_text:
            return f"favorite_{q_text.split('favorite')[1].strip().split()[0]}"
        elif 'how often' in q_text or 'frequency' in q_text:
            return "frequency_preferences"
        elif 'rate' in q_text or 'rating' in q_text:
            return "satisfaction_rating"
        else:
            # Generic fallback
            return f"general_preferences"
    
    def _generate_follow_up_prompts(self, question: Dict) -> List[str]:
        """Generate natural follow-up prompts for deeper conversation"""
        q_text = question.get('text', '').lower()
        
        if 'pizza' in q_text and 'topping' in q_text:
            return [
                "tell me more about that choice",
                "what draws you to that topping",
                "any other toppings you enjoy",
                "what about when you're feeling adventurous"
            ]
        elif 'often' in q_text:
            return [
                "what usually influences how often",
                "does it depend on the situation",
                "tell me about your typical routine"
            ]
        elif 'rate' in q_text:
            return [
                "what makes you feel that way",
                "tell me more about your experience",
                "what could make it better"
            ]
        else:
            return [
                "tell me more about that",
                "what else comes to mind",
                "anything else you'd like to share"
            ]
    
    def mark_information_collected(self, topic: str, value: Any, confidence: float = 1.0):
        """Mark information as collected with confidence score"""
        if topic in self.information_needed:
            self.information_needed[topic]['collected'] = True
            self.information_needed[topic]['value'] = value
            self.information_needed[topic]['confidence'] = confidence
            self.collected_information[topic] = value
    
    def get_next_topic_to_explore(self) -> Optional[str]:
        """Get the next topic that needs exploration"""
        uncollected = [
            (topic, info) for topic, info in self.information_needed.items()
            if not info['collected']
        ]
        
        if not uncollected:
            return None
            
        # Sort by priority (lowest first)
        uncollected.sort(key=lambda x: x[1]['priority'])
        return uncollected[0][0]
    
    def should_follow_up(self, topic: str, user_response: str) -> bool:
        """Determine if we should do a follow-up on this topic using memory system"""
        return self.memory.should_follow_up(topic, user_response)
    
    def get_completion_percentage(self) -> float:
        """Get percentage of information collected"""
        total = len(self.information_needed)
        if total == 0:
            return 1.0
        collected = sum(1 for info in self.information_needed.values() if info['collected'])
        return collected / total


class NaturalConversationManager:
    """Manages natural, organic conversations using LangChain"""
    
    def __init__(self):
        self.api_key = self._get_openai_key()
        self.llm = None
        self.sessions = {}  # Store conversation contexts
        self._setup_llm()
        
    def _get_openai_key(self) -> Optional[str]:
        """Get OpenAI API key"""
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            print("Warning: OPENAI_API_KEY not configured")
            return None
        return api_key.strip()
    
    def _setup_llm(self):
        """Setup LangChain LLM"""
        if not LANGCHAIN_AVAILABLE or not self.api_key:
            print("LangChain or API key not available")
            return
            
        try:
            self.llm = ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0.8,  # Higher for more natural, varied responses
                max_tokens=200,   # Keep responses concise
                openai_api_key=self.api_key
            )
            print("Natural conversation LLM initialized")
        except Exception as e:
            print(f"LLM setup error: {e}")
            self.llm = None
    
    def get_conversation_context(self, session_id: str, form_data: Dict) -> ConversationContext:
        """Get or create conversation context for session"""
        if session_id not in self.sessions:
            self.sessions[session_id] = ConversationContext(form_data, session_id)
        return self.sessions[session_id]
    
    def process_conversation_turn(self, session_id: str, form_data: Dict, 
                                user_message: str, conversation_history: List[Dict]) -> Tuple[str, bool]:
        """Process a conversation turn with natural flow"""
        
        context = self.get_conversation_context(session_id, form_data)
        
        # Handle conversation initiation
        if not user_message.strip() and len(conversation_history) == 0:
            response = self._initiate_conversation(context)
            context.memory.add_exchange("", response, context.get_next_topic_to_explore())
            return response, False
        
        # Analyze user message for information extraction
        topic_discussed = self._analyze_and_extract_information(user_message, context, conversation_history)
        
        # Generate natural response
        response = self._generate_natural_response(user_message, context, conversation_history)
        
        # Add to memory with topic context
        context.memory.add_exchange(user_message, response, topic_discussed)
        
        # Check if conversation should end
        completion_rate = context.get_completion_percentage()
        is_completed = completion_rate >= 0.8  # 80% completion threshold
        
        return response, is_completed
    
    def _initiate_conversation(self, context: ConversationContext) -> str:
        """Start natural conversation"""
        form_title = context.form_data.get('title', 'survey')
        
        # Get first topic to explore
        first_topic = context.get_next_topic_to_explore()
        if not first_topic:
            return f"hey! let's chat about {form_title.lower()}! 😊"
        
        # Create natural opening based on the topic
        topic_info = context.information_needed[first_topic]
        natural_topic = topic_info['natural_topic']
        
        if 'pizza' in natural_topic:
            return "hey! 🍕 i'm super curious about pizza preferences! what's your relationship with pizza like?"
        else:
            return f"hey! let's have a casual chat about {form_title.lower()}! what comes to mind when i mention that? 😊"
    
    def _analyze_and_extract_information(self, user_message: str, context: ConversationContext, 
                                       conversation_history: List[Dict]) -> Optional[str]:
        """Analyze user message and extract relevant information"""
        if not self.llm:
            return None
            
        # Create analysis prompt
        needed_info = {topic: info for topic, info in context.information_needed.items() if not info['collected']}
        
        analysis_prompt = f"""Analyze this user message for information extraction:

User message: "{user_message}"

Information we need to collect:
{json.dumps(needed_info, indent=2)}

For each piece of information found, determine:
1. Which topic it relates to
2. The extracted value
3. Confidence level (0.0-1.0)
4. Whether it's a complete or partial answer

Respond with JSON: {{"extractions": [{{"topic": "topic_name", "value": "extracted_value", "confidence": 0.8, "complete": true}}]}}

JSON:"""

        try:
            response = self.llm.invoke([HumanMessage(content=analysis_prompt)])
            result = response.content.strip()
            
            # Clean and parse JSON
            if result.startswith('```json'):
                result = result.replace('```json', '').replace('```', '').strip()
            
            extractions_data = json.loads(result)
            
            # Apply extractions to context
            topic_discussed = None
            for extraction in extractions_data.get('extractions', []):
                topic = extraction.get('topic')
                value = extraction.get('value')
                confidence = extraction.get('confidence', 0.5)
                
                if topic and value and confidence > 0.6:  # Only high-confidence extractions
                    context.mark_information_collected(topic, value, confidence)
                    topic_discussed = topic  # Return the most recent topic discussed
            
            return topic_discussed
                    
        except Exception as e:
            print(f"Information extraction error: {e}")
            return None
    
    def _generate_natural_response(self, user_message: str, context: ConversationContext,
                                 conversation_history: List[Dict]) -> str:
        """Generate natural conversational response"""
        if not self.llm:
            return self._fallback_response(user_message, context)
        
        # Use LangChain memory for conversation context
        history_text = context.memory.get_conversation_context()
        if not history_text:
            # Fallback to basic history
            for msg in conversation_history[-6:]:  # Last 6 messages for context
                role = "User" if msg.get('role') == 'user' else "You"
                history_text += f"{role}: {msg.get('text', '')}\n"
        
        # Determine conversation strategy
        completion_rate = context.get_completion_percentage()
        next_topic = context.get_next_topic_to_explore()
        
        # Check if user message was off-topic
        if self._is_off_topic(user_message, context):
            context.off_topic_count += 1
            if context.off_topic_count >= 3:
                return "hmm, we've gotten pretty off track! let me wrap this up - thanks for chatting! 😊"
            return f"bananas... anyway, back to our chat? 😊"
        
        # Build response prompt based on conversation state
        if completion_rate >= 0.8:
            strategy = "wrapping_up"
        elif next_topic:
            strategy = "exploring_topic"
            topic_info = context.information_needed[next_topic]
        else:
            strategy = "general_follow_up"
        
        response_prompt = f"""You're having a natural, friendly conversation about {context.form_data.get('title', 'preferences')}.

PERSONALITY: Casual, curious friend who's genuinely interested. Use natural language, emojis, be warm.

CONVERSATION HISTORY:
{history_text}

USER'S LATEST: "{user_message}"

CURRENT SITUATION:
- Completion: {completion_rate*100:.0f}%
- Strategy: {strategy}
"""

        if strategy == "exploring_topic" and next_topic:
            topic_info = context.information_needed[next_topic]
            natural_topic = topic_info['natural_topic']
            follow_ups = topic_info['follow_up_prompts']
            
            response_prompt += f"""
- Topic to explore: {natural_topic}
- Follow-up options: {follow_ups}

APPROACH:
1. Acknowledge what they said naturally
2. If they gave info about our topic, show interest and ask a follow-up
3. If they didn't mention our topic, naturally steer conversation there
4. Keep it conversational, not interrogative

Example flows:
- "that's interesting! speaking of [topic], what's your take on..."
- "nice! that reminds me, i'm curious about..."
- "totally! hey, while we're chatting, what about..."
"""
        elif strategy == "wrapping_up":
            response_prompt += """
APPROACH: Start wrapping up naturally
- Thank them for sharing
- Maybe one quick final question if there's something interesting
- Keep it warm and appreciative
"""
        
        response_prompt += "\nRespond naturally (1-2 sentences max):"
        
        try:
            response = self.llm.invoke([HumanMessage(content=response_prompt)])
            result = response.content.strip()
            
            # Add completion tag if needed
            if completion_rate >= 0.8 and ("thanks" in result.lower() or "appreciate" in result.lower()):
                result += " [END]"
                
            return result
        except Exception as e:
            print(f"Response generation error: {e}")
            return self._fallback_response(user_message, context)
    
    def _is_off_topic(self, message: str, context: ConversationContext) -> bool:
        """Check if message is off-topic"""
        message_lower = message.lower().strip()
        form_title = context.form_data.get('title', '').lower()
        
        # Quick checks for obviously valid responses
        if len(message_lower) < 2:
            return True
            
        # Common valid responses
        if message_lower in ['yes', 'no', 'maybe', 'sure', 'ok']:
            return False
            
        # Check if related to form topic
        topic_keywords = []
        if 'pizza' in form_title:
            topic_keywords = ['pizza', 'food', 'eat', 'taste', 'flavor', 'topping', 'crust', 'cheese']
            
        if any(keyword in message_lower for keyword in topic_keywords):
            return False
            
        # Check for obvious off-topic patterns
        off_topic_patterns = ['weather', 'what are you', '2+2', 'crypto', 'stock', 'politics']
        return any(pattern in message_lower for pattern in off_topic_patterns)
    
    def _fallback_response(self, user_message: str, context: ConversationContext) -> str:
        """Fallback when LangChain unavailable"""
        return "tell me more! 🤔"
    
    def extract_final_data(self, session_id: str) -> Dict:
        """Extract final structured data from conversation"""
        if session_id not in self.sessions:
            return {"questions": {}, "completion_status": "partial", "notes": ["No session found"]}
        
        context = self.sessions[session_id]
        
        # Convert collected information back to form format
        extracted_questions = {}
        for topic, info in context.information_needed.items():
            if info['collected']:
                original_question = info['original_question']
                extracted_questions[original_question] = info['value']
        
        completion_rate = context.get_completion_percentage()
        completion_status = "complete" if completion_rate >= 0.8 else "partial"
        
        return {
            "questions": extracted_questions,
            "demographics": {},  # Add demographics if implemented
            "completion_status": completion_status,
            "notes": [f"Natural conversation completion: {completion_rate*100:.0f}%"]
        }
    
    def cleanup_session(self, session_id: str):
        """Clean up session data"""
        if session_id in self.sessions:
            del self.sessions[session_id]


# Factory function
def create_natural_conversation_manager() -> NaturalConversationManager:
    """Create natural conversation manager instance"""
    return NaturalConversationManager()