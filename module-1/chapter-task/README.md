# Chapter 1 task: file-search agent + 3-model benchmark

An agentic chatbot on Nebius Token Factory that answers questions about the files in `sample_workspace/`, using the provided `search_files` function as its only tool. It's benchmarked on three Nemotron 3 sizes.

## Files

| Path | What it is |
|---|---|
| `app/search_tool.py` | The provided `search_files` function, unchanged |
| `app/agent.py` | The agent: tool schema, system prompt, agentic loop, chat memory, and an interactive CLI |
| `app/benchmark.py` | Runs the same scripted conversation on three models and writes the results |
| `sample_workspace/` | 20 demo files: 9 `.py`, 5 `.md` in `docs/` (one nested), 2 `README.md`, 4 with "retry" in the name |
| `results/runs.jsonl` | Raw data, one row per question per run |
| `results/summary.md` | Generated tables |

## Run it

```bash
# From module-1/chapter-task, with NEBIUS_API_KEY in the repo-root .env
../../.venv/bin/python app/agent.py                                       # chat with Nano
../../.venv/bin/python app/agent.py nvidia/nemotron-3-super-120b-a12b     # or any Token Factory model
../../.venv/bin/python app/benchmark.py 3                                 # 3 runs per model
```

## How the agent works

- **Native tool calling.** `search_files` is described with a JSON schema in `tools=[...]`, so the model returns structured `tool_calls` instead of free text that we'd have to parse (the lesson from Notebook 2).
- **Agentic loop** (`FileAgent.ask`): call the model. If it asks for tools, run each one, append the results as `role: "tool"` messages, and call the model again. Repeat until it answers without a tool call, with a cap of 5 rounds per question so a confused model can't loop forever.
- **The model decides when to search.** The system prompt says to search only for questions about local files, never for greetings or general knowledge, and to **reuse an earlier result from the conversation** instead of searching again.
- **Concise answers.** The system prompt asks for one to three sentences or a short list, with no lecturing.
- **Chat memory.** The conversation is a list (`self.history`) that is resent on every call, including earlier tool calls and their results. That's what lets the model answer "How many of those are there?" without searching again.
- **Help with counting.** The tool result is wrapped as `{"count": N, "paths": [...]}`, and the prompt says to use `count`. The task warns that LLMs can miscount even when the search itself is correct.
- **Errors go back to the model, not up the stack.** Bad arguments or a bad path become `{"error": "..."}` as the tool result, so the model can correct itself (`search_files` validates its inputs and blocks path traversal).
- **Metrics.** Every model call is streamed so we can measure TTFT. E2E covers the whole question, including tool round trips. Tokens are summed across all model calls for the question.

## Benchmark

**Models** (three sizes of the same family):

| Model | Size (total / active) | \$ per 1M tokens (in / out) |
|---|---|---|
| `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B` | 30B / 3B | 0.06 / 0.24 |
| `nvidia/nemotron-3-super-120b-a12b` | 120B / 12B | 0.30 / 0.90 |
| `nvidia/Nemotron-3-Ultra-550b-a55b` | 550B / 55B | 1.00 / 3.00 |

