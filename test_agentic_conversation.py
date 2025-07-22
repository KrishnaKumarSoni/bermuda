#!/usr/bin/env python3
"""
Test Agentic Conversation - Verify the new human-like conversation system
"""

import time
import json
import requests
import uuid
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def test_agentic_chat():
    """Test the new agentic conversation system"""
    
    print("🤖 TESTING AGENTIC CONVERSATION SYSTEM")
    
    api_url = "https://us-central1-bermuda-01.cloudfunctions.net/api"
    form_id = "test-form-123"
    session_id = f"agentic-test-{uuid.uuid4().hex[:8]}"
    
    print(f"\n1. Testing agent initiation (empty message)...")
    
    try:
        # Test agent initiation with empty message
        initiation_payload = {
            "session_id": session_id,
            "form_id": form_id,
            "message": "",  # Empty message to trigger agent initiation
            "device_data": {
                "screen_resolution": "1920x1080",
                "timezone_offset": -480,
                "platform": "MacIntel"
            }
        }
        
        response = requests.post(
            f"{api_url}/chat-message", 
            json=initiation_payload,
            headers={"Content-Type": "application/json"},
            timeout=20  # Longer timeout for new system
        )
        
        print(f"✅ Agent initiation status: {response.status_code}")
        if response.ok:
            data = response.json()
            bot_response = data.get('response', '')
            print(f"🤖 Agent greeting: {bot_response}")
            
            # Check if it's human-like
            human_indicators = [
                'hey' in bot_response.lower(),
                'hi' in bot_response.lower(),
                '😊' in bot_response or '!' in bot_response,
                len(bot_response) > 20,  # Not too short
                any(word in bot_response.lower() for word in ['what', 'pizza', 'favorite'])
            ]
            
            score = sum(human_indicators)
            print(f"📊 Human-like score: {score}/5")
            
            if score >= 3:
                print("✅ Agent greeting appears human-like!")
            else:
                print("❌ Agent greeting needs improvement")
                
        else:
            print(f"❌ Agent initiation failed: {response.text}")
            return
            
    except Exception as e:
        print(f"❌ Agent initiation error: {e}")
        return
    
    print(f"\n2. Testing conversation memory and intelligence...")
    
    # Test conversation flow with user responses
    conversation_tests = [
        {
            "user_input": "I love pepperoni pizza",
            "expect_keywords": ["cool", "nice", "awesome", "love", "pepperoni"],
            "description": "User answers first question"
        },
        {
            "user_input": "I eat it about twice a week",
            "expect_keywords": ["twice", "week", "often", "how"],
            "description": "User answers frequency question"
        },
        {
            "user_input": "Definitely thin crust",
            "expect_keywords": ["thin", "crust", "preference", "rate", "rating"],
            "description": "User answers preference question"
        }
    ]
    
    for i, test in enumerate(conversation_tests, 1):
        print(f"\n   Test {i}: {test['description']}")
        
        try:
            test_payload = {
                "session_id": session_id,
                "form_id": form_id,
                "message": test["user_input"],
                "device_data": {
                    "screen_resolution": "1920x1080",
                    "timezone_offset": -480,
                    "platform": "MacIntel"
                }
            }
            
            response = requests.post(
                f"{api_url}/chat-message", 
                json=test_payload,
                headers={"Content-Type": "application/json"},
                timeout=20
            )
            
            if response.ok:
                data = response.json()
                bot_response = data.get('response', '')
                print(f"   User: {test['user_input']}")
                print(f"   Bot: {bot_response}")
                
                # Check if bot shows memory/intelligence
                intelligence_indicators = [
                    len(bot_response) > 10,  # Substantial response
                    any(word in bot_response.lower() for word in ['cool', 'nice', 'awesome', 'great']),  # Acknowledgment
                    any(char in bot_response for char in ['!', '?', '😊']),  # Natural punctuation/emojis
                    not bot_response.lower().startswith('bananas'),  # Not off-topic response
                ]
                
                intelligence_score = sum(intelligence_indicators)
                print(f"   Intelligence score: {intelligence_score}/4")
                
                if '[END]' in bot_response:
                    print("   🏁 Conversation completed!")
                    
            else:
                print(f"   ❌ Test {i} failed: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Test {i} error: {e}")
            
        time.sleep(2)  # Small delay between tests
    
    print(f"\n3. Testing web interface with agentic system...")
    
    # Test via web interface
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1280,720")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        # Load chat interface
        chat_url = f"https://bermuda-01.web.app/f/{form_id}"
        print(f"🌐 Loading: {chat_url}")
        
        driver.get(chat_url)
        time.sleep(8)  # Give time for agent to initiate
        
        # Check for agent-initiated conversation
        try:
            messages_container = driver.find_element(By.ID, "chat-messages")
            flex_messages = messages_container.find_elements(By.CSS_SELECTOR, "div.flex")
            
            print(f"📨 Found {len(flex_messages)} messages")
            
            if len(flex_messages) >= 1:
                # Get the first message (should be agent greeting)
                first_message = flex_messages[0]
                message_text = first_message.get_attribute('textContent').strip()
                
                print(f"🤖 Agent's first message: '{message_text}'")
                
                # Check if it's a proper greeting
                if any(word in message_text.lower() for word in ['hey', 'hi', 'hello']):
                    print("✅ Agent properly initiated conversation!")
                else:
                    print("❌ Agent greeting doesn't seem natural")
            else:
                print("❌ No agent greeting found")
                
            # Test user interaction
            message_input = driver.find_element(By.ID, "message-input")
            send_btn = driver.find_element(By.ID, "send-btn")
            
            # Send test message
            test_message = "I absolutely love margherita pizza!"
            message_input.clear()
            message_input.send_keys(test_message)
            send_btn.click()
            
            print(f"💬 Sent: {test_message}")
            
            # Wait for response
            time.sleep(8)
            
            # Check for new messages
            updated_flex_messages = messages_container.find_elements(By.CSS_SELECTOR, "div.flex")
            
            if len(updated_flex_messages) > len(flex_messages):
                latest_message = updated_flex_messages[-1]
                latest_text = latest_message.get_attribute('textContent').strip()
                print(f"🤖 Agent response: '{latest_text}'")
                
                # Check if response is intelligent
                if any(word in latest_text.lower() for word in ['cool', 'awesome', 'nice', 'margherita']):
                    print("✅ Agent shows intelligence and memory!")
                else:
                    print("⚠️  Agent response could be more intelligent")
            else:
                print("❌ No agent response received")
                
        except Exception as e:
            print(f"❌ Web interface test error: {e}")
            
    finally:
        driver.quit()
    
    print(f"\n🎉 AGENTIC CONVERSATION TEST COMPLETE")

if __name__ == "__main__":
    test_agentic_chat()