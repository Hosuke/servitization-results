from collections import defaultdict
from typing import Dict, List, Tuple

from .config_keywords_cn import KEYWORDS_CN, CATEGORY_TYPE_CN

# 简单的中文否定模式，可以后续根据需要扩展
NEGATION_PATTERNS = [
    "不提供",
    "未提供",
    "不再提供",
]


def _is_negated(text: str, phrase: str) -> bool:
    """极简否定规则：如果出现“不提供X服务”这一类形式则视为否定。

    目前实现：检查若干固定否定前缀 + 关键词的组合；以后可以用更复杂的窗口匹配替换。
    """

    for neg in NEGATION_PATTERNS:
        if neg + phrase in text:
            return True
    return False


def classify_services_cn(text: str):
    """对中文文本做 13 类服务识别，返回 flags, evidence, comp_count, sub_count, service_num, risk_score。

    中文文本不做分词，直接基于子串匹配，适合先做一个 baseline，后续可以考虑接入 jieba/HanLP 等。
    """

    flags: Dict[str, int] = {cat: 0 for cat in KEYWORDS_CN.keys()}
    evidence: Dict[str, List[str]] = defaultdict(list)

    # 为了减少重复 snippet 的长度，这里限制每类只保留前若干个命中的片段
    MAX_SNIPPETS_PER_CAT = 20
    WINDOW = 60  # 从匹配位置左右各取约 60 字符作为证据窗口

    for cat, phrases in KEYWORDS_CN.items():
        for phrase in phrases:
            idx = 0
            while True:
                idx = text.find(phrase, idx)
                if idx == -1:
                    break
                if _is_negated(text, phrase):
                    idx += len(phrase)
                    continue
                flags[cat] = 1
                if len(evidence[cat]) < MAX_SNIPPETS_PER_CAT:
                    start = max(0, idx - WINDOW)
                    end = min(len(text), idx + len(phrase) + WINDOW)
                    snippet = text[start:end].replace("\n", " ")
                    evidence[cat].append(snippet)
                idx += len(phrase)

    comp_count = sum(
        flags[cat]
        for cat, t in CATEGORY_TYPE_CN.items()
        if t == "complementing"
    )
    sub_count = sum(
        flags[cat]
        for cat, t in CATEGORY_TYPE_CN.items()
        if t == "substituting"
    )
    service_num = sum(flags.values())

    # 与英文版保持类似的简单风险分数设定
    risk_score = 2.0 * sub_count + 0.5 * comp_count

    return flags, evidence, comp_count, sub_count, service_num, risk_score


def process_company_item1s_cn(company_id: str, year_texts: Dict[int, str]):
    """按照英文版的接口风格，对 {year: text} 做批处理，返回行列表。"""

    rows = []
    for year, text in sorted(year_texts.items()):
        flags, evidence, comp_count, sub_count, service_num, risk_score = classify_services_cn(text)
        rows.append(
            {
                "company": company_id,
                "year": year,
                "service_num": service_num,
                "comp_count": comp_count,
                "sub_count": sub_count,
                "risk_score": risk_score,
                "flags": flags,
                "evidence": dict(evidence),
            }
        )
    return rows
