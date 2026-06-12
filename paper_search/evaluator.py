"""论文相关性评估与 CCF 等级判定"""

import logging
from .base import Paper

logger = logging.getLogger(__name__)

# ============================================================
# CCF 推荐目录映射（第七版，2026年3月更新）
# 详见 ccf/CCF-2026-推荐目录.md
# ============================================================

CCF_VENUE_MAP: dict[str, str] = {
    # ===== 计算机体系结构 / 并行与分布计算 / 存储系统 =====
    # CCF-A
    "ASPLOS": "CCF-A", "ASPLOS Conference": "CCF-A",
    "DAC": "CCF-A", "Design Automation Conference": "CCF-A",
    "HPCA": "CCF-A", "High-Performance Computer Architecture": "CCF-A",
    "ISCA": "CCF-A", "International Symposium on Computer Architecture": "CCF-A",
    "MICRO": "CCF-A", "International Symposium on Microarchitecture": "CCF-A",
    "SC": "CCF-A", "Supercomputing": "CCF-A",
    "SIGMETRICS": "CCF-A",
    "ATC": "CCF-A", "USENIX Annual Technical Conference": "CCF-A",
    "EuroSys": "CCF-A", "European Conference on Computer Systems": "CCF-A",
    "FAST": "CCF-A", "USENIX Conference on File and Storage Technologies": "CCF-A",
    "OSDI": "CCF-A", "USENIX Symposium on Operating Systems Design and Implementation": "CCF-A",
    "SOSP": "CCF-A", "Symposium on Operating Systems Principles": "CCF-A",
    "PPoPP": "CCF-A",
    "TC": "CCF-A", "IEEE Transactions on Computers": "CCF-A",
    "TCAD": "CCF-A", "IEEE Transactions on Computer-Aided Design": "CCF-A",
    "TOCS": "CCF-A", "ACM Transactions on Computer Systems": "CCF-A",
    "TOS": "CCF-A", "ACM Transactions on Storage": "CCF-A",
    "TPDS": "CCF-A", "IEEE Transactions on Parallel and Distributed Systems": "CCF-A",
    "TACO": "CCF-A", "ACM Transactions on Architecture and Code Optimization": "CCF-A",
    # CCF-B
    "CODES+ISSS": "CCF-B", "EMSOFT": "CCF-B",
    "DATE": "CCF-B", "Design, Automation and Test in Europe": "CCF-B",
    "FPGA": "CCF-B", "FCCM": "CCF-B", "FPL": "CCF-B",
    "HOST": "CCF-B", "Hardware Oriented Security and Trust": "CCF-B",
    "ISLPED": "CCF-B", "ITC": "CCF-B",
    "MSST": "CCF-B", "PACT": "CCF-B", "PETS": "CCF-B",
    "RTAS": "CCF-B", "RTSS": "CCF-B",
    "VEE": "CCF-B", "VTS": "CCF-B",
    "TODAES": "CCF-B", "TECS": "CCF-B",
    "TVLSI": "CCF-B", "TCASI": "CCF-B", "TCASII": "CCF-B",
    "JSA": "CCF-B", "JPDC": "CCF-B",
    # CCF-C
    "ASP-DAC": "CCF-C", "ETS": "CCF-C",
    "GLSVLSI": "CCF-C", "Great Lakes Symposium on VLSI": "CCF-C",
    "ISCAS": "CCF-C", "International Symposium on Circuits and Systems": "CCF-C",
    "ISQED": "CCF-C", "MWSCAS": "CCF-C",
    "SLIP": "CCF-C", "VLSI-SoC": "CCF-C",
    "NORCHIP": "CCF-C",

    # ===== 计算机网络 =====
    # CCF-A
    "SIGCOMM": "CCF-A", "MobiCom": "CCF-A",
    "INFOCOM": "CCF-A", "IEEE Conference on Computer Communications": "CCF-A",
    "NSDI": "CCF-A", "USENIX Symposium on Networked Systems Design and Implementation": "CCF-A",
    "JSAC": "CCF-A", "IEEE Journal on Selected Areas in Communications": "CCF-A",
    "TON": "CCF-A", "IEEE/ACM Transactions on Networking": "CCF-A",
    "TMC": "CCF-A", "IEEE Transactions on Mobile Computing": "CCF-A",
    # CCF-B
    "CoNEXT": "CCF-B", "SECON": "CCF-B",
    "IPSN": "CCF-B", "MSN": "CCF-B",
    "ICNP": "CCF-B", "MobiHoc": "CCF-B",
    "IWQoS": "CCF-B", "ICDCS": "CCF-B",
    "CN": "CCF-B", "Computer Networks": "CCF-B",
    "TCOM": "CCF-B",
    # CCF-C
    "ANCS": "CCF-C",

    # ===== 网络与信息安全 =====
    # CCF-A
    "S&P": "CCF-A", "IEEE Symposium on Security and Privacy": "CCF-A",
    "USENIX Security": "CCF-A", "USENIX Security Symposium": "CCF-A",
    "CCS": "CCF-A", "ACM Conference on Computer and Communications Security": "CCF-A",
    "NDSS": "CCF-A", "Network and Distributed System Security Symposium": "CCF-A",
    "TDSC": "CCF-A", "IEEE Transactions on Dependable and Secure Computing": "CCF-A",
    "TIFS": "CCF-A", "IEEE Transactions on Information Forensics and Security": "CCF-A",
    "Journal of Cryptology": "CCF-A",
    # CCF-B
    "ACSAC": "CCF-B", "Annual Computer Security Applications Conference": "CCF-B",
    "ESORICS": "CCF-B",
    "RAID": "CCF-B", "International Symposium on Research in Attacks, Intrusions and Defenses": "CCF-B",
    "DSN": "CCF-B", "International Conference on Dependable Systems and Networks": "CCF-B",
    "CSF": "CCF-B", "Computer Security Foundations Symposium": "CCF-B",
    "ASIACRYPT": "CCF-B",
    "SEC": "CCF-B",
    "Computer & Security": "CCF-B",
    "Journal of Computer Security": "CCF-B",
    # CCF-C
    "SECRISC-V": "CCF-C", "WiSec": "CCF-C",
    "ACNS": "CCF-C", "SecureComm": "CCF-C",
    "SRDS": "CCF-C", "IMC": "CCF-C",
    "TrustCom": "CCF-C",

    # ===== 软件工程 / 程序设计语言 / 系统软件 =====
    # CCF-A
    "PLDI": "CCF-A", "Programming Language Design and Implementation": "CCF-A",
    "POPL": "CCF-A", "Principles of Programming Languages": "CCF-A",
    "ICSE": "CCF-A", "International Conference on Software Engineering": "CCF-A",
    "FSE": "CCF-A", "ESEC/FSE": "CCF-A",
    "ASE": "CCF-A", "Automated Software Engineering": "CCF-A",
    "ISSTA": "CCF-A", "International Symposium on Software Testing and Analysis": "CCF-A",
    "OOPSLA": "CCF-A",
    "TOPLAS": "CCF-A", "ACM Transactions on Programming Languages and Systems": "CCF-A",
    "TSE": "CCF-A", "IEEE Transactions on Software Engineering": "CCF-A",
    "TOSEM": "CCF-A", "ACM Transactions on Software Engineering and Methodology": "CCF-A",
    # CCF-B
    "ECOOP": "CCF-B", "ETAPS": "CCF-B",
    "ICPC": "CCF-B", "ICSME": "CCF-B",
    "SANER": "CCF-B", "MSR": "CCF-B",
    "ISSRE": "CCF-B", "FASE": "CCF-B",
    "ESEM": "CCF-B", "ICST": "CCF-B",
    "RE": "CCF-B", "CAiSE": "CCF-B",
    "TSC": "CCF-B", "JSS": "CCF-B",
    "SCP": "CCF-B", "SoSyM": "CCF-B", "EMSE": "CCF-B",
    "SPE": "CCF-B", "STVR": "CCF-B",
    # CCF-C
    "PEPM": "CCF-C",

    # ===== 人工智能 =====
    # CCF-A
    "AAAI": "CCF-A", "AAAI Conference on Artificial Intelligence": "CCF-A",
    "NeurIPS": "CCF-A", "Neural Information Processing Systems": "CCF-A",
    "ICML": "CCF-A", "International Conference on Machine Learning": "CCF-A",
    "IJCAI": "CCF-A", "International Joint Conference on Artificial Intelligence": "CCF-A",
    "CVPR": "CCF-A", "Computer Vision and Pattern Recognition": "CCF-A",
    "ICCV": "CCF-A", "International Conference on Computer Vision": "CCF-A",
    "ACL": "CCF-A", "Association for Computational Linguistics": "CCF-A",
    "EMNLP": "CCF-A", "Empirical Methods in Natural Language Processing": "CCF-A",
    "NAACL": "CCF-A", "North American Chapter of the ACL": "CCF-A",
    "SIGIR": "CCF-A", "International Conference on Research and Development in Information Retrieval": "CCF-A",
    "WWW": "CCF-A", "The Web Conference": "CCF-A",
    "SIGKDD": "CCF-A", "KDD": "CCF-A",
    "TPAMI": "CCF-A", "IEEE Transactions on Pattern Analysis and Machine Intelligence": "CCF-A",
    "AIJ": "CCF-A", "Artificial Intelligence Journal": "CCF-A",
    "JMLR": "CCF-A", "Journal of Machine Learning Research": "CCF-A",
    "IJCV": "CCF-A", "International Journal of Computer Vision": "CCF-A",
    "TALSP": "CCF-A", "IEEE/ACM Transactions on Audio, Speech, and Language Processing": "CCF-A",
    "CL": "CCF-A", "Computational Linguistics": "CCF-A",
    # CCF-B
    "AAMAS": "CCF-B", "COLT": "CCF-B",
    "ECCV": "CCF-B", "European Conference on Computer Vision": "CCF-B",
    "ICRA": "CCF-B", "International Conference on Robotics and Automation": "CCF-B",
    "ICAPS": "CCF-B",
    "COLING": "CCF-B", "International Conference on Computational Linguistics": "CCF-B",
    "UAI": "CCF-B",
    "ECAI": "CCF-B", "European Conference on Artificial Intelligence": "CCF-B",
    "TACL": "CCF-B", "Transactions of the Association for Computational Linguistics": "CCF-B",
    "TNNLS": "CCF-B", "IEEE Transactions on Neural Networks and Learning Systems": "CCF-B",
    "MLJ": "CCF-B", "Machine Learning Journal": "CCF-B",
    "JAIR": "CCF-B", "Journal of Artificial Intelligence Research": "CCF-B",
    "TKDE": "CCF-B", "IEEE Transactions on Knowledge and Data Engineering": "CCF-B",
    "TAFFC": "CCF-B",
    # CCF-C
    "ICANN": "CCF-C", "ICDAR": "CCF-C",
    "ICONIP": "CCF-C", "PRICAI": "CCF-C",
    "BMVC": "CCF-C", "ACCV": "CCF-C",
    "FG": "CCF-C",
    "CoNLL": "CCF-C", "EACL": "CCF-C",
    "AISTATS": "CCF-C", "ALT": "CCF-C",
    "WSDM": "CCF-C", "CIKM": "CCF-C",
    "ECIR": "CCF-C",

    # ===== 数据库 / 数据挖掘 / 内容检索 =====
    # CCF-A
    "SIGMOD": "CCF-A", "VLDB": "CCF-A",
    "ICDE": "CCF-A", "International Conference on Data Engineering": "CCF-A",
    "PODS": "CCF-A",
    "TODS": "CCF-A", "TOIS": "CCF-A",
    # CCF-B
    "DASFAA": "CCF-B", "EDBT": "CCF-B",
    "ISWC": "CCF-B", "International Semantic Web Conference": "CCF-B",
    "CIDR": "CCF-B", "SDM": "CCF-B",
    "DKE": "CCF-B", "GeoInformatica": "CCF-B",
    "TKDD": "CCF-B", "TWEB": "CCF-B",
    # CCF-C
    "ADMA": "CCF-C", "APWeb-WAIM": "CCF-C",
    "DEXA": "CCF-C", "RecSys": "CCF-C",

    # ===== 计算机图形学与多媒体 =====
    # CCF-A
    "SIGGRAPH": "CCF-A",
    "VR": "CCF-A", "IEEE Conference on Virtual Reality and 3D User Interfaces": "CCF-A",
    "MM": "CCF-A", "ACM International Conference on Multimedia": "CCF-A",
    "TOG": "CCF-A", "ACM Transactions on Graphics": "CCF-A",
    "TVCG": "CCF-A", "IEEE Transactions on Visualization and Computer Graphics": "CCF-A",
    # CCF-B
    "ICMR": "CCF-B", "ICME": "CCF-B",
    "CGI": "CCF-B", "PacificVis": "CCF-B",
    "CAD": "CCF-B", "CGF": "CCF-B",
    "TMM": "CCF-B",
    # CCF-C
    "SGP": "CCF-C",

    # ===== 人机交互 =====
    # CCF-A
    "CHI": "CCF-A", "ACM Conference on Human Factors in Computing Systems": "CCF-A",
    "UbiComp": "CCF-A", "IMWUT": "CCF-A",
    # CCF-B
    "CSCW": "CCF-B", "GROUP": "CCF-B",
    "MobileHCI": "CCF-B", "IUI": "CCF-B",
    "HSCC": "CCF-B", "HRI": "CCF-B",
    "IJHCI": "CCF-B", "IJHCS": "CCF-B",
    # CCF-C
    "INTERACT": "CCF-C",

    # ===== 交叉 / 综合 / 新兴 =====
    "CPP": "CCF-B", "FM": "CCF-B",
    "LICS": "CCF-A", "Logic in Computer Science": "CCF-A",
    "CAV": "CCF-A", "Computer Aided Verification": "CCF-A",
    "ESEC": "CCF-A",
    "FDL": "CCF-C", "Forum on specification and Design Languages": "CCF-C",
    "SOCC": "CCF-C",
    "IROS": "CCF-B",
    "RISC-V Summit": "",
}


