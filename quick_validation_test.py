#!/usr/bin/env python3
"""
Quick validation test for key functionality after fixes
"""

import requests
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager

def test_api_endpoints():
    """Test key API endpoints"""
    print("🔌 Testing API Endpoints...")
    api_url = "https://us-central1-bermuda-01.cloudfunctions.net/api"
    
    tests = []
    
    # Test 1: Form metadata access (anonymous)
    try:
        response = requests.get(f"{api_url}/forms/test-form-123", timeout=10)
        tests.append(("Form metadata access", response.status_code == 200))
    except Exception as e:
        tests.append(("Form metadata access", False))
    
    # Test 2: Chat message endpoint
    try:
        response = requests.post(f"{api_url}/chat-message", 
                               json={"session_id": "test", "form_id": "test-form-123", "message": "Hello"},
                               timeout=10)
        tests.append(("Chat message endpoint", response.status_code == 200))
    except Exception as e:
        tests.append(("Chat message endpoint", False))
    
    # Test 3: Form inference endpoint (requires auth - should fail)
    try:
        response = requests.post(f"{api_url}/infer", 
                               json={"dump": "test"},
                               timeout=10)
        tests.append(("Form inference auth protection", response.status_code == 401))
    except Exception as e:
        tests.append(("Form inference auth protection", False))
    
    return tests

def test_frontend_access():
    """Test frontend form access and chat interface"""
    print("🌐 Testing Frontend Access...")
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    tests = []
    
    try:
        # Test 1: Form page loads
        driver.get("https://bermuda-01.web.app/f/test-form-123")
        wait = WebDriverWait(driver, 15)
        
        # Check if page loads properly
        if "Bermuda" in driver.title:
            tests.append(("Form page loads", True))
        else:
            tests.append(("Form page loads", False))
        
        # Test 2: Chat interface present
        try:
            chat_input = wait.until(EC.presence_of_element_located((By.ID, "chat-input")))
            tests.append(("Chat interface present", True))
            
            # Test 3: Chat input functional
            try:
                chat_input.send_keys("Test message")
                send_button = driver.find_element(By.ID, "send-message")
                send_button.click()
                time.sleep(3)
                
                # Check for response or loading indicator
                messages = driver.find_elements(By.XPATH, "//*[contains(@class, 'message')]")
                loading = driver.find_elements(By.ID, "chat-loading")
                
                tests.append(("Chat functionality works", len(messages) > 0 or len(loading) > 0))
                
            except Exception as e:
                tests.append(("Chat functionality works", False))
                
        except TimeoutException:
            tests.append(("Chat interface present", False))
            tests.append(("Chat functionality works", False))
        
        # Test 4: App page authentication
        driver.get("https://bermuda-01.web.app/app")
        time.sleep(3)
        
        page_content = driver.page_source.lower()
        auth_present = any(word in page_content for word in ["sign in", "login", "google", "auth"])
        tests.append(("App requires authentication", auth_present))
        
    except Exception as e:
        tests.append(("Frontend testing", False))
    
    finally:
        driver.quit()
    
    return tests

def main():
    """Run quick validation tests"""
    print("🚀 Quick Validation Test Suite")
    print("=" * 50)
    
    all_tests = []
    
    # API tests
    api_tests = test_api_endpoints()
    all_tests.extend(api_tests)
    
    # Frontend tests
    frontend_tests = test_frontend_access()
    all_tests.extend(frontend_tests)
    
    # Results
    print("\n" + "=" * 50)
    print("📊 VALIDATION RESULTS")
    print("=" * 50)
    
    passed = 0
    total = len(all_tests)
    
    for test_name, success in all_tests:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if success:
            passed += 1
    
    success_rate = (passed / total * 100) if total > 0 else 0
    
    print("=" * 50)
    print(f"✅ Passed: {passed}/{total}")
    print(f"📊 Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 90:
        print("🎉 STATUS: EXCELLENT - System working well!")
    elif success_rate >= 75:
        print("✅ STATUS: GOOD - Minor issues remain")
    elif success_rate >= 50:
        print("⚠️  STATUS: NEEDS WORK - Several issues")
    else:
        print("❌ STATUS: CRITICAL - Major problems")

if __name__ == "__main__":
    main()