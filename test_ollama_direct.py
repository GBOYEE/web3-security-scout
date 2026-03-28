#!/root/.openclaw/workspace/polish/xander-operator/.venv/bin/python
import os, sys
from pathlib import Path

# Set env explicitly
os.environ["OLLAMA_BASE_URL"] = "http://127.0.0.1:11434"
os.environ["OPENAI_API_KEY"] = "ollama"
os.environ["OPENAI_MODEL"] = "qwen2.5-coder:7b"

sys.path.insert(0, str(Path("/root/.openclaw/workspace/polish/xander-operator")))
from xander_operator.llm import _generate_via_ollama

print("Calling _generate_via_ollama...", file=sys.stderr)
out = _generate_via_ollama("Say OK", model="qwen2.5-coder:7b", max_tokens=5, timeout=30)
if out:
    print("RESPONSE:", out)
else:
    print("FAILED", file=sys.stderr)
    sys.exit(1)
