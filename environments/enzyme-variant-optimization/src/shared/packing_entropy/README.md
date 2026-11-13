# Executed packing-entropy assessment code

The actual agent-generated driver and helpers used for the four-sequence BLA comparison are retained here. FASPR, PACKMAN, OpenMM and PDBFixer remain external pinned scientific dependencies. Exact method settings and preparation history are recorded in the BLA results.

This archived driver expects the original reviewed assessment layout and its source/settings/input manifests, external executables and isolated environment. Restore that layout in a separate workspace before use. It preserves completed native preparations and records scientific warning/error evidence; the source-linked ResourceWarning policy does not accept numerical warnings.

The calculation uses the same full483 backbone, repacks all sidechains for parent and variants, completes only the terminal OXT, checks atom identity/geometry and measures native PACKMAN packing entropy. It does not run MD or reproduce the original paper’s MD preparation. No third-party scientific implementation or binary is redistributed.
