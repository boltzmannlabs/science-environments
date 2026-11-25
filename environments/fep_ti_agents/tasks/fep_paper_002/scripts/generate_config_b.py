#!/usr/bin/env python3
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    cfg=json.loads((ROOT/'configs/config_B_agent.json').read_text())
    cfg['provenance']={'read_config_A':False,'read_reference_answer':False,'source':'TASK.md and inputs only'}
    cfg['status']='REVIEW'
    (ROOT/'execution').mkdir(exist_ok=True); (ROOT/'execution/generated_config.json').write_text(json.dumps(cfg,indent=2)+'\n'); print(json.dumps(cfg,indent=2)); return cfg
if __name__=='__main__': main()
