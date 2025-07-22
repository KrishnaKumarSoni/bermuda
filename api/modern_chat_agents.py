"""
Modern Chat Architecture using OpenAI Agents SDK Pattern (2025)
Multi-agent system with handoffs for conversational forms
"""

import os
import json
import uuid
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timezone
from dataclasses import dataclass
from enum import Enum

class ChatAction(Enum):
    CONTINUE = "continue"
    PAUSE = "pause" 
    END = "end"
    HANDOFF = "handoff"
    SAVE = "save"
    EXTRACT = "extract"

class AgentType(Enum):
    ORCHESTRATOR = "orchestrator"
    CONVERSATION = "conversation"
    EXTRACTOR = "extractor"
    VALIDATOR = "validator"

@dataclass
class ChatContext:
    session_id: str
    form_id: str
    form_data: Dict
    conversation_history: List[Dict]
    current_question_index: int = 0
    completed_questions: List[int] = None
    is_paused: bool = False
    last_action: Optional[ChatAction] = None
    
    def __post_init__(self):
        if self.completed_questions is None:
            self.completed_questions = []

class ModernChatAgent:
    """Base class for specialized chat agents"""
    
    def __init__(self, agent_type: AgentType, api_key: str):
        self.agent_type = agent_type
        self.api_key = api_key
        self.name = f"{agent_type.value}_agent"
        
    async def process(self, context: ChatContext, user_message: str) -> Tuple[str, ChatAction, Optional[AgentType]]:
        """Process message and return (response, action, next_agent)"""
        raise NotImplementedError

class OrchestratorAgent(ModernChatAgent):
    """Main decision-making agent that routes to specialized agents"""
    
    def __init__(self, api_key: str):
        super().__init__(AgentType.ORCHESTRATOR, api_key)
        
    async def process(self, context: ChatContext, user_message: str) -> Tuple[str, ChatAction, Optional[AgentType]]:
        """Decide what to do with the user message"""
        
        # Use OpenAI for intelligent routing
        decision_prompt = f"""You are a chat orchestrator for a conversational survey system.

Current context:
- Form: "{context.form_data.get('title', 'Survey')}"
- Current question: {context.current_question_index + 1}/{len([q for q in context.form_data.get('questions', []) if q.get('enabled', True)])}
- Is paused: {context.is_paused}
- Message count: {len(context.conversation_history)}

User message: "{user_message}"

Analyze the user's intent and decide the next action:

1. PAUSE - User wants to pause/stop for now ("I'll continue later", "save for now", "pause", "stop")
2. END - User wants to end permanently ("I'm done", "finish", "that's all") 
3. CONTINUE - Normal conversation flow (questions/answers)
4. EXTRACT - All questions answered, ready to extract data

Respond with JSON: {{"action": "PAUSE|END|CONTINUE|EXTRACT", "reasoning": "why this action", "user_intent": "what user wants"}}"""

        try:
            import requests
            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers={
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': 'gpt-4o-mini',
                    'messages': [{'role': 'user', 'content': decision_prompt}],
                    'temperature': 0.1,
                    'max_tokens': 200
                },
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()['choices'][0]['message']['content'].strip()
                
                # Parse JSON response
                try:
                    decision = json.loads(result)
                    action_str = decision.get('action', 'CONTINUE')
                    action = ChatAction(action_str.lower())
                    reasoning = decision.get('reasoning', '')
                    
                    # Route to appropriate agent based on decision
                    if action == ChatAction.PAUSE:
                        return f"got it! i'll save ur progress and we can continue later 👍", action, None
                    elif action == ChatAction.END:
                        return f"awesome, thanks for chatting! 🙌", action, AgentType.EXTRACTOR
                    elif action == ChatAction.EXTRACT:
                        return "", action, AgentType.EXTRACTOR
                    else:
                        return "", ChatAction.HANDOFF, AgentType.CONVERSATION
                        
                except json.JSONDecodeError:
                    # Fallback if JSON parsing fails
                    user_lower = user_message.lower().strip()
                    if any(word in user_lower for word in ['pause', 'later', 'continue later', 'save']):
                        return f"got it! saving ur progress. just come back anytime! 👋", ChatAction.PAUSE, None
                    elif any(word in user_lower for word in ['done', 'finish', 'end', 'that\'s all']):
                        return f"perfect! thanks so much! 😊", ChatAction.END, AgentType.EXTRACTOR
                    else:
                        return "", ChatAction.HANDOFF, AgentType.CONVERSATION
            
        except Exception as e:
            print(f"Orchestrator error: {e}")
            # Fallback to conversation agent
            return "", ChatAction.HANDOFF, AgentType.CONVERSATION

