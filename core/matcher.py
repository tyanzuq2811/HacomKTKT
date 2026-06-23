from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import numpy as np
from rapidfuzz import fuzz
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors

from .config import EnterpriseConfig
from .models import ItemRecord, MatchKind, MatchResult, RowType
from .text_normalizer import normalize_name, token_set


@dataclass(slots=True)
class _Proposal:
    ref_idx: int
    cand_idx: int
    kind: MatchKind
    score: float
    structure: float = 0.0
    code: float = 0.0
    lexical: float = 0.0
    semantic: float = 0.0
    reranker: float = 0.0
    unit: float = 0.0
    row_distance: Optional[int] = None
    reason: str = ""


class LocalSemanticEncoder:
    """Local-only multilingual embedding model.

    Qwen3-Embedding and BGE-M3 can both be loaded through SentenceTransformer.
    No hub identifier is accepted here: the path must exist on the company
    server, and local_files_only is always enabled.
    """

    def __init__(self, model_path: str, batch_size: int = 32):
        self.model = None
        self.batch_size = batch_size
        path = Path(model_path) if model_path else None
        self.is_qwen3 = bool(path and "qwen3" in str(path).lower())
        if path and path.exists():
            try:
                from sentence_transformers import SentenceTransformer
                self.model = SentenceTransformer(
                    str(path),
                    local_files_only=True,
                    trust_remote_code=True,
                )
            except Exception:
                self.model = None

    @property
    def available(self) -> bool:
        return self.model is not None

    def encode(self, texts: list[str], *, is_query: bool = False) -> Optional[np.ndarray]:
        if not self.model or not texts:
            return None
        kwargs = {
            "batch_size": self.batch_size,
            "normalize_embeddings": True,
            "show_progress_bar": False,
        }
        # Qwen3 Embedding is instruction-aware. Trong so sánh ngang hàng,
        # hướng query/document chỉ là kỹ thuật truy hồi; pipeline chạy lại theo
        # chiều ngược để loại bỏ thiên lệch do thứ tự hồ sơ.
        if is_query and self.is_qwen3:
            kwargs["prompt"] = (
                "Retrieve the line from another bid that describes the same work item, "
                "hierarchy, unit, material, brand, origin and technical specification; ignore price."
            )
        try:
            vectors = self.model.encode(texts, **kwargs)
        except TypeError:
            kwargs.pop("prompt", None)
            vectors = self.model.encode(texts, **kwargs)
        return np.asarray(vectors, dtype=np.float32)


class LocalReranker:
    """Optional local CrossEncoder-compatible reranker.

    The adapter fails closed: if the model architecture is not supported by the
    installed sentence-transformers version, matching continues with rules,
    lexical similarity and embeddings instead of attempting a network download.
    """

    def __init__(self, model_path: str, batch_size: int = 16):
        self.model = None
        self.batch_size = batch_size
        path = Path(model_path) if model_path else None
        if path and path.exists():
            try:
                from sentence_transformers import CrossEncoder
                self.model = CrossEncoder(
                    str(path),
                    local_files_only=True,
                    trust_remote_code=True,
                    prompts={
                        "boq_matching": (
                            "Judge whether two bid BOQ lines refer to the same work item. Consider "
                            "hierarchy, code, description, unit, material, brand, origin and technical "
                            "specification; ignore price differences and do not prefer either line."
                        )
                    },
                    default_prompt_name="boq_matching",
                )
            except Exception:
                self.model = None

    @property
    def available(self) -> bool:
        return self.model is not None

    def predict(self, pairs: list[tuple[str, str]]) -> Optional[np.ndarray]:
        if not self.model or not pairs:
            return None
        try:
            import torch
            scores = self.model.predict(
                pairs,
                batch_size=self.batch_size,
                show_progress_bar=False,
                activation_fn=torch.nn.Sigmoid(),
            )
        except (ImportError, TypeError):
            scores = self.model.predict(pairs, batch_size=self.batch_size, show_progress_bar=False)
        scores = np.asarray(scores, dtype=np.float32).reshape(-1)
        # CrossEncoders may return logits. Convert to 0..1 safely.
        if np.any((scores < 0) | (scores > 1)):
            scores = 1.0 / (1.0 + np.exp(-scores))
        return scores


