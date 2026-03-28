#!/usr/bin/env python3
import requests, os, sys, time

model = os.getenv("OPENAI_MODEL", "qwen2.5-coder:7b")
url = "http://127.0.0.1:11434/api/generate"

payload = {
    "model": model,
    "prompt": "Build a responsive navbar using Tailwind CSS. Output only HTML.",
    "stream": False,
    "options": {"num_predict": 512}
}

for attempt in range(1, 4):
    try:
        resp = requests.post(url, json=payload, timeout=60)
        if resp.status_code == 200:
            data = resp.json()
            print("Response received:\n")
            print(data.get("response", ""))
            break
        else:
            print(f"Attempt {attempt}: HTTP {resp.status_code}", file=sys.stderr)
    except Exception as e:
        print(f"Attempt {attempt} error: {e}", file=sys.stderr)
    if attempt < 3:
        time.sleep(2)
else:
    print("FAILED after 3 attempts", file=sys.stderr)
    sys.exit(1)
