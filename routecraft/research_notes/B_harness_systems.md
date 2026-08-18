# 证据流 B：Harness 与系统实现核验

> 检索/核验截止：2026-08-17（Asia/Shanghai）。本文只负责 Harness、会话/事件、切换与计量的系统证据。标签含义：**[代码事实]** 固定 commit 源码；**[文档事实]** 官方文档/作者报告；**[推断]** 基于前两者的工程判断；**[未核验]** 尚无足够一手证据。

> **安装状态更新（2026-08-17）：** 下文记录了调研时发现的同名包冲突。该包身份 blocker 现已关闭：`RESEARCH_WORKSPACE\deepseek-harness-local` 已替换为官方完整 checkout，固定 commit `47f943859bef60e4160492346772ded9b24f765a`，按锁文件安装并完成 build、90/90 相关测试与 Web smoke。可复核记录见 [`deepseek_harness_installation_2026-08-17.md`](../evidence/deepseek_harness_installation_2026-08-17.md)。snapshot、state portability 与 attempt attribution blocker 仍未关闭。

## 0. 科研决策结论（先读）

1. **DeepSeek Harness 足以作为 RouteCraft 的首个实验底座；调研时发现并随后关闭了同名包冲突。** 官方 `deepseek-ai/deepseek-harness` 在每次模型请求前提供可替换 `provider/model/reasoningEffort` 的 `agent/request` waterfall，`agent/request-error` 可触发重新尝试，Session 是 append-only event log，且 TokenUsage 能区分 uncached input、cache read/write、output、reasoning。调研时 `RESEARCH_WORKSPACE\deepseek-harness-local` 中安装的是 `HenryZ838978/deepseek-harness==0.2.0`（DeepSeek V4-Pro/Flash 客户端），不是官方事件驱动 Harness；现已替换为上述官方固定 commit。
2. **官方 fork 不是 world snapshot。** DeepSeek fork 复制截至稳定 turn 边界的事件前缀和 `cwd` 元数据；不会复制文件系统、数据库、正在运行的进程、端口、浏览器、远程工具副作用、时钟或 RNG。same-state fork 必须将 Harness fork 与 benchmark-specific `WorldSnapshot` 作为一个原子操作。
3. **跨模型切换的 state/cache 代价是真实且非二元的。** DeepSeek core 对跨 adapter 的 provider-private `replayState` 一律剥离；同一 adapter 跨模型/跨 provider 只会把 state 交给 adapter，能否复用由 adapter/provider 决定。模型或 provider 改变也进入不同 prompt/KV cache domain。因此 profile 应是 `(from deployment, to deployment, state kind)` 兼容矩阵，不是 `cache_compatible: bool`。
4. **vLLM Semantic Router 的 session-aware agentic routing（SAAR）是 RouteCraft 最强系统级同构反例。** 它已实现稳定 session memory、tool-loop/provider-state 硬锁、idle/drift reset、prefix-cache/handoff/switch-history penalty、replay-derived remaining-turn prior 与 per-turn cost accounting。RouteCraft 不能声称首个 session-aware、harness-native 或“决定何时切换”的 Router；唯一可辩护的差异是：在固定 workflow 上，以 matched counterfactual 标签学习联合动作 `(model, future termination boundary)`，其中 boundary 是可验证事件谓词，而非每请求重算后由固定锁/阈值决定 stay/switch。
5. **OpenSquilla 是很强的第二实现参照，但不是干净的直接 baseline。** 其 0.5.3 router 每 turn 重路由，输入当前语义消息、最近五个路由历史（30 分钟窗口）、前一助手输出/usage、历史 user text、附件等；还会改变 reasoning level、prompt policy，最高 tier 可触发 ensemble。它也有 session fork、turn decision ledger 和物理 provider-call usage ledger。因此可用于“第二 harness 可移植性”与 agent-issued/harness-issued 对照，但直接比较时必须冻结其 prompt/thinking/ensemble 改写，否则贡献混入 workflow/config 变化。
6. **最小实现可行，但主要 blocker 不在 Router 模型，而在可复现快照和物理成本归因。** 建议先只做稳定闭合 turn/tool-observation 边界；将每个分支放入独立 Docker/DB world clone；调用级 ledger 关联 `session_id/turn/step/attempt/provider/model`，并从 serving 层采集 queue/prefill/decode/KV 指标。不要把 Harness token meter 当作完整系统成本。

---

## 1. 固定版本与可复现信息

