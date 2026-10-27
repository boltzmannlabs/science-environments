---
name: reaction-template-builder
description: Build reaction-specific geometry templates.
metadata:
  sci:
    category: science
    tags: [enzymes, geometry, evidence]
---

# Reaction Template Builder Skill

Create a per-run catalytic-geometry JSON template with traceable sources and
explicit atom roles. A template describes a mechanistic hypothesis; it does not
prove catalysis or directly enforce generative-model geometry.

## When to Use

An enzyme workflow needs reaction-specific measurements or acceptance criteria.

## Prerequisites

Reaction identity, enzyme/family, substrate, represented structural state and
catalytic role annotations. Use available `web_search` and `web_extract` for
primary mechanistic evidence; if unavailable, request sources rather than claim
research happened. Read `references/template-contract.md` before constructing JSON.

## How to Run

Resolve the mechanism with the user, research primary sources and build
`reaction_template` and `template_binding` JSON files. Upload both files and pass
their storage paths to the current `Catalytic_Geometry` Node contract via the
workflow harness. The current live API requires the binding path; worker support
for inline objects or optional bindings does not change that API requirement.
No template IDs or NFS writes are needed.

## Quick Reference

Evidence order: same enzyme/substrate/state primary study → explicitly qualified
homolog transfer → mechanistic review → user-defined hypothesis. Keep substrate,
transition-state analogue and product geometries distinct.

## Procedure

1. Identify reaction state, catalytic residues, substrate atoms, cofactors, waters,
   metal identity and protonation assumptions. Resolve conflicting mechanisms.
2. Record primary citations for ordered atom roles, intervals and units. Never
   manufacture distances, angles or thresholds that a source does not support.
3. Use semantic roles with explicit structure bindings. Preserve source residue
   labels through generation, sequence design, folding and ligand placement.
4. Add supported checks appropriate to this reaction, not a universal fixed panel.
   Missing hydrogens/side chains/metals require preparation or an unresolved check.
5. Measurement mode reports geometry and validation mode applies the selected
   ranges. Supply the template fields required by the current tool, including
   numeric bounds where its parser requires them even in measurement mode. Use
   justified ranges; missing evidence is an incomplete scientific input, not a
   reason to invent numbers. Geometry is not experimental proof or a reaction
   energy calculation.
6. Store the exact template with this experiment's output and hash. The scientific
   tool assigns template identity; do not submit reviewed/active status claims.

## Pitfalls

Atom order matters: angle atom 2 is the vertex; a dihedral requires four ordered
atoms. A Bürgi–Dunitz angle alone does not establish a complete near-attack pose.
Alignment must not silently exchange symmetry-equivalent or catalytic atoms.
Metal coordination and hydrogen bonds depend on chemical state and atom presence.

## Verification

Each check has sources, rationale, evidence level, state, atom roles and units.
Every resolved binding traces to actual candidate atoms. Unresolved assumptions
remain visible; evidence absent means no claim of reviewed catalytic validity.
