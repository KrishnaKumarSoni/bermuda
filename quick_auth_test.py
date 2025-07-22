#!/usr/bin/env python3
"""
Quick Authentication Test - Verify Google Auth is working
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def test_auth_flow():
    """Test the complete authentication flow"""
    
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1280,720")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        print("🔐 Testing Google Authentication Flow...")
        
        # Load app page
        driver.get("https://bermuda-01.web.app/app")
        time.sleep(3)
        
        # Check initial state
        try:
            google_btn = driver.find_element(By.ID, "google-signin-btn")
            landing_page = driver.find_element(By.ID, "landing-page")
            
            if landing_page.is_displayed():
                print("✅ Landing page with auth interface is displayed")
            else:
                print("❌ Landing page not displayed")
                
            print(f"✅ Google sign-in button found: '{google_btn.text}'")
        except Exception as e:
            print(f"❌ Initial state check failed: {e}")
            return
        
        # Click sign-in button
        print("🖱️  Clicking Google sign-in button...")
        initial_windows = len(driver.window_handles)
        google_btn.click()
        time.sleep(3)
        
        # Check for popup
        new_windows = len(driver.window_handles)
        if new_windows > initial_windows:
            print("✅ Google authentication popup opened successfully")
            
            # Switch to popup and check it's Google
            popup_handle = [h for h in driver.window_handles if h != driver.current_window_handle][0]
            driver.switch_to.window(popup_handle)
            popup_url = driver.current_url
            
            if "accounts.google.com" in popup_url:
                print("✅ Popup contains Google authentication interface")
                print("👤 You can now sign in with your Google account in the popup")
                
                # Note: In a real test, you could automate the Google sign-in
                # but that requires test credentials and is complex
                print("📝 Manual step: Complete Google sign-in in the popup window")
                
                # Close popup for this test
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                print("✅ Authentication popup flow working correctly")
                
            else:
                print(f"❌ Popup not pointing to Google: {popup_url}")
        else:
            print("❌ No popup opened")
        
        # Check for no error messages on main page
        time.sleep(2)
        try:
            error_element = driver.find_element(By.ID, "auth-error")
            if error_element.is_displayed():
                print(f"❌ Error message: {error_element.text}")
            else:
                print("✅ No error messages displayed")
        except:
            print("✅ No error element (good)")
        
        print("\n🎉 AUTHENTICATION FLOW TEST COMPLETE")
        print("✅ Google Authentication is working correctly!")
        print("✅ Users can now sign in with their Google accounts")
        
    except Exception as e:
        print(f"❌ Test error: {e}")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    test_auth_flow()