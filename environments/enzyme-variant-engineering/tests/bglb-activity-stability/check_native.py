"""Call the installed native specialist parser without enabling or running it."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

ENV = Path(__file__).resolve().parents[2]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sci-source', type=Path, required=True)
    args = parser.parse_args()
    source = args.sci_source.resolve(strict=True)
    sys.path.insert(0, str(source))
    from agent.specialist_store import Specialist
    from agent.specialist_runtime import context_for
    raw = json.loads((ENV/'specialist/enzyme-variant-specialist.json').read_bytes())
    item = Specialist.parse(raw)
    assert not item.enabled and item.needs_review and not item.automatic
    assert not item.children and not item.sources and not item.skills
    assert set(item.tools) == {'read_file','web_search','web_extract'}
    context = context_for(item, 'Compatibility test only. No model or scientific execution.')
    assert item.instructions in context
    print(json.dumps({'native_definition_compatible': True,
        'agent_revision':subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip(),
        'enabled_or_installed':False,'model_calls':0,'scientific_jobs':0,
        'native_context_contains_instructions':True},indent=2))
