"""Benchmark the file agent on three Nemotron 3 sizes with the same scripted conversation.

Run:  python app/benchmark.py [runs_per_model]
Writes results/runs.jsonl (one row per turn) and results/summary.md.
"""
import json
import sys
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from statistics import mean

from agent import FileAgent
from search_tool import search_files

MODELS = [
    "nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B",  # 30B total / 3B active
    "nvidia/nemotron-3-super-120b-a12b",      # 120B / 12B
    "nvidia/Nemotron-3-Ultra-550b-a55b",      # 550B / 55B
]
RESULTS = Path(__file__).resolve().parents[1] / "results"

# Ground truth straight from the tool, so the checks always match the workspace
PY_FILES = search_files("*.py", max_results=100)
DOCS_MD = search_files("*.md", "docs", max_results=100)
RETRY_FILES = search_files("*retry*", max_results=100)


def mentions_all(*needles):
    return lambda answer: all(n.casefold() in answer.casefold() for n in needles)


# (question, should the model call the tool?, answer check or None)
SCRIPT = [
    ("Hi! What can you help me with?", False, None),
    ("How many Python files are there in the current directory?", True, mentions_all(str(len(PY_FILES)))),
    ("Which Markdown files do we have in the docs folder?", True, mentions_all(*(Path(p).name for p in DOCS_MD))),
    ("How many of those are there?", False, mentions_all(str(len(DOCS_MD)))),  # answerable from the previous result
    ("Where is README.md?", True, lambda a: "docs/readme.md" in a.casefold() and a.casefold().count("readme.md") >= 2),
    ("Are there any files with retry in their name?", True, mentions_all(*(Path(p).name for p in RETRY_FILES))),
    ("What is quantization?", False, None),  # general knowledge, even though src/models/quantize.py exists
    ("Which of the retry files is a test?", False, mentions_all("test_retry")),  # answerable from the previous result
]


def price_table(client):
    """$/token (input, output) for each model, read from the Token Factory catalog."""
    cards = {m.id: m.model_extra for m in client.models.list(extra_query={"verbose": "true"})}
    return {m: (float(cards[m]["pricing"]["prompt"]), float(cards[m]["pricing"]["completion"])) for m in MODELS}


def normalize_call(name, arguments):
    try:
        args = json.loads(arguments or "{}")
    except json.JSONDecodeError:
        return (name, arguments)
    args.setdefault("subpath", ".")
    args["name_pattern"] = str(args.get("name_pattern", "")).casefold()
    args["subpath"] = str(args["subpath"]).strip("./") or "."
    return (name, json.dumps(args, sort_keys=True))


def run_conversation(model, run, prices):
    agent = FileAgent(model)
    price_in, price_out = prices[model]
    seen_calls, rows = set(), []
    for turn, (question, expect_tool, check) in enumerate(SCRIPT, start=1):
        s = agent.ask(question)
        calls = [normalize_call(n, a) for n, a in s.tool_calls]
        repeated = sum(1 for c in calls if c in seen_calls) + (len(calls) - len(set(calls)))
        seen_calls.update(calls)
        rows.append({
            "model": model,
            "run": run,
            "turn": turn,
            "question": question,
            "expect_tool": expect_tool,
            "called_tool": bool(calls),
            "tool_calls": s.tool_calls,
            "repeated_calls": repeated,
            "model_calls": s.model_calls,
            "e2e_s": round(s.e2e_s, 3),
            "ttft_s": round(s.ttft_s, 3) if s.ttft_s is not None else None,
            "input_tokens": s.input_tokens,
            "output_tokens": s.output_tokens,
            "cost_usd": s.input_tokens * price_in + s.output_tokens * price_out,
            "answer_words": len(s.answer.split()),
            "correct": check(s.answer) if check else None,
            "answer": s.answer,
        })
        print(f"[{model.split('/')[1][:24]:24} run {run} turn {turn}] {s.e2e_s:5.1f}s tools={len(calls)} {question[:45]}", flush=True)
    return rows


def summarize(rows):
    by_model = defaultdict(list)
    for r in rows:
        by_model[r["model"]].append(r)

    lines = [
        "# Benchmark results",
        "",
        f"Same 8-turn conversation, {max(r['run'] for r in rows)} runs per model. Averages are per user request (one turn, "
        "including any tool round trips).",
        "",
        "| Model | E2E latency | TTFT | Input tokens | Output tokens | Cost / request | Tool decision correct | Missed calls | Unnecessary calls | Repeated calls | Answers correct | Answer words |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for model, rs in by_model.items():
        checked = [r for r in rs if r["correct"] is not None]
        lines.append(
            f"| `{model.split('/')[1]}` "
            f"| {mean(r['e2e_s'] for r in rs):.2f} s "
            f"| {mean(r['ttft_s'] for r in rs if r['ttft_s'] is not None):.2f} s "
            f"| {mean(r['input_tokens'] for r in rs):,.0f} "
            f"| {mean(r['output_tokens'] for r in rs):,.0f} "
            f"| ${mean(r['cost_usd'] for r in rs):.6f} "
            f"| {sum(r['called_tool'] == r['expect_tool'] for r in rs)}/{len(rs)} "
            f"| {sum(r['expect_tool'] and not r['called_tool'] for r in rs)} "
            f"| {sum(r['called_tool'] and not r['expect_tool'] for r in rs)} "
            f"| {sum(r['repeated_calls'] for r in rs)} "
            f"| {sum(r['correct'] for r in checked)}/{len(checked)} "
            f"| {mean(r['answer_words'] for r in rs):.0f} |"
        )

    runs = max(r["run"] for r in rows)
    lines += [
        "",
        f"## Per question: tool called (out of {runs} runs) and average latency",
        "",
        "| # | Question | Should call? | " + " | ".join(f"`{m.split('/')[1]}`" for m in by_model) + " |",
        "|---|---|---|" + "---|" * len(by_model),
    ]
    for turn, (question, expect_tool, _) in enumerate(SCRIPT, start=1):
        cells = []
        for rs in by_model.values():
            t = [r for r in rs if r["turn"] == turn]
            cells.append(f"{sum(r['called_tool'] for r in t)}/{len(t)} · {mean(r['e2e_s'] for r in t):.1f} s")
        lines.append(f"| {turn} | {question} | {'yes' if expect_tool else 'no'} | " + " | ".join(cells) + " |")
    return "\n".join(lines) + "\n"


def main():
    runs = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    prices = price_table(FileAgent().client)
    RESULTS.mkdir(exist_ok=True)

    def bench(model):  # runs of one model are sequential; the three models run in parallel
        return [row for run in range(1, runs + 1) for row in run_conversation(model, run, prices)]

    with ThreadPoolExecutor(max_workers=len(MODELS)) as pool:
        rows = [row for model_rows in pool.map(bench, MODELS) for row in model_rows]

    with open(RESULTS / "runs.jsonl", "w") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")
    summary = summarize(rows)
    (RESULTS / "summary.md").write_text(summary)
    print("\n" + summary)


if __name__ == "__main__":
    main()
