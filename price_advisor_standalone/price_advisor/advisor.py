from __future__ import annotations

from .config import PriceAdvisorConfig
from .egress_guard import anonymize_references, sanitize_prompt_for_external
from .llm_client import LLMClient, build_llm_client
from .normalizer import normalize_unit
from .rag_store import ChromaPriceStore, PriceStore
from .schemas import AdvisorError, PriceReference, PriceSuggestion
from .stats import clamp_price_range, compute_price_stats


class PriceAdvisor:
    def __init__(
        self,
        config: PriceAdvisorConfig | None = None,
        *,
        store: PriceStore | None = None,
        llm: LLMClient | None = None,
    ):
        self.config = config or PriceAdvisorConfig.from_env()
        self.store = store or ChromaPriceStore(self.config)
        self.llm = llm or build_llm_client(self.config)

    def suggest_price(
        self,
        description: str,
        unit: str,
        *,
        quantity: float | None = None,
        refs: list[PriceReference] | None = None,
        top_k: int | None = None,
    ) -> PriceSuggestion | AdvisorError:
        normalized_unit = normalize_unit(unit)
        references = refs if refs is not None else self.store.search(
            description,
            normalized_unit,
            top_k or self.config.top_k,
        )
        if len(references) < self.config.min_references:
            return AdvisorError(
                error="Không có đủ dữ liệu lịch sử trong kho giá RAG",
                description=description,
                unit=normalized_unit,
                reference_count=len(references),
            )

        stats = compute_price_stats(references)
        prompt = self._build_prompt(description, normalized_unit, quantity, references)
        if self.llm.backend_name == "gemini":
            prompt = sanitize_prompt_for_external(prompt)

        suggestion = self.llm.ask_price(prompt)
        low, high, warnings = clamp_price_range(
            suggestion.price_low,
            suggestion.price_high,
            stats,
            max_expansion=self.config.max_range_expansion,
        )
        suggestion.price_low = low
        suggestion.price_high = high
        suggestion.unit = suggestion.unit or normalized_unit
        suggestion.backend = self.llm.backend_name
        suggestion.source_ids = suggestion.source_ids or [ref.ref_id for ref in references]
        suggestion.warnings.extend(warnings)
        if not suggestion.reasoning.strip():
            suggestion.reasoning = "Khoảng giá được suy luận từ dữ liệu lịch sử tương đồng trong kho giá."
        return suggestion

    def _build_prompt(
        self,
        description: str,
        unit: str,
        quantity: float | None,
        refs: list[PriceReference],
    ) -> str:
        stats = compute_price_stats(refs)
        safe_refs = anonymize_references(refs) if self.llm.backend_name == "gemini" else [
            {
                "ref": ref.ref_id,
                "description": ref.description,
                "unit": ref.unit,
                "price": int(round(ref.price)),
                "source_type": ref.source_type,
            }
            for ref in refs
        ]
        history = ", ".join(f"{int(round(ref.price))}" for ref in refs)
        return f"""
Ví dụ:
Input: Cáp đồng 4x25. Đơn vị=m. Lịch sử=[98000, 104000, 110000]. Min=98000. Max=110000.
Output JSON: {{"price_low": 99000, "price_high": 108000, "unit": "m", "confidence": 0.78, "reasoning": "Giá dao động trong vùng 98k-110k/m từ các nguồn gần nhất; chọn khoảng an toàn nằm trong biên dữ liệu.", "source_ids": ["REF-1", "REF-2"]}}

---
Dữ liệu thực tế cần đánh giá:
Input: {description}
Đơn vị={unit}
Khối lượng={quantity if quantity is not None else "không cung cấp"}
Lịch sử=[{history}]
Min={stats.min_price}
Max={stats.max_price}
Median={stats.median_price}
Q1={stats.q1_price}
Q3={stats.q3_price}
Nguồn tham chiếu={safe_refs}

Yêu cầu:
- Trả JSON thuần đúng schema.
- price_low và price_high phải nằm trong hoặc rất sát vùng Min/Max.
- Không dùng số ngoài dữ liệu tham chiếu nếu không có lý do.
- reasoning viết ngắn gọn bằng tiếng Việt.
""".strip()

