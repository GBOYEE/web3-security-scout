#!/root/.openclaw/workspace/polish/xander-operator/.venv/bin/python
import os, sys
from openai import OpenAI

os.environ["OLLAMA_BASE_URL"] = "http://127.0.0.1:11434/v1"
os.environ["OPENAI_API_KEY"] = "ollama"

client = OpenAI(base_url=os.environ["OLLAMA_BASE_URL"], api_key=os.environ["OPENAI_API_KEY"])

try:
    resp = client.chat.completions.create(
        model="qwen2.5-coder:7b",
        messages=[{"role":"user","content":"Say OK"}],
        max_tokens=5,
        timeout=30
    )
    print("OK:", resp.choices[0].message.content)
except Exception as e:
    print("Error:", e, file=sys.stderr)
    sys.exit(1)
