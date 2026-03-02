"""Variant string parsing and classification (PRD FR1, 05_MECHANISM_TAXONOMY)."""

import re
from typing import Literal

VariantType = Literal["missense", "truncation", "splice"]
Track = Literal["structural", "non_structural"]

# Missense: single-letter aa, position, single-letter aa (e.g. R59W, I12T)
_MISSENSE_RE = re.compile(r"^[A-Z]\d+[A-Z]$", re.IGNORECASE)


def classify_variant(raw: str) -> tuple[VariantType, Track]:
    """
    Classify variant type and routing track.
    - Splice (IVS pattern) → splice, non_structural
    - Frameshift/truncation (ins, del, dup, fs) → truncation, non_structural
    - Missense (p.? pattern) → missense, structural
    """
    s = raw.strip()
    # Splice: IVS in name (e.g. IVS2-2 a→c)
    if "IVS" in s.upper():
        return ("splice", "non_structural")
    # Truncation/frameshift: ins, del, dup, ins/del, fs
    lower = s.lower()
    if any(x in lower for x in ("ins", "del", "dup", "fs", "*")):
        return ("truncation", "non_structural")
    # Missense: standard p.? format
    if _MISSENSE_RE.match(s):
        return ("missense", "structural")
    # Default: treat unrecognized as missense for now (conservative)
    return ("missense", "structural")


def variant_position(variant: str) -> int | None:
    """Extract residue position from missense variant (e.g. R59W -> 59)."""
    m = _MISSENSE_RE.match(variant.strip())
    if not m:
        return None
    return int(re.search(r"\d+", variant).group())
