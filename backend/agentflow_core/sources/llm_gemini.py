"""
AgentFlow Core - Gemini LLM Source Adapter

Adapter for Google Gemini language models.
Provides a unified interface for LLM operations.
"""

import os
from typing import Any, Dict, List, Optional

from agentflow_core.utils.error_handler import SourceConnectionError
from agentflow_core.utils.logger import get_logger

logger = get_logger(__name__)


# =============================================================================
# Constants
# =============================================================================

# Default configuration
DEFAULT_MODEL = "gemini-2.5-flash"
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_TOKENS = 4096

# Supported models
SUPPORTED_MODELS = [
    "gemini-2.5-flash",
    "gemini-2.5-pro",
    "gemini-2.0-flash",
    "gemini-2.0-flash-exp",
    "gemini-flash-latest",
]


# =============================================================================
# Gemini Client Factory
# =============================================================================


def create_gemini_client(config: Dict[str, Any]) -> Any:
    """
    Create a Gemini client from configuration.
    
    Args:
        config: Source configuration dictionary
            - api_key_env: Environment variable name for API key
            - api_key: Direct API key (not recommended)
            - model: Model name
            - temperature: Generation temperature
            - max_tokens: Maximum tokens to generate
    
    Returns:
        Configured Gemini GenerativeModel instance
        
    Raises:
        SourceConnectionError: If client creation fails
    """
    try:
        import google.generativeai as genai
    except ImportError:
        raise SourceConnectionError(
            message="google-generativeai package not installed. Run: pip install google-generativeai",
            source_id="gemini",
            source_kind="llm"
        )
    
    # Get API key
    api_key = config.get("api_key")
    if not api_key:
        api_key_env = config.get("api_key_env", "GEMINI_API_KEY")
        api_key = os.getenv(api_key_env)
    
    if not api_key:
        raise SourceConnectionError(
            message=f"Gemini API key not found. Set {config.get('api_key_env', 'GEMINI_API_KEY')} environment variable.",
            source_id="gemini",
            source_kind="llm"
        )
    
    # Configure the library
    genai.configure(api_key=api_key)
    
    # Get model configuration
    model_name = config.get("model", config.get("model_name", DEFAULT_MODEL))
    temperature = config.get("temperature", DEFAULT_TEMPERATURE)
    max_tokens = config.get("max_tokens", config.get("max_output_tokens", DEFAULT_MAX_TOKENS))
    
    # Create generation config
    generation_config = genai.GenerationConfig(
        temperature=temperature,
        max_output_tokens=max_tokens,
        top_p=config.get("top_p", 0.95),
        top_k=config.get("top_k", 40),
    )
    
    # Get safety settings
    safety_settings = config.get("safety_settings")
    
    # Create model
    model = genai.GenerativeModel(
        model_name=model_name,
        generation_config=generation_config,
        safety_settings=safety_settings,
        system_instruction=config.get("system_prompt"),
    )
    
    logger.info(
        "gemini_client_created",
        model=model_name,
        temperature=temperature,
        max_tokens=max_tokens
    )
    
    return model


def get_gemini_client(config: Dict[str, Any]) -> Any:
    """
    Get or create a Gemini client.
    
    This is an alias for create_gemini_client for consistency
    with other adapters.
    """
    return create_gemini_client(config)


# =============================================================================
# Generation Functions
# =============================================================================


