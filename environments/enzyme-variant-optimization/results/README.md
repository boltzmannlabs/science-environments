# Results and Validation Evidence

Keep technical checks separate from scientific results. The tests in this package use explicitly synthetic values to exercise comparison behavior; they are not enzyme predictions, scientific runs or evidence of specialist benefit.

Full scientific run artifacts belong in a dedicated workspace or `results/local/` (ignored by Git). Publish only reviewed summaries, small shareable artifacts and sanitized provenance. Exclude tokens, API keys, signed URLs, private user paths and billing/account identifiers. Link large scientific datasets through an approved artifact location instead of committing them here.

Every future comparison summary should identify the task/configuration version, frozen input and evaluator hashes, actual approaches/repeats, generated and evaluated counts, workflow completion, supported and unresolved outcomes, usage/cost units and limitations. Include negative results. Old runs made under a different generation policy must retain that distinction.

No scientific result is supplied with this initial implementation. See [implementation status](../STATUS.md) and the [benchmark protocol](../benchmark/PROTOCOL.md).
