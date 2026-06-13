---
name: paper-search-toolkit
description: 多源学术论文搜索工具，支持安全/AI/硬件/软件等领域论文检索
---

# Paper Search Toolkit

多源学术论文搜索工具。用户用中/英文描述需求，你负责执行搜索并展示结果。

## 执行命令

```bash
python collect.py --domain <领域> --limit 20 <中英混合关键词>
```

## 领域判断

| 用户关键词 | --domain |
|-----------|----------|
| 安全/攻击/防御/漏洞/侧信道/注入/投毒/隐私 | `security` |
| AI/ML/NLP/CV/深度学习/大模型/LLM/训练 | `ai` |
| 硬件/芯片/处理器/CPU/GPU/RISC-V/FPGA/微架构 | `hardware` |
| 软件/编译器/程序分析/测试/验证 | `software` |
| 不明确 | `general` |

## 关键词转换

用户中文需求 → 英文关键词为主 + 保留中文。每个独立概念一个引号参数，4-8 个为宜。

## 工作流

1. 确保已 `pip install -r requirements.txt`
2. 运行 `python collect.py --domain <domain> <keywords>`
3. 从终端输出中提取强相关论文，展示标题/作者/年份/venue/CCF/摘要前200字
4. 报告总数、强相关数、Excel 路径、PDF 下载情况

## 示例

用户："搜一下大模型供应链投毒论文"
→ `python collect.py --domain security "supply chain" "poisoning" "LLM" "large language model" "attack"`

用户："找 RISC-V 形式化验证的论文"
→ `python collect.py --domain hardware "RISC-V" "formal verification" "ISA" "processor"`

用户："microarchitecture side channel attack recent papers"
→ `python collect.py --domain security "microarchitecture" "side channel" "cache attack" "vulnerability"`
