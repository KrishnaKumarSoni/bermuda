#!/usr/bin/env python3
"""
Final Comprehensive Test Summary
Consolidates all testing results and provides overall system assessment
"""

import json
import requests
from datetime import datetime

def test_core_api_functionality():
    """Test core API endpoints quickly"""
    print("🔌 Testing Core API Functionality...")
    
    api_url = "https://us-central1-bermuda-01.cloudfunctions.net/api"
    tests = []
    
    # Test 1: Form inference (requires auth - should return 401)
    try:
        response = requests.post(f"{api_url}/infer", 
                               json={"dump": "Test survey about favorite foods"}, 
                               timeout=10)
        tests.append(("Form inference auth protection", response.status_code == 401))
    except:
        tests.append(("Form inference auth protection", False))
    
    # Test 2: Chat message (should work)
    try:
        response = requests.post(f"{api_url}/chat-message", 
                               json={
                                   "session_id": "test-session",
                                   "form_id": "test-form-123",
                                   "message": "Hello, I'm ready to start"
                               }, 
                               timeout=15)
        tests.append(("Chat messaging works", response.status_code == 200))
        
        if response.status_code == 200:
            data = response.json()
            has_response = "response" in data and len(data["response"]) > 0
            tests.append(("Chat returns meaningful response", has_response))
        else:
            tests.append(("Chat returns meaningful response", False))
    except:
        tests.append(("Chat messaging works", False))
        tests.append(("Chat returns meaningful response", False))
    
    # Test 3: Form metadata access (should work)
    try:
        response = requests.get(f"{api_url}/forms/test-form-123", timeout=10)
        tests.append(("Form metadata access", response.status_code == 200))
    except:
        tests.append(("Form metadata access", False))
    
    # Test 4: Data extraction (should work)
    try:
        sample_transcript = [
            {"role": "assistant", "text": "What's your favorite food?"},
            {"role": "user", "text": "I love pizza"}
        ]
        response = requests.post(f"{api_url}/extract", 
                               json={
                                   "session_id": "test-extract",
                                   "transcript": sample_transcript,
                                   "questions_json": {"questions": [{"text": "What's your favorite food?", "type": "text"}]}
                               }, 
                               timeout=10)
        tests.append(("Data extraction works", response.status_code == 200))
    except:
        tests.append(("Data extraction works", False))
    
    # Test 5: Off-topic detection
    try:
        response = requests.post(f"{api_url}/chat-message", 
                               json={
                                   "session_id": f"off-topic-{int(datetime.now().timestamp())}",
                                   "form_id": "test-form-123",
                                   "message": "What's the weather like today?"
                               }, 
                               timeout=15)
        if response.status_code == 200:
            data = response.json()
            response_text = data.get("response", "").lower()
            tests.append(("Off-topic detection works", "bananas" in response_text))
        else:
            tests.append(("Off-topic detection works", False))
    except:
        tests.append(("Off-topic detection works", False))
    
    return tests

def test_frontend_accessibility():
    """Test frontend access without selenium"""
    print("🌐 Testing Frontend Accessibility...")
    
    tests = []
    base_url = "https://bermuda-01.web.app"
    
    # Test 1: Landing page
    try:
        response = requests.get(base_url, timeout=10)
        tests.append(("Landing page accessible", response.status_code == 200))
        
        if response.status_code == 200:
            content = response.text.lower()
            has_bermuda = "bermuda" in content
            tests.append(("Landing page has correct content", has_bermuda))
        else:
            tests.append(("Landing page has correct content", False))
    except:
        tests.append(("Landing page accessible", False))
        tests.append(("Landing page has correct content", False))
    
    # Test 2: App page
    try:
        response = requests.get(f"{base_url}/app", timeout=10)
        tests.append(("App page accessible", response.status_code == 200))
    except:
        tests.append(("App page accessible", False))
    
    # Test 3: Form page routing
    try:
        response = requests.get(f"{base_url}/f/test-form-123", timeout=10)
        tests.append(("Form page routing works", response.status_code == 200))
        
        if response.status_code == 200:
            content = response.text.lower()
            has_chat = "chat" in content or "message" in content
            tests.append(("Form page contains chat interface", has_chat))
        else:
            tests.append(("Form page contains chat interface", False))
    except:
        tests.append(("Form page routing works", False))
        tests.append(("Form page contains chat interface", False))
    
    return tests

def load_previous_test_results():
    """Load results from previous test files"""
    previous_results = []
    
    # Load authentication test results
    try:
        with open('authentication_test_results.json', 'r') as f:
            auth_data = json.load(f)
            auth_summary = auth_data.get('summary', {})
            previous_results.append({
                'test_suite': 'Authentication Tests',
                'total_tests': auth_summary.get('total_tests', 0),
                'passed_tests': auth_summary.get('passed_tests', 0),
                'success_rate': auth_summary.get('success_rate', 0)
            })
    except FileNotFoundError:
        pass
    
    return previous_results

