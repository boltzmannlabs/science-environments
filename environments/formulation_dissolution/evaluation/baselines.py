"""Fixed conventional investigation baseline with zero external calls."""
from environment.state import Episode
from evaluation.verifier import verify

GAPS = ('primary_recall_record','manufacturer_and_product_identity','jurisdiction_lots','dissolution_method_and_criteria','measured_profiles','batch_formula_and_material_attributes','process_and_storage_history')


def run(task: dict) -> dict:
    """Do not assign cause when primary documentation is missing."""
    state = Episode(task)
    missing = list(GAPS)
    state.log('baseline', 'insufficient_data', {'missing_data': missing})
    return {'arm':'A','status':'insufficient_data','verified_facts':[],'hypotheses':[],'predictions':[],'unknowns':missing,'proposed_next_analyses':['obtain primary recall record and method/lot-specific controlled records'],'verifier_findings':verify(state),'budget':{'tool_calls':0,'experiments':0}}
