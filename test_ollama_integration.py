#!/root/.openclaw/workspace/polish/xander-operator/.venv/bin/python
import os, sys
from pathlib import Path

# Load .env
workspace = Path("/root/.openclaw/workspace")
env_path = workspace / ".env"
if env_path.exists():
    for line in env_path.read_text().splitlines():
        if line.strip() and not line.startswith('#'):
            k, _, v = line.partition("=")
            os.environ[k.strip()] = v.strip()

# Ensure operator on path
sys.path.insert(0, str(workspace / "polish" / "xander-operator"))

from xander_operator.llm import generate_response

prompt = "Create a simple HTML button with Tailwind classes, purple gradient, and hover effect."
print("Generating via Ollama...", file=sys.stderr)
out = generate_response(prompt, model="qwen2.5-coder:7b", max_tokens=500, temperature=0.3, use_cache=False)
if out:
    print("\n--- OUTPUT ---\n")
    print(out)
else:
    print("FAILED", file=sys.stderr)
    sys.exit(1)
