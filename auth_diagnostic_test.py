#!/usr/bin/env python3
"""
Authentication Diagnostic Test
Diagnose the specific "Could not sign in" error
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def diagnose_auth_error():
    """Diagnose authentication error in detail"""
    
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1280,720")
    # Enable console logging
    chrome_options.add_argument("--enable-logging")
    chrome_options.add_argument("--log-level=0")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        print("🔍 Diagnosing Authentication Error...")
        
        # Go to app page
        print("📱 Loading app page...")
        driver.get("https://bermuda-01.web.app/app")
        time.sleep(3)
        
        # Check if page loads correctly
        print(f"✅ Page title: {driver.title}")
        print(f"✅ Current URL: {driver.current_url}")
        
        # Find Google sign-in button
        try:
            google_btn = driver.find_element(By.ID, "google-signin-btn")
            print(f"✅ Found Google sign-in button: '{google_btn.text}'")
            print(f"✅ Button enabled: {google_btn.is_enabled()}")
            print(f"✅ Button visible: {google_btn.is_displayed()}")
        except Exception as e:
            print(f"❌ Google sign-in button not found: {e}")
            return
        
        # Check for any existing error messages
        try:
            error_element = driver.find_element(By.ID, "auth-error")
            if error_element.is_displayed():
                print(f"⚠️  Existing error message: {error_element.text}")
            else:
                print("✅ No existing error messages")
        except:
            print("✅ No error element found")
        
        # Check console logs before clicking
        logs = driver.get_log('browser')
        if logs:
            print("📋 Console logs before auth attempt:")
            for log in logs[-5:]:  # Last 5 logs
                if log['level'] in ['SEVERE', 'ERROR']:
                    print(f"  ❌ {log['level']}: {log['message']}")
                elif 'firebase' in log['message'].lower():
                    print(f"  🔥 {log['level']}: {log['message']}")
        
        # Click the sign-in button
        print("🔐 Clicking Google sign-in button...")
        initial_window_count = len(driver.window_handles)
        
        google_btn.click()
        time.sleep(2)
        
        # Check for loading state
        try:
            # Wait for button text to change or popup to appear
            time.sleep(3)
            
            button_text = google_btn.text
            if "signing in" in button_text.lower():
                print("✅ Button shows loading state")
            else:
                print(f"⚠️  Button text unchanged: '{button_text}'")
        except:
            print("⚠️  Could not check button state")
        
        # Check for popup windows
        new_window_count = len(driver.window_handles)
        if new_window_count > initial_window_count:
            print("✅ Popup window opened")
            
            # Switch to popup and check URL
            popup_handle = [h for h in driver.window_handles if h != driver.current_window_handle][0]
            driver.switch_to.window(popup_handle)
            popup_url = driver.current_url
            print(f"📝 Popup URL: {popup_url}")
            
            if "google" in popup_url.lower() or "accounts.google.com" in popup_url:
                print("✅ Popup is Google authentication")
            else:
                print("❌ Popup is not Google authentication")
            
            # Close popup and return to main window
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            
        else:
            print("❌ No popup window opened")
            
            # Check if redirected instead
            current_url = driver.current_url
            if "google" in current_url.lower():
                print("✅ Redirected to Google authentication")
            else:
                print("❌ No redirect to Google authentication")
        
        # Wait and check for error messages
        time.sleep(5)
        
        try:
            error_element = driver.find_element(By.ID, "auth-error")
            if error_element.is_displayed():
                error_text = error_element.text
                print(f"❌ Error message displayed: '{error_text}'")
                
                # Analyze error type
                if "popup" in error_text.lower():
                    print("🔍 Issue: Popup blocked or closed")
                    print("💡 Solution: Enable popups for bermuda-01.web.app")
                elif "network" in error_text.lower():
                    print("🔍 Issue: Network connectivity problem")
                elif "cancelled" in error_text.lower():
                    print("🔍 Issue: User cancelled sign-in")
                else:
                    print("🔍 Issue: Generic authentication failure")
            else:
                print("✅ No error message displayed")
        except:
            print("✅ No error element found")
        
        # Check console logs after clicking
        logs = driver.get_log('browser')
        if logs:
            print("📋 Console logs after auth attempt:")
            recent_logs = [log for log in logs if 'timestamp' not in log or log['timestamp'] > time.time() * 1000 - 10000]
            for log in recent_logs[-10:]:  # Last 10 logs
                level_icon = "❌" if log['level'] in ['SEVERE', 'ERROR'] else "📝"
                print(f"  {level_icon} {log['level']}: {log['message']}")
        
        # Check Firebase configuration
        firebase_config_script = driver.execute_script("""
            try {
                // Check if Firebase is loaded
                if (typeof firebase !== 'undefined' || typeof window.firebaseApp !== 'undefined') {
                    return 'Firebase loaded';
                } else {
                    return 'Firebase not loaded';
                }
            } catch (e) {
                return 'Error checking Firebase: ' + e.message;
            }
        """)
        print(f"🔥 Firebase status: {firebase_config_script}")
        
        # Check network connectivity to Firebase
        print("🌐 Testing Firebase connectivity...")
        try:
            driver.get("https://www.gstatic.com/firebasejs/10.7.1/firebase-app.js")
            time.sleep(1)
            if "export" in driver.page_source or "firebase" in driver.page_source.lower():
                print("✅ Firebase CDN accessible")
            else:
                print("❌ Firebase CDN not accessible")
        except Exception as e:
            print(f"❌ Firebase CDN error: {e}")
        
    except Exception as e:
        print(f"❌ Diagnostic error: {e}")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    diagnose_auth_error()