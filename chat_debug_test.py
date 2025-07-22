#!/usr/bin/env python3
"""
Chat Debug Test - Focused test on chat functionality
"""

import time
import json
import requests
import uuid
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def test_chat_with_real_form():
    """Test chat functionality with a real form"""
    api_url = "https://us-central1-bermuda-01.cloudfunctions.net/api"
    
    print("🧪 TESTING CHAT WITH ACTUAL FORM")
    
    # First, let's check what forms are available by creating one via API
    print("\n1. Testing form creation via API...")
    
    # We need to create a real form first to test with
    # For now, let's test with the known test form
    form_id = "test-form-123"
    
    # Test form metadata
    try:
        response = requests.get(f"{api_url}/forms/{form_id}", timeout=10)
        print(f"✅ Form metadata status: {response.status_code}")
        if response.ok:
            form_data = response.json()
            print(f"📋 Form title: {form_data.get('title')}")
            print(f"📋 Questions: {len(form_data.get('questions', []))}")
        else:
            print(f"❌ Form metadata error: {response.text}")
            return
    except Exception as e:
        print(f"❌ Form metadata request failed: {e}")
        return
    
    # Test chat message flow
    print("\n2. Testing chat message API...")
    session_id = f"test-session-{uuid.uuid4().hex[:8]}"
    
    try:
        # Send initial message
        chat_payload = {
            "session_id": session_id,
            "form_id": form_id,
            "message": "Hello, I want to start this survey",
            "device_data": {
                "screen_resolution": "1920x1080",
                "timezone_offset": -480,
                "platform": "MacIntel"
            }
        }
        
        response = requests.post(
            f"{api_url}/chat-message", 
            json=chat_payload,
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        
        print(f"✅ Chat API status: {response.status_code}")
        if response.ok:
            data = response.json()
            print(f"🤖 Bot response: {data.get('response', 'No response')[:100]}...")
            print(f"🏷️  Tag: {data.get('tag', 'None')}")
        else:
            print(f"❌ Chat API error: {response.text}")
            
    except Exception as e:
        print(f"❌ Chat API request failed: {e}")
    
    # Test with Selenium
    print("\n3. Testing chat via web interface...")
    
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1280,720")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        # Load chat interface directly
        chat_url = f"https://bermuda-01.web.app/f/{form_id}"
        print(f"🌐 Loading: {chat_url}")
        
        driver.get(chat_url)
        time.sleep(5)  # Give more time for loading
        
        # Check for chat interface
        try:
            chat_container = driver.find_element(By.ID, "chat-container")
            message_input = driver.find_element(By.ID, "message-input")
            send_btn = driver.find_element(By.ID, "send-btn")
            
            print("✅ Chat interface loaded successfully")
            
            # Check for form title
            try:
                title_element = driver.find_element(By.ID, "chat-form-title")
                print(f"📋 Form title displayed: {title_element.text}")
            except Exception as e:
                print(f"⚠️  Could not get form title: {e}")
            
            # Check for initial messages
            try:
                messages = driver.find_elements(By.CLASS_NAME, "message")
                print(f"📨 Initial messages: {len(messages)}")
            except Exception:
                print("📨 No initial messages found")
            
            # Send a test message
            test_message = "I love pepperoni pizza and eat it weekly"
            message_input.clear()
            message_input.send_keys(test_message)
            
            print(f"💬 Sending test message: {test_message}")
            send_btn.click()
            
            # Wait for response
            time.sleep(8)  # Give more time for API response
            
            # Check for messages again
            try:
                messages_container = driver.find_element(By.ID, "chat-messages")
                messages = messages_container.find_elements(By.CSS_SELECTOR, "div[class*='flex']")
                print(f"📨 Total messages after send: {len(messages)}")
                
                # Get message text
                for i, msg in enumerate(messages):
                    try:
                        msg_text = msg.get_attribute('textContent')
                        print(f"   Message {i+1}: {msg_text[:50]}...")
                    except Exception:
                        print(f"   Message {i+1}: Could not get text")
                
            except Exception as e:
                print(f"❌ Could not check messages: {e}")
            
            # Check for errors
            try:
                error_element = driver.find_element(By.ID, "chat-error")
                if error_element.is_displayed():
                    print(f"❌ Chat error: {error_element.text}")
                else:
                    print("✅ No chat errors displayed")
            except Exception:
                print("✅ No error element found")
            
            # Check browser console
            logs = driver.get_log('browser')
            errors = [log for log in logs if log['level'] in ['SEVERE', 'ERROR']]
            if errors:
                print(f"❌ Browser console errors: {len(errors)}")
                for error in errors[:3]:
                    print(f"   {error['message']}")
            else:
                print("✅ No severe browser console errors")
                
        except Exception as e:
            print(f"❌ Chat interface error: {e}")
            
            # Check if it's showing error page
            try:
                page_source = driver.page_source
                if "Form Not Found" in page_source:
                    print("📋 Form not found error displayed")
                elif "Error Loading Form" in page_source:
                    print("📋 Error loading form displayed")
                else:
                    print("📋 Unknown page state")
            except Exception:
                pass
        
    finally:
        driver.quit()

if __name__ == "__main__":
    test_chat_with_real_form()