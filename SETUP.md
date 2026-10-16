# My setup

Local folder: `~/Desktop/Nebius/nvidia agent course` (this repo)
Fork of [Nebius-Academy/ai-agents-nv-notebooks](https://github.com/Nebius-Academy/ai-agents-nv-notebooks)

## Course model

Routing key on Nebius Token Factory: `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B`
Endpoint (OpenAI-compatible): `https://api.tokenfactory.nebius.com/v1/`

## Files

| Path | What it is |
|---|---|
| `module-1..4/` | Course notebooks. Completed ones have my solutions and outputs. |
| `notes/` | My study notes per notebook and video |
| `nemotron_nano.py` | Minimal Nemotron 3 Nano call via the `openai` SDK |
| `claude_opus.py` | Same call shape on Claude Opus 5 via `claude -p` (runs on your Claude subscription, no API credit) |
| `.env.example` | Template. Copy it to `.env` and add your key. |

Kept local and gitignored: `.env` (the API key), `module-1/lesson/.env` (a symlink to it), `.venv/`, `video-transcripts/`.

## First-time setup

```bash
cp .env.example .env            # then paste your NEBIUS_API_KEY
python3 -m venv .venv
.venv/bin/pip install openai anthropic python-dotenv rich sympy nbconvert ipykernel
mkdir -p module-1/lesson && ln -sf ../../.env module-1/lesson/.env
```

## Run

```bash
# Scripts
set -a; source .env; set +a
.venv/bin/python nemotron_nano.py
.venv/bin/python claude_opus.py   # needs Claude Code installed and logged in

# A notebook, end to end, saving outputs
cd module-1 && ../.venv/bin/jupyter nbconvert --to notebook --execute --inplace 01_intro_to_token_factory.ipynb
```

## Pull course updates

```bash
git fetch upstream && git merge upstream/main
```
