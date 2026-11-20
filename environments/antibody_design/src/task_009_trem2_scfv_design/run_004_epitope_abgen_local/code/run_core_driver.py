
import json, sys
from pathlib import Path
sys.path.insert(0, "/home/boltzmann10/agent_sci_boltpro_errors_tools/epitope_abgen")
import main as tool
payload = json.loads(Path(sys.argv[1]).read_text())
input_dir = Path(sys.argv[2]); output_dir = Path(sys.argv[3])
tool.run_core_tool(payload, input_dir, output_dir)
n = tool.validate_generated_outputs(output_dir)
print("VALIDATED_SAMPLES", n)
