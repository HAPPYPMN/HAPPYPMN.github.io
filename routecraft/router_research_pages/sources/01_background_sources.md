# Page 01 source ledger — Why Router?

Last verified: 2026-08-17 (Asia/Shanghai)

## Scope and negative-evidence rule

This page asks two bounded questions: (1) why full-model routing is economically and technically motivated; and (2) what *publicly documented* routers major model/cloud platforms expose. “No first-party automatic router verified” means only that the official documentation reviewed below did not expose one. It is not evidence that the company has no internal routing system.

## Peer-reviewed and preprint research

| ID | Source | Status | Claims used |
|---|---|---|---|
| P0 | [ReAct](https://openreview.net/forum?id=WE_vluYUL-X) | ICLR 2023 | Interleaves reasoning traces, actions, and observations; used as the basic conceptual loop rather than a claim that every modern harness exposes explicit reasoning. |
| P1 | [FrugalGPT](https://openreview.net/forum?id=cSimKw5p6R) | TMLR 2024 | Query-level cascade; Table 3 evaluation-total API cost data: 98.3%, 73.3%, 59.2%, 75.4%, 52.3% savings on five datasets at matched best-single-model accuracy. |
| P2 | [RouteLLM](https://openreview.net/forum?id=8sSqNntaMr) | ICLR 2025 | Strong/weak prompt-level learned routing; author-reported >2× cost reduction in some public-benchmark settings without sacrificing response quality. |
| P3 | [TwinRouterBench](https://arxiv.org/abs/2605.18859) and [official code](https://github.com/CommonstackAI/TwinRouterBench) | arXiv preprint, 2026 | 970 router-visible prefixes/520 instances; full-agent dynamic track; each call selects a concrete model; official success and realized API spend. |
| P4 | [Agentic Routing: The Harness-Native Data Flywheel](https://arxiv.org/abs/2607.11399) and [OpenSquilla](https://github.com/opensquilla/opensquilla) | Technical report/preprint, 2026 | Full harness-state, step-level selection, LightGBM cold-start ranker, execution outcome/cost flywheel. |
| P5 | [TRACE-ROUTER](https://arxiv.org/abs/2607.22465) | arXiv preprint, 2026 | Live task-level wall-clock includes tool execution and environment interaction. Terminal-Bench §4.2 reports 270 s / 39.7% for always-27B and 172 s / 46.8% for TRACE-Router at α=0.75 on 48 matched tasks. The introduction says 268 s for the baseline; the page transcribes the detailed §4.2 result and discloses the discrepancy. |
| P6 | [MTRouter](https://aclanthology.org/2026.acl-long.2045/) and [official code](https://github.com/ZhangYiqun018/MTRouter) | ACL 2026 long paper | Per-Agent-turn full-model routing from recent-first trajectory history and model/cost features. |
| P7 | [SWE-Router](https://arxiv.org/abs/2607.00053) and [official Hugging Face organization](https://huggingface.co/SWE-Router) | ICML 2026 workshop preprint; source repository not verified | Cheap model explores for a fixed K turns before continue/restart-with-strong escalation; K is preset rather than learned as a re-decision boundary. |
| P8 | [HyDRA](https://arxiv.org/abs/2605.17106) | arXiv preprint, 2026; official code not verified | Session-sticky routing with compaction/drift events; used as evidence that continuity and cache-aware re-evaluation already have a direct precedent. |

## Local unpublished evidence

| ID | Source | Status | Claims used |
|---|---|---|---|
| L1 | MemoryCraft local manuscript（公开版未收录） | Unpublished submission; not citable as a published paper | Table 9 per-question means for Mem0, Supermemory, and MemOS; agent-issued vs harness-issued turn/input multipliers; loop changes ranking. PDF SHA-256: `82F96BF1B9E86AC206B31DE4DF50744B1B69230DBCD3B169A51A5D9B8A3D2289`. |

MemoryCraft contains PVLDB/DOI/artifact placeholders and incomplete metadata. It is used only as an internal methodological observation, not as published authority or as a Router baseline.

## Official vendor and system documentation

| ID | Entity | Official source | Publicly supported claim |
|---|---|---|---|
| V1 | OpenAI | [GPT-5 System Card](https://openai.com/index/gpt-5-system-card/) | Fast model + deeper reasoning model + real-time router; route signals include conversation type, complexity, tool needs, explicit intent; training signals include user switches, preference rates, measured correctness. |
| V2 | Microsoft | [Model Router concepts](https://learn.microsoft.com/en-us/azure/foundry/openai/concepts/model-router), [how-to](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/model-router), [agent integration](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/model-router-agents) | Trained language-model router, Quality/Balanced/Cost profiles, model subsets, automatic failover, per-request/per-agent-turn routing; caching only benefits consecutive overlapping prompts that select the same underlying model. |
| V3 | Google Cloud | [Gemini 2.5 and Model Optimizer announcement](https://cloud.google.com/blog/products/ai-machine-learning/gemini-2-5-pro-flash-on-vertex-ai), [Vertex AI pricing](https://cloud.google.com/vertex-ai/generative-ai/pricing) | Experimental meta-endpoint chooses Gemini intelligence appropriate for each prompt under cost/quality/balance preference; dynamic pricing. |
| V4 | AWS | [Bedrock Intelligent Prompt Routing](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-routing.html) | Exactly two models in the same family; per-prompt quality prediction; response-quality-difference criterion and fallback; English-only; cannot adapt decisions from application-specific performance data. |
| V5 | OpenRouter | [Auto Router](https://openrouter.ai/docs/guides/routing/routers/auto-router), [provider routing](https://openrouter.ai/docs/guides/routing/provider-selection) | NotDiamond-powered prompt selection over a curated pool; allowed-model control; session stickiness pins model and provider to preserve behavior and cache; provider routing/fallback is a distinct layer. |
| V6 | vLLM | [SAAR technical report/blog](https://vllm-project.github.io/2026/06/02/session-aware-agentic-routing.html), [Semantic Router repository](https://github.com/vllm-project/semantic-router) | Router-owned session memory; tool/provider-state locks; safe reset; prefix-cache, handoff, and switch-history penalties. Author-reported synthetic/live results are reproduced only with their conditions attached. |
| V7 | Cloudflare | [AI Gateway Dynamic Routing](https://developers.cloudflare.com/ai-gateway/features/dynamic-routing/) | Visual/JSON rule graph over request metadata, budgets, rate limits, A/B rollout, models, and fallbacks; this is policy routing, not documented learned capability prediction. |
| V8 | Tencent Cloud | [Model Routing product introduction](https://cloud.tencent.com/document/product/214/130981) | Unified API, automatic retry, and intelligent failure switch to another provider of the same model; internal beta. This is primarily availability/provider routing. |
| V9 | Anthropic | [Choosing the right Claude model](https://platform.claude.com/docs/en/about-claude/models/choosing-a-model), [model IDs and versioning](https://platform.claude.com/docs/en/about-claude/models/model-ids-and-versions) | Official first-party docs expose caller model/effort choice and recommend workload evaluation. No first-party automatic full-model selector was verified in the official docs reviewed. Bedrock/Foundry routing of Claude is attributed to those platforms, not Anthropic. |
| V10 | DeepSeek | [Models and pricing](https://api-docs.deepseek.com/quick_start/pricing), [reasoning model guide](https://api-docs.deepseek.com/guides/reasoning_model) | Caller selects model/mode; cache-hit and cache-miss prices are explicit. No first-party automatic full-model selector was verified in the official docs reviewed. |
| V11 | Alibaba Cloud | [Model Studio model catalog](https://www.alibabacloud.com/help/en/model-studio/models), [pricing](https://www.alibabacloud.com/help/en/model-studio/model-pricing), [agent applications](https://www.alibabacloud.com/help/en/model-studio/single-agent-application) | Public docs expose model catalogs, manual model selection, cache prices, monitoring, and agent construction. No automatic full-model quality/cost router was verified in the reviewed docs. |
| H1 | DeepSeek Harness | [Official repository at fixed commit `47f9438`](https://github.com/deepseek-ai/deepseek-harness/tree/47f943859bef60e4160492346772ded9b24f765a), [LLM streaming subsystem](https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/docs/subsystems/llm-streaming.md) | Concrete harness evidence for append-only session events, per-request model/provider replacement, tool-loop events, retries, and token/cache metering. External files, databases, processes, browsers, clocks, and RNG are not automatically restored by a session fork. |

## Derived local datasets

- `../assets/data/frugalgpt_tmlr_table3.csv`: transcription of P1 Table 3.
- `../assets/data/memorycraft_loop_metering.csv`: transcription of L1 Table 9 with derived `total_metered_tokens` and `output_share_percent`.
- `../assets/data/memorycraft_regime_multiplier.csv`: L1 regime multipliers.
- `../assets/data/vendor_router_landscape_2026-08-17.csv`: structured synthesis of V1–V11. Negative rows are bounded document-review findings, not universal absence claims.
- `../assets/data/trace_router_terminalbench_latency.csv`: transcription of P5 §4.2 Terminal-Bench mean task latency and resolved rate.
- `../assets/data/latency_evidence_coverage_audit.csv`: bounded coverage counts from the 18-work local latency audit; this is not a systematic-review prevalence estimate.

## Calculation notes

For MemoryCraft, `total_metered_tokens = cache_miss_input_tokens + cache_hit_input_tokens + output_tokens`; `output_share_percent = output_tokens / total_metered_tokens × 100`. This is a token-volume view, not a monetary-cost view: cache-read, cache-write, input, output, and reasoning tokens may have different prices.

The FrugalGPT percentages are reproduced as author-reported matched-accuracy results from a 2024 paper using its model pool, tasks, and price snapshot. They are not estimates of 2026 Agent cost per successful task.

## AI-assisted research disclosure

The source retrieval, comparison, data transcription, and HTML drafting were AI-assisted. Primary-source links and the local unpublished PDF were checked directly; readers should still revalidate dynamic vendor documentation before publication or deployment.
