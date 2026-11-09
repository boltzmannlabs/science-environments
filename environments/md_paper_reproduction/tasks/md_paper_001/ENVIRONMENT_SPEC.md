# Environment specification

The environment accepts the pinned PDB, paper reference, and one of four
configuration records. It emits a normalized protocol, generated engine input
plan, input hashes, and an execution/qualification decision.

The agent may select a supported alternative only in Config C and must record
each deviation. Config D is intentionally invalid and must be rejected before
production execution.
