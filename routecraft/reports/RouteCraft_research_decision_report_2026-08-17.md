# RouteCraft 科研决策报告

**主题：** Agent 中的完整模型 Router：模型选择与自适应重新决策边界  
**证据截止：** 2026-08-17（Asia/Shanghai）  
**研究对象：** 多个完整 LLM 之间、固定 Agent workflow 内的在线选择；不含 MoE token-to-expert routing  
**决策：** **Revise（有条件继续）**

## 决策摘要（不超过 800 字）

**结论：Revise。** task pinning、固定 K escalation、per-turn/call、harness-state、milestone workflow 及“下一模型+停止/继续”均已有先例，不能宣称首个 stage-level 或 harness-native Router。尚未核验到一项工作同时做到：固定原 workflow；联合选择完整模型与下一可验证重决策事件；用 same-state model×boundary fork 监督；并计入 Router、cache/replay、handoff、重试和 tail latency。问题应收窄为：**可验证事件上的自适应模型承诺，是否比最佳固定粒度产生可重复净收益？**

最大风险是策略坍缩为 `next_call`/`task_terminal`，或固定边界已获得几乎全部 Oracle 收益。MemoryCraft 说明 Agent loop、上下文重读和恢复会改写排序，但它不是 Router。更多信息只保证零开销 Oracle 不劣；cache loss、deliberation 和 handoff 可使 per-call 更差。先做一周 Phase 0：约 120 任务、240–300 状态、2 模型×4 边界、世界快照和确定性 verifier。若固定边界捕获 ≥90–95% 可恢复净增益，且 adaptive 增量 95% CI 上界同时 <2pp success、<5% CPS，则停止；若扣全成本后相对 task pinning 仍有约 ≥3pp 或 ≥10% CPS 空间，且 PlanIR+LightGBM 可预测反转，再进入 Phase 1。首稿避免复杂 RL 和强 LLM Router，优先做 benchmark、测量和轻量 scorer。

## 1. 决策口径、证据等级与概念边界

### 1.1 本报告的三种陈述

- **论文事实：** 仅由论文原文、官方项目页、会议页面、官方仓库或固定 commit 支持；作者自报结果只在其评测条件下陈述。
- **本报告推断：** 由多项证据推导，明确标为“推断”，不冒充论文结论或因果事实。
- **候选假设：** RouteCraft 尚待实验验证的主张，不因相关工作不足而自动成立。

核验标签：`VERIFIED` 表示标题/作者/状态/方法可由一手资料核验；`AUTHOR-REPORTED` 表示数值来自作者实验；`PARTIAL` 表示只能核验部分字段；`UNVERIFIED` 表示截至截止日未找到足够一手证据。检索优先级为正式会议页/ACL Anthology/OpenReview/PMLR、arXiv 原文、官方代码与系统文档；搜索结果页和二手报道不支撑关键结论。

### 1.2 纳入与排除

核心对象是“从多个**完整模型**中选择当前或后续 Agent LLM 调用所用模型”。决策粒度分为：

1. prompt/query 一次选择；
2. task/session model pinning；
3. 固定 K 轮或失败后 escalation/fallback；
4. 每 turn 或每 LLM call 重新路由；
5. tool observation 后重路由；
6. semantic stage 或 externally verified milestone 后重路由；
7. 重新生成 workflow 并给节点分配模型；
8. 联合选择模型与下一次重新决策边界。

MoE expert routing、tool/RAG/memory router、multi-agent role selection、workflow generation、speculative decoding、token early exit 和 dynamic layer skipping 不作为同类工作；只有其 temporal option、termination policy、state abstraction 或 deliberation-cost 理论可作为邻近依据。

### 1.3 对 MemoryCraft 的完整阅读结论

本地未发表的 MemoryCraft 原稿（公开版未收录）共 19 页，已逐页阅读、全文抽取并视觉核对；SHA-256 为 `82F96BF1B9E86AC206B31DE4DF50744B1B69230DBCD3B169A51A5D9B8A3D2289`。其方法学价值是：

- 固定执行协议，替换 memory backend、framework、backbone 与 control locus；
- 明确区分 harness-issued 与 agent-issued；
- 逐模型调用记录 cache miss/read、output、turn、retrieval/tool、latency、truncation、long-context tier 与 usage availability；
- Agent loop 可改变系统排序：同一 memory 系统在 harness-issued 与 agent-issued 下的排序不同；
- agent-issued 的主要成本可来自额外轮次、resident context 反复读取和失败恢复，而非 output token 或单次模型标价；
- 使用共同完成实例交集、same-framework/no-history 基线扣除与 tool-call validity gate。

它**不是 Router 系统或已发表 benchmark**：稿件含 PVLDB/DOI、artifact URL、部分 host/许可证/数值占位；未建模 Router、Judge、fallback、retry、跨模型 cache/replay、provider-private state、模型加载/队列或 handoff 行为不一致；部分 accuracy 与 cost 还不是同一完整样本。故本报告只把它作为固定协议、调用级计量和 loop-aware 排名的起点。更细审计见 [MemoryCraft 方法学笔记](../research_notes/00_memorycraft_methodology.md)。

## 2. 相关工作分类体系与总体结论

### 2.1 八类路线

| 类别 | 典型动作 | 信息使用 | 任务内切换 | 核心优势 | 固有盲区 |
|---|---|---|---:|---|---|
| Prompt/query router | 选一个模型处理查询 | prompt、模型 profile | 否 | 开销低、易部署 | 看不到工具反馈和失败 |
| Task/session pinning | admission 时选模型并固定 | 初始任务/少量上下文 | 否 | cache/一致性好 | 无法响应 capability-demand drift |
| Cascade/escalation | cheap-first，固定 K 或失败升级 | 部分轨迹/置信度 | 有限 | 易解释、控制成本 | 重决策时点多为固定超参 |
| Per-turn/per-call | 每轮选下一模型 | 历史、当前 call | 是 | 信息利用最大 | Router、cache 与 handoff 开销最高 |
| Observation-triggered | 工具/环境返回后再选 | 新外部证据 | 是 | 在高信息增益处决策 | harness 事件语义和快照要求高 |
| Stage/milestone | 阶段或子目标完成时选 | plan/progress/verifier | 是 | 稀疏决策、语义清晰 | milestone 常不可观测或被 LLM 猜测 |
| Workflow generation | 重构图/节点并分配模型 | 全局任务与搜索轨迹 | 是 | 联合优化强 | 改变工作流，不能隔离 Router 贡献 |
| Adaptive commitment | 选模型及下次开放路由边界 | 状态、模型、边界与切换成本 | 是 | 把粒度作为决策变量 | 可能退化到固定端点；数据昂贵 |

### 2.2 对“粒度是否通常是固定超参数”的判断

