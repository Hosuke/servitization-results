from pathlib import Path
from typing import Dict, List

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer


class CNMultiLabelServitizationModel:
    """简单的中文多标签服务化模型封装。

    - 采用 transformers 的多标签分类模型（13 维 sigmoid 输出）。
    - categories: 需要与训练时的类别顺序严格一致。
    """

    def __init__(self, model_dir: str, categories: List[str]) -> None:
        self.model_dir = str(model_dir)
        self.categories = list(categories)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        model_path = Path(self.model_dir)
        if not model_path.exists():
            raise FileNotFoundError(f"Model directory not found: {self.model_dir}")

        self.tokenizer = AutoTokenizer.from_pretrained(self.model_dir)
        self.model = AutoModelForSequenceClassification.from_pretrained(self.model_dir)
        self.model.to(self.device)
        self.model.eval()

    @torch.inference_mode()
    def predict_proba(self, sentences: List[str], batch_size: int = 8) -> List[Dict[str, float]]:
        """对一批句子做多标签预测，返回每句每类的概率字典。"""

        results: List[Dict[str, float]] = []
        if not sentences:
            return results

        for i in range(0, len(sentences), batch_size):
            batch = sentences[i : i + batch_size]
            encoded = self.tokenizer(
                batch,
                padding=True,
                truncation=True,
                max_length=512,
                return_tensors="pt",
            )
            encoded = {k: v.to(self.device) for k, v in encoded.items()}

            logits = self.model(**encoded).logits
            probs = torch.sigmoid(logits).cpu().tolist()

            for p in probs:
                prob_dict = {cat: float(p[idx]) for idx, cat in enumerate(self.categories)}
                results.append(prob_dict)

        return results
