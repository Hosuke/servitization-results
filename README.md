# Servitization Detection Project

This project detects 13 categories of services in annual report texts using a dictionary-based approach, and computes simple complementing/substituting service metrics and a supply-chain risk score.

## Structure

- `data/raw/`: input PDF/TXT/etc. files, named as `COMPANY_YEAR.ext` (e.g. `AAPL_2019.pdf`).
- `data/outputs/`: CSV/JSON results.
- `src/servitization/`: core logic modules.
- `scripts/run_detection.py`: convenience runner script.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

(可选) 如需开启 lemma 回退，在 `src/servitization/detector.py` 中把 `USE_SPACY = False` 改为 `True`，并安装 spaCy 模型：

```bash
pip install spacy
python -m spacy download en_core_web_sm
```

## Usage

1. Put raw files under `data/raw/`, e.g.
   - `data/raw/AAPL_2019.pdf`
   - `data/raw/AAPL_2020.txt`

2. Run via module (推荐)：

```bash
export PYTHONPATH=src
python -m servitization.pipeline \
  --input-dir data/raw \
  --output-csv data/outputs/servitization_results.csv \
  --output-json data/outputs/servitization_results.json
```

Or use the helper script:

```bash
python scripts/run_detection.py
```
