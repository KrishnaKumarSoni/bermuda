#!/usr/bin/env python3

import sys
import os
sys.path.append('/Users/admin/Desktop/Dev/bermuda-01/api')

from conversation import create_conversation_manager

def test_off_topic():
    cm = create_conversation_manager()
    
    test_cases = [
        ("what's 2+2", True),
        ("pineapple", False),
        ("2+2", True),
        ("I love pizza", False),
        ("bananas", False),
        ("what are you", True),
        ("help me with something", True),
        ("weather today", True),
        ("math problem", True),
        ("tell me about yourself", True)
    ]
    
    print("Testing off-topic detection:")
    print("=" * 40)
    
    for message, expected in test_cases:
        result = cm.handle_off_topic_message(message)
        status = "✓" if result == expected else "✗"
        print(f"{status} '{message}' -> {result} (expected: {expected})")
    
    print("\nTesting actual bananas responses:")
    print("=" * 40)
    
    # Test the actual response generation
    mock_form = {
        "title": "Test Survey",
        "questions": [{"text": "What's your favorite color?", "type": "text", "enabled": True}]
    }
    
    for message in ["what's 2+2", "pineapple", "what are you"]:
        try:
            response, completed = cm.get_bot_response(message, [], mock_form, [], "test-session")
            print(f"'{message}' -> '{response}' (completed: {completed})")
        except Exception as e:
            print(f"'{message}' -> ERROR: {e}")

if __name__ == "__main__":
    test_off_topic()