# Synthesis route planning — environment specification

**Status:** In Progress; current implementation status requires owner review.

This specification summarizes the intended environment and identifies contracts that still need a reviewed definition. The dated [status snapshot](STATUS.md) is historical and does not establish the present state of the implementation.

## Objective and scope

Support planning and comparing candidate synthesis routes for a target molecule. The reported plan includes starting-material constraints and scientific evidence. Define the task scope, exclusions and acceptance criteria in the linked issue before implementation work proceeds.

## Inputs

The status snapshot describes a target molecule, available starting materials or reagents, and user-defined constraints as intended inputs. Define supported representations, validation rules, provenance, access conditions and failure behavior before claiming an executable contract.

## Outputs

Define the route representation, supporting evidence, status signals and interpretation. A submitted or pending job is not a confirmed result; preserve explicit unknown and failure states.

## Evaluation and validation

Define route feasibility, material constraints, ranking criteria, baselines, evidence requirements and qualified review before evaluating results. Tool-interface tests do not establish scientific accuracy. No validated route result is established by the historical status snapshot.

## Dependencies and reproducibility

Record approved tool and service versions, model assets, data sources and revisions, settings, seeds, runtime requirements and reproduction steps when they are confirmed. Keep credentials and protected reference answers outside Git.

## Known limitations

The linked status snapshot reports that some submissions could not be confirmed through final job status and that the associated scientific results were unverified at its cutoff. Confirm current access, job outcomes and evidence with the owner.

## Research and status records

- [Research notes](../../research/synthesis-route-gym/research-notes.md)
- [References](../../research/synthesis-route-gym/references.md)
- [Historical status snapshot](STATUS.md)
