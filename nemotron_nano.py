# NVIDIA Nemotron 3 Nano (30B-A3B) via Nebius Token Factory
# Run:  set -a; source .env; set +a; python nemotron_nano.py
import os
from openai import OpenAI

client = OpenAI(
    base_url="https://api.tokenfactory.nebius.com/v1/",
    api_key=os.environ.get("NEBIUS_API_KEY")
)

response = client.chat.completions.create(
    model="nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B",
    messages=[
        {
            "role": "system",
            "content": """SYSTEM_PROMPT"""
        },
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
