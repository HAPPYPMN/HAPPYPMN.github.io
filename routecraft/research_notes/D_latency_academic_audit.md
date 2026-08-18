# Router 文献“时间成本”审计

**审计日期：2026-08-17。** 范围为本地 `A_router_literature.md` 的主要完整模型 Router／Agent Router 论文，并用英文一手论文补查 Agent workflow serving、queue 和 prefix-cache 文献。这里的“时间成本”严格区分：单次 call latency、task wall-clock / time-to-success、p95/p99 tail、router overhead、queue/tool/retry/recovery、model switch 与 KV/prefix-cache loss。

## 一、结论

**没有一篇已核验的模型 Router 论文同时充分覆盖上述全部时间项。**当前证据是碎片化的：

- **Aragog**最完整地测了多工作流、多arrival rate下的 average/P25/median/P95 end-to-end latency、queue-aware scheduling 和 routing-overhead ratio；但没有 time-to-success、失败删失、retry/recovery、跨模型 KV cache loss 或 provider handoff。[Aragog](https://arxiv.org/abs/2511.20975)
- **TRACE-Router**最接近 Agent task wall-clock：live end-to-end、按 task 计时，明确包含 tool execution 与 environment interaction，并揭示“失败耗尽turn budget会同时拉低成功率、拉高latency”；但只报 mean，没有 p95/p99，也没有 switch/cache/queue分解。[TRACE-Router](https://arxiv.org/abs/2607.22465)
- **Harness-Native Data Flywheel**实际报告 task p50/p95 和 coverage；然而 routing配置包含并行/串行 proposer与aggregator，router自身、tool/search、queue、retry、switch/cache未独立分解，且不同方法完成/被judge的分母有时不同。[paper](https://arxiv.org/abs/2607.11399)
- **HyDRA**对 router 自身覆盖最好：ONNX INT8 CPU约55 ms P50 / 120 ms P99，并有大规模A/B的per-turn latency与TTFT方向；但没有公开task-level tail/time-to-success，也只把prompt-cache作为sticky-session设计动机而非实测loss。[HyDRA](https://arxiv.org/abs/2605.17106)
- **TwinRouterBench**对cache的**货币计费**最细（fresh input/cache-read/cache-write/output，并在tier switch/TTL/prefix change记cache miss），但没有测这些miss带来的prefill/queue/tail latency。[TwinRouterBench](https://arxiv.org/abs/2605.18859)

因此，现有调研可以支持“时间成本测量存在明显空白”，但不能写成“此前无人测端到端或尾延迟”。更准确的主张是：**尚未看到固定 Agent harness 上的完整模型 Router 同时报告 success-conditioned/censored task time、p95 tail、router/tool/retry/recovery、queue及跨模型cache/handoff的闭合时间账本。**

## 二、主要论文覆盖矩阵

符号：`✓`=论文明确实测；`△`=代理估计、只报均值/吞吐或只讨论；`—`=主实验未覆盖。`TTS`指 task end-to-end / time-to-success，而非单次generation。

| 工作 | call/model latency | task TTS | p95/p99 | router overhead | queue/tool | retry/recovery | switch/cache-loss 时间 |
|---|---:|---:|---:|---:|---:|---:|---:|
| FrugalGPT | △只称cache/cascade可影响latency | — | — | — | — | — | — |
| RouteLLM | △router requests/s | — | — | △吞吐与VM成本；非per-request分布 | — | — | — |
| LLMRouterBench | △建议用OpenRouter TTFT/TPS估算 | — | — | △称可忽略 | — | △API retry存在但未进时间账 | — |
| SCOPE | — | — | — | △router token/FLOP，无wall-clock | — | — | — |
| HyDRA | △生产per-turn/TTFT | — | **✓ router P99** | **✓ 55ms P50/120ms P99** | — | △per-turn error率 | △sticky/cache动机，无loss测量 |
| Router-R1 | △承认multi-round latency | — | — | — | — | — | — |
| R²-Router | — | — | — | △单query均值<400ms、<1% generation time | — | — | — |
| MTRouter | — | — | — | — | — | △error后switch/recover行为 | △讨论cache loss会增latency，未测 |
| TRACE-Router | — | **✓ live task wall-clock** | — | △“无可测latency” | **✓ tool/environment含在task时间** | △失败耗尽episode被task时间吸收，未分解 | △通过task pinning规避，未测switch |
| SWE-Router | — | — | — | — | — | △fixed-K探索和strong restart只进美元账 | — |
| TwinRouterBench | — | — | — | — | — | △failure penalty/retry公式；无时间 | △cache miss有货币账，无时间账 |
| Harness-Native | — | **✓ task latency** | **✓ p50/p95** | — | △web-search/provider含在总时间，未拆 | △记录schema有recovery，结果未拆 | — |
| Budget-Aware | △按标准token throughput估计 | △估计E2E | — | △估计<0.2s/<2%，非live | — | — | — |
| EASy | — | — | — | — | — | — | — |
| GraphPlanner | —（只报training wall-clock） | — | — | — | — | — | — |
| Critique Controller | △承认iterative latency | — | — | — | — | — | — |
| Agent-as-a-Router | — | — | — | △router美元成本，无wall-clock | — | — | — |
| Aragog | ✓ | **✓ E2E** | **✓ P25/P50/P95** | **✓ ≤3.5%低载、<1%高载** | **✓ arrival/queue；tool/framework仅aggregate** | — | — |

### 分档

- **相对充分覆盖：**Aragog（queue、E2E、tail、router ratio）；TRACE-Router（live task wall-clock且含tool/env）；Harness-Native（task p50/p95）；HyDRA（router p50/p99）。它们各自只覆盖一部分，不能合并成“某篇已完整核算”。
- **仅粗略覆盖：**RouteLLM（requests/s与VM cost）、R²-Router（平均<400ms）、LLMRouterBench（由TTFT/TPS推算）、Budget-Aware（标准化throughput模拟）、MTRouter（switch/recovery行为但无时间）、TwinRouterBench（cache/retry美元账但无时间）。
- **明显缺口：**FrugalGPT、SCOPE、Router-R1、SWE-Router、EASy、GraphPlanner、Iterative Critique Controller、Agent-as-a-Router没有可用于RouteCraft端到端时间结论的实测主结果。

> 纠错：先前 `A_router_literature.md` 将 R²-Router 误记为 `<1ms`；原文为**单query平均 `<400 ms`，约占总LLM generation time `<1%`**。已同步修正该笔记。

## 三、需要补充的英文一手论文

这些是**系统/测量邻近工作，不是完整模型 Agent Router baseline**；作用是给时间账本、tail、queue、tool与cache设计提供成熟测量方法。

1. **Agentix / Autellix: An Efficient Serving Engine for LLM Agents as General Programs.** 最相关的补充：把整个Agent program作为调度单位，测average、P95/P99 program latency、call/program waiting time、head-of-line blocking，并在多engine load balancing中权衡data locality与KV recomputation。arXiv版本名为Autellix；NSDI 2026正式预印本名为Agentix。[arXiv](https://arxiv.org/abs/2502.13965)；[USENIX NSDI 2026 PDF](https://www.usenix.org/system/files/conference/nsdi26/nsdi26spring_luo_prepub.pdf)
2. **ThunderAgent: A Simple, Fast and Program-Aware Agentic Inference System.** 统一调度KV cache、system state和tool resources，覆盖cache hit、tool lifecycle、serving/RL rollout throughput；适合定义tool等待、环境预热与cache thrashing指标，但论文重点是throughput而非RouteCraft的success-conditioned tail。[paper](https://arxiv.org/abs/2602.13692)；[official code](https://github.com/ThunderAgent-org/ThunderAgent)
3. **Scepsy: Serving Agentic Workflows Using Aggregate LLM Pipelines.** 用workflow trace构造per-LLM latency/throughput模型，在目标arrival rate下联合优化GPU share、TP与replica；可借鉴critical-path与多模型瓶颈建模，但它不做语义状态路由，且当前为preprint。[paper](https://arxiv.org/abs/2604.15186)
4. **Preble: Efficient Distributed Prompt Scheduling for LLM Serving (ICLR 2025).** 明确测average与p99 request latency，并把queueing、prefill、decoding纳入端到端request latency；核心是prefix reuse与load balance，适合作为“cache locality不是免费”的系统证据，但不是模型选择论文。[official ICLR proceedings](https://proceedings.iclr.cc/paper_files/paper/2025/hash/5bc342f48de8264779952fac378f96dc-Abstract-Conference.html)；[arXiv](https://arxiv.org/abs/2407.00023)
5. **DistServe: Disaggregating Prefill and Decoding for Goodput-optimized LLM Serving (OSDI 2024).** 用TTFT/TPOT SLO与goodput而非平均token速度，说明仅以tokens/s估算latency会忽略queue和SLO violation；适合作为单call latency分解方法。[USENIX](https://www.usenix.org/conference/osdi24/presentation/zhong-yinmin)

Aragog已在主Router语料中，必须从“邻近工作”提升到时间成本章节的核心参考，而不只是stage-level novelty对照。

## 四、RouteCraft 应采用的最低时间测量协议

1. **每次LLM call：**router time、queue wait、TTFT/prefill、decode/TPOT、tool wait、serialization/network；标记model、prefix length、cache read/write/miss、cold/warm residency。
2. **每次切换：**同state matched fork测 `stay` 对 `switch` 的额外queue + re-prefill + context serialization；不能只用cache-write美元价格代替时间。
3. **每个task：**wall-clock到成功验证；失败/timeout不能从均值中删除。报告success-by-deadline曲线、失败按deadline计的penalized time，或用censoring-aware restricted mean time-to-success；同时报告共同成功实例交集。
4. **分位数：**p50/p95，系统实验最好再给p99；按task family宏平均并对task做paired/cluster bootstrap。Phase 0只有100–200 tasks时，P95仅作探索性结果，不宜作主要显著性结论。
5. **分解失败成本：**retry、fallback、recovery、额外turn和无效reasoning分别累计；报告successful tasks与failed tasks的时间分布，避免“较弱模型失败更快”在平均latency上看似占优。
6. **负载条件：**至少idle/controlled-load两档。只测串行、无queue的本地执行无法支持tail latency或真实switch结论。

## 五、最重要缺口排序

1. **Time-to-success及失败删失处理：几乎空白。**现有论文多报平均completed-task latency；失败、被安全过滤、未judge的任务会改变分母。
2. **跨模型switch的真实时间：空白。**没有主要Router工作把cache miss、re-prefill、provider-private replay、model residency/queue与handoff分开实测。
3. **tail under load：仅Aragog/Harness-Native较强。**大多数方法只报均值、throughput或token-derived估计。
4. **tool/retry/recovery分解：空白。**TRACE将tool/env包含进总时间但不拆；Harness schema能记录，论文结果未闭合。
5. **router开销分布：只有HyDRA较完整。**RouteLLM/R²/Budget-Aware主要是吞吐、均值或估计，不能替代P95/P99。

**审计判断：**RouteCraft的时间维度有明确measurement价值；最稳妥贡献不是“首次关注latency”，而是“首次在固定Agent model-routing counterfactual中，将success/censoring、tail、router、tool/retry/recovery、queue及switch/cache/handoff统一成逐事件、可归因的time-to-success账本”。

