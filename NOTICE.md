# Notices

This project includes software developed by third parties. The following sets forth required attributions and copyright notices for these components.

## Component 1: AgentDojo

Vendored under `Detection/benchmark/agentdojo/` from [github.com/ethz-spylab/agentdojo](https://github.com/ethz-spylab/agentdojo).

**License:** MIT License
**Copyright Notice:**
Copyright (c) 2024 Edoardo Debenedetti, Jie Zhang, Mislav Balunovic, Luca Beurer-Kellner, Marc Fischer, and Florian Tramèr

> **License Text:**
> Permission is hereby granted, free of charge, to any person obtaining a copy
> of this software and associated documentation files (the "Software"), to deal
> in the Software without restriction, including without limitation the rights
> to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
> copies of the Software, and to permit persons to whom the Software is
> furnished to do so, subject to the following conditions:
>
> The above copyright notice and this permission notice shall be included in all
> copies or substantial portions of the Software.
>
> THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
> IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
> FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
> AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
> LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
> OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
> SOFTWARE.

## Component 6: "Got a Secret? LLM Agents Can't Keep It" (fixture document)

Bundled as a benchmark fixture document under `Detection/context_providers/source_codes/mcp_servers_0/markdown_toolkit/environment/` (`paper.md`, `paper.pdf`, `paper2405.md`, `paper2405.pdf`) and `Detection/context_providers/source_codes/mcp_servers_0/ppt_toolkit/environment/` (`paper.pdf`, `paper2405.pdf`). Used as a realistic sample document for benign document-conversion benchmark tasks.

**Source:** arXiv:2605.27766 (https://arxiv.org/abs/2605.27766)
**Authors:** Aman Priyanshu, Supriti Vijay, Esha Pahwa
**License:** Creative Commons Attribution 4.0 International (CC BY 4.0) — https://creativecommons.org/licenses/by/4.0/

## Component 7: "ToolFailBench: Diagnosing Tool-Use Failures in LLM Agents" (fixture document)

Bundled as a benchmark fixture document under `Detection/context_providers/source_codes/mcp_servers_0/markdown_toolkit/environment/` (`paper2410.md`, `paper2410.pdf`) and `Detection/context_providers/source_codes/mcp_servers_0/ppt_toolkit/environment/` (`paper2410.pdf`). Used as a realistic sample document for benign document-conversion benchmark tasks.

**Source:** arXiv:2607.04686 (https://arxiv.org/abs/2607.04686)
**Authors:** Harsh Soni
**License:** Creative Commons Attribution 4.0 International (CC BY 4.0) — https://creativecommons.org/licenses/by/4.0/
## Component 2: YAML `!include` loader

Embedded in `Detection/benchmark/agentdojo/benchmarks/agentdojo/yaml_loader.py`, from [this gist](https://gist.github.com/joshbode/569627ced3076931b02f).

**License:** MIT License
**Copyright Notice:**
Copyright (c) 2018 Josh Bode

> **License Text:**
> Permission is hereby granted, free of charge, to any person obtaining a copy of this software
> and associated documentation files (the "Software"), to deal in the Software without restriction,
> including without limitation the rights to use, copy, modify, merge, publish, distribute,
> sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is
> furnished to do so, subject to the following conditions:
>
> The above copyright notice and this permission notice shall be included in all copies or
> substantial portions of the Software.
>
> THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT
> NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
> NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
> DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
> OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

## Component 3: YAML string representer snippet

Embedded in `Detection/benchmark/agentdojo/benchmarks/agentdojo/yaml_loader.py`, from [this Stack Overflow answer](https://stackoverflow.com/a/38370522).

**License:** CC BY-SA 3.0
**Copyright Notice:**
Copyright (c) Stack Overflow contributor, per [Stack Overflow's content license](https://stackoverflow.com/help/licensing)

## Component 4: OpenAI Python type re-definitions

Embedded in `Detection/benchmark/agentdojo/benchmarks/agentdojo/agentdojo_types.py`, re-derived from [openai/openai-python](https://github.com/openai/openai-python/blob/bba23438a63121102fe066982c91771fcca19c80/LICENSE).

**License:** Apache License 2.0
**Copyright Notice:**
Copyright (c) OpenAI

> **License Text:**
> See [Apache License, Version 2.0](https://www.apache.org/licenses/LICENSE-2.0).

## Component 5: LlamaFirewall

Consumed as a pip dependency (`llamafirewall` package, declared in `Detection/pyproject.toml`) from [meta-llama/PurpleLlama](https://github.com/meta-llama/PurpleLlama/tree/main/LlamaFirewall), called from `Detection/guardrail/llamafirewall_agent/llamafirewall_baseline.py`. Not vendored source.

**License:** MIT License
**Copyright Notice:**
Copyright (c) Meta Platforms, Inc. and affiliates.

> **License Text:**
> Permission is hereby granted, free of charge, to any person obtaining a copy
> of this software and associated documentation files (the "Software"), to deal
> in the Software without restriction, including without limitation the rights
> to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
> copies of the Software, and to permit persons to whom the Software is
> furnished to do so, subject to the following conditions:
>
> The above copyright notice and this permission notice shall be included in all
> copies or substantial portions of the Software.
>
> THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
> IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
> FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
> AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
> LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
> OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
> SOFTWARE.

## Component 6: "Got a Secret? LLM Agents Can't Keep It" (fixture document)

Bundled as a benchmark fixture document under `Detection/context_providers/source_codes/mcp_servers_0/markdown_toolkit/environment/` (`paper.md`, `paper.pdf`, `paper2405.md`, `paper2405.pdf`) and `Detection/context_providers/source_codes/mcp_servers_0/ppt_toolkit/environment/` (`paper.pdf`, `paper2405.pdf`). Used as a realistic sample document for benign document-conversion benchmark tasks.

**Source:** arXiv:2605.27766 (https://arxiv.org/abs/2605.27766)
**Authors:** Aman Priyanshu, Supriti Vijay, Esha Pahwa
**License:** Creative Commons Attribution 4.0 International (CC BY 4.0) — https://creativecommons.org/licenses/by/4.0/

## Component 7: "ToolFailBench: Diagnosing Tool-Use Failures in LLM Agents" (fixture document)

Bundled as a benchmark fixture document under `Detection/context_providers/source_codes/mcp_servers_0/markdown_toolkit/environment/` (`paper2410.md`, `paper2410.pdf`) and `Detection/context_providers/source_codes/mcp_servers_0/ppt_toolkit/environment/` (`paper2410.pdf`). Used as a realistic sample document for benign document-conversion benchmark tasks.

**Source:** arXiv:2607.04686 (https://arxiv.org/abs/2607.04686)
**Authors:** Harsh Soni
**License:** Creative Commons Attribution 4.0 International (CC BY 4.0) — https://creativecommons.org/licenses/by/4.0/