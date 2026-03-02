"""Sequence fetch and variant application (PRD FR2)."""

from pathlib import Path

# PPOX human UniProt accession
PPOX_UNIPROT = "P50336"
UNIPROT_FASTA_URL = "https://rest.uniprot.org/uniprotkb/{}.fasta"


def fetch_canonical_sequence(gene: str = "PPOX") -> str:
    """
    Fetch canonical sequence from UniProt.
    For PPOX uses P50336.
    """
    import requests

    url = UNIPROT_FASTA_URL.format(PPOX_UNIPROT)
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    lines = resp.text.strip().split("\n")
    seq = "".join(line for line in lines if not line.startswith(">"))
    return seq


def apply_missense_variant(sequence: str, variant: str) -> str:
    """
    Apply missense variant (e.g. R59W) to sequence.
    Position is 1-based. Returns new sequence.
    """
    import re

    m = re.match(r"^([A-Z])(\d+)([A-Z])$", variant.strip(), re.IGNORECASE)
    if not m:
        raise ValueError(f"Invalid missense variant: {variant}")
    wt_aa, pos_str, mut_aa = m.groups()
    pos = int(pos_str)
    idx = pos - 1
    if idx < 0 or idx >= len(sequence):
        raise ValueError(f"Position {pos} out of range for sequence length {len(sequence)}")
    if sequence[idx] != wt_aa.upper():
        raise ValueError(f"Expected {wt_aa} at position {pos}, found {sequence[idx]}")
    seq_list = list(sequence)
    seq_list[idx] = mut_aa.upper()
    return "".join(seq_list)
