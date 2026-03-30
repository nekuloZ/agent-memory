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
Batch edit images using Nano Banana Pro API.

Usage examples:
    # Process a directory
    uv run batch_edit_images.py -i "分镜图" -o "输出目录" -p "remove all text"
    
    # Process specific files
    uv run batch_edit_images.py -f "img1.jpg" "img2.jpg" -o "输出目录" -p "remove subtitles"
    
    # Process with custom naming
    uv run batch_edit_images.py -i "input" -o "output" -p "clean" --prefix "cleaned_"
"""

import argparse
import os
import sys
from pathlib import Path
import requests
from io import BytesIO
import base64
from datetime import datetime

# Load .env file if exists
try:
    from dotenv import load_dotenv
    for env_path in [Path(".env"), Path(__file__).parent.parent.parent.parent / ".env"]:
        if env_path.exists():
            load_dotenv(env_path)
            break
except ImportError:
    pass


def get_api_key() -> str | None:
    return os.environ.get("NANO_BANANA_API_KEY") or os.environ.get("GEMINI_API_KEY")


def get_api_config():
    """Get API URL and model name based on environment."""
    url = os.environ.get("NANO_BANANA_API_URL", "http://154.36.173.51:3000").rstrip("/")
    model = os.environ.get("NANO_BANANA_MODEL", "「Rim」gemini-3-pro-image-preview")
    return url, model


def edit_image(input_path: Path, output_path: Path, prompt: str, api_url: str, model: str, api_key: str, resolution: str = "2K") -> bool:
    """Edit a single image. Returns True on success."""
    from PIL import Image as PILImage
    
    # Load image
    img = PILImage.open(input_path)
    
    # Convert to base64
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    image_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
    
    # Build request
    body = {
        "contents": [{
            "role": "user",
            "parts": [
                {
                    "inlineData": {
                        "mimeType": "image/png",
                        "data": image_base64
                    }
                },
                {"text": prompt}
            ]
        }],
        "generationConfig": {
            "responseModalities": ["TEXT", "IMAGE"],
            "imageConfig": {
                "imageSize": resolution
            }
        }
    }
    
    headers = {
        "x-goog-api-key": api_key,
        "Content-Type": "application/json"
    }
    
    response = requests.post(
        f"{api_url}/v1beta/models/{model}:generateContent",
        json=body,
        headers=headers,
        timeout=180
    )
    response.raise_for_status()
    
    result = response.json()
    
    # Save output image
    if "candidates" in result:
        for part in result["candidates"][0]["content"]["parts"]:
            if "inlineData" in part:
                image_data = base64.b64decode(part["inlineData"]["data"])
                output_img = PILImage.open(BytesIO(image_data))
                
                # Ensure RGB mode
                if output_img.mode == 'RGBA':
                    rgb_img = PILImage.new('RGB', output_img.size, (255, 255, 255))
                    rgb_img.paste(output_img, mask=output_img.split()[3])
                    rgb_img.save(output_path, 'PNG')
                elif output_img.mode == 'RGB':
                    output_img.save(output_path, 'PNG')
                else:
                    output_img.convert('RGB').save(output_path, 'PNG')
                return True
    
    return False


def get_output_name(input_path: Path, prefix: str = "", suffix: str = "", use_timestamp: bool = False) -> str:
    """Generate output filename based on input and naming options."""
    parts = []
    if use_timestamp:
        parts.append(datetime.now().strftime("%Y%m%d-%H%M%S"))
    if prefix:
        parts.append(prefix)
    parts.append(input_path.stem)
    if suffix:
        parts.append(suffix)
    return "-".join(parts) + ".png"


def collect_input_files(args) -> list[Path]:
    """Collect all input files from various sources."""
    files = []
    
    # From explicit file list
    if args.files:
        for f in args.files:
            p = Path(f)
            if p.exists():
                files.append(p)
            else:
                print(f"Warning: File not found: {f}", file=sys.stderr)
    
    # From input directory
    if args.input_dir:
        input_dir = Path(args.input_dir)
        if input_dir.exists():
            # Support multiple patterns
            patterns = args.pattern.split(",") if "," in args.pattern else [args.pattern]
            for pattern in patterns:
                files.extend(input_dir.glob(pattern.strip()))
        else:
            print(f"Warning: Directory not found: {args.input_dir}", file=sys.stderr)
    
    # From recursive search
    if args.recursive and args.input_dir:
        input_dir = Path(args.input_dir)
        if input_dir.exists():
            patterns = args.pattern.split(",") if "," in args.pattern else [args.pattern]
            for pattern in patterns:
                files.extend(input_dir.rglob(pattern.strip()))
    
    # Remove duplicates and sort
    unique_files = sorted(set(files))
    return unique_files


def main():
    parser = argparse.ArgumentParser(
        description="Batch edit images using Nano Banana Pro",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Directory mode
  %(prog)s -i "input" -o "output" -p "remove text"
  
  # File mode
  %(prog)s -f img1.jpg img2.jpg -o "output" -p "clean"
  
  # With custom naming
  %(prog)s -i "input" -o "output" -p "remove text" --prefix "clean"
  
  # Multiple patterns
  %(prog)s -i "input" -o "output" -p "fix" --pattern "*.jpg,*.png"
  
  # Recursive
  %(prog)s -i "input" -o "output" -p "enhance" -r
        """
    )
    
    # Input options (mutually exclusive groups not enforced to allow flexibility)
    parser.add_argument("-i", "--input-dir", help="Input directory containing images")
    parser.add_argument("-f", "--files", nargs="+", help="Specific image files to process")
    
    # Output options
    parser.add_argument("-o", "--output-dir", required=True, help="Output directory for edited images")
    parser.add_argument("--prefix", default="", help="Prefix for output filenames")
    parser.add_argument("--suffix", default="", help="Suffix for output filenames")
    parser.add_argument("--timestamp", action="store_true", help="Add timestamp to filenames")
    parser.add_argument("--keep-name", action="store_true", help="Keep original filename (no timestamp/prefix/suffix)")
    
    # Processing options
    parser.add_argument("-p", "--prompt", required=True, help="Editing prompt (e.g., 'remove all subtitles')")
    parser.add_argument("--pattern", default="*.jpg", help="File pattern(s), comma-separated (default: *.jpg)")
    parser.add_argument("-r", "--recursive", action="store_true", help="Search recursively in input directory")
    parser.add_argument("--resolution", choices=["1K", "2K", "4K"], default="2K", help="Output resolution")
    parser.add_argument("--timeout", type=int, default=180, help="API timeout in seconds")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be processed without actually editing")
    
    args = parser.parse_args()
    
    # Validate inputs
    if not args.input_dir and not args.files:
        print("Error: Must specify either --input-dir or --files", file=sys.stderr)
        sys.exit(1)
    
    # Get API credentials
    api_key = get_api_key()
    if not api_key:
        print("Error: No API key. Set NANO_BANANA_API_KEY or GEMINI_API_KEY", file=sys.stderr)
        sys.exit(1)
    
    api_url, model = get_api_config()
    
    # Collect files
    images = collect_input_files(args)
    
    if not images:
        print("No images found to process", file=sys.stderr)
        sys.exit(1)
    
    # Setup output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Dry run mode
    if args.dry_run:
        print(f"[DRY RUN] Would process {len(images)} images:")
        for img in images:
            if args.keep_name:
                out_name = img.stem + ".png"
            else:
                out_name = get_output_name(img, args.prefix, args.suffix, args.timestamp)
            print(f"  {img} -> {output_dir / out_name}")
        return
    
    # Process
    print(f"Found {len(images)} images to process")
    print(f"Output directory: {output_dir.resolve()}")
    print(f"Prompt: {args.prompt}")
    print()
    
    success_count = 0
    fail_count = 0
    
    for idx, img_path in enumerate(images, 1):
        # Generate output name
        if args.keep_name:
            output_name = img_path.stem + ".png"
        else:
            output_name = get_output_name(img_path, args.prefix, args.suffix, args.timestamp)
        output_path = output_dir / output_name
        
        print(f"[{idx}/{len(images)}] {img_path.name} -> {output_name}", end=" ")
        sys.stdout.flush()
        
        try:
            if edit_image(img_path, output_path, args.prompt, api_url, model, api_key, args.resolution):
                print("OK")
                success_count += 1
            else:
                print("FAILED (no image in response)")
                fail_count += 1
        except Exception as e:
            print(f"ERROR: {e}")
            fail_count += 1
    
    print()
    print(f"Done! Success: {success_count}, Failed: {fail_count}")
    print(f"Output: {output_dir.resolve()}")


if __name__ == "__main__":
    main()