def guess_ccf(venue: str) -> str:
    """根据会议/期刊名称推断 CCF 推荐等级。

    匹配策略：按关键词长度降序匹配，避免短串误匹配（如 ISCA 匹配到 ISCAS）。
    同时检查词边界，确保精确匹配。
    """
    if not venue:
        return ""
    vl = venue.lower()
    # 按 key 长度降序排序，优先匹配更具体的名称
    for key, level in sorted(CCF_VENUE_MAP.items(), key=lambda x: -len(x[0])):
        kl = key.lower()
        idx = vl.find(kl)
        if idx == -1:
            continue
        # 检查词边界：前面不能是字母，后面不能是字母（除非是空格）
        after = idx + len(kl)
        before_ok = idx == 0 or not vl[idx - 1].isalpha()
        after_ok = after >= len(vl) or not vl[after].isalpha() or vl[after] == ' '
        if before_ok and after_ok:
            return level if level else ""
    # 兜底：IEEE/ACM Transactions 可能是 A 类
    if any(tla in vl for tla in [
        "ieee transactions on", "acm transactions on",
        "ieee journal on", "acm journal on"
    ]):
        return "CCF-A"
    return ""


def guess_category(paper: Paper) -> str:
    """自动推断论文分类标签。

    基于标题和摘要中的关键词匹配，可识别：
    形式化方法、模糊测试/测试生成、侧信道/微架构安全、
    机器学习/AI、软件工程、网络/系统安全等。
    """
    t = paper.title.lower()
    a = (paper.abstract or "").lower()
    text = t + " " + a

    tags: list[str] = []

    if _match(text, ["formal", "verification", "correctness", "refinement",
                      "bisimulation", "specification", "prove", "proof",
                      "model checking", "theorem", "satisfiability"]):
        tags.append("形式化方法")

    if _match(text, ["fuzz", "mutation", "seed", "test generation",
                      "test case", "input generation", "coverage guided",
                      "greybox", "blackbox", "feedback driven"]):
        tags.append("模糊测试")

    if _match(text, ["side channel", "side-channel", "cache attack",
                      "timing attack", "microarchitectur",
                      "speculative execution", "spectre", "meltdown",
                      "transient execution", "covert channel"]):
        tags.append("微架构安全")

    if _match(text, ["machine learning", "deep learning", "neural network",
                      "transformer", "llm", "large language model",
                      "gpt", "bert", "diffusion", "generative model",
                      "reinforcement learning", "rl", "fine-tun"]):
        tags.append("机器学习/AI")

    if _match(text, ["software engineering", "program analysis",
                      "static analysis", "dynamic analysis", "symbolic execution",
                      "bug detection", "vulnerability detection",
                      "code review", "program synthesis"]):
        tags.append("软件工程")

    if _match(text, ["network security", "intrusion detection",
                      "malware", "firewall", "ddos", "phishing",
                      "authentication", "access control", "privacy"]):
        tags.append("网络安全")

    if _match(text, ["risc-v", "isa", "instruction set", "processor",
                      "cpu", "gpu", "hardware design", "rtl", "soc"]):
        tags.append("处理器/硬件")

    if _match(text, ["prompt injection", "jailbreak", "adversarial",
                      "red team", "alignment", "safety", "guardrail",
                      "prompt engineering"]):
        tags.append("Prompt注入/安全")

    if not tags:
        tags.append("其他")
    return "；".join(tags)


