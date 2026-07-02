from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable, Protocol

from .config import PriceAdvisorConfig
from .normalizer import normalize_unit, retrieval_text
from .schemas import PriceReference


class PriceStore(Protocol):
    def add_references(self, refs: Iterable[PriceReference]) -> int:
        ...

    def search(self, description: str, unit: str, top_k: int) -> list[PriceReference]:
        ...


class LocalEmbeddingFunction:
    def __init__(self, model_name: str, device: str = "cpu"):
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as exc:
            raise RuntimeError("Install sentence-transformers to use local embeddings") from exc
        self.model = SentenceTransformer(model_name, device=device)

    def __call__(self, input: list[str]) -> list[list[float]]:
        vectors = self.model.encode(input, normalize_embeddings=True)
        return vectors.tolist()


class ChromaPriceStore:
    def __init__(self, config: PriceAdvisorConfig):
        try:
            import chromadb
        except ImportError as exc:
            raise RuntimeError("Install chromadb to use ChromaPriceStore") from exc
        config.db_dir.mkdir(parents=True, exist_ok=True)
        self.embedding = LocalEmbeddingFunction(config.embedding_model, config.embedding_device)
        self.client = chromadb.PersistentClient(path=str(config.db_dir))
        self.collection = self.client.get_or_create_collection(
            name=config.collection_name,
            embedding_function=self.embedding,
            metadata={"hnsw:space": "cosine"},
        )

    def add_references(self, refs: Iterable[PriceReference]) -> int:
        records = list(refs)
        if not records:
            return 0
        metadatas = []
        for ref in records:
            metadata = {
                "description": ref.description,
                "unit": normalize_unit(ref.unit),
                "price": float(ref.price),
                "source": ref.source,
                "source_type": ref.source_type,
                "observed_at": ref.observed_at.isoformat() if ref.observed_at else "",
            }
            for key, value in ref.metadata.items():
                if isinstance(value, (str, int, float, bool)):
                    metadata[f"meta_{key}"] = value
            metadatas.append(metadata)
        self.collection.upsert(
            ids=[ref.ref_id for ref in records],
            documents=[retrieval_text(ref.description, ref.unit) for ref in records],
            metadatas=metadatas,
        )
        return len(records)

    def search(self, description: str, unit: str, top_k: int) -> list[PriceReference]:
        normalized_unit = normalize_unit(unit)
        result = self.collection.query(
            query_texts=[retrieval_text(description, normalized_unit)],
            n_results=top_k,
            where={"unit": normalized_unit} if normalized_unit else None,
        )
        ids = result.get("ids", [[]])[0]
        metadatas = result.get("metadatas", [[]])[0]
        refs: list[PriceReference] = []
        for ref_id, metadata in zip(ids, metadatas):
            extra = {
                str(key)[5:]: value
                for key, value in metadata.items()
                if str(key).startswith("meta_")
            }
            refs.append(
                PriceReference(
                    ref_id=ref_id,
                    description=str(metadata.get("description", "")),
                    unit=str(metadata.get("unit", "")),
                    price=float(metadata.get("price", 0)),
                    source=str(metadata.get("source", "")),
                    source_type=str(metadata.get("source_type", "other")),
                    observed_at=metadata.get("observed_at") or None,
                    metadata=extra,
                )
            )
        return refs


class InMemoryPriceStore:
    def __init__(self):
        self.refs: list[PriceReference] = []

    def add_references(self, refs: Iterable[PriceReference]) -> int:
        records = list(refs)
        existing = {ref.ref_id: index for index, ref in enumerate(self.refs)}
        for ref in records:
            if ref.ref_id in existing:
                self.refs[existing[ref.ref_id]] = ref
            else:
                self.refs.append(ref)
        return len(records)

    def search(self, description: str, unit: str, top_k: int) -> list[PriceReference]:
        from rapidfuzz import fuzz

        query = retrieval_text(description, unit)
        normalized_unit = normalize_unit(unit)
        scored = []
        for ref in self.refs:
            if normalized_unit and normalize_unit(ref.unit) != normalized_unit:
                continue
            scored.append((fuzz.WRatio(query, retrieval_text(ref.description, ref.unit)), ref))
        scored.sort(key=lambda item: item[0], reverse=True)
        return [ref for _, ref in scored[:top_k]]


def load_references_from_csv(path: str | Path) -> list[PriceReference]:
    refs: list[PriceReference] = []
    with Path(path).open("r", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            known = {"ref_id", "description", "unit", "price", "source", "source_type", "observed_at"}
            metadata = {key: value for key, value in row.items() if key not in known and value not in (None, "")}
            refs.append(
                PriceReference(
                    ref_id=row.get("ref_id", "").strip(),
                    description=row.get("description", "").strip(),
                    unit=row.get("unit", "").strip(),
                    price=float(row.get("price", "0") or 0),
                    source=row.get("source", "").strip(),
                    source_type=row.get("source_type", "other").strip() or "other",
                    observed_at=row.get("observed_at", "").strip() or None,
                    metadata=metadata,
                )
            )
    return refs
