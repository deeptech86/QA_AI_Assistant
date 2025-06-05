# External Prompts System (JSON-Based)

This document explains the JSON-based external prompts system implemented for the Streamlit chat filter application.

## Overview

The external prompts system extracts all hardcoded prompts from Python files and stores them in external JSON configuration files. This provides several benefits:

- **Centralized Management**: All prompts are stored in one location
- **Easy Modification**: Change prompts without editing Python code
- **Version Control**: Track prompt changes separately from code
- **JSON Format**: Standard, widely-supported format
- **Easy Parsing**: Simple to read in any programming language
- **Reusability**: Prompts can be shared across different modules

## File Structure

```
prompts/
├── chat_filter_prompts.json   # Main prompts configuration (JSON)
├── json_prompts_helper.py     # Python utility to load JSON prompts
├── test_json_prompts.py       # Test script for JSON functionality
├── chat_filter_prompts.yaml   # Legacy YAML version (for reference)
├── prompt_loader.py           # Legacy YAML loader (for reference)
└── README.md                  # This documentation
```

## Files Description

### 1. `chat_filter_prompts.json`
The main configuration file containing all prompts and settings for the chat filter module:

- **system_prompt**: Main AI system prompt with instructions and formatting rules
- **input_validation**: Messages for user input validation
- **response_messages**: Various response templates for different scenarios
- **ui_text**: All UI labels and text content
- **topic_configuration**: Allowed and forbidden topics configuration
- **code_patterns**: Regular expressions for code detection
- **filter_messages**: Messages for different filter outcomes
- **action_options**: Available actions in the interface
- **language_options**: Language choices for different tools

### 2. `json_prompts_helper.py`
Python utility module providing functions to load and access prompts from JSON:

**Main Classes:**
- `JSONPromptsHelper`: Core class for loading and managing JSON prompts

**Convenience Functions:**
- `get_system_prompt()`: Get the main system prompt
- `get_ui_text(key)`: Get UI text by key
- `get_response_message(key, **kwargs)`: Get formatted response messages
- `get_input_validation_message(key, **kwargs)`: Get input validation messages
- `get_filter_message(key, **kwargs)`: Get filter messages
- `get_allowed_topics()`: Get allowed topics configuration
- `get_forbidden_topics()`: Get forbidden topics list
- `get_code_patterns()`: Get code detection patterns
- `get_action_options()`: Get available actions
- `get_language_options(tool_type)`: Get language options for tools

### 3. `test_json_prompts.py`
Test script to verify the JSON prompts system works correctly.

## Usage Examples

### Basic Python Usage

```python
# Import the JSON prompt functions
from prompts.json_prompts_helper import (
    get_system_prompt,
    get_ui_text,
    get_response_message,
    get_allowed_topics
)

# Get the system prompt
system_prompt = get_system_prompt()

# Get UI text
page_title = get_ui_text('page_title')
main_title = get_ui_text('main_title')

# Get formatted response messages
rejection_msg = get_response_message('rejection_base', 
                                   filter_message="Your message here")

# Get configuration data
allowed_topics = get_allowed_topics()
```

### Advanced Python Usage

```python
from prompts.json_prompts_helper import JSONPromptsHelper

# Create a custom helper
helper = JSONPromptsHelper()

# Load all prompts
prompts = helper.load_prompts()

# Get nested configuration
main_title = helper.get_prompt('ui_text.main_title')

# Format prompts with variables
error_msg = helper.format_prompt('response_messages.api_error',
                                error="Connection timeout")

# Reload prompts (clears cache)
helper.reload_prompts()
```

### Direct JSON Access (Any Language)

```python
import json

# Load JSON directly
with open('prompts/chat_filter_prompts.json', 'r') as f:
    prompts = json.load(f)

# Access data
system_prompt = prompts['system_prompt']
main_title = prompts['ui_text']['main_title']
allowed_topics = prompts['topic_configuration']['allowed_topics']
```

## How the Migration Was Done

### Original Code (Before)
```python
# Hardcoded in chat_filter.py
SYSTEM_PROMPT = """You are a specialized AI assistant focused ONLY on helping with:
1. Writing Test Cases for software applications
..."""

ALLOWED_TOPICS = {
    "programming": ["code", "programming", "python", ...],
    ...
}
```

### Updated Code (After)
```python
# Now using external JSON prompts
from json_prompts_helper import get_system_prompt, get_allowed_topics

SYSTEM_PROMPT = get_system_prompt()
ALLOWED_TOPICS = get_allowed_topics()
```

## JSON Structure

The JSON file follows this structure:

