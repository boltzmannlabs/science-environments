# Environment specification

## Scientific task and separation of evidence

For each of three targets separately, screen generated synthesis routes for target connectivity, chemically credible disconnections, exact vs analogous experimental precedent, feedstock availability, 100 g isolated/≥95% purity feasibility, hazard, and uncertainty-aware INR costs. The environment deliberately abstains when target identity, sources, yields, pricing or conditions are unresolved. A model pathway score is not experimental evidence.

Input contract: an authorized UTF-8 JSON export with a top-level object mapping original route keys to nested `path` objects; graph nodes contain `smile`, `children`, optional `reaction_name`, `procedure`, `uspto_link`, model scores, and a platform `building_block` flag. A target SMILES is supplied externally and independently reviewed. Original route IDs are retained exactly. A complete reaction scheme including reagents, byproducts and conditions is NOT assured by this format.

Output contract: a JSON summary containing source file *basename*, identity input, original IDs, reaction-node counts, precursor-leaf counts, root-match booleans, parse failures, missing-element-source flags, nonempty citation/procedure counts, and `Hold pending evidence` decisions. Source JSON is never modified. This is a computational input audit, not an exact atom-mapping check.

Safety gates: incorrect root/connectivity; malformed structures; missing step reagent/condition/citation; unresolved impurity stereo, regioisomer or salt/form; inaccessible precursor; unreviewed reactive/hazardous chemistry. No hard failure may be overridden by a weighted score. No experiment is authorized by this software. Physical work requires domain and process safety review.

## Intended expanded evaluation (not implemented)

- Verify exact substrate/product connectivity, atom maps, charges, valence and atom balance with reagents/byproducts included and a qualified reviewer.
- Compare patent/literature exact-substrate precedents separately from analogue transformations; cite primary text and extract reported vs measured yield provenance.
- Supplier-backed India-specific quotes with pack sizes, dates and lead times; scenario backward mass balance from 100 g isolated at ≥95% purity including purification recovery, chromatography feasibility, analytical and waste costs, and uncertainty.
- Human-reviewed weighted scorecard only after critical gates pass: 25% chemistry, 20% evidence, 15% starting materials/cost, 10% yield, 10% isolation, 10% safety/scale and 10% cost confidence (specification target, not computed result).

## Agent recovery

When a step is unclear, stop generation and document objective, blocker, route ID, disputed precursor and evidence. Use Target Identity, Chemistry, Literature/Patent, Supplier/Cost, Process, Analytical/Impurity and Critic roles only where actually available; preserve independent findings and escalate unresolved conflicts to a human. The historical Agent-Sci run used three literature subagents later for bibliographic verification; the earlier 19-route screening itself used separated reviews, not independently run scientific subagents. No agent transcript is published here.
