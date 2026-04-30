import base64
import os
from pathlib import Path

import requests

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None


def main() -> None:
    if load_dotenv is not None:
        load_dotenv()

    prompt = os.environ.get(
        "TEST_IMAGE_PROMPT",
        "a cute cat",
    )
    model = "flux"
    output_file = Path(os.environ.get("TEST_IMAGE_OUTPUT", "ai_image.jpg"))
    base_url = os.environ.get("TEST_IMAGE_BASE_URL", "https://image.pollinations.ai/prompt")

    url = f"{base_url}/{requests.utils.quote(prompt, safe='')}?model={model}&nologo=true"

    print(f"Prompt: {prompt}")
    print(f"Model: {model}")
    print(f"URL: {url}")

    response = requests.get(url, timeout=60)
    print(f"Status: {response.status_code}")

    if response.status_code != 200:
        print("报错了:")
        print(response.text)
        raise SystemExit(1)

    output_file.write_bytes(response.content)
    print(f"Saved image to: {output_file.resolve()}")
    print(f"Bytes: {len(response.content)}")
    print(f"Base64 preview: {base64.b64encode(response.content)[:60].decode('utf-8', errors='ignore')}...")


if __name__ == "__main__":
    main()
