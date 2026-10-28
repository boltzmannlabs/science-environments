"""Frozen host policies for experimental, evidence-triggered advisor composition."""
import hashlib
import json
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictInt, model_validator

ROLES = ('strategist', 'condition_scientist', 'route_critic')
MODES = ('main_role_prompt', 'main_all_advisors', 'main_adaptive')
Role = Literal['strategist', 'condition_scientist', 'route_critic']


class OrchestrationPolicy(BaseModel):
    model_config = ConfigDict(frozen=True, extra='forbid')
    schema_version: Literal['srg-orchestration-policy-v1'] = 'srg-orchestration-policy-v1'
    policy_id: str = Field(default='experimental-v1', min_length=1, max_length=120, strict=True)
    experimental: StrictBool = False
    enabled_roles: tuple[Role, ...] = Field(default=(), max_length=3)
    max_consultations: StrictInt = Field(default=0, ge=0, le=3)
    priority: tuple[Role, ...] = Field(default=ROLES, min_length=3, max_length=3)

    @model_validator(mode='after')
    def consistent(self):
        if len(set(self.enabled_roles)) != len(self.enabled_roles):
            raise ValueError('Enabled advisor roles must be unique')
        if len(self.priority) != 3 or set(self.priority) != set(ROLES):
            raise ValueError('Priority must contain each advisor exactly once')
        if bool(self.enabled_roles) != bool(self.max_consultations):
            raise ValueError('Enabled advisors require a positive consultation allowance')
        if self.max_consultations > len(self.enabled_roles):
            raise ValueError('Allowance exceeds enabled advisors')
        if self.enabled_roles and not self.experimental:
            raise ValueError('Advisor activation requires explicit experimental opt-in')
        return self


def normalize_policy(mode, policy=None):
    """Return an independent JSON policy; no inferred evidence of promotion."""
    if mode not in MODES:
        raise ValueError('Unknown orchestration mode')
    defaults = {'policy_id': mode + '-v1'}
    if mode == 'main_all_advisors':
        defaults.update(experimental=True, enabled_roles=ROLES, max_consultations=3)
    if isinstance(policy, OrchestrationPolicy):
        policy = policy.model_dump(mode='json')
    if policy is not None and not isinstance(policy, dict):
        raise ValueError('Orchestration policy must be an object')
    checked = OrchestrationPolicy.model_validate({**defaults, **(policy or {})})
    if mode == 'main_role_prompt' and checked.enabled_roles:
        raise ValueError('Role prompting cannot invoke additional advisors')
    if mode == 'main_adaptive' and checked.max_consultations > 1:
        raise ValueError('Experimental adaptive policy permits at most one advisor')
    if mode == 'main_all_advisors' and (set(checked.enabled_roles) != set(ROLES) or checked.max_consultations != 3):
        raise ValueError('All-advisor ablation must enable all three advisors')
    return checked.model_dump(mode='json')


def policy_fingerprint(policy):
    return hashlib.sha256(json.dumps(policy, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def role_prompt_instructions():
    """Parallel substantive instructions, not an exact prompt-matched causal control.

    Sources: strategist_runtime._prompt, route_condition_runtime._prompt and
    route_critic_runtime._prompt (Step 11). The single main conversation receives
    their domain rules and uncertainty limits, excluding specialist-only JSON
    serialization and tool-free delegation requirements. Context selection,
    timing, token use and conversation isolation still differ across arms.
    """
    return (
        'Use the same main conversation and configured main-profile model to apply the following three '
        'scientific perspectives. You select and execute existing metered environment actions yourself. '
        'These instructions provide no extra resources, authority, evidence or permission. Preserve inventory, '
        'constraints and the shared budget; reserve resources for submission. Separate predictions from '
        'experimental or literature support and report unsuccessful or incomplete work explicitly.\n\n'
        'Retrosynthesis Strategist: When public observations reveal a stalled search, failed branches or '
        'missing materials, compare only observed alternatives. Prefer a useful unexpanded frontier molecule; '
        'do not repeat failed branches or expand material known to be in inventory. Use only observed route '
        'IDs, alternative IDs, frontier SMILES and constraint keys. In each bounded strategy recommendation, '
        'identify at most two useful expansions and keep their number within the available action allowance; '
        'a recommendation does not grant permission or budget. State the relevant constraints and uncertainty. '
        'An empty recommendation is appropriate when no allowed alternative is useful. Treat every proposed '
        'route or disconnection as unvalidated until host evidence establishes its support.\n\n'
        'Condition Optimisation Scientist: Use measured route feedback and the catalog bound to the exact '
        'route and step. Select one useful eligible unqueried candidate from that catalog, or abstain; '
        'verify it is unattempted and observation resources remain. Cite only revealed measurement source IDs '
        'and state why the next observation is useful. Unknown candidate outcomes remain unknown. Candidate '
        'recipes are alternatives: a measured alternative never establishes the yield of an unchanged route. '
        'Do not invent conditions, yields, experimental support or uncertainty estimates. Host provenance '
        'describes reused measurements, not a newly conducted experiment. Use canonical route references and '
        'existing metered actions when making a revision; no advice itself modifies a stored route.\n\n'
        'Route Critic: Review the registered shortlist using only the public host packet. Separate definite '
        'contract errors from unresolved chemistry. Missing conditions, source ambiguity, incomplete atom '
        'accounting and uncertain model transfer do not prove a reaction impossible. A source connectivity '
        'match does not establish experimental feasibility. Prioritize concise material concerns; at most '
        'eight findings is a limit, not a quota, and empty findings are valid. Cite only known route, step, '
        'fact and source IDs. Treat a finding as an error only when a host deterministic error establishes '
        'the exact same route, step and category; otherwise retain review-level or informational uncertainty. '
        'Consider route_structure, constraint_violation, unsupported_transformation, missing_materials, '
        'stereochemistry, quantity_conflict, incomplete_conditions and model_domain_mismatch. Keep each '
        'rationale concise (at most 600 characters), grounded in cited facts and qualified by its support. '
        'Choose whether to revise_route, recheck, retain_uncertainty or make no change. Recommend at most one '
        'recheck from the available host menu per review. Execute any recheck or revision through ordinary '
        'metered actions. Do not upgrade source claims or opinions into host authority, invent numeric values, '
        'recipes or evidence, or claim access to hidden evaluator answers.'
    )