**论文事实：** TRACE-Router 固定为 task-level pinning；SWE-Router 用 cheap prefix 后一次 escalation；MTRouter、Budget-Aware Agentic Routing、TwinRouterBench 的动态设定把决策机会固定在 turn/step/call；EASy 的 milestone 来自其自生成 workflow；Iterative Critique-and-Routing Controller 每轮做 stop/continue 与下一 agent，但改变了 refinement workflow。对应一手来源包括 [TRACE-Router](https://arxiv.org/abs/2607.22465)、[SWE-Router](https://arxiv.org/abs/2607.00053)、[MTRouter](https://aclanthology.org/2026.acl-long.2045/)、[Budget-Aware Agentic Routing](https://arxiv.org/abs/2602.21227)、[TwinRouterBench](https://arxiv.org/abs/2605.18859)、[EASy](https://arxiv.org/abs/2608.04588) 和 [Iterative Critique-and-Routing Controller](https://arxiv.org/abs/2605.08686)。

**本报告推断：** 现有完整模型 Agent routing 通常把“什么时候允许再次路由”当作系统设计或固定调度粒度，而不是与模型共同输出的动作变量；但这只是截至截止日的检索结论，不能写成“首个”声明。RouteCraft 的可辩护差异必须同时依赖固定 workflow、event predicate、真实 switch/cache accounting 和 matched fork，而不能只依赖“stage-aware”措辞。

### 2.3 主要工作完整总表

包含作者、发表状态、论文/代码、路由对象、粒度、任务内切换、输入/历史/阶段、Router/标签/Judge、未见模型、workflow、成本覆盖、benchmark、作者结果、局限和重叠度的逐项矩阵见 [related_work_matrix.csv](../evidence/related_work_matrix.csv)。下列结论最影响决策：

- [MTRouter](https://aclanthology.org/2026.acl-long.2045/) 已覆盖全历史、逐 turn 完整模型选择；
- [TwinRouterBench](https://arxiv.org/abs/2605.18859) 已覆盖 step-level prefix、common continuation、cache 四桶和 live API spend；
- [Harness-Native Data Flywheel](https://arxiv.org/abs/2607.11399) 已覆盖丰富 harness state、recovery/verification、realized cost 和数据 flywheel；
- [HyDRA](https://arxiv.org/abs/2605.17106) 已覆盖 production sticky session 与 compaction/background-summary 固定事件重路由；
- [Iterative Critique-and-Routing Controller](https://arxiv.org/abs/2605.08686) 已联合输出下一模型和 `stop/continue`，虽然 stop 是结束专用 refinement workflow；
- [Aragog](https://arxiv.org/abs/2511.20975) 说明固定 DAG stage 上的 load-aware model assignment 也不是空白。

“SCOPE”在检索中存在标题歧义：本表按指定基础 Router 解释为 [Models Under SCOPE](https://arxiv.org/abs/2601.22323)；另有截止日前刚出现的 VLM/open-set 工作 *SCOPE-Router*，不应把两者混成一篇，其对 Agent commitment 的直接相关性较低。

## 3. Agent 阶段、信息增益与推荐路由粒度

“阶段”不是天然标签。优先级应是：harness 原生事件 > 可由规则确定的状态 > 小模型推断的语义状态 > 强 LLM 的不可验证猜测。没有显式 plan 或 milestone 的 Agent 不应被强行赋予看似精确的阶段。

| 阶段 | 通常含 LLM 调用 | 新信息 | 能改变最佳模型吗 | 外部可验证边界 | 错误可逆性 | 切换风险 | 推荐粒度 |
|---|---|---|---|---|---|---|---|
| OBSERVE | 否；视觉/摘要型 Agent 可有 | 工具结果、页面、DB/环境状态、用户增量 | **高**；需求和难度可突变 | 通常高：event、HTTP/exit code、state diff | 多数可逆 | 低到中；应保留原始 observation | 在 observation 后重路由；随后 stage pin |
| PLAN | 常有 | 主要是模型派生的分解、约束与假设 | 中；但常不是外部新证据 | 低到中；显式 plan 可检查但不等于正确 | 高 | 中到高；跨模型会破坏 plan ownership/术语一致性 | 默认 pin 至 next observation；仅 plan verifier 失败时重开 |
| RETRIEVE | query 生成/摘要可能有 | 检索文档、schema、memory 命中与空结果 | **高**，尤其长上下文/领域能力需求 | 中到高：检索完成、命中数、文档 ID | 高 | 中；摘要切换会丢失选择依据 | 在 retrieval result 后重路由 |
| ACT | 常有，用于 tool call/code/action | action proposal 本身多为派生；执行后才有外部信息 | 执行前中等；高风险动作可需要强模型 | action issued 可观测，但正确性通常未定 | 从可逆到不可逆 | **高**；模型交接易改变参数/约束 | 高风险动作前按规则升级；承诺到 next observation |
| VERIFY | 可由测试/规则完成，也可有 LLM judge | 测试、diff、约束检查、DB predicate、环境 reward | **很高**；失败类型驱动 escalation | 确定性 verifier 时最高 | 多数可恢复 | 低；若只换验证者需防标准漂移 | verifier 结果后重路由；机器验证优先 |
| RECOVER | 常有 | error class、retry count、失败上下文、回滚结果 | **很高**；出现 capability-demand drift | error/timeout/rollback event 高 | 视环境而定 | 中；新模型需理解失败历史 | 失败触发提前中断承诺；强度可升级至 verified recovery |
| ANSWER/TERMINATE | 常有 | 一般没有新外部信息；可能有最终汇总约束 | 低到中；长上下文/写作能力可能不同 | terminal/verifier 可观测 | 回答前可逆、提交后低 | 中；切换会导致语气/结论不一致 | 最终阶段 pin；只有终检失败才重开 |

关键点：真正高价值的重新决策机会通常不是“每一个 LLM call”，而是**外部世界改变、检索结果到达、确定性验证失败、错误/超时发生或预算/上下文阈值跨越**。纯粹的内部 reasoning call 只增加了相关状态，不保证增加可行动的新信息。阶段前后的推荐动作还受不可逆性约束：不可逆 ACT 前可以升级，但执行中不应为了追求粒度而切换。

### 3.1 四类状态来源

| 来源 | 例子 | 可信度 | Router 使用原则 |
|---|---|---:|---|
| Harness 原生 | request、tool result、error、retry、token/cache、model、budget | 高 | 直接编译，保留 event ID 和来源 |
| 规则确定 | exit code→failure class；test pass→verified；context threshold | 高到中 | 版本化规则并记录未知/冲突 |
| 小模型语义推断 | subgoal、粗 capability demand、文档类型 | 中 | 输出概率/置信度；用真实 outcome 校准 |
| 强 LLM 猜测 | 细粒度 progress、隐含 milestone、剩余义务 | 低到中 | 只做离线候选标签；需外部对齐或弃用 |

## 4. 完整系统成本模型

用户给出的扩展式方向正确，但应修正三点：离线成本需要摊销；switch 与 context replay 要避免和 input/cache token 双计；“失败任务”也必须进入分子。令任务集为 \(i=1,\ldots,N\)，调用/事件为 \(t\)，建议使用：

\[
C_{i,t}^{\mathrm{direct}}
=C_{\mathrm{model}}+C_{\mathrm{tool}}+C_{\mathrm{retry/recovery}},
\]

\[
C_{i,t}^{\mathrm{control}}
=C_{\mathrm{router}}+C_{\mathrm{judge}}+C_{\mathrm{switch}}+C_{\mathrm{replay}},
\]

\[
C_{i,t}^{\mathrm{infra}}
=C_{\mathrm{queue/network}}+C_{\mathrm{energy}},
\]

\[
C_{\mathrm{task},i}
=C_{\mathrm{ingest},i}+C_{\mathrm{profile/train},i}^{\mathrm{amortized}}
+\sum_t\left(C_{i,t}^{\mathrm{direct}}+C_{i,t}^{\mathrm{control}}+C_{i,t}^{\mathrm{infra}}\right).
\]

\[
\mathrm{CPS}
=\frac{\sum_i C_{\mathrm{task},i}}
{\sum_i \mathbf{1}[\mathrm{success}_i]}.
\]

这里的 cost per successful task 是**所有分配任务（含失败）的总成本/成功数**，不是 \(E[C\mid success]\)；后者会遗漏失败消耗并产生 survivor bias。若一个平台只提供 token 账单，则能源和本地推理时间单列，不能伪装成已包含的美元成本。

### 4.1 成本分类与计量字段

| 大类 | 必须计量 | 常见双计/遗漏 | 建议记录 |
|---|---|---|---|
| 直接推理 | cache-miss input、cache-read、cache-write、output、reasoning、本地时长/能耗 | reasoning token 有时已计入 output；cache write 计价因 provider 异 | provider、model、tariff version、token class、GPU-ms/J |
| Router | CPU/GPU/token、序列化、特征编译、LLM router、在线更新 | 只报模型调用而忽略 Router；把离线 profile 当免费 | router wall/CPU/GPU-ms、token、profile/train amortization |
| Judge/verifier | LLM judge、reward model、测试、容器、DB 检查 | Judge 既作标签又作在线决策但未计费 | judge kind、tokens、runtime、determinism |
| Agent 间接 | tool、额外 turn、无效 reasoning、retry、fallback、recovery、ensemble | 只比较成功调用；失败分支被删 | attempt ID、failure type、recovery chain、tool cost |
| 切换 | KV/prefix cache loss、private replay state、重编码、模型加载/驻留、queue/batch、网络、handoff inconsistency | replay token 又记作 switch 美元；不记 tail latency | from/to model、cache lineage、load/queue/network、replay bytes/tokens |

模型成本可写为 \(p_{miss}T_{miss}+p_{read}T_{read}+p_{write}T_{write}+p_{out}T_{out}+p_{reason}T_{reason}\)，但若 provider 的 reasoning 已包含在 output 中，最后一项只做分析字段而不再计费。切换的美元成本只计上述 token 账单以外的资源；被重新编码的 token 归入 replay/cached-input，同时保留 switch attribution 标签。

### 4.2 核心指标

主指标：task success、CPS、quality–cost Pareto/AUC。必须并列报告 p50/p95 latency、能源、失败恢复成本、Router overhead、switches/task、cache read/write/loss、retry/fallback、under-routing recall、ECE/Brier 和失败类型。价格比较固定 tariff snapshot；负载实验固定或记录 queue/load distribution。

### 4.3 现有论文成本结论的可解释边界

初步核验显示，FrugalGPT、RouteLLM、SWE-Router、MTRouter、HyDRA 等主要以模型调用价格、估算 token 成本或其 benchmark 费用为中心；TRACE-Router显式将 latency 纳入 terminal reward；TwinRouterBench 的动态设置记录 realized API spend 并锁定 pricing/cache rule；MemoryCraft 对 cache/turn/retrieval 的计量比多数 router 论文细，但不含 Router 与跨模型切换。**没有足够证据把任何作者报告的“节省”直接解释成完整 CPS 节省**，除非其评测同时计入 Router、Judge、失败重试、cache loss、replay、queue 和 handoff。逐论文字段在完整矩阵中标为 `计入 / 部分 / 未计入 / 未报告`，不能把“未报告”写成“成本为零”。

## 5. RouteCraft：形式化、差异与新颖性

### 5.1 Event-driven SMDP / temporally extended option 表述

在 harness event 时刻 \(\tau_k\) 观测状态 \(S_k\)，动作 \(a_k=(m_k,\beta_k)\) 选择完整模型和终止谓词。原 harness 继续运行；在 \(\beta_k\) 首次为真、terminal、明确失败、超时或安全中断时，下一决策时刻为 \(\tau_{k+1}\)。持续时间 \(\Delta_k=\tau_{k+1}-\tau_k\) 及期间调用数随机，回报聚合成功增量与全部成本，因而是 event-driven semi-Markov process。

它也可表为 option \(o=(I,\pi_m,\beta)\)：initiation set \(I\) 是允许路由的事件状态；intra-option policy \(\pi_m\) 不重新规划，而是让原 harness 在承诺期内将 LLM 请求交给模型 \(m\)；termination \(\beta\) 是 `next_call / next_observation / verified_milestone / task_terminal` 之一或带安全中断的谓词。若谓词确定，则是 deterministic termination option；若 PlanIR 非 Markov，则严格说是 POMDP/approximate SMDP representation，而不是完整充分状态。

### 5.2 与最相近路线的逐项差异

| 相近路线 | 共同点 | 关键差异 | 能否直接 baseline |
|---|---|---|---|
| TRACE-Router | 完整模型、Agent terminal reward | admission 后整任务 pin；不学习任务内 termination | 是，task-level |
| SWE-Router | cheap-first、部分轨迹后 escalation | 主要是固定探索前缀/一次升级；不是通用四边界承诺 | 是，fixed-K escalation |
| MTRouter | 多轮历史、每轮模型选择、terminal outcome estimator | 重决策机会固定为 turn；不把边界作为候选动作 | 是，history/per-turn |
| TwinRouterBench | per-call concrete model、静态/动态 benchmark、真实 API spend | 评测重心是每步选模型；边界不是联合动作 | 是，per-call 与 oracle |
| Agentic Routing flywheel | harness-native full state、step-level model/ensemble、LightGBM | 仍是 step-level；可改变为 ensemble，数据 flywheel 范围更广 | 是，去掉 ensemble 后 |
| Budget-Aware Agentic Routing | per-step cheap/expensive、预算约束、RL | 边界固定为 step；主要学模型动作 | 是，但首稿不复现复杂 RL 可用作者结果讨论 |
| EASy | milestone、模型/执行器分配、成本优化 | 自己分解并生成 workflow、并行执行；改变 planner/executor | 否，邻近上界/边界讨论 |
| GraphPlanner | 图工作流、不同节点选模型/角色 | 生成/检索 workflow 并联合角色；非固定 Agent | 否，邻近工作 |
| Iterative Critique Controller | stop/continue + 下一 agent，MDP | 控制 critique/refinement workflow，路由对象含 agent，不是固定 harness 的模型承诺 | 否或仅概念对照 |
| vLLM session-aware routing | session continuity、stay/switch 与 serving state | 更偏 serving/policy 规则；未证实学习 model×event-boundary | 是，系统规则 baseline |
| 传统 task pinning | \(\beta=task\_terminal\) | RouteCraft 允许其他可验证事件并显式定价切换 | 是 |
| MoE temporal option | 持续选择、termination 理论 | 选择模型内部 expert/token block，共享执行与 KV；不是完整模型跨 provider handoff | 否，只作理论参考 |

### 5.3 新颖性判断

**不能主张：** 首个 Agent Router、首个 stage-level router、首个 harness-native router、首个在多轮历史上路由、首个学习停止/继续、首个 milestone-aware 系统。

**可谨慎主张并需 Phase 0 证实：** 在不改变 Agent workflow 的前提下，把完整模型与下一次可验证重新决策事件联合为 action；使用 same-state model×boundary forks 估计相对固定 continuation policy 的局部效果；显式以 cache/replay/handoff/retry-adjusted CPS 优化承诺时长。检索未发现完全同构工作只能支持“据我们核验，尚未发现”，不能支持绝对首创。

最终应把题目收窄为：**When do externally verifiable Agent events justify paying to reopen full-model routing?** “Plan-state distillation”是实现手段而非首要 novelty；否则题目同时承诺 benchmark、因果数据、表示学习、routing、options/RL 和系统实现，过宽。

## 6. PlanIR 与 routing-sufficient plan-state distillation

### 6.0 轨迹/计划蒸馏的一手证据

| 工作 | 学习材料 | 对 RouteCraft 的正证据 | 负证据/边界 |
|---|---|---|---|
| [FireAct](https://arxiv.org/abs/2310.05915) | GPT-4 成功轨迹、不同 agent prompting | 成功轨迹可把 agent 行为蒸馏进较小模型 | success-only 有幸存者偏差；不同 base LM 可受益或受损 |
| [ToolLLM/ToolBench](https://openreview.net/forum?id=dHng2O0Jjr) | API/搜索树/回退路径 | 工具树提供候选未来与执行监督 | 主训练偏成功路径；ToolEval 依赖 ChatGPT Judge |
| [ToolPreference](https://proceedings.neurips.cc/paper_files/paper/2024/file/c0f7ee1901fef1da4dae2b88dfd43195-Paper-Conference.pdf) | 同 history 的成功/失败 branch preference | 支持 matched-history pairwise ranking | “最终成功路径 child”含 hindsight，不能放进在线特征 |
| [ETO](https://aclanthology.org/2024.acl-long.409/) | 探索得到成功/失败 trajectory pair | 失败轨迹和环境 reward 有用 | 其 step-wise terminal-reward label 极不稳定，直接反驳粗暴局部归因 |
| [MAGDi](https://proceedings.mlr.press/v235/chen24ah.html) | 多教师讨论图 | 结构化多教师信息可压缩 | 目标是单 student 行为，不是运行期 Router |
| [Agentic Plan Caching](https://proceedings.neurips.cc/paper_files/paper/2025/hash/9549f7d06700f0966d5f938f1d11022a-Abstract-Conference.html) | 成功 plan template cache | 紧凑 plan template 可比全文历史便宜且有时更准 | 改变 planner path、success-only；代码未核验 |
| [AgentRefine](https://openreview.net/forum?id=FDimWzmcWn) | 合成错误和 recovery | 支持把错误/恢复纳入数据 | synthetic DM 自洽不等于真实环境；仓库为部分开源 |
| [Exploring Expert Failures](https://arxiv.org/abs/2504.13145) | 从失败中间状态重新 rollout | 失败轨迹的可恢复后缀可成为正数据 | 价值依赖 snapshot+重新执行，不是教师解释 |
| [ProAct](https://arxiv.org/abs/2602.05327) | 环境 MCTS/search tree→压缩 reasoning | 搜索树能生成 counterfactual coverage | 压缩文本看过未来；随机 rollout 在 sparse reward 下可稀释信号 |
| [AgentArk](https://arxiv.org/abs/2602.03955) | 多 agent debate/self-correction | 多教师纠错可蒸馏 | 教师数/数据量与 OOD 收益非单调 |
| [ClawTrace/CostCraft](https://arxiv.org/abs/2604.23853) | hook trace→1.2–1.8kB TraceCard/skill patch | 与“事实 compiler+小 IR+cache 四桶”最接近 | 单 harness/model；跨 benchmark rules 使三项质量均回退，84-task aggregate 无成本节省 |

因此，轨迹压缩与失败数据提供**实验动机**，不提供 PlanIR 充分性的结论。完整证据卡、代码状态、理论与 PDF 哈希见 [C_theory_trajectory.md](../research_notes/C_theory_trajectory.md)。

### 6.1 与 CoT 蒸馏的区别

CoT 蒸馏尝试复制教师的生成推理过程或最终行为；PlanIR 的目标是压缩**路由决策所需的可观测状态**，不要求重现隐藏思维、完整 plan 或自然语言 rationale。其标签应是 pre-decision 时刻可知的事实或可外部对齐的结构化变量；真正监督信号来自后续 model×boundary 执行 outcome，而不是“教师说哪个模型更强”。因此 PlanIR 是状态表示/充分性问题，不是把教师 rationale 当真值。

### 6.2 建议字段分层

| 层 | 字段 | 必要性 | 风险与处理 |
|---|---|---:|---|
| 确定性核心 | event/stage source、tool/test result、error class、retry、budget、context tokens、cache state、current model、provider/adapter | 高 | 由 State Compiler 生成，保留原 event 指针 |
| 安全/执行核心 | reversibility、deadline、irreversible-action flag、world-snapshot capability | 高 | 尽量规则化；未知时保守处理 |
| 证据核心 | evidence IDs、verifier status、unmet machine-checkable predicates | 高 | 只包含决策前证据，严禁后验结果 |
| 语义可选 | current subgoal、remaining obligations、capability demand | 中 | 教师生成但必须带来源、置信度和可对齐 predicate；允许 `unknown` |
| 高风险 | scalar progress、自由文本 stopping condition、隐含“难度” | 低 | 容易主观、泄漏 gold plan/未来结果；Phase 0 默认移除 |

原 schema 中 `stage_type`、`last_error`、`retry_count`、`remaining_budget`、`context_tokens`、`cache_state`、`current_model` 应保留；`reversibility` 应改成事实来源+三值 `recoverable/irreversible/unknown`；`progress` 不应作为无来源的连续真值；`required_capabilities` 只能作为带不确定度的预测，不是教师权威标签；`remaining_obligations` 若来自 gold solution、隐藏测试或未来成功轨迹会造成严重标签泄漏。

### 6.3 RouteCard 构造规则

两层构造合理，但应给每个语义字段增加：`source_event_ids`、`teacher_confidence`、`alignment_predicate`、`alignment_result`、`abstain_reason` 与 `compiler_version`。工具退出码、测试、DB 状态、环境 predicate 或可复演 state diff 对不上的字段，不进入高可信训练集。失败和恢复轨迹必须包含：它们覆盖正常成功轨迹缺少的 error/retry/capability-drift 区域，也是学习“何时提前终止承诺”的主要信号；但需按 failure type 和 policy 分层，避免把某模型特有错误当成普遍状态需求。

### 6.4 是否比 raw trajectory 更便宜、更跨 harness

**候选假设而非既定事实：** PlanIR 可减少上下文 token、Router latency 与 provider-specific transcript 差异，并把不同 harness 映射到相同 event/predicate；但过度压缩会丢失代码、网页、工具参数和错误细节。跨 harness 泛化必须在第二个 adapter 上零样本/少样本测试，不能由 schema 相似性推断。

验证可写为经验充分性：令原历史为 \(H\)、PlanIR 为 \(Z=g(H)\)、候选及边界为 \(A\)、outcome vector 为 \(Y\)。理想充分性满足 \(Y\perp H\mid(Z,A)\)，或 \(I(Y;H\mid Z,A)=0\)。实践中不能证明为零，应用三项检验：

1. raw history 在 PlanIR scorer 之上不再显著改善 held-out task/model 的 regret、Brier、cost/latency pinball loss；
2. 相同 \(Z,A\) 的 outcome 分布稳定，representation collisions 不集中在模型反转状态；
3. 在约束 regret/calibration 不劣的前提下最小化 \(I(Z;H)\) 或表示大小，形成 information-bottleneck trade-off 曲线。

不要称 PlanIR 为“充分统计量”，除非对指定任务分布、action set 和 outcome 明确给出经验等价界；更稳妥的术语是 **routing-sufficient empirical representation**。

一个可预注册的操作性门槛是：相对 raw history，PlanIR 的 success 差距不超过 1–2pp、normalized oracle-gain recovery 差距不超过 5%，同时 Router 输入 token 或 latency 至少下降 30%；且在 PlanIR 上追加 raw embedding 不再显著改善 cross-fitted Brier/NLL/regret。该门槛只对本 benchmark 有效，不是普遍统计充分性证明。

## 7. Candidate-conditioned Router

建议 scorer：

\[
f_\theta(z_t,d_m,\beta)\rightarrow
(\hat p_{success},\hat C,\hat q_{50/95}(L),\hat R_{failure}).
\]

分别预测成功、成本、延迟分位数和失败类型，比单一 utility 更适合：成功有约束、价格/负载/\(\lambda\) 会变、tail latency 非均值、各头可单独校准。最终决策仍可组合为

\[
(m^*,\beta^*)=\arg\min_{m,\beta}
\hat C+\lambda\hat q_{95}(L)+\gamma\hat C_{switch}
\quad\mathrm{s.t.}\quad LCB(\hat p_{success})\ge\tau.
\]

但分头不应假定相互独立；在 Pareto/风险决策中用 matched outcome 的联合 bootstrap、copula 或多任务共享干表示保留相关性。

### 7.1 未见模型与 calibration probes

Candidate-conditioned 只有在 profile 覆盖真正影响 outcome 的交互、训练时阻断 model-ID shortcut、且新模型 profile 与训练支持域重叠时才支持未见模型。profile 必须来自执行 probe：能力维度、tool reliability、context/window、价格与 latency 分布、cache/replay compatibility、部署/隐私/availability；厂商自述只可作元数据。

不存在普适的最小 probe 数。MVP 建议以 50–100 个分层状态做排序冷启动，以 200–500 个执行样本做粗 success calibration，然后用 Beta-binomial/Wilson 区间或序贯停止：当关键能力 strata 的 success CI 半宽和 pairwise rank uncertainty 达到预设阈值才停止。低基率成功、长尾工具错误或多任务族需要更多样本。报告样本效率曲线，而不是宣称固定数量即可支持任意新模型。

数量级依据：对单一 Bernoulli rate，最坏 \(p=0.5\) 的 95% 正态近似中，约 \(n=97\) 才有 ±10pp 半宽，\(n=385\) 才有 ±5pp；分层、多失败类型和 p95 latency 通常要求更多。因此“几十个 probe 支持任意新模型”不可成立，50–100 只能作粗排序，不能作精确 LCB。

### 7.2 模型复杂度决策

- Logistic：PlanIR 特征低维、关系近线性，作为透明下界。
- LightGBM：结构化字段、缺失值、非线性交互、数百至数万 fork，建议为主模型。
- kNN：反事实 outcome bank 密、需要局部可解释相似状态时有效；高维稀疏区会退化。
- 小 encoder：raw snippets/错误文本仍有增益、但无需生成时。
- 0.5B–1.5B Router：只有 raw long trajectory 的语义增益在 held-out task/harness 上显著超过 PlanIR+LightGBM，且推理成本/延迟低于节省预算时才合理。
- 强 LLM-as-a-Router：作为 accuracy ceiling；在线 token、cache、Judge 与延迟全计入。短任务中它很可能吃掉节省。

第一篇论文不应直接采用复杂 RL。先做 matched supervised learning/offline evaluation；只有在部署后存在安全、可记录的部分反馈与 load/price drift 时考虑 contextual bandit；只有当路由显著改变未来状态分布、轨迹覆盖充分且 reward 可审计时才考虑 offline RL。

### 7.3 推荐训练目标和标签

\[
\mathcal L=\alpha_s\mathcal L_{BCE/Brier}
+\alpha_r\mathcal L_{pairwise}
+\alpha_c\mathcal L_{cost}
+\alpha_l\mathcal L_{quantile}
+\alpha_f\mathcal L_{failure}
+\alpha_a\mathcal L_{capability}
+\alpha_{cal}\mathcal L_{calibration}.
\]

| 目标 | 损失 | 标签来源 | 备注 |
|---|---|---|---|
| success | BCE + Brier/可选 focal | fork 终端测试、DB/environment reward | 不用 LLM rationale 当标签 |
| pairwise ranking | logistic/Bradley–Terry | 同一 state 下 action 的净 utility 或 constrained dominance | ties 和随机 CI 显式建模 |
| cost | Huber/Log-normal NLL | 完整调用、tool、retry、switch、replay 账单 | 训练/报告 tariff 版本 |
| latency | pinball q50/q95 | 端到端 wall time，含 queue/tool/router | 按负载 strata 建模 |
| failure risk/type | BCE/CE | verifier、exception、timeout、invalid tool、unsafe | 允许多标签链 |
| capability auxiliary | BCE/ranking | 独立实测 probes + 执行对齐 RouteCard | 不用厂商宣称或教师主观评分 |
| calibration | Brier、temperature/isotonic、conformal/LCB | held-out matched outcomes | calibration split 不参与模型选择 |

## 8. 三个可检验的核心假设

1. **H1—净反转存在：** 在可恢复中间状态中，存在足够比例的 model 或 boundary 排名反转，且扣除 Router/cache/replay/switch/retry 后，动态 Oracle 仍显著优于最佳 task pinning 和最佳单一固定边界。
2. **H2—信息集中于可验证事件：** observation、deterministic verification failure、error/recovery 等事件比任意 next-call 提供更高 capability-demand drift/EVSI，使稀疏 event routing 达到大部分 per-call Oracle 收益而使用更少 Router 调用和切换。
3. **H3—PlanIR 可预测且可迁移：** deterministic-core PlanIR 加少量对齐语义字段能在 held-out task/harness 上预测 model×boundary outcome，降低 oracle regret，并以更低开销不劣于 raw trajectory embedding。

## 9. 理论命题、成立条件与反例

### 9.1 命题 A：更多中间信息不保证更低真实系统成本

令在信息集 \(\mathcal I\) 下，动作 \(m\) 的净任务效用（暂不含获取额外信息/路由/切换成本）为随机变量 \(U_m\)。得到额外信息 \(G\) 后，Blackwell/value-of-information 关系给出：

\[
\mathbb E\!\left[\max_m\mathbb E[U_m\mid\mathcal I,G]\mid\mathcal I\right]
\ge \max_m\mathbb E[U_m\mid\mathcal I].
\]

成立条件是：相同 action set；允许忽略 \(G\)；信息获取不改变环境；没有 Router/deliberation/switch/replay/handoff 成本；Oracle 知道真实条件分布。它只说明 gross Oracle value 不下降，不说明实际学习 Router 的 net CPS 下降。

加入开销 \(K(G,a)\) 后：

\[
V^{net}_{more}=\mathbb E[\max_m Q(\mathcal I,G,m)]-\mathbb E[K]
\]

可低于 \(V^{net}_{less}=\max_m Q(\mathcal I,m)\)。最简单反例：两个模型在所有状态下成功率和费用完全相同，额外信息价值为 0，而 Router 每次需 20 ms 或产生任意正成本，故严格变差。更贴近 Agent 的反例：强弱模型只有 1% 预期成本差，而跨 provider 切换使 prefix cache 失效并重编码 50k context tokens，gross gain 小于 replay cost；per-call routing 即使选择从不出错也更贵。若获取信息需要额外 LLM turn，它还会改变状态和失败概率，连上述单纯 VOI 不等式的“免费观测”条件都不再满足。

### 9.2 命题 B：仅当信息价值超过重新决策总代价时重路由

对当前模型 \(m_c\)，事件状态 \(S_t\) 的近似条件是：

\[
\mathrm{EVSI}_t=
\mathbb E[\max_m Q(S_t,m)-Q(S_t,m_c)]
>
C_{router}+C_{switch}+C_{context}+C_{handoff}.
\]

严格决策还需考虑失败约束、下一 boundary 的 duration 和未来 option value。左侧可由 same-state forks 的 action outcome vector、cross-fitted Q-model 或分层 Bayesian outcome model估计；用未独立的样本内 max 会产生 winner's curse，应以独立重复/交叉拟合和 bootstrap 校正动态 Oracle。

delayed terminal reward 使估计方差和 credit ambiguity 增大：同一局部模型选择可能通过未来状态与 continuation policy 交互。common continuation policy 固定后估计的是 \(Q^{\pi_0}(S,a)\) 的局部策略效果，而不是任意后续自适应策略的总效果。可用确定性中间 verifier/progress predicate 降方差，但不能把相关的 LLM judge 分数冒充因果中介。

capability-demand drift 更可能出现在工具 observation、检索返回、隐藏约束暴露、测试失败、timeout/error、回滚/恢复和 context/cache regime 跨阈值处；在连续格式化调用、无新证据的内部 plan 延展中更低。因此：

- 排名跨阶段高度稳定或切换贵：task pinning 最优；
- 信息以稀疏、可验证跳变到达：milestone/observation routing 最优；
- 每个调用都有新独立信息且 cache/handoff 近零：per-call 可能最优。

### 9.3 命题 C：固定粒度可能接近或达到最优

以下充分或近充分条件会使自适应 boundary 无独立价值：

- 存在模型 \(m^*\) 在所有可达状态以超过最大开销差的 margin 支配其他模型；
- 各阶段模型效用排序相关系数接近 1，且反转概率/反转幅度很低；
- 任意重开路由的总代价大于状态条件 EVSI 上界；
- PlanIR/历史无法可靠区分 outcome 分布，Router posterior 接近先验；
- terminal reward 无法局部归因，fork variance 大于可接受效应；
- milestone 不可验证，semantic boundary 的误检/漏检损失抵消收益；
- Router 计算本身高于 gross saving；
- 最优策略几乎总选择 `task_terminal` 或 `next_call`，等价于既有固定策略。

这些条件若在两个任务域和合理成本区间普遍成立，将否定 RouteCraft 作为方法论文；若不同 harness/cache/provider 区域呈现清晰相变，仍可形成有价值的 benchmark/measurement 论文；若只在一个窄域为负，则应报告适用边界而非整体 No-Go。

## 10. Matched same-state fork 的因果解释与数据设计

### 10.1 估计对象

在 pre-decision 状态 \(s\) 同时恢复 session event log 与外部世界快照，随机分配 action \(a=(m,\beta)\)，执行到候选边界，再切到统一 continuation policy \(\pi_0\)。可估计：

\[
\tau_{a,a'}^{\pi_0}(s)=
\mathbb E[Y(a,\pi_0)-Y(a',\pi_0)\mid S=s].
\]

这是相对于 \(\pi_0\) 的局部 policy effect。common continuation 防止“不同分支后续用不同聪明策略”混入当前 action；`task_terminal` 本身无 continuation，应直接跑到终点并与其他 option+\(\pi_0\) 比较。它不自动等于部署时 adaptive policy 的总效果，Phase 2 仍需端到端验证。

### 10.2 有效性威胁

- **快照不完整：** 文件、git index、进程、browser/session、DB transaction、外部 API、clock/RNG/provider state 任一遗漏都会造成不可交换分支、污染或伪反转。
- **环境/工具非确定性：** 固定可控 seed、镜像与时间；用 common random numbers；外部服务需录制/重放或分层随机化。
- **模型随机性：** 不宜给所有分支同一固定重复数。先 2–3 次；对排名 CI 跨零、失败类型不稳定或接近决策阈值的分支序贯加到 5 次或预设上限。
- **provider-private state：** 无法 snapshot 时应标记为不可 fork/cross-provider，不可假设 event replay 等于 provider replay。
- **active-sampling shift：** 只选高不确定/模型分歧状态会夸大可路由性。保留 20–30% 随机 anchor，记录 sampling probability，并对总体估计加权。

若 fork action 在给定状态内随机化且概率已知，简单差值/分层估计即可；IPS/DR 主要用于非均匀 active sampling 的总体外推或复用 observational logs。对高方差 IPS，应同时报告 effective sample size、weight clipping sensitivity；有 outcome model 和已知 propensity 时用 cross-fitted doubly robust，但不能让复杂估计器掩盖支持域缺失。

common random numbers 也需谨慎：action 改变控制流时，共享 stateful PRNG 的“第 k 次随机数”可能对应不同事件。更稳妥的是以 `(task,state,event-id,replicate)` 做 event-keyed counter-based RNG；commitment 段独立采样，进入共同 continuation 后再按事件键耦合。相关 2026 方法论文还指出盲目全程耦合可能比独立模拟方差更高（[event-keyed hashing](https://arxiv.org/abs/2603.11084)，[rollout CRN](https://arxiv.org/abs/2605.04732)）。

### 10.3 控制组合爆炸

1. Phase 0 只用 2 个模型×4 个边界，并先删除上下文窗、工具/API、隐私不兼容 action；
2. 先在 random anchor 全因子采样，估计主效应和交互；其余状态用模型分歧、boundary uncertainty 与预期 EVSI active sampling；
3. 对明显支配 action 做安全 successive elimination；
4. 复用相同 prefix/snapshot，但每个分支使用隔离 world clone；
5. 对 nested boundary 可复用到早期边界的日志，但不能把同一随机输出当独立重复；
6. 用分层/低秩 action model 预测未执行组合，同时保留随机审计分支检测偏差。

## 11. Phase 0—Phase 2 实验方案

### 11.1 Phase 0：一周现象验证与快速证伪

建议收窄为约 120 个任务（每个任务族宏平均）、240–300 个可恢复且 verifier 明确的状态、2 个价格/能力不同的完整模型、4 个边界。τ²-Bench 选择可 snapshot 的 tool/DB episodes；SWE-bench Verified 选 50–60 个容器可复现实例。先不加入 AppWorld，不训练大 Router，不追求完整平台。

**2026 年有效性警告：** SWE-bench Verified 仍适合作为与近期 Router 工作可比、具有容器测试的工程域，但不应再被当作无污染的前沿能力测量。OpenAI 已在 2026 年说明其不再用 Verified 评估前沿 coding capability，理由包括训练污染与测试/规格问题；因此 Phase 0 应冻结一个经人工审计、可重复的诊断子集，并将较新的 SWE-rebench/私有 freshness slice 作为后续 robustness，而不是把 Verified 单独支撑泛化结论（[OpenAI 官方说明](https://openai.com/index/why-we-no-longer-evaluate-swe-bench-verified/)，[原 SWE-bench 论文](https://arxiv.org/abs/2310.06770)）。

按顺序回答：

1. model ranking 和 boundary ranking 的反转率、反转幅度及 bootstrap CI；
2. `net dynamic oracle – best task pinning`，扣除真实 Router、cache、replay、switch、retry；
3. `net dynamic oracle – best single fixed boundary`，并报告固定边界捕获的 recoverable gain ratio；
4. deterministic PlanIR+Logistic/LightGBM 是否在 held-out task 上预测反转，优于 prompt-only 和 capability matcher。

最能在一周内否定核心假设的实验不是训练 Router，而是全因子 matched fork 后计算：

\[
G_{boundary}=V_{oracle(m,\beta)}-\max_{\bar\beta}V_{oracle(m\mid\bar\beta)}.
\]

其中 Oracle 用独立重复/交叉拟合避免样本内 max 偏高。若 \(G_{boundary}\) 实际上为零或被 switch/cache 成本吞没，停止“自适应边界”方法线。

### 11.2 Phase 1：静态反事实 benchmark

每个发布状态含去标识化 pre-decision observation/PlanIR、candidate profile、feasible mask、model×boundary outcome vector、重复/seed、完整成本与 failure type。评估 routing top-1、pairwise ranking、regret-to-held-out-oracle、success AUROC/AUPRC、ECE/Brier、cost MAE/quantile coverage、latency q50/q95、unseen task、leave-one-model-out、price/load/cache shift。

为防泄漏，task 实例及其所有 forks 必须同 split；模型 profile calibration tasks 不进入 unseen-model test；teacher RouteCard 和 raw trajectory 只使用决策时刻之前内容；oracle outcomes 只作标签/评估，不回填 PlanIR。

### 11.3 Phase 2：动态端到端

在 τ²-Bench、SWE-bench Verified 子集和 AppWorld 上运行完整 policy；加入第二种 Agent harness；把 MemoryCraft long-memory slice 作为 cache/context-sensitive stress test，而非 Router benchmark 的唯一主体。比较所有 baseline，锁定 model/version、prompt、temperature、tool environment、tariff 与 cache policy；默认使用合理 prompt cache，不以“未缓存 full context”制造虚高基线。

端到端结果同时给出 all-assigned/intention-to-route（失败仍计成本）与共同完成实例交集；后者便于结构比较，前者防止删除难例。按任务族宏平均，并报告不同 cache provider/同 provider model switch 的分层结果。

## 12. Baseline、消融与研究主张矩阵

### 12.1 必须 baseline

| 组 | Baseline | 隔离的问题 |
|---|---|---|
| 常数 | always-cheap / always-strong / global-best | 池中简单支配与成本上下界 |
| 初始选择 | prompt-only；task-level TRACE-style pinning | 中间信息是否必要 |
| 升级 | fixed-K SWE-style；error-only fallback | 一次升级能否解释收益 |
| 固定粒度 | 每 call；每 observation；每 verified milestone；task terminal | adaptive boundary 是否优于最佳固定粒度 |
| 历史 | MTRouter/history embedding | PlanIR 是否优于原轨迹历史 |
| 系统规则 | vLLM session-aware stay/switch | 学习策略是否优于 cache-aware heuristic |
| 简单学习器 | Logistic、kNN、LightGBM | 模型复杂度是否必要 |
| Profile | HyDRA-style capability matcher | state×candidate 交互是否超过静态能力匹配 |
| Router 上界 | 小模型 Router；强 LLM-as-a-Router | 表示/模型容量上界，计全开销 |
| Oracle | net model×boundary held-out Oracle | 可恢复空间；扣除所有开销 |

Agentic Routing flywheel 可用其 step router/LightGBM 设定；TwinRouterBench 可用 per-call policy 与 outcome-vector 评测协议。EASy、GraphPlanner 和 Iterative Critique Controller 改变 workflow 或 agent sequence，不能作为“固定原 Agent 的 Router”直接等价比较；应作为邻近系统、联合优化上界或单独实验组，清楚标注 workflow 不同。

### 12.2 消融及对应主张

| 消融 | 被检验的研究主张 | 判读 |
|---|---|---|
| prompt-only vs raw trajectory vs PlanIR | 中间状态和压缩表示有用 | PlanIR 不胜 prompt→H3 失败；不胜 raw 但更便宜→看净效用 |
| 去语义状态，仅系统状态 | 教师 RouteCard 语义提供增量 | 无差异→删除主观字段 |
| 外部 verifier→LLM milestone judge | 可验证边界是否关键 | 若 LLM judge 同样好但更贵，保留系统版本；若更差，支持外部证据主张 |
| 去 boundary head，只选模型 | adaptive commitment 的独立贡献 | 无差异→收缩为普通 Router |
| 固定模型，只学 boundary | 收益来自时点还是模型切换 | 有收益说明 boundary 是调度/验证问题；需重写定位 |
| model-ID classifier→candidate-conditioned | unseen-model/profile 主张 | leave-one-model-out 无增益→删除 open-set claim |
| logged terminal→matched fork | 反事实标签缓解 policy confounding | 无增益且 fork 昂贵→benchmark 价值下降 |
| success-only→success+failure+recovery | 失败轨迹对 escalation/early abort 有用 | recovery recall/under-routing 应改善 |
| 忽略 cache/switch penalty | 系统成本会改变策略排序 | 排序不变→系统贡献弱；排序反转→核心 measurement |
| teacher label→execution label | 教师语义是否可靠 | 差距大→只保留 deterministic compiler |
| 每 call 调 Router→仅 event boundary | 稀疏信息到达假设 | event 方案应保留收益并降开销 |
| 单 harness→跨 harness | PlanIR/Adapter 可迁移 | 大幅下降→只作单系统论文 |

## 13. 统计分析协议

- 预注册三个 primary contrasts：adaptive vs best task pinning；adaptive vs best fixed boundary；PlanIR+LightGBM vs strongest nonadaptive learned baseline。
- 以**任务**为 cluster 做 paired bootstrap（建议 10,000 次）；同一任务的多个状态/fork 不得当独立样本。按任务族先求指标再宏平均。
- success 用 paired difference/McNemar 与 bootstrap CI；CPS、Pareto AUC、p95 latency、oracle regret 用 cluster bootstrap。高偏 ratio 可同时报告 percentile/BCa sensitivity。
- 多 primary endpoints/contrasts 用 Holm 校正；探索性分层结果标为 exploratory，不以 p 值挑故事。
- stochastic forks 使用独立 replicate；可控时 common random numbers。报告模型内方差、环境方差、ICC/排名稳定度和达到序贯停止的样本数。
- ECE 使用固定或自适应 bins 并给 bootstrap CI；Brier/NLL 为更稳定主校准指标。quantile head 报 coverage 与 pinball loss。
- Oracle 用独立 outcome replicate、cross-fitting 或 empirical-Bayes shrinkage，避免同一噪声样本既选 max 又评 max。
- “共同完成交集”遵循 MemoryCraft 的结构比较原则，但必须同时给 all-assigned 结果；timeout/crash/invalid tool 视为失败并保留已发生成本。
- price/load shift 只改变 tariff/queue 输入，不用 test outcome 重新训练；unseen task 按 instance-family group split，unseen model 做 leave-one-model-out 并限制 calibration probe 数。

## 14. 证伪和停止条件

原建议方向正确，但“95% Oracle 收益”和“3–5 点”必须带绝对效应与 CI，否则在 Oracle gap 很小时会误导。

| 门槛 | 建议的可执行规则 | 决策 |
|---|---|---|
| 固定边界已解释收益 | 最佳固定边界捕获 ≥90–95% **可恢复净增益**，且 adaptive 增量 95% CI 上界同时 <2 pp success 与 <5% CPS | 停止 adaptive boundary；保留固定 event Router |
| dynamic Oracle 空间不足 | 扣除全成本后，相对最佳 task policy 的 95% CI 不能支持 ≥3 pp success 或 ≥10% CPS；同时 practical upper bound <2 pp/<5% | No-Go 方法；转 measurement |
| 值得继续的 Oracle 空间 | 至少一个主域下 95% CI 下界 >2 pp success 或 >8% CPS，点估计达到约 3 pp/10%，且第二域方向一致 | 进入 Phase 1 |
| Router 开销 | dollar >任务成本 2–5%，或 p95 latency >5%，且未换来 success/CPS 改善 | 简化为 compiler+LightGBM/规则 |
| PlanIR 失败 | held-out task 上不能降低 ≥10% Oracle regret，且 Brier 改善 <0.01、CPS 无改善 | 不训练更大 Router；回到系统字段/measurement |
| 固定原计划后收益消失 | 所有收益只在允许重规划时出现 | 贡献属于 workflow/planning（EASy/GraphPlanner 范围），重写问题 |
| boundary 坍缩 | ≥90–95% 决策落在同一端点，且强制其他边界净效用更差 | adaptive commitment 无独立价值 |
| 反事实过噪 | 每 action 5 次后，关键 pair 的 CI 仍宽于最小有意义效应，或排名稳定性不足 | fork 数据成本不可接受；转聚合测量/确定性域 |

失败后仍可能形成论文：发布执行可复验的 model×boundary outcome benchmark；测量 cache/replay/switch 后动态 Oracle 消失的负结果；给出“何时 task pinning/per-call/milestone 最优”的相图。前提是至少跨两种 harness 或多个成本/环境 regime，并公开完整计量与负证据。

## 15. 6–8 周 MVP 任务表

| 周 | 交付 | 决策门 |
|---|---|---|
| 1 | 固定 commit HarnessAdapter；event/cost schema；SWE/τ² 最小 world snapshot；20-task smoke | fork 可重放率 ≥95%，token/cache/retry 对账 |
| 2 | 120 tasks、240–300 states、2×4 matched forks；随机 anchor | 快照污染、provider state 与 verifier validity gate |
| 3 | 反转、net Oracle、最佳固定粒度、敏感性/CI | 触发 Phase 0 Go/Stop 门槛 |
| 4 | deterministic State Compiler；RouteCard 小样；Logistic/LightGBM/kNN | H3 与标签泄漏审计 |
| 5 | Phase 1 schema、outcome vector、prompt/task/fixed/per-call/profile baselines | Oracle/regret/calibration 可复现 |
| 6 | 动态端到端 τ²/SWE；cache/switch/full-cost accounting | CPS、p95、失败恢复一致性 |
| 7 | 第二 harness/leave-one-model-out/price-load shift；主要消融 | 泛化与 open-set claim 门槛 |
| 8 | AppWorld 或 long-memory stress、artifact、论文；不足则 measurement/negative-result framing | 最终 Go/Revise/No-Go |

严格 MVP 可在第 3 周结束；后 5 周只有通过 H1 门槛才投入。AppWorld、0.5B Router、online bandit/RL 和完整 EASy/GraphPlanner 复现均不在 Phase 0 关键路径。

## 16. DeepSeek Harness 与系统实现映射

### 16.1 核验版本与高优先级版本风险

官方仓库固定在 commit [`47f943859bef60e4160492346772ded9b24f765a`](https://github.com/deepseek-ai/deepseek-harness/tree/47f943859bef60e4160492346772ded9b24f765a)（2026-08-13；package `0.1.0-rc.5`）。调研开始时，工作区原有 `RESEARCH_WORKSPACE\deepseek-harness-local` 是另一实现/客户端环境，不能支撑官方 Harness 结论；该**包身份 blocker 已于 2026-08-17 关闭**：目标目录现为官方完整 checkout，固定上述 commit，使用 Node `v24.19.0` 与 pnpm `11.7.0` 按锁文件安装并完成全仓 build、90 项相关 keyless tests 和 Web HTTP 200 smoke test，最终 Git 状态干净。安装审计见 [deepseek_harness_installation_2026-08-17.md](../evidence/deepseek_harness_installation_2026-08-17.md)。正式实验仍应保持 commit、lockfile 与运行时版本固定，避免 pre-release API 漂移。

### 16.2 指定接口逐项核验

| 问题 | 代码核验结论 | RouteCraft 用法/限制 |
|---|---|---|
| `agent/request` 可否改 provider/model/reasoning effort | **可以。** 每次 provider call 的 call config 暴露 provider、model、`reasoningEffort`，request listener 可替换；但 listener 不能直接改 messages，应从 canonical session events 编译状态（[call config](https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/packages/llm/llm/src/call-config.ts)，[agent loop](https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/packages/core/agent-loop/src/agent.ts)）。 | 在 `HarnessAdapter` 注册有状态 request listener；只修改调用规格，不改 transcript/workflow。 |
| `agent/request-error` 是否适合 fallback | **可作触发器，但不直接携带备用模型。** 它决定 retry/终止；当前代码会在同 turn/step 重新跑 `agent/request`。测试存在 mock provider 失败后切到 other provider 的路径。 | `request-error` 写 fallback ledger；下一次 request listener 读取 ledger 替换 provider/model。记录同坐标 attempt，不伪造新 turn。文档所称 fresh turn 与当前代码存在不一致，实验以固定代码行为为准。 |
| session event 是否 append-only | **是。** durable event log append-only，事件 deep-freeze；模型可见状态应可由 log 重构。 | 以 `(session,event,turn,step,attempt)` 作不可变主键；RouteCraft sidecar 另存世界快照和成本 ledger。 |
| fork/replay 恢复什么 | fork 复制截至已闭合 turn 的 event prefix 和 cwd 元数据；**不**复制外部文件系统、DB、进程、browser、network、clock、RNG 或 provider-private state。 | session fork 不是 world fork；任何 benchmark branch 先恢复外部快照，再 replay/fork harness。 |
| `TokenUsage` 桶 | 五类：uncached input、output、cacheRead、cacheWrite、reasoning；reasoning 是 output 的子集，不能重复相加；billed input 为 input+read+write。失败调用在已流式上报 usage 时仍可计量。 | 逐 attempt 保存原始 provider usage 与 normalized buckets；缺失值标 unknown，不能填 0。DeepSeek adapter无 cache-write，某些 adapter不分 reasoning。 |
| provider-private replay state 能否跨模型/adapter | 跨 adapter 时 core 会剥离 replay state；同 adapter 跨 model/provider 只能“交给 adapter”，是否有效由 adapter/provider 验证，**没有可迁移保证**。 | compatibility profile 使用实测 `same adapter/model/provider` 矩阵；不兼容时 treatment 必须包含 state loss 与 context replay。 |

### 16.3 最小实现架构

```text
adapters/
  deepseek_harness_adapter/   # request/request-error listener, event normalizer
  second_harness_adapter/     # 相同 canonical event/cost 接口
state_ir/
  deterministic_compiler/    # 系统事实、provenance、version
  routecard_teacher/          # 离线弱语义、alignment/abstention
world_snapshot/
  swe/ tau2/ appworld/        # clone/restore/validity checks
counterfactual_runner/
  sampler/ fork_executor/ common_continuation/ rng/
verifiers/
  swe_tests/ tau2_predicates/ appworld_state_tests/
model_profiler/
  probes/ tariff/ latency/ cache_replay_compat/
routers/
  rules/ logistic/ knn/ lightgbm/ encoder/ llm_ceiling/
benchmark_and_analysis/
  ledger/ metrics/ oracle/ bootstrap/ calibration/ reports/
```

事件流：`agent/request` → State Compiler → feasible action mask → scorer → request spec override → provider call → TokenUsage/latency ledger；tool/environment event 与 `request-error` 更新状态；\(\beta\) 未触发时 request listener保持 committed model，触发/安全中断时再调用 Router。

### 16.4 世界快照

| 域 | session fork 之外必须恢复 | validity gate |
|---|---|---|
| SWE-bench | 容器/镜像 digest、repo commit、worktree/patch、git index、依赖与 test cache、权限、进程、env、time/network policy、seed | 恢复后 hash/status/test precondition 一致；分支独立容器/overlay |
| τ²-Bench | simulator DB/slot、用户状态、conversation event、tool side effects、policy/rules、RNG/clock | 账户/订单等 predicate 与 pre-fork 完全一致；用户模拟 event-keyed |
| AppWorld | AppWorld DB、9-app/API state、filesystem、time、evaluator、RNG | state-based unit tests 的初始 predicate 与 collateral-damage baseline 一致 |

使用薄 adapter 是为了把 harness 特有 event 投影成 canonical IR，而不是把 routing 逻辑写进 agent loop；固定 commit 是为了保证 event/request/retry/replay semantics 不在实验中漂移。完整论文仍需第二 harness，因为只在 DeepSeek Harness 上有效无法区分“RouteCraft 学到通用事件信息”与“学到该实现的 turn/error/serialization 特征”。第二 harness 不必功能完全相同，但需实现同一最小 event、usage、snapshot 与 override contract。

### 16.5 vLLM Semantic Router / OpenSquilla 对实现的约束

[vLLM Semantic Router](https://github.com/vllm-project/semantic-router/tree/ef9e5dd99c953a21d20a99a93547e57468bae863) 的 Session-Aware Agentic Routing（SAAR，固定 commit `ef9e5dd…`）已实装 session memory、tool/provider-state hard lock、idle/decision-drift reset、prefix-cache/handoff/switch-history penalty、remaining-turn prior 与 per-turn cache-aware cost。其官方博客在 21,600 synthetic deterministic turns 上作者报告 switches -79.29%、unsafe switches 3836→0、估算 physical-model cost -78.71%，并在 2,896 live requests 上报告无 lock violation；这些是特定模拟/配置价格结果，不等同真实 CPS（[官方 SAAR 报告](https://vllm-project.github.io/2026/06/02/session-aware-agentic-routing.html)）。SAAR 应作为最强 `stay/switch` baseline，而不是普通 prompt router；它已覆盖“何时安全切换”的大量机制，但未显示用 same-state model×多值 boundary outcomes 学习 termination policy。

[OpenSquilla 0.5.3](https://github.com/opensquilla/opensquilla/tree/79d57b2fe63e1f83b364ca2bd022e0cb76081406) 是 Harness-Native flywheel 的官方实现：每 turn history-aware routing，最近路由历史与 prior usage 入模；有 agent-issued 600 秒 idle hold、session fork/replay、proposed-vs-executed decision ledger 及物理 provider-call usage ledger。它还可改变 reasoning level、prompt policy 和 ensemble，因此直接 baseline 必须禁用这些改写，仅保留模型选择。两者都要求 RouteCraft 把贡献锚定在**可学习的多值 reopen boundary 与反事实净价值**，而不是“session-aware”“harness-native”或“本地轻量 Router”。完整源码证据卡见 [B_harness_systems.md](../research_notes/B_harness_systems.md)。

## 17. 最终科研决策

### 17.1 `Revise`，不是无条件 `Go`

**实现可行性：有前置条件的 Go。** DeepSeek Harness 的 per-call override、append-only events、retry seam 和 usage buckets 足以做不改 Agent loop 的原型；τ²/AppWorld 有状态重建原语，SWE 可用独立容器/CoW。同名包已纠正，剩余前置条件是实现原子 harness+world snapshot、建立物理 attempt ledger 和 replay/cache compatibility matrix。

**方法/论文：Revise。** RouteCraft 的广义表述与 MTRouter、TwinRouterBench、Harness-Native、HyDRA、vLLM SAAR、SWE-Router、Budget-Aware 和 Critique Controller 重叠过大。仍未被完全覆盖的是一个更窄组合：固定 workflow、完整模型、**多值且可外部验证的未来 reopen boundary**、matched model×boundary fork、全 switch/cache/retry-adjusted CPS。这个组合有理论合理性，但是否存在净效应完全未知。

### 17.2 更窄、更稳妥的替代研究问题

> **在固定 Agent workflow、可恢复 harness event states 与真实 cache/switch/retry 成本下，哪些外部可验证事件具有正的 full-model re-routing value？最佳固定 event boundary 是否已经捕获几乎全部动态 Oracle 收益？**

这比原题更稳妥，因为它先测量“adaptive boundary 是否有空间”，再决定要不要训练 PlanIR Router。三种结果都可形成诚实贡献：

- Oracle 空间大、边界反转稳定、PlanIR 可预测：升级为 RouteCraft 方法论文；
- fixed observation/verification boundary 捕获绝大多数收益：形成简单系统策略与负方法结论；
- 扣全成本后 dynamic Oracle 消失：形成“为何 per-call Agent routing 不省钱”的 measurement/negative-result。

### 17.3 最终投入门

一周内先跑 random-anchor 2×4 matched fork。继续投入的**目标门槛**：full-cost dynamic Oracle 相对 pinning 约 ≥5pp success 或 ≥15% CPS，方向在两个域一致；最佳固定 boundary 捕获 <80–90% dynamic gain；至少约 20% random-anchor states 有跨重复稳定且超过 practical margin 的 action reversal；PlanIR v0+LightGBM 在 held-out task 恢复 ≥30–40% 可实现 Oracle gain。停止门槛：dynamic Oracle 的 one-sided 95% CI 上界同时 ≤3pp success 和 ≤10% CPS；或固定边界 gain-recovery 的 CI 下界接近/达到 95% 且 residual upper bound <1–2pp/<5%；或 world clone 失败 >2%、3 repeats label 一致率 <90%。

**最终结论：`Revise`。先批准一周 Oracle measurement，不批准直接建设完整平台、训练 0.5B–1.5B Router 或上复杂 RL。**

## 18. 本地交付与可审计性

- 完整报告：本文件；正式 DOCX 版本与本文件同目录。
- 21 项完整路由/系统工作、23 字段总表：[related_work_matrix.csv](../evidence/related_work_matrix.csv)。
- MemoryCraft 审计：[00_memorycraft_methodology.md](../research_notes/00_memorycraft_methodology.md)。
- Router 论文证据卡：[A_router_literature.md](../research_notes/A_router_literature.md)。
- Harness/DeepSeek/vLLM/OpenSquilla 代码证据卡：[B_harness_systems.md](../research_notes/B_harness_systems.md)。
- 轨迹/理论/反事实证据卡：[C_theory_trajectory.md](../research_notes/C_theory_trajectory.md)。
- 检索协议：[search_protocol.md](../evidence/search_protocol.md)。
- 本地 PDF 完整性、页数与 SHA-256：[local_archive_inventory.csv](../evidence/local_archive_inventory.csv)。
- 分类说明：[papers/README.md](../papers/README.md)。

截至归档清点，共 51 份有效 PDF，均通过 `%PDF` header 与 `pdfinfo` 页数检查；其中一份 1991 metareasoning 文件明确只是 1 页摘要扫描，不冒充全文。官方代码事实由固定 commit 链接支撑；网页/代码文档没有被伪装成论文 PDF。未开源、无法访问、只发布模型/数据或正式录用未确认的工作均在矩阵/证据卡中显式标注。
