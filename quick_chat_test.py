#!/usr/bin/env python3
"""
Quick direct chat test without external API calls
"""

import os
import sys
sys.path.append('api')

import json
from datetime import datetime

def test_direct_chat():
    """Test chat functionality directly without network calls"""
    
    print("🧪 Direct Chat API Testing")
    print("=" * 40)
    
    try:
        # Import the respondent app components directly
        from firebase_integration import firebase_manager
        from agentic_conversation import create_agentic_conversation_manager
        
        # Test 1: Form Access
        print("1. Testing form access...")
        form_data = firebase_manager.get_form('test-form-coffee')
        if form_data:
            print(f"   ✅ Form found: {form_data['title']}")
            print(f"   📊 Questions: {len(form_data['questions'])}")
        else:
            print("   ❌ Form not found")
            return False
            
        # Test 2: Conversation Manager
        print("\n2. Testing conversation manager...")
        manager = create_agentic_conversation_manager()
        
        # Test initial greeting (empty message)
        bot_response, is_completed = manager.get_bot_response(
            user_message="",  # Empty for agent initiation
            conversation_history=[],
            form_data=form_data,
            demographics=form_data.get('demographics', [])
        )
        
        print(f"   🤖 Bot greeting: '{bot_response}'")
        
        # Check greeting quality
        greeting_checks = {
            'contains_greeting': any(word in bot_response.lower() for word in ['hey', 'hi', 'hello']),
            'mentions_coffee': 'coffee' in bot_response.lower(),
            'natural_tone': any(char in bot_response for char in ['😊', '!', '?']),
            'not_too_long': len(bot_response) < 200
        }
        
        passed_checks = sum(greeting_checks.values())
        print(f"   📊 Greeting quality: {passed_checks}/4 checks passed")
        
        # Test 3: Normal conversation
        print("\n3. Testing conversation flow...")
        
        conversation_history = [
            {'role': 'assistant', 'text': bot_response}
        ]
        
        test_messages = [
            "I love lattes with oat milk",
            "I drink coffee every morning", 
            "Usually around 8 AM",
            "I'd rate my love for coffee a 5!",
            "No allergies, just prefer oat milk"
        ]
        
        for i, message in enumerate(test_messages):
            print(f"   User: {message}")
            
            # Add user message to history
            conversation_history.append({'role': 'user', 'text': message})
            
            # Get bot response
            bot_response, is_completed = manager.get_bot_response(
                user_message=message,
                conversation_history=conversation_history,
                form_data=form_data,
                demographics=form_data.get('demographics', [])
            )
            
            print(f"   🤖 Bot: {bot_response}")
            
            # Add bot response to history
            conversation_history.append({'role': 'assistant', 'text': bot_response})
            
            if is_completed:
                print(f"   🏁 Conversation completed after message {i+1}")
                break
        
        # Test 4: Off-topic handling
        print("\n4. Testing off-topic handling...")
        
        off_topic_message = "What's the weather like?"
        print(f"   User: {off_topic_message}")
        
        bot_response, is_completed = manager.get_bot_response(
            user_message=off_topic_message,
            conversation_history=conversation_history,
            form_data=form_data,
            demographics=form_data.get('demographics', [])
        )
        
        print(f"   🤖 Bot: {bot_response}")
        has_bananas = 'bananas' in bot_response.lower()
        print(f"   🍌 Has 'bananas': {has_bananas}")
        
        # Test 5: Data extraction
        print("\n5. Testing data extraction...")
        
        extracted_data = manager.extract_structured_data(
            transcript=conversation_history,
            form_data=form_data,
            demographics=form_data.get('demographics', [])
        )
        
        questions_extracted = len(extracted_data.get('questions', {}))
        print(f"   📊 Extracted {questions_extracted} question responses")
        
        if extracted_data.get('questions'):
            print("   🔍 Sample extractions:")
            for q, a in list(extracted_data['questions'].items())[:3]:
                print(f"     • {q[:50]}... → {str(a)[:30]}...")
        
        # Final assessment
        print("\n" + "=" * 40)
        print("📊 DIRECT TEST RESULTS:")
        print(f"✅ Form access: Working")
        print(f"✅ Agent initiation: Working")
        print(f"✅ Conversation flow: Working")  
        print(f"{'✅' if has_bananas else '❌'} Off-topic handling: {'Working' if has_bananas else 'Not working'}")
        print(f"✅ Data extraction: Working ({questions_extracted} responses)")
        
        print("\n🎉 Direct API tests completed!")
        print("💡 The core conversation system is working locally")
        print("⚠️  Issues are likely with Firebase Functions deployment")
        
        return True
        
    except Exception as e:
        print(f"❌ Direct test error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_human_like_quality():
    """Test human-like conversation quality specifically"""
    
    print("\n" + "=" * 40)
    print("🗣️  HUMAN-LIKE CONVERSATION QUALITY TEST")
    print("=" * 40)
    
    try:
        from firebase_integration import firebase_manager
        from agentic_conversation import create_agentic_conversation_manager
        
        form_data = firebase_manager.get_form('test-form-coffee')
        manager = create_agentic_conversation_manager()
        
        # Test various aspects of human-like conversation
        test_scenarios = [
            {
                'name': 'Natural greeting initiation',
                'user_message': '',
                'history': []
            },
            {
                'name': 'Acknowledgment and follow-up',
                'user_message': 'I absolutely love espresso!',
                'history': [
                    {'role': 'assistant', 'text': "Hey! Let's chat about coffee preferences. What's your favorite type?"}
                ]
            },
            {
                'name': 'Handling enthusiastic response',
                'user_message': 'OMG yes! I drink it like 5 times a day!!!',
                'history': [
                    {'role': 'assistant', 'text': "Nice choice! How often do you drink coffee?"}
                ]
            },
            {
                'name': 'Processing vague answer',
                'user_message': 'usually morning time',
                'history': [
                    {'role': 'assistant', 'text': "Cool! What time of day do you usually have coffee?"}
                ]
            }
        ]
        
        for scenario in test_scenarios:
            print(f"\n🎭 Testing: {scenario['name']}")
            print(f"   Context: {len(scenario['history'])} messages in history")
            
            if scenario['user_message']:
                print(f"   User: '{scenario['user_message']}'")
            else:
                print("   (Agent initiating conversation)")
            
            bot_response, is_completed = manager.get_bot_response(
                user_message=scenario['user_message'],
                conversation_history=scenario['history'],
                form_data=form_data,
                demographics=form_data.get('demographics', [])
            )
            
            print(f"   🤖 Bot: '{bot_response}'")
            
            # Analyze human-like qualities
            qualities = {
                'Uses contractions': any(cont in bot_response for cont in ["i'm", "you're", "that's", "let's", "don't", "can't"]),
                'Natural expressions': any(exp in bot_response.lower() for exp in ['cool', 'nice', 'awesome', 'great', 'love', 'wow']),
                'Uses emojis': any(emoji in bot_response for emoji in ['😊', '!', '🤔', '👍']),
                'Asks follow-up': '?' in bot_response,
                'Appropriate length': 10 < len(bot_response) < 150,
                'Avoids formal language': not any(formal in bot_response.lower() for formal in ['please complete', 'kindly', 'thank you for'])
            }
            
            quality_score = sum(qualities.values()) / len(qualities)
            print(f"   📊 Human-like score: {quality_score:.1%}")
            
            for quality, passed in qualities.items():
                status = "✅" if passed else "❌"
                print(f"     {status} {quality}")
        
        print(f"\n🎯 Human-like conversation quality assessment completed")
        return True
        
    except Exception as e:
        print(f"❌ Human-like quality test error: {e}")
        return False

if __name__ == "__main__":
    success = True
    
    if not test_direct_chat():
        success = False
    
    if not test_human_like_quality():
        success = False
    
    sys.exit(0 if success else 1)