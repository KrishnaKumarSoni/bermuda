#!/usr/bin/env python3
"""
Test Message Flow - Check if messages are properly displayed
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def test_message_display():
    """Test if messages are properly displayed in chat"""
    
    print("🧪 TESTING MESSAGE DISPLAY")
    
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1280,720")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        # Load chat interface
        chat_url = "https://bermuda-01.web.app/f/test-form-123"
        print(f"🌐 Loading: {chat_url}")
        
        driver.get(chat_url)
        time.sleep(5)
        
        # Check initial state
        try:
            messages_container = driver.find_element(By.ID, "chat-messages")
            print("✅ Chat messages container found")
            
            # Check initial content
            initial_html = messages_container.get_attribute('innerHTML')
            print(f"📨 Initial container HTML length: {len(initial_html)}")
            
            if len(initial_html.strip()) > 100:  # Should have welcome message
                print("✅ Container has content (likely welcome message)")
            else:
                print("❌ Container appears empty")
                print(f"Container content: {initial_html}")
            
            # Look for message elements more specifically
            message_divs = messages_container.find_elements(By.CSS_SELECTOR, "div")
            print(f"📨 Found {len(message_divs)} div elements in messages container")
            
            # Check for actual message content
            for i, div in enumerate(message_divs):
                try:
                    text_content = div.get_attribute('textContent').strip()
                    inner_html = div.get_attribute('innerHTML')
                    print(f"   Div {i+1}: textContent='{text_content}', innerHTML length={len(inner_html)}")
                    if text_content:
                        print(f"      Content: {text_content}")
                except Exception as e:
                    print(f"   Div {i+1}: Error getting content - {e}")
            
            # Send a message to test the flow
            message_input = driver.find_element(By.ID, "message-input")
            send_btn = driver.find_element(By.ID, "send-btn")
            
            test_message = "Test message for debugging"
            message_input.clear()
            message_input.send_keys(test_message)
            
            print(f"💬 Sending test message: {test_message}")
            send_btn.click()
            
            # Wait and check again
            time.sleep(6)
            
            # Re-check container
            updated_html = messages_container.get_attribute('innerHTML')
            print(f"📨 Updated container HTML length: {len(updated_html)}")
            
            # Check for new messages
            updated_message_divs = messages_container.find_elements(By.CSS_SELECTOR, "div")
            print(f"📨 Found {len(updated_message_divs)} div elements after send")
            
            # Look for flex class messages specifically  
            flex_messages = messages_container.find_elements(By.CSS_SELECTOR, "div.flex")
            print(f"📨 Found {len(flex_messages)} flex message elements")
            
            for i, msg in enumerate(flex_messages):
                try:
                    text_content = msg.get_attribute('textContent').strip()
                    classes = msg.get_attribute('class')
                    print(f"   Flex message {i+1}: classes='{classes}'")
                    print(f"      Content: '{text_content}'")
                    
                    # Check inner paragraphs
                    paragraphs = msg.find_elements(By.TAG_NAME, "p")
                    for j, p in enumerate(paragraphs):
                        p_text = p.get_attribute('textContent').strip()
                        print(f"         Paragraph {j+1}: '{p_text}'")
                        
                except Exception as e:
                    print(f"   Flex message {i+1}: Error - {e}")
            
            # Check for JavaScript errors that might prevent rendering
            logs = driver.get_log('browser')
            js_errors = [log for log in logs if log['level'] == 'SEVERE' and 'javascript' in log['message'].lower()]
            
            if js_errors:
                print(f"❌ JavaScript errors found: {len(js_errors)}")
                for error in js_errors:
                    print(f"   {error['message']}")
            else:
                print("✅ No JavaScript errors found")
            
        except Exception as e:
            print(f"❌ Error accessing chat interface: {e}")
            
            # Dump page source for debugging
            page_source = driver.page_source
            if len(page_source) > 1000:
                print("📄 Page loaded successfully")
                # Look for key elements in source
                if 'chat-messages' in page_source:
                    print("✅ chat-messages element exists in source")
                if 'message-input' in page_source:
                    print("✅ message-input element exists in source")
                if 'send-btn' in page_source:
                    print("✅ send-btn element exists in source")
            else:
                print("❌ Page may not have loaded properly")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    test_message_display()