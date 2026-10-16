# Module 1 · Notebook 1: Token Factory, model cards, first calls

Study notes for two course videos, "Choosing and Testing a Model" and "Calling a Model from Python", which both cover `module-1/01_intro_to_token_factory.ipynb`.

## Why managed inference

Open-weight models can be self-hosted, but that means GPUs, a serving stack, scaling and monitoring. Token Factory runs the models for you: send a request, get an answer, pay per token.

## Setup

- Get an API key at tokenfactory.nebius.com and treat it like a password.
- Store it as `NEBIUS_API_KEY=...` in `module-1/lesson/.env` (no quotes, no spaces). Here that file is a symlink to the repo-root `.env`, and both are gitignored.
- On Colab, use Secrets (the key icon) in place of a `.env` file.

## Nemotron 3 family

| | Routing key | Context | $ / 1M in / out |
|---|---|---|---|
| Nano | `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B` | 262k | 0.06 / 0.24 |
| Super | `nvidia/nemotron-3-super-120b-a12b` | 262k | 0.30 / 0.90 |
| Ultra | `nvidia/Nemotron-3-Ultra-550b-a55b` | 1M | 1.00 / 3.00 |

Prices are from the catalog API on 2026-10-16. All three are text-to-text and support tool calling and reasoning. The members share training lineage, so you can prototype on Nano and scale up without rewriting code. Rule: start small, scale only when the task needs it.

## Reading a model card

- **Routing key**: the exact `model=` string. Always copy it with the copy icon; one wrong character gives a bare "model not found".
- **Context window**: one budget shared by the prompt, the resent history and the output. Rough sizes: a book page is about 400 tokens, and code tokenizes worse than prose. Ask whether it's big *compared to what you'll send*.
- **Pricing**: input is read in one pass, so it's cheap. Output is generated token by token, so it's several times pricier. Chatty answers cost real money.
- **Modality**: what goes in and what comes out (text, image, embeddings).
- **Capabilities**: tool calling and reasoning flags.
- **License**: Nemotron uses the NVIDIA Open Model License, which allows commercial use. Check every model; open weights don't mean anything goes.

You can read the same fields from code with `client.models.list(extra_query={"verbose": "true"})`.

## Chat Completions API (OpenAI-compatible)

- Change `base_url` and the routing key, and any OpenAI tutorial works.
- Roles: `system` (voice, style, boundaries), `user`, `assistant` (earlier replies), `tool` (Notebook 2).
- Response fields that matter: `content` (the answer), `finish_reason` (`stop`, or `length` when it was cut off), `usage` (the tokens you're billed for).
- **The API is stateless.** Memory means appending each answer and resending the whole history, so long chats re-pay for every earlier turn.

## Gotchas I hit doing the exercises

1. **`max_tokens` and reasoning.** Nano reasons before answering, and those tokens count toward `max_tokens`. With `max_tokens=10` the reasoning used them all and `content` was `None`. Fix: `extra_body={"chat_template_kwargs": {"enable_thinking": False}}`.
2. **`temperature=0` isn't identical.** Ten runs with `temperature=0` + `seed` + thinking off gave 10 different outputs (similar meaning, different wording). Temperature does work: 2.0 gives gibberish. The likely cause is batched mixture-of-experts serving, which is non-deterministic. If you need the exact same output, cache it.
3. **Reasoning shows up in output tokens.** On the survey puzzle, Nano billed 812 output tokens, mostly reasoning, while Ultra billed 633. Both were correct; Ultra cost about 10× more.
4. **Small models can degenerate.** One "formal analyst" run produced a long list of CamelCase keywords instead of prose. Check outputs; don't assume.
5. **Both endpoints work.** `api.tokenfactory.us-central1.nebius.com` and `api.tokenfactory.nebius.com` both serve Nano, even though Nano's card lists `eu-north1`.
