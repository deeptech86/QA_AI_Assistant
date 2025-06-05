"""
Prompt loader utility for the langchain_demo application.
This module provides functions to load prompts from external YAML files.
"""

import yaml
import os
from typing import Dict, Any, List
from pathlib import Path

class PromptLoader:
    """
    A utility class to load and manage prompts from YAML configuration files.
    """
    
    def __init__(self, prompts_dir: str = None):
        """
        Initialize the PromptLoader.
        
        Args:
            prompts_dir (str): Directory containing prompt files. If None, uses default.
        """
        if prompts_dir is None:
            # Get the directory where this script is located
            current_dir = Path(__file__).parent
            self.prompts_dir = current_dir
        else:
            self.prompts_dir = Path(prompts_dir)
        
        self._cache = {}
    
    def load_prompts(self, filename: str) -> Dict[str, Any]:
        """
        Load prompts from a YAML file.
        
        Args:
            filename (str): Name of the YAML file (without extension)
            
        Returns:
            Dict[str, Any]: Dictionary containing all prompts from the file
            
        Raises:
            FileNotFoundError: If the prompt file doesn't exist
            yaml.YAMLError: If the YAML file is malformed
        """
        # Add .yaml extension if not present
        if not filename.endswith('.yaml') and not filename.endswith('.yml'):
            filename += '.yaml'
        
        file_path = self.prompts_dir / filename
        
        # Check cache first
        if str(file_path) in self._cache:
            return self._cache[str(file_path)]
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                prompts = yaml.safe_load(file)
                
            # Cache the loaded prompts
            self._cache[str(file_path)] = prompts
            return prompts
            
        except FileNotFoundError:
            raise FileNotFoundError(f"Prompt file not found: {file_path}")
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"Error parsing YAML file {file_path}: {e}")
    
    def get_prompt(self, filename: str, prompt_path: str) -> str:
        """
        Get a specific prompt by its path in the YAML structure.
        
        Args:
            filename (str): Name of the YAML file
            prompt_path (str): Dot-separated path to the prompt (e.g., 'system_prompt' or 'ui_text.main_title')
            
        Returns:
            str: The requested prompt text
            
        Raises:
            KeyError: If the prompt path doesn't exist
        """
        prompts = self.load_prompts(filename)
        
        # Navigate through nested dictionary using dot notation
        keys = prompt_path.split('.')
        current = prompts
        
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                raise KeyError(f"Prompt path '{prompt_path}' not found in {filename}")
        
        return current
    
    def get_config(self, filename: str, config_path: str) -> Any:
        """
        Get configuration data (not just prompts) by path.
        
        Args:
            filename (str): Name of the YAML file
            config_path (str): Dot-separated path to the configuration
            
        Returns:
            Any: The requested configuration data
        """
        return self.get_prompt(filename, config_path)  # Same logic applies
    
    def format_prompt(self, filename: str, prompt_path: str, **kwargs) -> str:
        """
        Get a prompt and format it with provided parameters.
        
        Args:
            filename (str): Name of the YAML file
            prompt_path (str): Dot-separated path to the prompt
            **kwargs: Variables to format into the prompt
            
        Returns:
            str: Formatted prompt text
        """
        prompt_template = self.get_prompt(filename, prompt_path)
        try:
            return prompt_template.format(**kwargs)
        except KeyError as e:
            raise KeyError(f"Missing format parameter for prompt '{prompt_path}': {e}")
    
    def clear_cache(self):
        """Clear the internal cache of loaded prompts."""
        self._cache.clear()
    
    def list_available_files(self) -> List[str]:
        """
        List all available YAML prompt files in the prompts directory.
        
        Returns:
            List[str]: List of available prompt file names
        """
        yaml_files = []
        for file_path in self.prompts_dir.glob("*.yaml"):
            yaml_files.append(file_path.name)
        for file_path in self.prompts_dir.glob("*.yml"):
            yaml_files.append(file_path.name)
        return sorted(yaml_files)


# Global instance for easy access
_default_loader = None

def get_default_loader() -> PromptLoader:
    """
    Get the default prompt loader instance.
    
    Returns:
        PromptLoader: Default prompt loader instance
    """
    global _default_loader
    if _default_loader is None:
        _default_loader = PromptLoader()
    return _default_loader

def load_chat_filter_prompts() -> Dict[str, Any]:
    """
    Convenience function to load chat filter prompts.
    
    Returns:
        Dict[str, Any]: Chat filter prompts configuration
    """
    loader = get_default_loader()
    return loader.load_prompts('chat_filter_prompts')

