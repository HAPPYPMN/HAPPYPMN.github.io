# Page 02 source ledger — Router 工作与决策粒度

Last verified: 2026-08-18 (Asia/Shanghai)

## 1. 本页回答的问题

Page 02 不按年份或 Router 模型大小罗列论文，而按四个系统变量组织：

1. Router 在什么时候获得重新选择完整模型的机会；
2. 做决定时可以读取哪些 Agent 状态；
3. Router 能执行的是模型选择、回答验收、停止还是流程配置；
4. 该方法是否保持原 Agent workflow 不变。

主线只覆盖完整模型选择。Workflow generation、role selection、termination controller 和 serving scheduler 作为邻近路线单列，不能混写为同一类 Agent Router。

结构化工作清单见 [`../assets/data/related_work_decision_granularity_2026-08-17.csv`](../assets/data/related_work_decision_granularity_2026-08-17.csv)。逐论文完整证据卡、成本审计与 SHA256 见 [`../../research_notes/A_router_literature.md`](../../research_notes/A_router_literature.md)；系统固定提交核验见 [`../../research_notes/B_harness_systems.md`](../../research_notes/B_harness_systems.md)。

## 2. 直接路线：请求前 routing 与回答后 cascading

- **FrugalGPT** — Chen, Zaharia, Zou. TMLR 2024. [Paper](https://openreview.net/forum?id=cSimKw5p6R) · [Code](https://github.com/stanford-futuredata/Frugalgpt). 固定 cascade 最多调用三种 API；每次回答后由 DistilBERT reliability scorer 接受或升级。作者在其 2023 年价格和任务设置下报告同质量最高约 98% 节省。没有 Agent trajectory、tool state、cache、handoff 或任务级时间核算。
- **RouteLLM** — Ong et al. ICLR 2025. [Paper](https://openreview.net/forum?id=8sSqNntaMr) · [Code](https://github.com/lm-sys/RouteLLM). strong/weak 二元池对 query 一次选择；主要训练信号来自约 80K Chatbot Arena 偏好。作者报告相同质量超过 2×、最高约 3.66× cost saving；未覆盖 Agent loop。
- **Models Under SCOPE** — Cao et al. arXiv preprint 2026. [Paper](https://arxiv.org/abs/2601.22323) · [Project](https://sullivan07043.github.io/SCOPE/). 约 250 anchor probes 形成模型 behavioral fingerprint；Qwen3-4B 为各候选预测 correctness 和 output length。论文报告 7 seen + 4 unseen models。项目页写 future release，官方代码未核验。
- **R²-Router** — Xue et al. ICML 2026 / PMLR 306. [Paper](https://arxiv.org/abs/2602.02823) · [Code](https://github.com/UCF-ML-Research/R2-Router). 对单次 query 联合选择 model 与 reasoning/output-token budget。作者报告 Router 平均低于 400 ms、低于 generation time 的 1%，并在其设置下将 token cost 降 4–5×。第二个动作是生成预算，不是未来重开 Router 的时机。
- **LLMRouterBench** — Li et al. Findings of ACL 2026. [Paper](https://aclanthology.org/2026.findings-acl.1881/) · [Code](https://github.com/ynulihao/LLMRouterBench). 超过 400K queries、21 datasets、33 models、10 routing baselines 的冻结 query × model outcome benchmark。包含 SWE/τ² 来源不等于执行 live Agent trajectory。

## 3. 直接路线：task pinning 与固定 K 升级

- **TRACE-Router** — Raj et al. arXiv preprint 2026. [Paper](https://arxiv.org/abs/2607.22465). admission 时用 contextual UCB 选择 backend，随后按 task ID 固定到终止；用 terminal accuracy 和 end-to-end latency 更新。作者在其 TerminalBench 设置下报告约 +7.1 points 且 latency 低 36%。代码未核验。
- **SWE-Router** — Son et al. ICML 2026 workshop preprint. [Paper](https://arxiv.org/abs/2607.00053) · [Model organization](https://huggingface.co/SWE-Router). cheap model 固定探索 K turns，value head 判断它是否能最终成功；若否，strong model 从原 issue 重启。K 是超参数，源码仓库未核验。
- **Agent-as-a-Router** — Zhou et al. arXiv preprint 2026. [Paper](https://arxiv.org/abs/2606.22902) · [Code](https://github.com/LanceZPF/agent-as-a-router). 每个 coding task 只选择一次模型，任务完成后把验证反馈写入跨任务 memory。它是 task-terminal commitment 与 continual feedback，不在单任务内动态切换。

## 4. 直接路线：逐轮或逐调用读取轨迹

- **MTRouter** — Zhang et al. ACL 2026 long. [Paper](https://aclanthology.org/2026.acl-long.2045/) · [Code](https://github.com/ZhangYiqun018/MTRouter). 每个 Agent turn 用 Qwen3-Embedding-0.6B 编码最长约 8192 tokens 的 recent-first history，再与 model ID/cost/profile 联合选模型。论文训练集约 515K turns。作者在 ScienceWorld 报告 53.8 vs always-GPT-5 48.4，成本低 58.7%；router、cache loss、tool 与 handoff 未进入统一成本。
- **Hera** — Zhang et al. arXiv preprint 2026. [Paper](https://arxiv.org/abs/2605.24598). 在 ALFWorld、WebShop、AppWorld 中逐 step 选择 device/cloud 模型。第一阶段把 cloud 轨迹中的每个状态重放给 device，并以两者 action agreement 作监督；第二阶段对跨 rollout 的相同状态分组，用终局 return 和未来 cloud-call 数生成偏好。作者报告达到 cloud-only success 的 92.5%，cloud 使用占 46.3% steps。它直接阻断“首个 step-level device/cloud Agent Router”及“首次用未来调用成本监督逐步路由”等主张；其重新决策边界仍固定为 next step。官方代码未核验。
- **Budget-Aware Agentic Routing** — Zhang et al. arXiv preprint 2026. [Paper](https://arxiv.org/abs/2602.21227). Qwen2.5-1.5B 每一步读取完整历史和剩余预算，输出 SMALL/LARGE；用 BoSFT + GRPO 训练。严格预算下 First-Large 仍有竞争力。官方代码未核验。
- **TwinRouterBench** — Yang et al. arXiv preprint 2026. [Paper](https://arxiv.org/abs/2605.18859) · [Code](https://github.com/CommonstackAI/TwinRouterBench). static track 对 strong 成功轨迹逐 step downgrade，并以固定 continuation 检查终局；dynamic track 记录 input/cache-read/cache-write/output。100-task live setting 中，作者报告 logistic router 75/100、$25.66，对比 Opus 74/100、$54.73。局部 downgrade 不是多 boundary 的长期 policy oracle。
- **Agentic Routing: The Harness-Native Data Flywheel** — TokenRhythm Technologies. technical report/preprint 2026. [Paper](https://arxiv.org/abs/2607.11399) · [OpenSquilla code](https://github.com/opensquilla/opensquilla). step-level action 可读取 observation、context、control、artifact、tool history、recovery 和 verification；LightGBM 是 cold-start ranker。作者报告 PinchBench score 93.14、平均 billed cost $0.0204/task；同一 OpenSquilla harness 的 fixed Opus score 94.33、$0.1649/task。DRACO score 52.33、$0.3729/task vs 52.36、$0.6559/task。IPS/DR/flywheel 多数是设计蓝图，cache-aware 列为未来工作。

## 5. 直接路线：逐请求连续性规则与固定系统事件

- **HyDRA** — Garg et al. arXiv preprint 2026. [Paper](https://arxiv.org/abs/2605.17106). 首 turn 路由并 sticky，仅在 compaction/background-summary 等固定事件重路由。149M ModernBERT 预测需求，再与实测 capability profile 匹配。论文的 production A/B 相对 prior router control 报告 per-inference-request cost 低 2.3%，但 aggregate segment COGS 因请求量变化大致持平；7–20% 是相对该 segment 全部使用旗舰模型的估算，不能写成生产 A/B 的 COGS 降幅。55 ms p50 / 120 ms p99 是 offline CPU routing overhead；arXiv landing abstract 另报 production median 86 ms，两种口径不应混用。cache 是策略动机，但逐请求 cache loss 核算未清楚披露。官方代码未核验。
- **vLLM Session-Aware Agentic Routing (SAAR)** — official open-source system, v0.3. [Official blog](https://vllm-project.github.io/2026/06/02/session-aware-agentic-routing.html) · [Fixed code](https://github.com/vllm-project/semantic-router/tree/ef9e5dd99c953a21d20a99a93547e57468bae863) · [Related framework paper, not the source of SAAR method/results](https://arxiv.org/abs/2603.04444). 每个请求先跑 base selector，再按 session memory、tool/provider state、idle/drift、prefix cache、handoff 与 switch history 决定 stay/switch；此处 drift 是 matched routing decision name 改变，不是 Agent 语义阶段推断。作者在 21,600 deterministic synthetic turns 报告 switches −79.29%、unsafe switches 3,836→0、作者估算的 physical-model cost −78.71%；这些不是包含 Router、工具、重试、恢复和部署开销的总任务成本，也不是外部 verifier 监督的 boundary policy。`unsafe switch` 和 `continuity violation` 是策略定义的约束指标，不是外部 verifier 下的任务错误率。
- **OpenSquilla 0.5.3** — official open-source system. [Technical report](https://arxiv.org/abs/2607.11399) · [Fixed code](https://github.com/opensquilla/opensquilla/tree/79d57b2fe63e1f83b364ca2bd022e0cb76081406). 每 turn 读取语义消息、前一 assistant output/usage、近五次路由历史、历史 user text 与附件，并计算、记录 `KEEP_PROVIDER / USE_PORTABLE_FALLBACK / DISCARD_PROVIDER_STATE` portability diagnostic；当前所引 Router 代码不足以证明它会自动硬锁、迁移或恢复 provider-native state。另有 router decision ledger 与 physical-call usage ledger。默认 Router 还会改变 reasoning/prompt policy，最高 tier 可 ensemble，直接 baseline 必须冻结这些改写。

> **证据去重：**Harness-Native 是 OpenSquilla 生态的技术报告，OpenSquilla 0.5.3 是固定提交实现审计。两者是方法叙述与代码事实两个证据层，不计为两个独立系统。`router_control` 的 hold 由用户显式请求触发，再由 Agent tool 执行；不是 Agent 自主学习出的承诺。

## 6. 邻近路线：workflow、milestone、termination

- **GraphPlanner** — Feng et al. ICLR 2026. [Paper](https://openreview.net/forum?id=ZdGB7MNQDT) · [Code](https://github.com/ulab-uiuc/GraphPlanner). 联合选择 Agent role、模型并生成 workflow graph。不是固定 Agent workflow 上只替换模型。
- **EASy** — Liu et al. preprint, under review 2026. [Paper](https://arxiv.org/abs/2608.04588). 7B orchestrator 生成 milestone、DAG 与 executor assignment；milestone 是有价值的 temporal abstraction，但收益混入 replanning/workflow generation。代码未核验。
- **Aragog** — Dai et al. arXiv preprint 2025. [Paper](https://arxiv.org/abs/2511.20975) · [Official lab page](https://nexs.scs.gatech.edu/publications/2025-aragog.html). 在固定 DAG stage 根据 load/queue 选择模型配置；stage 已由 workflow 给定，优化重点是 serving throughput/latency。代码未核验。
- **Router-R1** — Zhang, Feng, You. NeurIPS 2025. [Paper](https://arxiv.org/abs/2506.09033) · [Code](https://github.com/ulab-uiuc/Router-R1). 约 3B policy 生成 subquery、选择 candidate LLM 并聚合；它改变了解题流程。
- **Iterative Critique-and-Routing Controller** — Fang et al. arXiv preprint 2026; formal acceptance and code unverified. [Paper](https://arxiv.org/abs/2605.08686). 每轮读取 draft，联合输出 next model 与 stop/continue。stop 表示结束当前 refinement；continue 后下一轮仍重路由，不是“保持模型直到未来可验证事件”。
- **ARC / Learning to Configure Agentic AI Systems** — Taparia, Sagar, Senanayake. arXiv preprint 2026. [Paper](https://arxiv.org/abs/2602.11574). 将 query-level agent configuration 表述为 SMDP，每种 workflow/tool/budget/prompt configuration 是处理整条 query 的 temporally extended option；HRL 策略为不同 query 选配置。它不是任务内完整模型路由，但说明“agent configuration + temporal option / learned commitment”的宽泛表述已有直接先例。
- **AgentSwing** — Feng et al. arXiv preprint 2026. [Paper](https://arxiv.org/abs/2603.27490) · [Codebase linked by paper](https://github.com/Alibaba-NLP/DeepResearch). 当 context length 超过预设比例时，在同一轨迹状态并行展开多种 context-management branch，再用 lookahead Router 选择 continuation。作者报告在其 web-agent 设置中最多减少约 3× interaction turns。它选择的是上下文管理策略，trigger point 仍由规则给定，不是完整模型或未来 reopen boundary。
- **SyncPlan** — You et al. arXiv preprint 2026. [Paper](https://arxiv.org/abs/2608.01652). 轻量 Plan Staleness Detector 持续检查剩余 multi-agent plan，在环境变化使其假设失效时触发 replanning。它阻断宽泛的“首次学习何时重新考虑决策”主张；但动作是重新规划，不是切换完整模型，论文写明 code/data 将公开，执行日未核验到官方仓库。

## 7. 本页综合判断的证据边界

### 已有明确先例，不能作为 RouteCraft 首创

- prompt-level、cascade、task pinning、固定 K escalation；
- per-turn/per-call、history-aware、trajectory-aware、harness-native；
- candidate-conditioned profile 与有限 unseen-model transfer；
- session-aware、cache/handoff-aware stay/switch；
- fixed stage/milestone model assignment；
- next-model 与当前 task termination 的联合控制；
- same-prefix/common-continuation 的局部 counterfactual benchmark。
- query-level agent configuration 的 SMDP/option 表述，以及 context/plan 的 learned continuation 或 staleness trigger。

### 尚可检验、但没有被证明有净收益

在固定 Agent workflow 中，把动作定义为“完整模型 + 下一次重新开放路由的可验证未来边界”，用同状态、同外部世界快照的 model × boundary fork 取得标签，并在 Router、cache、replay、retry、handoff、tool 与 time-to-success 全部计入后，与最佳 task pinning、fixed-K、per-call、固定 event 规则比较。

这是本报告基于已核验文献作出的研究判断，不是任何单篇论文的结论。若最佳固定边界已经获得几乎全部 dynamic-oracle 收益，或 learned policy 退化为 task-terminal/next-call，则该独立方法假设不成立。

还必须区分三种 estimand：看到真实结果后的 outcome-oracle opportunity、给定部署时可观测状态的 Bayes-optimal gain、以及 held-out learned Router 的实际 gain。Oracle gap 是必要的现象检查，不是可学习收益的证据；最佳固定模型和最佳 Router 也不能在同一评测样本上选择后再作普通 paired inference。

## 8. 本轮新增 PDF 完整性记录

| Local file | SHA256 |
|---|---|
| `papers/02_agent_routing/2026_Hera.pdf` | `4C4637FE0C68241F43CBF3696A681DA2C64F85DFD34D0688EBA276F890F721CF` |
| `papers/05_theory_methods/2026_ARC_Learning_to_Configure_Agentic_AI.pdf` | `E2EDC0B2838962274BB54B95B45CD277105299E8A28565EE6A899C515E260692` |
| `papers/05_theory_methods/2026_AgentSwing.pdf` | `1AEE88E500CBD23E2AF649B270FD22E17C16A7857E4B2CB29C368FCBD684BC46` |
| `papers/05_theory_methods/2026_SyncPlan.pdf` | `598C19D91E1F350A49B15C10087443054EFD971500E68CF6B5AE1BA87AC9991E` |

四份文件均以 PDF 首页渲染核对标题、作者与摘要；方法事实另由全文文本提取定位。SyncPlan PDF 的内部 dictionary 存在 Poppler 语法警告，但首页和全文正文可正常渲染、提取，SHA256 如上保留。

## 9. 三篇补充文献：序列级 routing、Agent 逐步 routing 与 Oracle 可实现性

- **A Unified Approach to Routing and Cascading for LLMs** — Dekoninck, Baader, Vechev. ICML 2025 / PMLR 267. [PMLR](https://proceedings.mlr.press/v267/dekoninck25a.html) · [Code](https://github.com/eth-sri/cascade-routing). 对同一 query 先选一个模型，再根据已得回答重新选模型，直到估计质量足够；它统一了 prompt-level routing 与 cascading，但没有 Agent 轨迹、工具观测或外部世界状态。理论最优性依赖对各模型质量和成本的可用估计；作者也将质量估计识别为成败的关键。对 RouteCraft 的边界是：“回答后再选模型”已有理论先例，但重开时机仍是每次候选回答后的固定序列。
- **EvoRoute: Experience-Driven Self-Routing LLM Agent Systems** — Zhang et al. arXiv preprint v1, 2026. [Paper](https://arxiv.org/abs/2601.02695). 它在复杂 workflow 的每个 sub-task / step 前选择完整 LLM；用 agent role、sub-task 语义和预测工具从经验库检索历史记录，估计候选模型的 task performance、step cost 和 wall-clock duration，做 Pareto 过滤后用 Thompson sampling 选择。作者报告最高约 80% 货币成本与超过 70% 延迟降低；这些是该论文的 benchmark 结果，未单列 router 检索/工具预测、cache loss 和跨模型 handoff 的净开销。它直接覆盖“逐步 + history/experience-aware + cost/latency-aware 的 Agent 完整模型 Router”；每步都重开，不学习未来重开边界。论文写明代码将发布到 `bingreeky/evo-route`，执行日该链接返回 404，因此官方代码标记为**未核验/未可用**。
- **Opportunity Is Not Realizability: Selection-Valid Diagnostics for Multi-LLM Routing** — Shihab, Al Ahsan, Swaqeeb. arXiv preprint v1, 2026. [Paper](https://arxiv.org/abs/2608.08265). 该文不提出 Agent Router，而是区分 outcome-oracle opportunity、指定部署前信号下的 Bayes-optimal gain 和 held-out learned-router gain，并给出选择最佳固定模型/最佳 Router 后仍有效的置信区间。作者在 4 个 benchmark 上报告经选择校正的 Oracle gap 为 9.7–30.7 个点，而最强的可部署 prompt Router 只恢复 7.5%–14.4% 的 gap；11 个候选策略中最佳策略的 simultaneous interval 下界均为 0。对 RouteCraft 的直接要求是：Phase 0 不能把 model×boundary dynamic Oracle 优势当作 PlanIR 可学习性；基线和 Router 选择必须与最终测试分开。论文提到 artifact，但 arXiv 页和 PDF 未给出可核验的官方代码地址。

### PDF 完整性

| Local file | Pages | SHA256 |
|---|---:|---|
| `papers/01_model_routing/2025_Unified_Routing_and_Cascading.pdf` | 24 | `2E9F7E42FED197ABBD23DE7E0ED2071510D92383B64F5E1FFE3FCD447854B65D` |
| `papers/02_agent_routing/2026_EvoRoute.pdf` | 13 | `E2D15A2B14A85FD0C0360F5947610B74306B2C0AB78AB09ECE2937F95AC33E9D` |
| `papers/05_theory_methods/2026_Opportunity_Is_Not_Realizability.pdf` | 20 | `90A21BA188434EF13536D5F93EFA91C306E7A8771BEFCE066CAA8660E77A8DA4` |

三份文件均以 `%PDF-1.7` 开头，`pdfinfo` 可正常解析；全文经 `pdftotext -layout` 检索方法与结论，首页以 150 DPI 渲染后人工核对，未见裁切、字体丢失或页面损坏。

## 10. Page 02“代表方法精讲”的图表与公式出处

页面中的方法图均为根据原论文结构制作的 HTML/CSS 重绘，不是原图截图，也不表示完成了代码复现。公式按论文或固定源码等价转写；作者结果只适用于各自的模型池、价格、任务与执行协议。

| 精讲工作 | 页面采用的原始材料 | 页面保留的核心公式 / 规则 | 解释边界 |
|---|---|---|---|
| FrugalGPT | Figure 3（PDF 第 7 页）、Table 3（第 8 页） | cascade 停止位置 `z=min{i:g(q,f_Li(q))≥τ_i}`；预算约束下搜索顺序与阈值 | 只观察候选回答；2023 价格；无 Agent、cache、tool 或 wall-clock |
| RouteLLM | Figure 1（PDF 第 2 页）、Equation 2、Tables 1–3/7 | `P(strong wins|q)` 与阈值 α；PGR | Arena-only 在 MMLU/GSM8K 的负结果必须与 MT-Bench 正结果同时呈现 |
| R²-Router | Figures 2/4/5/7/8（PDF 第 2、5、7、8、12 页） | `argmax_(M,b)[(1−λ)Q̂−λC]` | 联合的是模型与当前生成预算；完整 profiling/Judge 成本不能被轻量预测头训练时间掩盖 |
| TRACE-Router | Figure 2（PDF 第 4 页）、Equations 9/11、Figure 3、Table 1 | 每 context 的 UCB；terminal accuracy–latency reward | task pinning；Terminal-Bench 子集 48 项；wall-clock 较完整但无货币/cache/能耗分解 |
| SWE-Router | Figure 1、Algorithm 1、Theorem 4.1（PDF 第 2–3 页）、Table 2 | `continue cheap iff r̂(T_≤K)≥θ`；`V(S_t)≥V(Q)` | 定理未扣 K 轮 rollout、strong restart、cache/replay 与延迟；最佳 K 随模型对和分布变化 |
| MTRouter | Figure 2、Equations 3–8（PDF 第 3–4 页）、Table 3 | history×candidate outcome score；error-adjusted terminal target | 逐 turn 重开已被覆盖；训练日志不是每状态严格 matched counterfactual；总成本未闭合 |
| TwinRouterBench | Figure 2（PDF 第 6 页）、Algorithm A1（第 17 页）、Table 3（第 10 页） | sequential-locking downgrade；input/cache-read/cache-write/output 四桶成本 | 固定 greedy 顺序与 continuation 下的局部 sufficiency，不是全轨迹 joint-policy Oracle |
| HyDRA | Figure 1、Equations 1–5（物理第 3–4 页）、Section 8 sticky policy | 四维需求预测；`Σ w_k max(0,r̂_k−c_mk)` shortfall；固定 turn-1/compaction/summary 事件 | predictor 不读 prior assistant/tool/repository state；生产 A/B 与 all-flagship 估算采用不同参照系 |
| vLLM SAAR | 官方 blog Figures 3/8；固定提交 `session_aware.go` 与 `session_aware_scoring.go` | tool/provider hard lock；adjusted stay/switch score；prefix/handoff/history penalty | 官方 blog + 开源实现而非同行评议论文；21,600 turns 为 deterministic synthetic workload；成本为 estimated physical-model cost |

### 两项本轮纠错

1. HyDRA 正文的 production A/B 相对 prior router control 报告 per-inference-request cost `−2.3%`，aggregate segment COGS 大致持平；`7–20%` 是相对 routed segment 全部使用旗舰模型的估算。正文 `55 ms P50 / 120 ms P99` 是 offline CPU routing overhead，arXiv landing abstract 的 production median `86 ms` 是另一口径。
2. `vLLM_Semantic_Router_arXiv2603.04444.pdf` 是相关 Signal-Decision Router 框架论文，不是 SAAR 方法、参数与实验结果的来源；SAAR 事实应链接官方 blog 与固定提交代码。

## 11. Page 02“Router 额外成本”证据审计

Page 01 定义价格与时间成本的类别；Page 02 新增部分只回答两个证据问题：现有论文实际测到了哪些 Router 额外开销，以及哪些项目仍未在同一 Agent 任务账本中闭合。不同论文的数字来自不同模型池、负载与执行协议，不能直接相加。

| 成本环节 | 已有一手证据 | 可以陈述的事实 | 仍未闭合 |
|---|---|---|---|
| 在线 Router | RouteLLM Table 7；R²-Router；Hera；HyDRA；vLLM SAAR | RouteLLM 报吞吐与 VM 成本换算；R² 报平均 `<400 ms`；Hera 实测约 `61 ms/step`；HyDRA 报 offline CPU `55 ms P50 / 120 ms P99`；SAAR 报 selector p95 | 并发负载下的统一 p95/p99、能耗，以及 Router 开销是否已从主 Pareto 曲线扣除 |
| 离线训练、Judge 与 profile | RouteLLM；SCOPE；R²-Router | RouteLLM 披露约 `$700` 的 Judge 数据构建与训练硬件；SCOPE 每个候选模型用 250 anchors；R² 给出新模型接入示例 | 原始数据矩阵、强教师/Judge、训练、持续更新的总成本与合理摊销范围 |
| Cascade、升级与 restart | FrugalGPT；Unified Routing and Cascading；SWE-Router | FrugalGPT 和 Unified 已累计实际发生的多模型调用；SWE-Router 明确前 K 轮即使升级也计入账单 | 可靠性 scorer、测试 verifier、工具、fallback、strong restart、顺序等待与 tail 的统一分解 |
| Cache、切换与 replay | TwinRouterBench；HyDRA；vLLM SAAR；OpenSquilla | Twin 区分 `fresh input + cache_read + cache_write + output`；其他系统采用 sticky、hard lock、penalty 或物理调用账本 | matched stay/switch 的真实 re-prefill、queue、网络、provider-private state 丢失、行为 handoff 与失败风险 |
| 任务时间与等待 | TRACE-Router；Hera；Harness-Native；Aragog | TRACE 报含工具/环境的平均任务 wall-clock；Hera 报平均 E2E 轨迹时间；Harness-Native 仅在 ensemble 实验中给部分 p50/p95；Aragog 报负载下 E2E P25/P50/P95 | 固定 Agent workflow 上、外部 verifier 支撑且处理失败删失的 time-to-success，以及 Router/tool/retry/recovery/queue/switch 的闭合时间账本 |

### 11.1 逐项口径约束

- **FrugalGPT** 已把停止前所有 cascade API 调用的 prompt、generation 与固定请求费相加；不能再把“cascade”作为第二份 token 账单。未量化的是 DistilBERT scorer、离线结果矩阵/搜索，以及顺序调用的 latency/tail。
- **Unified Routing and Cascading** 定义 cascade supermodel 成本为所有已调用模型成本之和。11 模型下约 `9.53–15.26 ms` 是给定质量/成本估计后的决策搜索时间，不是包含模型生成、测试 verifier 和质量估计的端到端延迟。
- **RouteLLM** 的 `$3.32 / million requests` 和 `155.16 req/s` 是 matrix-factorization Router 的平均 serving 换算；不是单请求 p95，也不包含约 `$700` Judge 数据构建与最高 8×A100 的训练。
- **R²-Router** 主结果中的所谓 total cost 是被选 LLM 的 input + output inference cost，不是包含 Router、R²-Bench、Qwen3-80B Judge、profile、cache、retry 和 handoff 的系统总成本。
- **TRACE-Router** 的 wall-clock 包含工具执行和环境交互，但只给平均任务时间，不能表述为 cost/time per successful task，也没有 recovery/queue/cache 分解。
- **SWE-Router** 明确前 K 个 cheap-model turns 在升级分支中仍计费；strong model 从原问题重启，但 replay/cache/switch time 未单列。
- **TwinRouterBench** 的失败罚项是 benchmark 代理，不是真实 retry 支出；其四桶 token 计费也没有测量 cache miss 对 prefill、queue 和 tail 的时间影响。
- **Hera** 是“Agent Router 没有测过 Router overhead 或任务时间”的反例：论文实测约 `61 ms/step`，并报告 ALFWorld、WebShop、AppWorld 的平均端到端时间；但没有拆工具、失败恢复、queue、cache、能耗或 tail。
- **Harness-Native** 的 p50/p95 来自多模型/ensemble 表，不能归因给 singleton LightGBM Router；它适合说明“账单更低不必然完成更快”，不构成完整 time-to-success 账本。
- **vLLM SAAR** 的 prefix/handoff/switch-history 项多为规则或 lookup score；作者估算的 physical-model cost 不是外部 verifier 下的总任务成本。
- **DeepSeek Harness** 的固定提交是 provider-private state 不可等同于 KV miss 的直接代码证据：跨 adapter 时 core 剥离 `replayState`；同 adapter 跨模型/跨 provider 只交给 adapter 验证，不能保证可迁移；换 provider/model 还会进入不同 cache domain。[Fixed code](https://github.com/deepseek-ai/deepseek-harness/tree/47f943859bef60e4160492346772ded9b24f765a) · [Local audit](../../research_notes/B_harness_systems.md).

### 11.2 等待机制的邻近系统证据

这些工作不是完整模型 Agent Router 的直接 baseline，但能说明为什么等待与切换开销不能被设为零：

- **Aragog** — [Paper](https://arxiv.org/abs/2511.20975). 在固定 DAG stage 中按 runtime load/queue 选择 accuracy-preserving 配置，报告 E2E P25/P50/P95。
- **Preble** — ICLR 2025. [Proceedings](https://proceedings.iclr.cc/paper_files/paper/2025/hash/5bc342f48de8264779952fac378f96dc-Abstract-Conference.html). 直接研究 prefix KV reuse 与 load balance 的冲突，并报告平均和 p99 request latency。
- **DistServe** — OSDI 2024. [USENIX](https://www.usenix.org/conference/osdi24/presentation/zhong-yinmin). 将 prefill 与 decode 分离，以 TTFT/TPOT SLO 和 goodput 评估，说明单一“request latency”会掩盖不同等待来源。
- **Agentix: An Efficient Serving Engine for LLM Agents as General Programs** — NSDI 2026 prepublication；其较早 arXiv 版本名为 Autellix. [USENIX prepublication](https://www.usenix.org/system/files/conference/nsdi26/nsdi26spring_luo_prepub.pdf) · [arXiv](https://arxiv.org/abs/2502.13965). 研究 Agent program 调度、call/program waiting、head-of-line blocking 与 KV locality；属于调度系统，不是模型能力 Router。

完整时间成本审计见 [`../../research_notes/D_latency_academic_audit.md`](../../research_notes/D_latency_academic_audit.md) 和 [`../../research_notes/E_latency_commercial_audit.md`](../../research_notes/E_latency_commercial_audit.md)。

### 11.3 本页最终判断

在本次核验范围内，尚未发现固定 Agent workflow 上的完整模型 Router，同时闭合 Router、工具、失败恢复、queue/tail、跨模型 cache/replay/handoff，并以外部 verifier 支撑的 cost/time per successful task 统一报告。因此可讨论的贡献不是“首次考虑 latency/cache”，而是在同一 harness 协议下建立 event-level physical-attempt ledger，并把价格与 time-to-success 对齐到成功任务。

计量时每个物理调用只记一次：cascade、retry 和 recovery 是触发原因或阶段标签；其新发生的模型/工具调用进入相应执行桶，等待进入 wall-clock span。远端 provider queue 不可观测时记为 `unknown`，不能记为 `0`。
