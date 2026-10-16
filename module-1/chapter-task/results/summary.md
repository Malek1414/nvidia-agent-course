# Benchmark results

Same 8-turn conversation, 3 runs per model. Averages are per user request (one turn, including any tool round trips).

| Model | E2E latency | TTFT | Input tokens | Output tokens | Cost / request | Tool decision correct | Missed calls | Unnecessary calls | Repeated calls | Answers correct | Answer words |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `NVIDIA-Nemotron-3-Nano-30B-A3B` | 4.10 s | 1.47 s | 1,524 | 359 | $0.000178 | 24/24 | 0 | 0 | 0 | 17/18 | 21 |
| `nemotron-3-super-120b-a12b` | 1.68 s | 0.80 s | 1,664 | 97 | $0.000586 | 24/24 | 0 | 0 | 0 | 18/18 | 26 |
| `Nemotron-3-Ultra-550b-a55b` | 2.21 s | 1.01 s | 1,644 | 148 | $0.002089 | 24/24 | 0 | 0 | 0 | 18/18 | 29 |

## Per question: tool called (out of 3 runs) and average latency

| # | Question | Should call? | `NVIDIA-Nemotron-3-Nano-30B-A3B` | `nemotron-3-super-120b-a12b` | `Nemotron-3-Ultra-550b-a55b` |
|---|---|---|---|---|---|
| 1 | Hi! What can you help me with? | no | 0/3 · 2.1 s | 0/3 · 1.2 s | 0/3 · 1.2 s |
| 2 | How many Python files are there in the current directory? | yes | 3/3 · 7.7 s | 3/3 · 2.1 s | 3/3 · 6.4 s |
| 3 | Which Markdown files do we have in the docs folder? | yes | 3/3 · 4.7 s | 3/3 · 2.3 s | 3/3 · 2.0 s |
| 4 | How many of those are there? | no | 0/3 · 2.0 s | 0/3 · 1.1 s | 0/3 · 1.1 s |
| 5 | Where is README.md? | yes | 3/3 · 5.6 s | 3/3 · 2.1 s | 3/3 · 2.3 s |
| 6 | Are there any files with retry in their name? | yes | 3/3 · 5.5 s | 3/3 · 2.3 s | 3/3 · 2.2 s |
| 7 | What is quantization? | no | 0/3 · 2.6 s | 0/3 · 1.5 s | 0/3 · 1.4 s |
| 8 | Which of the retry files is a test? | no | 0/3 · 2.6 s | 0/3 · 1.0 s | 0/3 · 1.1 s |
