# Proactive Coach Skill for XANDER

## Purpose
Enable XANDER to take initiative: schedule check-ins, track mood/energy, nudge goals, and provide therapeutic support.

## Activation
Add to `config.yaml`:
```yaml
skills:
  - path: "skills/proactive-coach"
    enabled: true
```

## Configuration
Create `skills/proactive-coach/config.yaml`:
```yaml
schedule:
  morning: "08:00"
  midday: "12:00"
  evening: "20:00"
  timezone: "Europe/Berlin"

mood_tags:
  - "🧘 focused"
  - "😤 stressed"
  - "🎉 accomplished"
  - "🕊️ peaceful"
  - "😴 tired"
  - "🔥 motivated"

therapist_trigger_phrases:
  - "i need to talk"
  - "i'm feeling down"
  - "i'm stressed"
  - "i can't focus"
  - "help me"

goal_checkin_frequency: "weekly"  # or "daily"
```

## Implementation

This skill uses OpenClaw's heartbeat and timer facilities to send scheduled messages.

### Core Functions

1. **Scheduled check-ins**: at configured times, XANDER sends a prompt to the chat.
2. **Mood/energy logging**: after each check-in, user can reply with tags; XANDER appends to daily log.
3. **Goal nudges**: weekly review of tasks linked to goals (from `goals.yaml`).
4. **Therapist mode**: when trigger detected, switch to empathetic listening, use CBT techniques.
5. **Weekly report**: generate insights about mood trends, task completion, energy patterns.

### Files

```
skills/proactive-coach/
├── SKILL.md
├── skill-config.yaml
├── coach.py           # main logic
├── prompts/
│   ├── morning.md
│   ├── midday.md
│   ├── evening.md
│   └── therapist.md
└── templates/
    └── weekly-report.html  # Jinja2
```

---

**We'll build this now.**
