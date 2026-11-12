"""Generate the task inventory from the agent-facing Markdown documents."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def build_config(root=ROOT):
    tasks=[]
    for path in sorted((root/'tasks').glob('task_*.md')):
        text=path.read_text()
        field=lambda name: re.search(r'\*\*'+name+r':\*\*\s*([^\n]+)',text).group(1).rstrip('\\').strip()
        tasks.append({'id':path.name[:8],'file':'tasks/'+path.name,
                      'title':text.splitlines()[0].removeprefix('# Task: '),
                      'target':field('Name'),'pdb':'6CM4',
                      'task_format':'goal_oriented','grading_mode':'manual_review_required',
                      'owner_file':'benchmark/'+path.name,
                      'expected_outputs':re.findall(r'^\|\s*`([^`]+)`\s*\|',text,re.M),
                      'input_files':re.findall(r'`(inputs/[^`]+)`',text),
                      'source_record_count':400,'shortlist_count':8,'final_priority_count':2})
    return {'name':'hit-identification','status':'draft_runtime_unqualified',
            'task_count':len(tasks),'working_directory':'environment_root','tasks':tasks}

if __name__=='__main__':
    path=ROOT/'config/environment.json'
    path.write_text(json.dumps(build_config(),indent=2)+'\n')
    print(path)
