# Servitization Detection Project

For a Chinese description, see [`README_CN.md`](README_CN.md).

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

## Output columns & research usage

The main output is `data/outputs/servitization_results.csv`. Each row corresponds to one firm-year `(company, year)` pair. Columns:

- **`company`**  
  Firm identifier parsed from filename prefix (e.g. `AAPL` from `AAPL_2019.pdf`). Use as the firm index `i` in panel data.

- **`year`**  
  Year parsed from filename (e.g. `2019`). Use as the time index `t`.

- **`service_num`**  
  Number of service categories (out of 13) detected as present in that firm-year (sum of all `flags`).  
  *Research use*: a simple measure of **servitization breadth/intensity** – how many distinct types of services the firm offers.

- **`comp_count`**  
  Count of categories tagged as **complementing** in `CATEGORY_TYPE` that are present (e.g. maintenance, spare parts, installation, technical support, training, integration, etc.).  
  *Research use*: extent of "support / complement"-type servitization (product + aftermarket/support services). Often interpreted as an earlier/less radical stage of servitization.

- **`sub_count`**  
  Count of categories tagged as **substituting** (e.g. leasing & rental, performance-based contracts, recycling/process management). These partly **substitute** for traditional one-off product sales (leasing, pay-per-use, outcome-based contracts).  
  *Research use*: extent of more **radical/outcome-based servitization**, where firms sell availability/performance/usage rather than just products.

- **`risk_score`**  
  Simple weighted index of potential supply-chain/operational risk exposure:  
  `risk_score = 2.0 * sub_count + 0.5 * comp_count`  
  (Weights are illustrative and can be adjusted.)  
  *Research use*: proxy for how deeply the firm is exposed to service-related operational risk (inspired by the idea that performance-based / usage-based contracts shift demand and performance risk back to the manufacturer).

- **`flags`**  
  Dictionary of 13 service categories with 0/1 values, e.g.  
  `{"maintenance_and_repair": 1, "leasing_and_rental": 0, ...}`  
  *Research use*: the detailed **service portfolio structure**. You can expand these to dummy variables for each category, build clusters (maintenance-heavy / solution-heavy / performance-based-heavy), or construct more refined indices (digital intensity, contractual risk intensity, etc.).

- **`evidence`**  
  Dictionary mapping each category to a list of text snippets (and optional `lemma_match::` markers) that triggered the detection.  
  *Research use*: 
  - Manual validation & keyword tuning (check false positives/negatives by reading snippets);  
  - Qualitative evidence in papers (representative quotes for how firms describe their services).

This structure is designed so that you can easily merge `service_num`, `comp_count`, `sub_count`, `risk_score` (and expanded `flags`) with your existing firm-year panel (e.g., financials, performance, stock volatility) to replicate or extend servitization and bullwhip-effect style studies.
