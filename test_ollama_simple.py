#!/root/.openclaw/workspace/polish/xander-operator/.venv/bin/python
import os, sys
from openai import OpenAI

os.environ["OLLAMA_BASE_URL"] = "http://localhost:11434/v1"
os.environ["OPENAI_API_KEY"] = "ollama"
model = os.getenv("OPENAI_MODEL", "codellama:7b")

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"], base_url=os.environ["OLLAMA_BASE_URL"])

print(f"Testing model: {model}", file=sys.stderr)
try:
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": "Say OK"}],
        max_tokens=5,
        stream=False
    )
    print("Success:", resp.choices[0].message.content)
except Exception as e:
    print("Error:", e), file=sys.stderr)
    sys.exit(1)