class ConversationAgent(ModernChatAgent):
    """Specialized agent for natural conversations and question handling"""
    
    def __init__(self, api_key: str):
        super().__init__(AgentType.CONVERSATION, api_key)
        
    async def process(self, context: ChatContext, user_message: str) -> Tuple[str, ChatAction, Optional[AgentType]]:
        """Handle natural conversation flow"""
        
        form_title = context.form_data.get('title', 'Survey')
        questions = [q for q in context.form_data.get('questions', []) if q.get('enabled', True)]
        
        # Check if conversation initiation
        if not user_message.strip() and len(context.conversation_history) == 0:
            if questions:
                first_q = questions[0]
                return f"hey! quick chat about {form_title.lower()}? {first_q.get('text', '')} 😊", ChatAction.CONTINUE, None
            else:
                return f"hey! let's chat about {form_title.lower()}! what would u like to share?", ChatAction.CONTINUE, None
        
        # Build conversation prompt for GPT
        conversation_prompt = f"""You're a super chill Gen Z friend doing a quick survey chat about "{form_title}".

PERSONALITY: Casual, authentic, use "ur", "tbh", lowercase, minimal punctuation. Keep responses SHORT (1-2 sentences).

CURRENT QUESTIONS TO COVER:
{chr(10).join([f"{i+1}. {q.get('text', '')} (type: {q.get('type', 'text')})" for i, q in enumerate(questions)])}

CONVERSATION HISTORY (last 6 messages):
{chr(10).join([f"{'Bot' if msg.get('role') == 'assistant' else 'User'}: {msg.get('text', '')}" for msg in context.conversation_history[-6:]])}

USER'S LATEST: "{user_message}"

RULES:
- Ask questions naturally without listing options
- Acknowledge answers casually ("nice!", "cool!", "got it!")  
- If they skip something: "no worries! moving on..."
- If unclear: "tell me more?" or "go on..."
- ONE question at a time
- If all questions covered, say thanks + add [COMPLETE] tag

Respond as the casual bot:"""

        try:
            import requests
            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers={
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': 'gpt-4o-mini', 
                    'messages': [{'role': 'user', 'content': conversation_prompt}],
                    'temperature': 0.8,
                    'max_tokens': 150
                },
                timeout=10
            )
            
            if response.status_code == 200:
                bot_response = response.json()['choices'][0]['message']['content'].strip()
                
                # Check for completion
                if '[COMPLETE]' in bot_response:
                    bot_response = bot_response.replace('[COMPLETE]', '').strip()
                    return bot_response, ChatAction.END, AgentType.EXTRACTOR
                
                return bot_response, ChatAction.CONTINUE, None
            
        except Exception as e:
            print(f"Conversation agent error: {e}")
            return "tell me more! 🤔", ChatAction.CONTINUE, None

class ExtractorAgent(ModernChatAgent):
    """Specialized agent for data extraction from conversations"""
    
    def __init__(self, api_key: str):
        super().__init__(AgentType.EXTRACTOR, api_key)
        
    async def process(self, context: ChatContext, user_message: str) -> Tuple[str, ChatAction, Optional[AgentType]]:
        """Extract structured data from conversation"""
        
        questions = [q for q in context.form_data.get('questions', []) if q.get('enabled', True)]
        
        # Format conversation for extraction
        conversation_text = "\n".join([
            f"{'User' if msg.get('role') == 'user' else 'Bot'}: {msg.get('text', '')}"
            for msg in context.conversation_history
        ])
        
        extraction_prompt = f"""Extract survey responses from this conversation:

QUESTIONS TO EXTRACT:
{chr(10).join([f"{i+1}. {q.get('text', '')} (type: {q.get('type', 'text')})" for i, q in enumerate(questions)])}

CONVERSATION:
{conversation_text}

Extract answers and return JSON:
{{"questions": {{"Question text": "extracted answer"}}, "completion_status": "complete|partial", "notes": ["any observations"]}}

For multiple choice/ratings: Map user's natural language to closest option or 'other'.
For text: Extract verbatim. For numbers: Parse to numeric.
Mark as 'skipped' if user explicitly skipped.

JSON:"""

        try:
            import requests
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
                    'max_tokens': 400
                },
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()['choices'][0]['message']['content'].strip()
                
                # Clean and parse JSON
                if result.startswith('```json'):
                    result = result.replace('```json', '').replace('```', '').strip()
                
                try:
                    extracted_data = json.loads(result)
                    # Store extraction result in context for later use
                    context.extracted_data = extracted_data
                    return "", ChatAction.EXTRACT, None
                except json.JSONDecodeError:
                    return "", ChatAction.EXTRACT, None
                    
        except Exception as e:
            print(f"Extraction error: {e}")
            return "", ChatAction.EXTRACT, None

