#!/root/.openclaw/workspace/polish/xander-operator/.venv/bin/python
import requests, sys
try:
    r = requests.get("http://127.0.0.1:11434/api/tags", timeout=10)
    print("Status:", r.status_code)
    print("Body preview:", r.text[:300])
except Exception as e:
    print("Error:", e, file=sys.stderr)
    sys.exit(1)
