# 证据流 A：完整模型路由与 Agent／多轮模型路由

**检索截止：2026-08-17（Asia/Shanghai）**  
**范围：** 多个完整 LLM 之间的选择；不把 MoE expert、tool/RAG/memory router、动态层跳过或 workflow generation 混称为固定 Agent harness 上的模型路由。本文只用英文论文原文、正式 proceedings／OpenReview、作者项目页和官方代码仓库。作者报告的结果只在其原评测条件下陈述。

## 0. 结论先行：对 RouteCraft 的证据含义

1. **现有决策粒度覆盖已经很宽。** prompt-only（FrugalGPT、RouteLLM、SCOPE、R²-Router）、task/session pinning（TRACE-Router、Agent-as-a-Router）、固定 (K) 后升级（SWE-Router）、每 turn/call（MTRouter、Budget-Aware、TwinRouterBench、Harness-Native）、workflow node/stage（GraphPlanner、EASy、Aragog）均已有明确先例。
2. **最接近但尚未等同的空位**是：在固定、不可改写的原 Agent workflow 内，把“完整模型 (m)”与“下一次重新开放路由的可验证终止边界 \(\beta\)”作为联合动作；候选边界不只 stop/continue，而是 `next_call / next_observation / verified_milestone / task_terminal`。在本证据流核验的论文中，重新决策时机通常是固定协议或固定超参数，而不是可学习的多值动作。
3. **禁止的强新颖性表述：**不能声称 first trajectory-aware、first history-aware、first stage-level、first harness-native、first per-step Agent router、first joint routing-and-termination。MTRouter、Harness-Native、TwinRouterBench、HyDRA、SWE-Router、Iterative Critique Controller 分别直接否定这些表述。
4. **最危险的新颖性冲突：**Iterative Critique Controller 已在每轮联合输出“下一模型 + stop/continue”；HyDRA 已以 session sticky 和 compaction event 平衡 cache 与需求漂移；Harness-Native 已把 recovery、verification、artifact、tool history 等 harness state 用于逐步路由；TwinRouterBench 已把 cache-read/write/miss 和逐调用 live routing 放进 benchmark。RouteCraft 的新意必须收窄到**多值、可验证、temporally extended commitment boundary 的选择及其净系统价值测量**。
5. **主要反例：**TRACE-Router 的 task pinning、Budget-Aware 的 First-Large、HyDRA 的生产 sticky session 都表明，延迟奖励、cache 折扣和 per-step 信用分配可能使固定粒度接近或优于细粒度动态路由。RouteCraft 必须先证明扣除 router/cache/handoff/重读后，动态 boundary oracle 对 task pinning 和最佳固定 boundary 仍有显著空间。

以下使用：**[事实]**=论文或官方仓库明示；**[判断]**=本调研推断；**未核验**=截至截止日没有可访问的一手材料足以确认。

## 1. 发表状态、来源与官方代码总表

