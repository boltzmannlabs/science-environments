"""Paper-setup assessment helpers."""
from __future__ import annotations

def summarize_configuration_matrix(matrix: dict) -> dict:
    configs = matrix.get("configs", {})
    return {
        "reference": configs.get("config_A_reference", {}).get("status", "UNRESOLVED"),
        "agent": configs.get("config_B_agent", {}).get("status", "UNRESOLVED"),
        "alternative": configs.get("config_C_alternative", {}).get("status", "UNRESOLVED"),
        "perturbed": configs.get("config_D_perturbed", {}).get("status", "UNRESOLVED"),
        "scientific_qualification": matrix.get("metrics", {}).get("scientific_qualification", "REVIEW"),
    }
