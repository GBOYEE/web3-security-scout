#!/root/.openclaw/workspace/polish/xander-operator/.venv/bin/python
import os, sys, http.client as http_client
from pathlib import Path

# Enable HTTP debug logging
http_client.HTTPConnection.debuglevel = 2

# Load .env
workspace = Path(__file__).parent
env_path = workspace / ".env"
if env_path.exists():
    for line in env_path.read_text().splitlines():
        if line.strip() and not line.startswith('#'):
            k, _, v = line.partition("=")
            os.environ[k.strip()] = v.strip()

from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY", "ollama"),
    base_url=os.getenv("OLLAMA_BASE_URL") or os.getenv("OPENAI_BASE_URL")
)

model = os.getenv("OPENAI_MODEL", "qwen2.5:7b-instruct")
print(f"Using model: {model}", file=sys.stderr)

prompt = """You are an expert frontend designer. Create a single-page portfolio website for an AI engineer named GBOYEE.

Requirements:
- Dark background (#050505), neon cyan (#22d3ee) and purple (#a855f7) accents.
- Animated canvas background: flowing particle network (neural / blockchain nodes) with connecting lines.
- Hero section: large name, title, gradient text, two CTA buttons (glow effect).
- About section: short bio in glassmorphism card.
- Tech stack: infinite horizontal marquee of tech tags (Python, Ollama, GitHub, Nginx, etc.).
- Projects: Bento grid (6 cards) with glassmorphism, hover lift, project info, tags, repo links.
- Contact section: email, resume download, GitHub link.
- Use Tailwind via CDN, custom CSS for animations, glass effect, marquee, fade-in on scroll.
- Mobile responsive, print-friendly, SEO meta tags.
- Output ONLY full HTML (no markdown, no commentary). Keep under 500 lines.

Make it A+ modern, sparkling, with subtle motion."""

resp = client.chat.completions.create(
    model=model,
    messages=[
        {"role": "system", "content": "You are a top-tier UI/UX designer and frontend engineer."},
        {"role": "user", "content": prompt}
    ],
    max_tokens=4000,
    temperature=0.2
)

html = resp.choices[0].message.content.strip()
# Strip any code fences if present
if html.startswith("```"):
    lines = html.splitlines()
    # Remove first and last lines if they are fences
    if lines[0].startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].startswith("```"):
        lines = lines[:-1]
    html = "\n".join(lines)

print(html)
