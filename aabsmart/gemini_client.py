"""
Gemini API client for AabSmart Farmer system.
"""

import os
import google.generativeai as genai
from typing import Optional


def initialize_gemini(api_key: Optional[str] = None) -> None:
    """
    Initialize Gemini API with API key.
    
    Args:
        api_key: Gemini API key. If None, tries to load from environment variable.
    """
    if api_key is None:
        # Load from environment variable (GitHub/local development)
        api_key = os.getenv("GEMINI_API_KEY")
        
        # Optional: Try Kaggle Secrets if running in Kaggle (for backward compatibility)
        if not api_key:
            try:
                from kaggle_secrets import UserSecretsClient
                client = UserSecretsClient()
                api_key = client.get_secret("GEMINI_API_KEY")
            except ImportError:
                pass  # Not in Kaggle environment
        
        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY not found. Please set it as an environment variable:\n"
                "  export GEMINI_API_KEY='your-api-key'\n"
                "Or pass it directly: initialize_gemini(api_key='your-api-key')"
            )
    
    genai.configure(api_key=api_key)


def call_gemini(
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.2,
    model_name: str = "gemini-1.5-flash"
) -> str:
    """
    Call Gemini API with system instruction and user prompt.
    
    Args:
        system_prompt: System instruction for the model
        user_prompt: User message/prompt
        temperature: Sampling temperature (0.0-1.0)
        model_name: Gemini model name
    
    Returns:
        Generated text response
    """
    try:
        model = genai.GenerativeModel(
            model_name,
            system_instruction=system_prompt
        )
        
        generation_config = {
            "temperature": temperature,
            "top_p": 0.95,
            "top_k": 40,
        }
        
        response = model.generate_content(
            user_prompt,
            generation_config=generation_config
        )
        
        return response.text
    except Exception as e:
        return f"Error calling Gemini API: {str(e)}"

