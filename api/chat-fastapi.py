from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import json
import os
import requests
import asyncio
from typing import List, Dict
import uuid
from datetime import datetime

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory conversation storage (use Firebase in production)
conversations: Dict[str, List[Dict]] = {}

class ChatMessage(BaseModel):
    message: str
    conversation_id: str = None
    form_data: Dict = None  # Optional form context

class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    timestamp: str

def get_openai_response(messages: List[Dict], stream: bool = False):
    """Direct OpenAI API call - proven to work on Vercel"""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise HTTPException(status_code=500, detail="API key not configured")
    
    # Clean API key
    api_key = api_key.strip().replace('\n', '').replace('\r', '')
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        'model': 'gpt-4o-mini',
        'messages': messages,
        'temperature': 0.7,
        'max_tokens': 500,
        'stream': stream
    }
    
    response = requests.post(
        'https://api.openai.com/v1/chat/completions',
        headers=headers,
        json=payload,
        timeout=10,
        stream=stream
    )
    
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail=f"OpenAI API error: {response.status_code}")
    
    return response

def create_conversation_prompt(form_data: Dict = None):
    """Create system prompt for conversational form filling"""
    base_prompt = """You are a friendly form assistant helping users fill out a survey. 
Ask questions in a natural, conversational way. Keep responses concise and engaging.
Ask only ONE question at a time and wait for the user's response before continuing."""
    
    if form_data:
        questions = form_data.get('questions', [])
        form_title = form_data.get('title', 'Survey')
        
        questions_list = "\n".join([
            f"- {q['text']} (Type: {q['type']})"
            for q in questions if q.get('enabled', True)
        ])
        
        base_prompt += f"""

You are helping the user complete: "{form_title}"

Questions to ask:
{questions_list}

Start by greeting the user and introducing the survey, then ask the first question naturally."""
    
    return base_prompt

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(chat_request: ChatMessage):
    """Main chat endpoint - non-streaming for simplicity"""
    try:
        # Generate conversation ID if not provided
        conversation_id = chat_request.conversation_id or str(uuid.uuid4())
        
        # Initialize conversation if new
        if conversation_id not in conversations:
            conversations[conversation_id] = []
            
            # Add system prompt based on form context
            system_prompt = create_conversation_prompt(chat_request.form_data)
            conversations[conversation_id].append({
                "role": "system",
                "content": system_prompt
            })
        
        # Add user message to conversation
        conversations[conversation_id].append({
            "role": "user", 
            "content": chat_request.message
        })
        
        # Get AI response using direct OpenAI API
        response = get_openai_response(conversations[conversation_id])
        
        # Parse response
        response_data = response.json()
        if 'choices' not in response_data or not response_data['choices']:
            raise HTTPException(status_code=500, detail="Invalid OpenAI response")
        
        ai_message = response_data['choices'][0]['message']['content']
        
        # Add AI response to conversation
        conversations[conversation_id].append({
            "role": "assistant",
            "content": ai_message
        })
        
        return ChatResponse(
            response=ai_message,
            conversation_id=conversation_id,
            timestamp=datetime.now().isoformat()
        )
        
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="Request timeout")
    except requests.exceptions.ConnectionError:
        raise HTTPException(status_code=503, detail="Connection error")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/chat/{conversation_id}/history")
async def get_conversation_history(conversation_id: str):
    """Get conversation history"""
    if conversation_id not in conversations:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Return only user and assistant messages (exclude system)
    history = [
        msg for msg in conversations[conversation_id] 
        if msg['role'] in ['user', 'assistant']
    ]
    
    return {"conversation_id": conversation_id, "history": history}

@app.post("/api/chat/stream")
async def chat_stream(chat_request: ChatMessage):
    """Streaming chat endpoint for real-time responses"""
    async def generate_stream():
        try:
            conversation_id = chat_request.conversation_id or str(uuid.uuid4())
            
            # Initialize conversation if new
            if conversation_id not in conversations:
                conversations[conversation_id] = []
                system_prompt = create_conversation_prompt(chat_request.form_data)
                conversations[conversation_id].append({
                    "role": "system",
                    "content": system_prompt
                })
            
            # Add user message
            conversations[conversation_id].append({
                "role": "user",
                "content": chat_request.message
            })
            
            # Get streaming response
            response = get_openai_response(conversations[conversation_id], stream=True)
            
            full_response = ""
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        data = line[6:]
                        if data == '[DONE]':
                            break
                        try:
                            chunk = json.loads(data)
                            if 'choices' in chunk and chunk['choices']:
                                delta = chunk['choices'][0].get('delta', {})
                                content = delta.get('content', '')
                                if content:
                                    full_response += content
                                    yield f"data: {json.dumps({'content': content, 'conversation_id': conversation_id})}\n\n"
                        except json.JSONDecodeError:
                            continue
            
            # Add complete response to conversation
            conversations[conversation_id].append({
                "role": "assistant",
                "content": full_response
            })
            
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return StreamingResponse(generate_stream(), media_type="text/plain")

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "chat-api",
        "openai": "configured" if os.getenv('OPENAI_API_KEY') else "missing"
    }

# For Vercel deployment
app = app