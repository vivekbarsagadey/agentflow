"""
AgentFlow Core - Gemini Image Source Adapter

Adapter for Google Imagen and Gemini image generation.
Provides a unified interface for image generation operations.
"""

import os
from typing import Any, Dict, Optional

from agentflow_core.utils.error_handler import SourceConnectionError
from agentflow_core.utils.logger import get_logger

logger = get_logger(__name__)


# =============================================================================
# Constants
# =============================================================================

DEFAULT_SIZE = "1024x1024"
SUPPORTED_SIZES = ["256x256", "512x512", "1024x1024", "1792x1024", "1024x1792"]


# =============================================================================
# Image Client Factory
# =============================================================================


def create_image_client(config: Dict[str, Any]) -> Any:
    """
    Create an image generation client from configuration.
    
    Args:
        config: Source configuration dictionary
            - api_key_env: Environment variable name for API key
            - model: Image model name
    
    Returns:
        Configured client instance
        
    Raises:
        SourceConnectionError: If client creation fails
    """
    try:
        import google.generativeai as genai
    except ImportError:
        raise SourceConnectionError(
            message="google-generativeai package not installed",
            source_id="gemini-image",
            source_kind="image"
        )
    
    # Get API key
    api_key = config.get("api_key")
    if not api_key:
        api_key_env = config.get("api_key_env", "GEMINI_API_KEY")
        api_key = os.getenv(api_key_env)
    
    if not api_key:
        raise SourceConnectionError(
            message=f"Gemini API key not found",
            source_id="gemini-image",
            source_kind="image"
        )
    
    genai.configure(api_key=api_key)
    
    logger.info("gemini_image_client_created")
    
    return genai


def get_image_client(config: Dict[str, Any]) -> Any:
    """Alias for create_image_client."""
    return create_image_client(config)


# =============================================================================
# Image Generation
# =============================================================================


def generate_image(
    client: Any,
    prompt: str,
    size: str = DEFAULT_SIZE,
    quality: str = "standard",
    style: str = "vivid",
    **kwargs: Any
) -> Dict[str, Any]:
    """
    Generate an image using Gemini/Imagen.
    
    Args:
        client: Configured genai module
        prompt: Description of image to generate
        size: Image size (e.g., "1024x1024")
        quality: Image quality (standard, hd)
        style: Image style (vivid, natural)
        **kwargs: Additional parameters
        
    Returns:
        Dictionary with:
            - type: Image type (url, base64, placeholder)
            - url: Image URL (if available)
            - data: Base64 data (if available)
            - prompt: Original prompt
            - model: Model used
            - size: Image dimensions
    """
    # Parse size
    width, height = _parse_size(size)
    
    try:
        # Try using Gemini's image generation
        # Note: Imagen API access may require specific setup
        model_name = kwargs.get("model", "gemini-1.5-flash")
        
        model = client.GenerativeModel(model_name)
        
        # Create an enhanced prompt for image description
        enhanced_prompt = f"""
        Generate a detailed visual description for the following image request:
        "{prompt}"
        
        Describe what the image should look like in detail.
        """
        
        response = model.generate_content(enhanced_prompt)
        
        # For now, return a placeholder with the description
        # Actual image generation requires Imagen API access
        return {
            "type": "description",
            "description": response.text if response.text else prompt,
            "prompt": prompt,
            "model": model_name,
            "size": size,
            "width": width,
            "height": height,
            "note": "Text description generated. For actual images, configure Imagen API.",
        }
        
    except Exception as e:
        logger.warning(
            "gemini_image_generation_fallback",
            error=str(e)
        )
        
        # Return placeholder
        return {
            "type": "placeholder",
            "url": f"https://via.placeholder.com/{width}x{height}?text=Image",
            "prompt": prompt,
            "model": "placeholder",
            "size": size,
            "width": width,
            "height": height,
            "error": str(e),
        }


def _parse_size(size: str) -> tuple[int, int]:
    """Parse size string to width and height."""
    if "x" in size:
        parts = size.split("x")
        try:
            return int(parts[0]), int(parts[1])
        except ValueError:
            pass
    return 1024, 1024


# =============================================================================
# Utility Functions
# =============================================================================


def is_image_generation_available() -> bool:
    """
    Check if image generation is available.
    
    Returns:
        True if Imagen API is accessible
    """
    try:
        import google.generativeai as genai
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return False
        genai.configure(api_key=api_key)
        return True
    except Exception:
        return False
