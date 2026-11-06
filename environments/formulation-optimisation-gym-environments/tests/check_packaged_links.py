"""Check relative Markdown links in the packaged environment and research folder."""
from pathlib import Path
import re
from urllib.parse import urlparse, unquote
root=Path(__file__).resolve().parents[3]
name="formulation-optimisation-gym-environments"
scopes=(root/"environments"/name,root/"research"/name)
errors=[]
count=0
for document in (p for scope in scopes for p in scope.rglob("*.md")):
    for link in re.findall(r"(?<!!)\[[^\]]+\]\(([^)]+)\)",document.read_text()):
        url=urlparse(link)
        if url.scheme or link.startswith("#"):continue
        target=(document.parent/unquote(url.path)).resolve()
        count+=1
        if not target.exists():errors.append(str(document.relative_to(root))+" -> "+link)
print("Local links checked:",count,"broken:",len(errors))
if errors:
    print("\n".join(errors))
    raise SystemExit(1)
