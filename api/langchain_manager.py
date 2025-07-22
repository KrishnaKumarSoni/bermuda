"""
Lightweight LangChain implementation for Bermuda following YAML specifications
Optimized for cloud functions deployment with minimal dependencies
"""

import os
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timezone

# Lightweight LangChain imports - only what we need
try:
    from langchain_openai import ChatOpenAI
    from langchain.memory import ConversationBufferMemory
    from langchain.chains import ConversationChain, LLMChain
    from langchain.prompts import PromptTemplate
    from langchain.schema import BaseMessage, HumanMessage, AIMessage
    LANGCHAIN_AVAILABLE = True
except ImportError as e:
    print(f"LangChain import warning: {e}")
    LANGCHAIN_AVAILABLE = False


class LightweightLangChainManager:
    """Lightweight LangChain manager optimized for Firebase Functions"""
    
    def __init__(self):
        self.api_key = self._get_openai_key()
        self.llm = None
        self.chains = {}
        self.memories = {}  # Session-based memory storage
        self._initialize_llm()
        self._setup_chains()
    
    def _get_openai_key(self) -> Optional[str]:
        """Get OpenAI API key from environment"""
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            print("Warning: OPENAI_API_KEY not configured")
            return None
        return api_key.strip()
    
    def _initialize_llm(self):
        """Initialize lightweight LLM for cloud functions"""
        if not LANGCHAIN_AVAILABLE or not self.api_key:
            print("LangChain or API key not available, falling back")
            return
            
        try:
            # Minimal LLM setup optimized for cloud functions
            self.llm = ChatOpenAI(
                model="gpt-4o-mini",  # As specified in YAML
                temperature=0.7,
                max_tokens=1000,
                timeout=30,
                max_retries=2,
                openai_api_key=self.api_key
            )
            print("LangChain LLM initialized successfully")
        except Exception as e:
            print(f"LLM initialization error: {e}")
            self.llm = None
    
    def _setup_chains(self):
        """Setup the three main chains as specified in YAML"""
        if not self.llm:
            return
            
        try:
            # 1. Inference Chain for form creation
            self._setup_inference_chain()
            
            # 2. Conversation Chain template (instantiated per session)
            self._setup_conversation_template()
            
            # 3. Extraction Chain for data extraction
            self._setup_extraction_chain()
            
            print("LangChain chains initialized successfully")
        except Exception as e:
            print(f"Chain setup error: {e}")
    
    def _setup_inference_chain(self):
        """Setup inference chain following YAML template"""
        inference_prompt = PromptTemplate(
            input_variables=["dump"],
            template="""You are an expert form inferrer. From this dump: {dump}

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
        )
        
        self.chains['inference'] = LLMChain(
            llm=self.llm,
            prompt=inference_prompt,
            output_key="result"
        )
    
    def _setup_conversation_template(self):
        """Setup conversation chain template following YAML specs"""
        # Store template for per-session instantiation
        self.conversation_template = PromptTemplate(
            input_variables=["form_title", "questions_json", "history", "input"],
            template="""You are a warm, friendly human conversationalist (like a curious friend) gathering info for this form: {form_title}. Act naturally—use emojis, casual language, empathy. Never sound robotic. Ask one question at a time, weave in follow-ups if needed.

Required data to collect (questions and demographics, in order): {questions_json}

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
{history}

User's latest message: {input}

###
Chain-of-Thought (reason step-by-step, output ONLY here):
Step 1: Analyze input - Extract any answers, detect skips/conflicts/vagueness/off-topic/INVALID RESPONSES. Compare to memory for consistency (prioritize latest if conflict).
Step 2: Validate response - Check if answer makes sense for question type. If asking about pizza toppings and they say "water", mark as INVALID. If asking yes/no and they say random word, mark INVALID.
Step 3: Track progress - List collected vs. required data (e.g., Question 1: collected 'Latte' via bucketizing; Demographics: pending). Identify next gap.
Step 4: Handle edges - If INVALID: Plan clarification follow-up. If off-topic: Plan "bananas". If vague/no-fit: Plan follow-up (max 2 per question). If skip insisted: Mark [SKIP].
Step 5: Plan response - If INVALID response, ask for clarification. Else, acknowledge + next question/follow-up. If all done: Thanks + [END].
Step 6: Self-critique - Is this on-topic, natural, unbiased? Is response validation working correctly? If not, adjust.

Response (output ONLY the bot's message here, nothing else):"""
        )
    
    def _setup_extraction_chain(self):
        """Setup extraction chain following YAML template"""
        extraction_prompt = PromptTemplate(
            input_variables=["transcript", "questions_json"],
            template="""From this chat transcript: {transcript}

Map to structured form data: {questions_json}

Rules:
- Extract answers accurately, using types (e.g., parse 'three' to 3 for number).
- Bucketize MCQ/yes_no/rating without bias: Map semantically to options (e.g., 'capp' → 'Latte' if closest; 'alien brew' → 'other: alien brew' if no fit). For text: Verbatim. For number: Numeric parse.
- CRITICAL - Invalid responses: If user gave nonsensical answers (e.g., "water" for pizza toppings), mark as 'invalid_response_given' NOT as a valid answer. Only extract meaningful responses.
- Resolve edges: Prioritize latest for conflicts; mark 'skipped' if insisted; 'unclear' if vague; 'invalid_response_given' if completely nonsensical.
- Output JSON: {{'questions': {{q_text: answer}}, 'demographics': {{}}, 'partial': true/false, 'notes': [any edges, e.g., 'Conflict resolved', 'Invalid response filtered']}}

###
Chain-of-Thought:
Step 1: Scan transcript for relevant snippets per question.
Step 2: Validate responses - Check if answers make logical sense for question context. Filter out obviously invalid responses.
Step 3: Apply bucketizing/validation (list options, find best match; if no fit, note 'other'; if invalid, note 'invalid_response_given').
Step 4: Handle edges (e.g., skips → 'skipped'; multi-answers → split; nonsense → 'invalid_response_given').
Step 5: Self-critique: Is extraction complete/accurate? Are invalid responses properly filtered? If partial, flag gaps.

Output (JSON only):"""
        )
        
        self.chains['extraction'] = LLMChain(
            llm=self.llm,
            prompt=extraction_prompt,
            output_key="result"
        )
    
    def get_session_memory(self, session_id: str):
        """Get or create ConversationBufferMemory for session"""
        if not LANGCHAIN_AVAILABLE:
            return None
            
        if session_id not in self.memories:
            try:
                self.memories[session_id] = ConversationBufferMemory(
                    memory_key="history",
                    input_key="input",
                    output_key="response",
                    return_messages=False,
                    k=10  # Last 10 messages as specified in YAML
                )
            except Exception as e:
                print(f"Memory creation error: {e}")
                return None
        return self.memories[session_id]
    
    def get_conversation_chain(self, session_id: str, form_title: str, questions_json: str):
        """Get ConversationChain for session with form context"""
        if not self.llm or not hasattr(self, 'conversation_template'):
            return None
            
        try:
            memory = self.get_session_memory(session_id)
            
            # Create contextual prompt with form data
            contextual_prompt = PromptTemplate(
                input_variables=["history", "input"],
                template=self.conversation_template.template.format(
                    form_title=form_title,
                    questions_json=questions_json,
                    history="{history}",
                    input="{input}"
                )
            )
            
            return ConversationChain(
                llm=self.llm,
                prompt=contextual_prompt,
                memory=memory,
                input_key="input",
                output_key="response"
            )
        except Exception as e:
            print(f"Conversation chain creation error: {e}")
            return None
    
    def infer_form_structure(self, text_dump: str) -> Dict:
        """Use inference chain to create form from text dump"""
        print(f"🔍 Starting inference for dump: {text_dump[:100]}...")
        print(f"🔧 LangChain available: {LANGCHAIN_AVAILABLE}")
        print(f"🔑 API key available: {bool(self.api_key)}")
        print(f"🤖 LLM initialized: {bool(self.llm)}")
        print(f"⛓️ Inference chain available: {bool(self.chains.get('inference'))}")
        
        if not self.chains.get('inference'):
            print("⚠️ No inference chain, using fallback")
            return self._fallback_inference(text_dump)
            
        try:
            print("🚀 Running LangChain inference...")
            result = self.chains['inference'].run(dump=text_dump)
            print(f"📤 Raw LangChain result: {result[:200]}...")
            
            # Clean and parse JSON result
            result = result.strip()
            if result.startswith('```json'):
                result = result.replace('```json', '').replace('```', '').strip()
            elif result.startswith('```'):
                result = result.replace('```', '').strip()
            
            parsed_result = json.loads(result)
            print(f"✅ Parsed LangChain result: {parsed_result}")
            
            # Validate result has required fields
            if not parsed_result.get('questions') or len(parsed_result['questions']) == 0:
                print("⚠️ LangChain result missing questions, using fallback")
                return self._fallback_inference(text_dump)
                
            return parsed_result
        except Exception as e:
            print(f"❌ Inference chain error: {e}")
            print(f"🔧 Error type: {type(e).__name__}")
            return self._fallback_inference(text_dump)
    
    def get_bot_response(self, user_message: str, session_id: str, 
                        form_title: str, questions_json: str) -> Tuple[str, bool]:
        """Get bot response using ConversationChain"""
        conversation_chain = self.get_conversation_chain(session_id, form_title, questions_json)
        
        if not conversation_chain:
            return self._fallback_response(user_message, form_title), False
            
        try:
            response = conversation_chain.predict(input=user_message)
            
            # Check for completion tags
            is_completed = '[END]' in response
            response = response.replace('[END]', '').strip()
            
            return response, is_completed
        except Exception as e:
            print(f"Conversation chain error: {e}")
            return self._fallback_response(user_message, form_title), False
    
    def extract_structured_data(self, transcript: List[Dict], questions_json: str) -> Dict:
        """Use extraction chain to extract structured data"""
        if not self.chains.get('extraction'):
            return self._fallback_extraction(transcript, questions_json)
            
        try:
            # Format transcript
            transcript_text = "\n".join([
                f"{'User' if msg.get('role') == 'user' else 'Bot'}: {msg.get('text', '')}"
                for msg in transcript
            ])
            
            result = self.chains['extraction'].run(
                transcript=transcript_text,
                questions_json=questions_json
            )
            
            # Clean and parse JSON result
            result = result.strip()
            if result.startswith('```json'):
                result = result.replace('```json', '').replace('```', '').strip()
            elif result.startswith('```'):
                result = result.replace('```', '').strip()
                
            return json.loads(result)
        except Exception as e:
            print(f"Extraction chain error: {e}")
            return self._fallback_extraction(transcript, questions_json)
    
    def _fallback_inference(self, text_dump: str) -> Dict:
        """Improved fallback inference when LangChain unavailable"""
        print(f"Using fallback inference for: {text_dump[:100]}...")
        
        # Simple heuristic-based inference
        dump_lower = text_dump.lower()
        
        # Generate title based on content
        title = "Survey"
        if "food" in dump_lower or "cook" in dump_lower or "cuisine" in dump_lower:
            title = "Food & Cooking Survey"
        elif "movie" in dump_lower or "film" in dump_lower:
            title = "Movie Preferences Survey"
        elif "music" in dump_lower or "song" in dump_lower:
            title = "Music Survey"
        elif "product" in dump_lower or "service" in dump_lower:
            title = "Product Feedback Survey"
        elif "travel" in dump_lower or "vacation" in dump_lower:
            title = "Travel Survey"
        elif "work" in dump_lower or "job" in dump_lower:
            title = "Work Experience Survey"
        
        # Generate questions based on content
        questions = []
        
        # Look for question patterns and question words
        if "favorite" in dump_lower and ("food" in dump_lower or "cuisine" in dump_lower):
            questions.append({"text": "What's your favorite cuisine?", "type": "text", "enabled": True})
        
        if "cook" in dump_lower and ("often" in dump_lower or "how" in dump_lower):
            questions.append({"text": "How often do you cook at home?", "type": "multiple_choice", 
                            "options": ["Never", "Rarely", "Sometimes", "Often", "Daily"], "enabled": True})
        
        if "rate" in dump_lower and ("skill" in dump_lower or "1-5" in dump_lower):
            questions.append({"text": "Rate your cooking skills", "type": "rating", 
                            "options": ["1", "2", "3", "4", "5"], "enabled": True})
        
        # Add generic questions if no specific ones found
        if not questions:
            if "?" in text_dump:
                # Extract questions from the dump
                sentences = text_dump.split(".")
                for sentence in sentences:
                    if "?" in sentence:
                        question_text = sentence.strip()
                        if len(question_text) > 5:
                            q_type = "text"
                            if "rate" in question_text.lower() and any(num in question_text for num in ["1-5", "1-10"]):
                                q_type = "rating"
                                options = ["1", "2", "3", "4", "5"] if "1-5" in question_text else ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
                                questions.append({"text": question_text, "type": q_type, "options": options, "enabled": True})
                            else:
                                questions.append({"text": question_text, "type": q_type, "enabled": True})
            
            # Fallback to generic questions
            if not questions:
                questions = [
                    {"text": "What are your thoughts on this topic?", "type": "text", "enabled": True},
                    {"text": "How would you rate your overall experience?", "type": "rating", 
                     "options": ["1", "2", "3", "4", "5"], "enabled": True}
                ]
        
        return {
            "title": title,
            "questions": questions[:5]  # Limit to 5 questions
        }
    
    def _fallback_response(self, user_message: str, form_title: str) -> str:
        """Fallback response when LangChain unavailable"""
        return f"thanks for sharing! tell me more about {form_title.lower()}?"
    
    def _fallback_extraction(self, transcript: List[Dict], questions_json: str) -> Dict:
        """Fallback extraction when LangChain unavailable"""
        return {
            "questions": {},
            "demographics": {},
            "partial": True,
            "notes": ["Fallback extraction - LangChain unavailable"]
        }
    
    def cleanup_session(self, session_id: str):
        """Clean up session memory to prevent memory leaks"""
        if session_id in self.memories:
            del self.memories[session_id]


# Global manager instance
langchain_manager = None

def get_langchain_manager() -> LightweightLangChainManager:
    """Get or create global LangChain manager instance"""
    global langchain_manager
    if langchain_manager is None:
        langchain_manager = LightweightLangChainManager()
    return langchain_manager