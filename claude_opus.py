# Claude Opus 5 via the Anthropic API — same shape as nemotron_nano.py
# Auth: uses your `ant auth login` profile, or ANTHROPIC_API_KEY if set
# Run:  .venv/bin/python claude_opus.py
import anthropic

client = anthropic.Anthropic()

response = client.beta.messages.create(
    model="claude-opus-5",
    max_tokens=16000,
    # If a safety classifier declines, re-run on Anthropic's recommended fallback model
    betas=["server-side-fallback-2026-07-01"],
    fallbacks="default",
    system="""SYSTEM_PROMPT""",
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": """USER_MESSAGE"""
                }
            ]
        }
    ]
)

print(response.to_json())
