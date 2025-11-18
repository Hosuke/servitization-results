import re
from collections import defaultdict
from typing import Dict, List, Tuple

from .config_keywords import KEYWORDS, CATEGORY_TYPE

# 可选：如果想用 lemma 回退，把 USE_SPACY 改 True 并安装 spaCy
USE_SPACY = False
nlp = None
if USE_SPACY:
    import spacy
    nlp = spacy.load("en_core_web_sm", disable=["ner", "parser"])


def build_patterns(keywords_dict: Dict[str, List[str]]) -> Dict[str, re.Pattern]:
    patterns = {}
    for cat, phrases in keywords_dict.items():
        sorted_phrases = sorted(set(phrases), key=lambda x: -len(x))
        or_group = "|".join(re.escape(p.lower()) for p in sorted_phrases)
        patterns[cat] = re.compile(r"\b(" + or_group + r")\b", flags=re.IGNORECASE)
    return patterns


PATTERNS = build_patterns(KEYWORDS)

NEGATION_CUES = [
    "do not provide", "does not provide", "did not provide",
    "do not offer", "does not offer", "did not offer",
    "no longer provide", "no longer offered",
    "we do not", "we don't", "does not include",
    "not available", "without providing",
]


def preprocess_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def has_negation_around(text: str, start: int, end: int, window: int = 80) -> bool:
    s = max(0, start - window)
    e = min(len(text), end + window)
    ctx = text[s:e].lower()
    return any(cue in ctx for cue in NEGATION_CUES)


def build_lemma_set(text: str) -> set:
    if not USE_SPACY or nlp is None:
        return set()
    doc = nlp(text)
    return {tok.lemma_.lower() for tok in doc if not tok.is_stop and tok.is_alpha}


def classify_services(
    item1_text: str,
    use_lemma_fallback: bool = False,
    evidence_window: int = 200,
) -> Tuple[Dict[str, int], Dict[str, List[str]]]:
    """对一段文本（如年报业务描述）识别 13 类服务"""
    raw_text = preprocess_text(item1_text)
    lower_text = raw_text.lower()

    flags = {c: 0 for c in PATTERNS.keys()}
    evidence = defaultdict(list)

    # 1) 短语/正则匹配
    for cat, pat in PATTERNS.items():
        for m in pat.finditer(lower_text):
            start, end = m.start(), m.end()
            if has_negation_around(lower_text, start, end):
                continue
            flags[cat] = 1
            ctx_start = max(0, start - evidence_window)
            ctx_end = min(len(raw_text), end + evidence_window)
            snippet = raw_text[ctx_start:ctx_end].strip()
            evidence[cat].append(snippet)

    # 2) 可选：lemma 回退
    if use_lemma_fallback:
        lemmas = build_lemma_set(raw_text)
        for cat in PATTERNS.keys():
            if flags[cat] == 0:
                for phrase in KEYWORDS[cat]:
                    if " " not in phrase and phrase.lower() in lemmas:
                        flags[cat] = 1
                        evidence[cat].append(f"lemma_match::{phrase}")
                        break

    return flags, evidence


def compute_supply_chain_risk(flags: Dict[str, int]) -> float:
    """简单供应链风险分数，可按需要调整公式"""
    comp_count = 0
    sub_count = 0
    for cat, v in flags.items():
        if v == 1:
            t = CATEGORY_TYPE.get(cat, "complementing")
            if t == "substituting":
                sub_count += 1
            else:
                comp_count += 1
    risk_score = sub_count * 2.0 + comp_count * 0.5
    return risk_score


def process_company_item1s(
    company_id: str,
    item1_texts_by_year: Dict[int, str],
    use_lemma_fallback: bool = False,
):
    """把某个公司的多个年份文本打包处理"""
    rows = []
    for year, txt in sorted(item1_texts_by_year.items()):
        flags, evidence = classify_services(
            txt,
            use_lemma_fallback=use_lemma_fallback,
        )
        service_num = sum(flags.values())
        comp_count = sum(
            1
            for k, v in flags.items()
            if v == 1 and CATEGORY_TYPE.get(k, "complementing") == "complementing"
        )
        sub_count = sum(
            1
            for k, v in flags.items()
            if v == 1 and CATEGORY_TYPE.get(k, "complementing") == "substituting"
        )
        risk_score = compute_supply_chain_risk(flags)

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
