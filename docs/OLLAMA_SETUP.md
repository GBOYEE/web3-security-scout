# Ollama Integration — Setup & Troubleshooting (Chef’s Kiss)

## What This Covers

- Installing and running Ollama as a service
- Pulling the right model for UI/code generation
- Integrating with `xander_operator.llm` (used by Xander CLI and `ui-designer` skill)
- Verifying end‑to‑end generation
- Common failure modes and fixes

---

## 1. Install Ollama

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Enable and start the service:

```bash
systemctl enable --now ollama
systemctl status ollama  # should show active (running)
```

Ollama listens on `127.0.0.1:11434` by default.

---

## 2. Pull a Coding‑Optimized Model

For UI/code generation, **qwen2.5-coder:7b** is currently the best balance of speed and quality on 7B–8GB RAM.

```bash
ollama pull qwen2.5-coder:7b
```

Verify:

```bash
ollama list | grep qwen2.5-coder
```

Expected output line:
```
qwen2.5-coder:7b   dae161e27b0e   4.7 GB   ...
```

---

## 3. Environment Configuration

Set these in your workspace `.env` file:

```bash
# Use local Ollama for code/UI tasks
OLLAMA_BASE_URL=http://127.0.0.1:11434
OPENAI_API_KEY=ollama                # dummy, required by client lib
OPENAI_MODEL=qwen2.5-coder:7b        # model to use
```

**Important:** Do **not** include inline comments in `.env` values; they become part of the string and break parsing.

Also keep `OPENAI_BASE_URL` if you use OpenRouter for other tasks; it is ignored when `OLLAMA_BASE_URL` is set.

---

## 4. How `xander_operator.llm` Routes Requests

The `generate_response` function checks `OLLAMA_BASE_URL`:

- If set → uses **direct Ollama `/api/generate`** endpoint (bypasses OpenAI Python client)
- Else if `OPENAI_API_KEY` set → uses OpenAI client (OpenRouter, OpenAI, etc.)

This separation avoids compatibility issues between Ollama and the OpenAI client library.

**Direct Ollama payload:**
```json
{
  "model": "qwen2.5-coder:7b",
  "prompt": "...",
  "stream": false,
  "options": {
    "num_predict": 1000,
    "temperature": 0.7
  }
}
```

---

## 5. Verifying the Integration

### 5.1 Check Ollama API

```bash
curl -s http://127.0.0.1:11434/api/tags | jq '.models[].name'  # should list models
```

### 5.2 Test a generate call

```bash
curl -s -X POST http://127.0.0.1:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{"model":"qwen2.5-coder:7b","prompt":"Say OK","stream":false,"options":{"num_predict":3}}' | jq -r .response
```

Expected output: `OK` (or similar). This confirms the endpoint and model are working.

### 5.3 Test from Python (using xander_operator)

```bash
/root/.openclaw/workspace/test_ollama_integration.py
```

The script loads `.env`, imports `xander_operator.llm.generate_response`, and prints the result.

**First call after Ollama restart may take 30–60 seconds** while the model loads into memory. Subsequent calls are fast (~1–2 s).

---

## 6. Using the `ui-designer` Skill

Once the above is verified, the skill works:

```bash
# Example
python3 skills/ui-designer/ui_designer.py "Create a glassmorphism card with Tailwind"
```

The skill calls `generate_response` under the hood, which routes to Ollama.

---

## 7. Common Pitfalls & Fixes

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| `400 Bad Request` from OpenAI client | Using OpenAI client against Ollama `/v1` endpoint with incompatible model name or payload | Ensure `OLLAMA_BASE_URL` is set and use `generate_response` (which switches to direct `/api/generate`). Do not set `OPENAI_BASE_URL` to Ollama; keep it for OpenRouter if needed. |
| Request hangs / never returns | Model not loaded (first call after restart) or timeout too low | Wait 30–60 s after `systemctl restart ollama` for model to load. Increase `timeout` in `_generate_via_ollama` if needed (default 120 s). |
| `404 Not Found` on `/api/generate` | Using `OLLAMA_BASE_URL` with trailing `/v1` path | Set `OLLAMA_BASE_URL=http://127.0.0.1:11434` (no `/v1`). |
| `"Failed to parse: http://..."` in logs | Inline comment in `.env` value | Remove comments from the value line. `.env` must be plain `KEY=value`. |
| `ModuleNotFoundError: No module named 'requests'` | `requests` not installed in venv | `source polish/xander-operator/.venv/bin/activate && pip install requests` |
| Out‑of‑memory / runner crashes | Model too large for RAM (e.g., 13B+ on <8GB) | Use 7B models (`qwen2.5-coder:7b`, `codellama:7b`). Add swap if needed. |

---

## 8. Performance Tips

- Use `num_predict` to limit output length (fewer tokens = faster)
- Cache is enabled by default (`use_cache=True`); repeated prompts are instant
- For UI generation, set `temperature=0.3` for more deterministic HTML/Tailwind
- Keep `max_tokens` around 2000–4000 for full page HTML; smaller for components

---

## 9. Switching Models

To experiment with other models:

1. Pull the model: `ollama pull <model-name>`
2. Update `.env`: `OPENAI_MODEL=<model-name>`
3. Restart any agents that cache the model name (usually not needed)

Example stable alternatives:
- `codellama:7b` — general code, decent HTML
- `qwen2.5:7b-instruct-fixed` — instruction-tuned, may produce better prose

Avoid models larger than 7B on CPU‑only machines with <12 GB RAM.

---

## 10. Full End‑to‑End Checklist

- [ ] Ollama service running (`systemctl status ollama`)
- [ ] Desired model pulled (`ollama list`)
- [ ] `.env` contains clean `OLLAMA_BASE_URL`, `OPENAI_API_KEY=ollama`, `OPENAI_MODEL=...`
- [ ] `requests` installed in venv (`pip show requests`)
- [ ] `xander_operator.llm` updated (includes `_generate_via_ollama`)
- [ ] Test script prints a response (not FAILED)
- [ ] `ui-designer` skill produces HTML

If all pass, you can generate UI with Ollama reliably.

---

## 11. Appendix — Minimal Python Verification Script

 Save as `test_ollama_integration.py`:

```python
#!/usr/bin/env python3
import os, sys
from pathlib import Path

workspace = Path("/root/.openclaw/workspace")
env_path = workspace / ".env"
if env_path.exists():
    for line in env_path.read_text().splitlines():
        if line.strip() and not line.startswith('#'):
            k, _, v = line.partition("=")
            os.environ[k.strip()] = v.strip()

sys.path.insert(0, str(workspace / "polish" / "xander-operator"))
from xander_operator.llm import generate_response

prompt = "Create a simple HTML button with Tailwind classes, purple gradient, and hover effect."
out = generate_response(prompt, model=os.getenv("OPENAI_MODEL"), max_tokens=500, temperature=0.3, use_cache=False)
if out:
    print(out)
else:
    print("Generation failed", file=sys.stderr)
    sys.exit(1)
```

Run:

```bash
chmod +x test_ollama_integration.py
./test_ollama_integration.py
```

First run after Ollama restart may take up to 60 seconds while the model loads.

---

**With this setup, Ollama works consistently for UI and code generation. Documented for future you — no fluff, just working commands.**
