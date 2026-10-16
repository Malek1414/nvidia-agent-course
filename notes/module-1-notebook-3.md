# Module 1 · Notebook 3: observability and cost

Notebook: `module-1/03_observability_and_cost.ipynb` · Video: "Measure Performance and Cost" (7:40)

A loop that works isn't a loop you can ship. Two questions decide it: **is it fast enough?** and **is it cheap enough?**

## Speed: three different numbers

| Metric | Measures | Matters most when |
|---|---|---|
| **TTFT**, time to first token | Delay before anything appears | Someone is waiting for a reply (chat widget). Three seconds of silence reads as "broken". |
| **t/s**, tokens per second | How fast text arrives once it starts | Someone is **reading along** with a long output. 10 t/s is painful; 60–100 t/s feels effortless. |
| **E2EL**, end-to-end latency | Request sent → full output received | **Nobody is watching**: agents doing internal steps, batch jobs. Steps add up: 10 calls × 4 s ≈ 40 s. |

- The playground shows all three under each response.
- **Chat Completions responses don't include latency.** Latency happens between you and the server, so you measure it client-side: stream the response and use a stopwatch.

### Latency exercise answers

1. **Live support chat**, 2–3 sentence answers → **TTFT**. A short answer streams in under a second, so the wait before the first word is what users feel.
2. **Nightly code-review agent**, 2am to 9am deadline → **E2EL summed over the whole run**. Nobody watches, but the *deadline* is on the clock: calls × E2EL must fit in the window. Rate limits and retries also count.
3. **Long-form report**, read live → **t/s**. About 2,700 tokens; the stream must stay ahead of reading speed (~5 tokens/s).

## Cost: one formula

```
cost = (prompt_tokens × price_in + completion_tokens × price_out) / 1,000,000
```

- Prices come from the **model card** (per **1M** tokens). Token counts come from **`response.usage`** on every response, so no estimating is needed.
- **Output costs several times more than input.** It's generated token by token, while input is read in one pass. On Nano it's 4× (\$0.06 vs \$0.24).
- **Reasoning tokens are output tokens.** A model that "thinks" more costs more, even if the visible answer is short.
- A fraction of a cent per request is the trap. Scale it: × requests/day × 30.

### Cost exercise (my run, averages of 5 requests)

| | Nano | Ultra |
|---|---|---|
| Per request | \$0.000061 | \$0.001033 (17×) |
| Per 100,000 | \$6.07 | \$103.32 |
| Per 1,000,000 | \$60.70 | \$1,033.20 |

The gap stops being academic at about **100k requests/day** (about \$2,900/month in difference). Agents reach that fast, since one task can mean 10 calls.

## Ground truth: the billing console

- Token Factory → **Billing settings → Usage**, view **Chart**, **Group by → Products**. Then pick the model's **Input** and **Output** products.
- Input and output are **separate products** because they're billed at separate rates. Output usually dominates the bar.
- **The console total is the ground truth.** If your own numbers disagree, the console is right.
- Habits: **one API key per project** (spend becomes attributable) and **a spend limit per key** (a runaway agent loop can burn budget fast).

## Gotchas found running the appendix on Token Factory

1. **Token Factory puts `usage` on every streamed chunk**, not just the last one. The course's `measure()` skips any chunk carrying usage, so it skipped all of them and crashed (`t_first` stayed `None`). Fix: record usage, then still process the chunk.
2. **Reasoning streams in a separate `reasoning` field**, before `content`. Timing only `content` gives *time to first answer token*, which includes the thinking. Report both TTFT figures.
3. **For hidden-reasoning models (Ultra), compute t/s over the whole request.** Its visible text arrives in one burst after silent thinking, and dividing all output tokens by that burst gives nonsense.
4. Different models report usage differently: Nano and Ultra resend running totals on every chunk, while Super sends one final chunk. **Take the last usage you see.**
