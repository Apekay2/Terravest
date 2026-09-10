# Open Source Release Notes

Summary of repository contents, data handling, and third-party attributions for the ADR research release accompanying [arXiv:2605.17380](https://arxiv.org/abs/2605.17380).

## Repository contents

- `Detection/` — ADR-Bench, dual-agent detector, LlamaFirewall baseline, MCP fixtures, evaluation scripts.
- `Sensor/` — ADR Sensor library for collecting and normalizing AI coding-agent telemetry.
- `CITATION.cff` — Primary paper citation metadata.
- Public repository: [github.com/uber/ADR](https://github.com/uber/ADR)

## Data and fixtures

`Detection/` includes synthetic benchmark material:

- AgentDojo integration and benchmark fixtures (vendored under `benchmark/agentdojo/`).
- SQLite/database fixtures for emulated MCP tool environments.
- Document, image, and audio fixtures for MCP server test environments. Document fixtures include two CC-BY-4.0-licensed arXiv papers bundled as realistic sample documents for benign document-conversion tasks (see `NOTICE.md` Components 6 and 7 for attributions).
- Synthetic policy, threat-intelligence, and prompt-injection data in YAML/JSON.

**Review outcome:**

- Fixtures are for **defensive** AI-agent security evaluation only.
- Credential-like strings are **synthetic** and intentionally included to exercise detection behavior.
- No production customer, employee, or business-confidential data is included.
- Benchmark execution does not require access to private infrastructure.

## Isolation and non-production use

This benchmark is a research artifact, not a production system. It must be run in an isolated environment (container, VM, or dedicated host).

- **Pinned dependencies with known CVEs:** Several dependencies are pinned to exact versions for benchmark reproducibility (matching the paper's evaluation). These pins are retained intentionally; the CVEs they carry are acceptable under the benchmark's isolated threat model but would not be acceptable in a production deployment. See the project's pyproject.toml for the pinned set (marked `# AgentDojo dependencies (exact versions from baseline)`).
- **Synthetic attack material:** Benchmark fixtures include synthetic credentials, prompt-injection payloads, and emulated vulnerable MCP servers (see "Data and fixtures" above). These are intentional and must not be exposed to production networks or real data.
- **No production data:** Benchmark execution does not require access to private infrastructure, real credentials, or production systems.
- **LlamaFirewall baseline dependency tree:** The `llamafirewall` package (used for the LlamaFirewall baseline comparison) hard-depends on `torch` and `transformers`, which in turn pull the NVIDIA CUDA runtime packages and carry known CVEs. These are retained for baseline reproducibility and are acceptable under the benchmark's isolated threat model.

Consumers integrating any of this code into a production system must re-evaluate the dependency set and upgrade pinned packages to current fixed versions.

## Synthetic credential disclosure

Security scanners may flag synthetic credential-like strings in `Detection/` (fake AWS keys, API tokens, session strings, prompt-injection payloads). These are benchmark fixtures, not real credentials.

## Third-party components


| Component                   | Location / usage                                                           |
| --------------------------- | -------------------------------------------------------------------------- |
| AgentDojo                   | `Detection/benchmark/agentdojo/` — MIT license, see `LICENSE` and `NOTICE` |
| LlamaFirewall / PurpleLlama | `Detection/guardrail/llamafirewall_agent/` — MIT license, pip dependency, see `NOTICE.md` |
| OpenAI SDK types            | `Detection/benchmark/agentdojo/benchmarks/agentdojo/agentdojo_types.py`    |
| YAML `!include` loader (MIT) | `Detection/benchmark/agentdojo/benchmarks/agentdojo/yaml_loader.py` — from [Josh Bode gist](https://gist.github.com/joshbode/569627ced3076931b02f), see `NOTICE.md` Component 2 |
| YAML string representer (CC BY-SA 3.0) | `Detection/benchmark/agentdojo/benchmarks/agentdojo/yaml_loader.py` — from [Stack Overflow](https://stackoverflow.com/a/38370522), see `NOTICE.md` Component 3 |


## Testing


| Component     | Tests                                                                               |
| ------------- | ----------------------------------------------------------------------------------- |
| `Sensor/`     | Parser, schema, utility, and observer unit tests (`uv run pytest`)                  |
| `Detection/`  | Deterministic unit tests for pack/unpack, metrics, parsers (`uv run pytest tests/`) |
| LLM detectors | Evaluated via benchmark workflow — see [REPRODUCIBILITY.md](REPRODUCIBILITY.md)     |


## License

Apache License 2.0 — see [LICENSE](../LICENSE). Vendored AgentDojo code is MIT — see [Detection/benchmark/agentdojo/LICENSE](../Detection/benchmark/agentdojo/LICENSE). Third-party attributions are in [NOTICE.md](../NOTICE.md).