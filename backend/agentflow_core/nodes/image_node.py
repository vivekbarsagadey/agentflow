"""
AgentFlow Core - Image Node

Image generation node that creates images using AI models.
Supports Google Imagen and other image generation providers.
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
from agentflow_core.utils.error_handler import NodeExecutionError
from agentflow_core.utils.logger import get_logger

logger = get_logger(__name__)


# =============================================================================
# Image Node Factory
# =============================================================================


def create_image_node(
    node_id: str,
    metadata: Optional[Dict[str, Any]] = None
) -> NodeCallable:
    """
    Create an image node that generates images.
    
    The image node generates images using configured AI models.
    It supports template-based prompts with variable interpolation.
    
    Args:
        node_id: Unique identifier for this node
        metadata: Configuration options:
            - source_id: ID of the image source to use
            - prompt: Static prompt text
            - prompt_template: Template with {placeholders}
            - size: Image size (e.g., "1024x1024")
            - quality: Image quality (standard, hd)
            - style: Image style (vivid, natural)
            - output_key: State key for output (default: "image_result")
    
    Returns:
        A callable that performs image generation
        
    Example:
        >>> node = create_image_node("image_1", {
        ...     "source_id": "gemini-imagen",
        ...     "prompt_template": "Generate an image of: {user_input}",
        ...     "size": "1024x1024"
        ... })
    """
    _metadata = metadata or {}
    
    def execute(state: GraphState, meta: Dict[str, Any]) -> GraphState:
        """Execute image node logic."""
        source_id = get_metadata_value(meta, "source_id")
        prompt = get_metadata_value(meta, "prompt")
        prompt_template = get_metadata_value(meta, "prompt_template")
        size = get_metadata_value(meta, "size", "1024x1024")
        quality = get_metadata_value(meta, "quality", "standard")
        style = get_metadata_value(meta, "style", "vivid")
        output_key = get_metadata_value(meta, "output_key", "image_result")
        
        # Build prompt from template or static prompt
        if prompt_template:
            final_prompt = interpolate_template(prompt_template, state)
        elif prompt:
            final_prompt = prompt
        else:
            # Use text_result or user_input as prompt
            final_prompt = state.get("text_result") or state.get("user_input", "")
        
        if not final_prompt:
            raise NodeExecutionError(
                message="No prompt provided for image node",
                node_id=node_id,
                node_type="image"
            )
        
        # Get source configuration
        source_config = _get_image_source_config(source_id, meta)
        
        # Generate image
        result = _generate_image(
            source_config=source_config,
            prompt=final_prompt,
            size=size,
            quality=quality,
            style=style,
            node_id=node_id
        )
        
        logger.info(
            "image_node_completed",
            node_id=node_id,
            has_url="url" in result
        )
        
        # Update state
        return merge_state(state, {output_key: result})
    
    return create_node_wrapper(node_id, "image", execute, _metadata)


# =============================================================================
# Image Source Configuration
# =============================================================================


def _get_image_source_config(
    source_id: Optional[str],
    metadata: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Get image source configuration.
    """
    # Try to get registered source
    if source_id and has_source(source_id):
        source = get_source(source_id)
        return source.get("config", {})
    
    # Check for inline configuration
    if metadata.get("model") or metadata.get("api_key_env"):
        return {
            "model": metadata.get("model", "imagen-3.0"),
            "api_key_env": metadata.get("api_key_env", "GEMINI_API_KEY"),
            "provider": metadata.get("provider", "gemini"),
        }
    
    # Default to Gemini Imagen
    return {
        "model": os.getenv("IMAGEN_MODEL", "imagen-3.0"),
        "api_key_env": "GEMINI_API_KEY",
        "provider": "gemini",
    }


# =============================================================================
# Image Generation
# =============================================================================


def _generate_image(
    source_config: Dict[str, Any],
    prompt: str,
    size: str,
    quality: str,
    style: str,
    node_id: str
) -> Dict[str, Any]:
    """
    Generate an image using the configured provider.
    
    Returns:
        Dictionary with image details (url, prompt, model, size, etc.)
    """
    provider = source_config.get("provider", "gemini")
    
    if provider == "gemini":
        return _generate_with_gemini(
            source_config=source_config,
            prompt=prompt,
            size=size,
            node_id=node_id
        )
    else:
        # Fallback: Return placeholder for unsupported providers
        logger.warning(
            "unsupported_image_provider",
            provider=provider,
            using_placeholder=True
        )
        return _generate_placeholder(prompt, size)


def _generate_with_gemini(
    source_config: Dict[str, Any],
    prompt: str,
    size: str,
    node_id: str
) -> Dict[str, Any]:
    """
    Generate image using Gemini/Imagen.
    
    Note: Gemini's image generation (Imagen) requires specific API access.
    This implementation uses the genai library if available.
    """
    try:
        import google.generativeai as genai
    except ImportError:
        logger.warning("google-generativeai not installed, using placeholder")
        return _generate_placeholder(prompt, size)
    
    # Get API key
    api_key_env = source_config.get("api_key_env", "GEMINI_API_KEY")
    api_key = os.getenv(api_key_env)
    
    if not api_key:
        logger.warning(
            "gemini_api_key_not_found",
            env_var=api_key_env,
            using_placeholder=True
        )
        return _generate_placeholder(prompt, size)
    
    # Configure Gemini
    genai.configure(api_key=api_key)
    
    model_name = source_config.get("model", "imagen-3.0")
    
    try:
        # Note: Imagen API might require different configuration
        # For now, we try to use the experimental image generation
        # If it fails, we return a placeholder
        
        # Try using Gemini's image generation capabilities
        model = genai.GenerativeModel(model_name)
        
        # Generate with image generation prompt
        response = model.generate_content(
            f"Generate an image based on this description: {prompt}"
        )
        
        # Check if response contains an image
        if hasattr(response, "candidates") and response.candidates:
            for candidate in response.candidates:
                if hasattr(candidate, "content") and candidate.content:
                    for part in candidate.content.parts:
                        if hasattr(part, "inline_data"):
                            # Image data found
                            return {
                                "type": "base64",
                                "data": part.inline_data.data,
                                "mime_type": part.inline_data.mime_type,
                                "prompt": prompt,
                                "model": model_name,
                                "size": size,
                            }
        
        # No image in response, return placeholder
        logger.info("gemini_image_generation_no_image_in_response")
        return _generate_placeholder(prompt, size)
        
    except Exception as e:
        logger.warning(
            "gemini_image_generation_failed",
            error=str(e),
            using_placeholder=True
        )
        return _generate_placeholder(prompt, size)


def _generate_placeholder(prompt: str, size: str) -> Dict[str, Any]:
    """
    Generate a placeholder image result.
    
    Used when actual image generation is not available.
    """
    # Parse size
    width, height = 1024, 1024
    if "x" in size:
        parts = size.split("x")
        try:
            width, height = int(parts[0]), int(parts[1])
        except ValueError:
            pass
    
    return {
        "type": "placeholder",
        "url": f"https://via.placeholder.com/{width}x{height}?text={prompt[:20]}...",
        "prompt": prompt,
        "model": "placeholder",
        "size": size,
        "width": width,
        "height": height,
        "note": "Image generation not available. This is a placeholder.",
    }
