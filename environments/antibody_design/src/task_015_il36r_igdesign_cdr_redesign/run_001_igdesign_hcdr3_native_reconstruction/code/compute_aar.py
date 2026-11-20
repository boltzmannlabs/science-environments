#!/usr/bin/env python
"""
Compute per-CDR amino-acid recovery (AAR) from an IgDesign output CSV.

- 1-shot AAR: recovery of a single generated sample vs the native CDR.
- best-of-100 AAR: max recovery over 100 generated samples vs the native CDR.

Per-CDR AAR = (matching positions) / (evaluated positions).
The native sequence, evaluated positions and sampling count are recorded.
"""
import argparse
import json
import pandas as pd
import numpy as np


def per_cdr_recovery(gen: str, nat: str) -> float:
    """Fraction of positions where gen matches nat (positional alignment)."""
    if len(gen) != len(nat):
        # Length mismatch: pad with X (no match) for positional comparison.
        n = max(len(gen), len(nat))
        g = gen.ljust(n, "X")
        a = nat.ljust(n, "X")
    else:
        g, a, n = gen, nat, len(nat)
    return np.mean([g[i] == a[i] for i in range(n)])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True, help="IgDesign output CSV")
    ap.add_argument("--native", required=True,
                    help="JSON mapping region->native CDR sequence")
    ap.add_argument("--budget", required=True, choices=["1shot", "best100"])
    ap.add_argument("--out", required=True, help="output JSON path")
    args = ap.parse_args()

    df = pd.read_csv(args.csv)
    native = json.loads(args.native)
    # region_order columns present in the CSV
    regions = [r for r in native.keys() if r in df.columns]

    if args.budget == "1shot":
        samples = df.iloc[:1]
    else:
        samples = df.iloc[:100]

    result = {"budget": args.budget, "n_samples": len(samples), "native": native,
              "per_cdr_aar": {}}
    for r in regions:
        recs = [per_cdr_recovery(str(x), native[r]) for x in samples[r]]
        if args.budget == "1shot":
            result["per_cdr_aar"][r] = float(recs[0])
        else:
            result["per_cdr_aar"][r] = float(max(recs))
        result["per_cdr_aar"][r + "_all"] = [float(x) for x in recs]

    with open(args.out, "w") as f:
        json.dump(result, f, indent=2)
    print(json.dumps({k: result[k] for k in ["budget", "n_samples", "per_cdr_aar"]
                      if not isinstance(result.get(k), dict) or k != "per_cdr_aar"}, indent=2))
    for r in regions:
        print(f"{r}: AAR={result['per_cdr_aar'][r]:.4f}")


if __name__ == "__main__":
    main()
