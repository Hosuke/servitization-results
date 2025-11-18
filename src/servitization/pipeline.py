import argparse
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict

import pandas as pd

from .detector import process_company_item1s
from .io_markitdown import convert_file_to_text


FILENAME_PATTERN = re.compile(r"^(.+)_([0-9]{4})$")


def parse_company_year(path: Path):
    """根据文件名解析公司和年份，约定格式：COMPANY_YYYY.xxx"""
    m = FILENAME_PATTERN.match(path.stem)
    if not m:
        return None, None
    company = m.group(1)
    year = int(m.group(2))
    return company, year


def build_company_year_texts(input_dir: Path) -> Dict[str, Dict[int, str]]:
    """扫描 input_dir 下所有文件，构建 {company: {year: text}}"""
    mapping: Dict[str, Dict[int, str]] = defaultdict(dict)

    for file in input_dir.glob("*"):
        if not file.is_file():
            continue
        company, year = parse_company_year(file)
        if company is None or year is None:
            continue
        text = convert_file_to_text(file)
        mapping[company][year] = text

    return mapping


def run_pipeline(input_dir: str, output_csv: str, output_json: str | None = None):
    input_path = Path(input_dir)
    if not input_path.exists():
        raise FileNotFoundError(f"Input dir not found: {input_dir}")

    company_texts = build_company_year_texts(input_path)

    all_rows = []
    for company, year_dict in company_texts.items():
        rows = process_company_item1s(company, year_dict, use_lemma_fallback=False)
        all_rows.extend(rows)

    df = pd.DataFrame(all_rows)
    output_path = Path(output_csv)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"[INFO] CSV results saved to: {output_path}")

    if output_json is not None:
        json_path = Path(output_json)
        json_path.parent.mkdir(parents=True, exist_ok=True)
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(all_rows, f, indent=2, ensure_ascii=False)
        print(f"[INFO] JSON results saved to: {json_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Detect service types in annual reports using 13-category dictionary.",
    )
    parser.add_argument(
        "--input-dir",
        type=str,
        required=True,
        help="Directory that contains raw pdf/txt files, named as COMPANY_YEAR.ext",
    )
    parser.add_argument(
        "--output-csv",
        type=str,
        default="data/outputs/servitization_results.csv",
        help="Path to save CSV results",
    )
    parser.add_argument(
        "--output-json",
        type=str,
        default=None,
        help="Optional: path to save JSON results (with evidence)",
    )

    args = parser.parse_args()
    run_pipeline(args.input_dir, args.output_csv, args.output_json)


if __name__ == "__main__":
    main()
