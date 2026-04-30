import requests
import os
from pathlib import Path
from typing import Optional


def generate_image(prompt: str, api_key: Optional[str] = None) -> str:
    """
    Generate an image for `prompt` using the free Pollinations endpoint and
    save it to disk.

    Args:
        prompt: Text prompt describing the image.
        api_key: Kept for backward compatibility, but ignored by the free endpoint.

    Returns:
        Absolute path to the saved image file.

    Raises:
        Exception: if the API call fails.
    """
    # Match the working test script exactly: fixed free model and no Authorization header.
    model = "flux"
    base_url = os.environ.get("POLLINATIONS_BASE_URL", "https://image.pollinations.ai/prompt")
    encoded_prompt = requests.utils.quote(prompt, safe="")
    url = f"{base_url}/{encoded_prompt}?model={requests.utils.quote(model)}&nologo=true"

    resp = requests.get(url, timeout=30)
    if resp.status_code == 200:
        output_dir = Path(os.environ.get("POLLINATIONS_OUTPUT_DIR", "generated_images"))
        output_dir.mkdir(parents=True, exist_ok=True)

        file_path = output_dir / f"ai_image_{os.getpid()}_{abs(hash(prompt)) & 0xFFFFFFFF:08x}.jpg"
        file_path.write_bytes(resp.content)
        return str(file_path.resolve())
    else:
        text = resp.text or ""
        raise Exception(f"Image generation failed: {resp.status_code} - {text}")
