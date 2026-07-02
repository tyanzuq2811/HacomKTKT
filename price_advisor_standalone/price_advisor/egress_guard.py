from __future__ import annotations

import re

from .schemas import PriceReference

# Chỉ chặn khi phát hiện tên doanh nghiệp cụ thể hoặc cụm từ nhà thầu tiếng Việt.
# Bỏ 'project', 'contractor', 'mall' vì chúng xuất hiện trong mô tả kỹ thuật hợp lệ.
_PROJECT_HINTS = re.compile(r"(?i)\b(hacom|nhà thầu|nha thau)\b")


def anonymize_references(refs: list[PriceReference]) -> list[dict[str, str | int | float]]:
    output: list[dict[str, str | int | float]] = []
    for index, ref in enumerate(refs, start=1):
        output.append(
            {
                "ref": f"REF-{index}",
                "description": ref.description,
                "unit": ref.unit,
                "price": int(round(ref.price)),
                "source_type": ref.source_type,
            }
        )
    return output


def sanitize_prompt_for_external(prompt: str) -> str:
    """Xóa bỏ các từ khóa nhạy cảm thay vì chặn toàn bộ request."""
    return _PROJECT_HINTS.sub("***", prompt)

