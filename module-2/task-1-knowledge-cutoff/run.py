"""Module 2 · Task 1: do models know recent facts, and does the answer change between regenerations?

Each "regenerate" in the playground is the same request sent again, so here every question is
sent RUNS times to each model with default sampling.

Run:  python run.py   (writes results.jsonl next to this file)
"""
import json
import os
from pathlib import Path

from dotenv import find_dotenv, load_dotenv
from openai import OpenAI

load_dotenv(find_dotenv())
client = OpenAI(
    base_url="https://api.tokenfactory.us-central1.nebius.com/v1/",
    api_key=os.environ.get("NEBIUS_API_KEY"),
)

MODELS = ["nvidia/Nemotron-3_5-Lightning", "nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B"]
QUESTIONS = {
    "A": "Does Python have an officially supported build that runs without the GIL?",
    "B": "Which NVIDIA GPU architecture powers Jetson Thor?",
    "C": "Does current stable Go support methods that declare their own type parameters? What was the first release?",
}
RUNS = 5

out = Path(__file__).with_name("results.jsonl")
# Resumable: skip answers already saved, so a dropped connection doesn't mean starting over
done = set()
if out.exists():
    done = {(r["model"], r["question"], r["run"]) for r in map(json.loads, out.read_text().splitlines())}

with out.open("a") as f:
    for model in MODELS:
        for qid, question in QUESTIONS.items():
            for run in range(1, RUNS + 1):
                if (model, qid, run) in done:
                    continue
                resp = client.with_options(max_retries=5).chat.completions.create(
                    model=model, messages=[{"role": "user", "content": question}]
                )
                answer = (resp.choices[0].message.content or "").strip()
                f.write(json.dumps({"model": model, "question": qid, "run": run, "answer": answer}) + "\n")
                f.flush()
                print(f"{model.split('/')[1]:32} {qid} run {run}: {' '.join(answer.split())[:110]}", flush=True)
