"""File Q&A chatbot on Nebius Token Factory with search_files as its only tool.

Run:  python app/agent.py [model]
"""
import json
import os
import sys
import time
from dataclasses import dataclass, field

from dotenv import find_dotenv, load_dotenv
from openai import OpenAI

from search_tool import search_files

load_dotenv(find_dotenv())

BASE_URL = "https://api.tokenfactory.us-central1.nebius.com/v1/"
DEFAULT_MODEL = "nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B"
MAX_ROUNDS = 5  # model calls allowed per user turn before the loop gives up

SYSTEM_PROMPT = """You answer questions about the files in a local project workspace.

You have one tool, search_files, which finds files by name pattern anywhere under a folder of the workspace.
- Call it only for questions about the local files: what exists, where something is, how many there are.
- Never call it for greetings, small talk, or general-knowledge questions (for example "what is quantization?"). Answer those directly.
- Before searching, check the conversation. If an earlier search result already answers the question, reuse it instead of searching again.
- For counts, use the "count" field of the tool result rather than counting the list yourself.
- Be concise: one to three sentences, or a short list of paths. Don't lecture or add background nobody asked for."""

SEARCH_TOOL = {
    "type": "function",
    "function": {
        "name": "search_files",
        "description": (
            "Find files in the local workspace whose names match a glob pattern (case-insensitive). "
            "Searches recursively under `subpath`. Returns the matching paths relative to the workspace root, and their count."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "name_pattern": {
                    "type": "string",
                    "description": "Glob pattern for the file name, e.g. '*.py', 'README.md', '*retry*'.",
                },
                "subpath": {
                    "type": "string",
                    "description": "Folder to search, relative to the workspace root. Use '.' for the whole workspace.",
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of paths to return, 1-100. Defaults to 20.",
                },
            },
            "required": ["name_pattern"],
            "additionalProperties": False,
        },
    },
}


def run_tool(name: str, arguments: str) -> str:
    """Execute one tool call and return its result as JSON text; errors go back to the model, not up the stack."""
    if name != "search_files":
        return json.dumps({"error": f"unknown tool: {name}"})
    try:
        args = json.loads(arguments or "{}")
        paths = search_files(**args)
    except (json.JSONDecodeError, TypeError, ValueError) as error:
        return json.dumps({"error": str(error)})
    result = {"count": len(paths), "paths": paths}
    if len(paths) == args.get("max_results", 20):
        result["note"] = "results may be truncated at max_results"
    return json.dumps(result)


@dataclass
class TurnStats:
    """What one user question cost: latency, tokens, and which tools the model asked for."""

    question: str
    answer: str = ""
    e2e_s: float = 0.0
    ttft_s: float | None = None
    input_tokens: int = 0
    output_tokens: int = 0
    model_calls: int = 0
    tool_calls: list[tuple[str, str]] = field(default_factory=list)


class FileAgent:
    def __init__(self, model: str = DEFAULT_MODEL, client: OpenAI | None = None):
        self.model = model
        self.client = client or OpenAI(base_url=BASE_URL, api_key=os.environ.get("NEBIUS_API_KEY"))
        self.reset()

    def reset(self):
        """Forget the conversation (chat memory is just this list, resent on every call)."""
        self.history = [{"role": "system", "content": SYSTEM_PROMPT}]

    def ask(self, question: str) -> TurnStats:
        stats = TurnStats(question)
        self.history.append({"role": "user", "content": question})
        start = time.perf_counter()

        for _ in range(MAX_ROUNDS):
            content, tool_calls, usage, first_token_at = self._stream_completion()
            stats.model_calls += 1
            if stats.ttft_s is None and first_token_at is not None:
                stats.ttft_s = first_token_at - start
            if usage:
                stats.input_tokens += usage.prompt_tokens
                stats.output_tokens += usage.completion_tokens

            if not tool_calls:
                stats.answer = content.strip()
                self.history.append({"role": "assistant", "content": stats.answer})
                break

            self.history.append({
                "role": "assistant",
                "content": content or None,
                "tool_calls": [
                    {"id": c["id"], "type": "function", "function": {"name": c["name"], "arguments": c["arguments"]}}
                    for c in tool_calls
                ],
            })
            for call in tool_calls:
                stats.tool_calls.append((call["name"], call["arguments"]))
                self.history.append({"role": "tool", "tool_call_id": call["id"], "content": run_tool(call["name"], call["arguments"])})
        else:
            stats.answer = f"(stopped after {MAX_ROUNDS} tool rounds)"
            self.history.append({"role": "assistant", "content": stats.answer})

        stats.e2e_s = time.perf_counter() - start
        return stats

    def _stream_completion(self):
        """One streamed model call. Returns (content, tool_calls, usage, time of first token of any kind)."""
        stream = self.client.chat.completions.create(
            model=self.model,
            messages=self.history,
            tools=[SEARCH_TOOL],
            stream=True,
            stream_options={"include_usage": True},
        )
        content, calls, usage, first_token_at = "", {}, None, None
        for chunk in stream:
            if chunk.usage:
                usage = chunk.usage  # some models resend running totals on every chunk; the last one is final
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta
            reasoning = (delta.model_extra or {}).get("reasoning")
            if first_token_at is None and (delta.content or reasoning or delta.tool_calls):
                first_token_at = time.perf_counter()
            content += delta.content or ""
            for part in delta.tool_calls or []:
                slot = calls.setdefault(part.index, {"id": None, "name": "", "arguments": ""})
                slot["id"] = part.id or slot["id"]
                if part.function:
                    slot["name"] += part.function.name or ""
                    slot["arguments"] += part.function.arguments or ""
        return content, [calls[i] for i in sorted(calls)], usage, first_token_at


def main():
    agent = FileAgent(sys.argv[1] if len(sys.argv) > 1 else DEFAULT_MODEL)
    print(f"File agent on {agent.model}. Ask about the sample workspace; 'reset' clears memory, 'quit' exits.")
    while True:
        try:
            question = input("\nyou> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if question in {"quit", "exit"}:
            break
        if question == "reset":
            agent.reset()
            print("(memory cleared)")
            continue
        if not question:
            continue
        s = agent.ask(question)
        print(f"bot> {s.answer}")
        tools = ", ".join(f"{name}({args})" for name, args in s.tool_calls) or "none"
        print(f"     [{s.e2e_s:.1f}s total | TTFT {s.ttft_s or 0:.1f}s | {s.input_tokens} in / {s.output_tokens} out | tools: {tools}]")


if __name__ == "__main__":
    main()
