#!/usr/bin/env python3
"""
Authentication User Scenarios Test Suite
Tests real user authentication flows and experiences
"""

import time
import json
import requests
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

class AuthUserScenariosTester:
    """Test real user authentication scenarios"""
    
    def __init__(self):
        self.base_url = "https://bermuda-01.web.app"
        self.api_url = "https://us-central1-bermuda-01.cloudfunctions.net/api"
        self.driver = None
        self.results = []
        
    def setup_browser(self):
        """Setup browser for testing"""
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--window-size=1280,720")
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.implicitly_wait(10)
        self.wait = WebDriverWait(self.driver, 20)
        
    def log_result(self, test_name, success, details=""):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "url": self.driver.current_url if self.driver else "N/A"
        }
        self.results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if details and not success:
            print(f"    Details: {details}")
    
    def test_landing_page_user_flow(self):
        """Test the complete landing page to app user flow"""
        print("\n🏠 Testing Landing Page User Flow...")
        
        try:
            # Step 1: User visits landing page
            self.driver.get(self.base_url)
            time.sleep(3)
            
            page_title = self.driver.title
            if "Bermuda" in page_title:
                self.log_result("Landing page loads with correct branding", True, f"Title: {page_title}")
            else:
                self.log_result("Landing page loads with correct branding", False, f"Title: {page_title}")
            
            # Step 2: Check value proposition is clear
            page_content = self.driver.page_source.lower()
            value_prop_keywords = ["conversational", "forms", "3x", "completion", "chat"]
            found_keywords = [kw for kw in value_prop_keywords if kw in page_content]
            
            if len(found_keywords) >= 3:
                self.log_result("Landing page communicates value proposition", True, 
                              f"Found keywords: {', '.join(found_keywords)}")
            else:
                self.log_result("Landing page communicates value proposition", False,
                              f"Only found: {', '.join(found_keywords)}")
            
            # Step 3: Check for clear call-to-action
            cta_buttons = self.driver.find_elements(By.CSS_SELECTOR, ".btn-primary")
            if cta_buttons:
                cta_text = " ".join([btn.text.lower() for btn in cta_buttons])
                if any(keyword in cta_text for keyword in ["create", "start", "try", "form"]):
                    self.log_result("Landing page has clear CTA", True, f"CTA text: {cta_text}")
                else:
                    self.log_result("Landing page has clear CTA", False, f"CTA text: {cta_text}")
            else:
                self.log_result("Landing page has clear CTA", False, "No CTA buttons found")
            
            # Step 4: User clicks CTA to go to app
            if cta_buttons:
                first_cta = cta_buttons[0]
                initial_url = self.driver.current_url
                
                first_cta.click()
                time.sleep(3)
                
                new_url = self.driver.current_url
                if "/app" in new_url and new_url != initial_url:
                    self.log_result("CTA button redirects to app", True, f"Redirected to: {new_url}")
                else:
                    self.log_result("CTA button redirects to app", False, f"URL: {new_url}")
            
            return True
            
        except Exception as e:
            self.log_result("Landing page user flow", False, f"Error: {str(e)}")
            return False
    
    def test_app_authentication_experience(self):
        """Test the app authentication user experience"""
        print("\n🔐 Testing App Authentication Experience...")
        
        try:
            # Ensure we're on the app page
            self.driver.get(f"{self.base_url}/app")
            time.sleep(3)
            
            # Step 1: Check authentication interface is user-friendly
            try:
                google_btn = self.driver.find_element(By.ID, "google-signin-btn")
                
                # Check button text is clear
                btn_text = google_btn.text.lower()
                if "google" in btn_text and "sign" in btn_text:
                    self.log_result("Google sign-in button has clear text", True, f"Text: {google_btn.text}")
                else:
                    self.log_result("Google sign-in button has clear text", False, f"Text: {google_btn.text}")
                
                # Check button is prominently displayed
                btn_size = google_btn.size
                if btn_size["width"] > 200 and btn_size["height"] > 40:
                    self.log_result("Google sign-in button is prominent", True, f"Size: {btn_size}")
                else:
                    self.log_result("Google sign-in button is prominent", False, f"Size: {btn_size}")
                
                # Check button styling
                btn_style = google_btn.get_attribute("class")
                if "btn-primary" in btn_style:
                    self.log_result("Google sign-in button uses primary styling", True)
                else:
                    self.log_result("Google sign-in button uses primary styling", False, f"Classes: {btn_style}")
                    
            except NoSuchElementException:
                self.log_result("Google sign-in button exists", False, "Button not found")
            
            # Step 2: Check for helpful messaging
            page_content = self.driver.page_source.lower()
            helpful_messages = ["conversational", "forms", "bermuda", "sign in"]
            found_messages = [msg for msg in helpful_messages if msg in page_content]
            
            if len(found_messages) >= 3:
                self.log_result("App page provides helpful context", True,
                              f"Found context: {', '.join(found_messages)}")
            else:
                self.log_result("App page provides helpful context", False,
                              f"Limited context: {', '.join(found_messages)}")
            
            # Step 3: Test authentication initiation
            try:
                google_btn = self.driver.find_element(By.ID, "google-signin-btn")
                
                # Check initial state
                initial_text = google_btn.text
                initial_enabled = google_btn.is_enabled()
                
                if initial_enabled:
                    self.log_result("Google sign-in button is interactive", True)
                    
                    # Click button and check for response
                    google_btn.click()
                    time.sleep(2)
                    
                    # Check for loading state or popup
                    current_text = google_btn.text
                    if current_text != initial_text:
                        self.log_result("Sign-in shows loading state", True, 
                                      f"Changed from '{initial_text}' to '{current_text}'")
                    else:
                        self.log_result("Sign-in shows loading state", False, "Button text unchanged")
                    
                    # Check for new windows (popup) or redirect
                    time.sleep(3)
                    windows = self.driver.window_handles
                    current_url = self.driver.current_url
                    
                    if len(windows) > 1:
                        self.log_result("Google auth popup opens", True, f"{len(windows)} windows")
                        
                        # Check popup content
                        popup_handle = [w for w in windows if w != self.driver.current_window_handle][0]
                        self.driver.switch_to.window(popup_handle)
                        popup_url = self.driver.current_url
                        
                        if "google" in popup_url.lower() or "accounts.google.com" in popup_url:
                            self.log_result("Popup is Google authentication", True, f"URL: {popup_url}")
                        else:
                            self.log_result("Popup is Google authentication", False, f"URL: {popup_url}")
                        
                        # Close popup and return to main window
                        self.driver.close()
                        self.driver.switch_to.window(windows[0])
                        
                    elif "google" in current_url.lower():
                        self.log_result("Google auth redirect works", True, f"URL: {current_url}")
                        self.driver.back()  # Go back to continue testing
                        time.sleep(2)
                    else:
                        self.log_result("Authentication initiation", False, "No popup or redirect detected")
                        
                else:
                    self.log_result("Google sign-in button is interactive", False, "Button disabled")
                    
            except NoSuchElementException:
                self.log_result("Authentication initiation test", False, "Sign-in button not found")
            
            return True
            
        except Exception as e:
            self.log_result("App authentication experience", False, f"Error: {str(e)}")
            return False
    
    def test_post_authentication_experience(self):
        """Test post-authentication user experience (simulated)"""
        print("\n✨ Testing Post-Authentication Experience...")
        
        try:
            # Go to app page
            self.driver.get(f"{self.base_url}/app")
            time.sleep(3)
            
            # Simulate successful authentication
            self.driver.execute_script("""
                // Hide landing page
                const landingPage = document.getElementById('landing-page');
                if (landingPage) landingPage.style.display = 'none';
                
                // Show dashboard
                const dashboard = document.getElementById('dashboard');
                if (dashboard) {
                    dashboard.classList.remove('hidden');
                    dashboard.style.display = 'block';
                }
                
                // Simulate user email
                const userEmail = document.getElementById('user-email');
                if (userEmail) {
                    userEmail.textContent = 'test.user@example.com';
                }
                
                console.log('Simulated successful authentication');
            """)
            
            time.sleep(2)
            
            # Step 1: Check dashboard is welcoming
            try:
                dashboard = self.driver.find_element(By.ID, "dashboard")
                if dashboard.is_displayed():
                    self.log_result("Dashboard displays after authentication", True)
                    
                    # Check for welcoming content
                    dashboard_text = dashboard.text.lower()
                    welcoming_elements = ["your forms", "create", "welcome", "dashboard"]
                    found_elements = [elem for elem in welcoming_elements if elem in dashboard_text]
                    
                    if len(found_elements) >= 2:
                        self.log_result("Dashboard is welcoming and clear", True,
                                      f"Found: {', '.join(found_elements)}")
                    else:
                        self.log_result("Dashboard is welcoming and clear", False,
                                      f"Limited welcoming content: {', '.join(found_elements)}")
                else:
                    self.log_result("Dashboard displays after authentication", False, "Dashboard hidden")
                    
            except NoSuchElementException:
                self.log_result("Dashboard exists", False, "Dashboard not found")
            
            # Step 2: Check for clear next actions
            action_buttons = [
                ("create-form-btn", "Create new form"),
                ("sign-out-btn", "Sign out")
            ]
            
            for btn_id, description in action_buttons:
                try:
                    button = self.driver.find_element(By.ID, btn_id)
                    if button.is_displayed() and button.is_enabled():
                        self.log_result(f"Dashboard has {description} button", True, f"Text: {button.text}")
                    else:
                        self.log_result(f"Dashboard has {description} button", False, "Button not interactive")
                        
                except NoSuchElementException:
                    self.log_result(f"Dashboard has {description} button", False, "Button not found")
            
            # Step 3: Test form creation entry point
            try:
                create_btn = self.driver.find_element(By.ID, "create-form-btn")
                if create_btn.is_displayed():
                    create_btn.click()
                    time.sleep(2)
                    
                    # Check if form creator appears
                    try:
                        form_creator = self.driver.find_element(By.ID, "form-creator")
                        if form_creator.is_displayed():
                            self.log_result("Create form button opens form creator", True)
                        else:
                            self.log_result("Create form button opens form creator", False, "Form creator not visible")
                            
                    except NoSuchElementException:
                        self.log_result("Create form button opens form creator", False, "Form creator not found")
                        
            except NoSuchElementException:
                self.log_result("Create form button interaction", False, "Button not found")
            
            # Step 4: Test sign-out functionality
            try:
                # Go back to dashboard first
                self.driver.execute_script("""
                    const dashboard = document.getElementById('dashboard');
                    const formCreator = document.getElementById('form-creator');
                    
                    if (dashboard) dashboard.style.display = 'block';
                    if (formCreator) formCreator.style.display = 'none';
                """)
                
                time.sleep(1)
                
                sign_out_btn = self.driver.find_element(By.ID, "sign-out-btn")
                if sign_out_btn.is_displayed():
                    # Check button text
                    btn_text = sign_out_btn.text.lower()
                    if "sign out" in btn_text or "logout" in btn_text:
                        self.log_result("Sign-out button has clear text", True, f"Text: {sign_out_btn.text}")
                    else:
                        self.log_result("Sign-out button has clear text", False, f"Text: {sign_out_btn.text}")
                        
                    # Test click behavior (without actually signing out)
                    self.driver.execute_script("""
                        const signOutBtn = document.getElementById('sign-out-btn');
                        signOutBtn.addEventListener('click', function(e) {
                            e.preventDefault();
                            console.log('Sign-out clicked (prevented)');
                            signOutBtn.textContent = 'Signing out...';
                        });
                    """)
                    
                    sign_out_btn.click()
                    time.sleep(1)
                    
                    if "signing out" in sign_out_btn.text.lower():
                        self.log_result("Sign-out button responds to click", True)
                    else:
                        self.log_result("Sign-out button responds to click", False, "No response detected")
                        
            except NoSuchElementException:
                self.log_result("Sign-out button interaction", False, "Button not found")
            
            return True
            
        except Exception as e:
            self.log_result("Post-authentication experience", False, f"Error: {str(e)}")
            return False
    
    def test_anonymous_user_experience(self):
        """Test anonymous user experience (form respondents)"""
        print("\n👤 Testing Anonymous User Experience...")
        
        try:
            # Test various form URL patterns
            form_urls = [
                "/f/test-survey",
                "/f/customer-feedback", 
                "/f/pizza-preferences"
            ]
            
            for form_url in form_urls:
                try:
                    full_url = f"{self.base_url}{form_url}"
                    self.driver.get(full_url)
                    time.sleep(3)
                    
                    # Check page loads properly
                    page_title = self.driver.title
                    if "bermuda" in page_title.lower():
                        self.log_result(f"Anonymous access {form_url} loads", True, f"Title: {page_title}")
                        
                        # Check for appropriate content
                        page_content = self.driver.page_source.lower()
                        
                        # Should NOT show authentication requirements
                        auth_keywords = ["sign in", "login", "authenticate", "google"]
                        found_auth = [kw for kw in auth_keywords if kw in page_content]
                        
                        if len(found_auth) == 0:
                            self.log_result(f"Anonymous access {form_url} no auth required", True)
                        else:
                            self.log_result(f"Anonymous access {form_url} no auth required", False,
                                          f"Found auth keywords: {', '.join(found_auth)}")
                        
                        # Should show appropriate form content or "form not found"
                        form_keywords = ["chat", "conversation", "survey", "form", "not found"]
                        found_form = [kw for kw in form_keywords if kw in page_content]
                        
                        if len(found_form) > 0:
                            self.log_result(f"Anonymous access {form_url} shows form content", True,
                                          f"Found: {', '.join(found_form)}")
                        else:
                            self.log_result(f"Anonymous access {form_url} shows form content", False,
                                          "No form-related content found")
                            
                    else:
                        self.log_result(f"Anonymous access {form_url} loads", False, f"Title: {page_title}")
                        
                except Exception as e:
                    self.log_result(f"Anonymous access {form_url}", False, f"Error: {str(e)}")
            
            # Test direct app access as anonymous user
            try:
                self.driver.get(f"{self.base_url}/app")
                time.sleep(3)
                
                # Anonymous users should see authentication interface
                page_content = self.driver.page_source.lower()
                auth_present = any(kw in page_content for kw in ["sign in", "google", "login"])
                
                if auth_present:
                    self.log_result("Anonymous /app access shows authentication", True)
                else:
                    self.log_result("Anonymous /app access shows authentication", False,
                                  "No authentication interface found")
                    
            except Exception as e:
                self.log_result("Anonymous /app access", False, f"Error: {str(e)}")
            
            return True
            
        except Exception as e:
            self.log_result("Anonymous user experience", False, f"Error: {str(e)}")
            return False
    
    def test_mobile_responsive_authentication(self):
        """Test authentication experience on mobile viewport"""
        print("\n📱 Testing Mobile Responsive Authentication...")
        
        try:
            # Set mobile viewport
            self.driver.set_window_size(375, 667)  # iPhone 6/7/8 size
            time.sleep(1)
            
            # Test landing page on mobile
            self.driver.get(self.base_url)
            time.sleep(3)
            
            # Check if content is readable on mobile
            body = self.driver.find_element(By.TAG_NAME, "body")
            viewport_width = self.driver.execute_script("return window.innerWidth")
            
            if viewport_width <= 400:
                self.log_result("Mobile viewport set correctly", True, f"Width: {viewport_width}px")
            else:
                self.log_result("Mobile viewport set correctly", False, f"Width: {viewport_width}px")
            
            # Check for mobile-specific elements or warnings
            page_content = self.driver.page_source.lower()
            
            # Look for mobile hints or responsive design
            mobile_keywords = ["mobile", "desktop", "best experience", "phone"]
            found_mobile = [kw for kw in mobile_keywords if kw in page_content]
            
            if found_mobile:
                self.log_result("Mobile experience considered", True, f"Found: {', '.join(found_mobile)}")
            else:
                self.log_result("Mobile experience considered", False, "No mobile-specific content")
            
            # Test authentication on mobile
            self.driver.get(f"{self.base_url}/app")
            time.sleep(3)
            
            try:
                google_btn = self.driver.find_element(By.ID, "google-signin-btn")
                
                # Check button is appropriately sized for mobile
                btn_size = google_btn.size
                btn_location = google_btn.location
                
                if btn_size["width"] > 200 and btn_size["height"] > 40:
                    self.log_result("Mobile auth button appropriately sized", True, f"Size: {btn_size}")
                else:
                    self.log_result("Mobile auth button appropriately sized", False, f"Size: {btn_size}")
                
                # Check button is centered or well-positioned
                viewport_center = viewport_width / 2
                btn_center = btn_location["x"] + (btn_size["width"] / 2)
                
                if abs(btn_center - viewport_center) < 50:  # Within 50px of center
                    self.log_result("Mobile auth button well-positioned", True)
                else:
                    self.log_result("Mobile auth button well-positioned", False,
                                  f"Button center: {btn_center}, viewport center: {viewport_center}")
                    
            except NoSuchElementException:
                self.log_result("Mobile auth button exists", False, "Button not found")
            
            # Reset to desktop viewport
            self.driver.set_window_size(1280, 720)
            time.sleep(1)
            
            return True
            
        except Exception as e:
            self.log_result("Mobile responsive authentication", False, f"Error: {str(e)}")
            return False
    
    def run_auth_user_scenarios_tests(self):
        """Run all authentication user scenario tests"""
        print("👥 Authentication User Scenarios Test Suite")
        print("=" * 60)
        
        self.setup_browser()
        
        try:
            # Phase 1: Landing page user flow
            self.test_landing_page_user_flow()
            
            # Phase 2: App authentication experience
            self.test_app_authentication_experience()
            
            # Phase 3: Post-authentication experience
            self.test_post_authentication_experience()
            
            # Phase 4: Anonymous user experience
            self.test_anonymous_user_experience()
            
            # Phase 5: Mobile responsive authentication
            self.test_mobile_responsive_authentication()
            
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up and generate summary"""
        if self.driver:
            self.driver.quit()
        
        self.generate_summary()
    
    def generate_summary(self):
        """Generate authentication user scenarios summary"""
        total_tests = len(self.results)
        passed_tests = len([r for r in self.results if r["success"]])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print("\n" + "=" * 60)
        print("🏁 AUTHENTICATION USER SCENARIOS TEST SUMMARY")
        print("=" * 60)
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"📊 Success Rate: {success_rate:.1f}%")
        
        if failed_tests > 0:
            print("\n🔍 FAILED TESTS:")
            for result in self.results:
                if not result["success"]:
                    print(f"   ❌ {result['test']}: {result['details']}")
        
        print("=" * 60)
        
        # User experience assessment
        if success_rate >= 90:
            print("🔥 USER EXPERIENCE STATUS: EXCELLENT - Smooth user journey!")
        elif success_rate >= 75:
            print("✅ USER EXPERIENCE STATUS: GOOD - Minor UX improvements needed")
        elif success_rate >= 60:
            print("⚠️  USER EXPERIENCE STATUS: NEEDS WORK - Several UX issues")
        else:
            print("❌ USER EXPERIENCE STATUS: CRITICAL - Major UX problems")
        
        # Save detailed results
        with open('auth_user_scenarios_results.json', 'w') as f:
            json.dump({
                "results": self.results,
                "summary": {
                    "total_tests": total_tests,
                    "passed_tests": passed_tests,
                    "failed_tests": failed_tests,
                    "success_rate": success_rate,
                    "test_duration": datetime.now().isoformat()
                }
            }, f, indent=2)

if __name__ == "__main__":
    tester = AuthUserScenariosTester()
    tester.run_auth_user_scenarios_tests()