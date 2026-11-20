
import json, peptides, sys
items = json.load(open(sys.argv[1])); out = {}
for it in items:
    p = peptides.Peptide(it["seq"])
    out[it["id"]] = {"pI": p.isoelectric_point(), "MW_da": p.molecular_weight()}
json.dump(out, open(sys.argv[2], "w"))
