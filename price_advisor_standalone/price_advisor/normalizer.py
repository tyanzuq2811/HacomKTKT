from __future__ import annotations

import re
import unicodedata
from functools import lru_cache
from typing import Any

_SPACE = re.compile(r"\s+")
_NON_ALNUM = re.compile(r"[^0-9a-zA-ZÀ-ỹ]+", re.UNICODE)

UNIT_ALIASES = {
    "cai": "cái",
    "cái": "cái",
    "chiec": "cái",
    "chiếc": "cái",
    "bo": "bộ",
    "bộ": "bộ",
    "tu": "tủ",
    "tủ": "tủ",
    "m": "m",
    "met": "m",
    "mét": "m",
    "md": "m",
    "m2": "m²",
    "met2": "m²",
    "mét2": "m²",
    "metvuong": "m²",
    "métvuông": "m²",
    "met vuong": "m²",
    "mét vuông": "m²",
    "m3": "m³",
    "met3": "m³",
    "mét3": "m³",
    "metkhoi": "m³",
    "métkhối": "m³",
    "met khoi": "m³",
    "mét khối": "m³",
    "kg": "kg",
    "tan": "tấn",
    "tấn": "tấn",
    "kw": "kW",
    "kva": "kVA",
    "mm2": "mm²",
    "mm3": "mm³",
}

STOPWORDS = {"va", "và", "cua", "của", "cho", "theo", "kem", "kèm", "hang", "hạng", "muc", "mục"}


def strip_accents(value: Any) -> str:
    text = unicodedata.normalize("NFD", str(value or ""))
    text = "".join(char for char in text if unicodedata.category(char) != "Mn")
    return text.replace("đ", "d").replace("Đ", "D")


@lru_cache(maxsize=100_000)
def normalize_text(text: str) -> str:
    value = unicodedata.normalize("NFKC", str(text or "")).strip().lower()
    value = value.replace("×", "x").replace("Ø", " phi ").replace("ø", " phi ")
    value = value.replace("^2", "2").replace("^3", "3")
    value = _NON_ALNUM.sub(" ", value)
    return _SPACE.sub(" ", value).strip()


@lru_cache(maxsize=100_000)
def normalize_description(text: str) -> str:
    plain = strip_accents(normalize_text(text))
    return " ".join(token for token in plain.split() if token not in STOPWORDS)


@lru_cache(maxsize=10_000)
def normalize_unit(unit: str) -> str:
    value = normalize_text(unit)
    compact = value.replace(" ", "")
    plain = strip_accents(value)
    plain_compact = plain.replace(" ", "")
    for candidate in (value, compact, plain, plain_compact):
        if candidate in UNIT_ALIASES:
            return UNIT_ALIASES[candidate]
    return value


def retrieval_text(description: str, unit: str) -> str:
    normalized_unit = normalize_unit(unit)
    return f"{normalize_description(description)} | unit:{normalized_unit}"