| 系统 | 固定 commit / 版本 | 核验范围 | 备注 |
|---|---|---|---|
| DeepSeek Harness（官方） | `47f943859bef60e4160492346772ded9b24f765a`, 2026-08-13, npm `0.1.0-rc.5` | agent loop、session、LLM runtime、retry、token meter、DeepSeek/Pi-AI adapters | [官方仓库](https://github.com/deepseek-ai/deepseek-harness/tree/47f943859bef60e4160492346772ded9b24f765a) |
| 调研时旧本地同名包（已移除） | `deepseek-harness==0.2.0`，Home `HenryZ838978/deepseek-harness` | `pip show`、CLI | 非官方 DeepSeek Harness；名称冲突已关闭 |
| vLLM Semantic Router | `ef9e5dd99c953a21d20a99a93547e57468bae863`, 2026-08-17 | session-aware selector、router memory、telemetry/cost、官方 SAAR blog | [官方仓库](https://github.com/vllm-project/semantic-router/tree/ef9e5dd99c953a21d20a99a93547e57468bae863) |
| OpenSquilla | `79d57b2fe63e1f83b364ca2bd022e0cb76081406`, 2026-08-17, `0.5.3` | router step、routing history、router-control hold、session fork/replay、usage ledger | [官方仓库](https://github.com/opensquilla/opensquilla/tree/79d57b2fe63e1f83b364ca2bd022e0cb76081406) |
| LangGraph | `644815f9e5bc52ad8f7a5227a456227e9c3e639b`, `1.2.11` | 仅官方 persistence/time-travel 文档对照 | 非完整源码审计 |
| OpenAI Agents SDK Python | `37a7aa20cee5f16d3720214c39dc66ca9f143e74`, `0.21.1` | 仅官方 run/session/usage 文档对照 | 非完整源码审计 |

### 1.1 本地安装冲突（必须先解决）

**[代码/环境事实]** `RESEARCH_WORKSPACE\deepseek-harness-local\venv\Scripts\python.exe -m pip show deepseek-harness` 返回版本 `0.2.0`、项目主页 `https://github.com/HenryZ838978/deepseek-harness`、说明为 DeepSeek V4-Pro/V4-Flash protocol-aware client。它与本报告核验的 TypeScript monorepo `deepseek-ai/deepseek-harness` 完全不同。

**阻断动作：** 删除/重建实验 venv 或改用独立 Node workspace；启动时记录 `git rev-parse HEAD`、lockfile hash、所有 adapter 版本。不要在现有 Python venv 上“就地补包”后假定行为一致。

---

## 2. DeepSeek Harness 精确接口核验

### 2.1 `agent/request` 能否改 provider/model/reasoning effort？——可以，且是逐调用 waterfall

**[代码事实]** [`LlmCallConfig`](https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/packages/llm/llm/src/call-config.ts#L18-L30) 明确定义 `provider`、`model`、可选 `reasoningEffort/temperature/maxTokens/stop`。[`agent/request`](https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/packages/core/agent/src/runtime-types.ts#L233-L244) 是 waterfall：listener 等待 `next()` 得到当前配置后返回替换配置。Agent loop 在每次实际 stream 前调用它，并检查 provider/model、准备精确 adapter call、写入 request header（[`agent.ts`](https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/packages/core/agent-loop/src/agent.ts#L417-L470)）。官方文档也明确说可以替换 provider、model、reasoning effort 和 sampling（[`llm-streaming.md`](https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/docs/subsystems/llm-streaming.md#L589-L597)）。

**边界：**

- listener payload 只有 `agent, turn, step, signal`，不会直接给完整 history；Router 要从 `agent.session.events` 编译状态。
- waterfall 替换 call config，不允许原地改 messages；到 `llm/stream` 的请求 deep-frozen。
- unsupported explicit reasoning-effort 会被 adapter preparation 拒绝，不会自动 clamp。

**[推断]** 可将 Router 安装为高优先级 `agent/request` listener；当前 commitment 未触发时返回 held route，触发时才调用 Router。

### 2.2 `agent/request-error` 是否适合 fallback？——适合作为触发器，不是原子“返回备用模型”API

**[代码事实]** [`agent/request-error`](https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/packages/core/agent/src/runtime-types.ts#L245-L260) 接收失败 provider、结构化 failure、该次调用捕获的 retry policy，只能返回 `{kind:'retry'}` 或不处理。当前 loop 在同一 `turn, step` 的 `while(true)` 中，失败后若 retry 就重新执行 `buildRequest()`，从而再次触发 `agent/request`（[`agent.ts`](https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/packages/core/agent-loop/src/agent.ts#L339-L370)）。测试用第一次 `mock`、后续 `other` 的 request listener 得到 `['mock','other','other']`，证明跨 provider fallback 可组合实现（[`retry.spec.ts`](https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/packages/llm/llm-retry/tests/retry.spec.ts#L531-L573)）。

**需要的实现：** `request-error` 写入 attempt ledger 并设置 `fallback_pending`; 下一次 `agent/request` 根据该标记选备用 deployment。必须限制总 attempts、同一 failure code 的 budgets，并把 fallback 当作一次 switch。

**文档/代码不一致：** `llm-retry` README 声称每次 retry 打开 fresh numbered turn，并关闭失败 turn（[`README`](https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/packages/llm/llm-retry/README.md#L5-L13)）；固定 commit 的 `agent.ts` 实际在同一 step 内循环，并且 `llm/retry-started` 也记录原 turn/step。实验应以代码和事件日志为准，启动单测断言坐标；不要依赖 README 的 “fresh turn” 表述。

**计费语义：** 每次 retry 都是新 provider request，可能重复 input billing；前缀仅“有资格”按 provider 规则命中 cache（[`llm-retry README`](https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/packages/llm/llm-retry/README.md#L37-L45)）。

### 2.3 Session event 是否 append-only？——是；通知是 post-commit，不是事务回调

**[文档事实]** 官方把 Session 定义为 append-only typed `SessionEvent` log，history/state 均为派生视图（[`session.md`](https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/docs/subsystems/session.md#L5-L11)）。

**[代码事实]** 构造 seed 必须 lossless JSON、seq 从 0 连续，并逐条通过与 append 相同的状态转移验证；event/data deep-frozen（[`session index.ts`](https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/packages/core/session/src/index.ts#L482-L547)）。`events` 返回缓存的 immutable snapshot（[同文件](https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/packages/core/session/src/index.ts#L550-L566)），`append()` 在 commit 后发布 `session/event`；listener 抛错不会回滚日志。

**[推断]** Counterfactual runner 应直接订阅 canonical `session/event` 作为可重放事实流，但自己的实验索引/usage ledger 必须另存数据库，因为 fire-and-forget telemetry 不是 exactly-once durable writer。

### 2.4 fork/replay 恢复什么？——事件前缀；不恢复外部世界

**[代码/文档事实]** `fork(source,boundary)` 深拷贝 inclusive boundary 前缀，继承 `cwd`、写入 parent/seedLength，且 boundary 不得落在 open turn 内（[`session.md`](https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/docs/subsystems/session.md#L536-L538)，[`session index.ts`](https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/packages/core/session/src/index.ts#L1066-L1137)）。Agent seed 还要求 completed-turn balanced prefix、无 open step 和 dangling tool call（[`agent index.ts`](https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/packages/core/agent/src/index.ts#L103-L109)）。

**[推断，重要]** 源码只复制 event data 与元数据，`cwd` 只是路径字符串；因此不会自动恢复：工作区字节/权限/untracked files、进程和端口、数据库/队列、浏览器/应用 session、外部 API 副作用、环境变量变化、时钟和 RNG、provider KV cache 或 server-side conversation。same-state fork 必须在 stable boundary 同时创建 Harness checkpoint 与 WorldSnapshot；任一失败则整个 checkpoint 无效。

### 2.5 TokenUsage 精确字段与陷阱

**[代码事实]** [`TokenUsage`](https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/packages/llm/llm/src/types.ts#L127-L141) 包含：

| 字段 | 语义 | 成本使用方式 |
|---|---|---|
| `inputTokens` | **未缓存**输入 token | 乘普通 input 价 |
| `cacheReadTokens` | cache read 输入 | 乘 cache-read 价 |
| `cacheWriteTokens` | cache write 输入 | 乘 cache-write 价 |
| `outputTokens` | 全部输出 | 乘 output 价 |
| `reasoningTokens` | output 的子集 | **不得再加到 output**；只作分析或 provider 特殊账单字段 |

总 billed input token 数为 `input + cacheRead + cacheWrite`。Token meter 的 durable projection 记录前四桶，reasoning 仍是 output subdivision；失败调用在失败前已发出的 usage chunk 仍被计量，成功 assistant usage 会替换同 `(turn,step)` sample 以免重复（[`token-meter README`](https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/packages/llm/token-meter/README.md#L20-L34)）。

**Adapter 覆盖差异：** DeepSeek adapter 把 `prompt_tokens - cache_hit` 映射到 uncached input，给 cache-read/reasoning，但官方 API无 cache-write 指标（[`translate.ts`](https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/packages/llm/llm-deepseek/src/translate.ts#L49-L61)，[`README`](https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/packages/llm/llm-deepseek/README.md#L69-L73)）；Pi-AI 可给 cache read/write，但其统一层不总能区分 reasoning。**因此“schema 有字段”不等于所有 provider 可观测。**

**未提供：** 核心 TokenUsage 没有美元价格、工具费用、能源、网络字节、模型加载/驻留、queue/batching、重试标签。必须按 request header + adapter/provider pricing 外接 ledger。

### 2.6 provider-private replay state 能否跨模型/adapter？

| 迁移 | 代码结论 | RouteCraft 处理 |
|---|---|---|
| 跨 adapter instance | **不能。** Core 在历史 provider 与目标 provider 不由同一个 adapter instance 拥有时剥离 replayState（[`llm index.ts`](https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/packages/llm/llm/src/index.ts#L822-L836)）。 | 必须走 provider-neutral transcript replay；记 `private_state_lost=1`。 |
| 同 adapter、跨 model/provider | **可能交给 adapter，但不保证可用。** 官方明确 adapter 验证并决定转换（[`llm-streaming.md`](https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/docs/subsystems/llm-streaming.md#L210-L217)）。PiAiAdapter 可恢复 response ids/signatures，再由目标 API 判断复用（[`Pi-AI README`](https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/packages/llm/llm-pi-ai/README.md#L132-L142)）。 | 做三值/概率 profile：portable / reconstructable / unavailable，并按实测 probe 校准。 |
| prompt/KV cache | DeepSeek 文档明确换 provider 或 model 选择不同 cache domain（[`DeepSeek README`](https://github.com/deepseek-ai/deepseek-harness/blob/47f943859bef60e4160492346772ded9b24f765a/packages/llm/llm-deepseek/README.md#L103-L107)）。 | Switch cost 包括预计 cache hit 差、重新 prefill/context replay；不能从“文本相同”推断 cache 可迁移。 |

失败流只有成功 finish 组装的 replayState 才会进入 assistant message；失败 partial chunks 不进入派生 messages。因此 retry/fallback 恢复的是 canonical surface history，不是失败模型内部隐状态。

---

## 3. vLLM Semantic Router：session-aware agentic routing（SAAR）

### 3.1 已实现的能力

**[文档事实]** 当前官方 session-aware 教程将其定义为：在一个 decision 的 `modelRefs` 中选择完整模型，包装 hybrid 等 base selector，使用 stable `x-session-id` 保存 router-owned memory；tool loop 和 provider-managed continuation state（如 `previous_response_id`）硬锁到上一 physical model；idle timeout/decision drift 允许重选；切换需要支付 prefix-cache、handoff、switch-history 等 penalty；lookup table 可提供 replay-derived remaining-turn prior（[官方教程固定 commit](https://github.com/vllm-project/semantic-router/blob/ef9e5dd99c953a21d20a99a93547e57468bae863/website/versioned_docs/version-v0.3/tutorials/algorithm/selection/session-aware.md)）。

**[代码事实]** 默认配置包括 idle 300s、min turns 1、switch margin 0.05、stay bias 0.10、tool/context hard lock、prefix cache weight 0.20、handoff weight 1.0、switch history 0.04、remaining-turn horizon 8（[`session_aware.go`](https://github.com/vllm-project/semantic-router/blob/ef9e5dd99c953a21d20a99a93547e57468bae863/src/semantic-router/pkg/selection/session_aware.go#L15-L61)）。选择器每次请求先跑 base selector，检查 current/idle/drift/hard lock，再对 candidate 调整 score（[同文件](https://github.com/vllm-project/semantic-router/blob/ef9e5dd99c953a21d20a99a93547e57468bae863/src/semantic-router/pkg/selection/session_aware.go#L161-L210)）；switch score 显式减去 handoff、prefix、tool-loop、switch-history 和 margin（[`session_aware_scoring.go`](https://github.com/vllm-project/semantic-router/blob/ef9e5dd99c953a21d20a99a93547e57468bae863/src/semantic-router/pkg/selection/session_aware_scoring.go#L79-L130)）。

Router memory 记录 current model、turn/switch count、各模型 turns、prompt/cached/cache-write/completion tokens、累计 cost 与 estimated cache savings、active tool loop、last policy（[`router_memory.go`](https://github.com/vllm-project/semantic-router/blob/ef9e5dd99c953a21d20a99a93547e57468bae863/src/semantic-router/pkg/sessiontelemetry/router_memory.go#L24-L88)）；每 turn cost 可使用普通 prompt、cached input、cache write、completion 的独立价格（[`telemetry.go`](https://github.com/vllm-project/semantic-router/blob/ef9e5dd99c953a21d20a99a93547e57468bae863/src/semantic-router/pkg/sessiontelemetry/telemetry.go#L124-L159)，[cost function](https://github.com/vllm-project/semantic-router/blob/ef9e5dd99c953a21d20a99a93547e57468bae863/src/semantic-router/pkg/sessiontelemetry/telemetry.go#L337-L347)）。

### 3.2 作者报告结果与限制

**[文档事实/作者报告]** 2026-06-02 官方 blog 报告在 21,600 个 deterministic synthetic turns 上，完整 SAAR 相对 single-turn routing 减少 79.29% switches、把 3,836 个 unsafe switch 降至 0、估算 physical-model cost 降 78.71%；2,896 个 live ROCm requests 上无 lock violation，并报告 selector p95 overhead（balanced 约 6.181ms、stateful 约 26.805ms）（[官方 blog](https://vllm-project.github.io/2026/06/02/session-aware-agentic-routing.html)）。

**限制/不可外推：** synthetic task traces 使用模拟 tool observations 和 exact-answer；“cost reduction”是配置价格、usage 与 cache estimate 组合，不等同于 cloud bill、能源或整任务 `cost/success`；模型加载/驻留、跨集群网络、queue/batching tail 的因果贡献未由该 selector 独立识别。blog 的结果只能表述为作者在该评测设置下报告。

### 3.3 与 RouteCraft 的重叠和差异

| 维度 | SAAR | RouteCraft 候选 |
|---|---|---|
| 决策时机 | 每个进入 router 的请求都重算；固定 hard lock/reset/score 决定 stay/switch | 在事件点联合选择 `model + 下一次重新开放路由的 boundary` |
| 时间扩展 | tool/provider-state lock、idle/drift reset 和 continuation prior 产生隐式持续性 | 明确 `next_call / next_observation / verified_milestone / task_terminal` termination predicate |
| 标签/学习 | base selector + lookup tables + 配置权重；remaining-turn prior 可来自 replay | matched same-state `(model,boundary)` counterfactual outcome，学习 boundary value |
| 状态 | HTTP/session/router memory，tool/state portability signals | harness-native PlanIR + external verifier/world snapshot |
| 成本 | prompt/cache-write/cache-read/completion price、estimated cache savings、handoff weights | 要求加入 retry/tool/router/judge/context replay/physical serving cost |

**新颖性警告：** SAAR 已覆盖“session-aware stay/switch + cache/handoff + tool/provider lock”。如果 RouteCraft 学到的 policy 只等价于这些固定规则，或退化为每请求 re-evaluate，它没有独立系统贡献。

---

## 4. OpenSquilla 0.5.3

### 4.1 Router 粒度、输入和控制方式

**[代码事实]** `apply_squilla_router` 是每个 turn 的 pipeline step（[`squilla_router.py`](https://github.com/opensquilla/opensquilla/blob/79d57b2fe63e1f83b364ca2bd022e0cb76081406/src/opensquilla/engine/steps/squilla_router.py#L1305-L1390)）。默认 v4 strategy 使用最近 5 个 routing-history entries、1800 秒窗口（[同文件](https://github.com/opensquilla/opensquilla/blob/79d57b2fe63e1f83b364ca2bd022e0cb76081406/src/opensquilla/engine/steps/squilla_router.py#L90-L99)，[history load](https://github.com/opensquilla/opensquilla/blob/79d57b2fe63e1f83b364ca2bd022e0cb76081406/src/opensquilla/engine/steps/squilla_router.py#L1654-L1684)），并传入当前 semantic/routing message、前一 assistant text/usage、历史 user texts、附件数量等。它还做 image route、long-context capability floor、anti-downgrade/confidence policy、provider mismatch/continuity diagnostic，并能改变 thinking level 与 prompt policy。

**[代码事实] agent-issued control：** 内建 `router_control` tool 只在用户显式请求指定 route 时允许 `set_hold/clear_hold`；hold 默认无 turn cap、idle TTL 600 秒（[`router_control.py`](https://github.com/opensquilla/opensquilla/blob/79d57b2fe63e1f83b364ca2bd022e0cb76081406/src/opensquilla/router_control.py#L17-L48)，[store](https://github.com/opensquilla/opensquilla/blob/79d57b2fe63e1f83b364ca2bd022e0cb76081406/src/opensquilla/router_control.py#L166-L238)）。这是 agent-issued/manual short-lived commitment，但不是从环境反事实学习的 boundary policy。

**Provider-private state：** OpenSquilla 会根据 candidate provider 与最新 native state 选择 keep-provider、portable fallback 或 discard-provider-state，并显式标记 loss risk（[`context_capabilities.py`](https://github.com/opensquilla/opensquilla/blob/79d57b2fe63e1f83b364ca2bd022e0cb76081406/src/opensquilla/provider/context_capabilities.py#L319-L381)）。这再次证明 switch profile 应区分 native vs portable state。

### 4.2 事件、fork/replay 和计量

- **[代码事实] Router decision ledger：** turn 内先 stage proposal，结束时补齐 executed provider/model、ensemble、fallback hops/reason，异步写 SQLite，保留 proposed 与 executed 的差异（[`router_decision_record.py`](https://github.com/opensquilla/opensquilla/blob/79d57b2fe63e1f83b364ca2bd022e0cb76081406/src/opensquilla/engine/steps/router_decision_record.py#L179-L330)）。
- **[代码事实] Physical-call usage ledger：** `UsageEventCompletion/Item` 区分 input/output/reasoning/cache-read/cache-write，provider-billed 与 estimated cost，以 nano-USD 存储，带 execution/call index/provider/model/status/coverage（[`usage_ledger.py`](https://github.com/opensquilla/opensquilla/blob/79d57b2fe63e1f83b364ca2bd022e0cb76081406/src/opensquilla/session/usage_ledger.py#L88-L159)）。`normalize_provider_usage` 优先使用 ensemble member breakdown，否则由 DoneEvent 合成（[`usage_accounting.py`](https://github.com/opensquilla/opensquilla/blob/79d57b2fe63e1f83b364ca2bd022e0cb76081406/src/opensquilla/engine/usage_accounting.py#L765-L855)）。
- **[文档事实] 成本来源：** UI/API 区分 `provider_billed / opensquilla_estimate / mixed / unavailable`；provider bill 仍是真值（[`usage-and-cost.md`](https://github.com/opensquilla/opensquilla/blob/79d57b2fe63e1f83b364ca2bd022e0cb76081406/docs/usage-and-cost.md#L74-L88)）。
- **[代码事实] Session fork：** 可复制完整 transcript、message-prefix 或 through-terminal-turn prefix，继承 model/provider/workspace id，复制 canonical transcript/material refs；prefix fork 不复制旧 compaction summary/context state（[`session/manager.py`](https://github.com/opensquilla/opensquilla/blob/79d57b2fe63e1f83b364ca2bd022e0cb76081406/src/opensquilla/session/manager.py#L1406-L1490)）。
- **[文档事实] Replay：** `opensquilla replay` 只读 decision log 并打印 transcript，**不重新运行 tools**（[`diagnostics-and-replay.md`](https://github.com/opensquilla/opensquilla/blob/79d57b2fe63e1f83b364ca2bd022e0cb76081406/docs/diagnostics-and-replay.md#L50-L60)）。

**[推断]** OpenSquilla fork 比 DeepSeek session fork 多复制部分 workspace/material 元数据，但仍未证明可还原 benchmark 外部 DB、进程/端口和 remote side effects；不能把“session fork”当 world fork。

### 4.3 Agentic Routing 报告的成本口径警告

**[论文事实]** *Agentic Routing: The Harness-Native Data Flywheel*（arXiv:2607.11399v1）提出 step-level full harness-state routing、LightGBM cold-start ranker，并在 PinchBench/DRACO 报告与固定强模型相比约 90%/43% billed-cost reduction。论文方法部分承认 Router 自身成本/延迟应在 trade-off 中，但实验表格只把 cost 注为“average billed cost per task”，token 为 input+output。

**[推断]** 论文公开表格没有单列本地 LightGBM CPU、offline profile/training、tool、cache loss、failed retry、context replay、energy；因此其“成本降低”不能直接作为 RouteCraft 完整成本模型已经验证的证据。应将其作为 step-level/harness-native 最近工作，而不是证明自适应 boundary 必然有效。

---

## 5. 其他框架的最小对照（非完整审计）

| 框架 | 已核验能力 | 不能假定的能力 | RouteCraft 用途 |
|---|---|---|---|
| LangGraph 1.2.11 | 官方 persistence 保存每 super-step checkpoint；time travel 可从 checkpoint replay，或用 `update_state` 创建 fork；checkpoint 后的 LLM/API/interrupt 会重执行（[官方 time-travel](https://docs.langchain.com/oss/python/langgraph/use-time-travel)，[persistence](https://docs.langchain.com/oss/python/langgraph/persistence)）。 | Checkpoint 不自动回滚节点外的 DB/HTTP side effects；它是 graph state，不是完整世界快照。未完成逐调用 cache/cost schema 源码审计。 | 第二 harness 候选：状态边界天然明确，但 model routing 常映射到 node/workflow，需避免改变 graph。 |
| OpenAI Agents SDK Python 0.21.1 | `RunConfig` 可按 run 覆盖 model/provider/model settings；Session 保存跨 run history；usage 聚合所有 model calls，并提供 per-request entries、cached input、reasoning output（[running](https://openai.github.io/openai-agents-python/running_agents/)，[sessions](https://openai.github.io/openai-agents-python/sessions/)，[usage](https://openai.github.io/openai-agents-python/usage/)）。 | Session 支持 `pop_item/clear`，不是 append-only；未核验内部每次 call 都有动态 model waterfall；没有证据表明 session 恢复外部工具世界；官方 usage 页面未列 cache-write/tool dollar cost。 | 做 portability 对照较轻，但不如 DeepSeek 适合不改 loop 的 per-call router。 |

**[未核验]** AutoGen、CrewAI、PydanticAI、Agent Lightning、ResearchHarness/agent-lens 未在本证据流完成固定 commit 源码审计；不得引用本报告宣称其支持完整 session fork 或真实 cost accounting。

---

## 6. 成本、cache、queue/batching 与 tail latency 的实现边界

### 6.1 Harness 可直接记录

- 每 attempt 的 provider/model/reasoning effort 和 `(turn,step)`；
- uncached input、cache read、cache write、output、reasoning（按 adapter 可用性）；
- request-error/retry/fallback、工具 call/result/error、wall-clock spans；
- request header 改变、context replacement/compaction、session event bytes；
- verifier outcome 和 task terminal success。

### 6.2 Harness 不能单独归因

- 物理 KV blocks 是否命中/何时 eviction；
- GPU model load/residency、显存竞争、抢占；
- scheduler queue、continuous batching 组成、prefill/decode 分解、network/tail；
- provider-private cache/response-state 的真实节省；
- remote provider 的能耗。

若本地模型由 vLLM serving，官方 `/metrics` 已提供 `num_requests_running/waiting`、KV-cache usage/prefix hit、queue/prefill/decode/e2e/TTFT/ITL；新 per-request metrics 可直接返回 queue/TTFT/decode（[vLLM Production Metrics](https://docs.vllm.ai/en/latest/usage/metrics/)，[Per-request Metrics](https://docs.vllm.ai/en/latest/features/per_request_metrics/)）。**[推断]** 每个 branch 必须带唯一 request id，并把 provider gateway/vLLM span join 到 Harness attempt；不能用全局 Prometheus histogram 给某个 switch 做局部归因。

### 6.3 推荐任务成本 ledger

除用户给出的扩展式外，建议再拆开：

\[
C_{task}=C_{fixed\ ingest}/N + \sum_a(C^{uncached-in}_a+C^{cache-read}_a+C^{cache-write}_a+C^{out}_a+C^{tool}_a+C^{router}_a+C^{judge}_a+C^{network}_a+C^{energy}_a) + C_{failure-recovery}+C_{switch-state-loss}.
\]

其中 `a` 是**物理 provider attempt**，不能只按成功 assistant message；`failure-recovery` 另报 wasted token/latency，避免被成功 continuation 掩盖；`switch-state-loss` 用 matched stay/switch 分支的额外 prefill、cache hit delta、handoff failure 与 load/queue delta估计，避免仅按价格表臆算。主指标为 `sum task cost / # successful tasks`，并同时报未成功任务的 sunk cost。

---

## 7. Benchmark world snapshot 需求

| Benchmark | Harness fork 之外必须保存 | 推荐恢复方式 | 关键偏差/验证 |
|---|---|---|---|
| SWE-bench Verified | 固定 instance image digest、`/testbed` 全部 tracked/untracked/ignored 文件及权限/symlink、当前 HEAD/index、已安装环境、环境变量；若 fork 点有服务/daemon，需显式重启配方和端口状态 | 每 state 制作只读 OCI lower layer + 每 branch 独立 CoW container/volume；或完整 workspace tar/overlay snapshot。禁止多个分支共享 writable worktree。 | 官方任务以 `base_commit`/instance image 和 Docker verifier 为基底（[官方仓库](https://github.com/SWE-bench/SWE-bench/tree/187897a2d730faae089ff77bae7ff18ec7f8bac8)）。只保存 `git diff` 会漏 untracked、生成物、依赖和进程状态。每 fork 前后 hash file manifest，记录测试顺序/timeout/exit code。 |
| τ²-Bench | assistant 与 user 两套 DB、initialization data/actions、完整 message/tool history、task/user-simulator状态、domain policy、RNG/seed、clock；telecom 的双方 tools 会同步共享动态状态 | 当前 `Environment.set_state` 可从 initialization data/actions + message history 重放**会改变状态的 tool calls**，并在 strict 模式比较重放输出（[`environment.py`](https://github.com/sierra-research/tau2-bench/blob/c3398666e6559e3a063da3fc04b5acf7f941464e/src/tau2/environment/environment.py#L207-L319)）；每 branch 新建 Environment，并复制 user simulator transcript/seed。 | `set_state` 跳过 non-mutating calls，并假设 mutating tool replay deterministic；外部时间/随机/LLM user 输出仍需固定或重复。相同 env state 不保证相同 user continuation。保存 DB hash、tool outputs 和 communication state。 |
| AppWorld | 9 个 app 的数据库 state、任务的初始 date/time、API call log、output directory、supervisor/complete-task 状态；任何额外文件/进程 | 官方 `world.save_state()` / `world.load_state(state_id)` 作为 DB checkpoint；每 branch 独立 `AppWorld`/output dir，并复制 state id 对应 DB delta（[官方 README](https://github.com/StonyBrookNLP/appworld/blob/a072b7a86e7c1d5b1d7175659d750ebb9b79f10a/README.md#L210-L260)）。 | AppWorld 官方警告任意回滚在真实世界不可行；研究中必须标为 counterfactual benchmark，不与无回滚 agent leaderboard 直接比较。验证 state-based unit tests、DB hash 和 collateral-damage assertions。 |

**共同原则：** checkpoint 需要 `{harness_event_prefix_hash, world_snapshot_hash, benchmark/version/image digest, clock/RNG policy, open-resource manifest}`；same-state fork 只有五者一致才可进入训练集。

---

## 8. 薄 `HarnessAdapter` 与最小目录映射

### 8.1 建议接口

```text
HarnessAdapter
  attach(session) -> canonical event subscription
  state_at(stable_boundary) -> HarnessCheckpoint(event_prefix, header, cwd, hashes)
  fork(checkpoint, child_id) -> child session              # 只做 harness
  set_commitment(child, model, provider, effort, beta)
  run_until(child, beta | exception | timeout | safety)
  attempts(child) -> per-physical-call usage/retry/latency records
  cancel_and_drain(child)

WorldAdapter
  snapshot(task, boundary) -> WorldSnapshot
  clone(snapshot, branch_id) -> isolated world
  verify_clone(snapshot, clone) -> hashes/assertions
  terminal_verify(clone) -> success/progress/failure_type
```

DeepSeek 实现：`agent/request` listener 读取 commitment store；`agent/request-error` 记录 failure 并触发 emergency break/fallback；`session/event` 编译 PlanIR；只在 closed turn（Phase 0）或显式 tool-observation 后的下一个 stable turn boundary checkpoint。不要 patch core loop。

### 8.2 请求的目录职责

```text
adapters/
  deepseek_harness.ts       # 固定 47f943... 的窄接口，含版本断言
  second_harness.py         # 首选 LangGraph 或冻结 OpenSquilla direct-mode
state_ir/
  event_compiler.*          # 纯确定性系统字段；语义字段单独带 provenance/confidence
world_snapshot/
  swe_container.*           # OCI/CoW workspace
  tau2_replay.*              # initialization + message replay + DB hash
  appworld_checkpoint.*      # save/load_state + output-dir isolation
counterfactual_runner/
  matched_fork.*            # 原子 harness+world checkpoint、branch randomization
verifiers/
  swe_tests.*  tau2_assertions.*  appworld_state_tests.*
model_profiler/
  deployment_profile.*      # 能力/价格/延迟/state/cache compatibility matrix
routers/
  commitment_store.*        # (model,beta), emergency interrupts, fallback budget
benchmark_and_analysis/
  attempt_ledger.*          # token/cache/retry/tool/switch/queue/energy
  paired_stats.*
```

### 8.3 为什么固定 commit、薄 adapter、第二 harness 都必要

- DeepSeek rc API 变化快，且本地已有同名包冲突；固定 commit 和 startup invariant 可防 silent semantic drift。
- 薄 adapter 只映射 event/request/fork/usage，不改 agent planning/tools/workflow，才能检验“routing”而非“重写 agent”。
- 第二 harness 必须验证 PlanIR/β 不是 DeepSeek event taxonomy 的人工特征。Phase 0 可暂缓；完整论文至少在一种不同 checkpoint/event 语义的 harness 上复现。若用 OpenSquilla，必须 `router disabled/direct model`、禁用 prompt/thinking/ensemble 改写，只把它当执行 substrate；若无法做到，改用 LangGraph 固定 graph。

---

## 9. 实现风险与立即停止条件

### 高优先级 blocker

1. **包身份 blocker（已关闭）：** 本地现为官方固定 commit；安装、build、相关测试与 Web smoke 均通过。
2. **snapshot blocker：** DeepSeek/OpenSquilla session fork 都不是完整 benchmark world fork。
3. **state portability blocker：** provider-private replay state 和 KV cache 不可普遍跨 deployment；switch 成本需要 profile matrix 与实测。
4. **attempt attribution blocker：** 失败 usage、重试和 ensemble member 必须按物理 call 入账；只读 assistant final usage 会低估成本。
5. **SAAR novelty blocker：** session-aware stay/switch、hard locks、cache/handoff penalty 已有开源实现。

### 一周内最小系统证伪

在 20–30 个 SWE 与 20–30 个 τ² task 上，仅取 50–100 个稳定、可恢复边界；两个模型；比较 task-pin、每 call、`next_observation` 三类（`verified_milestone/task_terminal` 暂由规则）。每 state 做 stay/switch matched fork，join provider/vLLM request metrics。若在扣除重复 prefill/cache loss/retry/queue 后：

- 可选择状态的净收益分布集中在 0，或
- `next_observation` 固定规则获得 ≥95% dynamic oracle gain，或
- world clone/hash 失败率 >2% / 同一分支 verifier label 在 3 repeats 中一致率 <90%，

则不要建设大 Router；转为 snapshot-aware agent routing measurement/benchmark。

### 最终可行性判断

**系统实现：GO（有前置修正）**。DeepSeek 官方接口足以无侵入实现逐调用模型替换、错误 fallback、事件状态编译与 token/cache 计量；τ²/AppWorld 已提供较强 state reconstruction/checkpoint primitive；SWE 可用 container CoW。**研究新颖性：REVISE**。必须将主张收窄为“verifier-grounded matched counterfactual learning of temporally extended commitment boundary under measured state/cache/switch costs”，并以 SAAR/OpenSquilla 为强 baseline/反例。若只有 stay/switch heuristic 或每 turn router，则已有工作基本覆盖。

---

## 10. 本地 PDF 与 SHA256

目录：`RESEARCH_WORKSPACE\papers\03_harness_systems`

| 文件 | 来源 | SHA256 | bytes |
|---|---|---|---:|
| `Agentic_Routing_Harness_Native_Data_Flywheel_arXiv2607.11399v1.pdf` | [arXiv:2607.11399](https://arxiv.org/abs/2607.11399) | `D3C2A6969790EBA66FFF276B7F7FF9ED2482770852B547AD1BE2C19027AFE540` | 2,358,971 |
| `vLLM_Semantic_Router_arXiv2603.04444.pdf` | [arXiv:2603.04444](https://arxiv.org/abs/2603.04444) | `DD5E435440A28E8C7B8BD5A6E8C8065D6A528B3755E2652B79D06CED15CA398A` | 28,971,129 |
| `vLLM_WRP_Vision_arXiv2603.21354.pdf` | [arXiv:2603.21354](https://arxiv.org/abs/2603.21354) | `F8FEA49709EC0A8CCEAE977D45B95BA84ABDA182B255D35FCD71F6FE8D9E5AAC` | 1,084,759 |
| `tau2_bench_arXiv2506.07982.pdf` | [arXiv:2506.07982](https://arxiv.org/abs/2506.07982) | `0817E3FD33915326180D548CAA900DCC5CBA42DED27688105D8CE2F7E73AAD84` | 1,243,001 |
| `AppWorld_ACL2024.pdf` | [ACL Anthology 2024.acl-long.850](https://aclanthology.org/2024.acl-long.850/) | `6A995817D25CE1C4C5E102DD8C907B3B07E1028F1456F65A0F470BEE98007E36` | 4,347,939 |

备注：DeepSeek Harness 与 OpenSquilla 的关键事实来自固定 commit 官方源码/Markdown 文档，没有公开技术报告 PDF 可替代代码事实；未将网页打印件伪装成论文保存。
