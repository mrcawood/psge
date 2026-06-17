"""Core data types (from 08_ARCHITECT_DESIGN.md)."""

from dataclasses import dataclass, field
from typing import Literal

VariantType = Literal["missense", "truncation", "splice"]
Track = Literal["structural", "non_structural"]


@dataclass
class VariantRecord:
    """Preflight output: variant classification and routing."""

    raw: str
    parsed: str
    type: VariantType
    track: Track


@dataclass
class SequencePair:
    """Sequence stage output (PRD FR2)."""

    wt_sequence: str
    mutant_sequence: str


@dataclass
class StructurePair:
    """Structure stage output (PRD FR3)."""

    wt_pdb_path: str
    mutant_pdb_path: str
    backend: str


@dataclass
class DeltaFeatures:
    """Alignment/delta output (PRD FR4). Phase 1.6: extended SASA fields."""

    global_rmsd: float
    local_rmsd: float
    sasa_delta: float
    contact_deltas: dict
    # Phase 1.6: real SASA (BioPython Shrake-Rupley)
    sasa_total_wt: float | None = None
    sasa_total_mut: float | None = None
    delta_sasa_total: float | None = None
    sasa_residue_wt: dict[int, float] | None = None  # UniProt pos -> SASA
    sasa_residue_mut: dict[int, float] | None = None
    delta_sasa_residue: dict[int, float] | None = None
    sasa_patch_8A: float | None = None  # local patch within 8 Å of mutation (WT only)
    sasa_mapping_status: str | None = None  # e.g. "mapped" or "residue_missing"
    sasa_source_pairing: str | None = None  # "same_backend" | "incomparable" (for delta validity)


@dataclass
class StabilityResult:
    """Stability stage output (PRD FR5). Phase 1.6: backend field for provenance."""

    ddg: float
    flags: list[str]
    backend: str = "mock"  # "mock" | "foldx" | "rosetta" | "foldx_failed" | "not_available"
    foldx_version: str | None = None
    stability_signal_band: str | None = None
    audit_passed: bool | None = None
    foldx_provenance: dict | None = None


@dataclass
class ContextFeatures:
    """Context mapping output (PRD FR6). Phase 1.5: 3D Å metrics + membership."""

    # Real 3D distances (Å); primary for mechanism rules
    min_dist_to_fad_atoms_angstrom: float | None = None
    min_dist_to_inhibitor_atoms_angstrom: float | None = None  # ACJ in 3NKS
    min_dist_to_active_site_residue_atoms_angstrom_excl_self: float | None = None  # excluding self
    # Membership (residue in curated set); fallback when ligand atoms missing
    is_in_fad_residue_set: bool = False
    is_in_active_site_residue_set: bool = False
    # Deprecated (sequence-distance); kept for debug
    distance_fad: float | None = None
    distance_active_site: float | None = None
    in_targeting_region: bool = False
    in_membrane_region: bool = False
    n_terminal_targeting_signal_end: int | None = None  # from knowledge, for evidence


MechanismClass = Literal[
    "cofactor_binding_perturbation",
    "active_site_region_perturbation",
    "folding_stability_hydrophobic_core",
    "targeting_signal_perturbation",
    "truncation_misexpression",
    "unknown_mechanism",
]


@dataclass
class MechanismHypothesis:
    """Mechanism classifier output (PRD FR7)."""

    class_: MechanismClass
    confidence: str
    evidence_table: list[dict]
    interpretation: str
    limits: str
    decision_trace: list[str]  # Which rules fired (for transparency)
    secondary_hypotheses: list[str] = field(default_factory=list)  # Additional plausible mechanisms


@dataclass
class Config:
    """Resolved configuration."""

    results_dir: str
    gene: str = "PPOX"
    structure_backend: str = "alphafold"
    stability_backend: str = "foldx"
    cache_dir: str | None = None  # None = use default under data/public/structures
    structure_source: str = "pdb_first"  # pdb_first | predict_first (Phase 1.5)
    foldx_path: str | None = None  # Local FoldX binary; FOLDX_PATH env overrides when set
