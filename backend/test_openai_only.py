#!/usr/bin/env python3
"""
Test OpenAI inference directly without Firebase auth
"""
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import json
import re

# Load environment variables
load_dotenv('../.env')

def test_openai_direct():
    """Test OpenAI inference directly"""
    
    print("🧪 Testing OpenAI GPT-4o-mini directly...")
    print(f"🔑 OpenAI API Key: {'✓ Set' if os.getenv('OPENAI_API_KEY') else '✗ Missing'}")
    
    # Initialize OpenAI
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.7,
        max_tokens=1000,
        api_key=os.getenv('OPENAI_API_KEY')
    )
    
    # Create the exact prompt from YAML
    inference_template = """You are an expert form inferrer. From this dump: {dump}

Output JSON: {{'title': str, 'questions': [{{'text': str, 'type': 'text'|'multiple_choice'|'yes_no'|'number'|'rating', 'options': [str] if multiple_choice/yes_no/rating (infer logical ones), 'enabled': true}}]}}

###
Chain-of-Thought:
Step 1: Summarize dump's intent.
Step 2: Derive 5-10 clear questions.
Step 3: Infer type per question (e.g., choices → multiple_choice with options; binary → yes_no; numeric → number; scale → rating; else text).
Step 4: Self-critique: Are types/options logical/non-redundant?

Few-Shot Examples:
- Dump: "Favorite color: red/blue/green?" Output: {{'title': 'Color Survey', 'questions': [{{'text': 'Favorite color?', 'type': 'multiple_choice', 'options': ['red', 'blue', 'green'], 'enabled': true}}]}}
- Dump: "How many pets? Yes or no to cats?" Output: {{'title': 'Pet Survey', 'questions': [{{'text': 'How many pets?', 'type': 'number', 'enabled': true}}, {{'text': 'Do you like cats?', 'type': 'yes_no', 'options': ['Yes', 'No'], 'enabled': true}}]}}
- Dump: "Rate service 1-5" Output: {{'questions': [{{'text': 'Rate service?', 'type': 'rating', 'options': ['1', '2', '3', '4', '5'], 'enabled': true}}]}}

Output (JSON only):"""

    inference_prompt = PromptTemplate(
        input_variables=["dump"],
        template=inference_template
    )
    
    inference_chain = inference_prompt | llm | StrOutputParser()
    
    # Test with coffee shop example
    test_dump = """
    Customer feedback survey about our new coffee shop experience:
    
    We want to understand what customers think about our new location. 
    Questions we need answered:
    - What's your favorite type of coffee? (espresso, latte, cappuccino, americano)
    - How often do you visit coffee shops? (daily, weekly, monthly, rarely)
    - What's your preferred time to visit? (morning, afternoon, evening)
    - How would you rate our service on a scale of 1-5?
    - Do you have any dietary restrictions or allergies?
    - Would you recommend us to friends? yes/no
    - How much do you typically spend on coffee per visit?
    """
    
    print("🚀 Sending request to OpenAI...")
    print(f"📝 Test dump: {test_dump[:100]}...")
    
    try:
        response = inference_chain.invoke({"dump": test_dump})
        
        print(f"📤 Raw OpenAI response:")
        print(response)
        print("-" * 50)
        
        # Extract JSON from response
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            json_str = json_match.group()
            form_data = json.loads(json_str)
            
            print("✅ Successfully parsed JSON!")
            print(f"🎯 Title: {form_data.get('title', 'N/A')}")
            print(f"📋 Questions ({len(form_data.get('questions', []))}):")
            
            for i, question in enumerate(form_data.get('questions', []), 1):
                print(f"  {i}. {question.get('text', 'N/A')} [{question.get('type', 'N/A')}]")
                if question.get('options'):
                    print(f"     Options: {question.get('options')}")
            
            return True
        else:
            print("❌ Could not extract JSON from response")
            return False
            
    except Exception as e:
        print(f"❌ OpenAI request failed: {e}")
        return False

def main():
    print("🧪 Testing OpenAI Integration for Bermuda")
    print("=" * 50)
    
    success = test_openai_direct()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 OpenAI integration is working perfectly!")
        print("💡 The LangChain + GPT-4o-mini setup is ready for the backend")
    else:
        print("⚠️  OpenAI integration has issues. Check your API key and connection.")

if __name__ == "__main__":
    main()