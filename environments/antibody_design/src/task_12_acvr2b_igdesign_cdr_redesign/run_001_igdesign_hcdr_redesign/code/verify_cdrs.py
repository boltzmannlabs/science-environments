import json
with open("/home/boltzmann4/.sci/profiles/ab_task_10/workspace/5ngv_sequences.json") as f:
    seqs = json.load(f)

H = seqs["H"]["sequence"]
L = seqs["L"]["sequence"]
A = seqs["A"]["sequence"]
print("Heavy (H), len", len(H))
print(H)
print()

native = {"HCDR1":"GYTFTSSY","HCDR2":"INPVSGST","HCDR3":"ARGGWFDY"}
print("=== Locate native HCDRs in heavy chain (1-indexed and 0-indexed) ===")
for name, cdr in native.items():
    idx0 = H.find(cdr)
    if idx0 >= 0:
        print(f"  {name}={cdr}: 0-indexed {idx0}-{idx0+len(cdr)-1}, 1-indexed {idx0+1}-{idx0+len(cdr)}")
    else:
        print(f"  {name}={cdr}: NOT FOUND in heavy chain")

# config positions (0-indexed hypothesis)
cfg = {"HCDR1":list(range(24,32)),"HCDR2":list(range(49,57)),"HCDR3":list(range(95,103))}
print("\n=== Config positions (assumed 0-indexed) -> extracted AA ===")
for name, pos in cfg.items():
    extracted = "".join(H[p] for p in pos)
    print(f"  {name}: positions {pos[0]}-{pos[-1]} (0-idx) -> {extracted}  (native {native[name]})  MATCH={extracted==native[name]}")

print("\nLight (L), len", len(L))
print(L)
print("\nAntigen A (ACVR2B fragment), len", len(A))
print(A)
