from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

from models_cn import CNMultiLabelServitizationModel
from servitization_cn.config_keywords_cn import KEYWORDS_CN, CATEGORY_TYPE_CN
from servitization_cn.pipeline_cn import build_company_year_texts_cn


def split_sentences_cn(text: str, min_len: int = 5) -> List[str]:
    """与导出脚本相同的极简中文断句：按标点切分，去掉过短片段。"""

    import re

    if not text:
        return []

    sent_split_pattern = re.compile(r"[。！？；!?;]+")
    cleaned = re.sub(r"\s+", " ", text)
    parts = sent_split_pattern.split(cleaned)
    sentences: List[str] = []
    for part in parts:
        sent = part.strip()
        if len(sent) >= min_len:
            sentences.append(sent)
    return sentences


def classify_services_cn_bert(
    text: str,
    model: CNMultiLabelServitizationModel,
    prob_threshold: float = 0.5,
) -> Tuple[Dict[str, int], Dict[str, List[str]], int, int, int, float]:
    """使用句子级多标签模型对中文文本做 13 类服务识别。

    - 对文本断句；
    - 对每句调用多标签模型；
    - 若任一句在某类上的概率 >= prob_threshold，则视为该类激活；
    - evidence 中保存激活类别对应的若干句子片段。
    """

    sentences = split_sentences_cn(text)
    if not sentences:
        flags: Dict[str, int] = {cat: 0 for cat in KEYWORDS_CN.keys()}
        return flags, {}, 0, 0, 0, 0.0

    categories = list(KEYWORDS_CN.keys())
    probs_list = model.predict_proba(sentences)

    flags: Dict[str, int] = {cat: 0 for cat in categories}
    evidence: Dict[str, List[str]] = defaultdict(list)

    max_snippets_per_cat = 50

    for sent, prob_dict in zip(sentences, probs_list):
        for cat in categories:
            p = prob_dict.get(cat, 0.0)
            if p >= prob_threshold:
                if flags[cat] == 0:
                    flags[cat] = 1
                if len(evidence[cat]) < max_snippets_per_cat:
                    evidence[cat].append(sent)

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

    risk_score = 2.0 * sub_count + 0.5 * comp_count

    return flags, dict(evidence), comp_count, sub_count, service_num, risk_score


def process_company_item1s_cn_bert(
    company_id: str,
    year_texts: Dict[int, str],
    model: CNMultiLabelServitizationModel,
    prob_threshold: float = 0.5,
):
    """与规则版接口类似：对 {year: text} 做批处理，返回行列表。"""

    rows = []
    for year, text in sorted(year_texts.items()):
        flags, evidence, comp_count, sub_count, service_num, risk_score = classify_services_cn_bert(
            text,
            model=model,
            prob_threshold=prob_threshold,
        )
        rows.append(
            {
                "company": company_id,
                "year": year,
                "service_num": service_num,
                "comp_count": comp_count,
                "sub_count": sub_count,
                "risk_score": risk_score,
                "flags": flags,
                "evidence": evidence,
            }
        )
    return rows


def load_company_texts_cn(input_dir: str):
    """简单包装 build_company_year_texts_cn，供 pipeline_cn_bert 使用。"""

    input_path = Path(input_dir)
    return build_company_year_texts_cn(input_path)