```json
{
  "system_prompt": "Main AI system prompt...",
  
  "input_validation": {
    "insufficient_detail": "Message for insufficient detail",
    "topic_restriction": "Message for topic restriction with {reason}",
    "input_approved": "Input approved message"
  },
  
  "response_messages": {
    "rejection_base": "Base rejection message with {filter_message}",
    "forbidden_topic_response": "Forbidden topic response",
    "api_error": "API error with {error}",
    "unexpected_error": "Unexpected error with {error}",
    "processing_failed": "Processing failed message"
  },
  
  "ui_text": {
    "page_title": "Page title",
    "page_icon": "🔒",
    "sidebar": {
      "title": "Sidebar title",
      "allowed_topics_header": "Header text",
      "forbidden_topics_header": "Header text"
    },
    "main_title": "Main page title",
    "main_description": "Description text",
    "examples": {
      "header": "Examples header",
      "good_examples": "Good examples text",
      "bad_examples": "Bad examples text"
    }
  },
  
  "topic_configuration": {
    "allowed_topics": {
      "programming": ["list", "of", "keywords"],
      "data_science": ["list", "of", "keywords"]
    },
    "forbidden_topics": ["list", "of", "forbidden", "topics"]
  },
  
  "code_patterns": ["regex", "patterns", "for", "code"],
  
  "filter_messages": {
    "forbidden_topic": "Message with {topic}",
    "allowed_topics_found": "Message with {topics}",
    "code_content_detected": "Code detected message",
    "no_topics_detected": "No topics message"
  },
  
  "action_options": ["list", "of", "action", "options"],
  
  "language_options": {
    "selenium_languages": ["Java", "Python", "JavaScript", "C#"],
    "testcomplete_languages": ["Java", "Python", "JavaScript", "C#"],
    "api_test_languages": ["Java", "Python", "JavaScript"],
    "conversion_options": ["conversion", "options"]
  }
}
```

## Installation and Setup

1. **Install Dependencies**:
   ```bash
   # JSON is part of Python standard library, no additional dependencies needed
   ```

2. **Verify Installation**:
   ```bash
   cd prompts/
   python test_json_prompts.py
   ```

3. **Run the Application**:
   ```bash
   streamlit run chat_models/5.chat_filter.py
   ```

## Testing

Run the test script to verify everything works:

```bash
cd prompts/
python test_json_prompts.py
```

The test script will:
- ✅ Verify JSON file exists and is readable
- ✅ Load all prompts successfully
- ✅ Test formatted responses
- ✅ Verify JSONPromptsHelper class functionality
- ✅ Test JSON structure and required keys
- ✅ Display sample data

## Benefits of JSON Format

### 1. **Universal Compatibility**
- Supported by virtually every programming language
- No external dependencies required
- Easy to parse and modify

### 2. **Simple Structure**
- Human-readable format
- Clear hierarchical organization
- Easy to validate and debug

### 3. **Lightweight**
- Minimal overhead
- Fast parsing
- Small file size

### 4. **IDE Support**
- Syntax highlighting in most editors
- Built-in validation in many IDEs
- Easy to navigate and edit

## Adding New Prompts

To add new prompts to the JSON system:

### 1. Update the JSON file:
```json
{
  "existing_prompts": "...",
  "new_section": {
    "my_new_prompt": "This is my new prompt with {variable} support.",
    "another_prompt": "Simple string prompt"
  }
}
```

### 2. Add convenience functions (optional):
```python
# Add to json_prompts_helper.py
def get_my_new_prompt(**kwargs):
    helper = get_helper()
    return helper.format_prompt('new_section.my_new_prompt', **kwargs)
```

### 3. Use in your code:
```python
from json_prompts_helper import get_my_new_prompt

# Use the prompt
prompt_text = get_my_new_prompt(variable="example")
```

## Troubleshooting

### Common Issues:

1. **json.JSONDecodeError: Expecting ',' delimiter**
   - Check for syntax errors in the JSON file
   - Ensure all strings are properly quoted
   - Validate JSON using an online validator

2. **KeyError: Prompt path not found**
   - Check the path in the JSON file
   - Use dot notation for nested keys (e.g., 'ui_text.main_title')

3. **FileNotFoundError: JSON file not found**
   - Ensure you're running from the correct directory
   - Check the file path in JSONPromptsHelper initialization

4. **Format string error**
   - Ensure all required variables are provided to format functions
   - Check for typos in variable names

### Validation

You can validate your JSON file using:

```bash
# Using Python
python -m json.tool chat_filter_prompts.json

# Using online validators
# https://jsonlint.com/
# https://jsonformatter.curiousconcept.com/
```

## Performance Considerations

- **Caching**: The helper automatically caches loaded prompts
- **Memory**: JSON data is kept in memory after first load
- **Reload**: Use `reload_prompts()` to refresh from disk
- **File Size**: JSON format is compact and loads quickly

## Future Enhancements

Potential improvements to consider:

1. **Schema Validation**: Add JSON schema validation
2. **Multi-language Support**: Add language-specific JSON files
3. **Environment-specific Prompts**: Different JSON files for dev/staging/production
4. **Hot Reloading**: Automatically reload when JSON file changes
5. **Web Interface**: Create a web UI for editing the JSON file

## Contributing

When adding new prompts or modifying existing ones:

1. Update the JSON file with proper formatting
2. Add appropriate convenience functions if needed
3. Update tests in `test_json_prompts.py`
4. Validate JSON syntax before committing
5. Update this documentation
6. Test thoroughly before committing

## Migration from YAML

If you were using the previous YAML-based system:

1. **Backup**: Keep your YAML files for reference
2. **Update imports**: Change from `prompt_loader` to `json_prompts_helper`
3. **Test**: Run the test script to verify functionality
4. **Remove**: Delete old YAML dependencies if no longer needed

---

## Summary

The JSON-based external prompts system provides a clean, maintainable, and universally compatible way to manage all text content and prompts in your Streamlit application. The JSON format ensures maximum compatibility while the helper functions provide convenient access to all prompts with caching and formatting support.

### Key Benefits:
- ✅ **No external dependencies** (JSON is built into Python)
- ✅ **Universal format** (works with any programming language)
- ✅ **Simple structure** (easy to read and modify)
- ✅ **Fast performance** (cached loading)
- ✅ **Easy validation** (built-in JSON tools)
- ✅ **IDE friendly** (syntax highlighting and validation)
