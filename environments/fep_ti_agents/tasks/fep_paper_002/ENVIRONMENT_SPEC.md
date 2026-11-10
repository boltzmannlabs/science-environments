# FEP-PAPER-002 environment specification

The environment reconstructs a single PTP1B RBFE benchmark edge from the
public 2023 benchmark. It separates frozen source inputs, agent-generated
configuration, execution artifacts and independent evaluation. The published
experimental ΔΔG is a reference comparison value, not a substitute for a new
FEP calculation.

Configuration A is the independently curated benchmark metadata. Configuration
B is generated from the task inputs. Configuration C is a supported OpenFE
alternative with explicitly declared missing protocol fields. Configuration D
contains an intentionally invalid ligand direction and must fail validation.
