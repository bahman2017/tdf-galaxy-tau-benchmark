from __future__ import annotations

from tdf_galaxy_tau.validation.failure_modes import build_claim_traceability_matrix


def test_all_claim_ids_present() -> None:
    matrix = build_claim_traceability_matrix()
    assert set(matrix["claim_id"]) == {"A", "B", "C", "D", "E", "F", "G", "H"}


def test_claim_e_not_supported() -> None:
    matrix = build_claim_traceability_matrix()
    e = matrix[matrix["claim_id"] == "E"].iloc[0]
    assert "not_supported" in str(e["status"])
    assert "future" in str(e["status"]).lower() or "not_supported" in str(e["status"])


def test_claim_d_ngc7814_not_supported() -> None:
    matrix = build_claim_traceability_matrix()
    d = matrix[matrix["claim_id"] == "D"].iloc[0]
    assert d["status"] == "not_supported"
    assert "NGC7814" in str(d["claim_text"]) or "works" in str(d["claim_text"])
