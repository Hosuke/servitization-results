from pathlib import Path
from typing import Union

from markitdown import MarkItDown


_md = MarkItDown()


def convert_file_to_text(path: Union[str, Path]) -> str:
    """统一把 pdf / docx / pptx / txt 等文件转换成纯文本"""
    p = Path(path)
    suffix = p.suffix.lower()

    if suffix in [".txt", ".md", ".markdown"]:
        return p.read_text(encoding="utf-8", errors="ignore")

    # 其他格式用 markitdown
    result = _md.convert(str(p))
    text = getattr(result, "text_content", "") or ""
    return text
