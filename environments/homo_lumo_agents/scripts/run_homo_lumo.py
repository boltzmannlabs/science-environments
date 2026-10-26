#!/usr/bin/env python3
"""Run the frozen RHF/STO-3G HOMO-LUMO prototype and independent checks."""
import argparse, hashlib, json, platform, time
from pathlib import Path

EV_PER_HARTREE = 27.211386245988

def run(path):
    started = time.perf_counter()
    base = json.loads(Path(path).read_text())
    result = {"task_id": base.get("task_id"), "name": base.get("name"),
              "status": "failed", "failure_category": None}
    try:
        from pyscf import gto, scf, __version__
        atoms = [(a[0], tuple(a[1:])) for a in base["geometry"]]
        if base.get("multiplicity") != 1:
            raise ValueError("unsupported_state: prototype supports multiplicity=1 only")
        mol = gto.M(atom=atoms, charge=base["charge"], spin=0,
                    basis=base["basis_set"], unit="Angstrom", verbose=0)
        mf = scf.RHF(mol).set(conv_tol=1e-9, max_cycle=100)
        energy = mf.kernel()
        if not mf.converged:
            raise RuntimeError("scf_nonconvergence")
        mo = mf.mo_energy
        occ = mf.mo_occ
        occupied = [i for i, x in enumerate(occ) if x > 1e-8]
        virtual = [i for i, x in enumerate(occ) if x <= 1e-8]
        if not occupied or not virtual:
            raise RuntimeError("orbital_index_error")
        hi, li = occupied[-1], virtual[0]
        homo, lumo = float(mo[hi]), float(mo[li])
        gap = lumo - homo
        if not all(map(lambda x: x == x and abs(x) < float("inf"), [energy, homo, lumo, gap])):
            raise RuntimeError("nonfinite_result")
        result.update({"status":"passed", "energy_hartree":float(energy),
                       "homo_index":hi, "lumo_index":li,
                       "homo_energy_hartree":homo, "lumo_energy_hartree":lumo,
                       "gap_hartree":gap, "gap_ev":gap*EV_PER_HARTREE,
                       "scf_converged":bool(mf.converged),
                       "nmo":int(mol.nao), "engine":"pyscf",
                       "engine_version":__version__, "method":"RHF",
                       "basis_set":base["basis_set"], "charge":base["charge"],
                       "multiplicity":base["multiplicity"],
                       "geometry_sha256":hashlib.sha256(Path(path).read_bytes()).hexdigest()})
    except ValueError as exc:
        result.update({"failure_category":"invalid_input", "error":str(exc)})
    except RuntimeError as exc:
        msg = str(exc); result.update({"failure_category":msg.split(":",1)[0], "error":msg})
    except Exception as exc:
        result.update({"failure_category":"runtime_error", "error":f"{type(exc).__name__}: {exc}"})
    result["wall_time_s"] = round(time.perf_counter() - started, 6)
    return result

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tasks", nargs="+", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()
    rows = [run(x) for x in args.tasks]
    out = {"protocol":"RHF/STO-3G", "results":rows,
           "pass_count":sum(x["status"] == "passed" for x in rows),
           "task_count":len(rows), "reproducibility":"repeat with same protocol and engine version"}
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))

if __name__ == "__main__":
    main()
