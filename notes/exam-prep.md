# Exam prep: Nebius certifications

Source: the official exam guides, kept locally (not in this repo).

## Format (identical for both exams)

- **Multiple choice:** every question has **one correct answer and three distractors** (4 options).
- **1 hour**, remote, AI-assisted proctoring, delivered on a partner exam platform.
- No prerequisites. The guides don't state the number of questions or the pass score.

---

## Nebius Agentic AI Builder (the exam this course prepares for)

**Role:** builds AI-powered apps on Token Factory: agentic workflows, RAG, fine-tuning, external tools like Tavily, plus evaluation, prompt tuning and monitoring of usage, latency and cost. Responsible for the **application layer, not the infrastructure**.

Coverage legend: ✅ covered in my notes · 🟡 partly · ❌ not yet

### 1. Running inference on Token Factory (~20%)

| Topic | Coverage | Where |
|---|---|---|
| Connecting an app to Token Factory | ✅ | NB1: OpenAI-compatible, `base_url` + `NEBIUS_API_KEY` |
| Chat completions and streamed responses | ✅ | NB1, NB3 (streaming, `include_usage`, reasoning field) |
| Prototyping in the Playground | ✅ | NB1 video, NB3 metrics |
| Choosing a model for cost, latency and quality | ✅ | NB1 card exercise, NB3 cost exercise, chapter-task benchmark |
| Generation parameters: determinism vs creativity | 🟡 | NB1 ex3: `temperature`, `seed`, `top_p` (and why hosted MoE still varies) |
| Batch processing for high-volume, latency-tolerant work | ❌ | |

### 2. Building agentic AI (~35%)

| Topic | Coverage | Where |
|---|---|---|
| Structured, schema-constrained outputs | 🟡 | Tool JSON schemas (NB2, chapter task); response formats not yet |
| Agent loop with short- and long-term memory | 🟡 | Short-term: chat history (NB1, chapter task). Long-term: not yet |
| Web search (Tavily) and tools via MCP | ❌ | Module 2 (Tavily); MCP not yet |
| Agent reasoning, tool use and error recovery | 🟡 | NB2 breaks, chapter task (errors returned to the model, round cap) |
| Evaluating agent output quality | ❌ | Module 4 (LLM-as-a-judge, deep research evals) |
| Guardrails, approvals and cost budgets | 🟡 | Spend limit per key (NB3); the rest not yet |

### 3. Customizing a model with your own data (~20%)

| Topic | Coverage | Where |
|---|---|---|
| Preparing and uploading training datasets | ❌ | Not in the course notebooks |
| Fine-tuning jobs in Token Factory **Data Lab** | ❌ | |
| Deploying and calling fine-tuned models | ❌ | |
| Prompting vs RAG vs fine-tuning | ❌ | |
| Interpreting training results | ❌ | |
| LoRA vs full SFT vs distillation | ❌ | |

### 4. Production AI operations (~25%)

| Topic | Coverage | Where |
|---|---|---|
| Rate limits with client-side backoff | 🟡 | Saw per-model TPM/RPM limits in the catalog; backoff not yet |
| Issuing and rotating API keys, safeguarding secrets | 🟡 | `.env`, never commit keys, one key per project (NB1, NB3) |
| Data retention and deletion controls | ❌ | |
| Inference capacity for the traffic shape | ❌ | |
| Cost: model choice, prompt size, caching | 🟡 | Model choice and resent history (NB3, chapter task); caching not yet |
| Data residency and compliance | 🟡 | Catalog lists a region per model (Nano `eu-north1`, Ultra/Super `us-central1`) |

**Gaps the course notebooks don't cover:** batch inference, fine-tuning/Data Lab, MCP, data retention, capacity, caching, residency. These need the Token Factory docs.

---

## Nebius AI CloudOps (separate track, not covered by this course)

**Role:** keeps GPU clusters running day to day: deploys from templates, manages access, watches dashboards, restarts failed nodes, follows runbooks and escalates. Makes **no architecture decisions**.

| Domain | Weight | Topics |
|---|---|---|
| 1. Security, compliance and billing | ~20% | Platform authentication; IAM; encryption and secret management; governing spend; shared responsibility |
| 2. Setting up and operating GPU clusters | ~35% | GPU instances; storage and disk lifecycle; networking; Kubernetes with GPU drivers; cluster health and GPU readiness; InfiniBand fabric |
| 3. Training and inference workloads | ~20% | Distributed jobs; persistent and shared storage; ready-made inference apps; choosing orchestration; managed Slurm under live load |
| 4. Platform automation and maintenance | ~25% | Infrastructure as code; planned and unplanned maintenance; network and storage diagnosis; GPU and interconnect health events; observability stack |

Preparing for this exam needs the Nebius AI Cloud docs (Compute, Managed Kubernetes, Slurm, InfiniBand, Terraform, monitoring).
