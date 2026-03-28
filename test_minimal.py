#!/usr/bin/env python3
import requests, os, sys, time

base = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
url = f"{base.rstrip('/')}/api/generate"
payload = {
    "model": "qwen2.5-coder:7b",
    "prompt": "OK",
    "stream": False,
    "options": {"num_predict": 3}
}
print("URL:", url, file=sys.stderr)
print("Payload:", payload, file=sys.stderr)
try:
    r = requests.post(url, json=payload, timeout=30)
    print("Status:", r.status_code, file=sys.stderr)
    print("Body:", r.text[:200], file=sys.stderr)
    if r.ok:
        print(r.json().get("response", ""))
    else:
        print("HTTP error", r.status_code, file=sys.stderr)
except Exception as e:
    print("Exception:", e, file=sys.stderr)
    sys.exit(1)
