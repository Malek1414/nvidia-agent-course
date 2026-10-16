# Module 2: agentic web search

Video: "Intro to Agentic Web Search" (3:12), presented by a forward-deployed engineer from Tavily. Notebook: `module-2/web_search_tools.ipynb`.

## Why a model needs the web

- A model's knowledge is **frozen at its training cutoff**. The course's Nemotron model has a **June 2025** cutoff, so it knows nothing after that date.
- Questions about the present (this week's AI news, today's weather, current prices, the latest release) **can't be answered from memory**. The model either says it doesn't know or, worse, answers confidently from stale data.
- The course's running project is a **competitor research agent**: give it a company and it reports pricing changes, launches and funding rounds, with sources. Anything built from memory alone goes stale within weeks.

## Division of labor

| | LLM | Web |
|---|---|---|
| Good at | **Reasoning**: planning, comparing, synthesizing | **Current facts**: news, docs, releases, prices |
| Limit | Only reasons over what it can see; can't fetch anything new | Doesn't reason |

**Tools connect the two.** Reasoning is the model's job; current facts are the web's job.

## The two Tavily tools

| Tool | Input | Output | Use when |
|---|---|---|---|
| **Search** | A question or query | **Ranked results** with content and metadata, already shaped for an LLM to read | You don't know where the answer is yet |
| **Extract** | One or more **URLs** | The **clean full page as markdown** | You already have promising URLs and need their full content |

A typical sequence: **search** to narrow down to a few articles, then **extract** the most important ones.

## The research pattern: an agent loop, not a pipeline

1. **Search.**
2. The model decides: **is the evidence enough?**
   - **Yes:** answer, **with citations**.
   - **No:** choose the next step: **extract** a promising URL, or **search again** with a better query.
3. Decide again, and repeat.

Steps can repeat in any order. **The model choosing its next step is what makes this an agent loop rather than a fixed pipeline.**

**Rule of thumb:** when a question needs facts the model never saw in training, don't trust its memory; get evidence from the web.

## Task 1: recent facts without web access

Asked Lightning and Nano three recent-fact questions, 5 regenerations each ([full write-up](../module-2/task-1-knowledge-cutoff/README.md)).

| Model | A: no-GIL Python (3.13) | B: Jetson Thor = Blackwell | C: Go generic methods (1.27, Aug 2026) |
|---|---|---|---|
| Lightning | 4/5 | 4/5 | 0/5 (always "Go 1.18") |
| Nano | 0/5 | 0/5 (Ampere / Ada Lovelace) | 0/5 |

**Answer: partially.** Exam-relevant lessons:
- What a model knows is bounded by its **training cutoff**. A newer model knows more, but nothing after its cutoff.
- Models **don't say "I don't know"**. They invent confident specifics (versions, dates, specs).
- **Regenerations disagreeing** means the model is uncertain. **Consistent doesn't mean correct.**
- Plausible "right for the wrong reason" answers fool naive graders, so check the reasoning, not just yes/no.
- The fix is **retrieval**: search → (extract) → answer with citations.
