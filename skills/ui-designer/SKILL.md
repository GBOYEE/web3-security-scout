# UI Designer Skill — XANDER

## Purpose
Generate UI components, pages, and design assets using the local LLM (Ollama).
Produces HTML, Tailwind classes, color palettes, layout structures.

## Activation
Add to `config.yaml`:
```yaml
skills:
  - path: "skills/ui-designer"
    enabled: true
```

## Capabilities

### 1. Generate Component
Prompt: "Create a [button/card/form/navbar] with [specs]"
Output: HTML + Tailwind classes

### 2. Suggest Palette
Prompt: "Suggest a [tech/creative/minimal] color palette"
Output: Hex codes and usage notes

### 3. Design Review
Prompt: "Review this UI code for accessibility and responsiveness"
Output: Feedback + improvements

### Implementation
This skill calls the LLM via xander-operator's `generate_response` with specialized prompts.
It does not execute code; returns textual design artifacts.

## Example Usage
User: "Design a hero section with headline, subhead, and CTA"
Agent: Generates HTML/Tailwind snippet ready to copy-paste.
