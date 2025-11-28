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
        model_name: Gemini model name (default: "gemini-1.5-flash")
    
    Returns:
        Generated text response
    """
    # List of models to try in order of preference
    # For Generative Language API, try these model names
    models_to_try = [
        "gemini-1.5-flash",  # Most common and fast
        "gemini-1.5-pro",    # More capable
        "gemini-pro",        # Legacy model
        model_name,          # Try user-specified model last
    ]
    
    last_error = None
    for model in models_to_try:
        try:
            # Try without system_instruction first (some models may not support it)
            try:
                gen_model = genai.GenerativeModel(
                    model,
                    system_instruction=system_prompt
                )
                actual_user_prompt = user_prompt
            except:
                # If system_instruction fails, try without it
                gen_model = genai.GenerativeModel(model)
                # Add system prompt to user prompt instead
                actual_user_prompt = f"{system_prompt}\n\n{user_prompt}"
            
            generation_config = {
                "temperature": temperature,
                "top_p": 0.95,
                "top_k": 40,
            }
            
            response = gen_model.generate_content(
                actual_user_prompt,
                generation_config=generation_config
            )
            
            return response.text
        except Exception as e:
            last_error = e
            error_str = str(e).lower()
            # If this is not a 404/model not found error, return immediately
            if "404" not in str(e) and "not found" not in error_str and "not supported" not in error_str:
                return f"Error calling Gemini API: {str(e)}"
            # Otherwise, try next model
            continue
    
    # If all models failed, try to list available models for debugging
    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        return f"Error calling Gemini API: Could not find a working model. Last error: {str(last_error)}\nAvailable models: {', '.join(available_models[:5])}"
    except:
        return f"Error calling Gemini API: Could not find a working model. Last error: {str(last_error)}"

