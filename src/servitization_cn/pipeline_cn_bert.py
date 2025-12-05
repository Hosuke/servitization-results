import argparse
import json
from pathlib import Path
from typing import Dict

import pandas as pd

from models_cn import CNMultiLabelServitizationModel
from servitization_cn.config_keywords_cn import KEYWORDS_CN
from servitization_cn.detector_cn_bert import (
    load_company_texts_cn,
    process_company_item1s_cn_bert,
)


def run_pipeline_cn_bert(
    input_dir: str,
    model_dir: str,
    output_csv: str,
    output_json: str | None = None,
    prob_threshold: float = 0.5,
) -> None:
    input_path = Path(input_dir)
    if not input_path.exists():
        raise FileNotFoundError(f"Input dir not found: {input_dir}")

    categories = list(KEYWORDS_CN.keys())
    model = CNMultiLabelServitizationModel(model_dir=model_dir, categories=categories)

    company_texts: Dict[str, Dict[int, str]] = load_company_texts_cn(input_dir)

    all_rows = []
    for company, year_dict in company_texts.items():
        rows = process_company_item1s_cn_bert(
            company,
            year_dict,
            model=model,
            prob_threshold=prob_threshold,
        )
        all_rows.extend(rows)

    df = pd.DataFrame(all_rows)
    output_path = Path(output_csv)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"[INFO] CN BERT CSV results saved to: {output_path}")

    if output_json is not None:
        json_path = Path(output_json)
        json_path.parent.mkdir(parents=True, exist_ok=True)
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(all_rows, f, indent=2, ensure_ascii=False)
        print(f"[INFO] CN BERT JSON results saved to: {json_path}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Detect 13 categories of services in Chinese annual reports "
            "using a sentence-level multi-label model."
        ),
    )
    parser.add_argument(
        "--input-dir",
        type=str,
        default="data/raw/CN",
        help="Directory that contains CN raw pdf/txt files (default: data/raw/CN)",
    )
    parser.add_argument(
        "--model-dir",
        type=str,
        required=True,
        help="Directory of the fine-tuned multi-label model (transformers format)",
    )
    parser.add_argument(
        "--output-csv",
        type=str,
        default="data/outputs/servitization_results_cn_bert.csv",
        help="Path to save CN BERT CSV results",
    )
    parser.add_argument(
        "--output-json",
        type=str,
        default="data/outputs/servitization_results_cn_bert.json",
        help="Optional: path to save CN BERT JSON results (with evidence)",
    )
    parser.add_argument(
        "--prob-threshold",
        type=float,
        default=0.5,
        help="Probability threshold for activating a service category (default: 0.5)",
    )

    args = parser.parse_args()
    run_pipeline_cn_bert(
        input_dir=args.input_dir,
        model_dir=args.model_dir,
        output_csv=args.output_csv,
        output_json=args.output_json,
        prob_threshold=args.prob_threshold,
    )


if __name__ == "__main__":
    main()
