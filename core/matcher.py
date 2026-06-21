from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import numpy as np
from rapidfuzz import fuzz
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors

from .config import EnterpriseConfig
from .models import ItemRecord, MatchKind, MatchResult
from .text_normalizer import token_set


@dataclass(slots=True)
class _Candidate:
    ref_idx: int
    cand_idx: int
    lexical: float
    semantic: float = 0.0
    unit: float = 0.0

    @property
    def score(self) -> float:
        # Lexical dominates because it is explainable; semantic resolves paraphrases.
        if self.semantic > 0:
            return min(1.0, 0.62 * self.lexical + 0.28 * self.semantic + 0.10 * self.unit)
        return min(1.0, 0.88 * self.lexical + 0.12 * self.unit)


class LocalSemanticEncoder:
    """Loads embeddings only from a local path. No hub/network access is used."""

    def __init__(self, model_path: str, batch_size: int = 64):
        self.model_path = Path(model_path) if model_path else None
        self.batch_size = batch_size
        self.model = None
        if self.model_path and self.model_path.exists():
            try:
                from sentence_transformers import SentenceTransformer
                self.model = SentenceTransformer(str(self.model_path), local_files_only=True)
            except Exception:
                self.model = None

    @property
    def available(self) -> bool:
        return self.model is not None

    def encode(self, texts: list[str]) -> Optional[np.ndarray]:
        if not self.model or not texts:
            return None
        vec = self.model.encode(
            texts,
            batch_size=self.batch_size,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        return np.asarray(vec, dtype=np.float32)


def _unit_score(a: ItemRecord, b: ItemRecord) -> float:
    if not a.normalized_unit or not b.normalized_unit:
        return 0.5
    return 1.0 if a.normalized_unit == b.normalized_unit else 0.0


def _lexical_score(a: ItemRecord, b: ItemRecord) -> float:
    an, bn = a.normalized_name, b.normalized_name
    if not an or not bn:
        return 0.0
    wr = fuzz.WRatio(an, bn) / 100.0
    ts = fuzz.token_set_ratio(an, bn) / 100.0
    tokens_a, tokens_b = token_set(an), token_set(bn)
    jaccard = len(tokens_a & tokens_b) / max(len(tokens_a | tokens_b), 1)
    return 0.45 * wr + 0.35 * ts + 0.20 * jaccard


def match_items(reference: list[ItemRecord], candidate: list[ItemRecord], config: EnterpriseConfig) -> list[MatchResult]:
    refs = [x for x in reference if not x.is_group]
    cands = [x for x in candidate if not x.is_group]
    results: list[MatchResult] = []
    used_ref: set[int] = set()
    used_cand: set[int] = set()

    # 1) Exact code within same normalized sheet first, then global code.
    by_sheet_code: dict[tuple[str, str], list[int]] = {}
    by_code: dict[str, list[int]] = {}
    for i, item in enumerate(cands):
        if item.normalized_code:
            by_sheet_code.setdefault((item.sheet.lower(), item.normalized_code), []).append(i)
            by_code.setdefault(item.normalized_code, []).append(i)

    for ri, ref in enumerate(refs):
        if not ref.normalized_code:
            continue
        pool = by_sheet_code.get((ref.sheet.lower(), ref.normalized_code), []) or by_code.get(ref.normalized_code, [])
        available = [ci for ci in pool if ci not in used_cand]
        if len(available) == 1:
            ci = available[0]
            used_ref.add(ri); used_cand.add(ci)
            lex = _lexical_score(ref, cands[ci])
            results.append(MatchResult(ri, ci, MatchKind.EXACT_CODE, max(0.90, lex), 1.0, lex, 0.0, _unit_score(ref, cands[ci]), "Trùng mã hiệu"))

    # 2) Exact normalized name.
    name_index: dict[str, list[int]] = {}
    for ci, item in enumerate(cands):
        if ci not in used_cand and item.normalized_name:
            name_index.setdefault(item.normalized_name, []).append(ci)
    for ri, ref in enumerate(refs):
        if ri in used_ref or not ref.normalized_name:
            continue
        available = [ci for ci in name_index.get(ref.normalized_name, []) if ci not in used_cand]
        if len(available) == 1:
            ci = available[0]
            used_ref.add(ri); used_cand.add(ci)
            results.append(MatchResult(ri, ci, MatchKind.EXACT_NAME, 0.98, 0.0, 1.0, 0.0, _unit_score(ref, cands[ci]), "Trùng tên sau chuẩn hóa"))

    remaining_ref = [i for i in range(len(refs)) if i not in used_ref]
    remaining_cand = [i for i in range(len(cands)) if i not in used_cand]

    # 3) Sparse char n-gram nearest neighbours: avoids O(N*M) for large files.
    proposals: list[_Candidate] = []
    if remaining_ref and remaining_cand:
        ref_names = [refs[i].normalized_name or refs[i].normalized_code for i in remaining_ref]
        cand_names = [cands[i].normalized_name or cands[i].normalized_code for i in remaining_cand]
        corpus = ref_names + cand_names
        vectorizer = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), min_df=1, max_features=250_000, dtype=np.float32)
        matrix = vectorizer.fit_transform(corpus)
        ref_matrix = matrix[:len(ref_names)]
        cand_matrix = matrix[len(ref_names):]
        k = min(config.fuzzy_top_k, len(remaining_cand))
        nn = NearestNeighbors(n_neighbors=max(1, k), metric="cosine", algorithm="brute", n_jobs=-1)
        nn.fit(cand_matrix)
        distances, indices = nn.kneighbors(ref_matrix, return_distance=True)
        for local_ri, (dist_row, idx_row) in enumerate(zip(distances, indices)):
            ri = remaining_ref[local_ri]
            for dist, local_ci in zip(dist_row, idx_row):
                ci = remaining_cand[int(local_ci)]
                sparse_cos = max(0.0, 1.0 - float(dist))
                lexical = 0.55 * sparse_cos + 0.45 * _lexical_score(refs[ri], cands[ci])
                proposals.append(_Candidate(ri, ci, lexical, unit=_unit_score(refs[ri], cands[ci])))

        # Semantic score only for the reduced proposal set and only from an on-prem model.
        encoder = LocalSemanticEncoder(config.embedding_model_path, config.semantic_batch_size)
        if config.enable_semantic_matching and encoder.available and proposals:
            unique_ref = sorted({p.ref_idx for p in proposals})
            unique_cand = sorted({p.cand_idx for p in proposals})
            rv = encoder.encode([refs[i].normalized_name for i in unique_ref])
            cv = encoder.encode([cands[i].normalized_name for i in unique_cand])
            if rv is not None and cv is not None:
                rmap = {idx: pos for pos, idx in enumerate(unique_ref)}
                cmap = {idx: pos for pos, idx in enumerate(unique_cand)}
                for p in proposals:
                    p.semantic = float(np.dot(rv[rmap[p.ref_idx]], cv[cmap[p.cand_idx]]))

        # Global greedy assignment by score. Deterministic tie-breakers prevent duplicate reuse.
        proposals.sort(key=lambda p: (-p.score, -p.lexical, p.ref_idx, p.cand_idx))
        for p in proposals:
            if p.ref_idx in used_ref or p.cand_idx in used_cand:
                continue
            if p.score < config.thresholds.name_reject_score:
                continue
            kind = MatchKind.SEMANTIC if p.semantic > p.lexical + 0.08 else MatchKind.FUZZY
            used_ref.add(p.ref_idx); used_cand.add(p.cand_idx)
            results.append(MatchResult(
                p.ref_idx, p.cand_idx, kind, p.score,
                code_score=0.0, lexical_score=p.lexical, semantic_score=p.semantic,
                unit_score=p.unit, reason="Khớp lai TF-IDF/RapidFuzz/BGE-M3 cục bộ",
            ))

    for ri in range(len(refs)):
        if ri not in used_ref:
            results.append(MatchResult(ri, None, MatchKind.MISSING, 0.0, reason="Không có hạng mục tương ứng"))
    for ci in range(len(cands)):
        if ci not in used_cand:
            results.append(MatchResult(None, ci, MatchKind.EXTRA, 0.0, reason="Hạng mục chỉ có trong HSDT"))

    results.sort(key=lambda m: (
        refs[m.reference_index].sheet if m.reference_index is not None else "~",
        refs[m.reference_index].row_number if m.reference_index is not None else 10**9,
        cands[m.candidate_index].row_number if m.candidate_index is not None else 10**9,
    ))
    return results
