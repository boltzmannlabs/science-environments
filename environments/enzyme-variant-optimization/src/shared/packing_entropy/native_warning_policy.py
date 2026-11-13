"""Exact source-linked operational warning allowlist; never numerical warnings."""
def is_known_resource_warning(w):
    if w['category']!='ResourceWarning': return False
    filename=w['filename'].replace('\\','/')
    if filename.endswith('/packman/molecule/molecule.py') and w['lineno']==48:
        return w['message'].startswith('unclosed file <_io.TextIOWrapper ')
    if filename.endswith('/multiprocessing/pool.py'):
        return w['message'].startswith('unclosed running multiprocessing pool <multiprocessing.pool.ThreadPool ')
    return False
