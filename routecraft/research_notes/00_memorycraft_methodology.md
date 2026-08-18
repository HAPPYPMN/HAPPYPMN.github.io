# MemoryCraft 完整阅读记录（方法学起点，不是 Router 系统）

- 文件：`background/MemoryCraft_VLDB_Submission_Sept.pdf`
- PDF 标题：*MemoryCraft: A Runtime and Cost Characterization of Agent Memory Across Frameworks and Retrieval Regimes [Experiment, Analysis & Benchmark]*
- 作者：Cheng Deng, Eve Sauvage, Danna Zheng, Wenyu Huang, Luo Mai, Jun Wang, Jeff Z. Pan
- 页数：19
- SHA256：`82F96BF1B9E86AC206B31DE4DF50744B1B69230DBCD3B169A51A5D9B8A3D2289`
- 稿件状态：用户说明为未正式发表投稿稿；PDF 自报 PVLDB 2027，但 DOI、artifact URL、许可与部分版本信息仍有占位符，不能作为已录用论文引用。
- 阅读方法：`pdftotext -layout` 全文抽取（1,197 行）+ 19 页 PNG 逐页渲染核查。

## 对 RouteCraft 直接可迁移的方法学

1. **固定协议、可替换组件。** 将 execution protocol 固定，把 memory backend、agent framework、backbone 和 retrieval-control locus 作为可替换轴。RouteCraft 应照此把原 Agent workflow 固定，仅替换 `(model, boundary)` policy。
2. **harness-issued 与 agent-issued 控制分离。** MemoryCraft 的两种 retrieval regime 只改变谁构造查询；RouteCraft 对应要区分 harness-native 决策事件与 agent 自行决定的语义/工具事件，不能把二者的结果混称为同一 Router 效果。
3. **逐模型调用计量。** 每次 model call 记录 cache-miss input、cache-hit input、output、turn、retrieval/tool event、tool success、latency、truncation、long-context tier 与 usageFound。MemoryCraft 没有系统性列出 reasoning token、retry/fallback、switch/handoff，因此 RouteCraft 必须扩展 schema。
4. **Agent loop 改变排序。** 在同一 store、同一 ingestion、同一预算下，LoCoMo 上 Supermemory > MemOS > Mem0 的 harness-issued 排序变为 Mem0 > MemOS > Supermemory；说明离线/单调用 ranking 不足以外推到 live loop。
5. **成本主要来自额外轮次和上下文重读。** agent-issued 相比 harness-issued：MemOS turn 3.7x、input token 2.9x；Supermemory turn 3.1x、input token 2.5x。多轮中 output token 低于总 token 的 1%，resident context/cache-hit 重读是一阶成本。
6. **cache-aware 成本。** 不能先把 cache-hit 与 cache-miss 相加；价格比应显式保留。MemoryCraft 使用 cache-miss-equivalent token：`T_eff=t_miss+rho_hit*t_hit+rho_out*t_out`。
7. **共同完成实例交集。** 所有跨条件比较限制在全部条件均完成的实例交集；失败、部分 ingestion、context overflow、missing usage 不能当作零成本或零分。
8. **同配置基线。** 增益应减去同 backbone、同 framework 的 no-history baseline；跨 framework 搬用 baseline 会把 abstention/guessing policy 混入效果。
9. **工具可靠性是 validity gate。** tool-call success <90% 的 `(backbone, framework)` cell 应排除或单报，否则 retry/turn cost 测到的是工具协议缺陷。
10. **薄 adapter + 行为验证。** 配置“看起来生效”不代表代码路径真的使用。应通过 dead endpoint、known namespace、retrieval call count、scope argument 等行为检查，而非只读配置。

## 对 RouteCraft 必须修正/扩展的地方

- MemoryCraft 研究的是 memory system access，不选择完整模型，也不学习 re-decision boundary；它不是可直接复用的 Router baseline。
- 其单次主网格运行较多，重复仅覆盖固定小子集；RouteCraft 的 same-state fork 与边界反转是核心，随机分支需更强重复与 paired inference。
- monetary cost 排除 local embedding/CPU/GPU、能耗，并且 token 跨 host 不可比；RouteCraft 需报告本地推理时间、能耗、queue/batching/tail latency。
- 未显式计量 Router、Judge、retry、fallback、switch、provider-private replay、context serialization/handoff；这些必须进入 RouteCraft 总成本。
- agent-issued 只覆盖 3/5 stores，第二 backbone 只覆盖 2 stores；不能从该稿件推出普遍的 agent-loop interaction。
- 作者明确称其机制解释仍是 correlational；RouteCraft 的 matched fork 需要更接近因果的 same-state、same-world、common-continuation 设计。
- 成本与准确率来自不同子集（主网格 vs 20-instance metering），而 RouteCraft 的 `cost per successful task` 必须在相同任务/分支上联合观测。

## 稿件内部未完成/风险标记

- PVLDB citation 中 `XXX-XXX`、`XX.XX/XXX.XX`。
- Artifact URL 为 `URL_TO_YOUR_ARTIFACTS`，正文称“upon acceptance”。
- 版本表 Host C 含 `[collect]`；benchmark licence 含 `[verify]`。
- 一处 memory-free contamination 提升写为 `[X] points`。
- 这些不削弱其方法学启发，但使任何“已发表/已完整复现/所有 artifact 已发布”的表述均不成立。

## RouteCraft 可直接采用的最小 trace 扩展

在 MemoryCraft trace 基础上增加：`model_id`、`boundary_id`、`router_invoked_at`、`router_cpu/gpu/token/latency`、`reasoning_tokens`、`retry_reason`、`fallback_chain`、`cache_write`、`cache_invalidated_by_switch`、`provider_private_state_replayed`、`context_serialization_bytes/time`、`model_load/residency/queue/batch`、`verifier_result`、`world_snapshot_id`、`continuation_policy_id`、`terminal_success`。

