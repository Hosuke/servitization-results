import json
from pathlib import Path
import csv


DEF_INPUT_JSON = "data/outputs/servitization_results_cn.json"
DEF_OUTPUT_CSV = "data/outputs/cn_evidence_flat.csv"
DEF_OUTPUT_DIR = "data/outputs/cn_evidence"


def load_results(path: str):
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Input JSON not found: {path}")
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)


def export_flat_csv(rows, csv_path: str):
    """将 evidence 展平成一张 CSV: company, year, category, idx, snippet"""

    out_path = Path(csv_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with out_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["company", "year", "category", "idx", "snippet"])

        for row in rows:
            company = row.get("company")
            year = row.get("year")
            evidence = row.get("evidence") or {}
            # evidence: {category: [snippets...]}
            for cat, snippets in evidence.items():
                for i, snip in enumerate(snippets):
                    # 去掉换行，避免 CSV 过乱
                    cleaned = str(snip).replace("\n", " ").strip()
                    writer.writerow([company, year, cat, i, cleaned])


def export_per_category_txt(rows, out_dir: str):
    """按类别输出 txt，每个文件一行一个 snippet（前面带 company/year）。"""

    base = Path(out_dir)
    base.mkdir(parents=True, exist_ok=True)

    # 先收集 {category: ["[company-year] snippet", ...]}
    buckets = {}
    for row in rows:
        company = row.get("company")
        year = row.get("year")
        evidence = row.get("evidence") or {}
        for cat, snippets in evidence.items():
            key = str(cat)
            lst = buckets.setdefault(key, [])
            for snip in snippets:
                cleaned = str(snip).replace("\n", " ").strip()
                lst.append(f"[{company}-{year}] {cleaned}")

    for cat, snippets in buckets.items():
        # 简单处理一下文件名中的特殊字符
        safe_cat = cat.replace("/", "_")
        out_path = base / f"{safe_cat}.txt"
        with out_path.open("w", encoding="utf-8") as f:
            for line in snippets:
                f.write(line + "\n")


def main():
    rows = load_results(DEF_INPUT_JSON)
    export_flat_csv(rows, DEF_OUTPUT_CSV)
    export_per_category_txt(rows, DEF_OUTPUT_DIR)
    print(f"[INFO] Flat CSV written to: {DEF_OUTPUT_CSV}")
    print(f"[INFO] Per-category TXT written under: {DEF_OUTPUT_DIR}")


if __name__ == "__main__":
    main()