def _sheet(item: ItemRecord) -> str:
    return normalize_name(item.sheet)


def _unit_score(a: ItemRecord, b: ItemRecord) -> float:
    if not a.normalized_unit or not b.normalized_unit:
        return 0.5
    return 1.0 if a.normalized_unit == b.normalized_unit else 0.0


def _path_score(a: ItemRecord, b: ItemRecord) -> float:
    if not a.normalized_path or not b.normalized_path:
        return 0.5
    return fuzz.token_set_ratio(a.normalized_path, b.normalized_path) / 100.0


def _lexical_score(a: ItemRecord, b: ItemRecord) -> float:
    left = " ".join(filter(None, [a.normalized_name, normalize_name(a.material), a.normalized_code]))
    right = " ".join(filter(None, [b.normalized_name, normalize_name(b.material), b.normalized_code]))
    if not left or not right:
        return 0.0
    wr = fuzz.WRatio(left, right) / 100.0
    token = fuzz.token_set_ratio(left, right) / 100.0
    ta, tb = token_set(left), token_set(right)
    jaccard = len(ta & tb) / max(len(ta | tb), 1)
    return 0.45 * wr + 0.40 * token + 0.15 * jaccard


def _combined_text(item: ItemRecord) -> str:
    technical = " ".join(f"{key} {value}" for key, value in sorted(item.technical_specs.items()))
    return " | ".join(filter(None, [
        normalize_name(item.sheet),
        item.normalized_path,
        item.normalized_stt,
        item.normalized_code,
        item.normalized_name,
        item.normalized_unit,
        normalize_name(item.material),
        normalize_name(item.brand),
        normalize_name(item.origin),
        normalize_name(technical),
    ]))


def _make_result(proposal: _Proposal) -> MatchResult:
    return MatchResult(
        proposal.ref_idx,
        proposal.cand_idx,
        proposal.kind,
        proposal.score,
        structure_score=proposal.structure,
        code_score=proposal.code,
        lexical_score=proposal.lexical,
        semantic_score=proposal.semantic,
        reranker_score=proposal.reranker,
        unit_score=proposal.unit,
        row_distance=proposal.row_distance,
        reason=proposal.reason,
    )


def _assign(
    proposal: _Proposal,
    results: list[MatchResult],
    used_ref: set[int],
    used_cand: set[int],
) -> bool:
    if proposal.ref_idx in used_ref or proposal.cand_idx in used_cand:
        return False
    used_ref.add(proposal.ref_idx)
    used_cand.add(proposal.cand_idx)
    results.append(_make_result(proposal))
    return True


