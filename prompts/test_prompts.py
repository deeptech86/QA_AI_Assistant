#!/usr/bin/env python3
"""
Test script for the external prompts system.
This script verifies that all prompts can be loaded correctly.
"""

import sys
from pathlib import Path

# Add the prompts directory to Python path
prompts_dir = Path(__file__).parent
sys.path.append(str(prompts_dir))

try:
    from prompt_loader import (
        PromptLoader,
        get_system_prompt,
        get_ui_text,
        get_response_message,
        get_allowed_topics,
        get_forbidden_topics,
        get_code_patterns,
        get_action_options,
        get_language_options,
        load_chat_filter_prompts
    )
    print("✅ Successfully imported prompt_loader module")
except ImportError as e:
    print(f"❌ Failed to import prompt_loader: {e}")
    sys.exit(1)

def test_prompt_loading():
    """Test basic prompt loading functionality."""
    print("\n🧪 Testing prompt loading...")
    
    try:
        # Test loading all prompts
        prompts = load_chat_filter_prompts()
        print("✅ Successfully loaded chat filter prompts")
        
        # Test system prompt
        system_prompt = get_system_prompt()
        assert isinstance(system_prompt, str) and len(system_prompt) > 100
        print("✅ System prompt loaded successfully")
        
        # Test UI text
        main_title = get_ui_text('main_title')
        assert isinstance(main_title, str) and len(main_title) > 0
        print("✅ UI text loaded successfully")
        
        # Test configuration data
        allowed_topics = get_allowed_topics()
        assert isinstance(allowed_topics, dict) and 'programming' in allowed_topics
        print("✅ Allowed topics loaded successfully")
        
        forbidden_topics = get_forbidden_topics()
        assert isinstance(forbidden_topics, list) and len(forbidden_topics) > 0
        print("✅ Forbidden topics loaded successfully")
        
        # Test code patterns
        code_patterns = get_code_patterns()
        assert isinstance(code_patterns, list) and len(code_patterns) > 0
        print("✅ Code patterns loaded successfully")
        
        # Test action options
        action_options = get_action_options()
        assert isinstance(action_options, list) and "Test Case generation" in action_options
        print("✅ Action options loaded successfully")
        
        # Test language options
        selenium_langs = get_language_options('selenium_languages')
        assert isinstance(selenium_langs, list) and "Python" in selenium_langs
        print("✅ Language options loaded successfully")
        
    except Exception as e:
        print(f"❌ Error testing prompt loading: {e}")
        return False
    
    return True

def test_formatted_responses():
    """Test formatted response messages."""
    print("\n🧪 Testing formatted responses...")
    
    try:
        # Test rejection message
        rejection_msg = get_response_message('rejection_base', filter_message="Test filter message")
        assert "Test filter message" in rejection_msg
        print("✅ Rejection message formatting works")
        
        # Test API error message
        api_error_msg = get_response_message('api_error', error="Test API error")
        assert "Test API error" in api_error_msg
        print("✅ API error message formatting works")
        
    except Exception as e:
        print(f"❌ Error testing formatted responses: {e}")
        return False
    
    return True

def test_prompt_loader_class():
    """Test the PromptLoader class directly."""
    print("\n🧪 Testing PromptLoader class...")
    
    try:
        loader = PromptLoader()
        
        # Test file listing
        files = loader.list_available_files()
        assert 'chat_filter_prompts.yaml' in files
        print("✅ File listing works")
        
        # Test specific prompt retrieval
        system_prompt = loader.get_prompt('chat_filter_prompts', 'system_prompt')
        assert isinstance(system_prompt, str) and len(system_prompt) > 100
        print("✅ Specific prompt retrieval works")
        
        # Test nested path retrieval
        main_title = loader.get_prompt('chat_filter_prompts', 'ui_text.main_title')
        assert isinstance(main_title, str) and len(main_title) > 0
        print("✅ Nested path retrieval works")
        
        # Test formatted prompt
        formatted = loader.format_prompt(
            'chat_filter_prompts', 
            'response_messages.api_error', 
            error="Test error"
        )
        assert "Test error" in formatted
        print("✅ Prompt formatting works")
        
    except Exception as e:
        print(f"❌ Error testing PromptLoader class: {e}")
        return False
    
    return True

def print_sample_data():
    """Print some sample data to verify content."""
    print("\n📄 Sample Data:")
    print("-" * 50)
    
    try:
        print("System Prompt (first 200 chars):")
        system_prompt = get_system_prompt()
        print(f"'{system_prompt[:200]}...'")
        
        print("\nMain Title:")
        print(f"'{get_ui_text('main_title')}'")
        
        print("\nAllowed Topics:")
        allowed = get_allowed_topics()
        for category, topics in allowed.items():
            print(f"  {category}: {topics[:3]}... ({len(topics)} total)")
        
        print("\nAction Options:")
        actions = get_action_options()
        for i, action in enumerate(actions[:5]):
            print(f"  {i+1}. {action}")
        
        print("\nSelenium Languages:")
        selenium_langs = get_language_options('selenium_languages')
        print(f"  {selenium_langs}")
        
    except Exception as e:
        print(f"❌ Error printing sample data: {e}")

def main():
    """Run all tests."""
    print("🚀 External Prompts System Test")
    print("=" * 50)
    
    all_tests_passed = True
    
    # Run tests
    all_tests_passed &= test_prompt_loading()
    all_tests_passed &= test_formatted_responses()
    all_tests_passed &= test_prompt_loader_class()
    
    # Print sample data
    print_sample_data()
    
    # Final result
    print("\n" + "=" * 50)
    if all_tests_passed:
        print("🎉 All tests passed! The external prompts system is working correctly.")
        print("\n💡 You can now:")
        print("   - Run your Streamlit app with: streamlit run chat_models/5.chat_filter.py")
        print("   - Edit prompts in: prompts/chat_filter_prompts.yaml")
        print("   - Use the JS version: prompts/chat_filter_prompts.js")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
