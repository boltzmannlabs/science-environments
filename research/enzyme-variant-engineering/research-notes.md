# Enzyme Variant Optimization Research Notes

## Scientific scope

Improve an existing enzyme for a specified reaction. Full variant sequences,
relevant property estimates, candidate structures and catalytic evidence are
needed to connect a proposed mutation to a defensible design decision.
A stability scan alone does not complete the workflow.

Est30-mediated MHET hydrolysis provides a defined starting enzyme and small-molecule
reaction. PDB 1TQH provides an experimental structural reference, but its covalent
intermediate must not be mistaken for a prepared noncovalent MHET reactant complex.
The exact construct and intended chemical state are qualified during the task.
See the [assignment](../../environments/enzyme-variant-engineering/tasks/est30-mhet/TASK.md).

## Method and evidence choices

The agent chooses methods from configured scientific services rather than following
a provider-specific fixed pipeline. Chemistry, endpoint suitability, reproducibility
and executable availability guide that choice.

Activity, folding stability, melting temperature, thermal half-life, solubility and
binding are different endpoints. Docking and static catalytic geometry can identify
risks but do not establish a reaction rate. Simulation occupancy, if used, needs a
defined chemical state, parameters, sampling and source-supported interpretation.

An optimization round should test a failure explanation, not simply run another
model until a favorable score appears. An independent evaluator must distinguish
changed predictions from experimentally demonstrated improvement.

## Architecture

Keep native tool discovery, input validation, authorization, job handling and
delegation in Agent-Scientist. This environment defines the scientific work and
how its outputs will be compared. Domain subagents are maintained in the
Agent-Scientist repository; no definitions are embedded here.

## Information separation

The design task excludes published winning variants, reference outcomes and the
target study's optimization procedure. Operator reference material stays outside
the design inputs. General chemistry research is allowed. Prompt restrictions
cannot guarantee that a model has not seen a public paper during training.

The two independent arms use their own results and do not read each other's
outputs. A later common-method comparison can evaluate published designs and new
candidates, but must not compare unlike scores or substitute predictions for assays.

Sources are listed in [references.md](references.md). Ongoing run outputs and
earlier pilot outcomes are not published in this contribution.
