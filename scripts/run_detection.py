from pathlib import Path

from servitization.pipeline import run_pipeline


if __name__ == "__main__":
    input_dir = "data/raw"
    output_csv = "data/outputs/servitization_results.csv"
    output_json = "data/outputs/servitization_results.json"

    Path("data/outputs").mkdir(parents=True, exist_ok=True)
    run_pipeline(input_dir, output_csv, output_json)
