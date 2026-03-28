#!/root/.openclaw/workspace/polish/xander-operator/.venv/bin/python
"""
Test Ollama integration with xander_operator.llm
"""

import os, sys, time
from pathlib import Path

# Load .env
workspace = Path(__file__).parent.parent.parent.parent
env_path = workspace / ".env"
if env_path.exists():
    for line in env_path.read_text().splitlines():
        if line.strip() and not line.startswith('#'):
            k, _, v = line.partition("=")
            os.environ[k.strip()] = v.strip()

# Add operator to path
sys.path.insert(0, str(workspace / "polish" / "xander-operator"))

from xander_operator.llm import generate_response

prompt = "Generate a simple HTML button with Tailwind classes, purple gradient, and hover effect."
model = os.getenv("OPENAI_MODEL", "qwen2.5-coder:7b")

print(f"Using model: {model}", file=sys.stderr)
print(f"OLLAMA_BASE_URL: {os.getenv('OLLAMA_BASE_URL')}", file=sys.stderr)

for attempt in range(1, 4):
    try:
        resp = generate_response(
            prompt,
            model=model,
            max_tokens=500,
            temperature=0.3,
            use_cache=False
        )
        if resp:
            print("SUCCESS:\n")
            print(resp)
            break
        else:
            print(f"Attempt {attempt}: empty response, retrying...", file=sys.stderr)
    except Exception as e:
        print(f"Attempt {attempt} error: {e}", file=sys.stderr)
        if attempt < 3:
            time.sleep(2)
        else:
            print("FAILED after 3 attempts", file=sys.stderr)
            sys.exit(1)