def match_items(reference: list[ItemRecord], candidate: list[ItemRecord], config: EnterpriseConfig) -> list[MatchResult]:
    refs = [item for item in reference if item.is_comparable]
    cands = [item for item in candidate if item.is_comparable]
    results: list[MatchResult] = []
    used_ref: set[int] = set()
    used_cand: set[int] = set()

    # 1. Exact structural key. Duplicates are resolved by row proximity rather
    # than collapsed, preserving every BOQ line.
    ref_by_structure: dict[str, list[int]] = defaultdict(list)
    cand_by_structure: dict[str, list[int]] = defaultdict(list)
    for idx, item in enumerate(refs):
        if item.structural_key:
            ref_by_structure[item.structural_key].append(idx)
    for idx, item in enumerate(cands):
        if item.structural_key:
            cand_by_structure[item.structural_key].append(idx)
    for key in sorted(set(ref_by_structure) & set(cand_by_structure)):
        rpool = ref_by_structure[key]
        cpool = cand_by_structure[key]
        candidates: list[_Proposal] = []
        for ri in rpool:
            for ci in cpool:
                lex = _lexical_score(refs[ri], cands[ci])
                distance = abs(refs[ri].row_number - cands[ci].row_number)
                candidates.append(_Proposal(
                    ri, ci, MatchKind.EXACT_STRUCTURE,
                    score=max(0.96, 0.96 + min(0.03, lex * 0.03)),
                    structure=1.0, code=1.0 if refs[ri].normalized_code and refs[ri].normalized_code == cands[ci].normalized_code else 0.0,
                    lexical=lex, unit=_unit_score(refs[ri], cands[ci]), row_distance=distance,
                    reason="Trùng sheet, phân cấp và khóa cấu trúc",
                ))
        for proposal in sorted(candidates, key=lambda p: (-p.score, p.row_distance or 0)):
            _assign(proposal, results, used_ref, used_cand)

    # 2. Exact code in same sheet/path, then same sheet.
    cand_by_code: dict[tuple[str, str], list[int]] = defaultdict(list)
    for ci, item in enumerate(cands):
        if ci not in used_cand and item.normalized_code:
            cand_by_code[(_sheet(item), item.normalized_code)].append(ci)
    proposals: list[_Proposal] = []
    for ri, ref in enumerate(refs):
        if ri in used_ref or not ref.normalized_code:
            continue
        for ci in cand_by_code.get((_sheet(ref), ref.normalized_code), []):
            if ci in used_cand:
                continue
            cand = cands[ci]
            lex = _lexical_score(ref, cand)
            path = _path_score(ref, cand)
            distance = abs(ref.row_number - cand.row_number)
            score = 0.76 + 0.12 * lex + 0.08 * path + 0.04 * _unit_score(ref, cand)
            proposals.append(_Proposal(
                ri, ci, MatchKind.EXACT_CODE, min(score, 0.99),
                structure=path, code=1.0, lexical=lex, unit=_unit_score(ref, cand), row_distance=distance,
                reason="Trùng mã hiệu trong cùng sheet",
            ))
    for proposal in sorted(proposals, key=lambda p: (-p.score, p.row_distance or 0)):
        _assign(proposal, results, used_ref, used_cand)

    # 3. Exact normalized name in the same sheet and row type. Resolve repeated
    # names by path similarity and row proximity.
    cand_by_name: dict[tuple[str, RowType, str], list[int]] = defaultdict(list)
    for ci, item in enumerate(cands):
        if ci not in used_cand and item.normalized_name:
            cand_by_name[(_sheet(item), item.row_type, item.normalized_name)].append(ci)
    proposals = []
    for ri, ref in enumerate(refs):
        if ri in used_ref or not ref.normalized_name:
            continue
        for ci in cand_by_name.get((_sheet(ref), ref.row_type, ref.normalized_name), []):
            if ci in used_cand:
                continue
            cand = cands[ci]
            path = _path_score(ref, cand)
            distance = abs(ref.row_number - cand.row_number)
            score = 0.88 + 0.07 * path + 0.05 * _unit_score(ref, cand)
            proposals.append(_Proposal(
                ri, ci, MatchKind.EXACT_NAME, min(score, 0.99),
                structure=path, lexical=1.0, unit=_unit_score(ref, cand), row_distance=distance,
                reason="Trùng tên sau chuẩn hóa",
            ))
    for proposal in sorted(proposals, key=lambda p: (-p.score, p.row_distance or 0)):
        _assign(proposal, results, used_ref, used_cand)

    # 4. Row-near pass for files sharing the same BOQ template. This handles a
    # few inserted/deleted rows without spending O(N*M).
    refs_by_sheet: dict[tuple[str, RowType], list[int]] = defaultdict(list)
    cands_by_sheet: dict[tuple[str, RowType], list[int]] = defaultdict(list)
    for ri, item in enumerate(refs):
        if ri not in used_ref:
            refs_by_sheet[(_sheet(item), item.row_type)].append(ri)
    for ci, item in enumerate(cands):
        if ci not in used_cand:
            cands_by_sheet[(_sheet(item), item.row_type)].append(ci)
    proposals = []
    for key, rpool in refs_by_sheet.items():
        cpool = cands_by_sheet.get(key, [])
        if not cpool:
            continue
        for ri in rpool:
            ref = refs[ri]
            nearby = sorted(cpool, key=lambda ci: abs(cands[ci].row_number - ref.row_number))[:8]
            for ci in nearby:
                if ci in used_cand:
                    continue
                cand = cands[ci]
                distance = abs(cand.row_number - ref.row_number)
                if distance > 35:
                    continue
                lex = _lexical_score(ref, cand)
                path = _path_score(ref, cand)
                unit = _unit_score(ref, cand)
                score = 0.58 * lex + 0.22 * path + 0.12 * unit + 0.08 * max(0.0, 1.0 - distance / 35)
                if score >= max(config.thresholds.name_reject_score, 0.68):
                    proposals.append(_Proposal(
                        ri, ci, MatchKind.ROW_NEAR, score,
                        structure=path, lexical=lex, unit=unit, row_distance=distance,
                        reason="Cùng sheet, cùng loại dòng và gần vị trí",
                    ))
    for proposal in sorted(proposals, key=lambda p: (-p.score, p.row_distance or 0)):
        _assign(proposal, results, used_ref, used_cand)

    # 5. Sparse character TF-IDF shortlist. Work per sheet and row type to avoid
    # a dense N*M matrix on large files.
    proposals = []
    for key, rpool_all in refs_by_sheet.items():
        rpool = [ri for ri in rpool_all if ri not in used_ref]
        cpool = [ci for ci in cands_by_sheet.get(key, []) if ci not in used_cand]
        if not rpool or not cpool:
            continue
        ref_texts = [_combined_text(refs[ri]) for ri in rpool]
        cand_texts = [_combined_text(cands[ci]) for ci in cpool]
        try:
            vectorizer = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), min_df=1, max_features=120_000, sublinear_tf=True)
            matrix = vectorizer.fit_transform(cand_texts + ref_texts)
            cand_matrix = matrix[:len(cand_texts)]
            ref_matrix = matrix[len(cand_texts):]
            top_k = min(config.fuzzy_top_k, len(cpool))
            nn = NearestNeighbors(n_neighbors=top_k, metric="cosine", algorithm="brute", n_jobs=-1)
            nn.fit(cand_matrix)
            distances, indices = nn.kneighbors(ref_matrix)
        except ValueError:
            continue
        for local_ri, ri in enumerate(rpool):
            ref = refs[ri]
            for distance, local_ci in zip(distances[local_ri], indices[local_ri]):
                ci = cpool[int(local_ci)]
                cand = cands[ci]
                tfidf = max(0.0, 1.0 - float(distance))
                lex = _lexical_score(ref, cand)
                path = _path_score(ref, cand)
                unit = _unit_score(ref, cand)
                score = 0.46 * tfidf + 0.34 * lex + 0.12 * path + 0.08 * unit
                if score >= config.thresholds.name_reject_score:
                    proposals.append(_Proposal(
                        ri, ci, MatchKind.FUZZY, score,
                        structure=path, lexical=max(tfidf, lex), unit=unit,
                        row_distance=abs(ref.row_number - cand.row_number),
                        reason="TF-IDF ký tự + RapidFuzz",
                    ))

    # 6. Optional local embedding stage. It does two jobs:
    #    a) enrich lexical proposals; and
    #    b) retrieve additional semantically close candidates that lexical
    #       matching may miss. All inference stays local and is limited to the
    #       still-unmatched rows.
    encoder = LocalSemanticEncoder(config.embedding_model_path, config.semantic_batch_size) if config.enable_semantic_matching else None
    if encoder and encoder.available:
        remaining_ref = sorted(ri for ri in range(len(refs)) if ri not in used_ref)
        remaining_cand = sorted(ci for ci in range(len(cands)) if ci not in used_cand)
        ref_vectors = encoder.encode([_combined_text(refs[i]) for i in remaining_ref], is_query=True)
        cand_vectors = encoder.encode([_combined_text(cands[i]) for i in remaining_cand], is_query=False)
        if ref_vectors is not None and cand_vectors is not None:
            ref_pos = {idx: pos for pos, idx in enumerate(remaining_ref)}
            cand_pos = {idx: pos for pos, idx in enumerate(remaining_cand)}

            # Enrich proposals already shortlisted by TF-IDF/RapidFuzz.
            for proposal in proposals:
                if proposal.ref_idx not in ref_pos or proposal.cand_idx not in cand_pos:
                    continue
                proposal.semantic = float(np.dot(
                    ref_vectors[ref_pos[proposal.ref_idx]],
                    cand_vectors[cand_pos[proposal.cand_idx]],
                ))
                proposal.semantic = max(0.0, min(1.0, proposal.semantic))
                proposal.score = min(1.0, 0.54 * proposal.score + 0.36 * proposal.semantic + 0.10 * proposal.unit)
                proposal.kind = MatchKind.SEMANTIC
                proposal.reason += " + embedding local"

            # Semantic nearest-neighbour retrieval per sheet and row type.
            # This recovers equivalent items whose wording differs strongly.
            for key, rpool_all in refs_by_sheet.items():
                rpool = [ri for ri in rpool_all if ri in ref_pos]
                cpool = [ci for ci in cands_by_sheet.get(key, []) if ci in cand_pos]
                if not rpool or not cpool:
                    continue
                cmat = np.asarray([cand_vectors[cand_pos[ci]] for ci in cpool], dtype=np.float32)
                rmat = np.asarray([ref_vectors[ref_pos[ri]] for ri in rpool], dtype=np.float32)
                top_k = min(config.semantic_top_k, len(cpool))
                if top_k <= 0:
                    continue
                nn = NearestNeighbors(n_neighbors=top_k, metric="cosine", algorithm="brute", n_jobs=-1)
                nn.fit(cmat)
                distances, indices = nn.kneighbors(rmat)
                for local_ri, ri in enumerate(rpool):
                    ref = refs[ri]
                    for distance, local_ci in zip(distances[local_ri], indices[local_ri]):
                        ci = cpool[int(local_ci)]
                        cand = cands[ci]
                        semantic = max(0.0, min(1.0, 1.0 - float(distance)))
                        lexical = _lexical_score(ref, cand)
                        path = _path_score(ref, cand)
                        unit = _unit_score(ref, cand)
                        score = 0.56 * semantic + 0.20 * lexical + 0.14 * path + 0.10 * unit
                        if semantic >= 0.46 and score >= max(0.52, config.thresholds.name_reject_score - 0.06):
                            proposals.append(_Proposal(
                                ri, ci, MatchKind.SEMANTIC, score,
                                structure=path, lexical=lexical, semantic=semantic, unit=unit,
                                row_distance=abs(ref.row_number - cand.row_number),
                                reason="Qwen3/BGE embedding nearest-neighbour local",
                            ))

    # Deduplicate pair proposals before the expensive reranker. Keep the best
    # score while preserving the richest component scores for auditability.
    best_proposals: dict[tuple[int, int], _Proposal] = {}
    for proposal in proposals:
        key = (proposal.ref_idx, proposal.cand_idx)
        current = best_proposals.get(key)
        if current is None or proposal.score > current.score:
            best_proposals[key] = proposal
    proposals = list(best_proposals.values())

    reranker = LocalReranker(config.reranker_model_path, config.reranker_batch_size) if config.enable_reranker else None
    if reranker and reranker.available and proposals:
        shortlist = sorted(proposals, key=lambda p: p.score, reverse=True)[: min(len(proposals), 20_000)]
        pairs = [(_combined_text(refs[p.ref_idx]), _combined_text(cands[p.cand_idx])) for p in shortlist]
        scores = reranker.predict(pairs)
        if scores is not None:
            for p, rr in zip(shortlist, scores):
                p.reranker = float(rr)
                p.score = min(1.0, 0.65 * p.score + 0.35 * p.reranker)
                p.kind = MatchKind.RERANKED
                p.reason += " + reranker local"

    for proposal in sorted(proposals, key=lambda p: (-p.score, p.row_distance or 0)):
        if proposal.score >= config.thresholds.name_reject_score:
            _assign(proposal, results, used_ref, used_cand)

    # Explicit unmatched rows, preserving one-to-one semantics.
    for ri in range(len(refs)):
        if ri not in used_ref:
            results.append(MatchResult(ri, None, MatchKind.MISSING, 0.0, reason="Không tìm thấy hạng mục tương ứng"))
    for ci in range(len(cands)):
        if ci not in used_cand:
            results.append(MatchResult(None, ci, MatchKind.EXTRA, 0.0, reason="Không tìm thấy hạng mục tương ứng trong hồ sơ còn lại"))

    results.sort(key=lambda m: (
        refs[m.reference_index].sheet if m.reference_index is not None else cands[m.candidate_index].sheet,
        refs[m.reference_index].row_number if m.reference_index is not None else cands[m.candidate_index].row_number,
        m.candidate_index if m.candidate_index is not None else -1,
    ))
    return results