def generate_text(
    client: Any,
    prompt: str,
    system_prompt: Optional[str] = None,
    **kwargs: Any
) -> Dict[str, Any]:
    """
    Generate text using Gemini.
    
    Args:
        client: Gemini GenerativeModel instance
        prompt: The prompt to send
        system_prompt: Optional system prompt (may be ignored if set on client)
        **kwargs: Additional generation parameters
        
    Returns:
        Dictionary with:
            - text: Generated text
            - tokens_used: Token count
            - model: Model used
            - finish_reason: Why generation stopped
    """
    try:
        # Generate content
        response = client.generate_content(prompt)
        
        # Extract text
        text = response.text if response.text else ""
        
        # Get usage metrics
        tokens_used = 0
        if hasattr(response, "usage_metadata"):
            usage = response.usage_metadata
            tokens_used = getattr(usage, "total_token_count", 0)
        else:
            # Approximate
            tokens_used = (len(prompt) + len(text)) // 4
        
        # Get finish reason
        finish_reason = "completed"
        if hasattr(response, "candidates") and response.candidates:
            candidate = response.candidates[0]
            if hasattr(candidate, "finish_reason"):
                finish_reason = str(candidate.finish_reason)
        
        logger.info(
            "gemini_generation_success",
            prompt_length=len(prompt),
            response_length=len(text),
            tokens_used=tokens_used
        )
        
        return {
            "text": text,
            "tokens_used": tokens_used,
            "model": client.model_name if hasattr(client, "model_name") else "gemini",
            "finish_reason": finish_reason,
        }
        
    except Exception as e:
        logger.error("gemini_generation_failed", error=str(e))
        raise SourceConnectionError(
            message=f"Gemini generation failed: {str(e)}",
            source_id="gemini",
            source_kind="llm"
        )


def generate_chat(
    client: Any,
    messages: List[Dict[str, str]],
    **kwargs: Any
) -> Dict[str, Any]:
    """
    Generate a chat response using Gemini.
    
    Args:
        client: Gemini GenerativeModel instance
        messages: List of messages with 'role' and 'content'
        **kwargs: Additional generation parameters
        
    Returns:
        Dictionary with generation result
    """
    try:
        # Start chat session
        chat = client.start_chat(history=[])
        
        # Send messages
        response = None
        for message in messages:
            role = message.get("role", "user")
            content = message.get("content", "")
            
            if role in ("user", "human"):
                response = chat.send_message(content)
        
        if response is None:
            return {
                "text": "",
                "tokens_used": 0,
                "model": "gemini",
                "finish_reason": "no_messages",
            }
        
        # Extract response
        text = response.text if response.text else ""
        tokens_used = 0
        if hasattr(response, "usage_metadata"):
            tokens_used = getattr(response.usage_metadata, "total_token_count", 0)
        
        return {
            "text": text,
            "tokens_used": tokens_used,
            "model": client.model_name if hasattr(client, "model_name") else "gemini",
            "finish_reason": "completed",
        }
        
    except Exception as e:
        logger.error("gemini_chat_failed", error=str(e))
        raise SourceConnectionError(
            message=f"Gemini chat failed: {str(e)}",
            source_id="gemini",
            source_kind="llm"
        )


# =============================================================================
# Streaming (for future use)
# =============================================================================


async def generate_text_stream(
    client: Any,
    prompt: str,
    **kwargs: Any
):
    """
    Generate text using Gemini with streaming.
    
    Yields chunks of generated text.
    """
    try:
        response = client.generate_content(prompt, stream=True)
        
        for chunk in response:
            if chunk.text:
                yield chunk.text
                
    except Exception as e:
        logger.error("gemini_stream_failed", error=str(e))
        raise SourceConnectionError(
            message=f"Gemini streaming failed: {str(e)}",
            source_id="gemini",
            source_kind="llm"
        )


# =============================================================================
# Utility Functions
# =============================================================================


def count_tokens(client: Any, text: str) -> int:
    """
    Count tokens in text using Gemini's tokenizer.
    
    Args:
        client: Gemini client
        text: Text to count tokens for
        
    Returns:
        Token count
    """
    try:
        result = client.count_tokens(text)
        return result.total_tokens
    except Exception:
        # Fallback: approximate
        return len(text) // 4


def list_models() -> List[str]:
    """
    List available Gemini models.
    
    Returns:
        List of model names
    """
    try:
        import google.generativeai as genai
        models = genai.list_models()
        return [m.name for m in models if "generateContent" in m.supported_generation_methods]
    except Exception as e:
        logger.warning("failed_to_list_models", error=str(e))
        return SUPPORTED_MODELS
