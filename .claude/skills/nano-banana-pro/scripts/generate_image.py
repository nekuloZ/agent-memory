#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "requests>=2.31.0",
#     "pillow>=10.0.0",
#     "python-dotenv>=1.0.0",
# ]
# ///
"""
Generate images using Nano Banana Pro API with custom endpoint support.
Features: Auto-failover to backup models if primary fails.

Usage:
    uv run generate_image.py --prompt "your image description" --filename "output.png" [--resolution 1K|2K|4K] [--api-key KEY] [--api-url URL]

Available models (auto-failover order):
    - 「Rim」gemini-3-pro-image-preview (default)
    - 「WF」gemini-3-pro-image-preview (fallback 1)
    - 「YS」gemini-3-pro-image-preview (fallback 2)
    - 「XQ」gemini-3-pro-image-preview (fallback 3)

Environment variables:
    NANO_BANANA_API_URL - API endpoint
    NANO_BANANA_API_KEY - API key
    NANO_BANANA_MODEL_RIM - Primary model (default: 「Rim」gemini-3-pro-image-preview)
    NANO_BANANA_AUTO_FAILOVER - Enable auto-failover (default: true)
    NANO_BANANA_FAILOVER_MODELS - Comma-separated fallback models
"""

import argparse
import os
import sys
import time
from pathlib import Path
import requests
from io import BytesIO
import base64

# Load .env file if it exists
try:
    from dotenv import load_dotenv
    # Try to load .env from current directory and project root
    env_loaded = False
    for env_path in [Path(".env"), Path(__file__).parent.parent.parent.parent / ".env"]:
        if env_path.exists():
            load_dotenv(env_path)
            env_loaded = True
            break
except ImportError:
    pass  # python-dotenv not available


# ============================================
# Model Configuration with Auto-Failover
# ============================================

# All available models with priority order (higher index = lower priority)
DEFAULT_MODEL_PRIORITY = [
    "「Rim」gemini-3-pro-image-preview",       # Primary - stable
    "「YQ」gemini-3-pro-image-preview",        # Fallback 1 - YQ Pro
    "「Rim」gemini-3.1-flash-image-preview",   # Fallback 2 - Rim 3.1 flash
    "「YQ」gemini-3.1-flash-image-preview",    # Fallback 3 - YQ 3.1 flash
]

# Model characteristics for logging
MODEL_INFO = {
    "「Rim」gemini-3-pro-image-preview": {"name": "Rim 3 Pro", "desc": "稳定均衡"},
    "「YQ」gemini-3-pro-image-preview": {"name": "YQ 3 Pro", "desc": "备用稳定"},
    "「Rim」gemini-3.1-flash-image-preview": {"name": "Rim 3.1", "desc": "快速轻量"},
    "「YQ」gemini-3.1-flash-image-preview": {"name": "YQ 3.1", "desc": "快速备用"},
}


def get_api_key(provided_key: str | None) -> str | None:
    """Get API key from argument first, then environment."""
    if provided_key:
        return provided_key
    return os.environ.get("NANO_BANANA_API_KEY") or os.environ.get("GEMINI_API_KEY")


def get_api_url(provided_url: str | None, provider: str | None = None) -> str:
    """Get API URL from argument first, then provider config, then environment, then default."""
    if provided_url:
        return provided_url.rstrip("/")

    # Provider-specific default URLs
    provider_urls = {
        "google": "https://generativelanguage.googleapis.com",
        "rim": "http://64.186.244.43:12001",
    }

    # Check provider-specific env var first
    if provider:
        env_var = f"NANO_BANANA_API_URL_{provider.upper()}"
        env_url = os.environ.get(env_var)
        if env_url:
            return env_url.rstrip("/")
        # Return provider default
        if provider in provider_urls:
            return provider_urls[provider]

    # Fall back to generic env var
    env_url = os.environ.get("NANO_BANANA_API_URL")
    if env_url:
        return env_url.rstrip("/")

    # Default to Google's endpoint if not specified
    return provider_urls.get(provider, "https://generativelanguage.googleapis.com")


