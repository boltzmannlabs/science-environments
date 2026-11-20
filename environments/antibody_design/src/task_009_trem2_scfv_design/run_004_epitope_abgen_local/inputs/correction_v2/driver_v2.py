import json, sys
from pathlib import Path
sys.path.insert(0, '/home/boltzmann10/agent_sci_boltpro_errors_tools/epitope_abgen')
import main as tool
payload = json.loads(Path(sys.argv[1]).read_text())
tool.run_core_tool(payload, Path(sys.argv[2]), Path(sys.argv[3]))
n = tool.validate_generated_outputs(Path(sys.argv[3]))
print('VALIDATED_SAMPLES', n)
