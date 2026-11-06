# Task configuration versions

Each numbered task owns v1, v2 and later reviewed settings versions. A proposed version can contain `agent_alone.json` and `agent_with_specialist.json`; a wholly unselected later version has a short README instead of invented settings. A v1 filename does not mean that a run occurred. Repeated runs of one version get distinct run IDs.

Profiles describe proposed LLM settings, budgets, concurrency, sequence limits and delegation. Every JSON states `draft_not_executed_from_this_profile`, has no historical run mapping, and distinguishes observed model settings from proposed shared defaults. RML/LEH v1 explicitly records `gpt-6.1-sol`, provider `openai-codex` (Codex), and `xhigh` reasoning. These settings are taken from observed native sessions and reused prospectively; these files are not retroactive frozen receipts. The other three tasks have no selected model/effort and require that choice before launch. Null response-token limit means no explicit environment override.

Unbounded token/credit budgets are explicit, not missing decisions. Declare wall-time policy in the frozen run plan. Record owner-authorized scientific-attempt/request increases without resetting accounting or relaxing scientific constraints, concurrency or evaluator reserve.

SCI does not automatically load or enforce these JSON profiles. Read the selected profile, select corresponding native settings, and retain the effective configuration, actual parameters, hashes and amendments with each run. No new execution or permission service is introduced. MLDE and aliases resolving to it are excluded from every profile.
