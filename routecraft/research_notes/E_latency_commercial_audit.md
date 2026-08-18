# 商业 API 与开源系统的时间成本覆盖审计

> 截止日期：2026-08-17（Asia/Shanghai）。审计对象：OpenAI、Anthropic、Google Vertex AI、AWS Bedrock、Azure OpenAI / Microsoft Foundry、OpenRouter、vLLM / vLLM Semantic Router、DeepSeek API / DeepSeek Harness、OpenSquilla。只使用官方文档、官方仓库和作者技术报告。  
> 标签：**[官方事实]**＝官方文档或固定提交代码直接支持；**[作者报告]**＝作者实验表述；**[推断]**＝据前述事实作出的研究判断；**[公开材料未找到]**＝本轮检索未找到，不等于功能一定不存在。

## 1. 决策结论

**[推断] 商业服务公开材料能够支撑“单次请求时间成本”的测量，却不能替代 RouteCraft 自建的 Agent `time-to-success` ledger。** 当前公开能力大致分三层：

1. OpenAI、Google、AWS、Azure、OpenRouter 和 vLLM 提供 TTFT、请求总延迟或吞吐中的一部分；AWS/vLLM 的 prefill/decode 解释最清楚，OpenRouter 的跨 provider 尾延迟路由最直接。
2. OpenAI/Anthropic/Google/AWS/Azure 提供优先级、预留吞吐、跨区域或 latency-optimized 等服务路径；这些是 **capacity/service-tier routing**，不是根据 Agent 任务状态选择完整模型。
3. 所有商业厂商都公开了某种 cache、限流/错误或 retry/fallback 机制，但其计量边界不统一。客户端看到的 TTFT 通常混合网关、网络、上游排队和 prefill；除自托管 vLLM 外，很难拆出真实 scheduler queue。

**[公开材料未找到]** 未找到任何一家商业 API 官方文档提供“从 Agent 任务开始，到外部 verifier 首次判定成功”的统一字段、SLA 或跨模型因果证据。最接近的是 OpenSquilla 作者报告中的任务级 p50/p95 wall-clock，但它没有把 queue、cache loss、retry、tool、switch 与成功分母完整拆开。因此主报告不得把 TTFT、TPS 或 uptime SLA 写成端到端 time-to-success 证据。

## 2. 统一口径

| 层级 | 定义 | 能回答什么 | 不能回答什么 |
|---|---|---|---|
| TTFT / first-byte | 请求发出或服务收到后至首 token/byte | 交互首响应；通常含排队与 prefill | 完成速度、Agent 是否成功 |
| TPOT / ITL / OTPS | 首 token 后的逐 token 延迟或输出吞吐 | decode 速度 | 工具、重试、额外轮次、失败恢复 |
| request E2E / TTLT | 一次物理模型 attempt 至最后 token | 单次调用 wall-clock | 多 attempt、tool loop、terminal success |
| task wall-clock | Agent 开始至终止 | 整体等待时间 | 若不接 verifier，终止不等于成功 |
| time-to-success | Agent 开始至外部 verifier 首次确认成功 | RouteCraft 应优化的时间目标 | 商业 API 通常不掌握任务 verifier |

并行 ensemble 必须同时报告：`elapsed wall-clock`、各分支 `compute/request time` 和总资源占用。只报告 elapsed 会掩盖并行消耗；只求和调用时间又会夸大用户等待。

## 3. 覆盖矩阵

图例：✅＝公开、可直接用；◐＝部分公开、需派生或仅特定 tier/API；—＝本轮公开官方材料未找到。

