# Replicating the ALRPHFS and GuardAgent Baselines

Instructions for implementing and running the ALRPHFS and GuardAgent baseline detectors against ADR-Bench, for comparison against the numbers in Table 2. Neither baseline ships as code in this repo — this document describes each method well enough to build your own implementation from the published papers.

## Evaluation harness contract

To run a baseline against ADR-Bench through this repo's `main_detector.py`, implement the `BaseDetector` interface defined in `Detection/guardrail/base_detector.py`:

1. Subclass `BaseDetector`.
2. Implement the two abstract methods:
   - `analyze_conversation(messages) -> DetectionResult` — the core detection logic.
   - `is_available() -> bool` — whether the detector is configured and ready (e.g. API keys present, models loaded).
3. Optionally override `analyze_task()` if you need custom task-level handling beyond the default per-conversation flow.
4. Populate `DetectionResult` with at least: `task_id`, `is_malicious`, `confidence_score`, `total_messages`, `threat_messages`, `detections`, `method`.

`Detection/guardrail/llamafirewall_agent/llamafirewall_baseline.py` is a good template to read first — it wraps a pip-installed dependency rather than vendoring source, which is the pattern to follow if you're building on top of a package the original authors released, rather than reimplementing from scratch.

To wire a new detector into the CLI:

1. Import your detector class at the top of `main_detector.py`.
2. Add its name to the `--detector` `choices` list in the argparse setup.
3. Add an `elif args.detector == "your_detector":` branch in the dispatch block that instantiates your class, reading its settings from a new section in `config_detector.yaml`.

---

## ALRPHFS

**Citation:** Shiyu Xiang, Tong Zhang, Ronghao Chen. "ALRPHFS: Adversarially Learned Risk Patterns with Hierarchical Fast & Slow Reasoning." [arXiv:2505.19260](https://arxiv.org/abs/2505.19260).
**Original code:** [ShiyuXiang77/ALRPHFS](https://github.com/ShiyuXiang77/ALRPHFS)

### Method

A three-stage pipeline run over each conversation or query:

1. **Essence extraction.** Prompt an LLM to abstract the input into a generalized "essence" — the underlying strategy or intent, stripped of surface wording (paraphrase, role-play framing, hypothetical scenarios). This normalizes obfuscated attacks that vary in phrasing but share intent.
2. **Fast thinking.** Embed the essence and compute cosine similarity against a library of pre-computed "attack essence" embeddings. The library is built offline via an adversarial self-learning loop that iteratively refines a balanced set of harmful/benign patterns — see the paper for the full offline training procedure. Two thresholds classify the result: similarity above the high threshold → harmful; below the low threshold → benign; in between → ambiguous, escalate to stage 3.
3. **Slow thinking.** For ambiguous cases, prompt a second (typically stronger) LLM with the essence, the most-similar known attack pattern, and the original input, asking for a harmful/benign judgment with reasoning.

### Hyperparameters

- Embedding model: `text-embedding-3-large`
- Fast-thinking thresholds: harmful ≥ 0.38, benign ≤ 0.25 (from the authors' `defence_online.py` — tune against your own pattern library rather than treating these as universal)
- Slow-thinking model: Claude, `max_turns: 10`, `timeout: 60`

### Pattern library

The 301-pattern library used for fast-thinking similarity is published in the authors' repo at [`method/risk_pattern_data/unsafe.json`](https://github.com/ShiyuXiang77/ALRPHFS/blob/main/method/risk_pattern_data/unsafe.json) — each entry has `id`, `scenario`, `attack_essence`, `harmful_result`, and related fields; use `attack_essence` as the text to embed. If you want to build your own instead (e.g. to cover a different threat domain), the paper's offline pattern-generation procedure — adversarial refinement over a labeled harmful/benign set — is implemented in `method/offline_train_harmful.py` / `offline_train_benign.py` in the same repo.

---

## GuardAgent

**Citation:** Zhen Xiang, Linzhi Zheng, Yanjie Li, Junyuan Hong, Qinbin Li, Han Xie, Jiawei Zhang, Zidi Xiong, Chulin Xie, Carl Yang, Dawn Xiaodong Song, Bo Li. "GuardAgent: Safeguard LLM Agents by a Guard Agent via Knowledge-Enabled Reasoning." [arXiv:2406.09187](https://arxiv.org/abs/2406.09187).
**Original code:** [guardagent/code](https://github.com/guardagent/code)

### Method

A code-generation-based guardrail, run per agent input/output pair:

1. **Task decomposition.** Prompt an LLM to break the guard request (a set of security policies) into 2–4 concrete, checkable subtasks, given the agent's input and output.
2. **Example retrieval.** Select the *k* most similar prior (input, output, subtasks, generated-code) examples from a memory bank, using Levenshtein distance between the current and stored input/output pairs, to use as few-shot demonstrations in the next step.
3. **Code generation.** Prompt an LLM to write a short Python snippet — using only the input/output variables, no function definitions — that raises an error if a violation is detected, following the format of the retrieved examples.
4. **Code execution.** Run the generated snippet in a restricted namespace; a raised error means a violation was found.

### Hyperparameters

- Model: `gpt-4o`, `temperature: 0`, `max_tokens: 1000`
- `num_shots: 3`
- Guard rules checked: data exfiltration, privilege escalation, credential theft, policy violation, unauthorized modification

### Memory bank

GuardAgent doesn't ship a static memory file — the authors' `guardagent.py` takes memory as a runtime argument (`update_memory(num_shots, memory)`) seeded from a `CodeGEN_Examples` list defined per target agent (`request_ehr.py` for their EHR-agent benchmark, `request_seeact.py` for SeeAct — both in [guardagent/code](https://github.com/guardagent/code)), then grows during execution: each correctly-predicted case is appended (`long_term_memory.append(new_item)`) as a new few-shot example for later cases. Since neither published seed targets ADR-Bench/AgentDojo-style tasks, write your own `CodeGEN_Examples`-equivalent — a handful of (input, output, subtasks, code) tuples covering your threat categories — and let the memory grow from there as you run it.

---

## Validation

Compare against the paper's Table 2 (also reproduced in [../Detection/README.md](../Detection/README.md) and [REPRODUCIBILITY.md](REPRODUCIBILITY.md)) on ADR-Bench's 42 malicious / 261 benign tasks:

| Detector   | Precision | False positives |
| ---------- | --------- | ---------------- |
| ALRPHFS    | 0.333     | 34                |
| GuardAgent | 0.231     | 30                |

Only precision and false-positive count are reported for these two baselines — recall and F1 aren't published for them, so don't expect to validate against those. Using the authors' published pattern library, ALRPHFS should land close to the reported numbers; GuardAgent depends on the memory bank you seed, so treat agreement there as a sanity check on method correctness rather than a bit-exact match.
