# Ollama + OpenAI Client Integration — Chef’s Kiss Guide

## Overview

Ollama provides an OpenAI‑compatible HTTP API at `http://localhost:11434/v1`. This allows any library that speaks to OpenAI (like the `openai` Python package) to use local models with minimal configuration.

**Key points:**
- Base URL: `http://localhost:11434/v1` (or `https://...` if TLS termination)
- API key: any non‑empty string (Ollama ignores it) — commonly set to `ollama`
- Model name: must match exactly the tag shown by `ollama list` (e.g., `codellama:7b`, `qwen2.5:7b-instruct`)
- No streaming required; default `stream=False` works

---

## Prerequisites

1. **Install Ollama** (Linux)
   ```bash
   curl -fsSL https://ollama.com/install.sh | sh
   ```
2. **Start and enable service**
   ```bash
   systemctl enable --now ollama
   ```
3. **Pull desired models**
   ```bash
   ollama pull codellama:7b
   ollama pull qwen2.5:7b-instruct
   # etc.
   ```
4. **Verify models**
   ```bash
   ollama list
   # or
   curl http://localhost:11434/api/tags | jq .
   ```

---

## Basic Python Test (works standalone)

```python
from openai import OpenAI

client = OpenAI(
    base_url='http://localhost:11434/v1',
    api_key='ollama'  # dummy, not used
)

resp = client.chat.completions.create(
    model='codellama:7b',
    messages=[{'role': 'user', 'content': 'Say OK'}],
    max_tokens=5
)
print(resp.choices[0].message.content)
```

If this prints `OK`, the integration works.

---

## Integrating with xander_operator.llm

The `xander_operator.llm` module already supports Ollama via environment variables:

| Variable | Purpose | Example |
|----------|---------|---------|
| `OLLAMA_BASE_URL` | Points to Ollama API | `http://localhost:11434/v1` |
| `OPENAI_API_KEY` | Dummy API key (any string) | `ollama` |
| `OPENAI_MODEL` | Model to use | `codellama:7b` |

`get_llm_client()` checks `OLLAMA_BASE_URL` first; if set, returns `OpenAI(base_url=..., api_key=...)`. Otherwise falls back to OpenAI/OpenRouter if `OPENAI_API_KEY` is set.

**Therefore, to use Ollama globally:**
```bash
export OLLAMA_BASE_URL=http://localhost:11434/v1
export OPENAI_API_KEY=ollama
export OPENAI_MODEL=codellama:7b
```

---

## Common Pitfalls & Fixes

### 1. “Invalid model name” (400 Bad Request)

**Cause:** Model tag mismatch. Ollama requires exact tag (including `:latest` if present).

**Fix:** Use the exact name from `ollama list`. For example, if you pulled `qwen2.5:7b-instruct-fixed`, use that full string. Do not use aliases like `qwen2.5:7b` unless that exact tag exists.

**Check:**
```bash
ollama list | grep qwen
# Output shows: qwen2.5:7b-instruct-fixed
```

Then set:
```bash
export OPENAI_MODEL=qwen2.5:7b-instruct-fixed
```

### 2. “Runner process no longer running”

**Cause:** Ollama’s model runner crashed or was killed due to memory pressure.

**Fix:**
- Restart service: `systemctl restart ollama`
- Ensure enough RAM (7B models need ~4–6 GB free)
- Use smaller model if needed (`codellama:7b` is lighter than instruct variants)

**Quick restart:**
```bash
systemctl restart ollama
sleep 2
# Test again
```

### 3. “Connection refused” or timeout

**Cause:** Ollama not running or bound to different interface.

**Fix:**
```bash
systemctl status ollama
# If inactive: systemctl start ollama
```
Check listening port:
```bash
ss -tlnp | grep 11434
# Should show 127.0.0.1:11434 or 0.0.0.0:11434
```

### 4. Import errors when using xander_operator as a skill

**Cause:** The skill script doesn’t have the workspace `polish/xander-operator` on `PYTHONPATH`.

**Fix:** In the skill (e.g., `skills/ui-designer/ui_designer.py`), add:

```python
import sys
from pathlib import Path

workspace = Path(__file__).parent.parent.parent
sys.path.insert(0, str(workspace / "polish" / "xander-operator"))
```

Also ensure the script runs with the venv Python (re‑exec if needed).

---

## Recommended Stable Models

| Model | Strengths | Notes |
|-------|-----------|-------|
| `codellama:7b` | Code generation, HTML/Tailwind, stable | Best for UI tasks, lower memory |
| `qwen2.5:7b-instruct-fixed` | Instruction following, cleaner output | May be heavier, but good for summaries |
| `llava:7b` | Vision + text (multimodal) | Not needed for pure text UI |

Start with `codellama:7b`. If you need better reasoning, try `qwen2.5:7b-instruct-fixed` once runner stability is confirmed.

---

## Testing Checklist

- [ ] `ollama list` shows desired model
- [ ] `curl http://localhost:11434/api/tags` returns JSON with model name
- [ ] Minimal Python script (above) prints response without error
- [ ] Environment variables set in shell or `.env`:
  - `OLLAMA_BASE_URL=http://localhost:11434/v1`
  - `OPENAI_API_KEY=ollama`
  - `OPENAI_MODEL=codellama:7b`
- [ ] `xander_operator.llm.generate_response("test")` returns non‑None

If all pass, any skill using `generate_response` will work.

---

## Performance Tips

- Use `temperature=0.3` for code generation (lower = more deterministic)
- Set `max_tokens` appropriately (2000 for HTML snippets, 4000 for full pages)
- Enable caching (default in xander_operator) to avoid re‑generating same prompts
- For large generations, consider increasing `max_tokens` and timeout

---

## Security Note

Ollama by default binds to `127.0.0.1`. If you need remote access, set `OLLAMA_HOST=0.0.0.0` but add firewall rules. Never expose Ollama publicly without auth.

---

## Troubleshooting Commands

```bash
# Restart Ollama
sudo systemctl restart ollama

# Check logs
sudo journalctl -u ollama -f

# List models
ollama list

# Test API directly
curl -s -X POST http://localhost:11434/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"codellama:7b","messages":[{"role":"user","content":"OK"}],"max_tokens":5}' | jq .

# Memory usage
free -h
```

---

## Conclusion

Once Ollama is running and environment variables are set, the `xander_operator.llm` module works seamlessly. The `ui-designer` skill can then generate UI components by calling `generate_response` with appropriate prompts.

**Stable setup:**
- Model: `codellama:7b`
- Env: `OLLAMA_BASE_URL`, `OPENAI_API_KEY=ollama`, `OPENAI_MODEL=codellama:7b`
- Client: `OpenAI(base_url=..., api_key=...)`

With this guide, you should be able to integrate Ollama for all LLM needs (UI generation, PR reviews, etc.) reliably.