| 系统 | latency/service routing | TTFT / TPOT | queue / batch | cache 时间与计量 | fallback / retry | provider/model routing | SLA / tail | Agent time-to-success |
|---|---|---|---|---|---|---|---|---|
| OpenAI API | ◐ `service_tier` Priority/Scale/Flex | ✅ TTFT、Request Time、Token Velocity 百分位；无统一 TPOT 字段 | ◐ Batch 24h；`queued` 状态不是 scheduler queue time | ✅ cached tokens、cache retention；切模型可失去 cache domain | ◐ SDK retry；Priority 罕见降级到 Standard | — 完整模型任务路由 | ◐ Enterprise Priority/Scale uptime/速度承诺；Standard 无统一 latency SLA | — |
| Anthropic API | ◐ Standard/Priority、Fast mode | ◐ TTFT 定义与优化；Fast mode强调 OTPS 而非 TTFT | ◐ Message Batches 最长 24h，需求可影响速度 | ✅ prompt cache；Fast/standard 是不同 cache domain | ✅ SDK 默认重试；Priority 超容量回落 Standard | —（beta policy fallback 不等于负载路由） | ◐ 既有 Priority 有 uptime target；未见公开 tail-latency SLA | — |
| Google Vertex AI | ◐ DSQ 与 Provisioned Throughput | ✅ first-token 和 invocation-latency distribution；未见托管 Gemini 通用 TPOT | ◐ 429 建议 retry；有 batch 服务，未见交互 queue time | ✅ implicit/explicit context cache 与 cached-token burndown | ◐ 应用自行 retry 429；PT overage 可转 PAYG | ◐ 区域/容量路径，不是能力路由 | ◐ Vertex SLA 是 monthly uptime；未见 TTFT/TPOT SLA | — |
| AWS Bedrock | ✅ latency-optimized 与 cross-Region inference | ✅ TTFT、InvocationLatency、可派生 OTPS | ◐ throttle 指标、batch；无托管 scheduler queue time | ✅ CacheRead/CacheWrite tokens 和 prompt cache | ✅ optimized 配额耗尽回落 standard；SDK retry 影响 throttle 观测 | ✅ 区域/实例路径；另有 Bedrock intelligent prompt routing | ◐ 有 availability SLA；未见 request-tail latency SLA | — |
| Azure OpenAI / Foundry | ✅ Global/Data Zone routing、Provisioned、spillover | ✅ Time to Response/TTFT、normalized TTFT 等监控 | ✅ PT 满载立即 429 而非排队；有 batch deployment | ✅ cached tokens；prefix-hash routing | ✅ PT→Standard spillover；429 含 retry-after | ✅ 区域/部署路由；Model Router 属另一产品能力 | ◐ PT 有模型吞吐目标/可预测延迟表述；未见完整 task tail SLA | — |
| OpenRouter | ✅ 直接按 latency/throughput/price 排 provider | ✅ provider TTFT、throughput；p50/p75/p90/p99 滚动统计 | ◐ 上游 queue 吸收到观测延迟；无独立 queue 字段 | ✅ cached/read/write；按 conversation/session sticky provider | ✅ provider/model fallback，失败会增加本次延迟 | ✅ 多 provider、多模型列表与 fallback | ◐ 有尾延迟过滤阈值；未见公开 latency SLA | — |
| vLLM | ◐ serving scheduler；配 Semantic Router 才做模型选择 | ✅ TTFT、ITL/TPOT、E2E、prefill/decode | ✅ queue time、waiting/running、continuous batching 状态 | ✅ prefix/KV cache hits/usage/eviction | ◐ 部署层自行实现 retry/fallback | ◐ Semantic Router/session-aware；vLLM engine本身非任务路由 | 自托管，无厂商 SLA；可自行算 p95/p99 | — |
| DeepSeek API + Harness | — API 本身无 latency router；Harness 可逐调用换模型 | ◐ cache 新闻有单个 TTFT 示例；无标准 per-request TTFT/TPOT | — 未见 queue/batch 细分 | ✅ hit/miss input tokens；无公开 cache-write token | ✅ 429/500/503 建议 retry；Harness 有 request-error/retry 事件 | ◐ Harness 可换 provider/model，不是 API 自动 router | — 未见公开 latency SLA/tail dashboard | — |
| OpenSquilla 0.5.3 | ◐ per-turn route、provider probe、ensemble timeout | ◐ 有 provider latency probe；未见统一 TTFT/TPOT/queue schema | ◐ ensemble quorum/timeout；无物理 serving queue | ✅ cache read/write usage ledger，prompt-cache preservation | ✅ primary+fallback、physical-call ledger | ✅ 多 provider、多完整模型 | ◐ 作者报告部分任务 p50/p95；无服务 SLA | ◐ 作者报告 task wall-clock，但非 verifier-normalized 全量 TTS |

## 4. 厂商/系统逐项核验

### 4.1 OpenAI

