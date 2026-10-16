# Module 2 · Task 1: recent facts without web access

Three questions with recent ground truth, each asked **5 times** (= 5 playground regenerations, default sampling) to two models. Raw answers are in `results.jsonl`; `run.py` reproduces the experiment and resumes if a connection drops.

| | Ground truth |
|---|---|
| **A** Python build without the GIL? | Yes: the free-threaded build, since **CPython 3.13** |
| **B** GPU architecture in Jetson Thor? | **Blackwell** |
| **C** Go methods with their own type parameters? First release? | Yes, since **Go 1.27** (August 2026) |

## Results (correct answers out of 5 runs)

| Model | A | B | C |
|---|---|---|---|
| `Nemotron-3_5-Lightning` | **4/5**: "Yes, since 3.13" ×4; one run said "No" | **4/5**: "Blackwell" ×4; one run dodged ("not branded under a known architecture") | **0/5**: always "Yes, since **Go 1.18** (2022)" |
| `NVIDIA-Nemotron-3-Nano-30B-A3B` | **0/5**: always "No, only experimental builds" | **0/5**: Ampere ×3, Ada Lovelace ×2 (one run even said Thor is "built around Orin") | **0/5**: "Yes, since Go 1.18" ×2, "Go 1.20" ×2, "No" ×1 |

**Do the answers match the ground truth? Partially.** Lightning gets A and B right in most runs. Neither model gets C right in any run, and Nano gets nothing right.

## Observations

1. **Knowledge cutoff decides what a model can know.** Lightning is the newer model and knows the 2024–2025 facts (the Python 3.13 free-threaded build, Blackwell in Thor). Go 1.27 shipped in August 2026, after both models' training data, so neither can know it.
2. **They answer confidently instead of saying they don't know.** No answer mentioned a knowledge cutoff or the possibility of being out of date. Both models invented specifics: release dates for the wrong Go versions, and for Thor "800 billion transistors" and "~1,000 TOPS".
3. **C is "right for the wrong reason".** Most runs said "Yes", but credited Go 1.18, which added generics. Methods with *their own* type parameters were **not** allowed until 1.27; the models confused this with methods on generic types. Nano's one "No" run was actually the correct answer before 1.27. A yes/no grader would wrongly mark most C answers as correct.
4. **Answers change between regenerations.**
   - Nano named three different "facts" for Thor across 5 runs.
   - Nano flipped Yes/No on C and gave two different release numbers.
   - Lightning flipped once each on A and B.

   **Disagreement across runs is a cheap signal that the model doesn't actually know.**
5. **Consistency isn't correctness.** Lightning said "Go 1.18" in all 5 runs, consistently wrong (and even gave two different dates for 1.18's release).
6. **This is why the agent needs web search.** For anything that may have changed after the cutoff, don't trust memory; retrieve evidence (Tavily search, then extract) and answer with citations.
