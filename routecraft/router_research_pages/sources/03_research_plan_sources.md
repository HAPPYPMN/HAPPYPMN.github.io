# Page 03 source ledger：研究分支、证据门与投入边界

核验日期：2026-08-17  
对应页面：[`03_research_plan_branches.html`](../03_research_plan_branches.html)

## 1. 本页的证据层级

本页不是实验结果页。页面内容必须按下列四层阅读：

1. **论文或官方系统事实**：已有工作实际采用的决策粒度、状态输入、连续性机制和作者报告结果。
2. **跨论文综合判断**：把多篇工作放在一起后得到的研究推论，不等同于任一论文的原始结论。
3. **候选研究假设**：RouteCraft Phase 0—2 将要检验的命题，执行前不能写作事实。
4. **规划规则**：样本规模、停止阈值和资源门，用于控制投入；它们不是领域通用常数。

## 2. 从前人工作继承的事实

| 页面判断 | 一手证据 | 能支持什么 | 不能支持什么 |
|---|---|---|---|
| Agent 历史和执行状态可以进入完整模型选择 | [MTRouter](https://aclanthology.org/2026.acl-long.2045/)、[Hera](https://arxiv.org/abs/2605.24598)、[EvoRoute](https://arxiv.org/abs/2601.02695) | 已有 trajectory/history-aware 的完整模型 Router；逐 step 或 turn 路由并非空白 | 不能证明每次调用重新路由在完整成本下最优 |
| 整任务保持或固定事件重选可能有价值 | [TRACE-Router](https://arxiv.org/abs/2607.22465)、[HyDRA](https://arxiv.org/abs/2605.17106)、[vLLM SAAR](https://vllm-project.github.io/2026/06/02/session-aware-agentic-routing.html) | task pinning、session stickiness、continuity lock 和切换惩罚已有直接先例 | 不能证明某个固定事件对所有 Agent 和任务都最优 |
| Same-prefix、harness state 与 cache-aware 计量已有先例 | [TwinRouterBench](https://arxiv.org/abs/2605.18859)、[Harness-Native technical report](https://arxiv.org/abs/2607.11399)、[OpenSquilla 0.5.3](https://github.com/opensquilla/opensquilla/tree/79d57b2fe63e1f83b364ca2bd022e0cb76081406) | RouteCraft 不能声称首次 trajectory-aware、harness-native 或 cache-aware | 在本次已核验工作中，尚未发现同一外部世界快照上的 `model × future boundary` 完整反事实 |
| Oracle opportunity 不等于可部署收益 | [Opportunity Is Not Realizability](https://arxiv.org/abs/2608.08265) | 必须区分 outcome oracle、可用信号下的 Bayes gain 和 held-out learned gain | 不能把 full-information dynamic Oracle 直接写成 Router 可实现收益 |
| Agent loop 会改变真实成本与系统排序 | MemoryCraft 未公开原稿（公开版未收录） | 固定执行协议、逐模型调用计量、额外轮次与上下文重读是方法学起点 | MemoryCraft 不是完整模型 Router，不能作为 Router 效果证据 |

更完整的逐项证据卡见：

- [`A_router_literature.md`](../../research_notes/A_router_literature.md)
- [`B_harness_systems.md`](../../research_notes/B_harness_systems.md)
- [`C_theory_trajectory.md`](../../research_notes/C_theory_trajectory.md)
- [`RouteCraft_research_decision_report_2026-08-17.md`](../../reports/RouteCraft_research_decision_report_2026-08-17.md)

## 3. 跨论文综合判断

以下是本报告的综合分析，不是单篇论文的原话：

- 执行中的新状态可能改变最佳模型，但更多可见状态并不自动产生更低的任务成本。
- `next_call`、固定 K、每 turn、compaction event 和 task terminal 多数仍是系统预设的重决策时机；“未来何时重新开放 Router”通常不是学习动作的一部分。
- 外部工具反馈、确定性验证和错误恢复比无外部反馈的连续 reasoning 更可能带来新的能力需求；这是待检验的关联和预测假设，不是已经识别的因果效应。
- 不可逆 ACT、provider-private replay state、长前缀和高 cache 命中阶段具有更高切换风险。
- RouteCraft 只有在完整成本下超过最佳 task pinning 与最佳固定事件，并且部署前状态能识别这部分剩余机会时，才有独立方法贡献。

## 4. 三个候选假设及标签

### H1：完整成本下仍有净机会

比较 `model × boundary` 策略、最佳 task pinning、最佳固定事件与 per-call routing。Phase 0 的 checkpoint states 来自冻结的参考策略 `π_ref` base rollouts，因此估计的是参考状态分布 `d(π_ref)` 上的局部反事实机会，不是新 Router 改变未来状态分布后的端到端效应。主要标签来自外部 verifier、物理调用账本和实际 wall-clock；失败任务已经发生的价格与时间仍计入。

`cost per successful task (CPS)` 的口径为：

```text
CPS = 所有分配任务实际发生的总成本 / 外部 verifier 确认成功的任务数
```

失败任务不能从分子删除。价格、成功率、p95 与 time-to-success 分别报告，不把它们提前压成单一 utility。

### H2：机会集中在可观测事件

比较工具 observation、retrieval result、deterministic verification、error/recovery 之后的动作排序变化，与没有新外部信息的普通 call。只能先声称这些事件与更高净决策价值相关；若没有事件随机化或有效因果设计，不写成事件导致了 capability-demand drift。

### H3：部署前信息能够实现机会

训练与测试只使用决策时刻已经可见的 Harness facts、PlanIR 或 raw trajectory。先用 Logistic、kNN、LightGBM；只有 raw trajectory 明显优于结构化特征、且增量覆盖部署成本后，才考虑小型 encoder 或 0.5B–1.5B Router。

## 5. 顺序 Gate 的解释

| Gate | 要回答的问题 | 通过后允许的主张 | 失败后的正确转向 |
|---|---|---|---|
| G0 | 快照、隔离、verifier 和物理调用账本是否可信 | 可以解释 matched fork | 只做 snapshot/ledger 工程审计；暂停 Router 效果解释 |
| G1 | 是否存在 action heterogeneity | 当前模型池存在动态机会 | 单一策略支配；停止动态 Router |
| G2 | 扣除 Router、cache、replay、retry、handoff 后是否仍有净收益 | 在 `d(π_ref)` 上存在 full-cost counterfactual opportunity | 转为“局部 Oracle 机会被系统成本吞噬”的 measurement/negative result |
| G3 | 外部可观测事件能否以更少的重决策保留主要局部净机会 | event-driven routing 可能有独立价值 | H2 失败；转 per-call Router 或报告事件边界无增量价值 |
| G4 | 自适应策略是否仍显著超过最佳固定事件 | CI 下界越过预注册正收益门槛，且另一指标非劣，才支持 adaptive boundary | CI 上界落入停止区则采用固定事件；区间跨过停止区与通过区则在资源门内补样本，仍不收敛就报告 inconclusive |
| G5 | 决策前状态能否在 held-out task 上识别剩余机会 | 可以进入可部署 Router 训练 | 形成 opportunity-not-realizability benchmark；不训练更大 Router |
| G6 | 效应能否跨域或跨 Harness 复现 | 可以提高通用性主张 | 限定为单域或单 Harness 系统结论 |

范围退出分支：

- 只有允许重新规划时才有收益：转向 workflow/planning，不再声称固定 Agent Router。
- 最优边界坍缩为 `next_call`：退化为已有 per-call Router。
- 最优边界坍缩为 `task_terminal`：退化为 task pinning。

## 6. Branch run 与规模算术

一个 branch run 是从参考策略 `π_ref` 产生的同一 Agent checkpoint state 恢复 Harness 和外部世界，执行一个 `(model, boundary)`，再按统一 continuation policy 运行到预定义终点。它不等于一次 LLM 请求；分支内可以发生多次模型调用、工具调用、失败重试与上下文重放。

Matched fork 固定了起点和 continuation，因此估计受控的局部 action effect。它没有重新采样新 Router 早期动作所诱导的未来状态分布，不能直接称为端到端 dynamic policy Oracle。Phase 0 结果统一写作 `full-cost counterfactual opportunity on d(π_ref)` 或 `empirical local-Oracle upper bound`；端到端收益只在 Phase 2 动态 rollout 中判断。

```text
N_branch = Σ_state Σ_action repeats(state, action)
```

若每个状态运行全部动作：

```text
N_branch = N_state × N_model × N_boundary × N_repeat
```

规划算术：

- 20-state smoke：每个 task 暂取 1 个 checkpoint state，`20 × 2 × 4 × 1 = 160`；工程门通过后累计补到 3 repeats，即 `480`。
- 40–50 random anchors：`40–50 × 2 × 4 × 3 = 960–1,200`。
- 一周 Phase 0：anchors 跑全因子，其余状态只跑 3–4 个候选动作，累计约 `1,680–3,000` branches。
- 较大全因子 Phase 0：`240–300 × 2 × 4 × 3 = 5,760–7,200`，不是默认第一周方案。
- Phase 1 示例：`500 × 2 × 4 × 3 = 12,000` branches。

这些数字是累计规模：如果 smoke 状态继续作为 random anchors，不能重复相加。生成中间状态的 base rollout 成本不包含在 branch 数中，必须另记。

## 7. 现在可确定与必须实测的成本

| 现在可以确定 | Smoke 后才能确定 |
|---|---|
| task、state、model、boundary、repeat 推出的 branch 数 | 每个 branch 的美元成本、物理 provider call 数、token 四桶、工具与重试成本 |
| 两个冻结 deployment 的公开价格快照 | 完整 Phase 0 账单与 price uncertainty |
| world snapshot 的逻辑组成 | CoW 后的实际磁盘占用与清理周期 |
| 计划并发、provider quota | queue 与长尾作用下的 makespan、p50/p95 branch latency |
| State Compiler/Router 调用次数 | CPU/GPU 开销、p95 Router latency 与净部署成本 |

页面中的 80% spend/time/storage 规则是内部规划门：pilot 投影的 95% 上界不超过已批准资源的约 80%，留下至少 20% 处理重试和长尾。它不是论文结论，也不应替代实际预算审批。

## 8. 候选统计和停止规则

- 基线、固定事件和 Router family 在 design split 或 nested cross-fitting 中选择；最终效应只在未参与选择的 task-level test split 上估计。
- 每状态取 observed minimum 只能称为 in-sample empirical local-Oracle upper bound。选出最佳固定策略后的区间必须使用 selection-valid 或 simultaneous interval，不能在同一批结果上选择赢家后继续使用普通区间。
- 成功率提高且 CPS 不劣；或者 CPS 降低且成功率在预注册 1 percentage point 非劣界内，才算方向性正结果。
- Gate 2 的 practical margin 必须在 smoke 后根据可接受的任务级改善、方差与资源预算预注册；极小的正点估计不能自动放行。
- Gate 4 三分：若 adaptive 相对最佳 fixed event 的 95% CI 上界同时低于 1 pp success 与 5% CPS 改善，停止 adaptive boundary；若 CI 下界超过 smoke 后预注册的 success 或 CPS 正收益门槛，且另一指标满足非劣约束，才通过；区间同时跨过停止区与通过区则标记 inconclusive，只能在资源门内追加样本，达到上限仍不收窄就停止，不能进入 G5。
- 状态反转比例只作描述；主要量使用按 `π_ref` 状态占用率加权的 fixed-policy regret。
- Snapshot mismatch 的分支不能进入 paired analysis。`>2%` 只可作为工程暂停线，不是可接受失败率。
- 对随机输出采用序贯重复；无法稳定区分的 state-action 标记为 `stochastically ambiguous`，不强造 hard label。
- Router overhead 必须小于增量 gross saving，并满足 p95 SLO；“不超过任务成本 5%”只作早期工程目标。
- Phase 0 对预先固定策略使用 task-level paired bootstrap，并按任务族宏平均；涉及 data-dependent 最佳策略选择时改用独立 test split、nested cross-fitting 或 simultaneous interval。多指标阈值与 primary endpoint 必须在正式执行前预注册。

上述数值是候选规划规则，需由 smoke 的方差、基准成功率、价格和延迟分布修订，不是普适统计常数。

## 9. 证据状态与限制

- 本页引用的 2026 工作多为 preprint；正式发表状态以逐项证据卡为准。
- EvoRoute 论文指向的代码仓库在核验日不可访问，因此不声称其代码可复现。
- HyDRA 代码状态未完全核验；页面只使用论文可核验信息。
- vLLM SAAR 的成本结果是其特定 synthetic/live 协议下的系统结果，不等于完整 Agent `cost per successful task`。
- Page 03 的可能结果、Gate 和排期都是未来研究计划，不是对实验结果的预测。
