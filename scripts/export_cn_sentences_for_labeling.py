import argparse
import csv
import re
import sys
from pathlib import Path
from typing import Dict, List


# 确保可以在命令行直接运行本脚本：自动把项目的 src 目录加入 sys.path
CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from servitization_cn.pipeline_cn import build_company_year_texts_cn
from servitization_cn.config_keywords_cn import KEYWORDS_CN


SENT_SPLIT_PATTERN = re.compile(r"[。！？；!?;]+")


def split_sentences_cn(text: str, min_len: int = 5) -> List[str]:
    """非常简单的中文断句：按标点切分，去掉过短片段。"""

    if not text:
        return []
    # 统一换行和空白
    cleaned = re.sub(r"\s+", " ", text)
    parts = SENT_SPLIT_PATTERN.split(cleaned)
    sentences: List[str] = []
    for part in parts:
        sent = part.strip()
        if len(sent) >= min_len:
            sentences.append(sent)
    return sentences


def build_labels_for_sentence(sentence: str) -> Dict[str, int]:
    """基于 KEYWORDS_CN 在句子级别构造 13 维标签（B_i）。"""

    labels: Dict[str, int] = {}
    for cat, phrases in KEYWORDS_CN.items():
        flag = 0
        for phrase in phrases:
            if phrase and phrase in sentence:
                flag = 1
                break
        labels[cat] = flag
    return labels


def export_sentences_for_labeling(input_dir: str, output_csv: str, min_len: int = 5) -> None:
    """从原始中文年报导出句子级样本，用于人工标注。

    - 读取 input_dir 下的年报文件，复用 build_company_year_texts_cn 的解析逻辑；
    - 对每个 company-year 文本做断句，得到句子集合 A；
    - 基于 KEYWORDS_CN 为每个句子打 13 维 0/1 初始标签（对应 B_i 是否命中）；
    - 将结果写入 CSV：company, year, sent_id, sentence, <13 个类别列>。
    """

    input_path = Path(input_dir)
    if not input_path.exists():
        raise FileNotFoundError(f"Input dir not found: {input_dir}")

    company_texts = build_company_year_texts_cn(input_path)

    categories = list(KEYWORDS_CN.keys())

    out_path = Path(output_csv)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with out_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        header = ["company", "year", "sent_id", "sentence"] + categories
        writer.writerow(header)

        for company, year_dict in sorted(company_texts.items()):
            for year, text in sorted(year_dict.items()):
                sentences = split_sentences_cn(text, min_len=min_len)
                for idx, sent in enumerate(sentences):
                    labels = build_labels_for_sentence(sent)
                    row = [company, year, idx, sent]
                    for cat in categories:
                        row.append(labels.get(cat, 0))
                    writer.writerow(row)

    print(f"[INFO] Sentence-level CSV written to: {out_path}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Export Chinese annual report sentences for multi-label servitization "
            "annotation (13 categories)."
        ),
    )
    parser.add_argument(
        "--input-dir",
        type=str,
        default="data/raw/CN",
        help="Directory that contains CN raw pdf/txt files (default: data/raw/CN)",
    )
    parser.add_argument(
        "--output-csv",
        type=str,
        default="data/outputs/cn_sentences_for_labeling.csv",
        help="Path to save sentence-level CSV for human annotation",
    )
    parser.add_argument(
        "--min-len",
        type=int,
        default=5,
        help="Minimum length of a sentence to keep (in characters, default: 5)",
    )

    args = parser.parse_args()
    export_sentences_for_labeling(
        input_dir=args.input_dir,
        output_csv=args.output_csv,
        min_len=args.min_len,
    )


if __name__ == "__main__":
    main()
