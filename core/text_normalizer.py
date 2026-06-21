from __future__ import annotations

import re
import unicodedata
from functools import lru_cache

_SPACE = re.compile(r"\s+")
_CODE_SEP = re.compile(r"[\s_/\\.]+")
_NON_ALNUM = re.compile(r"[^0-9a-zA-ZÀ-ỹ]+", re.UNICODE)

UNIT_ALIASES = {
    "cai": "cái", "chiếc": "cái", "chiec": "cái",
    "bo": "bộ", "bộ": "bộ", "tu": "tủ", "tủ": "tủ",
    "m": "m", "met": "m", "mét": "m", "md": "m",
    "m2": "m²", "m²": "m²", "m^2": "m²",
    "m3": "m³", "m³": "m³", "m^3": "m³",
    "kg": "kg", "tan": "tấn", "tấn": "tấn",
    "lot": "lô", "lo": "lô", "lô": "lô",
}

STOPWORDS = {
    "va", "và", "cua", "của", "cho", "tai", "tại", "theo", "kem", "kèm",
    "bao", "gom", "gồm", "cac", "các", "hang", "hạng", "muc", "mục",
}


def strip_accents(text: str) -> str:
    text = unicodedata.normalize("NFD", text)
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    return text.replace("đ", "d").replace("Đ", "D")


@lru_cache(maxsize=200_000)
def normalize_text(text: str) -> str:
    s = str(text or "").strip().lower()
    s = s.replace("×", "x").replace("Ø", " phi ").replace("ø", " phi ")
    s = _NON_ALNUM.sub(" ", s)
    s = _SPACE.sub(" ", s).strip()
    return s


@lru_cache(maxsize=200_000)
def normalize_name(text: str) -> str:
    s = strip_accents(normalize_text(text))
    tokens = [t for t in s.split() if t not in STOPWORDS]
    return " ".join(tokens)


@lru_cache(maxsize=200_000)
def normalize_code(code: str) -> str:
    s = strip_accents(str(code or "").strip().upper())
    s = _CODE_SEP.sub("-", s)
    s = re.sub(r"[^A-Z0-9-]", "", s)
    s = re.sub(r"-+", "-", s).strip("-")
    # M 04 -> M-04; preserve meaningful long numeric identifiers.
    m = re.fullmatch(r"([A-Z]+)-?(\d+)", s)
    return f"{m.group(1)}-{m.group(2)}" if m else s


@lru_cache(maxsize=10_000)
def normalize_unit(unit: str) -> str:
    s = normalize_text(unit)
    plain = strip_accents(s)
    return UNIT_ALIASES.get(s, UNIT_ALIASES.get(plain, s))


def token_set(text: str) -> set[str]:
    return set(normalize_name(text).split())


def canonical_id(sheet: str, code: str, name: str, ordinal: int = 0) -> str:
    sh = normalize_name(sheet)[:40]
    cd = normalize_code(code)
    nm = normalize_name(name)[:80]
    base = cd or nm or f"ROW-{ordinal}"
    return f"{sh}::{base}" if sh else base
