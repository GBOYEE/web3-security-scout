#!/root/.openclaw/workspace/polish/xander-operator/.venv/bin/python
import os, sys
from openai import OpenAI
os.environ["OLLAMA_BASE_URL"] = "http://localhost:11434/v1"
os.environ["OPENAI_API_KEY"] = "ollama"
model = "qwen2.5:7b-instruct"
client = OpenAI(api_key="ollama", base_url=os.environ["OLLAMA_BASE_URL"])
resp = client.chat.completions.create(
    model=model,
    messages=[{"role":"user","content":"Say OK"}],
    max_tokens=5
)
print(resp.choices[0].message.content)
