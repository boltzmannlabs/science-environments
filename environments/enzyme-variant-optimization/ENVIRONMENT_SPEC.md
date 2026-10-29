# Environment specification

## Identity and objective

- Name: Enzyme Variant Optimization.
- Python distribution: `boltzmann-enzyme-research` (development version `0.1.1`).
- Import/Agent-Scientist plugin identifier: `enzyme_research`.
- Status: In Progress.
- Goal: choose and investigate variants of a supplied enzyme, preserving declared catalytic requirements while evaluating task-specific activity, stability, solubility, and structure evidence.

The scientific question is whether adaptive tool use, with or without the enzyme specialist, produces better task outcomes under a matched resource allowance than a fixed reference. This environment supplies execution and evidence handling. The independent benchmark determines how outcomes are scored.

## Task input

The executable `enzyme-research-task/1` contract contains:

| Field | Meaning |
| --- | --- |
| `task_id`, `objective` | Stable task name and scientific objective. |
| `parent` | Candidate ID, uppercase standard-amino-acid sequence, prepared structure path/SHA-256, and explicit catalytic residue mapping. |
| `substrate` | Molecule name and exact, case-preserved SMILES. |
| `allowed_jobs` | Backend job names obtained from the configured canonical catalogue. |
| `budget` | Round, candidate, scientific-submission, and outstanding-job limits. |
| `evidence_sources` | Task provenance, assumptions, and supporting sources. |
| `evidence_track` | `synthetic`, `computational`, or `protected_measured_library`. |
| `candidate_library` | Required in the measured-library track: public member IDs/sequences and frozen membership hash, without assay answers. |

See [tasks/README.md](tasks/README.md) for task creation and validation. Native research start also checks sequence/structure agreement and catalytic numbering. A local task path is resolved relative to the invoking process, not automatically relative to a JSON file.

## Actions and scientific loop

The external connector handles validation, uploads, submission, status, logs, and downloads. Common operations prepare input, attach verified sequences/structures, synchronize metrics, and build a joined report. Scientific calls use the existing authorized Boltzmann connector.

All listed tools, including EnzyControl, DeepAllo, RFD3, MolProbity, and Catalytic Geometry, resolve their wire names and availability from the current Agent-Scientist catalogue. The environment does not require a separate activation step. A tool disabled in that catalogue remains unavailable.

Single-structure input preparation writes the selected, hash-checked coordinate bytes to the tool's file field: `pdb_path` for EnzyControl, and `input_path` for DeepAllo and RFD3. EnzyControl and DeepAllo accept PDB; RFD3 accepts PDB or CIF. Each request represents one candidate structure. The adapter retains residue mappings and ligand atoms, and does not silently rename unsupported formats or drop ligand data. Scientific settings such as chain, motif, ligand selection, seed, and sample count come from the current tool contract and task. Prepared geometry checks and generated scaffolds still require their own appropriate downstream processing.

Scaffold sample counts must fit the remaining campaign allocation. EnzyControl also uses the declared task substrate. Live scaffold generation requires the campaign's prepared/uploaded file receipt.

The specialist's `investigate` operation uses separate proposer and critic model requests. Each proposal includes a claim, plan, competing explanation, actual observation references, reason for revision, and one explicit scientific action. DiscoveryRSI selects and records the reviewed investigation. A later round cites preceding observations. Critique scores assess investigation quality and are never molecular activity measurements. The proposer/critic share the host model budget.

The base arm uses the same execution/state interfaces without the dedicated specialist loop. The fixed arm uses predetermined policy settings. Those modes do not force a fixed tool order on either adaptive arm. The `reference.py` module is a shared executor helper; real fixed policies, evaluation data, and comparison reports belong to the benchmarking contribution.

## Candidate and artifact semantics

- Sequence candidates retain explicit parent IDs, substitutions, and sequence hashes. Protected-site changes and duplicates are rejected.
- Structure versions must match the candidate sequence. New sequences require new coordinate evidence; parent coordinates do not validate a mutant.
- Coordinate mapping currently targets a single unambiguous, exact-sequence protein chain. Ambiguous assemblies require explicit preparation.
- Backbone-only structures do not satisfy all-atom requirements.
- Quality and geometry results refer to the exact evaluated coordinate version.
- Ligand HETATM records alone do not establish chemical identity. The current ligand-verification path needs a matching 3D SDF in the same returned artifact and a valid graph/coordinate mapping.
- Native ThermoMPNN matrix indices are mapped to structure/sequence positions. Its candidate lookup supports individual substitutions; it does not sum matrix values to score combined mutants.

## Results and persistence

The environment records tasks, candidates, observations, decisions, structure versions, upload/submission receipts, and hash-linked events in local state. A confirmed remote job keeps its original document ID. Uncertain submissions remain explicit rather than being marked successful. Model context can page complete records through snapshot-checked read operations.

Joined reports associate each result with its candidate, source job, artifact, and coordinate version. Empty, corrupt, partial, mismatched, or changed results cannot provide a successful completion receipt. Reports expose incomplete stages and rejected candidates; counts of evidence are not automatic scientific rankings.

A task may configure `csv_headers: ["Seq_id", "Sequences", "SMILES"]` for prepared CSV inputs, as shown in the runtime example. This does not alter molecule letter case or replace tool-specific catalogue validation.

## Limits and evaluation

The current task contract permits up to three rounds, 60 nonparent candidates, and one outstanding scientific job. A stricter benchmark must count its parent within its total allowance; for a 60-sequence comparison configure at most 59 nonparent variants. The fixed-reference v2 helper enforces this inclusive comparison limit. Scientific-submission and model budgets are separately recorded by their host components.

Software acceptance covers installation, true upstream synthetic-loop execution, restart behavior, catalytic preservation, candidate/coordinate association, artifact integrity, output parsing, and explicit failures. Tests may generate mocked predictor outputs but must label them as fixtures. Scientific acceptance requires the separate approved assay endpoint and independent evaluator. No frozen scientific thresholds or enzyme improvement claims are supplied by this environment alone.

## Reproducibility and resources

The core and synthetic loop require Python 3.12+, pinned DiscoveryRSI source, and local disk. The chemistry extra adds RDKit. Native execution also needs the host support packages described in the README. Scientific model GPU/CPU use and external service cost depend on the selected tools; no universal environment GPU requirement is asserted. Seeds, source revisions, catalogue hashes, settings, job records, and resource reports should accompany real runs where available.

See [research notes](../../research/enzyme-variant-optimization/research-notes.md) and [references](../../research/enzyme-variant-optimization/references.md) for rationale and uncertainties.