def generate_final_comprehensive_summary():
    """Generate final comprehensive test summary"""
    print("🚀 Final Comprehensive Test Summary")
    print("=" * 80)
    print(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 System URL: https://bermuda-01.web.app")
    print(f"🔌 API URL: https://us-central1-bermuda-01.cloudfunctions.net/api")
    print("=" * 80)
    
    all_test_results = []
    
    # Run current tests
    api_tests = test_core_api_functionality()
    frontend_tests = test_frontend_accessibility()
    
    all_test_results.extend(api_tests)
    all_test_results.extend(frontend_tests)
    
    # Load previous test results
    previous_results = load_previous_test_results()
    
    # Calculate overall results
    total_current_tests = len(all_test_results)
    passed_current_tests = len([t for t in all_test_results if t[1]])
    current_success_rate = (passed_current_tests / total_current_tests * 100) if total_current_tests > 0 else 0
    
    # Display current test results
    print("\n🔬 CURRENT TEST RESULTS")
    print("-" * 40)
    
    for test_name, success in all_test_results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nCurrent Tests: {passed_current_tests}/{total_current_tests} passed ({current_success_rate:.1f}%)")
    
    # Display previous test summaries
    if previous_results:
        print("\n📊 PREVIOUS TEST SUMMARIES")
        print("-" * 40)
        
        for result in previous_results:
            print(f"• {result['test_suite']}: {result['passed_tests']}/{result['total_tests']} passed ({result['success_rate']:.1f}%)")
    
    # Overall system assessment
    print("\n" + "=" * 80)
    print("🏁 FINAL SYSTEM ASSESSMENT")
    print("=" * 80)
    
    # Key functionality matrix
    key_functions = {
        "🔐 Authentication": any("auth" in t[0].lower() for t in all_test_results if t[1]),
        "💬 Chat Functionality": any("chat" in t[0].lower() for t in all_test_results if t[1]),
        "📝 Form Access": any("form" in t[0].lower() and "access" in t[0].lower() for t in all_test_results if t[1]),
        "🔌 API Endpoints": any("api" in t[0].lower() or "endpoint" in t[0].lower() for t in all_test_results if t[1]),
        "🌐 Frontend Hosting": any("page" in t[0].lower() and "accessible" in t[0].lower() for t in all_test_results if t[1]),
        "⚠️  Error Handling": any("off-topic" in t[0].lower() or "detection" in t[0].lower() for t in all_test_results if t[1])
    }
    
    print("Key System Functions:")
    for function, working in key_functions.items():
        status = "✅ Working" if working else "❌ Issues"
        print(f"  {function}: {status}")
    
    # Overall status determination
    working_functions = sum(key_functions.values())
    total_functions = len(key_functions)
    system_health = (working_functions / total_functions * 100) if total_functions > 0 else 0
    
    print(f"\n📈 System Health: {working_functions}/{total_functions} core functions working ({system_health:.1f}%)")
    
    # Final verdict
    print("\n🎯 FINAL VERDICT:")
    if system_health >= 85 and current_success_rate >= 80:
        print("🎉 PRODUCTION READY - System is working excellently!")
        print("   ✓ All core functionality operational")
        print("   ✓ Authentication and security working")
        print("   ✓ Chat conversations flowing naturally")
        print("   ✓ Frontend and backend integrated properly")
        verdict = "EXCELLENT"
    elif system_health >= 70 and current_success_rate >= 65:
        print("✅ GOOD - System is functional with minor issues")
        print("   ✓ Most core functionality working")
        print("   ⚠️  Some edge cases need attention")
        print("   ✓ Ready for user testing")
        verdict = "GOOD"
    elif system_health >= 50:
        print("⚠️  NEEDS WORK - System has significant issues")
        print("   ⚠️  Several core functions not working properly")
        print("   ❌ Not ready for production use")
        verdict = "NEEDS_WORK"
    else:
        print("❌ CRITICAL - System requires major fixes")
        print("   ❌ Core functionality broken")
        print("   ❌ Extensive development needed")
        verdict = "CRITICAL"
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    
    if verdict == "EXCELLENT":
        print("   • Deploy to production")
        print("   • Start user testing and feedback collection")
        print("   • Monitor performance and usage metrics")
        print("   • Plan feature enhancements")
    elif verdict == "GOOD":
        print("   • Address remaining test failures")
        print("   • Conduct additional edge case testing")
        print("   • Begin limited user testing")
        print("   • Monitor chat conversation quality")
    elif verdict == "NEEDS_WORK":
        print("   • Fix core functionality issues")
        print("   • Re-run comprehensive test suite")
        print("   • Address authentication and routing problems")
        print("   • Delay production deployment")
    else:
        print("   • Major development work required")
        print("   • Fix fundamental system issues")
        print("   • Complete system architecture review")
        print("   • Extensive testing needed")
    
    print("=" * 80)
    
    # Save comprehensive summary
    summary_data = {
        "test_timestamp": datetime.now().isoformat(),
        "current_tests": all_test_results,
        "previous_results": previous_results,
        "system_health": system_health,
        "current_success_rate": current_success_rate,
        "key_functions": key_functions,
        "verdict": verdict,
        "total_current_tests": total_current_tests,
        "passed_current_tests": passed_current_tests
    }
    
    with open('final_comprehensive_summary.json', 'w') as f:
        json.dump(summary_data, f, indent=2)
    
    return summary_data

if __name__ == "__main__":
    generate_final_comprehensive_summary()