| 工作 | 作者（首要作者，完整作者见论文） | 截止日状态 | 论文／正式页 | 官方代码或项目 | 本地 PDF |
|---|---|---|---|---|---|
| FrugalGPT (2024) | Lingjiao Chen, Matei Zaharia, James Zou | TMLR 2024 | [OpenReview](https://openreview.net/forum?id=cSimKw5p6R), [arXiv](https://arxiv.org/abs/2305.05176) | [GitHub](https://github.com/stanford-futuredata/Frugalgpt) | `papers/01_model_routing/2024_FrugalGPT.pdf` |
| RouteLLM (2025) | Isaac Ong et al. | ICLR 2025 conference paper | [OpenReview](https://openreview.net/forum?id=8sSqNntaMr), [arXiv](https://arxiv.org/abs/2406.18665) | [GitHub](https://github.com/lm-sys/RouteLLM) | `papers/01_model_routing/2025_RouteLLM.pdf` |
| LLMRouterBench (2026) | Hao Li et al. | Findings of ACL 2026 | [ACL Anthology](https://aclanthology.org/2026.findings-acl.1881/), [arXiv](https://arxiv.org/abs/2601.07206) | [GitHub](https://github.com/ynulihao/LLMRouterBench) | `papers/01_model_routing/2026_LLMRouterBench.pdf` |
| Models Under SCOPE (2026) | Qi Cao et al. | arXiv preprint | [arXiv](https://arxiv.org/abs/2601.22323), [project](https://sullivan07043.github.io/SCOPE/) | 官方代码未核验；项目页写 future release | `papers/01_model_routing/2026_Models_Under_SCOPE.pdf` |
| HyDRA (2026) | Aashna Garg et al. | arXiv preprint | [arXiv](https://arxiv.org/abs/2605.17106) | 官方代码未核验 | `papers/01_model_routing/2026_HyDRA.pdf` |
| Router-R1 (2025) | Haozhen Zhang, Tao Feng, Jiaxuan You | NeurIPS 2025 poster | [arXiv](https://arxiv.org/abs/2506.09033) | [GitHub](https://github.com/ulab-uiuc/Router-R1) | `papers/01_model_routing/2025_Router_R1.pdf` |
| R²-Router (2026) | Jiaqi Xue, Qian Lou, Jiarong Xing, Heng Huang | ICML 2026 / PMLR Vol. 306 | [arXiv](https://arxiv.org/abs/2602.02823), [ICML downloads](https://icml.cc/Downloads/2026) | [GitHub](https://github.com/UCF-ML-Research/R2-Router) | `papers/01_model_routing/2026_R2_Router.pdf` |
| MTRouter (2026) | Yiqun Zhang et al. | ACL 2026 long paper | [ACL Anthology](https://aclanthology.org/2026.acl-long.2045/), [arXiv](https://arxiv.org/abs/2604.23530) | [GitHub](https://github.com/ZhangYiqun018/MTRouter) | `papers/02_agent_routing/2026_MTRouter.pdf` |
| TRACE-Router (2026) | Ritik Raj et al. | arXiv preprint | [arXiv](https://arxiv.org/abs/2607.22465) | 官方代码未核验 | `papers/02_agent_routing/2026_TRACE_Router.pdf` |
| SWE-Router (2026) | Seongho Son et al. | ICML 2026, 5th Deep Learning for Code workshop；非 ICML 主会 | [arXiv](https://arxiv.org/abs/2607.00053) | [official Hugging Face org](https://huggingface.co/SWE-Router)；源码仓库未核验 | `papers/02_agent_routing/2026_SWE_Router.pdf` |
| TwinRouterBench (2026) | Pei Yang et al. | arXiv preprint | [arXiv](https://arxiv.org/abs/2605.18859) | [GitHub](https://github.com/CommonstackAI/TwinRouterBench) | `papers/02_agent_routing/2026_TwinRouterBench.pdf` |
| Agentic Routing: The Harness-Native Data Flywheel (2026) | TokenRhythm Technologies | arXiv technical report / preprint | [arXiv](https://arxiv.org/abs/2607.11399) | [OpenSquilla GitHub](https://github.com/opensquilla/opensquilla) | `papers/02_agent_routing/2026_Agentic_Routing_Harness_Native.pdf` |
| Budget-Aware Agentic Routing (2026) | Caiqi Zhang et al. | arXiv preprint | [arXiv](https://arxiv.org/abs/2602.21227) | 官方代码未核验 | `papers/02_agent_routing/2026_Budget_Aware_Agentic_Routing.pdf` |
| EASy (2026) | Junnan Liu et al. | preprint, under review | [arXiv](https://arxiv.org/abs/2608.04588) | 官方代码未核验 | `papers/02_agent_routing/2026_EASy.pdf` |
| GraphPlanner (2026) | Tao Feng et al. | ICLR 2026 conference paper | [OpenReview](https://openreview.net/forum?id=ZdGB7MNQDT), [arXiv](https://arxiv.org/abs/2604.23626) | [GitHub](https://github.com/ulab-uiuc/GraphPlanner) | `papers/02_agent_routing/2026_GraphPlanner.pdf` |
| Iterative Critique-and-Routing Controller (2026) | Wenzhi Fang et al. | arXiv preprint；正式录用未核验 | [arXiv](https://arxiv.org/abs/2605.08686) | 官方代码未核验 | `papers/02_agent_routing/2026_Iterative_Critique_Routing.pdf` |
| Agent-as-a-Router (2026) | Pengfei Zhou et al. | arXiv preprint | [arXiv](https://arxiv.org/abs/2606.22902), [project](https://omnisource.cn/agent-as-a-router) | [GitHub](https://github.com/LanceZPF/agent-as-a-router) | `papers/02_agent_routing/2026_Agent_as_a_Router.pdf` |
| Aragog (2025, 邻近系统) | Yinwei Dai et al. | arXiv preprint | [arXiv](https://arxiv.org/abs/2511.20975), [official lab page](https://nexs.scs.gatech.edu/publications/2025-aragog.html) | 官方代码未核验 | `papers/02_agent_routing/2025_Aragog.pdf` |
| AgentRouter (2026, 补查项) | Rudrendu Kumar Paul, Sourav Nandy | ICML 2026 AdaptFM workshop 元数据可见；正文访问受限，非主会 | [OpenReview forum](https://openreview.net/forum?id=nu3GPfkyJV), [workshop program](https://icml.cc/virtual/2026/75165) | 官方代码未核验 | **未保存：OpenReview 于执行日返回 403；方法细节未完全核验** |

> 注：EASy 的 arXiv 编号在截止日前可用且 PDF 明示 “Preprint. Under review”；不得写成已录用。AgentRouter 因官方 PDF 无法访问，本笔记不采用搜索摘要中的结果数字。

## 2. 粒度与系统边界总览

| 路线 | 代表工作 | 是否任务内切换 | Router 看到的增量信息 | 重新决策时机是否为决策变量 |
|---|---|---:|---|---:|
| Prompt-level 一次选择 | RouteLLM, SCOPE, R²-Router | 否 | 原始 query；有时模型 profile | 否 |
| Prompt-level cascade | FrugalGPT | 是（同一问答内级联） | 前一候选 answer 与置信度 | 仅 accept/escalate；无 Agent event |
| Task/session pinning | TRACE-Router, Agent-as-a-Router | 否（单任务内） | admission context；前序任务 feedback 可影响未来任务 | 固定为 task terminal |
| 固定 (K) 探索后升级 | SWE-Router | 最多一次 | cheap-agent trajectory | (K) 是超参数；仅 continue weak / restart strong |
| 每 turn / 每 LLM call | MTRouter, Budget-Aware, TwinRouterBench, Harness-Native | 是 | history、budget、harness state 或 prefix | 固定 next turn/call |
| 输出 refinement 的逐轮控制 | Iterative Critique Controller | 是 | query、draft、critique history | 联合 next model + **任务 stop**；继续后仍逐 turn 重路由 |
| 多轮子问询与聚合 | Router-R1 | 是 | policy 的自生成 reasoning、候选回答 | 最多若干 route；同时改写解题流程 |
| Session event sticky | HyDRA | 是但很稀疏 | turn-1 / compaction / background summary，7 个系统 flag + 当前消息 | 触发事件固定；不学习开放时间 |
| Workflow node / milestone | GraphPlanner, EASy | 是 | 生成中的 workflow graph / milestone result | 角色、模型与 workflow 联合生成；不是固定 harness |
| 固定 DAG stage + load | Aragog | 是 | 系统负载、queue 等 serving state | stage 边界由 workflow 固定 |

**[判断]**在已核验工作中，只有 Iterative Critique Controller 把一个二值 `stop/continue` 与模型选择联合，但它的 stop 是结束答案 refinement，continue 后仍在下一轮重新路由；没有工作把**下一次路由开放点**作为 `next_call / next_observation / verified_milestone / task_terminal` 这样的多值、temporally extended action。该空位真实存在，但比“adaptive stage routing”窄得多。

## 3. 逐工作证据卡

### 3.1 FrugalGPT

- **[事实｜对象/粒度]**对一次 query 构造最多三 API 的固定序列 cascade；每个候选模型回答后，DistilBERT reliability scorer 决定接受或升级。[论文](https://openreview.net/forum?id=cSimKw5p6R)；[代码](https://github.com/stanford-futuredata/Frugalgpt)。
- **输入/历史/阶段：**query + 当前候选 answer；无 Agent trajectory、tool observation 或 planning/acting/verify/recover 区分。
- **Router/标签/Judge：**监督学习的可靠性评分；标签来自下游数据集 ground truth。无需在线强 Judge。没有未见模型机制；cascade order 和 scorer 均与已知 API 绑定。
- **Workflow：**改变一次问答的调用序列，但不属于 Agent loop。评测 12 个 API，HEADLINES、OVERRULING、COQA。
- **成本：**按当时 API 请求/输入输出价格优化；论文称相同质量最高节省约 98%，或相同成本最高提升约 4 个百分点（2023 年价格/池）。训练 reliability scorer 的数据和资源被承认，但 router 部署、cache、切换、工具、失败恢复、延迟和能耗未进入统一成本。
- **局限/重叠：**标签和分布依赖，模型/价格漂移需重建；answer acceptance 与 RouteCraft 的 termination predicate 形式相似，但没有环境状态或跨 Agent 阶段 commitment，重叠低。

### 3.2 RouteLLM

- **[事实｜对象/粒度]**在 strong/weak 二元池中对 query 一次选择，然后仅调用一个模型。[ICLR paper](https://openreview.net/forum?id=8sSqNntaMr)；[代码](https://github.com/lm-sys/RouteLLM)。
- **输入/历史/阶段：**prompt-only；无历史和 Agent stage。方法包括 similarity-weighted ranking、matrix factorization、BERT classifier、causal LLM classifier。
- **标签/Judge：**主要用约 80K Chatbot Arena 人类偏好；MMLU 可用 gold correctness 扩充；论文还研究 GPT-4 合成偏好（约 120K labels、报告约 $700）。MT-Bench 评测依赖 Judge，MMLU/GSM8K 可规则评测。
- **未见模型：**论文把在 GPT-4/Mixtral 上训练的 router 用到 Claude 3、Llama 3.1 等新 strong/weak pair，显示一定 transfer；但不是显式 candidate-conditioned profile，也不是任意池的 open-set 保证。
- **成本/结果：**论文条件下质量不变可超过 2×、最高约 3.66× cost saving；最昂贵 router 的推理开销估计不超过 GPT-4 generation 成本的 0.4%。主要成本由路由比例×token/API price 得到；未计 cache、重试、Agent 轮次、工具、handoff。
- **局限/重叠：**二元池、prompt OOD/分布漂移，低重叠；是必须的 prompt-only baseline。

### 3.3 LLMRouterBench

- **[事实｜对象/粒度]**统一冻结 `query × model outcome` 的静态 benchmark：超过 400K queries、21 datasets、33 models、10 routing baselines，论文报告约 1.8B token、$2.7K API 和约 1K GPU-hours 的构建规模。[ACL paper](https://aclanthology.org/2026.findings-acl.1881/)；[代码](https://github.com/ynulihao/LLMRouterBench)。
- **Agent 边界：**包含 SWE/tau2 等来源不等于执行 live Agent loop；router 不观察真实中间 event，也不承担任务内切换。
- **标签/Judge/池：**模型回答的 task correctness 或 Judge 结果；20 个轻量模型形成主要性能池，另含 13 个旗舰模型的 cost-sensitive pool。
- **成本：**输入/输出 token×价格；OpenRouter 调用最多重试 10 次，耗尽失败置零；Frugal 类方法最多级联两次。论文还用 OpenRouter TTFT/TPS 近似延迟。没有 prompt cache、Agent 工具、router 训练/在线成本、能耗或真实 handoff。
- **结果/反例：**许多 router 差距小，部分商业/新模型 setting 不如 Best Single；静态 oracle gap 很大但主要来自 recall failure，且 model-pool 构造强烈影响结论。
- **重叠：**不是 Agent Router；适合检验 candidate-conditioned unseen-model，但不能支持 RouteCraft 的 boundary 因果主张。

### 3.4 Models Under SCOPE

- **[事实｜对象/粒度]**Qwen3-4B router 在调用候选前，从 query 和模型 behavioral fingerprint 预测每个模型的 correctness 与 output-token length，再按目标选模型。[论文](https://arxiv.org/abs/2601.22323)；[项目页](https://sullivan07043.github.io/SCOPE/)。
- **profile/未见模型：**每模型约 250 anchor probes 构造 fingerprint；报告 7 seen + 4 unseen models，以及 AIME/HLE/SimpleQA/Olympiad OOD。
- **训练标签/Judge：**两阶段：SFT hindsight distillation 中教师可看到已实现结果/理由；随后 GRPO 对 correctness 和 token error 优化。**[判断]**教师事后理由可能发生 label rationalization/leakage，不能等同可执行能力标签。
- **成本/结果：**论文报告不同 setting 下最高 +25.7 accuracy points 或 95.1% cost reduction；router 平均约 238.7 predicted tokens/model/query，7-model pool 约 1.8K token，对比 test-time-sampling 约 19.2K，并报告新模型适配 compute 下降约 38×。router 的本地 4B 美元/能耗、cache、Agent retry/tool/switch/latency未统一计入。
- **重叠：**candidate-conditioned success/cost prediction和 calibration probe 与 RouteCraft 高重叠；但仍是 prompt-only，没有历史或 boundary。RouteCraft 不能把 candidate-conditioned/unseen-model 支持本身作为主要创新。

### 3.5 HyDRA

- **[事实｜对象/粒度]**149M ModernBERT-base 预测 reasoning/code/debug/tool 需求，再与每模型实测 capability YAML 做 cost-constrained matching。[论文](https://arxiv.org/abs/2605.17106)。输入含当前用户消息（截断 512）和 7 个确定性 flag（turn bin、error、file/URL/command/code/short 等），不读取完整 assistant/tool/repo trajectory。
- **session 策略：**生产默认在首 turn 路由并 sticky；只在 explicit compaction 或 background summarization 等事件重新调用 router，以保留 provider prefix cache（论文举约 90% cache discount）。这已经是**固定 event-driven commitment**。
- **训练标签/Judge：**50,159 个去标识 Copilot turns，每个由两个模型生成，LLM judge 做 position swap；capability profile 来自公开 benchmark 的实测归一化分数。需求预测器不必随加模型重训，但 profile 需要重新跑。
- **pool/结果：**五模型池；SWE-bench Verified、LiveCodeBench、BigCodeBench、tau2。作者报告 SWE 条件下约 54.1% saving 而接近目标质量。生产 A/B 相对 prior router control 的 per-inference-request cost 约 -2.3%，但 aggregate segment COGS 因请求量变化大致持平；7–20% 是相对该 segment 全部使用旗舰模型的估算，不能写成生产 A/B COGS 降幅。offline CPU routing overhead 约 55ms p50、120ms p99；arXiv landing abstract 另报 production median 86ms，口径不同。
- **成本：**实验用 realised input/output token price；cache 是策略动机但 cache-read/write/loss 是否逐请求纳入实验 cost 未清楚披露；router latency 有测量。Judge、profile build、switch、queue、retry/tool/energy 未完整计量。
- **局限/反例：**tool head 标注一致性弱/负 Krippendorff alpha；512 截断、语言不平衡、profile staleness/adversarial inflation。论文把“更自适应的多轮、平衡 cache 与 drift”列为未来方向。
- **重叠：****高危先例。**RouteCraft 相对它的差异只能是学习并联合选择边界、使用可验证 Agent event/PlanIR、测真实 switch/replay；不能声称首次 cache-aware event routing。

### 3.6 Router-R1

- **[事实｜对象/粒度]**约 3B policy 交错生成 reasoning 与 `<search> Candidate LLM: subquery`，可在同一 query 多次调用候选（上限约四次）并聚合。[NeurIPS paper](https://arxiv.org/abs/2506.09033)；[代码](https://github.com/ulab-uiuc/Router-R1)。
- **输入/历史/阶段：**自生成的分解和先前候选回答；不是既有 Agent harness event。PPO reward 含 format、terminal EM/F1 和 cost；约 14K NQ/Hotpot 训练，7 QA datasets、6 candidate models。
- **未见模型：**通过自然语言模型描述可加入两种 unseen candidate 而不重训，属于 descriptor-conditioned 的证据。
- **成本：**cost reward 主要按候选模型 output tokens×price；policy/router 自身 reasoning/input、候选 input、cache、切换、latency 未完整计入。论文承认 multi-round latency。
- **重叠：**联合选择下一候选与是否继续，但同时生成 subquery、聚合并改变解题 workflow；不是固定 Agent 中“保持某模型直到外部边界”。应作邻近序列决策而非直接 baseline。

### 3.7 R²-Router

- **[事实｜对象/粒度]**题名为 *R²-Router: A New Paradigm for LLM Routing with Reasoning*；对一次 query 联合选 model 和 reasoning/output-token budget。[论文](https://arxiv.org/abs/2602.02823)；[代码](https://github.com/UCF-ML-Research/R2-Router)。
- **router/标签：**R²-Bench 覆盖 6 datasets、15 models、每模型约 5–6 budgets；query embedding 后为各 model/budget 训练小 MLP，使用已有结果作为质量/成本标签。Judge（论文采用强模型评估）和 exact-match secondary metric 需按任务区分。
- **未见模型：**原 R² 的 head 与 model/budget 绑定；新模型需收集响应/probe并重训。论文与 UniRouter 组合时才讨论 open-set。
- **成本/结果：**作者报告质量相近时总输入+输出 token cost 可降 4–5×，单 query router 平均 **<400 ms**、约占总 LLM generation time <1%；15 模型训练约 30 分钟单 RTX 3090。未计 Agent loop、cache/switch/tool/retry、部署能耗。
- **重叠：**说明 joint action 比单 utility 合理，但其第二动作是单次生成 budget，不是 temporal re-decision boundary；中等结构重叠。

### 3.8 MTRouter

- **[事实｜对象/粒度]**每个 Agent turn 选择一个完整模型，随后 parser/action/tool observation；使用 Qwen3-Embedding-0.6B 对最长约 8192 tokens 的 recent-first 全历史编码，并与 context/cost/profile 和 learned model-ID 联合。[ACL paper](https://aclanthology.org/2026.acl-long.2045/)；[代码](https://github.com/ZhangYiqun018/MTRouter)。
- **标签/数据：**offline random per-turn 与 single-model trajectories；约 1,291 train instances、29,693 trajectories、515,221 turns，作者报告采集约 $1,620。训练目标以 terminal score 和 progress-weighted downstream error severity 构造 regression target。
- **stage/history：**trajectory-aware，但未显式把 OBSERVE/PLAN/ACT/VERIFY/RECOVER 作为语义状态；tool observation和error已隐含在 raw history。模型 ID residual 使 unseen-model 不自然。
- **评测/结果：**ScienceWorld、HLE tool agent，6 个 frontier models，最多 50/30 turns 和 $2 cap。作者报告 ScienceWorld 53.8 vs always-GPT-5 48.4 且成本低 58.7%；HLE 成本低 43.4%。这些只在论文池/协议成立。
- **成本：**模型 token 美元成本；embedding/router、tool、Jina/Serper、Judge、cache loss、switch/handoff、energy未计。论文明确把跨模型 cache loss 列为 limitation。其策略错误后保持原模型概率很高，表明逐 turn 决策可学成近 sticky。
- **重叠：****最直接 baseline。**状态和模型选择高度重叠；差异是其 reopen 固定每 turn，RouteCraft 必须证明 adaptive commitment 的净收益，而非仅替换 history encoder。

### 3.9 TRACE-Router

- **[事实｜对象/粒度]**任务 admission 时用 regex/coarse task context + contextual UCB 选一次 backend，并用 task ID 在后续 calls pin model；terminal accuracy 与 end-to-end latency 更新 bandit。[论文](https://arxiv.org/abs/2607.22465)。
- **理论动机：**作者认为 Agent 的 supervision 单位是 delayed task outcome；逐 call router 很难信用分配，且会破坏 backend state/cache。因此主张 route once, pin all subsequent calls。
- **评测/结果：**tau2 retail/telecom（各 114）、LiveCodeBench 300、TerminalBench 48；主要 Qwen3.5 4B/9B。patched LiteLLM wall-clock 包含工具/环境等待。作者报告若干设置比 latency-aware mixture 高约 7–8 points；TerminalBench 约 +7.1 points 且 latency 低 36%。样本小，不能外推。
- **成本：**优化 accuracy/latency而非货币/token；没有逐 bucket cache、router overhead、switch、energy。没有未见模型/跨任务 profile机制；workflow不变。
- **重叠/反例：**恰是 `β=task_terminal` baseline，也是 RouteCraft 的核心反例：terminal reward 与 cache 显著时，固定任务可能更优。

### 3.10 SWE-Router

- **[事实｜对象/粒度]**cheap model 先固定执行 (K) 个探索 turns；Qwen2.5-Coder-7B LoRA value head 读 trajectory，预测 cheap agent 是否最终成功；若低则由 strong model 从**原始 issue 重新开始**，不继承 cheap trajectory，以避免 anchoring。[论文](https://arxiv.org/abs/2607.00053)；[模型页](https://huggingface.co/SWE-Router)。
- **pool/标签：**weak 为 GPT-5-mini 或 DeepSeek-V3.2，strong 为 Gemini-3-Pro-preview；mini-swe-agent、最多 75 steps。SWE-Smith/SWE-bench Verified 的 unit tests 给 binary terminal labels；每模型运行约 500，约 1.7K weak trajectories 训练，另有 100 个真正 held-out SWE instances。
- **结果：**作者用 route-AUC 报告相对强 prompt-only baseline 最低约 +12 points；一个 DeepSeek pair 报 0.780、约 +15.3 points。美元表中 GPT-5-mini/DeepSeek/Gemini 全量运行约 $105.4/$130.5/$608.2（按论文协议）。
- **理论限制：**论文的信息单调性 (V(S_t)\ge V(Q)) 只在相同 utility 且忽略获取信息/切换成本时成立；固定 (K) cheap roll-in 是真实付费信息采集，且强模型 restart 重读上下文。
- **成本：**API spend计入两模型运行，但 router inference、cache、重读/失败重试、latency、tool/energy未逐项分解。
- **重叠：****高危固定-K baseline。**它证明中间 trajectory 可突破 prompt Bayes floor，却没有学习边界；RouteCraft 必须优于最佳 (K\in\{1,2,3,4\}) 并把 restart/replay算全。

### 3.11 TwinRouterBench

- **[事实｜对象/粒度]**step-level benchmark：static track 有 970 router-visible prefixes/520 instances，来自 SWE、BFCL、multi-turn RAG、QMSum、Pinch；dynamic track 支持 mini-swe-agent full 500，论文 live 试验使用 100 held-out。[论文](https://arxiv.org/abs/2605.18859)；[代码/数据](https://github.com/CommonstackAI/TwinRouterBench)。
- **标签构造：**11 models/4 cost tiers。由 strong successful seed trajectory 出发，借 Claude Opus hint，然后 greedy sequential-lock downgrade 当前 call；既往 tier锁定、未来使用 strong，只有整条 trajectory仍通过才给低 tier。开放任务使用 LLM judge，执行任务可确定性 verifier；人工抽查 64 steps，63 个被称为 tight。
- **重要因果限制：**static outcome 是“当前 step downgrade + 固定 continuation”的局部 effect，不是全局 joint policy oracle；greedy locking 忽略多步交互，标签与当前 pool/price/protocol绑定。
- **成本/动态结果：**明确记录 input、cache-read、cache-write、output 四类计费；跨模型、TTL 或 prefix mismatch视为 cache miss；dynamic 采用 OpenRouter realised spend，并对 unresolved failure 罚 $0.60。锁定池含 Opus-4.6、Gemini-3-Flash、MiniMax-M2.7、DeepSeek-3.2。论文 100-task live 中 logistic router 75/100、$25.66 vs Opus 74/100、$54.73（约 53.1% cost cut）。
- **遗漏：**没有完整 router training/deployment、tool/energy、queue/P95 latency；开放任务仍依赖 Judge；live sample 仅100。
- **重叠：****极高 benchmark 先例。**same-prefix/common-continuation和 cache 四桶都已出现；RouteCraft 的 matched fork 必须增加完整 world snapshot、model×boundary、随机重复与真正 boundary intervention，不能声称首个 Agent counterfactual routing benchmark。

### 3.12 Agentic Routing: The Harness-Native Data Flywheel

- **[事实｜对象/粒度]**OpenSquilla technical report 将 route action 设为 singleton model 或 model set，并让 router 可条件于 observation、raw/compressed context、control state、actions、artifacts、tool history、recovery、verification 等 harness state。[论文](https://arxiv.org/abs/2607.11399)；[代码](https://github.com/opensquilla/opensquilla)。
- **router/data：**四阶段 admission/demand/risk/capability match；确定性/轻量规则 + LightGBM seed ranker。typed arena record 包含 task/state/slate/demand/action/scores/confidence、后续 verifier/final outcome、realised cost/latency/provenance。报告提出 IPS/DR、uncertainty exploration、replay/oracle 和 staged learned router，但多数是设计蓝图，非同等完成度的实证。
- **评测/结果：**DRACO/PinchBench；模型池含 Opus、GLM、DeepSeek variants。作者报告 PinchBench score 93.14、平均 billed cost $0.0204/task vs fixed Opus score 94.33、$0.1649/task；DRACO score 52.33、$0.3729/task vs Opus 52.36、$0.6559/task。这里的 score 不是已核验的 success 百分比。
- **成本审计：**报告 token/billed cost，部分 ensemble latency；工具、search、Judge、LightGBM训练/CPU、cache loss没有清楚统一进净成本。cache-aware明确列为未来工作。缺少完整置信区间、显著性和 route-level数据规模披露。
- **workflow/未见模型：**framework 能改变 harness config/proposer，但该报告声称隔离 model selection；candidate profile可扩展，真正 unseen-model实验披露有限。
- **重叠：****最大概念冲突。**harness-native state、环境 outcome、realised cost、flywheel均非 RouteCraft 新颖点；差异只能是固定 workflow 下的 adaptive boundary + matched model×boundary fork + switch/cache完整测量。

### 3.13 Budget-Aware Agentic Routing

- **[事实｜对象/粒度]**Qwen2.5-1.5B router 每一步读取完整 interaction history 和 remaining budget，输出 SMALL/LARGE；ReAct harness继续执行。[论文](https://arxiv.org/abs/2602.21227)。
- **训练：**BoSFT 对任务作 easy/hard/intractable taxonomy；always-small/large rollouts（K=5）和 hard tasks 上 N=10/20 trajectories、扫 large-call比例，选 cheapest successful 轨迹。BoPO 用 terminal success-cost 与 reference-guided advantage 做 GRPO。
- **评测：**ScienceWorld、ALFWorld、AppWorld；主池 GPT-4.1-mini/GPT-4.1，另验 Llama 8B/72B；3 seeds。hard budget限制 large calls，超额时回落 small。
- **反例：**严格 hard budget 下，简单 First-Large baseline 仍具竞争力，说明“早用强模型避免后续错误”可能压过复杂 history policy。
- **成本：**输入/输出 list price；论文明确不把 router compute放进主要 frontier，只按吞吐估计 router <0.2s、<2%，并非实测完整E2E。cache、switch、tool、retry、judge、energy和昂贵rollout收集未计。
- **重叠：**trajectory+budget+per-step 二模型路由高度重叠；其 β 固定 `next_call`，是 RouteCraft 必须 baseline。

### 3.14 EASy

- **[事实｜对象/粒度]**7B orchestrator 生成 milestone、DAG和 executor assignment，可并行执行节点、聚合结果并再生成下一 milestone。[论文](https://arxiv.org/abs/2608.04588)（PDF明示 under review）。
- **pool/训练：**基础 executor 实际主要为同一 Qwen2.5-7B 的不同 context/output budgets；还评 GPT-5-mini；unseen配置加入Qwen-14B。RL搜索以 milestone/plan树分支，约7K训练；数学用 CompassVerifier/MathVerify，最多150 steps。
- **评测：**AIME24/25、MATH500、ALFWorld、WebShop、GAIA、HLE；比较 ReAct、AutoGen、Reflexion、PlanAct、AgentFlow、MasRouter 等 workflow。
- **成本：**“efficiency”主要定义为 (1/(1+\ln \#tokens))，没有把 orchestrator/router、verifier、tool、cache、switch、retry、latency/energy拆开成真实美元系统成本。
- **重叠边界：**milestone 是重要 temporal abstraction 先例，但其贡献来自生成/重写workflow和规划器；RouteCraft明确不改workflow，因此不宜当直接可比 baseline，只作邻近工作与“收益是否来自 replanning”的对照。

### 3.15 GraphPlanner

- **[事实｜对象/粒度]**每一步联合选择 agent role（Planner/Executor/Summarizer）和模型，并生成 workflow；GARNet编码历史/workflow graph，PPO训练。[ICLR paper](https://openreview.net/forum?id=ZdGB7MNQDT)；[代码](https://github.com/ulab-uiuc/GraphPlanner)。
- **训练/未见模型：**14 tasks、6 domains、12 models（7B–176B）；text descriptions/profiles支持 unseen task/model。phase 1 在固定 workflow 分配models，phase 2生成workflow。论文报告平均 accuracy phase1 +3.8、phase2 +9.3 points（相对其论文 baselines）。
- **成本：**按 input/output token×估计price；router训练时间/显存有报告，但部署、cache、switch、retry、tool、judge/energy未计。“1.04 GiB”是内存单位，不能写成 GPU compute。
- **重叠边界：**role/model joint action与graph state相关，但 workflow会改变；planner次数/termination仍是固定上限或policy stop，不是保持现模型直到外部事件。邻近而非公平直接baseline。

### 3.16 Iterative Critique-and-Routing Controller

- **[事实｜对象/粒度]**4B/7B controller 每 turn 读取 query + previous draft，输出 critique/verifier判断、stop/continue和下一模型；所选模型根据 query、draft、critique refinement。[论文](https://arxiv.org/abs/2605.08686)。
- **训练：**MDP action 是controller生成文本并解析model/stop；GRPO/composite reward含“所选agent是否能解题”的routing correctness与verification decision correctness，并有利用率Lagrange项。
- **评测/结果：**7 math benchmarks；模型池为Qwen 30/7/1.5或Qwen30/Ministral8/Llama1；作者报告两个setting平均80.5/82.3，对比Router-R1 69.1/66.5，且strong agent调用 <25%。仅在其iterative math workflow成立。
- **成本：**没有美元/token cost frontier；controller、critique、额外轮、latency未计，论文承认 latency overhead。无unseen-model实验。
- **重叠：****最危险结构同构。**已联合“下一模型+termination”；但 stop=答案终止，continue后下一turn必重新路由，且workflow本身是反复改稿。RouteCraft必须把创新定位为**选择未来重开边界而非当前是否停任务**，并在固定Agent工具逻辑中验证。

### 3.17 Agent-as-a-Router

- **[事实｜对象/粒度]**C-A-F（Context–Action–Feedback）是在连续任务流上：对每个coding task选择一个模型、执行完整任务、验证，再把经验写回memory影响未来任务；**单任务内不切换**。[论文](https://arxiv.org/abs/2606.22902)；[项目](https://omnisource.cn/agent-as-a-router)；[代码](https://github.com/LanceZPF/agent-as-a-router)。
- **router/state：**ACRouter以fine-tuned Qwen3.5-0.8B和启发式加权投票结合 DimensionBest performance prior、top-10 memory kNN和task metadata；20K向量store记录model/perf/cost/trace。verifier可用AST、sandbox、self-consistency或Judge。
- **评测：**CodeRouterBench 10,111（约7,080 probing、2,919 ID、176 OOD agentic），8 frontier models；OOD用mini-swe-agent且40 steps，而标准设置可更长。论文报告ID 49.98、OOD 62.5等综合结果，需限定其自定义score/protocol；静态router OOD退化而online memory改善。
- **成本：**backend input/output token×官方价格；self-hosted router按H100吞吐折算约$0.054/M token。作者明确说provider cache不可观测；embedding、verification/sandbox/Judge、tool、失败恢复未清楚合并。
- **重叠：**history/feedback跨任务，而不是单任务trajectory；等价于 `β=task_terminal` 加continual memory。是task-pinning baseline，不覆盖adaptive intra-task boundary。

### 3.18 Aragog（指定清单外但重要）

- **[事实]**固定多stage/DAG agentic workflow上，先为请求找 accuracy-preserving model configurations，再在每个固定stage根据实时load/queue选择配置，逐步适应serving dynamics。[arXiv](https://arxiv.org/abs/2511.20975)；[官方实验室页](https://nexs.scs.gatech.edu/publications/2025-aragog.html)。
- **对象/边界：**模型配置与系统调度；stage boundary由workflow给定，不读开放式Agent语义状态，也不决定何时重开。workflow拓扑固定但每个stage/agent可分配不同模型。
- **结果/成本：**重点是GPU serving throughput/median latency并维持昂贵配置的accuracy，而非API token-price。当前arXiv摘要与下载PDF中的区间数字存在差异（摘要为throughput +50.0–217.0%、median latency -32.5–78.9%；PDF文本为 +42.8–217.0%、-32.5–86.1%），故不在主报告选用具体区间，需引用时先核对版本。
- **重叠：**证明stage-level runtime model scheduling并不新；RouteCraft差异是可变边界、Agent capability-demand state与switch/cache净成本，而非load-aware固定DAG scheduling。

### 3.19 AgentRouter（只能部分核验）

- 官方元数据标题为 *AgentRouter: Heterogeneous Model Routing for Cost-Optimal Multi-Step Agentic Workflows*，作者 Rudrendu Kumar Paul、Sourav Nandy；官方页面指向ICML 2026 AdaptFM workshop，不应写ICML主会。[OpenReview](https://openreview.net/forum?id=nu3GPfkyJV)。
- 执行日官方PDF返回403，无法按一手全文核验其features、50K labels、模型池、成本数字或是否有代码。因此这些细节一律标**未核验**，不据此做结果比较。
- 仅从可核验题名/摘要元数据可把它列为“multi-step workflow中的step级异构模型选择”潜在冲突；在取得正文前，RouteCraft不应声称first step-level model router。

## 4. 成本覆盖审计

符号：✓=明确测量/计费；△=部分、代理指标或只在讨论中；✗=主结果未计；?=披露不足。

| 工作 | model input/output | router在线 | Judge/verifier | tool/retry/额外轮 | cache read/write/loss | switch/context/handoff | latency/energy |
|---|---:|---:|---:|---:|---:|---:|---:|
| FrugalGPT | ✓（API price） | ✗ | labels离线 | cascade调用✓，Agent项✗ | ✗ | ✗ | ✗/✗ |
| RouteLLM | ✓ | △（≤0.4%估计） | △（训练/评测） | ✗ | ✗ | ✗ | ✗/✗ |
| LLMRouterBench | ✓ | ✗ | △ | △（最多10次API retry但非系统cost模型） | ✗ | ✗ | △TTFT/TPS/✗ |
| SCOPE | △token/FLOPs | △token overhead | △teacher | ✗ | ✗ | ✗ | ✗/✗ |
| HyDRA | ✓ | ✓latency、CPU金额? | △ | ✗ | △设计动机 | ✗ | △请求延迟/✗ |
| Router-R1 | △主要output | ✗（policy本身） | terminal eval | 多candidate output△ | ✗ | ✗ | △讨论/✗ |
| R²-Router | ✓总I/O token | ✓<400ms（均值） | △ | ✗ | ✗ | ✗ | △router/✗ |
| MTRouter | ✓ | ✗embedding | △ | 额外turn反映在model token；tool/retry✗ | ✗（明确limitation） | ✗ | ✗/✗ |
| TRACE-Router | ✗货币 | △bandit很小但未单列 | terminal verifier△ | ✓wall-clock含tool/env | △动机 | △动机 | ✓E2E latency/✗ |
| SWE-Router | ✓API spend | ✗ | unit test✓ | cheap K + restart金额△ | ✗ | context重启计费隐含、未拆 | ✗/✗ |
| TwinRouterBench | ✓四bucket | ✗ | △open task Judge | △failure penalty | ✓ | △cache miss；handoff行为✗ | ✗/✗ |
| Harness-Native | ✓realised bill | ? | ? | △概念记录、未逐项净化 | ✗（future） | ✗ | △/✗ |
| Budget-Aware | ✓ | ✗（论文明确排除） | terminal env | model turns✓，tools/retry✗ | ✗ | ✗ | △估计/✗ |
| EASy | △总tokens | ✗（混入总量不透明） | ✗单列 | extra workflow nodes△ | ✗ | ✗ | ✗/✗ |
| GraphPlanner | ✓估价 | ✗部署 | △ | workflow calls计token、tool/retry✗ | ✗ | ✗ | △训练/✗ |
| Critique Controller | ✗ | ✗ | controller内置但未计 | ✗ | ✗ | ✗ | △承认开销/✗ |
| Agent-as-a-Router | ✓ | ✓自托管估价 | ? | ? | ✗（明确不可观测） | ✗ | ✗/✗ |
| Aragog | GPU serving而非token $ | △scheduler | offline accuracy△ | workflow stage✓ | serving层非prompt cache | model residency/queue△ | ✓throughput/latency；energy✗ |

**[判断]**几乎所有“cost reduction”都不能直接等同 `cost per successful Agent task`：TwinRouterBench最接近真实API billing但缺tool/router/latency；TRACE最接近E2E latency但缺货币/cache桶；HyDRA最接近生产router overhead但cache只作策略理由；Harness-Native称 realised cost，却未把所有服务/Judge/tool/cache逐项闭合。因此 RouteCraft 的完整成本核算本身有 measurement contribution，但不能夸称此前完全没人考虑cache。

## 5. 与 RouteCraft 的逐项差异与新颖性风险

| 近邻 | 相同点 | 已覆盖内容 | 尚未覆盖、可作为 RouteCraft 的必要差异 | 风险等级 |
|---|---|---|---|---:|
| MTRouter | raw history、任务内动态完整模型切换 | 每turn预测模型、terminal-derived labels | 联合选择多值reopen boundary；PlanIR；switch/cache净cost；same-state model×boundary | 极高 |
| TwinRouterBench | per-step prefix、common continuation、真实cost | step counterfactual downgrade、cache四桶、live routing | 外部world snapshot；多boundary intervention；随机重复；adaptive policy | 极高 |
| Harness-Native | harness state、recovery/verify、outcome flywheel | harness-native逐步route、realised bills、arena records | learned temporal commitment；固定workflow；完整switch/replay计量 | 极高 |
| HyDRA | profile matching、cache、session event | sticky task + compaction event重新路由 | event时机由policy选择；Agent语义/外部验证；实际cache-loss | 高 |
| SWE-Router | trajectory揭示难度、升级 | fixed-K cheap roll-in + strong restart | K/boundary自适应、多于一次切换、全成本 | 高 |
| Critique Controller | 联合model与termination | next model + stop/continue | stop不是未来reopen；固定Agent工具workflow；多值boundary | 高 |
| Budget-Aware | full history、budget、per-step | SMALL/LARGE逐步policy、GRPO | boundary head、候选profile、多模型、cache/switch | 高 |
| TRACE-Router | 延迟terminal reward、cache一致性 | `task_terminal` pinning | 条件性学习何时提前开放；可靠stage evidence | 高反例 |
| GraphPlanner/EASy | graph/milestone temporal abstraction | 联合role/model/workflow生成 | RouteCraft不改workflow，只在现有event上route | 中（范围边界） |
| SCOPE/R² | candidate-conditioned multi-output prediction | unseen profile；分别预测quality/cost或joint budget | trajectory PlanIR和temporal boundary | 中 |
| Agent-as-a-Router | feedback memory、task pinning | 跨task continual adaptation | 单task内dynamic boundary | 中 |
| Aragog | stage-level动态model assignment | 固定DAG、system-load JIT scheduling | 可变reopen时机、semantic capability drift | 中 |

**稳妥新颖性表述：**“We study whether, in a fixed agent harness, the router should jointly select a full model and a verifiable, temporally extended re-decision boundary, and measure the counterfactual net value after cache, replay, router, retry, and handoff costs.” 这不是“首个 Agent Router”，而是一个受限的 adaptive commitment / measurement 问题。

## 6. 对候选理论与实验的直接启示

### 6.1 三个必须可证伪的假设

1. **Boundary reversal：**在同一任务的不同可恢复状态上，净效用最优的 β 不总是同一个固定粒度；且这种反转在扣除router/cache/replay/switch后仍存在。
2. **可预测性：**仅用harness可验证facts + 受约束PlanIR，held-out task上能显著降低 `model×boundary` oracle regret，相比prompt-only、raw-history embedding、HyDRA-style profile matcher和最佳fixed boundary。
3. **系统净收益：**学习策略相对最佳task pinning、fixed-K escalation、per-call和最佳固定boundary，能提高cost/success Pareto；收益不是由replanning、Judge泄漏或不公平禁用cache造成。

### 6.2 最危险的反例/停止信号

- TRACE/HyDRA式task pinning因cache和delayed credit占优；
- Budget-Aware的First-Large说明强模型早期规划可防止不可逆错误；
- MTRouter虽每turn开放，但学成高度sticky，暗示boundary head可能坍缩；
- SWE-Router的强模型从原prompt重启可能优于handoff，说明“继承PlanIR”会锚定错误；
- Twin静态label的greedy/common-continuation无法代表joint dynamic oracle，RouteCraft不能只做单步fork就声称长期因果；
- strong-model dominance、阶段能力高度相关或milestone不可验证时，adaptive boundary退化为task_terminal/next_call。

### 6.3 对 Phase 0 的优先建议

先只做 `2 models × 4 boundaries × 200–500 recoverable states` 的**净oracle测量**，不训练大router：

1. 同一state保存Agent event和外部world snapshot；对每个(model,boundary)运行并在触发点交给共同continuation policy；task-terminal单独作为完整episode处理。
2. 记录四桶tokens、router hypothetical/actual latency、tool、retry、failure recovery、context replay、provider state失效、switches和P95；默认启用合法prompt cache。
3. 比较 dynamic oracle、每个single fixed boundary、task pinning、fixed-K、per-call。若最佳fixed boundary获取 ≥95% dynamic-oracle增益，或净oracle相对最佳task pinning不足约3–5 success points且cost/success不足10%，adaptive boundary应停止，转为benchmark/measurement论文。
4. 训练顺序应为 Logistic/LightGBM/kNN→小encoder；只有PlanIR简单模型显著优于prompt/raw-history和profile matcher，才值得0.5–1.5B router。强LLM-as-router必须把自身完整上下文与reasoning token计费。

## 7. 核验与未核验清单

### 已核验（论文全文 + 一手状态来源）

FrugalGPT、RouteLLM、LLMRouterBench、SCOPE、HyDRA、Router-R1、R²-Router、MTRouter、TRACE-Router、SWE-Router、TwinRouterBench、Agentic Routing: The Harness-Native Data Flywheel、Budget-Aware Agentic Routing、EASy、GraphPlanner、Iterative Critique-and-Routing Controller、Agent-as-a-Router、Aragog。

### 未核验或仅部分核验

- **AgentRouter：**题名、作者、workshop元数据可核验；官方PDF执行日403，因此算法细节、数字、代码均未核验。
- **官方代码未核验/未发现：**SCOPE（项目页称future release）、HyDRA、TRACE-Router、Budget-Aware、EASy、Iterative Critique Controller、Aragog；SWE-Router仅核验官方Hugging Face组织，未核验源码仓库。
- **正式录用未核验：**Iterative Critique Controller、Agent-as-a-Router、TRACE-Router、TwinRouterBench、Budget-Aware、HyDRA、SCOPE、Harness-Native、Aragog均应按preprint/technical report写；EASy明确under review。
- **Agent-as-a-Router 的PDF中部分自定义聚合score与切分需按代码复现后再用于跨论文数值比较。**

## 8. 本地论文文件与 SHA256

| 文件 | SHA256 |
|---|---|
| `papers/01_model_routing/2024_FrugalGPT.pdf` | `035AE8B90333DAD8B7817FC8F55E7C4CBCA435368C5C1A4DBF7BBA9E5DB87473` |
| `papers/01_model_routing/2025_RouteLLM.pdf` | `C9BC9C8171CAB95BB3832CDE8767C6B5E0925CD62930E51DDBD60D7CB2616741` |
| `papers/01_model_routing/2025_Router_R1.pdf` | `178736092D1B93396B3DC0E273E5C90E0CA42F02958516138F47FB3959CDFCC2` |
| `papers/01_model_routing/2026_HyDRA.pdf` | `80820549216B5B438C78C792B9B257E87116900EEE160994D4EBA475B98021E0` |
| `papers/01_model_routing/2026_LLMRouterBench.pdf` | `C18DD0D6289E9EDCE33AEAFC9F45F9C38C72CC120ED47D4D89054A4E74CFCAFF` |
| `papers/01_model_routing/2026_Models_Under_SCOPE.pdf` | `514B8887467C58CAEA64FA170AD6A174B4E0DC503E1438CAB4D5D8D5543124DA` |
| `papers/01_model_routing/2026_R2_Router.pdf` | `1B693B0DC5B19555C7FA6333AA22C943BFC94890FBF7118DAB6C7481B723580F` |
| `papers/02_agent_routing/2025_Aragog.pdf` | `F806D38CDA9FF557171093BD572ECF0E0B52DAC3EA139FFD09EC89ECA8037AF7` |
| `papers/02_agent_routing/2026_Agent_as_a_Router.pdf` | `1EDA4F453A611356B553EF5BA0F82351EF0CF54D46E281E36F0BEDFAAF93255D` |
| `papers/02_agent_routing/2026_Agentic_Routing_Harness_Native.pdf` | `D3C2A6969790EBA66FFF276B7F7FF9ED2482770852B547AD1BE2C19027AFE540` |
| `papers/02_agent_routing/2026_Budget_Aware_Agentic_Routing.pdf` | `B2983F5648052E36A6D3A7F2BF941D976EBC250AE2DE34D9E56F23A9451AF877` |
| `papers/02_agent_routing/2026_EASy.pdf` | `9C9316E22E9C93E74E03E02DA6AABC4EFF11D658EAAD58ED743F2E895F94C624` |
| `papers/02_agent_routing/2026_GraphPlanner.pdf` | `448C283C0E86A2AB9A273B16FE0D742BC8B089A715E3AD9C0F55C6C4A0B93477` |
| `papers/02_agent_routing/2026_Iterative_Critique_Routing.pdf` | `07D577830004E249CD0F53C8CD476450CBD28CA0E836C43DB3716CD7D74873DA` |
| `papers/02_agent_routing/2026_MTRouter.pdf` | `339973FB8E766C652AA9F990E90197DB735A01E6EE574AB6178DB7DDEC7D0581` |
| `papers/02_agent_routing/2026_SWE_Router.pdf` | `F55DB25135D0D28C601A4AC93C730076001BA93806D30047EA7BEFC4379DCC32` |
| `papers/02_agent_routing/2026_TRACE_Router.pdf` | `34F702B6B45E28288C00FEEB060B9C85DBD80ECE1912447C04C65CE33337237A` |
| `papers/02_agent_routing/2026_TwinRouterBench.pdf` | `3C4B038C04D1ED6B3C144FF2C2272C2713EEBD25044EACD32F8522E4C3120FF9` |

## 9. Page 02 定向补充核验（2026-08-17）

在 Page 02 的独立新颖性复核中新增四项一手论文。它们不改变“Revise”结论，但进一步禁止宽泛的 `first learned commitment / first adaptive reconsideration` 表述。

### 9.1 Hera：直接逐 step 完整模型 Router

- **来源：** *Hera: Learning Long-Horizon Coordination for Device-Cloud Collaborative LLM Agents*，arXiv preprint 2026。[论文](https://arxiv.org/abs/2605.24598)；官方代码未核验；本地 `papers/02_agent_routing/2026_Hera.pdf`。
- **动作与粒度：**在 ALFWorld、WebShop、AppWorld 的每个 environment step 二选一 device/cloud 模型，重新决策边界固定为 next step。
- **标签：**第一阶段在 cloud trajectories 上重放 device agent，以 device/cloud action agreement 监督；第二阶段对跨 rollout 的相同状态分组，按 terminal return 和 future cloud-call 数构造 step-level preference。
- **作者报告：**达到 cloud-only success 的 92.5%，cloud 使用为 46.3% steps；仅适用于其模型、任务与协议。
- **对 RouteCraft：**不能声称首个 step-level device/cloud Agent Router、首次用 future strong-model calls 训练 Router 或首次对相同状态分组。剩余差异只能是多值 future reopen boundary、完整 world fork 与全部切换成本。

### 9.2 三项结构同构但非完整模型 Router 的先例

- **ARC / Learning to Configure Agentic AI Systems**（[arXiv:2602.11574](https://arxiv.org/abs/2602.11574)）：把 query-level workflow/tool/budget/prompt configuration 表述为 SMDP 中处理完整 query 的 temporally extended option；不是单任务内完整模型路由，但阻断宽泛的“首次把 Agent commitment 写成 option/SMDP”。本地 `papers/05_theory_methods/2026_ARC_Learning_to_Configure_Agentic_AI.pdf`。
- **AgentSwing**（[arXiv:2603.27490](https://arxiv.org/abs/2603.27490)）：context length 超过预设比例后，在同一轨迹并行展开多种 context-management branch，再用 lookahead 选择 continuation；选择对象不是模型，trigger 仍固定。本地 `papers/05_theory_methods/2026_AgentSwing.pdf`；论文首页链接 [Alibaba-NLP/DeepResearch](https://github.com/Alibaba-NLP/DeepResearch)。
- **SyncPlan**（[arXiv:2608.01652](https://arxiv.org/abs/2608.01652)）：Plan Staleness Detector 持续检查剩余 plan 并在环境变化使假设失效时触发 replanning；选择对象是重新规划，不是完整模型。它阻断宽泛的“首次学习何时重新考虑”，但不覆盖 model + future boundary。论文写明 code/data will be made publicly available；执行日官方仓库未核验。本地 `papers/05_theory_methods/2026_SyncPlan.pdf`。

### 9.3 新增文件 SHA256

| 文件 | SHA256 |
|---|---|
| `papers/02_agent_routing/2026_Hera.pdf` | `4C4637FE0C68241F43CBF3696A681DA2C64F85DFD34D0688EBA276F890F721CF` |
| `papers/05_theory_methods/2026_ARC_Learning_to_Configure_Agentic_AI.pdf` | `E2EDC0B2838962274BB54B95B45CD277105299E8A28565EE6A899C515E260692` |
| `papers/05_theory_methods/2026_AgentSwing.pdf` | `1AEE88E500CBD23E2AF649B270FD22E17C16A7857E4B2CB29C368FCBD684BC46` |
| `papers/05_theory_methods/2026_SyncPlan.pdf` | `598C19D91E1F350A49B15C10087443054EFD971500E68CF6B5AE1BA87AC9991E` |

## 10. 新增三篇边界证据核验（2026-08-17）

### 10.1 A Unified Approach to Routing and Cascading for LLMs

- **来源/状态：**Jasper Dekoninck, Maximilian Baader, Martin Vechev；ICML 2025，PMLR 267:12987–13010。[PMLR 论文页](https://proceedings.mlr.press/v267/dekoninck25a.html) · [官方代码](https://github.com/eth-sri/cascade-routing) · 本地 `papers/01_model_routing/2025_Unified_Routing_and_Cascading.pdf`。
- **观察/问题：**单次 prompt 的 routing 只选一个模型，传统 cascade 又必须按固定顺序升级；两者都限制了“看到已生成回答后再选模型”。
- **方法：**将 routing/cascading 写成预算约束下的线性优化。Cascade routing 对同一 query 可先调任意模型，再根据当前已观测回答的质量/不确定性继续调用另一模型或停止。其理论依赖 ex-ante/ex-post quality estimator 和 cost estimator；论文明确指出质量估计精度是实际收益的关键。
- **作者报告：**在其 RouterBench 和 SWE-Bench 设置下，cascade routing 相比单独 routing/cascading 的改善最高分别为 8% 和 14%。这些是该论文的质量-成本设置，不包含 Agent loop、tool、cache、retry 或 handoff 成本。
- **对 RouteCraft：**不能把“获得中间模型回答后重选完整模型”作为新颖点。可保留的区别是 Agent 执行状态与外部观测、可学习的未来 reopen boundary，以及完整系统净成本。

### 10.2 EvoRoute：最直接的新冲突

- **来源/状态：***EvoRoute: Experience-Driven Self-Routing LLM Agent Systems*，arXiv:2601.02695v1，2026-01-06，preprint。[论文](https://arxiv.org/abs/2601.02695) · 本地 `papers/02_agent_routing/2026_EvoRoute.pdf`。论文写明代码将发布到 `https://github.com/bingreeky/evo-route`，执行日该地址返回 404，故代码**未核验/未可用**。
- **决策对象/粒度：**在已有 Agent workflow 的每个 sub-task / step 前，为当前 active agent role 从六个完整 LLM backbone 中选一个；每步都重新路由，不保持多步 commitment。
- **Router 输入/方法：**经验记录包含 agent role、LLM、sub-task/嵌入、工具集、step 成本与时长、step 成功以及 terminal task performance。新步骤按 role match、MiniLM 语义相似度和 predicted-tool overlap 检索；对 performance/cost/duration 做 Pareto 过滤，再从 Normal-Inverse-Gamma 后验做 Thompson sampling。任务结束后将各步结果追加到经验库；cold start 用树形多轨迹探索。
- **作者报告：**在 ReAct、Smolagents 和 CK-Pro 三类 harness，以及 GAIA、BrowseComp+、DS-1000、HotpotQA、DDXPlus 上，最高降低约 80% 货币成本、超过 70% 延迟，并报告最高 10.3 个性能点改善。成本和 delay 是整个 benchmark 运行的累计量；论文没有单列 Router 检索/工具预测开销、cache loss 或跨模型行为 handoff 成本。
- **对 RouteCraft：**EvoRoute 已直接覆盖 step-level、history/experience-aware、在线更新、cost+latency-aware 的 Agent 完整模型路由，且使用 role/sub-task/tool 类似 PlanIR 的状态。RouteCraft 不得再宣称这些属性首创；唯一清晰的方法空间是学习“当前选哪个模型 + 在哪个未来可验证事件重开”，并在计入 switch/cache/replay/handoff 后证明优于 EvoRoute 式 every-step routing。

### 10.3 Opportunity Is Not Realizability：Phase 0 的统计门槛

- **来源/状态：***Opportunity Is Not Realizability: Selection-Valid Diagnostics for Multi-LLM Routing*，arXiv:2608.08265v1，2026-08-08，preprint。[论文](https://arxiv.org/abs/2608.08265) · 本地 `papers/05_theory_methods/2026_Opportunity_Is_Not_Realizability.pdf`。PDF 提到 artifact，但 arXiv 页和正文未给出可核验的官方仓库地址。
- **理论分解：**`G_out`（看到所有候选真实结果后的 outcome-oracle gap）、`G_Z`（指定部署前可观测信号 `Z` 下的 Bayes-optimal gain）和 held-out learned-router gain 是三个不同 estimand，且 `0 ≤ G_Z ≤ G_out`。大 Oracle gap 只证明模型池存在互补正确性，不证明 prompt/PlanIR 能在部署前识别它。
- **统计方法：**给出在同一样本上选择 empirical-best fixed model 后仍有效的 selection-valid interval，以及对候选 Router family 选优后的 simultaneous interval。该文明确指出：固定选中的基线后做普通 paired interval 不保持 coverage；router 训练/调参与最终测试结果必须独立。
- **作者报告：**8 个 checkpoints、4 个 benchmark 上，selection-valid outcome-oracle gap 为 9.7–30.7 个点；最强的可部署 prompt Router 仅恢复 7.5%–14.4%，11 个候选策略中最佳策略的 simultaneous interval 下界在四个任务上均为 0。这不证明所有 Router 不可学，只证明被测的信号/假设类没有被证明恢复 Oracle opportunity。
- **对 RouteCraft：**Phase 0 必须同时报告（1）model×boundary outcome Oracle opportunity，（2）对预先声明的 harness/PlanIR 信号可实现的 held-out gain，（3）学习 Router 在未见状态上的净 gain。选最佳 task-pinning/fixed-boundary 基线、选 Router 架构/超参和最终置信区间不得共用同一份 test outcomes。

### 10.4 文件完整性

| 文件 | 页数 | SHA256 |
|---|---:|---|
| `papers/01_model_routing/2025_Unified_Routing_and_Cascading.pdf` | 24 | `2E9F7E42FED197ABBD23DE7E0ED2071510D92383B64F5E1FFE3FCD447854B65D` |
| `papers/02_agent_routing/2026_EvoRoute.pdf` | 13 | `E2D15A2B14A85FD0C0360F5947610B74306B2C0AB78AB09ECE2937F95AC33E9D` |
| `papers/05_theory_methods/2026_Opportunity_Is_Not_Realizability.pdf` | 20 | `90A21BA188434EF13536D5F93EFA91C306E7A8771BEFCE066CAA8660E77A8DA4` |

三份官方 PDF 均为 `%PDF-1.7`；`pdfinfo` 标题与官方元数据一致，`pdftotext -layout` 可读取完整方法/结论，150 DPI 首页渲染未见视觉缺陷。

---

**建议给总报告的判断：`Revise` 而非无条件 `Go`。** 研究问题应收窄为：“在固定Agent harness中，哪些**外部可验证事件**使多值 temporal commitment 相对task pinning和per-call获得扣除cache/replay/handoff后的净价值？”先做oracle measurement；只有存在稳定boundary reversal且PlanIR简单模型可预测时，再推进完整RouteCraft。