def get_model_priority_list() -> list[str]:
    """Get the list of models to try in order (with failover support)."""
    # Check if user specified a custom primary model
    custom_primary = os.environ.get("NANO_BANANA_MODEL_RIM")
    
    # Check if user specified custom failover models
    custom_fallbacks = os.environ.get("NANO_BANANA_FAILOVER_MODELS")
    
    if custom_fallbacks:
        # User specified custom failover chain
        models = [m.strip() for m in custom_fallbacks.split(",") if m.strip()]
        return models
    
    # Build priority list starting with custom primary (if set)
    priority_list = []
    if custom_primary and custom_primary not in priority_list:
        priority_list.append(custom_primary)
    
    # Add remaining models from default list
    for model in DEFAULT_MODEL_PRIORITY:
        if model not in priority_list:
            priority_list.append(model)
    
    return priority_list


def is_auto_failover_enabled() -> bool:
    """Check if auto-failover is enabled."""
    env_value = os.environ.get("NANO_BANANA_AUTO_FAILOVER", "true").lower()
    return env_value in ("true", "1", "yes", "on")


def calculate_image_size(width: int | None, height: int | None, aspect: str | None, resolution: str, input_image=None) -> tuple[int, int]:
    """Calculate final image width and height based on parameters.

    Returns: (width, height) tuple
    """
    # Priority 1: Explicit width and height
    if width and height:
        return width, height
    elif width and not height:
        # Calculate height from aspect ratio or default to 4:3
        if aspect:
            height = int(width / parse_aspect_ratio(aspect))
        else:
            height = int(width * 3 / 4)
        return width, height
    elif height and not width:
        # Calculate width from aspect ratio or default to 4:3
        if aspect:
            width = int(height * parse_aspect_ratio(aspect))
        else:
            width = int(height * 4 / 3)
        return width, height

    # Priority 2: Aspect ratio with resolution base
    if aspect:
        base_sizes = {"1K": 1024, "2K": 2048, "4K": 4096}
        base = base_sizes.get(resolution, 1024)
        ratio = parse_aspect_ratio(aspect)
        if ratio >= 1:
            # Landscape: width is base
            width = base
            height = int(base / ratio)
        else:
            # Portrait: height is base
            height = base
            width = int(base * ratio)
        return width, height

    # Priority 3: Resolution only (default 1:1 for simplicity)
    base_sizes = {"1K": 1024, "2K": 2048, "4K": 4096}
    base = base_sizes.get(resolution, 1024)
    return base, base


def parse_aspect_ratio(aspect: str) -> float:
    """Parse aspect ratio string like '16:9' to float (1.777...).

    Returns: width/height ratio
    """
    ratios = {
        "16:9": 16/9,
        "9:16": 9/16,
        "1:1": 1.0,
        "4:3": 4/3,
        "3:4": 3/4,
        "21:9": 21/9,
        "9:21": 9/21,
    }
    return ratios.get(aspect, 1.0)


def make_api_request(api_url: str, api_key: str, model_name: str, 
                     contents: list, generation_config: dict, timeout: int = 120) -> tuple[bool, dict | str]:
    """Make API request to generate image.
    
    Returns: (success: bool, result: dict or error_message: str)
    """
    try:
        headers = {
            "x-goog-api-key": api_key,
            "Content-Type": "application/json"
        }

        request_body = {
            "contents": contents,
            "generationConfig": generation_config
        }

        response = requests.post(
            f"{api_url}/v1beta/models/{model_name}:generateContent",
            json=request_body,
            headers=headers,
            timeout=timeout
        )
        
        # Check for HTTP errors
        if response.status_code == 404:
            return False, f"Model '{model_name}' not found (404)"
        elif response.status_code == 429:
            return False, f"Rate limit exceeded for '{model_name}' (429)"
        elif response.status_code == 503:
            return False, f"Service unavailable for '{model_name}' (503)"
        elif response.status_code >= 500:
            return False, f"Server error for '{model_name}' ({response.status_code})"
        
        response.raise_for_status()
        result = response.json()
        
        # Check if response contains valid image data
        if "candidates" in result and len(result["candidates"]) > 0:
            candidate = result["candidates"][0]
            if "content" in candidate and "parts" in candidate["content"]:
                for part in candidate["content"]["parts"]:
                    if "inlineData" in part:
                        return True, result  # Success with image
                    if "text" in part:
                        # Check for error messages in text
                        error_text = part["text"].lower()
                        if any(e in error_text for e in ["error", "failed", "unable", "cannot"]):
                            return False, f"Model error: {part['text']}"
        
        return False, f"No image in response from '{model_name}'"
        
    except requests.exceptions.Timeout:
        return False, f"Timeout waiting for '{model_name}'"
    except requests.exceptions.ConnectionError:
        return False, f"Connection error to '{model_name}'"
    except Exception as e:
        return False, f"Error with '{model_name}': {str(e)}"


