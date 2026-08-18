# 证据流 C：规划/轨迹蒸馏、理论与反事实实验设计

**检索截止日：2026-08-17（Asia/Shanghai）**  
**研究对象：完整 LLM 之间的 Agent Router；不把 MoE token-to-expert routing、工具路由或 workflow generation 淵称为同一问题。**

## 0. 决策结论（仅针对证据流 C）

**结论：`Revise / Go to Phase 0 measurement`，尚不足以直接 Go 到复杂 Router 或 RL。**

最强理论支持来自三条彼此一致、但不能被夸大为“已证明 RouteCraft 有效”的证据：

1. [Options 框架](https://doi.org/10.1016/S0004-3702(99)00052-1)把 temporally extended action 写成 `(initiation set, intra-option policy, termination)`，在终止事件上形成 SMDP；[Option-Critic](https://ojs.aaai.org/index.php/AAAI/article/view/10916)进一步联合学习 option policy 与 termination。这足以说明“选择对象 + 重新开放决策的终止条件”是一个合理的序贯决策形式。
2. [Harb et al. 2018](https://ojs.aaai.org/index.php/AAAI/article/view/11794)明确把 option 终止/重选的 deliberation cost 加入回报；[Callaway et al. 2018](https://www.auai.org/uai2018/proceedings/papers/269.pdf)把计算选择写成 metalevel MDP，并以 value of computation（VOC）决定是否继续计算。它们共同支持“重路由收益必须超过 Router、切换、上下文与交接成本”。
3. 轨迹文献显示真实的新信息常来自工具观察、验证失败和恢复状态，而不是均匀地在每个 call 出现。尤其 [ETO](https://aclanthology.org/2024.acl-long.409/)发现用 terminal reward 构造 step-wise 标签明显不稳定，[EEF](https://arxiv.org/abs/2504.13145)则显示失败轨迹中的恢复段可以有用。这同时支持事件边界采样，也否定“任意 step 都有可靠局部标签”。

最强反例不是一个构造出来的玩具，而是两项一手实验：

- ETO 的 trajectory-wise DPO 优于 step-wise 对比；作者把后者不稳定归因于仅用最终奖励估计动作质量不准确。这直接挑战用 delayed terminal reward 为每个 PlanIR 状态赋局部能力/边界标签。
- [ClawTrace](https://arxiv.org/abs/2604.23853)的 TraceCard/CostCraft 是与 PlanIR 最相似的“轨迹压缩 + 成本字段”证据之一，但 SpreadsheetBench 学到的 preserve rules 在 SkillsBench 跨任务迁移时造成全部三个质量回退，且全 84-task benchmark 没有聚合成本节省。压缩表示和可读规则并不自动跨 harness/任务泛化。

因此，第一篇论文应把贡献收窄为：**在固定 Agent workflow 下，测量并预测“何时重新开放完整模型选择”是否存在可复现的净价值**。先做 matched fork 和动态 Oracle 空间测量；只有在 Oracle 空间、边界反转和简单模型可预测性同时成立后，才训练小语言模型 Router。不要第一篇就上 contextual bandit/offline RL。

---

## 1. 证据等级与核验规则

- **论文事实**：只来自论文原文、ACL/PMLR/NeurIPS/OpenReview/arXiv 页面或作者官方 GitHub/项目页。
- **本报告推断**：明确写为“推断”；不把相关性写成因果。
- **候选假设**：尚需 same-state fork 或端到端实验检验。
- **未核验**：标题、正式状态、官方代码或关键结论找不到一手证据时不补全。
- 本流归档的 24 份 PDF 均已检查 `%PDF` 文件头、非零长度与 `pdfinfo` 页数；SHA256 见末尾。`1999_Options...pdf` 已从 0 字节重新下载为 31 页官方作者机构版本。`1991_Principles_of_Metareasoning_abstract_only.pdf` 只有一页摘要扫描，**不列作全文归档**；完整期刊正文受限，正文理论由官方期刊页和 2018 UAI 后续论文交叉核验。

## 2. 规划与轨迹蒸馏工作核验总表

> 表中“与 RouteCraft 的关系”是本报告推断，不是原作者主张。所有这些工作都主要学习 Agent 行为、计划、技能或表示；它们不是“在一次固定 Agent 执行中联合选择完整模型与重决策边界”的直接覆盖。

| 工作 | 作者；状态 | 论文/官方实现 | 训练材料与标签 | Judge / 成本 | 与 RouteCraft 的关系与关键局限 |
|---|---|---|---|---|---|
| **FireAct: Toward Language Agent Fine-tuning** (2023) | Baian Chen, Chang Shu, Ehsan Shareghi, Nigel Collier, Karthik Narasimhan, Shunyu Yao；arXiv preprint，正式录用状态未核验 | [arXiv](https://arxiv.org/abs/2310.05915)；[项目页](https://fireact-agent.github.io/)；[代码/数据](https://github.com/anchen1011/FireAct) | 用 GPT-4 生成**成功**轨迹，把 CoT/ReAct/Reflexion 等路径转成 ReAct 后 SFT；默认实验使用 500 条成功轨迹 | 教师生成成本离线；论文按当时 API 单价报告单 trial 成本/时间，但不是完整 Agent 成本模型 | 证明不同 prompting/agent method 的最优混合依赖 base LM；ReAct+CoT 会改善部分模型、伤害 CodeLlama。它蒸馏行为到权重，不在线选模型/边界；成功-only 有幸存者偏差，且主要是单一 Google-search QA 环境 |
| **ToolLLM / ToolBench** (2023/ICLR 2024 Spotlight) | Yujia Qin, Shihao Liang, Yining Ye, Kunlun Zhu, Lan Yan, Yaxi Lu, Yankai Lin, Xin Cong, Xiangru Tang, Bill Qian, Sihan Zhao, Lauren Hong, Runchu Tian, Ruobing Xie, Jie Zhou, Mark Gerstein, Dahai Li, Zhiyuan Liu, Maosong Sun | [OpenReview](https://openreview.net/forum?id=dHng2O0Jjr)；[arXiv](https://arxiv.org/abs/2307.16789)；[GitHub](https://github.com/OpenBMB/ToolBench) | ChatGPT 收集/生成 16,464 APIs 与 126,486 instruction–solution path；DFSDT 搜索、回退、放弃，但训练主要保留通过的 solution paths | ToolEval 使用 ChatGPT 自动 evaluator，并重复预测；数据生成和搜索包含大量教师调用 | 说明工具搜索树可生成候选未来，但 ToolBench 的成功路径训练丢掉失败分支。不是模型 Router；API 文档与完整历史被放进输入，直接搬到 PlanIR 会很贵 |
| **ToolPreference / TP-LLaMA** (NeurIPS 2024) | Sijia Chen, Yibo Wang, Yi-Feng Wu, Qing-Guo Chen, Zhao Xu, Weihua Luo, Kaifu Zhang, Lijun Zhang | [NeurIPS PDF](https://proceedings.neurips.cc/paper_files/paper/2024/file/c0f7ee1901fef1da4dae2b88dfd43195-Paper-Conference.pdf)；[数据集](https://huggingface.co/datasets/chrissiecsj/ToolPreference)；完整官方训练代码**未核验** | 从 ToolBench DFS tree 中抽取含失败分支的树；在同一 history 的 branch child 间构造 step-wise preferred/dispreferred 对；69,393 preference pairs，TP-LLaMA 子集 8,202，DPO | 分支标签来自最终成功路径；部分 ToolEval 仍用 ChatGPT judge | 是“same-history 比较”的近邻，但“成功路径 child=preferred”使用了未来结果，若作为在线 PlanIR 字段会产生 hindsight leakage。作者也指出全历史逐步输入耗时，并建议摘要化 |
| **ETO: Trial and Error** (ACL 2024 long) | Yifan Song, Da Yin, Xiang Yue, Jie Huang, Sujian Li, Bill Yuchen Lin | [ACL Anthology](https://aclanthology.org/2024.acl-long.409/)；[GitHub](https://github.com/Yifan-Song793/ETO) | 先用 expert trajectory SFT，再让当前 agent 探索；按 environment terminal/dense reward 构造成功–失败 trajectory pair，以 DPO 迭代优化 | 主要依赖环境奖励，不需 reward model；8×A100；未完整计数据生成/训练能耗 | 对 RouteCraft 最重要的负证据：trajectory-wise 最好；step-wise 用最终 reward 给动作定质明显不稳定，WebShop 63.1 SFT → 8.3（其报告条件），需更小 LR/更强约束。迭代超过 2–3 轮也会下降；说明 terminal reward 局部归因和重复自训练都可能失败 |
| **MAGDi** (ICML 2024) | Justin Chih-Yao Chen, Swarnadeep Saha, Elias Stengel-Eskin, Mohit Bansal | [PMLR](https://proceedings.mlr.press/v235/chen24ah.html)；[GitHub](https://github.com/dinobby/MAGDi) | 将多教师、多轮讨论表示为 interaction graph；next-token、正确/错误 reasoning contrastive 与 graph objective 联合蒸馏到单模型 | 生成端是多模型/多轮，推理端单模型；离线教师成本存在 | 说明结构化多教师信号可压缩，但目标是把协作推理写进一个 student，不是执行期模型路由；图表示是否保留 route-sufficient 信息未被检验 |
| **Agentic Plan Caching (APC)** (NeurIPS 2025) | Qizheng Zhang, Michael Wornow, Kunle Olukotun | [NeurIPS proceedings](https://proceedings.neurips.cc/paper_files/paper/2025/hash/9549f7d06700f0966d5f938f1d11022a-Abstract-Conference.html)；作者页未列代码，**官方代码未核验** | 从完成的成功执行中提取 plan template；关键词检索；cache hit 时小 planner 适配，miss 时大 planner 重新规划 | GPT-4o 大 planner、Llama-3.1-8B 小 planner/actor、GPT-4o-mini 做抽取；报告平均 cost -50.31%、latency -27.28%、96.61% 最优应用性能；成本按 API input/output 价格，未分 cache-read/write、切换/重试/能耗 | 最接近“计划表示影响昂贵/便宜模型选择”的系统，但它改变 planning path 并复用 workflow template；是 cache-hit 触发的大/小 **planner** 选择，不联合学习 commitment boundary。全文历史 cache 在 FinanceBench 反而比 template 差，支持压缩；但只成功轨迹建 cache，可能漏恢复状态 |
| **AgentRefine** (ICLR 2025) | Dayuan Fu, Keqing He, Yejie Wang, Wentao Hong, Zhuoma Gongque, Weihao Zeng, Wei Wang, Jingang Wang, Xunliang Cai, Weiran Xu | [OpenReview](https://openreview.net/forum?id=FDimWzmcWn)；[项目页](https://agentrefine.github.io/)；[GitHub](https://github.com/Fu-Dayuan/AgentRefine) | GPT-4o 同时扮演 DM/player 合成含错误与 refinement 的多轮环境；规则/LLM verifier 检查；错误 action token mask loss，仅正确与恢复动作训练 | 强教师生成世界、错误与验证；不是实测真实外部环境。官方 repo 截止核验日主要发布数据，README 仍写 inference code/model 后续提供，故只能算**部分开源** | 支持把错误后观察与恢复行为加入数据；但其 synthetic DM 对“真实状态”有控制权，不能证明 teacher semantic fields 在真实 harness 中可靠。某些无限参数动作并不验证，标签仍可能主观/自洽而不真实 |
| **Exploring Expert Failures (EEF)** (arXiv 2025) | Li-Cheng Lan, Andrew Bai, Minhao Cheng, Cho-Jui Hsieh, Tianyi Zhou；arXiv v2。另有 ICLR 2026 under-review 版本，但正式接收未核验 | [arXiv](https://arxiv.org/abs/2504.13145)；[OpenReview under-review PDF](https://openreview.net/pdf?id=4fh0Z9nwjx)；官方代码**未核验** | 从失败 expert trajectory 均匀选中间状态；由当前 policy 从该状态 rollout。若较早状态可成功、较晚状态失败，则后者标作 recovery state；只把从重要状态出发、最终成功的后缀加入 SFT | 需要大量环境 simulation；不训练 reward model；WebShop/ScienceWorld 有环境 reward | 强力支持失败/恢复轨迹：失败整体不等于所有动作无用。但识别依赖 snapshotable expert states 与多次 rollout；它训练行为而不是 Router，且 beneficial action 的识别是 policy-relative，不能直接当成跨模型通用 capability 标签 |
| **ProAct: Agentic Lookahead in Interactive Environments** (2026) | Yangbin Yu, Mingyu Yang, Junyou Li, Yiming Gao, Feiyu Liu, Yijun Yang, Zichuan Lin, Jiafei Lyu, Yicheng Liu, Zhicong Lu, Deheng Ye, Jie Jiang；arXiv preprint | [arXiv](https://arxiv.org/abs/2602.05327)；[GitHub](https://github.com/GreatX3/ProAct) | GLAD 用环境 MCTS 生成包括 optimal/suboptimal/dead-end 的真实未来树，再用 teacher 压成 causal reasoning；随后用 parameter-free MC-Critic 和 PPO/GRPO | 2048/Sokoban 有可快速复制的环境；MC-Critic 可达 1,000 random-policy rollouts；训练/搜索成本很大 | 是 search-tree→compact representation 的强近邻。关键警告：压缩文本看过真实未来；若把相同信息放进测试时 PlanIR 就是泄漏。随机 critic 在 sparse reward 下增大 M 反会稀释信号，说明“更多 rollout/信息”不必然更好 |
| **AgentArk** (2026) | Yinyi Luo, Yiqiao Jin, Weichen Yu, Mengqi Zhang, Srijan Kumar, Xiaoxiao Li, Weijie Xu, Xin Chen, Jindong Wang；arXiv preprint | [arXiv](https://arxiv.org/abs/2602.03955)；[GitHub](https://github.com/AIFrontierLab/AgentArk) | 5-agent、最多 3 轮 debate；提取正确与纠错轨迹；RSFT、diverse data augmentation、PRM+GRPO。也实验五种异构 teacher | Qwen2.5-72B verifier/judge；PAD 用 PRM、8×H100；论文称训练离线、推理单模型，但多 agent 数据生成成本共享且未完全折算 | 证明 multi-teacher/self-correction 可转移，但 OOD 增益小于 ID，数据量增加不单调，0.6B student 在 >5 agents 时会退化。强教师给“推理质量”分数不能当 RouteCraft 真标签；与 candidate-conditioned unseen-model routing 无直接等价 |
| **ClawTrace / CostCraft** (Agent Skills '26 Workshop, CAIS 2026) | Boqin Yuan, Yue Su, Renchu Song, Sen Yang, Jing Qin | [arXiv](https://arxiv.org/abs/2604.23853)；[GitHub](https://github.com/epsilla-cloud/clawtrace) | 8 类 hook 捕获 session/LLM/tool/subagent；确定性编译 1.2–1.8 kB TraceCard；success/error analyst 生成 preserve/prune/repair skill patches | 每步分 input/output/cacheRead/cacheWrite USD；repair analyst 有 oracle，merge 用 LLM；插件开销报告中位约 0.30% wall time | 与 PlanIR 架构最近：事实编译器 + 小 IR + 离线语义分析。但 role/redundancy/subagent 字段含启发式，部分未验证；单一 OpenClaw+gpt-5.4；跨 benchmark preserve rules 过拟合且总成本不降。它优化未来 skill 文档，不在线路由完整模型 |

### 2.1 从成功、失败、搜索树与多教师轨迹能学到什么

| 数据来源 | 一手证据 | 可支持的 PlanIR/Router 信号 | 不可直接推出的结论 |
|---|---|---|---|
| 仅成功轨迹 | FireAct、ToolLLM、APC | 常见 subgoal、有效工具序列、可复用 plan template | 不能估计失败风险、恢复价值或“便宜模型在此状态会不会失败”；有幸存者与任务难度偏差 |
| 成功–失败成对 | ETO、ToolPreference | 在同一任务/history 下的相对行为信号；适合 pairwise ranking | terminal success 不能无条件归因给某一步；未来路径身份不可进入在线特征 |
| 失败中的可恢复后缀 | EEF、AgentRefine | last error、retry、recovery mode、可逆性、过去环境反馈 | “专家失败轨迹中的某步有用”仍需从该状态重新执行验证；教师解释不等于因果标签 |
| 搜索树/环境 rollout | ToolLLM、ProAct | counterfactual action coverage、dead-end、future value；用于离线生成/检验 | 测试时不可把真实未来放进 PlanIR；随机 rollout 在 sparse reward 或不匹配 continuation 下可误导 |
| 多教师/多 agent | MAGDi、AgentArk | 教师分歧、候选策略多样性、纠错行为 | 更多教师并非单调更好；小 student 会被过多/复杂信号压垮；教师共识不是真值 |
| 成本归因 trace | ClawTrace | cache-aware token、tool/retry、span cost、错误位置；支持 route-sufficient compiler | 可读压缩和规则并不保证跨任务/跨 harness；成本最小步骤也可能是质量护栏 |

### 2.2 直接影响研究决策的四个事实

1. **失败与恢复轨迹必须纳入，但不能原样 SFT。** EEF 的价值来自“从失败轨迹的中间状态重新 rollout，只有能通向实测成功的后缀才训练”，而不是把所有 negative trace 当反例。建议把 failure 分成 `model-limited / tool-transient / environment-invalid / budget-timeout / handoff-inconsistent / unknown`；只有外部证据能定类时才做 hard label。
2. **step label 是最危险的标签。** ETO 的消融已给出直接负证据；ToolPreference 的 step-wise 对来自未来成功路径；ProAct 的 compressed reasoning看过搜索树未来。RouteCraft 若用终局 reward 给 `stage_type/progress/capability` 逐步标签，极可能学到 hindsight。
3. **紧凑 IR 有系统动机但没有充分性保证。** APC 的 template 比完整 history 更便宜且有时更准；ClawTrace 把 trace 压至 1.2–1.8 kB；但两者都未证明对 `(model,boundary)` outcome 的条件充分性，ClawTrace 还出现跨任务规则回退。
4. **多教师/大 Router 不是默认答案。** AgentArk 数据规模与 agent 数增加非单调；ProAct sparse-reward MC rollout 非单调；因此 Phase 0 应先用 deterministic compiler + LightGBM/kNN，而不是 0.5B–1.5B Router 或 RL。

---

## 3. PlanIR：routing-sufficient plan-state，而不是 CoT 蒸馏

### 3.1 与完整 CoT/计划蒸馏的概念差异

令完整、仅包含决策时可见信息的 history 为 (H_t)，PlanIR 为 (Z_t=g(H_t))，候选 action 为 (a=(m,\beta))，潜在结果向量为

\[
Y_t(a)=\bigl(S_t(a),C_t(a),L_t(a),F_t(a)\bigr),
\]

分别表示在统一 continuation policy 下的终局成功、成本、延迟和失败类型。完整 CoT 蒸馏试图复现 teacher 的 reasoning token 或行为 policy；PlanIR 的目标更窄：**只保留足以比较候选 `(model,boundary)` 的信息**，不要求复现、解释或生成 teacher 的思考过程。

理想的结果充分性可写为

\[
\{Y_t(a):a\in\mathcal A\}\ \perp\ H_t\mid Z_t,D_a,
\]

或较弱的 action-ranking sufficiency：对任意两个 action (a,a')，

\[
\operatorname{sign}\,\mathbb E[Y_t(a)-Y_t(a')\mid H_t]
=
\operatorname{sign}\,\mathbb E[Y_t(a)-Y_t(a')\mid Z_t].
\]

后一条件对 Router 已足够，却远弱于重构 trajectory。它与 [Information Bottleneck](https://arxiv.org/abs/physics/0004057) 的相关信息压缩一致：可把 (H) 当输入、(Y(a)) 当 relevance variable，以

\[
\min_g I(H;Z)-\alpha I(Z;Y)
\]

解释压缩/充分性权衡。**但这只是解释视角，不建议 Phase 0 直接估计互信息**：小样本、混合连续/离散 outcome 下 MI estimator 会成为新误差源。更实用的是结果预测与 policy regret 的非劣检验。

[Li, Walsh & Littman 2006](https://thomasjwalsh.net/pub/aima06Towards.pdf)进一步给出有用类比：保留 transition/reward 或 (Q^*) 的抽象可保持最优 policy，而仅“同一个最优动作”的粗抽象并不总保证学习收敛或 ground-MDP 最优。对应到 PlanIR：**分类标签相同并不等于表示充分**；最好保留各候选 action 的 calibrated outcome vector，而非只训练一个 argmax model ID。

### 3.2 字段审查

| 候选字段 | 来源类别 | 保留建议 | 泄漏/泛化风险与修订 |
|---|---|---|---|
| `stage_type` | harness-native event，或规则推断 | 保留，但允许 `unknown/mixed` | 许多 ReAct agent 无显式 plan/milestone。若用强 LLM 看完整轨迹事后标 stage，会泄漏；应记录 provenance 与置信度 |
| `current_subgoal` | teacher semantic | 可选、弱标签 | 只能由**截至 t 的前缀**生成；不得用成功 continuation 反推。文本应 canonicalize，并与已调用工具/外部对象对齐 |
| `remaining_obligations` | verifier/checklist + teacher | 保留“可验证义务”；语义义务可选 | gold tests、隐藏 rubric、未来数据库状态若运行时不可见，不得进入。建议每项带 `source` 与 `evidence_id` |
| `progress: 0..1` | 常为 teacher 主观 | 不建议作为单一标量核心字段 | 最易把结局泄漏回中间。优先改成 `verified_completed / verified_total / unknown_obligations`；连续 progress 仅作弱特征 |
| `required_capabilities` | teacher 主观 | 降级为 auxiliary，不当 ground truth | “此步需要 0.8 reasoning”不可外部证伪，也容易复制厂商印象。改用 route outcome 反推的 empirical demand，或模型 profile probe 的交互特征 |
| `evidence_state` | 工具结果/测试/DB predicate | 核心保留 | 只存决策时已观察证据、ID/摘要/hash；不得存未来 verifier 结果或隐藏答案 |
| `last_error` | harness/tool | 核心保留 | 用结构化 error code + sanitized message embedding；自由文本可能包含 gold answer 或 provider-private 数据 |
| `retry_count` | deterministic | 核心保留 | 应按 failure signature、tool、model 分开，而不是单一总数 |
| `reversibility` | tool schema/policy + world state | 保留，但改成 pending action 层级 | 不应由教师凭直觉标全局。至少分 `read-only / transactional-rollback / snapshot-restorable / externally irreversible / unknown` |
| `remaining_budget` | deterministic | 核心保留 | 同时记录 money/token/wall-time/tool-call；归一化值之外保留绝对单位 |
| `context_tokens` | tokenizer/provider | 核心保留 | 应区分 fresh、cache-read、cache-write、reasoning/output 估计；不同 tokenizer 不可直接等同 |
| `cache_state` | harness/provider | 核心保留 | 明确 prefix identity、provider/model/adapter compatibility、TTL；不要把“可能 hit”当已 hit |
| `current_model` | system | 保留为 action/context，不一定放入语义 (z) | 单独输入可避免 fixed-ID shortcut；另需 previous model、provider、resident/loading state |

**建议的最小 PlanIR v0 只有四块：**

1. `control`: event type、past verified stage、pending tool/action、terminal flag；
2. `verified_progress`: 已完成外部谓词、尚未完成的显式义务、最近 observation 摘要；
3. `failure_recovery`: structured error、按签名 retry、timeout、安全中断、可逆性；
4. `resources_compatibility`: 剩余预算、上下文长度、四类 token/cache、current model/provider、replay/cache compatibility、queue/load snapshot。

`current_subgoal` 可作为第五块实验特征；`progress` 与 `required_capabilities` 不进入 v0 hard label。

### 3.3 标签泄漏检查表

以下任一项出现，应把 sample 标为 `leaky` 并从主训练/主结果剔除：

- 在状态 (t) 的 RouteCard 中使用 (t) 之后才出现的 test result、tool output、final answer、reward、数据库谓词；
- 用“最终成功路径上的 child”给 step preference，却没有在同一状态 fork 验证（ToolPreference 型 hindsight）；
- teacher 读取隐藏 unit tests/gold rubric 后生成 `remaining_obligations/progress/capability`；
- 只在成功轨迹上定义 milestone，失败轨迹对应字段为空，从 missingness 直接预测 outcome；
- 不同候选 model/boundary 的 prompt serialization 带有 outcome 或分支文件名；
- same-state fork 后把某分支产生的 cache/provider-private state 复用给另一分支；
- 训练/测试同一 task 的 sibling states 被随机拆到不同 split，导致 trajectory identity 泄漏。

### 3.4 是否使用失败与恢复轨迹

**应该使用，而且必须分层。** ETO、AgentRefine、EEF 一致说明失败中存在可学习信号；但 ETO 同时说明最终 reward 不足以稳定定位坏 step。建议：

- 用外部 exit code、test、DB predicate 标事实；
- 在失败点与最近一次 verified progress 之间做 matched fork，估计“换模型/换边界”的恢复率；
- 失败轨迹训练 `failure-risk` 与 `under-routing recall`，成功轨迹训练成本/延迟；两类都用于 pairwise action ranking；
- 不把 teacher 的“根因解释”当标签，只当可检索注释或 weak auxiliary；
- 按任务宏平均，避免简单成功任务数量压过少量高价值 recovery state。

### 3.5 怎样验证 PlanIR 没有过度压缩

在 held-out task family、严格 group-by-trajectory split 下比较：

1. `prompt-only`；
2. `system facts only`；
3. `PlanIR v0`；
4. `PlanIR + semantic subgoal`；
5. `raw trajectory embedding`；
6. `raw trajectory + PlanIR`。

主要检验不是重构 loss，而是：action outcome NLL/Brier、pairwise ranking、regret-to-oracle、ECE、under-routing recall。做两项充分性诊断：

- **增量历史检验**：在 (Z) 上加入 raw-history embedding，若 cross-fitted paired log-loss、Brier 或 normalized oracle regret 有稳定显著改善，则 (Z) 不充分；
- **非劣与压缩共同条件**：PlanIR 的 success 差距不超过 1–2 个百分点或 normalized oracle-gain recovery 差距不超过 5%，同时 Router input token/latency 至少下降 30%，才可称“routing-sufficient in this benchmark”。这不是普遍统计充分性证明，只是操作性证据。

ClawTrace 的负结果要求再加一项：**跨 harness 的增量历史检验**。在单 harness 上充分不代表跨 harness 足够。

---

## 4. Candidate-conditioned Router 与 unseen-model calibration

### 4.1 为什么分开预测 success、cost、latency、failure risk

推荐 candidate-conditioned scorer

\[
f_\theta(Z_t,d_m,\beta)
\to (\hat p_{\rm succ},\hat C,\hat L,\hat R_{\rm fail})
\]

而不是单 utility，理由是：

- 价格、load 和 SLO 在部署时变化，分头预测允许不重训模型就重算 utility；
- success 是 Bernoulli/calibration 问题，cost/latency 是右偏且 tail-heavy 的分布，损失函数不同；
- `LCB(p_success) >= tau` 需要 calibrated probability，而非任意 utility score；
- 分解可以暴露“省钱来自失败更早结束”的伪 Pareto；ClawTrace 跨 benchmark 中有坏规则让 agent 便宜地不产出，单 utility 很容易掩盖。

代价是多头误差可能累积，因此同时报告最终 utility regret，并在价/load shift 下重新标定。

### 4.2 推荐训练目标与标签

\[
\mathcal L=
w_s\mathcal L_{\rm success}
+w_r\mathcal L_{\rm pair}
+w_c\mathcal L_{\rm cost quantile}
+w_l\mathcal L_{\rm latency quantile}
+w_f\mathcal L_{\rm failure}
+w_a\mathcal L_{\rm capability aux}
+w_{cal}\mathcal L_{\rm calibration}.
\]

| loss | 推荐形式 | 标签来源 | 备注 |
|---|---|---|---|
| success | weighted BCE/Brier | deterministic test、DB/environment terminal predicate；同分支重复的 empirical success rate | LLM judge 仅用于无 verifier 的探索性附表，不作主标签 |
| pairwise ranking | Bradley–Terry / pairwise logistic；同成功时按 full cost，成功不同则安全优先 | same-state fork 的 `(model,boundary)` outcome；只在 CI 可分或 dominance 明确时 hard pair | 不用单次 terminal reward 给每步排序；平局/不确定保留 soft target |
| cost quantile | pinball loss 预测 p50/p90/p95，或 log-cost Huber | segment + continuation 的实测 input/cache/output/reasoning、router、tool、retry、switch、replay 成本 | 同时保存 `cost_to_boundary` 与 `cost_to_terminal under pi_c`，防止混淆 |
| latency quantile | pinball / survival head（timeout censored） | wall-clock span、queue、load/model-residency snapshot | p95 是一等指标；timeout 不是普通最大值 |
| failure type | hierarchical multi-label CE | 外部 error/exit/verifier + 规则映射 | teacher root-cause 只作 weak label，单独标 provenance |
| capability auxiliary | regression/ranking | model profile 上实际 probe 结果与同状态 outcome interaction | teacher 的 `required_capabilities` 不作 ground truth；辅助项权重小且做去除消融 |
| calibration | Brier/NLL + held-out temperature/isotonic；可加 conformal/empirical LCB | held-out task family / time window | 同时按 model、task family、stage 分组画 reliability；LCB 覆盖率必须实测 |

### 4.3 candidate-conditioned 是否真的支持未见模型

**只能支持条件外推，不能支持无校准 zero-shot。** 固定 model-ID classifier 无法给新模型打分；加入 (d_m) 至少允许 leave-one-model-out。但只有当 profile 覆盖决定 outcome 的轴，并且新模型处在训练 profile 的插值/轻度外推区域时才可信。以下未编码行为会破坏它：tool schema 严格性、provider-private state、reasoning-token API、safety refusal、特定 tokenizer、cache compatibility、部署 queue、同名模型静默更新。

必须做：

- leave-one-model-out 与 leave-one-family-out；
- profile permutation：打乱 (d_m) 后性能应下降，否则模型偷用 ID/价格 shortcut；
- price/load shift 不改 success profile，只改 cost/latency；
- model-version/time split；
- 对新模型给 extrapolation/OOD score，超过训练 profile convex hull/距离阈值时回退到 conservative calibration。

### 4.4 新模型需要多少 probe

对单一 Bernoulli 能力率 (p)，最坏 (p=0.5) 时，95% 正态近似半宽为

\[
h\approx 1.96\sqrt{0.25/n}.
\]

因此约 (n=385) 才能达到 ±5pp，(n=97) 才能达到 ±10pp；稀有 tool failure/tail latency 往往需要更多。不能声称“几十个 probe 就精确”。

MVP 推荐分层顺序：

1. 每个主要 capability/task family 20–40 个微任务 × 3 seeds，总计约 60–120 runs，作粗筛；
2. hierarchical shrinkage 合并相似任务，但报告未经 shrinkage 的区间；
3. 只在候选 action 的 LCB/utility 区间重叠时追加 sequential probe，直到排序区间分离或达到预算；
4. 新模型尚未稳定校准时，`LCB(p_success)` 采用较宽区间并禁止不可逆/高风险路由。

### 4.5 何时简单模型足够，何时需要小语言模型

- **200–500 states 的 Phase 0/1**：Logistic、LightGBM、kNN 加结构化字段和固定 text embedding 足够；复杂 LM 几乎必然数据不足。
- 若 raw trajectory/semantic subgoal 在跨任务上对简单模型仍带来稳定增量，且 input 的长文本交互不能被固定 embedding 捕捉，才考虑 0.5B–1.5B encoder/LM。
- 强 LLM-as-a-Router 必须把其 token、latency、失败与重试计入；如果每个 event 调一次，其成本可能超过模型差价。它更适合作 offline teacher/upper bound，不是默认在线 baseline。
- 第一篇论文避免复杂 RL：matched fork 已提供 supervised counterfactual vector；先证明 supervised policy 有端到端收益。只有出现 load/price/nonstationarity、partial feedback 且安全在线探索可行，才考虑 contextual bandit；长程 boundary credit 与高方差使 offline RL 更晚。

---

## 5. RouteCraft 的 event-driven SMDP / option 表述

### 5.1 可以怎样严谨表述

在 event time (t_k) 上，Router 观察 (Z_k=g(H_{t_k}))，选择

\[
A_k=(m_k,\beta_k),\qquad
\beta_k\in\{\texttt{next_call},\texttt{next_observation},
\texttt{verified_milestone},\texttt{task_terminal}\}.
\]

基础 Agent workflow 在 primitive events 上继续执行，但从 (t_k) 到边界触发时间

\[
T_{k+1}=\inf\{t>t_k:\beta_k(H_t)=1\}
\]

的所有完整模型调用固定为 (m_k)。持续时间 (K_k=T_{k+1}-t_k) 随状态、工具和边界而变。若 (Z_k)（必要时连同 current model/cache/world snapshot）对下一 event-state、累计 reward/cost 与 duration 足够 Markov，则高层过程可写为 event-driven SMDP：

\[
Q(z,a)=\mathbb E\!\left[
\sum_{j=0}^{K-1}\gamma^j r_{t+j}
-C_{\rm commit}(z,a)
+\gamma^K\max_{a'}Q(Z_{k+1},a')
\mid Z_k=z,A_k=a\right].
\]

安全风险、明确失败、timeout 可视为所有 commitment 共有的 interrupt predicate；这与 Options 原论文允许在高层 value 改善时提前 interruption 有形式关联。

**必须加限定语：这是建模等价/类比，不是现有 theorem 对 LLM Router 的直接保证。** 实际 Agent 是 POMDP、provider/tool 非平稳，PlanIR 可能不 Markov；因此可称“event-driven semi-Markov formulation”或“option-inspired adaptive commitment”，不宜声称已满足严格 SMDP 假设。

### 5.2 与标准 temporal option、MoE temporal option、milestone workflow、task pinning 的差异

| 对象 | 高层 action | action 内部控制什么 | termination | 是否改变 workflow | 与 RouteCraft 的关键差异 |
|---|---|---|---|---|---|
| Sutton–Precup–Singh option | (o=(I,\pi_o,\beta_o)) | intra-option policy 直接选择环境 primitive actions | state/history-dependent | 可以决定行为路径 | RouteCraft 不学习/替换 Agent action policy；只固定调用哪一个**完整模型**，原 harness/workflow 仍决定 tool/action |
| Option-Critic | option policy + termination joint learning | 同上 | differentiable learned beta | 是 | 提供 termination 数学模板，但 RouteCraft beta 是少量可审计 event predicate，不应直接复制 end-to-end option RL |
| MoE temporal option / token expert | expert/token/layer | 模型内部计算路径 | token/segment | 改变模型内部执行 | 完全不是完整 LLM provider/model 的切换；cache、handoff、API、agent history 成本结构不同，不能混称 |
| EASy/GraphPlanner 类 milestone workflow | workflow node/role/model | 生成或修改 DAG/plan node | workflow milestone | **是** | 若收益只在重规划后出现，RouteCraft 贡献落入 workflow generation；它们是邻近工作而非固定-agent直接 baseline |
| task pinning | model | 全任务同一模型 | task terminal | 否 | 是 RouteCraft 的 `task_terminal` 退化情形 |
| per-call routing | model | 下一次 call | next call | 否 | 是 `next_call` 退化情形；RouteCraft 只有在中间边界真正被选择时才有独立价值 |

### 5.3 Options 理论能支持什么，不能支持什么

[Sutton et al. 1999](https://all.cs.umass.edu/pubs/1999/sutton_ps_AI99.pdf) 的 interruption theorem 在已知 (Q^\mu(h,o)<V^\mu(s)) 时允许提前终止，且在其假设下不会更差。它**没有 Router/switch/cache/handoff 成本**，而且 option 内部 policy 与 RouteCraft 的模型承诺不同。将这些成本加入 state/reward 后，净 interruption 条件才是本题需要的条件。

[Harb et al. 2018](https://ojs.aaai.org/index.php/AAAI/article/view/11794)把每次 option switch 的固定 deliberation cost (eta) 写入 reward，并使 termination advantage 带 margin (A(s,o)+\eta)。这为“不要因微小预测差频繁重路由”提供最直接理论先例；但作者在 Atari/option discovery 上实验，不能作为 LLM Agent 实证。

---

## 6. 命题 A：更多中间信息不一定降低真实系统成本

### 6.1 免费信息、无强制决策时的单调性

设粗信息 (Z_c) 是细信息 (Z_f) 的可测函数，即 (sigma(Z_c)\subseteq\sigma(Z_f))；策略集合允许细策略忽略额外信息，且观察、Router、切换不产生成本/不改变系统转移。对要最小化的 loss (L)，有

\[
\inf_{\pi\in\Pi(Z_f)}\mathbb E[L(\pi(Z_f))]
\le
\inf_{\pi\in\Pi(Z_c)}\mathbb E[L(\pi(Z_c))].
\]

证明只需注意每个 (Z_c)-measurable policy 也是 (Z_f)-measurable policy；细策略可以忽略新信息。这与 [Blackwell information ordering](https://doi.org/10.1214/aoms/1177729032) 的“更有信息的 experiment 不降低所有 decision problems 的可达效用”一致。

### 6.2 为什么真实 per-call routing 可变差

真实目标加入强制 deliberation 和 dynamics-changing overhead：

\[
L_{\rm sys}=L_{\rm task}
+N_r c_{\rm router}+N_s c_{\rm switch}
+C_{\rm cache-loss}+C_{\rm context}+C_{\rm handoff}.
\]

若细粒度方案规定每 call 调 Router，或切换会丢 cache/改变后续行为，则粗策略不再是同一“零成本子策略”；上面的集合包含关系对**总系统过程**不成立。

**数值反例。** 当前 cheap model 在下一段的预期总损失为 1.00；观察一个 tool result 后能完美识别是否需要 strong model，免费重选可把任务损失降到 0.92，信息价值 0.08。但一次 Router 0.02、cache/context replay 0.07、handoff/switch 0.06，总 overhead 0.15；真实 loss 1.07，劣于 pinning 的 1.00。额外信息提高了 oracle decision ability，却提高了系统成本。

**更强反例。** 即使最佳模型从不变化，mandatory per-call Router 每次花 0.01，10 calls 就增加 0.10；没有任何信息价值。若模型切换引发 agent 语气/计划不一致，还可能提高失败重试，差距更大。

这不是说“信息有害”，而是说**获取/处理/据此切换的策略有成本并改变转移**。因此论文应同时报告 `oracle without overhead` 与 `deployable oracle after all overhead`。

---

## 7. 命题 B：只在信息价值超过重决策成本时重路由

### 7.1 净值条件

令 (Q_t(h,m)) 是从 history (h) 开始、先用 (m) 到候选边界再遵循统一 continuation 的期望净效用（越大越好，且暂不含本次重决策成本）。重开 Router 的状态条件为

\[
\Delta_t(h)=
\mathbb E\!\left[
\max_m Q_t(H'_t,m)-Q_t(H'_t,m_{\rm current})
\mid H_t=h\right]
>
K_t,
\]

其中

\[
K_t=C_{\rm router}+C_{\rm switch}+C_{\rm cache/context}
+C_{\rm handoff}+C_{\rm added\ tail-risk}.
\]

若问题是“是否先等待下一 observation 再选”，标准 value of information 写成

\[
\operatorname{VOI}(O\mid h)=
\mathbb E_O\big[\max_m Q(h,O,m)\big]
-\max_m\mathbb E_O[Q(h,O,m)].
\]

它与 [Russell & Wefald 1991](https://doi.org/10.1016/0004-3702(91)90015-C) 和 [Callaway et al. 2018](https://www.auai.org/uai2018/proceedings/papers/269.pdf) 的 VOC 一致：计算/观察只在提高外部决策质量的期望值超过 computation cost 时值得做。

### 7.2 左侧怎样近似

优先级从可靠到复杂：

1. **matched fork direct estimate**：同一 state snapshot 上跑所有候选 (a=(m,\beta))，以 paired outcome 估计 (Q(a)-Q(a_{cur}))；
2. **supervised candidate-conditioned model**：预测 success/cost/latency/failure distribution，以 bootstrap/ensemble 得到 LCB/UCB；
3. **doubly robust/OPE**：仅在只有 logged partial actions 且有 positivity 时使用；
4. **offline RL**：只有需要估计多次未来重决策相互作用时才考虑，且必须处理 partial observability 与长 horizon variance。

对安全约束，选择应使用

\[
\operatorname{LCB}(\hat p_{succ}(z,m,\beta))\ge\tau
\]

并对高风险不可逆 action 设更高 (	au) 或强制 strong/pinned policy。

### 7.3 delayed terminal reward 的影响

终局 reward 使局部 (Q) 标签高方差、受 continuation 与之后恢复行为混杂。ETO 的 step-wise 失败是直接实证。常见错误是把 terminal success 回填为每一步相同标签；这会把先前错误但后来被强模型恢复的动作标成好动作。

缓解方法：

- 固定 common continuation policy，估计受控的局部分支效应；
- 在 verified milestone 提供可验证 intermediate outcome，但必须验证它预测 terminal success，不能用 LLM 自评替代；
- 同时预测 `probability of reaching next verified predicate` 和 terminal outcome；前者是 surrogate，不是最终 reward；
- 对长边界报告更宽 CI，必要时用 repeated rollout；
- 不同 continuation policy 下重新验证外部有效性。

[Callaway et al. 2018](https://www.auai.org/uai2018/proceedings/papers/269.pdf)还指出 myopic VOC 在多个 computation 具有互补性时会**过早停止**：单次 observation 不足以改变决策，但两次合起来足够。这是 RouteCraft 的反例之一；只估下一事件的 myopic gain 可能 under-route，需要至少纳入到候选边界的整段 value。

### 7.4 哪些阶段更可能发生 capability-demand drift

- **高**：外部 tool observation 到达；test/verifier fail；timeout/rate limit；新的文件/数据库 schema 被发现；context/cache compatibility 跨阈值；预算显著变化；不可逆 action 即将执行。
- **中**：明确 subgoal/milestone 被外部证据完成；retrieval 返回长/多模态内容；执行从规划转到实现。
- **低**：连续格式化/序列化 call；相同 evidence 下的纯文本改写；确定性 read-only tools 之间；没有新 observation 的内部反思。

由此 task pinning、milestone routing、per-call routing 分别在不同区域最优：demand 稳定/切换贵时 pinning；稀疏且可验证 drift 时 milestone；高频外部反馈、switch/cache 低且每次反馈改变能力需求时 per-call。

---

## 8. 命题 C：固定粒度可能接近最优

### 8.1 充分或近充分条件

下列任一条件可让 adaptive boundary 退化：

1. **dominant model**：存在 (m^*)，对所有可达 (s,\beta,m)，
   \[
   Q(s,m^*,\texttt{task_terminal})
   \ge Q(s,m,\beta)-K(s,m,\beta).
   \]
2. **跨阶段最优模型高度相关**：
   (Pr(\arg\max_m Q(S_{t+1},m)=\arg\max_m Q(S_t,m))\approx1)。新信息不改变排序。
3. **最小 switch/deliberation cost 高于最大可实现改进**：
   (sup_s\Delta(s)\le\inf_s K(s))。
4. **不可区分状态**：存在相同 (Z) 的 histories 需要相反模型选择，且 raw history 也无法可靠预测；任何 PlanIR Router 有 irreducible regret。
5. **terminal reward 无局部可识别性**：不同 `(model,boundary)` 的影响被 later continuation 完全抵消/放大，且无可信 milestone。
6. **边界不可验证**：`verified_milestone` 实际由强 LLM 猜测；Router 开销和错误触发超过收益。
7. **策略坍缩**：最优 (\beta) 几乎总为 `task_terminal` 或 `next_call`；RouteCraft 分别退化为 pinning 或 per-call router。

### 8.2 这些结果是否直接否定论文

- 若 1–3 在两个 benchmark、两个 harness、计入真实开销后均成立，**否定 adaptive commitment 作为方法贡献**。
- 若 4–6 成立，否定当前 PlanIR/边界定义，但可能支持“可观测性与 route-sufficient state benchmark”论文。
- 若 7 成立且退化比例 ≥90–95%、对应固定策略与 adaptive 的差 ≤1pp success 且 ≤5% cost/success，则 adaptive boundary 没有独立价值。
- 即使方法失败，same-state fork、cache/switch/retry 全成本测量、跨 harness state taxonomy 仍可形成 benchmark/measurement/negative-result 论文；前提是结论覆盖有代表性的状态，而不是只采不确定样本。

---

## 9. Matched same-state fork：能估计什么因果量

### 9.1 明确 estimand

以 pre-decision snapshot (i) 为实验单元，候选 (a=(m,\beta))。令

\[
Y_i(a;\pi_c)
\]

表示从同一 harness state + world snapshot 出发，先执行 commitment (a)，边界触发后用固定 continuation policy (\pi_c) 直到任务终止的潜在结果。全分支可执行时，局部 controlled effect 为

\[
\tau_{a,a'}^{\pi_c}
=\mathbb E_i[Y_i(a;\pi_c)-Y_i(a';\pi_c)].
\]

它估计的是**在该 state 分布和该 continuation 下，commitment 的受控局部效应**；不是任意未来 adaptive Router policy 的总体效应，也不自动跨 continuation/harness/provider 外推。

识别条件：

1. **consistency**：实现的 `(model,boundary)` 与定义一致；
2. **snapshot fidelity**：每分支初始 harness 与外部世界相同，隐藏 provider state 的处理属于明确 treatment 定义；
3. **no interference**：一个 fork 不改变另一个 fork 的外部世界、queue、rate-limit 或 cache；
4. **common continuation**：边界后政策相同且只依赖可记录的 handed-off state；
5. **randomized order/seeds**：时间/load/provider drift 不与 action 系统绑定；
6. **完整或已知分配概率**：若不是全分支，选择/分配机制可记录。

### 9.2 common continuation policy 的作用与局限

作用：把“这段 commitment 的影响”与“之后 Router 的不同选择”分开，减少 delayed reward 的不可比性。建议主分析用固定、稳定的 strong continuation；另做 original-model continuation 检验外部有效性。

局限：boundary 产生的不同 state、context、错误和 cache 是 treatment 的 mediator，必须保留；不能强行把 fork 的输出改写成同一文本。common continuation 只是后续**决策规则相同**，不是后续状态相同。若某 provider-private state 只有原模型可读，跨模型 treatment 应包括 state loss/replay cost；若无法定义可比 handoff，则标为 incompatible，而非静默丢弃。

### 9.3 `task_terminal` 边界

`task_terminal` 没有 (\pi_c) 段：该 model 从 state 运行至结束，结果就是完整 remaining-task outcome。它与短边界的比较仍可做，但 duration、累计上下文和失败恢复均不同，必须全部计入。不能只比较“到各自边界的局部质量”。对于未在预算内终止的分支，用 timeout/censoring 与 failure type，不要把最大观察成本当普通完成值。

### 9.4 snapshot 分层

| benchmark | 必需快照 | 常见遗漏偏差 |
|---|---|---|
| SWE-bench | repo commit、worktree/patch、容器镜像与依赖、文件权限、进程、test cache、env vars、随机种子、时间/网络 mock | 只 fork chat history 会让分支看到不同文件系统；依赖下载和测试缓存造成成本/延迟偏差 |
| τ²-Bench | simulator DB/slot、用户状态、conversation event、tool side effects、policy/rules、RNG、time | 订单/账户修改未回滚导致 interference；模拟用户 stochasticity 未对齐 |
| AppWorld | AppWorld DB snapshot、app/API state、filesystem、time、task evaluator、RNG | DB 事务与外部 app state 不一致；同名 API 非确定输出 |
| 外部网络/API | 录制响应或版本化 sandbox；若必须 live，交错随机顺序和时间 block | 搜索结果、rate-limit、价格、provider model version 漂移，破坏 same-state |

snapshot 不完整带来的不是普通噪声，而是 consistency violation：所谓“同一 state”其实不同，paired difference 会混合模型效应和世界差异。IPS/DR **不能修复未观察 hidden state 或 snapshot 错误**。

### 9.5 随机输出、重复次数与 common random numbers

先每 branch 做 3 次 pilot，估计 state×action 方差、branch ranking 稳定性与 intra-class correlation；随后顺序追加到 5，只有排序 CI 重叠或高价值 state 才到 10。不要固定宣称 3 次足够：独立 Bernoulli (p=0.5) 若要 ±5pp 95% 半宽约需 385 次，Agent fork 只能通过 paired design、确定性 verifier、分层与较粗决策 margin 降低需要。

推荐停止重复的操作标准：

- paired utility difference 的 95% CI 已完全越过 practical margin；或
- 达到 5 repeats 后仍无法分开，标作 `stochastically ambiguous`，不强造 hard label；
- 若从 3 增到 5 seeds 后 >15% states 的 branch winner 翻转，或 winner ranking Kendall (	au<0.8)，反事实标签成本/稳定性进入 No-Go 审查。

对可控 simulator，可用 common random numbers（CRN）降低 paired difference 方差，但不能只给两分支相同 base seed。2026 年预印本 [Event-keyed hashing](https://arxiv.org/abs/2603.11084)指出：intervention 改变控制流后，stateful PRNG 的相同 draw index 不再对应相同 modeled event，会产生因果不一致。应以 `(task,state,event-id,replicate)` 生成 counter-based RNG；provider LLM sampling 若无法 event-key，应独立采样并记录。

[Yadav et al. 2026](https://arxiv.org/abs/2605.04732)给出更细警告：所有阶段盲目共享随机数甚至可使 value-difference 方差**高于独立模拟**；当两个候选在 depth (d) 后采用相同 rollout policy 时，只在共同 continuation 后做 depth-dependent coupling 才有不增方差的理论保证。这非常适合本设计：commitment 段独立，进入 (\pi_c) 后按事件键耦合。

### 9.6 IPS / DR 何时需要

- **全 action matched fork 或在 state 内随机分配并直接观察候选结果**：paired mean/difference 已是自然估计；不需要 IPS/DR。
- **logged bandit data，只看到行为 policy 选择的一个 action**：若 propensity 已知/可估、positivity 成立，可用 IPS；[Li et al. 2010](https://arxiv.org/abs/1003.5956)的 replay evaluator也依赖随机 logging policy 覆盖。
- **想减小 IPS 方差**：可用 [Dudík et al. 2011](https://icml.cc/2011/papers/554_icmlpaper.pdf) 的 DR；其一致性依赖 propensity 或 reward model 至少一个正确（有限样本仍受误差/overlap 影响），且需要 sample splitting/cross-fitting 避免同数据过拟合。
- **长序列 logged policy**：可用 [Jiang & Li 2016](https://proceedings.mlr.press/v48/jiang16.html) 的 sequential DR，但 importance ratio 方差随 horizon 增长，不能替代实验 fork。
- **只在高不确定 state 做 fork，想估全体 state ATE**：若每个 state 的 inclusion probability 已知且随机 anchor 提供 positivity，可对 selection 做 IPW/DR；否则只能声明 active-sampled conditional estimand。

### 9.7 active sampling 与组合爆炸

Phase 0 的 2 models × 4 boundaries 是 8 branches/state；500 states、3 repeats 已是 12,000 runs。建议：

- 25–30% **random anchor states** 跑全 8 branches，保持 population coverage 与 unbiased Oracle-space 测量；
- 40–50% 由简单模型分歧/uncertainty 采样，只跑 current、top-2 actions 与相邻 boundaries；
- 20–30% 按 stage/task/error/reversibility/cache strata 做 coverage quota；
- task-terminal 可早停/预算截断；若某 model 在 random anchors 被另一 model 在 success、cost、latency上稳健支配，对低风险 active states 使用 sequential elimination；
- 保留少量 `random action` anchor 来检验 active learner 是否漏掉反转；记录所有 inclusion/action probabilities。

不要在 active-only 数据上报告“全部 Agent states 的反转率”。主文分别报告 random-anchor population estimate、active hard-slice estimate 与加权 estimate。

---

## 10. Phase 0：一周内最快证伪

### 10.1 一周版最小实验（先不训练大 Router）

为了在一周内否定核心假设，建议比完整 Phase 0 更窄：

- 80–100 tasks：τ²-Bench 40–50，SWE-bench Verified 40–50；
- 每任务取 1–2 个可恢复 event state，共 120–200 states；
- 两个能力/价格明显不同且 tool API 都稳定的模型；
- 四个 boundaries；
- random anchor 40–50 states 跑全 8 actions × 3 seeds；其余 states 用 disagreement/coverage 选 3–4 actions × 3 seeds；
- 所有分支使用确定性 verifier；先不训练 0.5B Router，只训练 Logistic/LightGBM/kNN。

**最重要的实验不是 Router accuracy，而是 full-cost dynamic Oracle room。** 先回答：

1. random anchors 上是否有稳健 model winner reversal / boundary winner reversal？
2. 扣除 Router、cache loss、context replay、handoff、retry 后，model×boundary Oracle 是否仍超过 best task pinning？
3. 最佳单一固定 boundary 已捕获多少 Oracle gain？
4. pre-decision PlanIR v0 是否能 out-of-task 预测反转？

### 10.2 三个可检验核心假设

**H1：状态依赖的净反转存在。** 至少 20% random-anchor states 在两模型或两边界之间出现跨 3 seeds 稳定的 winner reversal，且差异超过 practical margin，而非纯噪声。

**H2：自适应边界有超越固定粒度的 Oracle 空间。** 计全成本后，dynamic model×boundary Oracle 相对 best task pinning 提高至少 5pp success（相近 cost）或降低至少 15% cost/success（相近 success）；且任何单一固定 boundary 捕获不超过 80–90% 的 dynamic Oracle gain。

**H3：可部署表示可预测反转。** group-by-task held-out 上，PlanIR v0 + LightGBM 至少恢复 30–40% 的可实现 Oracle gain，校准优于 prompt-only/capability matcher，并且 Router overhead < gross saving 的 25%（同时最好 < task cost/latency 的 5%）。

### 10.3 Oracle 与统计协议

对 loss (J)（越低越好），定义 fixed-boundary 回收比例：

\[
G_{\rm fixed}(b)=
\frac{J_{\rm pin}-J_{\rm fixed(b)}}
{J_{\rm pin}-J_{\rm oracle}}.
\]

同一数据上取 action 最小值会产生 optimistic Oracle bias；必须对 oracle policy/threshold 用 nested cross-fitting 或在 train states 选择、held-out task states 评估。纯“每个测试 state 选 observed minimum”只能标为 in-sample empirical oracle upper bound。

统计要求：

- task family 宏平均；SWE/τ² 分别报告再平均；
- paired task/state bootstrap，cluster 至 task，不把同 task sibling states 当独立；
- success 用 paired bootstrap / randomization interval；cost/success 用 two-part bootstrap（成功率与成功任务成本），并同时在共同完成实例交集报告条件成本，避免只失败更多而显得便宜；
- p50/p95 latency 分别报告，p95 用 cluster bootstrap；
- 预注册 primary utility/约束；多 boundary pair 比较用 Holm 或把它们列为探索性；
- 每个 CI 同时给 absolute effect 与 normalized oracle gain，不只给 p-value。

### 10.4 修订后的停止条件

| 建议条件 | 修订后的可执行判据 | 决策 |
|---|---|---|
| 固定边界拿到 ≥95% Oracle gain | 只有当 95% CI **下界** ≥0.95，且 adaptive 对最佳 fixed 的绝对剩余收益 95% CI 上界 <1pp success 且 <5% cost/success，才停止 | 停 adaptive boundary；保留 fixed event routing measurement |
| dynamic Oracle 无 3–5pp / 10% 空间 | one-sided 95% CI 上界同时 ≤3pp success 且 ≤10% cost/success reduction（计全开销） | 核心方法 No-Go |
| Router overhead >5% | 5% 不是统计定律。若 overhead > task cost 或 p95 latency 的 5%，或 > gross Oracle saving 的 25–33%，触发简化 | 先退到规则/GBM；不是直接否定现象 |
| PlanIR+LightGBM 不优于 raw/matcher | 在 held-out task 的 normalized regret、Brier/ECE、under-routing recall 上无稳定增量；大 Router 只有能多恢复 ≥5% oracle gain 或在同效用下降低 ≥10% input/latency 才继续 | 停大 Router |
| 收益在固定 Agent 计划后消失 | fork 必须冻结原 workflow；若只有允许 replanning 才有收益 | RouteCraft 方法 No-Go，归入 workflow generation |
| boundary collapse | ≥90–95% actions 选同一个 boundary，且 adaptive vs 对应 fixed ≤1pp success / ≤5% cost/success | adaptive commitment 无独立价值 |
| 重复过多 | 3→5 repeats 后 >15% winner 翻转或 Kendall τ<0.8；5 repeats 的大多数关键 pair CI 仍跨 practical margin | 反事实训练成本警报；转 measurement/减少 action pool |

### 10.5 足以继续投入的结果

同时满足以下四项才进入完整 6–8 周 MVP：

1. full-cost dynamic Oracle 相对 pinning ≥5pp success 或 ≥15% cost/success，并有 paired 95% CI 支持；
2. 最佳 fixed boundary 捕获 <80–90% dynamic gain；
3. ≥20% random-anchor states 出现可重复反转，且集中在 observation/verification/recovery 等有机制解释的事件；
4. PlanIR v0 + LightGBM 在 held-out task 恢复 ≥30–40% Oracle gain，Router+compiler overhead 未吃掉大部分收益。

若只满足 1–2 而 3–4 不满足，适合做 benchmark/Oracle-space measurement；若 1 都不满足，应 No-Go adaptive router。

---

## 11. 成本 estimand 与 matched-fork 记账

候选加法模型是好的日志 schema，但需要避免重叠并增加 amortization、失败分母与 tail risk：

\[
C_i=
\frac{C_{\rm ingest}+C_{\rm profile}+C_{\rm train}}{N_{\rm served}}
+\sum_t\left(
C_{\rm model,t}+C_{\rm router,t}+C_{\rm tool,t}+C_{\rm judge,t}
+C_{\rm retry,t}+C_{\rm switch,t}+C_{\rm replay,t}
\right)+C_{\rm infra,idle/load}.
\]

其中 `retry` 是重试触发的额外 model/tool/replay 的**归因标签**；若这些 token 已计入 `model/tool/replay`，就不能再把完整 retry span 二次相加。推荐事件账本先逐资源计费，再用 cause tags 分解。

核心 population metric：

\[
\operatorname{CostPerSuccess}
=\frac{\sum_i C_i}{\sum_i \mathbf 1\{success_i\}},
\]

并报告 macro task-family 版本。另报共同完成实例交集上的 conditional cost，但不能用它代替上式。对 timeout/无 deliverable，成本仍进入分子，成功为零。queue/load/tail latency 不一定能折算 USD，应作为独立多目标约束；能耗也独立报告。

fork 对边界的成本必须包括：

- commitment 段模型 fresh/cache-read/cache-write/output/reasoning；
- Router compiler/scorer；
- tool、judge/verifier；
- 切换后的 prefix/KV loss、重新序列化/编码、provider-private state 失效；
- model loading/residency、queue/batching、网络；
- handoff 引起的额外 turn、retry、恢复和行为不一致；
- boundary 后 common continuation 的 terminal cost。

ClawTrace 提供直接测量依据：其成本按 fresh input、output、cacheRead、cacheWrite 四种费率分开；论文样本中 cache-read 占 input volume 30–50%，按 fresh input 计会把真实成本高估 1.6–2.0×（仅限其 OpenClaw+gpt-5.4/SpreadsheetBench 设置）。这说明 benchmark 必须默认启用合理 prompt cache，不能用未缓存 full-context 人为扩大 baseline。

---

## 12. Ablation—研究主张映射

| Ablation | 验证/证伪的具体主张 | 预期解读 |
|---|---|---|
| prompt-only vs raw trajectory vs PlanIR | 中间历史是否有增量；PlanIR 是否 route-sufficient | PlanIR 只需接近 raw 的 regret，不需重构 history；若 raw+PlanIR 仍明显更好，PlanIR 过压缩 |
| 去掉语义状态，仅系统事实 | teacher semantic fields 是否必要 | 若不降，移除 subgoal/capability，降低成本与泄漏；若降，必须检查这些字段不是 hindsight |
| 外部 verifier → LLM milestone judge | 可验证边界是否是关键机制 | 若 LLM judge 同样好需计 judge 成本与校准；若回退，支持 verified milestone 定义 |
| 去 boundary head，只选 model | 自适应 commitment 是否有独立贡献 | 若等价，论文收窄为 model router/measurement |
| 固定 model，只学 boundary | 收益来自“何时重决策”还是模型能力差异 | 若仍有收益，说明 routing overhead scheduling 本身重要；否则联合交互为主 |
| fixed model-ID vs candidate-conditioned | profile 是否支持 model transfer | leave-one-model-out 是主检验；seen-model 更高不证明 unseen 支持 |
| logged terminal outcome vs matched fork | observational/hindsight label 偏差有多大 | 若 logged 同样好，fork 可能不值成本；若 fork 显著改善校准/regret，构成 benchmark 贡献 |
| 成功-only vs 成功+失败+恢复 | recovery state 是否贡献 under-routing recall | 重点看 recovery slice，而不只总体 accuracy |
| 忽略 cache/switch penalty | 动态收益是否是错误成本模型产物 | 若 oracle 优势消失，方法 No-Go、measurement 仍有价值 |
| teacher label vs actual execution label | capability/progress 描述是否可信 | teacher 字段只可作 weak auxiliary；执行标签应主导 |
| Router per-call vs event-only | 中间信息收益是否超过 deliberation cost | 同时比较净 cost/success、p95、switch 数，不只 routing accuracy |
| 单 harness vs 跨 harness | PlanIR 是否依赖事件 schema/隐式 workflow | 单 harness 成功不能支持通用性；第二 harness 至少需要薄 adapter 与共同 IR |

---

## 13. 6–8 周 MVP 建议（仅在 Phase 0 通过后）

| 周 | 交付 | 退出检查 |
|---|---|---|
| 1 | 固定两模型/两个 benchmark/harness commit；world snapshot；40–50 random anchors 全分支 | snapshot 重放 verifier 一致率应接近 100%；外部 nondeterminism 有记录 |
| 2 | 120–200 states fork；三 seeds；全成本事件账本；in-sample empirical oracle 与 nested held-out oracle | full-cost Oracle room 不达阈值则停止方法开发 |
| 3 | deterministic PlanIR v0；leakage audit；Logistic/kNN/LightGBM | group-by-task split；若 system facts 已足够则不做语义教师 |
| 4 | offline RouteCard teacher 仅生成 subgoal/obligation；逐字段 evidence alignment；success/failure/recovery 数据 | 无法与 pre-state 工具/谓词对齐的字段全部降 weak/drop |
| 5 | candidate profile/probe；leave-one-model-out；cost/latency quantile 与 calibration | unseen model LCB 覆盖差则不宣称泛化 |
| 6 | end-to-end event router；fixed boundaries/pinning/per-call baselines；paired bootstrap | adaptive vs best fixed 的独立收益必须存在 |
| 7 | 第二 harness 薄 adapter；跨 harness PlanIR sufficiency；price/load shift | 若只在首 harness 成立，结论降为 harness-specific |
| 8 | ablation、failure taxonomy、artifact/SHA、负结果审计 | 预注册 stop conditions，不因结果临时改 primary metric |

---

## 14. 最终科研判断与更窄替代问题

### 判断

**`Revise`。** 理论上联合 `(model, termination predicate)` 完全可表述为 option-inspired event-driven SMDP；deliberation/VOC 也为自适应 commitment 提供清晰目标。但理论只说明问题形式合理，不说明 Agent 中存在足够大的净收益。现有轨迹文献同时给出三类失败条件：terminal reward 难局部归因（ETO）、压缩语义/规则跨域过拟合（ClawTrace）、更多教师/rollout/数据非单调（AgentArk、ProAct）。

因此不建议当前就把论文主张写成“Plan-state distillation enables a general adaptive Router”，更不建议先训练 0.5B–1.5B Router 或 offline RL。

### 更窄、更稳妥的研究问题

> **在固定 Agent workflow、可恢复的 harness event states 和真实 cache/switch/retry 成本下，哪些外部可验证事件具有正的 model re-routing value，固定 event boundary 能否捕获几乎全部动态 Oracle 收益？**

这个问题有三种都可发表的结果：

- adaptive boundary 的净 Oracle 空间显著且可预测 → 再升级 RouteCraft 方法；
- 某个固定 observation/verified boundary 已捕获 ≥95% 收益 → 得到简洁的系统设计/负方法结论；
- 扣全成本后 dynamic Oracle 无空间 → 得到“为何 per-call Agent routing 不省钱”的 measurement/negative-result。

### 一周内最能否定核心假设的单个实验

**不训练 Router，直接做 40–50 个 random-anchor states 的全 2×4 matched fork（3 seeds），使用 event-keyed snapshot/RNG、统一 strong continuation、确定性 verifier和完整 cache/switch/retry 记账；用 held-out/nested bootstrap 比较 dynamic Oracle、best task pinning 与四个 fixed-boundary Oracles。**

若扣除全开销后 dynamic Oracle 的 one-sided 95% CI 上界同时不超过 +3pp success 与 10% cost/success reduction，立即停止 adaptive commitment 方法；这是最快、最少平台建设、且不会被 Router 拟合失败混淆的证伪。

---

## 15. 一手来源索引

### 15.1 Agent 轨迹、计划与蒸馏

1. FireAct — [arXiv 2310.05915](https://arxiv.org/abs/2310.05915), [project](https://fireact-agent.github.io/), [official GitHub](https://github.com/anchen1011/FireAct). 项目 BibTeX 仍标 `@misc/arXiv`，正式录用未核验。
2. ToolLLM/ToolBench — [OpenReview ICLR 2024](https://openreview.net/forum?id=dHng2O0Jjr), [arXiv 2307.16789](https://arxiv.org/abs/2307.16789), [official GitHub](https://github.com/OpenBMB/ToolBench).
3. ToolPreference/TP-LLaMA — [NeurIPS 2024 paper](https://proceedings.neurips.cc/paper_files/paper/2024/file/c0f7ee1901fef1da4dae2b88dfd43195-Paper-Conference.pdf), [arXiv 2406.07115](https://arxiv.org/abs/2406.07115), [official author dataset](https://huggingface.co/datasets/chrissiecsj/ToolPreference). 完整训练代码未核验。
4. ETO — [ACL Anthology 2024 long.409](https://aclanthology.org/2024.acl-long.409/), [official GitHub](https://github.com/Yifan-Song793/ETO).
5. MAGDi — [ICML 2024 PMLR](https://proceedings.mlr.press/v235/chen24ah.html), [official GitHub](https://github.com/dinobby/MAGDi).
6. Agentic Plan Caching — [NeurIPS 2025 proceedings](https://proceedings.neurips.cc/paper_files/paper/2025/hash/9549f7d06700f0966d5f938f1d11022a-Abstract-Conference.html), [arXiv 2506.14852](https://arxiv.org/abs/2506.14852), [author publication page](https://alex-q-z.github.io/research.html). 作者页该条未提供 code link；官方代码未核验。
7. AgentRefine — [OpenReview ICLR 2025](https://openreview.net/forum?id=FDimWzmcWn), [project](https://agentrefine.github.io/), [official GitHub](https://github.com/Fu-Dayuan/AgentRefine). Repo 明示数据已发布、inference/model 仍待发布，因此标“部分开源”。
8. Exploring Expert Failures — [arXiv 2504.13145 v2](https://arxiv.org/abs/2504.13145), [ICLR 2026 under-review PDF](https://openreview.net/pdf?id=4fh0Z9nwjx). 接收与官方代码均未核验；本地以 arXiv v2 五作者版本为准。
9. ProAct — [arXiv 2602.05327](https://arxiv.org/abs/2602.05327), [official GitHub](https://github.com/GreatX3/ProAct). 截止日为 preprint。
10. AgentArk — [arXiv 2602.03955 v3](https://arxiv.org/abs/2602.03955), [official GitHub](https://github.com/AIFrontierLab/AgentArk). 截止日为 preprint。
11. ClawTrace — [arXiv 2604.23853 v2](https://arxiv.org/abs/2604.23853), [official GitHub](https://github.com/epsilla-cloud/clawtrace). arXiv comments 核验为 CAIS 2026 Agent Skills '26 Workshop accepted。

### 15.2 理论与实验方法

1. Blackwell (1953), *Equivalent Comparisons of Experiments* — [Project Euclid/DOI](https://doi.org/10.1214/aoms/1177729032).
2. Russell & Wefald (1991), *Principles of Metareasoning* — [Elsevier/DOI](https://doi.org/10.1016/0004-3702(91)90015-C). 本地只有 CMU archive 的 1 页摘要扫描，非全文。
3. Sutton, Precup & Singh (1999), *Between MDPs and Semi-MDPs: A Framework for Temporal Abstraction in Reinforcement Learning* — [DOI](https://doi.org/10.1016/S0004-3702(99)00052-1), [official UMass PDF](https://all.cs.umass.edu/pubs/1999/sutton_ps_AI99.pdf).
4. Tishby, Pereira & Bialek (2000), *The Information Bottleneck Method* — [arXiv physics/0004057](https://arxiv.org/abs/physics/0004057).
5. Li, Walsh & Littman (2006), *Towards a Unified Theory of State Abstraction for MDPs* — [author PDF](https://thomasjwalsh.net/pub/aima06Towards.pdf).
6. Li et al. (2010), *Unbiased Offline Evaluation of Contextual-bandit-based News Article Recommendation Algorithms* — [arXiv 1003.5956](https://arxiv.org/abs/1003.5956).
7. Dudík, Langford & Li (2011), *Doubly Robust Policy Evaluation and Learning* — [official ICML PDF](https://icml.cc/2011/papers/554_icmlpaper.pdf).
8. Jiang & Li (2016), *Doubly Robust Off-policy Value Evaluation for Reinforcement Learning* — [PMLR](https://proceedings.mlr.press/v48/jiang16.html).
9. Bacon, Harb & Precup (2017), *The Option-Critic Architecture* — [AAAI](https://ojs.aaai.org/index.php/AAAI/article/view/10916).
10. Harb et al. (2018), *When Waiting Is Not an Option: Learning Options with a Deliberation Cost* — [AAAI](https://ojs.aaai.org/index.php/AAAI/article/view/11794), [arXiv 1709.04571](https://arxiv.org/abs/1709.04571).
11. Callaway et al. (2018), *Learning to Select Computations* — [official UAI PDF](https://www.auai.org/uai2018/proceedings/papers/269.pdf).
12. Buffalo, Pearson & Klein (2026), *Realizing Common Random Numbers: Event-Keyed Hashing for Causally Valid Stochastic Models* — [arXiv 2603.11084](https://arxiv.org/abs/2603.11084), preprint。
13. Yadav et al. (2026), *Using Common Random Numbers for Simulation-based Planning with Rollouts* — [arXiv 2605.04732](https://arxiv.org/abs/2605.04732), journal reference: Reinforcement Learning Journal 2026。
14. Glasserman & Yao (1992), *Some Guidelines and Guarantees for Common Random Numbers* — [INFORMS/DOI](https://doi.org/10.1287/mnsc.38.6.884). 官方全文未本地归档。

---

## 16. 本地 PDF 归档与 SHA256

机器可校验的独立清单另存为 [`papers/SHA256SUMS_C.txt`](../papers/SHA256SUMS_C.txt)；下列 24 项已于 2026-08-17 重新计算，索引与磁盘文件逐项一致。

### `papers/04_trajectory_distillation`

| 文件 | 页数 | bytes | SHA256 |
|---|---:|---:|---|
| `2023_FireAct_arXiv2310.05915.pdf` | 28 | 785239 | `f25210a50e197285f404c5a17e437fa93c21f3ab6a9db8687985b6d8613a773f` |
| `2024_ETO_ACL.pdf` | 17 | 2044057 | `63bad5458845c942dafa9734ad80ee3c65f9cea04afc28e5fbb3f6e9628a10f3` |
| `2024_MAGDi_ICML.pdf` | 16 | 1913151 | `dc1a7f21536b8e044871d9aa823e45495e64940361fab4a8a6cc77894696c3ac` |
| `2024_ToolLLM_ToolBench_ICLR.pdf` | 24 | 2048075 | `295299721d67b250661fb6598bee86a2e9fe766241fdc08dd7cf389e984b4d1a` |
| `2024_ToolPreference_TP-LLaMA_NeurIPS.pdf` | 20 | 1645349 | `129c1cc1c0b966c389929135d5ca59980ee0c61a933f1568dab916f665799f97` |
| `2025_Agentic_Plan_Caching_NeurIPS.pdf` | 27 | 839168 | `f3968cfa5142fdf55adc834e8ada19b1ab1ccc81c7a3291b9166b4ca52e6637f` |
| `2025_AgentRefine_ICLR.pdf` | 20 | 1216481 | `1f4570144eaea3f1bd4ac97b362b08784ca1cde4d116656d002bd1ca23e20200` |
| `2025_Exploring_Expert_Failures_arXiv2504.13145.pdf` | 21 | 580414 | `05388c16a22ed15cbdded054b6b550e8e8fe6c3243f4b1f1bd4b6db339dc0a7c` |
| `2026_AgentArk_arXiv2602.03955.pdf` | 32 | 1777448 | `76c46555e41da9b1dd411d000ff31d2ecbcd6c6189f94a7d1e50cc3b4ef14601` |
| `2026_ClawTrace_arXiv2604.23853.pdf` | 14 | 4220511 | `49098ff67e2cf76f9621e8690f778f2e95c82bac83e4db807a77fdda095caa34` |
| `2026_ProAct_arXiv2602.05327.pdf` | 22 | 1220888 | `764794b51e9509dba6080099e131fbb8df72a67e8755734c1df7efe1f0e545d7` |

### `papers/05_theory_methods`

| 文件 | 页数 | bytes | SHA256 | 备注 |
|---|---:|---:|---|---|
| `1953_Blackwell_Equivalent_Comparisons.pdf` | 8 | 794785 | `f490b8395187edc34ab46a3d45455f1f59cbbc9632964c63218a2f4c8ba8cd1d` | Project Euclid 全文 |
| `1991_Principles_of_Metareasoning_abstract_only.pdf` | 1 | 123728 | `957ade260771c5ff84ed17210896806535b0198e192b3f7de93d40937bcc01a5` | **仅摘要扫描，不是全文** |
| `1999_Options_SMDP_Sutton_Precup_Singh.pdf` | 31 | 829204 | `124fbfc2a35d22a08d80abf3298d6c24ed87bc972e5cdd8847f0342740bd3485` | 已修复此前 0 字节文件 |
| `2000_Information_Bottleneck.pdf` | 16 | 136267 | `afdbc45366b590086e34faef76ad0570885884489ed32233c8571912ef92ef47` | 全文 |
| `2006_State_Abstraction_MDP.pdf` | 10 | 307868 | `647308a72fe5a2f692089f1672ce570722b0b51eb3f5f18a0420561b96628dcd` | 全文 |
| `2010_Unbiased_Offline_Evaluation_Contextual_Bandit.pdf` | 10 | 319760 | `ea72ce425888ae8adba1957a9f0acbef7ed0dc232a52982b9e7424d7ef73ae19` | 全文 |
| `2011_Doubly_Robust_Contextual_Bandit.pdf` | 8 | 116595 | `b63fd729da1750f709e4867fbff49a62a47d08f7167c202a4ba2791a5816174e` | 全文 |
| `2016_Doubly_Robust_OPE_RL.pdf` | 14 | 500519 | `df2a2a5c0e5eb6545413143ad44ea185bc97d7f08d56d2308263825791e459e9` | 全文 |
| `2017_Option_Critic_AAAI.pdf` | 9 | 815129 | `d8089c6012c607f3a9e8b560290dea629c91b174e246e18864ac6615467e208f` | 全文 |
| `2018_Deliberation_Cost_AAAI.pdf` | 8 | 928893 | `552ab27409772a04040714533ae827cae0775e2a069cb2df46af35f397184ce2` | 全文 |
| `2018_Learning_to_Select_Computations_UAI.pdf` | 10 | 2591204 | `e8b2aa2b2229f75080f1fcd923b0230b84ba96ab6ac0b929db1af268d4e9e7bb` | 全文 |
| `2026_Common_Random_Numbers_Rollouts.pdf` | 17 | 1609825 | `24bdf61810876afc09be78e7ba9313ce4302a3772e597b830a21cc303a6a9c11` | 全文 |
| `2026_Event_Keyed_Common_Random_Numbers.pdf` | 20 | 684726 | `b6f4e4fda29f75b4e08b2df8c42f51d436b1db50b74c15728c5be4772e568390` | 全文 |

---

## 17. 未核验与避免误读

- FireAct 的正式会议录用状态未核验，按 arXiv preprint 处理。
- Agentic Plan Caching 官方代码未核验；作者 official publication page 该条只列 paper/bibtex。
- ToolPreference 发布了官方数据集，但完整训练代码未核验。
- AgentRefine official GitHub 截止核验日不是完整复现实装，不能仅因 repo 存在就写“代码完整开源”。
- Exploring Expert Failures 的 ICLR 2026 页面仅支持“under review/submission”，未核验接收；官方代码未核验。
- ProAct、AgentArk 截止日按 arXiv preprint，不补写未来会议状态。
- ClawTrace 是 workshop accepted，不是 CAIS 主会 full paper；其全部实证限于单一 OpenClaw + gpt-5.4，不能外推到所有 harness/model。
- RouteCraft 与 Options 的关系是**建模类比**。Options 控制 primitive actions；RouteCraft 只承诺完整模型而保持 Agent workflow，不是 MoE expert routing，也不是已有 option method 的直接重命名。
- 信息瓶颈、state abstraction、VOC 提供分析语言，不构成 PlanIR 充分或 adaptive routing 必胜的证明。