def get_system_prompt(name) -> str:
    """
    Get the main system prompt for chat filtering.
    
    Returns:
        str: System prompt text
    """
    loader = get_default_loader()
    if name.lower() == 'testcases':
        return loader.get_prompt('chat_filter_prompts', 'system_prompt_testcases')
    elif name.lower() == 'selenium':
        return loader.get_prompt('chat_filter_prompts', 'system_prompt_selenium')
    elif name.lower() == 'testcomplete':
        return loader.get_prompt('chat_filter_prompts', 'system_prompt_testcomplete')
    elif name.lower() == 'APICode'.lower():
        return loader.get_prompt('chat_filter_prompts', 'system_prompt_APICode')
    elif name.lower() == 'playwright':
        return loader.get_prompt('chat_filter_prompts', 'system_prompt_playwright')
    elif name.lower() == 'unittest':
        return loader.get_prompt('chat_filter_prompts', 'system_prompt_unittest')
    elif name.lower() == 'convert':
        return loader.get_prompt('chat_filter_prompts', 'system_prompt_conversion')
    elif name.lower() == 'newRepo'.lower():
        return loader.get_prompt('chat_filter_prompts', 'system_prompt_newRepo')
    else:
        return loader.get_prompt('chat_filter_prompts', 'system_prompt')

def get_ui_text(key: str) -> str:
    """
    Get UI text by key.
    
    Args:
        key (str): UI text key (e.g., 'main_title', 'sidebar.title')
        
    Returns:
        str: UI text
    """
    loader = get_default_loader()
    return loader.get_prompt('chat_filter_prompts', f'ui_text.{key}')

def get_response_message(key: str, **kwargs) -> str:
    """
    Get and format a response message.
    
    Args:
        key (str): Response message key
        **kwargs: Format parameters
        
    Returns:
        str: Formatted response message
    """
    loader = get_default_loader()
    return loader.format_prompt('chat_filter_prompts', f'response_messages.{key}', **kwargs)

def get_allowed_topics() -> Dict[str, List[str]]:
    """
    Get the allowed topics configuration.
    
    Returns:
        Dict[str, List[str]]: Allowed topics by category
    """
    loader = get_default_loader()
    return loader.get_config('chat_filter_prompts', 'topic_configuration.allowed_topics')

def get_forbidden_topics() -> List[str]:
    """
    Get the forbidden topics list.
    
    Returns:
        List[str]: List of forbidden topics
    """
    loader = get_default_loader()
    return loader.get_config('chat_filter_prompts', 'topic_configuration.forbidden_topics')

def get_code_patterns() -> List[str]:
    """
    Get code detection patterns.
    
    Returns:
        List[str]: List of regex patterns for code detection
    """
    loader = get_default_loader()
    return loader.get_config('chat_filter_prompts', 'code_patterns')

def get_action_options() -> List[str]:
    """
    Get available action options.
    
    Returns:
        List[str]: List of action options
    """
    loader = get_default_loader()
    return loader.get_config('chat_filter_prompts', 'action_options')

def get_language_options(tool_type: str) -> List[str]:
    """
    Get language options for a specific tool type.
    
    Args:
        tool_type (str): Type of tool (e.g., 'selenium_languages', 'api_test_languages')
        
    Returns:
        List[str]: List of language options
    """
    loader = get_default_loader()
    return loader.get_config('chat_filter_prompts', f'language_options.{tool_type}')

def get_input_validation_message(key: str, **kwargs) -> str:
    """
    Get and format an input validation message.

    Args:
        key (str): Input validation message key
        **kwargs: Format parameters

    Returns:
        str: Formatted validation message
    """
    loader = get_default_loader()
    return loader.format_prompt('chat_filter_prompts', f'input_validation.{key}', **kwargs)

def get_filter_message(key: str, **kwargs) -> str:
    """
    Get and format a filter message.

    Args:
        key (str): Filter message key
        **kwargs: Format parameters

    Returns:
        str: Formatted filter message
    """
    loader = get_default_loader()
    return loader.format_prompt('chat_filter_prompts', f'filter_messages.{key}', **kwargs)

def get_prompts_config() -> Dict[str, Any]:
    """
    Get the complete prompts configuration.

    Returns:
        Dict[str, Any]: Complete prompts configuration
    """
    return load_chat_filter_prompts()


if __name__ == "__main__":
    # Example usage and testing
    try:
        loader = PromptLoader()
        print("Available prompt files:", loader.list_available_files())

        # Test loading chat filter prompts
        prompts = load_chat_filter_prompts()
        print("✅ Successfully loaded chat filter prompts")

        # Test specific prompt retrieval
        system_prompt = get_system_prompt()
        print("✅ Successfully retrieved system prompt")

        # Test UI text retrieval
        main_title = get_ui_text('main_title')
        print(f"✅ Main title: {main_title}")

        # Test formatted response
        rejection_msg = get_response_message('rejection_base', filter_message="Test message")
        print("✅ Successfully formatted response message")

        # Test input validation message
        validation_msg = get_input_validation_message('insufficient_detail')
        print("✅ Successfully retrieved input validation message")

        # Test filter message
        filter_msg = get_filter_message('code_content_detected')
        print("✅ Successfully retrieved filter message")

        # Test prompts config
        config = get_prompts_config()
        print(f"✅ Successfully loaded prompts config with {len(config)} sections")
        
        print("🎉 All tests passed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
