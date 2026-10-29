# Paper feedback and ranking seeds

Scores 1–5 are explicit preference ratings. A blank score means the paper was mailed but not rated; blank-score rows are not positive seeds and contribute only a very small negative signal.

| 论文名 | arXiv 页面链接 | 打分 | TLDR（核心贡献） |
| --- | --- | ---: | --- |
| Qwen Technical Report | https://arxiv.org/abs/2309.16609 | 4 | 报告 Qwen 基础模型、对话模型及代码和数学模型的训练与能力表现。 |
| Qwen2 Technical Report | https://arxiv.org/abs/2407.10671 | 4 | 介绍覆盖不同规模的稠密与 MoE 模型系列及其多语言和多任务评测。 |
| Qwen2.5 Technical Report | https://arxiv.org/abs/2412.15115 | 4 | 通过扩大预训练数据并改进后训练，构建面向多种规模和任务的模型系列。 |
| Qwen2.5-1M Technical Report | https://arxiv.org/abs/2501.15383 | 5 | 结合长上下文训练、稀疏注意力、分块预填充与推理引擎优化支持百万 token 上下文。 |
| Qwen3 Technical Report | https://arxiv.org/abs/2505.09388 | 4 | 报告支持思考与非思考模式的模型系列，并介绍稠密和 MoE 模型的训练与评测。 |
| DeepSeek LLM | https://arxiv.org/abs/2401.02954 | 4 | 总结开源模型的大规模预训练、数据与规模定律分析，以及训练配置选择。 |
| DeepSeek-V2 | https://arxiv.org/abs/2405.04434 | 5 | 结合多头潜在注意力压缩 KV Cache，并以 MoE 架构降低推理开销。 |
| DeepSeek-V3 Technical Report | https://arxiv.org/abs/2412.19437 | 5 | 报告基于 MoE、MLA 和多 token 预测的模型训练与高效推理实践。 |
| DeepSeek-R1 | https://arxiv.org/abs/2501.12948 | 3 | 通过强化学习及冷启动数据提升模型的长链推理能力。 |
| Hunyuan-Large | https://arxiv.org/abs/2411.02265 | 4 | 报告大规模 MoE 模型，并探索 KV Cache 压缩和专家路由等实践。 |
| Hunyuan-A13B Technical Report | https://arxiv.org/abs/2609.27284 | 4 | 介绍总参数 80B、推理激活 13B 的 MoE 模型及其训练和推理设计。 |
| ChatGLM: A Family of Large Language Models from GLM-130B to GLM-4 All Tools | https://arxiv.org/abs/2406.12793 | 4 | 回顾 GLM 模型系列演进，并介绍 GLM-4 的长上下文、多语言和工具使用能力。 |
| GLM-4.5: Agentic, Reasoning, and Coding Foundation Models | https://arxiv.org/abs/2508.06471 | 4 | 构建兼顾智能体、推理与代码任务的 MoE 基础模型，并支持思考和直接回答模式。 |
| Llama 2 | https://arxiv.org/abs/2307.09288 | 5 | 报告开放基础模型与对话模型，并比较 GQA 对 KV Cache 和推理效率的影响。 |
| The Llama 3 Herd of Models | https://arxiv.org/abs/2407.21783 | 4 | 系统报告 Llama 3 基础模型的训练、能力评估及多模态扩展。 |
| Mistral 7B | https://arxiv.org/abs/2310.06825 | 5 | 将分组查询注意力与滑动窗口注意力用于高效的小型语言模型。 |
| Mixtral of Experts | https://arxiv.org/abs/2401.04088 | 4 | 采用每 token 激活两个专家的稀疏 MoE 架构，以有限计算调用更大参数容量。 |
| Gemma: Open Models Based on Gemini Research and Technology | https://arxiv.org/abs/2403.08295 | 4 | 报告基于 Gemini 研究技术构建的开放轻量模型及其训练和安全评估。 |
| Phi-3 Technical Report | https://arxiv.org/abs/2404.14219 | 4 | 通过高质量数据训练小型语言模型，并评估其在有限部署资源下的能力。 |
| Baichuan 2 | https://arxiv.org/abs/2309.10305 | 4 | 报告从头训练的多语言基础模型系列及其通用和垂直领域表现。 |
| FlashAttention | https://arxiv.org/abs/2205.14135 | 5 | 通过分块和 IO 感知算法减少 Attention 的高带宽内存读写，同时保持精确计算。 |
| FlashAttention-2 | https://arxiv.org/abs/2307.08691 | 5 | 重新组织并行划分和线程工作分配，提升精确 Attention 的 GPU 利用率。 |
| FlashAttention-3 | https://arxiv.org/abs/2407.08608 | 5 | 利用异步执行和低精度计算优化新一代 GPU 上的 Attention 内核。 |
| PagedAttention (vLLM) | https://arxiv.org/abs/2309.06180 | 5 | 将 KV Cache 按块管理并按需分配，减少内存碎片并提升 LLM 服务吞吐。 |
| SGLang | https://arxiv.org/abs/2312.07104 | 5 | 通过结构化语言程序和 RadixAttention 复用前缀状态，提高复杂 LLM 程序执行效率。 |
| FlashInfer | https://arxiv.org/abs/2501.01005 | 5 | 提供可定制的 Attention 推理引擎，以高效处理不同批次和 KV Cache 布局。 |
| FastServe | https://arxiv.org/abs/2305.05920 | 4 | 在 token 粒度抢占和迁移推理状态，以降低请求排队延迟。 |
| SARATHI | https://arxiv.org/abs/2308.16369 | 4 | 将预填充分块，并把解码请求搭载到预填充批次中以提升 GPU 利用率。 |
| Sarathi-Serve | https://arxiv.org/abs/2403.02310 | 4 | 以分块预填充调节吞吐与延迟之间的权衡，并改善 LLM 服务调度。 |
| Splitwise | https://arxiv.org/abs/2311.18677 | 4 | 将预填充和解码阶段拆分到不同资源配置的机器上执行。 |
| DistServe | https://arxiv.org/abs/2401.09670 | 5 | 分离预填充与解码资源，并联合放置和调度以优化服务 goodput。 |
| Preble | https://arxiv.org/abs/2407.00023 | 4 | 面向共享前缀的分布式请求调度，利用前缀树结构提升缓存复用。 |
| Mooncake | https://arxiv.org/abs/2407.00079 | 5 | 将分布式 KV Cache 作为中心资源，构建解耦式 LLM 服务架构。 |
| P/D-Serve | https://arxiv.org/abs/2408.08147 | 5 | 联合组织预填充与解码实例，并优化集群间 KV Cache 传输和调度。 |
| Hydragen | https://arxiv.org/abs/2402.05099 | 4 | 将共享长前缀与请求特有后缀分开计算，以加速共享提示词场景的推理。 |
| ChunkAttention | https://arxiv.org/abs/2402.15220 | 4 | 使用前缀感知的分块 KV Cache 管理减少重复存储和注意力计算。 |
| CacheGen | https://arxiv.org/abs/2310.07240 | 4 | 压缩并流式传输 KV Cache，以降低跨网络复用上下文的传输延迟。 |
| FlexGen | https://arxiv.org/abs/2303.06865 | 4 | 联合调度 GPU、CPU 和磁盘上的权重与 KV Cache，在单卡资源下提升生成吞吐。 |
| Llumnix | https://arxiv.org/abs/2406.03243 | 5 | 通过跨实例动态重调度和在线迁移推理状态，改善负载均衡与尾延迟。 |
| Fast Inference from Transformers via Speculative Decoding | https://arxiv.org/abs/2211.17192 | 5 | 用小模型草拟多个 token，再由目标模型并行验证，在保持输出分布不变时加速解码。 |
| Accelerating Large Language Model Decoding with Speculative Sampling | https://arxiv.org/abs/2302.01318 | 5 | 通过草稿模型提出候选并采用拒绝采样校正，实现无损的并行 token 生成。 |
| SpecInfer | https://arxiv.org/abs/2305.09781 | 4 | 将多个草稿分支组织成 token 树，并由目标模型批量验证以加速服务推理。 |
| Draft & Verify | https://arxiv.org/abs/2309.08168 | 4 | 利用目标模型自身的辅助预测头进行草拟，并验证以实现自推测解码。 |
| Medusa | https://arxiv.org/abs/2401.10774 | 4 | 为目标模型增加多个解码头并设计树状验证，以并行生成后续 token。 |
| EAGLE | https://arxiv.org/abs/2401.15077 | 5 | 在特征空间中预测未来表示，再结合采样验证提高推测解码接受率。 |
| Lookahead Decoding | https://arxiv.org/abs/2402.02057 | 4 | 通过并行生成和验证候选 n-gram，减少自回归解码的串行依赖。 |
| Speculative Streaming | https://arxiv.org/abs/2402.11131 | 4 | 将未来 n-gram 预测融入目标模型，在不增加独立草稿模型的情况下加速生成。 |
| Block Verification | https://arxiv.org/abs/2403.10444 | 4 | 以块结构组织推测 token 的验证，降低目标模型验证阶段的开销。 |
| EAGLE-2 | https://arxiv.org/abs/2406.16858 | 4 | 根据动态置信度构建草稿树，使推测解码在不同输入上自适应分配分支。 |
| Request-Adaptive Execution for Efficient Hybrid LLM Inference | https://arxiv.org/abs/2610.37432 | 5 | This paper presents **Morph**, a serving system that co-designs a request-adaptive hybrid LLM architecture using prefill-oriented gating to select per-request layouts and employs selective batching with hybrid-aware context caching to enable efficient serving with divergent layer choices. |
| TAO: Tool-Aware Joint Scheduling for LLM-Based Agentic Serving | https://arxiv.org/abs/2610.37230 | 3 | TAO 提出了一种针对基于 LLM 的智能代理服务的工具感知联合调度框架，通过结合近端工具就绪状态、带时间感知衰减的节点特定缓存信用以及 Token 足迹，利用动态程序在容量约束下联合选择并放置待处理会话，从而将延迟降低高达 26.8%、首 Token 时间降低高达 36.3% 并提升解码吞吐量高达 29.5%。 |
| Distributed LLM Inference via Communication-Efficient Speculative Decoding | https://arxiv.org/abs/2610.35957 |  | 本文提出了 DISCO 框架，通过在服务器端部署小语言模型（SLM）副本来本地获取拒采所需的草稿分布，从而消除了分布式投机解码中基于词汇表的分布传输，仅交换**已起草的 token 索引**和**标量概率值**。 |
| JustGoal: With Only a Goal, the AI Baseline Is Above the Expert Kernels | https://arxiv.org/abs/2610.36434 | 5 | 本文提出了名为 JustGoal 的基线方法，该方法仅让通用智能体接收优化目标与约束，而不提供任何内核特定的基础设施、知识库或预设工作流，并使其自主构建评估循环；实验表明，在 NVIDIA B200 GPU 上，JustGoal 在 10 个算子中的 8 个上优于开源库（每算子几何平均加速比为 1.14$\times$ 至 2.34$\times$），在 9 个有公开比较的算子中的 5 个上超越了最快的公开专用智能体内核，同时针对 Fable 5.1 在单形状上的同模型对比显示，去除这些专家机制后性能损失不超过 5%。 |
| DCKV: Learned Transform Coding of the Prompt KV Cache in Hybrid Language Models | https://arxiv.org/abs/2610.36950 | 3 | DCKV 提出了一种**首篇**端到端训练的 KV 缓存压缩器，该压缩器通过联合优化**受提示词和已解码邻域条件化**的变换、量化器与熵模型，在 Qwen3.5-2B 模型上实现了相对于 bf16 格式**55 倍以上**的压缩率（损失不超过 1.8 点）和**100 倍以上**的压缩率（损失不超过 3.6 点）。 |
| Let the Gate Decide: Per-Lookup Precision for Quantized Conditional Memory in LLMs | https://arxiv.org/abs/2610.35985 |  | **GateRQ** 将量化条件存储中的每行编码为 1 位残差码栈，并在 GPU 内存中仅保留第一级以计算门控，从而仅在门控评分最高的查找中读取更深层级，实现了在无需重新训练的情况下大幅降低 GPU 表内存占用（DeepSeek-V4.1-Flash 上减少 7.8 倍）并提升 vLLM 吞吐量的贡献。 |
| EdgePace: Deadline- and Freshness-Aware LLM Scheduling on Unified-Memory Platforms | https://arxiv.org/abs/2610.37307 |  | EdgePace 通过创建一个跨预填充和解码阶段的**安全挂起点**、监控**前景内存需求**并在**低开销**下挂起，从而保护**前景截止日期**的同时保持**及时 LLM 反馈**，并在**内存带宽竞争风险**、**截止日期松弛**和**输出新鲜度**方面调度推理。 |
| DeepInfer-Mac: Running a 750B-Class MoE on a 24 GB Laptop | https://arxiv.org/abs/2610.36564 |  | DeepInfer-Mac 实现了一个在配备 24 GB 统一内存的 MacBook Air 上本地运行 750B 参数混合专家模型（MoE）的系统，该设计通过组织专家权重以直接填充可重用 GPU 缓冲区并将缓存分配与缓冲区生命周期耦合，从而在保留约 7.6 GiB 常驻权重的同时，将模型其余部分（路由专家及 Engram 行）存储在内部 SSD 上按需加载。 |
| HiLo-RD: Cross-Budget Self-Distillation for Masked Diffusion Language Models | https://arxiv.org/abs/2610.36901 |  | HiLo-RD 提出了一种无需外部教师的高 - 低预算表示蒸馏方法，通过将大窗口教师状态与裁剪后的小窗口视图配对并在已承诺位置匹配其隐藏表示，从而同时指导掩码扩散语言模型的令牌预测与承诺顺序。 |
| V-LUMEN: Visual Lookup Memory for Embedding Scaling in Vision-Language Models | https://arxiv.org/abs/2610.37019 |  | 本文提出了**V-LUMEN**，一种通过非参数化查找机制将连续视觉特征离散化为可复用记忆键，并利用文本条件信号进行检索与融合，从而在冻结的 Qwen3-VL-2B 主干网络上提升推理性能并实现零样本迁移的视觉查找记忆系统。 |
