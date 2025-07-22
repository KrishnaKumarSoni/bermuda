#!/usr/bin/env python3
"""
Simple manual authentication test to debug page loading
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def test_page_loading():
    """Simple test to see what's actually on the page"""
    
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1280,720")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        print("🌐 Loading Bermuda landing page...")
        driver.get("https://bermuda-01.web.app")
        time.sleep(5)  # Wait longer for page to fully load
        
        print(f"✅ Page title: {driver.title}")
        print(f"✅ Current URL: {driver.current_url}")
        
        # Check page source
        page_source = driver.page_source
        print(f"✅ Page source length: {len(page_source)} characters")
        
        # Look for specific elements
        elements_to_check = [
            ("google-signin-btn", "Google Sign-in button by ID"),
            ("landing-page", "Landing page container"),
            ("auth-error", "Auth error element"),
        ]
        
        for element_id, description in elements_to_check:
            try:
                element = driver.find_element(By.ID, element_id)
                print(f"✅ Found {description}: {element.tag_name}")
                if element.text:
                    print(f"    Text: '{element.text}'")
                if element.is_displayed():
                    print(f"    Visible: Yes")
                else:
                    print(f"    Visible: No")
            except Exception as e:
                print(f"❌ {description} not found: {str(e)}")
        
        # Check for text content
        text_searches = [
            "Sign in with Google",
            "Bermuda", 
            "Conversational forms",
            "google-signin-btn"
        ]
        
        for text in text_searches:
            if text.lower() in page_source.lower():
                print(f"✅ Found text: '{text}'")
            else:
                print(f"❌ Missing text: '{text}'")
        
        # Check for JavaScript errors
        logs = driver.get_log('browser')
        if logs:
            print("\n🔍 Browser console logs:")
            for log in logs:
                print(f"  {log['level']}: {log['message']}")
        else:
            print("✅ No browser console errors")
        
        # Take a screenshot
        try:
            driver.save_screenshot("debug_screenshot.png")
            print("✅ Screenshot saved as debug_screenshot.png")
        except:
            print("❌ Could not save screenshot")
        
        # Test navigation to /app
        print("\n🔗 Testing navigation to /app...")
        driver.get("https://bermuda-01.web.app/app")
        time.sleep(3)
        
        print(f"✅ App page URL: {driver.current_url}")
        
        # Check if we can find the sign-in button on /app
        try:
            signin_btn = driver.find_element(By.ID, "google-signin-btn")
            print(f"✅ Found Google sign-in button on /app page")
            print(f"    Text: '{signin_btn.text}'")
            print(f"    Visible: {signin_btn.is_displayed()}")
            print(f"    Enabled: {signin_btn.is_enabled()}")
        except Exception as e:
            print(f"❌ Google sign-in button not found on /app: {str(e)}")
        
    except Exception as e:
        print(f"❌ Error during test: {str(e)}")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    test_page_loading()