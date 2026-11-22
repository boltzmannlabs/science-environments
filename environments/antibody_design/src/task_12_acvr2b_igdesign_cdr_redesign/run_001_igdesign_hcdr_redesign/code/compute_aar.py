"""Compute per-CDR AAR (native recovery) from IgDesign output CSVs.
AAR per CDR = fraction of positions matching the native CDR.
1-shot = first sample; best-of-100 = max over all samples.
"""
import pandas as pd, json, sys, os

NATIVE = {"hcdr1":"GYTFTSSY","hcdr2":"INPVSGST","hcdr3":"ARGGWFDY"}

def aar(gen, nat):
    if len(gen) != len(nat):
        return None, len(gen), len(nat)
    return sum(g==n for g,n in zip(gen,nat))/len(nat), len(gen), len(nat)

def process(csv_path, scope):
    df = pd.read_csv(csv_path)
    cdRs = [c for c in ["hcdr1","hcdr2","hcdr3"] if c in df.columns]
    n = len(df)
    out = {"scope": scope, "csv": csv_path, "n_samples": n, "per_cdr": {}}
    for c in cdRs:
        nat = NATIVE[c]
        aars = []
        for i in range(n):
            a,_,_ = aar(str(df[c].iloc[i]), nat)
            aars.append(a)
        out["per_cdr"][c] = {
            "native": nat,
            "n_positions": len(nat),
            "aar_1shot": aars[0],
            "aar_best_of_100": max(aars),
            "aar_mean": sum(aars)/len(aars),
            "n_native_matches_1shot": int(aars[0]*len(nat)),
            "n_native_matches_best": int(max(aars)*len(nat)),
            "best_sample_idx": int(aars.index(max(aars))),
            "best_seq": str(df[c].iloc[aars.index(max(aars))]),
            "first_seq": str(df[c].iloc[0]),
        }
    return out

if __name__=="__main__":
    results = {}
    for scope, csv in [("HCDR3","output/acvr2b_hcdr3_results.csv"),("HCDR123","output/acvr2b_hcdr123_results.csv")]:
        if os.path.exists(csv):
            results[scope] = process(csv, scope)
    with open("aar_results.json","w") as f:
        json.dump(results, f, indent=2)
    for scope,r in results.items():
        print(f"=== {scope} ({r['n_samples']} samples) ===")
        for c,d in r["per_cdr"].items():
            print(f"  {c}: native={d['native']} 1-shot AAR={d['aar_1shot']:.3f} best-of-100 AAR={d['aar_best_of_100']:.3f} mean={d['aar_mean']:.3f}")
            print(f"      1-shot seq={d['first_seq']}  best seq={d['best_seq']}")
    print("Saved aar_results.json")