**Method.** One 8-question conversation (memory carried across questions), run 3 times per model: 72 requests in total. Each question has an expected tool decision and, where possible, an automatic answer check against `search_files` itself. Two follow-ups (#4 and #8) are answerable from the previous search, so a search there counts as unnecessary or repeated.

| # | Question | Should search? | Answer check |
|---|---|---|---|
| 1 | Hi! What can you help me with? | no | – |
| 2 | How many Python files are there in the current directory? | yes | says 9 |
| 3 | Which Markdown files do we have in the docs folder? | yes | names all 5 |
| 4 | How many of those are there? | **no** (reuse #3) | says 5 |
| 5 | Where is README.md? | yes | both `README.md` and `docs/README.md` |
| 6 | Are there any files with retry in their name? | yes | names all 4 |
| 7 | What is quantization? | **no** (general knowledge, despite `src/models/quantize.py`) | – |
| 8 | Which of the retry files is a test? | **no** (reuse #6) | `test_retry` |

**Metric definitions.**
- **E2E:** user question → final answer, including tool execution and the second model call.
- **TTFT:** time to the first streamed token of any kind (reasoning, content or tool call) on the question's first model call.
- **Cost:** tokens × catalog prices, summed over the question's model calls.
- **Repeated call:** the same tool and arguments (normalized) as an earlier call in the conversation.

### Results (averages per request, 24 requests per model)

| Model | E2E latency | TTFT | Input tokens | Output tokens | Cost / request | Tool decision correct | Missed | Unnecessary | Repeated | Answers correct | Answer words |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **Nano** 30B-A3B | 4.10 s | 1.47 s | 1,524 | 359 | **\$0.000178** | 24/24 | 0 | 0 | 0 | 17/18 | 21 |
| **Super** 120B-A12B | **1.68 s** | **0.80 s** | 1,664 | **97** | \$0.000586 | 24/24 | 0 | 0 | 0 | 18/18 | 26 |
| **Ultra** 550B-A55B | 2.21 s | 1.01 s | 1,644 | 148 | \$0.002089 | 24/24 | 0 | 0 | 0 | 18/18 | 29 |

Per question (searched out of 3 runs · average E2E):

| # | Question | Should search? | Nano | Super | Ultra |
|---|---|---|---|---|---|
| 1 | Hi! What can you help me with? | no | 0/3 · 2.1 s | 0/3 · 1.2 s | 0/3 · 1.2 s |
| 2 | How many Python files…? | yes | 3/3 · 7.7 s | 3/3 · 2.1 s | 3/3 · 6.4 s |
| 3 | Which Markdown files… docs? | yes | 3/3 · 4.7 s | 3/3 · 2.3 s | 3/3 · 2.0 s |
| 4 | How many of those are there? | no | 0/3 · 2.0 s | 0/3 · 1.1 s | 0/3 · 1.1 s |
| 5 | Where is README.md? | yes | 3/3 · 5.6 s | 3/3 · 2.1 s | 3/3 · 2.3 s |
| 6 | Any files with retry in their name? | yes | 3/3 · 5.5 s | 3/3 · 2.3 s | 3/3 · 2.2 s |
| 7 | What is quantization? | no | 0/3 · 2.6 s | 0/3 · 1.5 s | 0/3 · 1.4 s |
| 8 | Which of the retry files is a test? | no | 0/3 · 2.6 s | 0/3 · 1.0 s | 0/3 · 1.1 s |

### What I learned

1. **Tool decisions were perfect on every model.** With native `tools=`, a clear system prompt and chat memory, all three searched exactly when needed. None searched for the greeting, for "what is quantization?" (even though `quantize.py` exists), or for the two follow-ups the history already answered. On this task the size of the model didn't matter for tool use.
2. **The smallest model was the slowest.** Nano averaged 4.1 s per request versus 1.7 s for Super. It produced about 3.7× more output tokens (359 vs 97), mostly reasoning before every call, and questions that use the tool need two calls. Smaller doesn't automatically mean faster for a reasoning model.
3. **Nano made the one counting mistake**, the "LLMs aren't perfect at counting" case from the task. In one of 3 runs it reported "3 Python files *directly* in the current directory": it re-filtered the tool's 9 recursive results down to the top level instead of using `count`. The tool was right; the model reinterpreted it. The bigger models got all 18 checks right.
4. **Cost per request follows price, softened by verbosity.** Super is 3.75× Nano's output price, but because Nano thinks so much more, Super's requests cost only 3.3× more. Ultra costs 3.6× Super and 11.7× Nano and wasn't better at anything here.
5. **Memory is the main input cost.** About 1,500–1,650 input tokens per request, mostly the system prompt and resent history. Input grows with every turn, the "long chats re-pay for everything" lesson from Notebook 1.
6. **"Concise" is honored better by smaller models.** On "What is quantization?", Nano gave 39–49 words, while Super (66–109) and Ultra (43–106) drifted toward mini-lectures despite the same prompt.
7. **Latency varies a lot.** Ultra's question #2 averaged 6.4 s because of a slow outlier run; its other file questions took about 2 s. Averages over several runs matter, as Notebook 3 said.

### Recommendation

**Nemotron 3 Super** for this agent. It was the fastest (1.7 s E2E, 0.8 s TTFT), had perfect tool use and answers, and costs about \$0.0006 per request (≈ \$59 per 100k requests). Choose **Nano** when cost dominates at scale (≈ \$18 per 100k, 3.3× cheaper), but expect slower turns and an occasional misread. Turning off its thinking would be the next experiment for speed. **Ultra** adds cost without a measurable gain on a task this simple.
