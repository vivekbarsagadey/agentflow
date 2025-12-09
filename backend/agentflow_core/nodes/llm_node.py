"""
AgentFlow Core - LLM Node

Language model node that calls AI models for text generation.
Supports Gemini AI (primary) and other LLM providers.
"""

import os
from typing import Any, Dict, Optional

from agentflow_core.nodes.base_node import (
    NodeCallable,
    create_node_wrapper,
    get_metadata_value,
    interpolate_template,
)
from agentflow_core.runtime.registry import get_source, has_source
from agentflow_core.runtime.state import GraphState, add_tokens, merge_state
from agentflow_core.utils.error_handler import NodeExecutionError, SourceNotFoundError
from agentflow_core.utils.logger import get_logger

logger = get_logger(__name__)


# =============================================================================
# LLM Node Factory
# =============================================================================


def create_llm_node(
    node_id: str,
    metadata: Optional[Dict[str, Any]] = None
) -> NodeCallable:
    """
    Create an LLM node that calls a language model.
    
    The LLM node generates text using configured AI models.
    It supports template-based prompts with variable interpolation.
    
    Args:
        node_id: Unique identifier for this node
        metadata: Configuration options:
            - source_id: ID of the LLM source to use
            - prompt: Static prompt text
            - prompt_template: Template with {placeholders}
            - system_prompt: Optional system prompt
            - temperature: Model temperature (0-2)
            - max_tokens: Maximum tokens to generate
            - output_key: State key for output (default: "text_result")
    
    Returns:
        A callable that performs LLM inference
        
    Example:
        >>> node = create_llm_node("llm_1", {
        ...     "source_id": "gemini-llm",
        ...     "prompt_template": "Respond to: {user_input}",
        ...     "temperature": 0.7
        ... })
    """
    _metadata = metadata or {}
    
    def execute(state: GraphState, meta: Dict[str, Any]) -> GraphState:
        """Execute LLM node logic."""
        source_id = get_metadata_value(meta, "source_id")
        prompt = get_metadata_value(meta, "prompt")
        prompt_template = get_metadata_value(meta, "prompt_template")
        system_prompt = get_metadata_value(meta, "system_prompt")
        temperature = get_metadata_value(meta, "temperature", 0.7)
        max_tokens = get_metadata_value(meta, "max_tokens", 4096)
        output_key = get_metadata_value(meta, "output_key", "text_result")
        
        # Build prompt from template or static prompt
        if prompt_template:
            final_prompt = interpolate_template(prompt_template, state)
        elif prompt:
            final_prompt = prompt
        else:
            # Use user_input as prompt if nothing else specified
            final_prompt = state.get("user_input", "")
        
        if not final_prompt:
            raise NodeExecutionError(
                message="No prompt provided for LLM node",
                node_id=node_id,
                node_type="llm"
            )
        
        # Get source configuration
        source_config = _get_llm_source_config(source_id, meta)
        
        # Call LLM
        result, tokens_used = _call_llm(
            source_config=source_config,
            prompt=final_prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            node_id=node_id
        )
        
        logger.info(
            "llm_node_completed",
            node_id=node_id,
            tokens_used=tokens_used,
            output_length=len(result)
        )
        
        # Update state
        updated_state = merge_state(state, {output_key: result})
        updated_state = add_tokens(updated_state, tokens_used)
        
        return updated_state
    
    return create_node_wrapper(node_id, "llm", execute, _metadata)


# =============================================================================
# LLM Source Configuration
# =============================================================================


def _get_llm_source_config(
    source_id: Optional[str],
    metadata: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Get LLM source configuration.
    
    Priority:
    1. Registered source by source_id
    2. Inline configuration in metadata
    3. Environment variables (default)
    """
    # Try to get registered source
    if source_id and has_source(source_id):
        source = get_source(source_id)
        return source.get("config", {})
    
    # Check for inline configuration
    if metadata.get("model") or metadata.get("api_key_env"):
        return {
            "model": metadata.get("model", "gemini-2.5-flash"),
            "api_key_env": metadata.get("api_key_env", "GEMINI_API_KEY"),
            "provider": metadata.get("provider", "gemini"),
        }
    
    # Default to Gemini from environment
    return {
        "model": os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
        "api_key_env": "GEMINI_API_KEY",
        "provider": "gemini",
    }


# =============================================================================
# LLM Calling
# =============================================================================


def _call_llm(
    source_config: Dict[str, Any],
    prompt: str,
    system_prompt: Optional[str],
    temperature: float,
    max_tokens: int,
    node_id: str
) -> tuple[str, int]:
    """
    Call the LLM API and return the result.
    
    Returns:
        Tuple of (generated_text, tokens_used)
    """
    provider = source_config.get("provider", "gemini")
    
    if provider == "gemini":
        return _call_gemini(
            source_config=source_config,
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            node_id=node_id
        )
    else:
        raise NodeExecutionError(
            message=f"Unsupported LLM provider: {provider}",
            node_id=node_id,
            node_type="llm"
        )


def _call_gemini(
    source_config: Dict[str, Any],
    prompt: str,
    system_prompt: Optional[str],
    temperature: float,
    max_tokens: int,
    node_id: str
) -> tuple[str, int]:
    """
    Call Google Gemini API.
    
    Returns:
        Tuple of (generated_text, tokens_used)
    """
    try:
        import google.generativeai as genai
    except ImportError:
        raise NodeExecutionError(
            message="google-generativeai package not installed",
            node_id=node_id,
            node_type="llm"
        )
    
    # Get API key
    api_key_env = source_config.get("api_key_env", "GEMINI_API_KEY")
    api_key = os.getenv(api_key_env)
    
    if not api_key:
        raise NodeExecutionError(
            message=f"API key not found in environment variable: {api_key_env}",
            node_id=node_id,
            node_type="llm"
        )
    
    # Configure Gemini
    genai.configure(api_key=api_key)
    
    # Get model
    model_name = source_config.get("model", source_config.get("model_name", "gemini-2.5-flash"))
    
    # Create generation config
    generation_config = genai.GenerationConfig(
        temperature=temperature,
        max_output_tokens=max_tokens,
    )
    
    try:
        # Create model instance
        model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=system_prompt,
            generation_config=generation_config,
        )
        
        # Generate response
        response = model.generate_content(prompt)
        
        # Extract text
        generated_text = response.text if response.text else ""
        
        # Get token count (approximate if not available)
        tokens_used = 0
        if hasattr(response, "usage_metadata"):
            usage = response.usage_metadata
            tokens_used = getattr(usage, "total_token_count", 0)
        else:
            # Approximate: 4 chars per token
            tokens_used = (len(prompt) + len(generated_text)) // 4
        
        logger.info(
            "gemini_call_success",
            model=model_name,
            prompt_length=len(prompt),
            response_length=len(generated_text),
            tokens_used=tokens_used
        )
        
        return generated_text, tokens_used
        
    except Exception as e:
        logger.error(
            "gemini_call_failed",
            model=model_name,
            error=str(e)
        )
        raise NodeExecutionError(
            message=f"Gemini API call failed: {str(e)}",
            node_id=node_id,
            node_type="llm",
            original_error=e
        )


# =============================================================================
# Async Version (for future use)
# =============================================================================


async def create_llm_node_async(
    node_id: str,
    metadata: Optional[Dict[str, Any]] = None
) -> NodeCallable:
    """
    Create an async LLM node.
    
    Note: Currently not implemented. Use sync version.
    """
    raise NotImplementedError("Async LLM node not yet implemented")
