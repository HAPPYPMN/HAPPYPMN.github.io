# Agent 完整模型 Router 调研检索协议

## 时间与对象

- 执行日：2026-08-17（Asia/Shanghai）。
- 核心时间窗：2025-2026；必要奠基工作回溯至 2023 或更早 options/SMDP 理论。
- 核心对象：多个完整 LLM 之间的选择，尤其单个 Agent 任务内动态切换。
- 排除：MoE token-to-expert、Tool/RAG/Memory Router、多 Agent role selection、workflow generation、speculative decoding、token early exit、dynamic layer skipping；仅在理论或边界讨论中纳入。

## 一手来源优先级

1. 正式 proceedings / ACL Anthology / PMLR / OpenReview / 期刊页。
2. arXiv 原文（标 preprint，不把投稿/将发表当录用）。
3. 作者/组织官方 GitHub、release、commit、官方系统文档。
4. 厂商官方博客只支持该系统的实现/自报结果，不支持普适结论。
5. 搜索结果页、聚合站、二手报道仅用于找线索，不作为关键事实证据。

## 检索族

- `LLM model routing agent multi-turn history trajectory routing`
- `agentic model router per-call turn session milestone escalation`
- `harness native routing model switching agent event replay cache`
- `LLM routing switch cost KV cache context replay handoff`
- `LLM router unseen model capability profile candidate conditioned`
- `agent trajectory distillation plan state failure recovery`
- `same-state fork counterfactual agent benchmark`
- `semi-Markov options termination deliberation cost value of information`
- 对用户列出的每个精确标题单独检索；标题不匹配或同名时标“未核验”。

## 纳入/排除与核验字段

- 纳入：可找到英文原论文/官方仓库/官方文档，且能确定路由对象或对 RouteCraft 的理论/系统边界有直接贡献。
- 排除：只路由工具/检索器/专家、只生成 workflow、只有营销页且无技术内容；但保留边界卡。
- 每项记录：标题、作者、年份、venue/status、paper URL、code URL、路由对象、粒度、任务内切换、输入/历史/阶段、router/标签/Judge、未见模型、workflow 改动、成本计入遗漏、benchmark/model pool、结果、局限、RouteCraft overlap、verification status。
- `VERIFIED`：原论文或官方代码/文档直接支持。
- `AUTHOR-REPORTED`：只在作者实验设置内陈述，未复现。
- `PARTIAL`：元数据/代码/结论只核验一部分。
- `UNVERIFIED`：标题、状态、代码或结论无法从一手来源确认；绝不补全。

## 反证优先规则

- 主动检索与“自适应边界”同构的方法。
- 优先报告简单 fixed boundary/kNN/LightGBM/task pinning 达到动态 Oracle 大部分收益的证据。
- 不把相关性写成因果；matched fork 只在 snapshot、随机化和 continuation 条件满足时提供局部因果估计。
- 成本声明必须注明是否包含 Router/Judge/cache loss/retry/switch/外部工具/本地能耗。

