import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Dict

import pandas as pd

from servitization.io_markitdown import convert_file_to_text
from .detector_cn import process_company_item1s_cn


def parse_company_year_cn(path: Path):
    """针对中文年报文件名的解析逻辑。

    假设文件名（不含扩展名）形如：
        688708_2024_佳驰科技_2024年年度报告_2025-04-18
    或更一般的：
        <公司代码>_<年份>_其它若干字段...

    策略：
    - company: 取第一个下划线之前的字段（例如股票代码 688708）；
    - year: 在各个字段里找到第一个 4 位数字的字段，视为年份。
    """

    stem = path.stem
    parts = stem.split("_")
    if not parts:
        return None, None

    company = parts[0]
    year = None
    for p in parts[1:]:
        if len(p) == 4 and p.isdigit():
            year = int(p)
            break

    if year is None:
        return None, None
    return company, year


def build_company_year_texts_cn(input_dir: Path) -> Dict[str, Dict[int, str]]:
    """扫描 input_dir 下所有文件，构建 {company: {year: text}}。"""

    mapping: Dict[str, Dict[int, str]] = defaultdict(dict)

    for file in input_dir.rglob("*"):
        if not file.is_file():
            continue
        company, year = parse_company_year_cn(file)
        if company is None or year is None:
            continue
        text = convert_file_to_text(file)
        mapping[company][year] = text

    return mapping


def run_pipeline_cn(input_dir: str, output_csv: str, output_json: str | None = None):
    input_path = Path(input_dir)
    if not input_path.exists():
        raise FileNotFoundError(f"Input dir not found: {input_dir}")

    company_texts = build_company_year_texts_cn(input_path)

    all_rows = []
    for company, year_dict in company_texts.items():
        rows = process_company_item1s_cn(company, year_dict)
        all_rows.extend(rows)

    df = pd.DataFrame(all_rows)
    output_path = Path(output_csv)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"[INFO] CN CSV results saved to: {output_path}")

    if output_json is not None:
        json_path = Path(output_json)
        json_path.parent.mkdir(parents=True, exist_ok=True)
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(all_rows, f, indent=2, ensure_ascii=False)
        print(f"[INFO] CN JSON results saved to: {json_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Detect 13 categories of services in Chinese annual reports.",
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
        default="data/outputs/servitization_results_cn.csv",
        help="Path to save CN CSV results",
    )
    parser.add_argument(
        "--output-json",
        type=str,
        default="data/outputs/servitization_results_cn.json",
        help="Optional: path to save CN JSON results (with evidence)",
    )

    args = parser.parse_args()
    run_pipeline_cn(args.input_dir, args.output_csv, args.output_json)


if __name__ == "__main__":
    main()
