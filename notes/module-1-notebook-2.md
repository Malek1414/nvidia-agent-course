# Module 1 · Notebook 2: a very simple tool call

Notebook: `module-1/02_tool_calling.ipynb`. The course had no separate video for this notebook in the set I was given.

## Core ideas

- **Tool** = a function you write. **Tool call** = the model *asking* you to run it, with arguments.
- **The model never executes anything; your code does.** A tool call is just generated text, JSON with a function name and arguments.
- To the model, tool descriptions are **just more text in the prompt**. JSON schemas are used because models like Nemotron were trained on that format.
- Because a tool call is generated text, **it can be malformed**: wrapped in markdown, almost-JSON, several calls at once, or the wrong arguments.
- **The agentic loop:** the model emits a request → your code parses it, decides whether to run it, and executes it → the result goes back as a message → the model answers, grounded in the result. Every agent is this loop, scaled up.

## Two ways to do tool calling

| | Manual JSON in the prompt (the notebook's demo) | Native `tools=` parameter |
|---|---|---|
| How the tool is described | Written into the system prompt | JSON schema passed in `tools=[...]` |
| What comes back | Free text you must `json.loads` | Structured `message.tool_calls` (id, name, arguments) |
| `finish_reason` | `stop` | `tool_calls` |
| Result goes back as | A `user` message ("Tool result: …") | A `role: "tool"` message with the matching `tool_call_id` |
| Robustness | Brittle | Much better; arguments still need validating |

The playground's **Functions → Add function** panel is the same thing as `tools=`. It shows the requested call and executes nothing.

## Why use a calculator tool?

LLMs don't really compute; they produce what *looks* right from their training. A tool makes the numbers exact, for example 4,823 × 3,917 = 18,891,691 computed by SymPy.

## "Break it!": what I found (and whose fault each was)

1. **No tool needed** ("capital of France?") → prose → `json.loads` crashes. **Our code** assumed every reply is a tool call.
2. **Two calculations** → two JSON objects → `json.loads` "Extra data". **Our parser** handles exactly one call.
3. **"Format it in markdown"** → JSON inside a ```` ```json ```` fence → `json.loads` crashes. **Shared**: the model let the user override the system prompt, and the parser should strip fences anyway.
4. **`15% * 2400`** → `SympifyError` inside the tool. **The tool's**: no input validation.
5. **`4,823*3,917`** (with commas) → no crash, *silently wrong*: SymPy returns the tuple `(4, 2469, 917)`, and the model reports it confidently.
6. **`5/0`** → the tool returns `zoo` (SymPy's complex infinity), not an error.
7. **Python disguised as math** → **`sympify` executes it** (it uses `eval`). A user message reached code execution on the host machine. The model refused in one run and complied in two, so the model can't be the safety layer.
8. **Wrong argument name** → the model quietly corrected it. No break.

**Lesson:** the model behaves *plausibly*; agents fail at the **boundary between model output and your code**.

## How to harden that boundary

- Use native `tools=` instead of parsing free text.
- Parse defensively (strip fences, catch errors, handle several calls), and **send errors back to the model as the tool result** so it can retry.
- Validate arguments against the schema before running anything.
- Never `eval`/`sympify` untrusted input. Use a whitelist evaluator, reject commas, and reject non-finite results.
