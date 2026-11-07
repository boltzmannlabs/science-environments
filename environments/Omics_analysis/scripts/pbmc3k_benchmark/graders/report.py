"""QC / filtering grader: counts in ranges, cell-level agreement of exclusions, accounting."""
import pandas as pd

from .common import clip01


def _check(value, spec):
    if value is None:
        return None
    if spec["mode"] == "exact":
        return 1.0 if value == spec["value"] else 0.0
    return 1.0 if spec["min"] <= value <= spec["max"] else 0.0


def _prf(pred, truth):
    tp = len(pred & truth)
    p = tp / len(pred) if pred else 0.0
    r = tp / len(truth) if truth else 0.0
    return p, r, (2 * p * r / (p + r) if p + r else 0.0)


def grade(ctx, p):
    ref = pd.read_csv(ctx.ref_dir / "qc_reference.csv", dtype={"cell_id": str})
    all_ids = set(ref.cell_id)
    ref_ret = set(ref.cell_id[ref.cell_status == "retained"])
    cq = ctx.cell_qc()
    if cq is None and p.get("required_file"):
        return 0.0, {"error": "missing or unreadable required file: cell_qc.csv (needs cell_id and status columns)"}
    nums, items = ctx.numbers(), {}
    if cq is not None:
        cov = len(set(cq.cell_id) & all_ids) / len(all_ids)
        items["accounting"] = cov * (0.5 if cq.cell_id.duplicated().any() else 1.0)
        agent_ret = set(cq.cell_id[cq.retained]) & all_ids
        exc = cq[~cq.retained]
        items["exclusion_reasons"] = float((exc.reason != "").mean()) if len(exc) else None
        n_retained = int(cq.retained.sum())
        if "retained_cells" in nums:
            items["manifest_consistent"] = 1.0 if nums["retained_cells"] == n_retained else 0.0
    else:
        a = ctx.assignments()
        agent_ret = set(a.cell_id) & all_ids if a is not None else None
        n_retained = len(a) if a is not None else nums.get("retained_cells")
    for key in ("input_cells", "qc_passing_cells", "doublets_removed", "genes_after_filter"):
        items[key] = _check(nums.get(key), p[key])
    items["retained_cells"] = _check(n_retained, p["retained_cells"])
    info = {"numbers_found": nums}
    if agent_ret is not None:
        pe, re_, fe = _prf(all_ids - agent_ret, all_ids - ref_ret)  # excluded class
        info.update({"excluded_precision": round(pe, 3), "excluded_recall": round(re_, 3), "excluded_f1": round(fe, 3),
                     "retained_f1_info": round(_prf(agent_ret, ref_ret)[2], 3)})
        items["excluded_f1"] = clip01(fe / p["excluded_f1_full_credit"])
    avail = {k: v for k, v in items.items() if v is not None}
    info["items"] = items
    info["not_found"] = [k for k, v in items.items() if v is None]
    return (float(sum(avail.values()) / len(avail)) if avail else None), info
