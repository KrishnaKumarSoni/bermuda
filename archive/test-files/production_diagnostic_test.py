#!/usr/bin/env python3
"""
Production Diagnostic Test Suite
Comprehensive testing of production deployment to identify specific issues
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
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

class ProductionDiagnostic:
    def __init__(self):
        self.production_url = "https://bermuda-01.web.app"
        self.api_url = "https://us-central1-bermuda-01.cloudfunctions.net/api"
        self.driver = None
        
    def setup_browser(self):
        """Setup Chrome browser for testing"""
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1280,720")
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)
        
    def cleanup(self):
        """Cleanup browser resources"""
        if self.driver:
            self.driver.quit()
            
    def test_api_endpoints_directly(self):
        """Test API endpoints directly with HTTP requests"""
        print("\n🔌 TESTING API ENDPOINTS DIRECTLY")
        
        # Test health endpoint
        try:
            response = requests.get(f"{self.api_url}/health", timeout=10)
            print(f"✅ Health endpoint: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ Health endpoint failed: {e}")
            
        # Test form metadata (should fail for non-existent form)
        try:
            response = requests.get(f"{self.api_url}/forms/test-form-123", timeout=10)
            print(f"📊 Form metadata test: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ Form metadata failed: {e}")
            
        # Test chat message endpoint
        try:
            chat_data = {
                "session_id": f"test-{uuid.uuid4().hex[:8]}",
                "form_id": "test-form-123",
                "message": "Hello, I want to start the survey"
            }
            response = requests.post(f"{self.api_url}/chat-message", 
                                   json=chat_data, 
                                   headers={"Content-Type": "application/json"},
                                   timeout=10)
            print(f"💬 Chat message test: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ Chat message failed: {e}")
            
    def test_landing_page(self):
        """Test landing page and authentication"""
        print("\n🏠 TESTING LANDING PAGE")
        
        self.driver.get(f"{self.production_url}/app")
        time.sleep(3)
        
        # Check if landing page loads
        try:
            landing_page = self.driver.find_element(By.ID, "landing-page")
            if landing_page.is_displayed():
                print("✅ Landing page loads correctly")
            else:
                print("❌ Landing page not displayed")
        except Exception as e:
            print(f"❌ Landing page element not found: {e}")
            
        # Check for Google sign-in button
        try:
            google_btn = self.driver.find_element(By.ID, "google-signin-btn")
            print(f"✅ Google sign-in button found: '{google_btn.text}'")
        except Exception as e:
            print(f"❌ Google sign-in button not found: {e}")
            
        # Check console for errors
        logs = self.driver.get_log('browser')
        errors = [log for log in logs if log['level'] == 'SEVERE']
        if errors:
            print(f"❌ Browser console errors: {len(errors)}")
            for error in errors[:3]:  # Show first 3 errors
                print(f"   {error['message']}")
        else:
            print("✅ No severe browser console errors")
            
    def test_form_creation_flow(self):
        """Test form creation flow (requires manual auth)"""
        print("\n📝 TESTING FORM CREATION FLOW")
        
        # Navigate to app
        self.driver.get(f"{self.production_url}/app")
        time.sleep(3)
        
        # Check if we need to authenticate
        try:
            google_btn = self.driver.find_element(By.ID, "google-signin-btn")
            print("🔐 Authentication required - manual step needed")
            print("👤 Please sign in with Google to continue form creation test")
            
            # Wait for potential authentication (30 seconds)
            print("⏳ Waiting 30 seconds for authentication...")
            time.sleep(30)
            
        except Exception:
            print("✅ Already authenticated or auth not required")
            
        # Check for form creation interface
        try:
            dump_textarea = self.driver.find_element(By.ID, "dump-textarea")
            create_btn = self.driver.find_element(By.ID, "create-form-btn")
            print("✅ Form creation interface found")
            
            # Test form creation
            test_dump = "Customer feedback survey about coffee preferences: favorite type, frequency of visits, preferred time of day"
            dump_textarea.clear()
            dump_textarea.send_keys(test_dump)
            
            # Wait for button to enable
            time.sleep(1)
            if create_btn.is_enabled():
                print("✅ Create form button enabled with valid input")
                
                # Click create (but don't wait for full process)
                create_btn.click()
                print("🚀 Form creation initiated")
                
                # Check for loading state
                time.sleep(2)
                try:
                    loading = self.driver.find_element(By.CLASS_NAME, "loading")
                    print("✅ Loading state displayed")
                except Exception:
                    print("⚠️  Loading state not found")
                    
            else:
                print("❌ Create form button not enabled")
                
        except Exception as e:
            print(f"❌ Form creation interface not found: {e}")
            
    def test_chat_interface(self):
        """Test chat interface with a test form"""
        print("\n💬 TESTING CHAT INTERFACE")
        
        # Try to access a test form (will likely fail but tests routing)
        test_form_url = f"{self.production_url}/f/test-form-123"
        self.driver.get(test_form_url)
        time.sleep(3)
        
        # Check if chat interface loads
        try:
            chat_container = self.driver.find_element(By.ID, "chat-container")
            message_input = self.driver.find_element(By.ID, "message-input")
            send_btn = self.driver.find_element(By.ID, "send-btn")
            
            print("✅ Chat interface elements found")
            
            # Test message sending
            test_message = "Hello, I want to start the survey"
            message_input.clear()
            message_input.send_keys(test_message)
            
            if send_btn.is_enabled():
                print("✅ Send button enabled")
                send_btn.click()
                
                # Wait for response
                time.sleep(5)
                
                # Check for bot response
                try:
                    messages = self.driver.find_elements(By.CLASS_NAME, "message")
                    print(f"✅ Found {len(messages)} messages in chat")
                    
                    if len(messages) >= 2:  # User message + bot response
                        print("✅ Bot response received")
                    else:
                        print("❌ No bot response received")
                        
                except Exception as e:
                    print(f"❌ Could not find messages: {e}")
                    
            else:
                print("❌ Send button not enabled")
                
        except Exception as e:
            print(f"❌ Chat interface not found: {e}")
            # Check if it's a form not found error
            try:
                error_msg = self.driver.find_element(By.CLASS_NAME, "error-message")
                print(f"📋 Error message: {error_msg.text}")
            except Exception:
                print("❌ No error message displayed")
                
    def test_dashboard_functionality(self):
        """Test dashboard and form management"""
        print("\n📊 TESTING DASHBOARD FUNCTIONALITY")
        
        # Navigate to dashboard
        self.driver.get(f"{self.production_url}/app")
        time.sleep(3)
        
        # Look for dashboard elements
        try:
            # Check for forms list or empty state
            forms_list = self.driver.find_element(By.ID, "forms-list")
            print("✅ Forms list container found")
            
            # Check for create new form button
            create_new_btn = self.driver.find_element(By.ID, "create-new-form-btn")
            print("✅ Create new form button found")
            
            # Check for existing forms
            try:
                form_items = self.driver.find_elements(By.CLASS_NAME, "form-item")
                print(f"📋 Found {len(form_items)} existing forms")
                
                if len(form_items) == 0:
                    empty_state = self.driver.find_element(By.ID, "empty-state")
                    print("✅ Empty state displayed correctly")
                    
            except Exception as e:
                print(f"⚠️  Forms list check: {e}")
                
        except Exception as e:
            print(f"❌ Dashboard elements not found: {e}")
            
    def run_full_diagnostic(self):
        """Run complete production diagnostic"""
        print("🔍 PRODUCTION DIAGNOSTIC TEST SUITE")
        print("=====================================")
        
        # Test API endpoints first (no browser needed)
        self.test_api_endpoints_directly()
        
        # Setup browser for frontend tests
        self.setup_browser()
        
        try:
            # Test frontend components
            self.test_landing_page()
            self.test_form_creation_flow()
            self.test_chat_interface()
            self.test_dashboard_functionality()
            
        finally:
            self.cleanup()
            
        print("\n📋 DIAGNOSTIC COMPLETE")
        print("Check output above for specific issues to fix")

if __name__ == "__main__":
    diagnostic = ProductionDiagnostic()
    diagnostic.run_full_diagnostic()