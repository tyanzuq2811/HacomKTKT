from __future__ import annotations

from price_advisor.advisor import PriceAdvisor
from price_advisor.config import PriceAdvisorConfig
from price_advisor.llm_client import DeterministicClient
from price_advisor.rag_store import InMemoryPriceStore
from price_advisor.schemas import AdvisorError, PriceReference, PriceSuggestion


def _advisor(refs: list[PriceReference], llm=None) -> PriceAdvisor:
    store = InMemoryPriceStore()
    store.add_references(refs)
    config = PriceAdvisorConfig(llm_backend="deterministic", min_references=1)
    return PriceAdvisor(config, store=store, llm=llm or DeterministicClient())


def test_suggest_price_uses_python_min_max_and_sources() -> None:
    refs = [
        PriceReference(ref_id="A", description="Cáp đồng XLPE 4x25", unit="m", price=98_000),
        PriceReference(ref_id="B", description="Cáp điện đồng 4 x 25 mm2", unit="m", price=104_000),
        PriceReference(ref_id="C", description="Cáp đồng 4x25mm2", unit="m", price=110_000),
    ]
    result = _advisor(refs).suggest_price("Cáp đồng XLPE/PVC 4x25mm2", "m", refs=refs)

    assert isinstance(result, PriceSuggestion)
    assert result.price_low >= 98_000
    assert result.price_high <= 110_000
    assert result.unit == "m"
    assert result.source_ids == ["A", "B", "C"]


def test_empty_rag_returns_structured_error() -> None:
    result = _advisor([]).suggest_price("Bơm nước", "bộ", refs=[])

    assert isinstance(result, AdvisorError)
    assert "Không có đủ dữ liệu" in result.error


def test_llm_range_is_clamped_to_rag_boundary() -> None:
    class WideClient:
        backend_name = "deterministic"

        def ask_price(self, prompt: str) -> PriceSuggestion:
            return PriceSuggestion(
                price_low=1,
                price_high=999_999,
                unit="m",
                confidence=0.9,
                reasoning="test",
            )

    refs = [
        PriceReference(ref_id="A", description="Cáp đồng XLPE 4x25", unit="m", price=100_000),
        PriceReference(ref_id="B", description="Cáp điện đồng 4x25", unit="m", price=110_000),
    ]
    result = _advisor(refs, WideClient()).suggest_price("Cáp đồng XLPE/PVC 4x25mm2", "m", refs=refs)

    assert isinstance(result, PriceSuggestion)
    assert result.price_low == 95_000
    assert result.price_high == 115_500
    assert result.warnings