def _match(text: str, keywords: list[str], threshold: int = 2) -> bool:
    """文本中包含足够多的关键词则返回 True"""
    hits = sum(1 for kw in keywords if kw in text)
    return hits >= min(threshold, max(1, len(keywords) // 3))


def evaluate_papers(
    papers: list[Paper],
    topic_keywords: list[str],
    domain_hint: str = "general",
) -> list[Paper]:
    """批量评估论文相关性。

    Args:
        papers: 待评估论文列表
        topic_keywords: 用户指定的研究主题关键词
        domain_hint: 领域提示（general / security / ai / hardware / software）

    Returns:
        已填充 relevance / relevance_score / category / ccf_level 的论文列表

    相关性分级逻辑：
    - 标题/摘要中包含 ≥5 个主题关键词 → 强相关 (score >= 8)
    - 标题/摘要中包含 ≥3 个主题关键词 → 相关   (score >= 5)
    - 标题/摘要中包含 ≥1 个主题关键词 → 弱相关 (score >= 3)
    - 领域相关但无明显主题匹配      → 一般   (score >= 1)
    - 完全不相关                   → 无关   (score = 0)
    """
    for paper in papers:
        t = paper.title.lower()
        a = (paper.abstract or "").lower()
        text = t + " " + a
        score = 0

        # 1. 主题关键词匹配（权重最高）
        kw_hits = 0
        for kw in topic_keywords:
            kwl = kw.lower()
            count = text.count(kwl)
            if count > 0:
                kw_hits += min(count, 3)  # 单次命中最多计 3 分

        if kw_hits >= 8:
            score += 6
        elif kw_hits >= 5:
            score += 4
        elif kw_hits >= 3:
            score += 2
        elif kw_hits >= 1:
            score += 1

        # 2. 领域相关性加成
        domain_keywords = _get_domain_keywords(domain_hint)
        domain_hits = sum(1 for dk in domain_keywords if dk in text)
        if domain_hits >= 3:
            score += 2
        elif domain_hits >= 1:
            score += 1

        # 3. 发表质量加分
        if paper.venue and paper.venue.lower() not in ("arxiv", ""):
            score += 1
        if paper.doi:
            score += 1
        if paper.year and paper.year >= 2023:
            score += 1

        # 4. 分级
        if score >= 8:
            paper.relevance = "强相关"
        elif score >= 5:
            paper.relevance = "相关"
        elif score >= 3:
            paper.relevance = "弱相关"
        elif score >= 1:
            paper.relevance = "一般"
        else:
            paper.relevance = "无关"
        paper.relevance_score = score

        # 5. CCF & 分类
        paper.ccf_level = guess_ccf(paper.venue)
        paper.category = guess_category(paper)

    return papers


def _get_domain_keywords(hint: str) -> list[str]:
    """根据领域提示返回辅助匹配关键词"""
    mapping = {
        "security": [
            "security", "attack", "defense", "vulnerability", "exploit",
            "malware", "privacy", "trust", "crypto", "authentication",
        ],
        "ai": [
            "machine learning", "deep learning", "neural network", "model",
            "training", "inference", "transformer", "llm", "embedding",
        ],
        "hardware": [
            "hardware", "processor", "cpu", "gpu", "risc-v", "rtl",
            "fpga", "soc", "microarchitecture", "cache", "verilog",
        ],
        "software": [
            "software", "compiler", "program", "code", "analysis",
            "testing", "verification", "debugging", "optimization",
        ],
    }
    return mapping.get(hint, [])
