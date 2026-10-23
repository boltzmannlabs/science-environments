"""Adapter for the local Boltzmann PySCF/GPU4PySCF SPE module."""

from __future__ import annotations

import hashlib
import importlib
import importlib.metadata
import json
import sys
import time
import uuid
from dataclasses import replace
from pathlib import Path
from typing import Any

from .adapters import (
    ADAPTER_PROTOCOL_VERSION,
    AdapterCapabilities,
    AdapterExecutionError,
    AdapterFailure,
    AdapterResult,
    AdapterStateError,
    Artifact,
    FailureClass,
    JobState,
    SPERequest,
    UnsupportedCapabilityError,
    UnknownJobError,
    require_compatible_adapter,
)


DEFAULT_LOCAL_MODULE_ROOT = Path(
    "/home/boltzmann15/Esther/Esther/boltzmann_api/spe"
)


def _package_version(name: str) -> str:
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        try:
            module = importlib.import_module(name)
        except ImportError:
            return "unavailable"
        return str(getattr(module, "__version__", "version-unreported"))


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


class LocalBoltzmannSPEAdapter:
    """Synchronous adapter around the local module's ``SPEExecutor``.

    Submission completes in-process because the module exposes a synchronous
    executor. Cancellation is therefore advertised as unsupported.
    """

    protocol_version = ADAPTER_PROTOCOL_VERSION
    _SUPPORTED_SETTINGS = {
        "use_gpu",
        "max_memory_mb",
        "conv_tol",
        "max_cycles",
        "compute_mulliken",
        "compute_hirshfeld",
        "compute_dipole",
        "compute_method_ensemble",
        "dispersion",
        "solvent",
        "use_density_fitting",
        "density_fit_min_atoms",
        "grid_level",
        "cube_grid_dimensions",
        "initial_density_path",
        "checkpoint_density",
    }
    _PROPERTY_ALIASES = {
        "occupations": "orbital_occupations",
        "electron_density_cube": "electron_density_grid",
        "esp_cube": "electrostatic_potential_grid",
    }

    def __init__(
        self,
        artifact_root: Path | str,
        *,
        module_root: Path | str = DEFAULT_LOCAL_MODULE_ROOT,
        max_atoms: int = 100,
    ):
        self.module_root = Path(module_root).resolve()
        self.artifact_root = Path(artifact_root).resolve()
        if not (self.module_root / "src/pipeline/executor.py").is_file():
            raise FileNotFoundError(f"local SPE executor unavailable: {self.module_root}")
        # Import through the repaired public package path.  The directory that
        # contains ``boltzmann_api`` belongs on sys.path, not SPE's internal
        # ``src`` directory.
        package_parent_text = str(self.module_root.parents[1])
        if package_parent_text not in sys.path:
            sys.path.insert(0, package_parent_text)
        executor_module = importlib.import_module("boltzmann_api.spe.pipeline.executor")
        constants_module = importlib.import_module("boltzmann_api.spe.common.constants")
        self._executor_type = executor_module.SPEExecutor
        self._gpu_available = bool(executor_module.GPU_AVAILABLE)
        self._atomic_numbers = {
            element: index
            for index, element in enumerate(constants_module.ELEMENT_SYMBOLS, start=1)
        }
        engine_version = f"PySCF {_package_version('pyscf')}"
        if self._gpu_available:
            engine_version += f"; GPU4PySCF {_package_version('gpu4pyscf')}"
        self._capabilities = AdapterCapabilities(
            adapter_name="local-boltzmann-spe-module",
            adapter_version="0.1.0",
            engine_name="PySCF/GPU4PySCF" if self._gpu_available else "PySCF",
            engine_version=engine_version,
            supported_elements=frozenset(constants_module.ELEMENT_SYMBOLS),
            supported_methods=frozenset(constants_module.SUPPORTED_FUNCTIONALS),
            # 6-31G(d) is the standard parenthetical spelling of 6-31G*.
            # PySCF accepts both spellings; expose the alias so campaign inputs
            # can retain the requested scientific metadata verbatim.
            supported_basis_sets=frozenset(
                {*constants_module.SUPPORTED_BASIS_SETS, "6-31G(d)"}
            ),
            supported_properties=frozenset(
                {
                    "total_energy",
                    "orbital_energies",
                    "homo_lumo_gap",
                    "dipole",
                    "mulliken_charges",
                    "hirshfeld_charges",
                    "scf_history",
                    "orbital_occupations",
                    "spin_diagnostics",
                    "electron_density_grid",
                    "electrostatic_potential_grid",
                }
            ),
            supports_open_shell=True,
            max_atoms=max_atoms,
            supports_cancellation=False,
        )
        self._states: dict[str, JobState] = {}
        self._results: dict[str, AdapterResult] = {}
        self._failures: dict[str, AdapterFailure] = {}

    def capabilities(self) -> AdapterCapabilities:
        return self._capabilities

    def submit(self, request: SPERequest) -> str:
        require_compatible_adapter(self)
        aliases = {
            self._PROPERTY_ALIASES.get(prop, prop)
            for prop in request.requested_properties
        }
        if aliases != set(request.requested_properties):
            request = replace(request, requested_properties=tuple(sorted(aliases)))
        self._capabilities.validate(request)
        electron_count = (
            sum(self._atomic_numbers[atom.element] for atom in request.atoms)
            - request.charge
        )
        unpaired_electrons = request.multiplicity - 1
        if electron_count < 1:
            raise UnsupportedCapabilityError(
                f"charge {request.charge} leaves no electrons for this structure"
            )
        if electron_count < unpaired_electrons or electron_count % 2 != unpaired_electrons % 2:
            raise UnsupportedCapabilityError(
                "charge/multiplicity electron-count mismatch: "
                f"{electron_count} electrons cannot have multiplicity {request.multiplicity}"
            )
        unknown_settings = sorted(set(request.settings) - self._SUPPORTED_SETTINGS)
        if unknown_settings:
            raise UnsupportedCapabilityError(
                f"unsupported adapter settings: {', '.join(unknown_settings)}"
            )
        job_id = f"local-spe-{uuid.uuid4().hex[:12]}"
        self._states[job_id] = JobState.RUNNING
        job_dir = self.artifact_root / job_id
        job_dir.mkdir(parents=True, exist_ok=False)
        input_path = job_dir / "normalized_input.json"
        input_path.write_text(
            json.dumps(request.canonical_payload(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        settings = dict(request.settings)
        coordinates = [(atom.x, atom.y, atom.z) for atom in request.atoms]
        if request.coordinate_unit == "bohr":
            coordinates = [tuple(value * 0.529177210903 for value in xyz) for xyz in coordinates]
        started = time.perf_counter()
        try:
            executor = self._executor_type(verbose=0)
            requested_properties = set(request.requested_properties)
            density_cube_path = (
                str(job_dir / "electron_density.cube")
                if "electron_density_grid" in requested_properties
                else None
            )
            esp_cube_path = (
                str(job_dir / "electrostatic_potential.cube")
                if "electrostatic_potential_grid" in requested_properties
                else None
            )
            result = executor.run(
                atoms=[atom.element for atom in request.atoms],
                coordinates=coordinates,
                name=request.task_id,
                charge=request.charge,
                spin_multiplicity=request.multiplicity,
                functional=request.method,
                basis_set=request.basis,
                use_gpu=bool(settings.get("use_gpu", self._gpu_available)),
                max_memory_mb=int(settings.get("max_memory_mb", 16000)),
                conv_tol=float(settings.get("conv_tol", 1e-9)),
                max_cycles=int(settings.get("max_cycles", 200)),
                compute_mulliken=bool(settings.get("compute_mulliken", True)),
                compute_hirshfeld=bool(settings.get("compute_hirshfeld", True)),
                compute_dipole=bool(settings.get("compute_dipole", True)),
                compute_method_ensemble=bool(settings.get("compute_method_ensemble", False)),
                dispersion=settings.get("dispersion"),
                solvent=settings.get("solvent"),
                use_density_fitting=bool(settings.get("use_density_fitting", True)),
                density_fit_min_atoms=int(settings.get("density_fit_min_atoms", 30)),
                grid_level=settings.get("grid_level"),
                initial_density_path=settings.get("initial_density_path"),
                save_density_path=(
                    str(job_dir / "scf_density_checkpoint.chk")
                    if settings.get("checkpoint_density", False)
                    else None
                ),
                density_cube_path=density_cube_path,
                esp_cube_path=esp_cube_path,
                cube_grid_dimensions=tuple(settings.get("cube_grid_dimensions", (40, 40, 40))),
            )
            raw = result.to_dict()
            raw["adapter_wall_time_seconds"] = time.perf_counter() - started
            raw_path = job_dir / "engine_result.json"
            raw_path.write_text(
                json.dumps(raw, indent=2, sort_keys=True, allow_nan=False) + "\n",
                encoding="utf-8",
            )
            if not result.converged:
                failure = AdapterFailure(
                    FailureClass.NON_CONVERGENCE,
                    result.error_message or "SCF did not converge",
                    retryable=True,
                )
                self._failures[job_id] = failure
                self._states[job_id] = JobState.FAILED
                return job_id
            outputs: dict[str, Any] = {
                "total_energy": {"value": result.total_energy_ha, "unit": "hartree"},
                "nuclear_repulsion": {"value": result.nuclear_repulsion_ha, "unit": "hartree"},
                "electronic_energy": {"value": result.electronic_energy_ha, "unit": "hartree"},
                "converged": result.converged,
                "scf_iterations": result.scf_iterations,
                "final_energy_change": {"value": result.final_energy_change, "unit": "hartree"},
                "homo_energy": {"value": result.homo_energy_ha, "unit": "hartree"},
                "lumo_energy": {"value": result.lumo_energy_ha, "unit": "hartree"},
                "homo_lumo_gap": {"value": result.homo_lumo_gap_ev, "unit": "eV"},
                "orbital_energies": {
                    "values": result.all_orbital_energies_ev,
                    "unit": "eV",
                },
                "orbital_occupations": result.orbital_occupations,
                "beta_orbital_energies": {
                    "values": result.beta_orbital_energies_ev,
                    "unit": "eV",
                },
                "beta_orbital_occupations": result.beta_orbital_occupations,
                "spin_diagnostics": {
                    "spin_square": result.spin_square,
                    "spin_contamination": result.spin_contamination,
                },
                "electron_density_grid": (
                    {
                        "path": result.density_cube_path,
                        "dimensions": result.cube_grid_dimensions,
                        "value_unit": "electrons / bohr^3",
                        "coordinate_unit": "bohr",
                    }
                    if result.density_cube_path
                    else None
                ),
                "electrostatic_potential_grid": (
                    {
                        "path": result.esp_cube_path,
                        "dimensions": result.cube_grid_dimensions,
                        "value_unit": "hartree / elementary_charge",
                        "coordinate_unit": "bohr",
                    }
                    if result.esp_cube_path
                    else None
                ),
                "dipole_magnitude": {"value": result.dipole_magnitude_debye, "unit": "debye"},
                "mulliken_charges": result.mulliken_charges,
                "hirshfeld_charges": result.hirshfeld_charges,
                "scf_energy_history": result.scf_energy_history,
                "backend": result.backend,
                "n_atoms": result.n_atoms,
                "n_electrons": result.n_electrons,
                "n_basis": result.n_basis,
                "engine_wall_time_seconds": result.wall_time_seconds,
                "adapter_wall_time_seconds": raw["adapter_wall_time_seconds"],
            }
            input_sha256 = _sha256(input_path)
            raw_sha256 = _sha256(raw_path)
            executor_source = self.module_root / "src/pipeline/executor.py"
            provenance_path = job_dir / "provenance.json"
            provenance_path.write_text(
                json.dumps(
                    {
                        "adapter": self._capabilities.adapter_name,
                        "adapter_version": self._capabilities.adapter_version,
                        "adapter_protocol": self.protocol_version,
                        "engine": self._capabilities.engine_name,
                        "engine_version": self._capabilities.engine_version,
                        "module_root": str(self.module_root),
                        "module_source": str(executor_source),
                        "module_source_sha256": _sha256(executor_source),
                        "request_fingerprint": request.fingerprint(),
                        "input_artifact_sha256": input_sha256,
                        "engine_result_sha256": raw_sha256,
                        "backend": result.backend,
                        "started_at": result.started_at,
                        "completed_at": result.completed_at,
                    },
                    indent=2,
                    sort_keys=True,
                )
                + "\n",
                encoding="utf-8",
            )
            artifacts = [
                Artifact("normalized-input", str(input_path), input_sha256, "application/json"),
                Artifact("engine-result", str(raw_path), raw_sha256, "application/json"),
                Artifact(
                    "provenance",
                    str(provenance_path),
                    _sha256(provenance_path),
                    "application/json",
                ),
            ]
            if density_cube_path:
                density_path = Path(density_cube_path)
                artifacts.append(
                    Artifact(
                        "electron-density-grid",
                        str(density_path),
                        _sha256(density_path),
                        "chemical/x-gaussian-cube",
                    )
                )
            if esp_cube_path:
                esp_path = Path(esp_cube_path)
                artifacts.append(
                    Artifact(
                        "electrostatic-potential-grid",
                        str(esp_path),
                        _sha256(esp_path),
                        "chemical/x-gaussian-cube",
                    )
                )
            self._results[job_id] = AdapterResult(
                task_id=request.task_id,
                request_fingerprint=request.fingerprint(),
                engine_name=self._capabilities.engine_name,
                engine_version=self._capabilities.engine_version,
                converged=True,
                outputs=outputs,
                artifacts=tuple(artifacts),
                warnings=tuple(result.warnings),
            )
            self._states[job_id] = JobState.COMPLETED
        except Exception as exc:
            failure = AdapterFailure(FailureClass.EXECUTION_ERROR, str(exc), retryable=False)
            self._failures[job_id] = failure
            self._states[job_id] = JobState.FAILED
            error_path = job_dir / "adapter_error.json"
            error_path.write_text(
                json.dumps(
                    {
                        "failure_class": failure.failure_class.value,
                        "message": failure.message,
                        "retryable": failure.retryable,
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
        return job_id

    def status(self, job_id: str) -> JobState:
        try:
            return self._states[job_id]
        except KeyError as exc:
            raise UnknownJobError(f"unknown job: {job_id}") from exc

    def cancel(self, job_id: str) -> None:
        self.status(job_id)
        raise UnsupportedCapabilityError("local synchronous SPE module does not support cancellation")

    def result(self, job_id: str) -> AdapterResult:
        state = self.status(job_id)
        if state == JobState.FAILED:
            raise AdapterExecutionError(self._failures[job_id])
        if state != JobState.COMPLETED:
            raise AdapterStateError(f"result unavailable while job is {state.value}")
        return self._results[job_id]