- **[官方事实]** [API Service Health dashboard](https://help.openai.com/en/articles/1000499-api-service-health-dashboard)公开 Token Velocity、Request Time、TTFT 的百分位视图，并建议看 percentiles 而非 averages。它是账户流量的请求级健康视图，不是 Agent task 指标。
- **[官方事实]** [Priority processing FAQ](https://help.openai.com/en/articles/11647665-priority-processing-faq)允许按请求设置 `service_tier="priority"`；性能降级时极少量请求可能降为 Standard，实际 tier 应从响应确认。Priority 的企业 SLA 口径与 Scale Tier 对齐。
- **[官方事实]** [Scale Tier](https://openai.com/api-scale-tier/)列出 99.9% uptime 与按模型定义的 token-speed targets。这不是 TTFT、P95 task latency 或成功时间保证。
- **[官方事实]** [Batch API](https://platform.openai.com/docs/api-reference/batch/object)目前公开 `24h` completion window 和异步状态。`queued/in_progress` 是作业/响应状态；公开响应字段没有把物理 scheduler queue 单独计时。
- **[官方事实]** Responses API 的 usage/cache 字段可区分 cached input 与 reasoning/output；prompt cache 有 retention/key 机制。它没有公开 provider-private KV 的可迁移句柄。
- **[推断]** OpenAI 足以记录 `tier + TTFT + request time + token/cache`，但 retry、fallback、tool、verifier 和 switch 前后 cache 差需要客户端/Harness join；不能用 Scale token-speed SLA推导 Agent P95 time-to-success。

### 4.2 Anthropic

- **[官方事实]** [Service tiers](https://platform.claude.com/docs/en/api/service-tiers)说明 Standard 是 best effort；既有 Priority commitment 在容量内优先，超过容量可回落 Standard，响应 usage 记录实际 tier。该页的 Priority 目标主要是 uptime/capacity，不是 task-latency SLA。
- **[官方事实]** [Reduce latency](https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/reduce-latency)将 TTFT 作为基线指标；[Fast mode](https://platform.claude.com/docs/en/build-with-claude/fast-mode)明确优化输出 tokens/s，而不是 TTFT。Fast 和 standard 属不同 prompt-cache domain，切换会使已有 cache 无效。
- **[官方事实]** [Prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)支持预热并可降低首次交互 TTFT；[Message Batches](https://platform.claude.com/docs/en/build-with-claude/batch-processing)最长 24h，多数批次在一小时内完成，但速度受 demand 和 batch volume 影响。
- **[代码事实]** 官方 TypeScript SDK 的 [`maxRetries`](https://github.com/anthropics/anthropic-sdk-typescript/blob/main/src/client.ts)默认是 2，覆盖连接错误、408/409/429/5xx 等常见可重试错误。stream 已部分返回后通常不能无损透明重试，应用需把它记为新的 physical attempt。
- **[推断]** tier fallback、SDK retry 与 model fallback 必须分列。它们的延迟与 cache 后果不同；不能把“最终成功响应”的 usage 当作全部失败尝试成本。

### 4.3 Google Vertex AI / Gemini

- **[官方事实]** [Throughput quota](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/resources/throughput-quota)区分 Dynamic Shared Quota 与 Provisioned Throughput；DSQ 发生 429 时建议应用 retry，PT 是预留并优先服务的固定吞吐。
- **[官方事实]** PT monitoring 公开 `model_invocation_latencies` 与 `first_token_latencies` distribution；[Cloud Monitoring metric catalog](https://docs.cloud.google.com/monitoring/api/metrics_gcp_a_b)也将 first-token latency 定义为请求收到至首 token。公开托管 Gemini 指标中，本轮未找到通用 per-request TPOT/ITL 字段。
- **[官方事实]** [PT sizing](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/provisioned-throughput/measure-provisioned-throughput)使用 GSU/burndown 衡量输入输出吞吐；implicit/explicit caching 可降低 latency、价格和 throughput burndown。
- **[官方事实]** [Vertex AI SLA](https://cloud.google.com/vertex-ai/sla)公开的是 covered service 的 monthly uptime percentage；不能据此声称 TTFT、tail 或 time-to-success 达标。
- **[推断]** distribution 可计算服务侧 p95，但必须用 trace/request ID 与 Harness attempt 对齐；跨区域/DSQ/PT 路径变化和 429 retry 都是混杂变量。

### 4.4 AWS Bedrock

- **[官方事实]** [Bedrock runtime metrics](https://docs.aws.amazon.com/bedrock/latest/userguide/monitoring-runtime-metrics.html)公开 `InvocationLatency`（请求至最后 token）、streaming API 的 `TimeToFirstToken`、Input/Output tokens、throttles、`CacheReadInputTokens` 和 `CacheWriteInputTokens`。
- **[官方事实]** [OTPS 指南](https://docs.aws.amazon.com/bedrock/latest/userguide/monitoring-runtime-otps.html)给出 `OTPS = OutputTokenCount / (InvocationLatency - TimeToFirstToken)`，并建议用 p50 等 CloudWatch statistic。它是派生 decode throughput，不是 provider 直接返回的 task latency。
- **[官方事实]** [Latency-optimized inference](https://docs.aws.amazon.com/bedrock/latest/userguide/latency-optimized-inference.html)允许 `performanceConfig.latency=optimized`；超出配额或请求范围可回落 standard，响应/CloudTrail记录实际配置。[Cross-Region inference](https://docs.aws.amazon.com/bedrock/latest/userguide/cross-region-inference.html)按可用资源自动选 region，以提高吞吐/可用性。
- **[官方事实]** [Prompt caching](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-caching.html)显式区分 cache read/write，且 cross-region 高需求时可能增加 cache writes。Bedrock Mantle 文档同时明确其当前尚不发布 InvocationLatency/TTFT 对等指标，不能跨 endpoint 默认同等可观测。
- **[推断]** Bedrock 是商业 API 中最适合 request-level time decomposition 的一个，但 CloudWatch 仍未公开托管 scheduler queue。SDK retry 会改变 throttle/error计数，必须把客户端 attempt ID 单独持久化。

### 4.5 Azure OpenAI / Microsoft Foundry

- **[官方事实]** [Performance and latency](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/latency)区分系统 TPM 与 per-call latency，后者受模型、prompt/output 长度和部署负载影响；监控文档使用 Time to Response/TTFT 等指标。
- **[官方事实]** [Provisioned deployment operation](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/provisioned-get-started)明确：利用率满时立即返回 429 并给 `retry-after(-ms)`，而不是排队，从而保护已接受请求的延迟。这里的“无 queue”只表示 PT admission，不代表客户端/网关/网络无等待。
- **[官方事实]** [Spillover](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/spillover-traffic-management)可在 PT 429/500/503 时自动转 Standard，并明确这种优先尝试可能增加延迟；费用也分 PT 与 Standard token账单。
- **[官方事实]** [Prompt caching](https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/prompt-caching)用 prefix hash 路由，响应 `cached_tokens`；改变前缀或切换不兼容 deployment 会产生 miss。
- **[推断]** Azure spillover 是 RouteCraft 测 switch/retry 成本的优质真实反例：故障恢复提高可用性，却可能增加 TTFT/总时间并改变价格。实验必须记录 executed deployment，而不能只记 requested deployment。

### 4.6 OpenRouter

- **[官方事实]** [Provider routing](https://openrouter.ai/docs/guides/routing/provider-selection)用最近 5 分钟滚动统计的 p50/p75/p90/p99 latency/throughput，支持 `preferred_max_latency`、`preferred_min_throughput`、price/throughput sort 和 `allow_fallbacks`。不满足阈值的 endpoint 被降优先级而非绝对排除。
- **[官方事实]** [Latency and performance](https://openrouter.ai/docs/features/latency-and-performance)说明失败 primary 会增加该请求延迟，系统会绕开近期故障 provider；冷 edge cache 和低余额检查也会增加 gateway latency。
- **[官方事实]** [Prompt caching](https://openrouter.ai/docs/guides/best-practices/prompt-caching)按 account/model/conversation 做 sticky provider，可用 `session_id` 明确会话；sticky endpoint 不可用时再 fallback。该机制与 vLLM Semantic Router 的 session continuity 同类，但不观察 Agent PLAN/VERIFY/RECOVER 状态。
- **[官方事实]** [Generation metadata](https://openrouter.ai/docs/api/api-reference/generations/get-generation)公开 `latency`、`generation_time`、`moderation_latency`、provider/model/router、cached/reasoning tokens 与费用；[usage accounting](https://openrouter.ai/docs/cookbook/administration/usage-accounting)公开 cache read/write 和 upstream cost。
- **[推断]** OpenRouter 是 latency-aware provider/model routing 的强系统 baseline，但其 rolling provider metric 是观察性统计，且 upstream queue 被吸收到 TTFT/throughput；它没有 Agent verifier，不能估计“换模型后更快成功”的局部因果效应。

### 4.7 vLLM 与 vLLM Semantic Router

- **[官方事实]** [Production Metrics](https://docs.vllm.ai/en/latest/usage/metrics/)公开 request queue/prefill/decode/E2E/TTFT/ITL、waiting/running、KV usage、prefix-cache hit/query、preemption 等直方图。自托管时这是唯一能直接观察 scheduler queue 与 cache residency 的本审计对象。
- **[官方事实]** [Per-request Metrics](https://docs.vllm.ai/en/latest/features/per_request_metrics/)可返回 `queue_time_ms`、`time_to_first_token_ms`、`generation_time_ms`、`mean_itl_ms`、`tokens_per_second`；高并发下启用可能带来不可忽略 CPU overhead，`n>1` 时无法准确归因而抑制该对象。
- **[官方事实]** vLLM Semantic Router v0.3 的 [session-aware configuration](https://vllm-semantic-router.com/docs/v0.3/installation/configuration/)具有 session memory、tool/provider-state locks、idle/drift reset、prefix-cache checkout cost 和 replay-derived remaining-turn prior。这是 stay/switch 成本规则，不是成功监督下的 task TTS 预测器。
- **[推断]** RouteCraft 本地实验应以 per-request metric join attempt；同时保留全局 Prometheus load snapshot。不能从同一时间窗的全局 histogram 给单一 fork 归因，也不能忽略观测本身的 CPU overhead。

### 4.8 DeepSeek API 与官方 DeepSeek Harness

- **[官方事实]** [Context Caching](https://api-docs.deepseek.com/guides/kv_cache)返回 `prompt_cache_hit_tokens`/`prompt_cache_miss_tokens`，best-effort cache 的构建需数秒、通常数小时到数天清理。官方新闻给出 128K 高重复输入 TTFT 从 13s 到 500ms 的单一示例；这是厂商特定条件结果，不是普遍 tail 保证。
- **[官方事实]** [Error Codes](https://api-docs.deepseek.com/quick_start/error_codes/)对 429/500/503 建议等待/重试；本轮未找到标准 per-request TTFT/TPOT、scheduler queue、batch latency 或公开 latency SLA 字段。
- **[代码事实]** DeepSeek Harness 固定 commit [`47f943859bef60e4160492346772ded9b24f765a`](https://github.com/deepseek-ai/deepseek-harness/tree/47f943859bef60e4160492346772ded9b24f765a)有逐调用 `agent/request`、`agent/request-error`、retry 和 token/cache usage 事件，但核心 TokenUsage 不提供 provider queue/batching/prefill/decode；这些必须接服务层 trace。详见本地 [`B_harness_systems.md`](./B_harness_systems.md)。
- **[推断]** DeepSeek cache 示例证明 cache 能显著改变 TTFT，恰好反对“按单价估算时间/成本”；它不能证明跨模型切换后的 cache loss 数值，必须 same-state stay/switch 实测。

### 4.9 OpenSquilla

- **[代码事实]** 固定 commit [`79d57b2fe63e1f83b364ca2bd022e0cb76081406`](https://github.com/opensquilla/opensquilla/tree/79d57b2fe63e1f83b364ca2bd022e0cb76081406)（0.5.3）实现 per-turn full-model routing、primary/fallback、provider probes、ensemble quorum/timeout、decision ledger 和物理 provider-call token/cache/cost ledger。release notes 称 provider probe 报告 latency；未见统一 TTFT/TPOT/physical queue 字段。
- **[作者报告]** *Agentic Routing: The Harness-Native Data Flywheel*（arXiv:2607.11399v1，本地 PDF 已归档）在部分 multi-model 表中报告 task p50/p95 seconds。例如 DRACO ensemble 表以完整 benchmark execution 比较 wall-clock，但表中没有 queue/cache loss/retry/tool/switch 分解；singleton 主表也没有同步列出 latency。
- **[推断]** 这是本审计中最接近 Agent 端到端 latency 的公开证据，但仍不是 `time-to-success`：报告的是完成任务的 wall-clock/benchmark score operating point，未用统一外部 verifier 定义“首次成功时间”，也未以失败/删失数据构造 success-normalized latency。

## 5. 本地调研覆盖复核

- [`A_router_literature.md`](./A_router_literature.md)已指出：LLMRouterBench 使用 OpenRouter TTFT/TPS 近似；TRACE 报 end-to-end wall time；Aragog 使用 live load/queue；大多数 routing 论文忽略 Router、cache、retry 和 p95。它没有系统横向核验商业 service tier/SLA。
- [`B_harness_systems.md`](./B_harness_systems.md)已覆盖 DeepSeek Harness、vLLM 和 OpenSquilla 的事件/usage/queue边界，并正确指出 Harness token meter 不等于完整时间成本。
- [`C_theory_trajectory.md`](./C_theory_trajectory.md)已建议 quantile/survival、queue/load snapshots 和 terminal success。本审计新增的关键证据是：Azure PT明确“不排队而立即429”、OpenRouter按最近5分钟 p90/p99路由、AWS可由TTFT和InvocationLatency派生OTPS、Anthropic fast/standard切换会破坏cache domain。

## 6. RouteCraft 必须自建的时间 ledger

**每个物理 attempt：**

```text
task_id, state_id, fork_id, turn, step, attempt
requested_provider/model/tier, executed_provider/model/tier, route_chain
t_router_start/end
t_request_start, t_first_byte, t_first_token, t_last_token, t_request_end
server_queue_ms?, prefill_ms?, decode_ms?, network_gateway_residual_ms?
cache_read/write/miss_tokens, private_state_kept/lost
status/error_code, retry_after_ms, retry/fallback_parent_attempt
input/output/reasoning tokens, provider_cost
load_snapshot, region, endpoint, batching_snapshot
```

`?` 表示只有服务端或自托管 serving 暴露时才可观测；不可观测时应记 `unknown`，不能填 0。`TTFT - known_queue - known_network` 也不应被直接命名为 prefill，除非 trace 边界一致。

**每个 Agent task：** 另记 router、tool、verifier、recovery、world restore 的 span，以及 terminal verifier outcome。主要时间指标建议为：

- 成功任务的 `time-to-first-verified-success` p50/p95；失败任务作为 right-censored 或单列 timeout，不从分母静默删除；
- `total wall-clock / #success` 与 `total provider-compute-seconds / #success` 分开；
- retry/fallback wasted seconds、tool waiting、router deliberation、context replay/prefill penalty、switch-induced queue/cache delta；
- 分任务族宏平均，并对 same-state stay/switch 做 paired bootstrap；价格/负载漂移实验同时记录 tier、region 和 load snapshot。

## 7. 对主报告的直接约束

1. 不得把 token/s、TTFT 或 uptime SLA称为 task latency 或 time-to-success。
2. 不得把 Batch 的 `queued` 状态称为在线 scheduler queue time；远程商业 API 未公开 queue 时标为不可观测。
3. fallback 的“最终成功”必须保留所有先前 attempt 的 token、时间和 cache/state loss。
4. provider routing（OpenRouter）、region/capacity routing（AWS/Azure/Google）、service-tier routing（OpenAI/Anthropic）与 Agent capability model routing 必须分栏。
5. Phase 0 至少报告两套时间结果：`provider-request-only` 与 `end-to-end verified task`。若动态策略只改善 TTFT 而没有改善 time-to-success，不能支持 RouteCraft 的系统主张。
6. **最关键负面证据：** OpenRouter 已能按近期 p90/p99 latency与throughput进行 provider/model fallback，vLLM Semantic Router 已给 cache/session continuity定价。RouteCraft 的时间新颖性只能来自“在可验证 Agent 状态上联合学习模型与承诺边界，并按完整 time-to-success/switch cost 评估”，不能来自一般 latency-aware routing。

## 8. 最终审计判断

**覆盖充分度：请求层为“中等到强”，Agent成功层为“弱”。** AWS/vLLM 能较好拆 request latency，OpenRouter能做公开 tail-aware provider routing，Azure明确 admission/spillover latency语义，OpenAI/Google提供分布监控；但没有商业系统公开统一的 Agent time-to-success、跨模型 switch/cache 因果代价或 failure-recovery latency。因此，商业文档可用于定义测量字段与系统 baseline，不能作为候选方法已经改善端到端时间的证据。Phase 0 必须自行做 matched fork + verifier + physical-attempt spans；否则关于“更省时间”的结论应标为未核验。
