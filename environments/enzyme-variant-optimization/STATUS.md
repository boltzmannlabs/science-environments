# Implementation Status

## Implemented locally

- A capability-based full workflow with mandatory tool-generated variants and a results-driven sequence revision.
- Five standalone case-study task specifications in the antibody task format, each with its own full workflow, parent/target, design constraints, execution limits, evaluation table, output artifacts and instructions.
- Shared starting limits, separate native SCI run prompts and a fair comparison protocol.
- An offline numerical comparison helper and tests. It checks comparable measurement records; it does not validate molecular science or execute models.
- Companion proposer and critic definitions in a separate Agent-Scientist working branch, not copied into this environment.

## Before scientific comparison

Prepare the exact shared parent and chemical input bundle for the selected task and freeze a compatible final scoring protocol. Confirm actual tool access through SCI's normal mechanisms. The BLA historical comparison additionally requires checking the supplementary per-variant values and reported energy units. The RML parent construct/model and all relevant ligand states must be established from source inputs rather than assumed from an enzyme name.

Run and review both approaches before reporting specialist benefit. Old Est30 runs used different generation requirements and are not results for this version. Est30 has already been discussed in prior sessions and should not be advertised as an unseen rediscovery benchmark.

## Validation boundary

Software test results are recorded in [results](results/README.md). Passing them proves only the behaviors exercised by those checks. No new scientific run, improved enzyme, completed two-arm comparison, public release or upstream merge is claimed here.

## Development branch

The environment's persistent working branch is `team/enzyme-variant-optimization`, created from `dev`. The owner confirmed `dev` as the destination for a later pull request; this working-branch publication does not merge the environment into `dev` or `main`. Continue environment development on this branch and open the PR only when requested after the work is ready.

The separate Agent-Scientist proposer/critic contribution remains local. Native SCI infrastructure and the installed user profile are unchanged.
