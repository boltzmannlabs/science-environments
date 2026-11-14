"""Check relative Markdown links in the packaged environment and research folder."""
from pathlib import Path
import re
from urllib.parse import urlparse, unquote
root=Path(__file__).resolve().parents[3]
scopes=[root/'environments/formulation-optimisation-gym-environments',
        root/'research/formulation-optimisation-gym-environments']
errors=[]
count=0
for scope in scopes:
    for document in scope.rglob("*.md"):
        for link in re.findall(r"(?<!!)\[[^\]]+\]\(([^)]+)\)",document.read_text()):
            url=urlparse(link)
            if url.scheme or link.startswith("#"):continue
            target=(document.parent/unquote(url.path)).resolve()
            count+=1
            if not target.exists():errors.append(str(document.relative_to(root))+" -> "+link)
print("Scoped local links checked:",count,"broken:",len(errors))
if errors:
    print("\n".join(errors))
    raise SystemExit(1)