def extract_and_save_image(result: dict, output_path: Path) -> bool:
    """Extract image from API response and save to file."""
    from PIL import Image as PILImage
    
    if "candidates" in result and len(result["candidates"]) > 0:
        candidate = result["candidates"][0]
        if "content" in candidate and "parts" in candidate["content"]:
            for part in candidate["content"]["parts"]:
                if "text" in part:
                    print(f"Model response: {part['text']}")
                elif "inlineData" in part:
                    image_data = base64.b64decode(part["inlineData"]["data"])
                    image = PILImage.open(BytesIO(image_data))

                    # Ensure RGB mode for PNG
                    if image.mode == 'RGBA':
                        rgb_image = PILImage.new('RGB', image.size, (255, 255, 255))
                        rgb_image.paste(image, mask=image.split()[3])
                        rgb_image.save(str(output_path), 'PNG')
                    elif image.mode == 'RGB':
                        image.save(str(output_path), 'PNG')
                    else:
                        image.convert('RGB').save(str(output_path), 'PNG')
                    return True
    return False


def main():
    parser = argparse.ArgumentParser(
        description="Generate images using Nano Banana Pro (Gemini 3 Pro Image) with auto-failover"
    )
    parser.add_argument(
        "--prompt", "-p",
        required=True,
        help="Image description/prompt"
    )
    parser.add_argument(
        "--filename", "-f",
        required=True,
        help="Output filename (e.g., sunset-mountains.png)"
    )
    parser.add_argument(
        "--input-image", "-i",
        action="append",
        dest="input_images",
        help="Optional input image path(s) for editing/modification. Can be specified multiple times for multi-image fusion."
    )
    parser.add_argument(
        "--resolution", "-r",
        choices=["1K", "2K", "4K"],
        default="1K",
        help="Output resolution: 1K (default), 2K, or 4K. Overridden by --width/--height or --aspect"
    )
    parser.add_argument(
        "--width", "-W",
        type=int,
        help="Custom image width in pixels"
    )
    parser.add_argument(
        "--height", "-H",
        type=int,
        help="Custom image height in pixels"
    )
    parser.add_argument(
        "--aspect", "-a",
        choices=["16:9", "9:16", "1:1", "4:3", "3:4", "21:9", "9:21"],
        help="Aspect ratio (combined with --resolution for size)"
    )
    parser.add_argument(
        "--api-key", "-k",
        help="API key (overrides NANO_BANANA_API_KEY/GEMINI_API_KEY env var)"
    )
    parser.add_argument(
        "--api-url", "-u",
        help="Custom API URL (overrides NANO_BANANA_API_URL env var)"
    )
    parser.add_argument(
        "--provider",
        choices=["google", "rim"],
        help="API provider (google or rim). If not specified, auto-detected from URL"
    )
    parser.add_argument(
        "--no-failover",
        action="store_true",
        help="Disable auto-failover to backup models"
    )
    parser.add_argument(
        "--model",
        help="Specific model to use (disables auto-failover)"
    )

    args = parser.parse_args()

    # Get API key and URL
    api_key = get_api_key(args.api_key)
    if not api_key:
        print("Error: No API key provided.", file=sys.stderr)
        print("Please either:", file=sys.stderr)
        print("  1. Provide --api-key argument", file=sys.stderr)
        print("  2. Set NANO_BANANA_API_KEY or GEMINI_API_KEY environment variable", file=sys.stderr)
        sys.exit(1)

    # Determine provider
    provider = args.provider
    if not provider:
        if args.api_url and "154.36.173.51" in args.api_url:
            provider = "rim"
        elif os.environ.get("NANO_BANANA_API_URL") and "154.36.173.51" in os.environ.get("NANO_BANANA_API_URL"):
            provider = "rim"
    
    api_url = get_api_url(args.api_url, provider)
    
    # Import PIL here
    from PIL import Image as PILImage

    # Set up output path
    output_path = Path(args.filename)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Load input image(s) if provided
    input_images = []

    # Calculate final image dimensions
    if args.input_images:
        for idx, img_path in enumerate(args.input_images, 1):
            try:
                img = PILImage.open(img_path)
                input_images.append(img)
                print(f"Loaded input image {idx}: {img_path}")
            except Exception as e:
                print(f"Error loading input image {img_path}: {e}", file=sys.stderr)
                sys.exit(1)

        first_img = input_images[0]
        if not args.width and not args.height and not args.aspect:
            img_width, img_height = first_img.size
            print(f"Using first input image size: {img_width}x{img_height}")
            final_width, final_height = img_width, img_height
        else:
            final_width, final_height = calculate_image_size(
                args.width, args.height, args.aspect, args.resolution, first_img
            )
    else:
        final_width, final_height = calculate_image_size(
            args.width, args.height, args.aspect, args.resolution
        )

    print(f"Generating image size: {final_width}x{final_height}")
    print(f"API endpoint: {api_url}")

    # Build request body
    contents = []
    if input_images:
        parts = []
        for img in input_images:
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            image_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
            parts.append({
                "inlineData": {
                    "mimeType": "image/png",
                    "data": image_base64
                }
            })
        parts.append({"text": args.prompt})
        contents.append({"role": "user", "parts": parts})
        print(f"Editing with {len(input_images)} image(s)...")
    else:
        contents.append({"role": "user", "parts": [{"text": args.prompt}]})
        print(f"Generating image with aspect ratio {args.aspect or 'auto'}...")

    generation_config = {
        "responseModalities": ["TEXT", "IMAGE"],
        "imageConfig": {"imageSize": args.resolution}
    }
    if args.aspect:
        generation_config["imageConfig"]["aspectRatio"] = args.aspect
    elif not input_images:
        generation_config["imageConfig"]["aspectRatio"] = "auto"

    # ============================================
    # Auto-Failover Logic
    # ============================================
    
    # Determine models to try
    if args.model:
        # User specified specific model
        models_to_try = [args.model]
        print(f"Using specific model: {args.model}")
    elif args.no_failover or not is_auto_failover_enabled():
        # Failover disabled
        models_to_try = [get_model_priority_list()[0]]
        model_info = MODEL_INFO.get(models_to_try[0], {"name": "Unknown", "desc": ""})
        print(f"Auto-failover disabled. Using: {model_info['name']} ({model_info['desc']})")
    else:
        # Auto-failover enabled
        models_to_try = get_model_priority_list()
        print(f"\n{'='*50}")
        print("Auto-failover enabled. Will try models in order:")
        for i, model in enumerate(models_to_try, 1):
            info = MODEL_INFO.get(model, {"name": model, "desc": ""})
            prefix = "*" if i == 1 else " "
            print(f"  {prefix} {i}. {info['name']} - {info['desc']}")
        print(f"{'='*50}\n")

    # Try each model in order
    last_error = None
    for attempt, model_name in enumerate(models_to_try, 1):
        info = MODEL_INFO.get(model_name, {"name": model_name, "desc": ""})
        
        if len(models_to_try) > 1:
            print(f"\n[Attempt {attempt}/{len(models_to_try)}] Trying {info['name']}...")
        else:
            print(f"Using model: {info['name']}")

        success, result = make_api_request(
            api_url=api_url,
            api_key=api_key,
            model_name=model_name,
            contents=contents,
            generation_config=generation_config,
            timeout=120
        )

        if success:
            # Extract and save image
            if extract_and_save_image(result, output_path):
                full_path = output_path.resolve()
                if len(models_to_try) > 1 and attempt > 1:
                    print(f"\n[OK] Success with fallback model: {info['name']}")
                else:
                    print(f"\n✓ Image saved: {full_path}")
                sys.exit(0)
            else:
                last_error = "Failed to extract image from response"
                print(f"  [FAIL] {last_error}")
        else:
            last_error = result
            print(f"  [FAIL] Failed: {last_error}")
            
            # Brief pause before trying next model
            if attempt < len(models_to_try):
                time.sleep(0.5)

    # All models failed
    print(f"\n{'='*50}", file=sys.stderr)
    print("Error: All models failed to generate image.", file=sys.stderr)
    print(f"Last error: {last_error}", file=sys.stderr)
    print(f"{'='*50}", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