class ModernChatManager:
    """Main chat manager using multi-agent architecture"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.agents = {
            AgentType.ORCHESTRATOR: OrchestratorAgent(api_key),
            AgentType.CONVERSATION: ConversationAgent(api_key),
            AgentType.EXTRACTOR: ExtractorAgent(api_key)
        }
        self.sessions = {}  # In-memory session storage
        
    def get_session(self, session_id: str, form_data: Dict) -> ChatContext:
        """Get or create chat session"""
        if session_id not in self.sessions:
            self.sessions[session_id] = ChatContext(
                session_id=session_id,
                form_id=form_data.get('form_id', ''),
                form_data=form_data,
                conversation_history=[]
            )
        return self.sessions[session_id]
    
    async def process_message(self, session_id: str, form_data: Dict, user_message: str, device_id: str = None) -> Dict:
        """Main entry point for processing messages"""
        
        context = self.get_session(session_id, form_data)
        
        # Add user message to history (if not empty)
        if user_message.strip():
            context.conversation_history.append({
                'role': 'user',
                'text': user_message,
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
        
        # Start with orchestrator for decision making
        current_agent = AgentType.ORCHESTRATOR
        response = ""
        final_action = ChatAction.CONTINUE
        
        try:
            # Process through agent chain
            while current_agent:
                agent = self.agents[current_agent]
                agent_response, action, next_agent = await agent.process(context, user_message)
                
                if agent_response:  # Agent provided a response
                    response = agent_response
                    final_action = action
                    break
                elif action == ChatAction.HANDOFF:  # Agent wants to handoff
                    current_agent = next_agent
                    continue
                else:  # Agent completed without response
                    final_action = action
                    break
            
            # Add bot response to history
            if response:
                context.conversation_history.append({
                    'role': 'assistant',
                    'text': response,
                    'timestamp': datetime.now(timezone.utc).isoformat()
                })
            
            # Handle session state changes
            if final_action == ChatAction.PAUSE:
                context.is_paused = True
            elif final_action == ChatAction.END:
                context.is_paused = False
                # Trigger extraction if not already done
                if not hasattr(context, 'extracted_data'):
                    extractor = self.agents[AgentType.EXTRACTOR]
                    await extractor.process(context, "")
            
            # Periodic saves every 5 messages
            if len(context.conversation_history) % 5 == 0 and len(context.conversation_history) > 0:
                await self._save_partial_data(context)
            
            return {
                'response': response,
                'completed': final_action == ChatAction.END,
                'paused': final_action == ChatAction.PAUSE,
                'message_count': len(context.conversation_history),
                'session_id': session_id,
                'action': final_action.value
            }
            
        except Exception as e:
            print(f"Chat processing error: {e}")
            return {
                'response': "sorry, something went wrong. can you try again? 🤔",
                'completed': False,
                'paused': False,
                'error': str(e),
                'session_id': session_id
            }
    
    async def resume_session(self, session_id: str) -> Dict:
        """Resume a paused conversation"""
        if session_id in self.sessions:
            context = self.sessions[session_id]
            context.is_paused = False
            
            # Re-engage with a friendly message
            resume_msg = "hey! ready to continue where we left off? 😊"
            context.conversation_history.append({
                'role': 'assistant',
                'text': resume_msg,
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
            
            return {
                'response': resume_msg,
                'completed': False,
                'paused': False,
                'message_count': len(context.conversation_history),
                'session_id': session_id,
                'resumed': True
            }
        
        return {'error': 'Session not found'}
    
    async def _save_partial_data(self, context: ChatContext):
        """Save partial conversation data"""
        try:
            # Trigger extraction for partial save
            extractor = self.agents[AgentType.EXTRACTOR]
            await extractor.process(context, "")
            
            # Here you would save to your database
            # For now just log it
            print(f"Partial save for session {context.session_id}")
            
        except Exception as e:
            print(f"Partial save error: {e}")
    
    def get_extracted_data(self, session_id: str) -> Optional[Dict]:
        """Get extracted data for a session"""
        if session_id in self.sessions:
            context = self.sessions[session_id]
            return getattr(context, 'extracted_data', None)
        return None

# Factory function for easy instantiation
def create_modern_chat_manager(api_key: str = None) -> ModernChatManager:
    """Create a modern chat manager with all agents"""
    if not api_key:
        # Try to get from environment variables (includes Firebase Functions config)
        api_key = os.getenv('OPENAI_API_KEY', '').strip()
        print(f"API key loaded: {'yes' if api_key else 'no'}")
    return ModernChatManager(api_key)