# AUTOGENERATED! DO NOT EDIT! File to edit: 01_cli.ipynb (unless otherwise specified).

__all__ = ['ghapi', 'completion_ghapi']

# Cell
from fastcore.utils import *
from .core import *
from collections import defaultdict

# Cell
def _parse_args(a):
    pos,kw = [],{}
    i=1
    while i<len(a):
        x = a[i]
        if x[:2]=='--':
            k = x[2:]
            if k in ('help','debug'): y = 1
            else:
                i += 1
                y = a[i]
            kw[k] = y
        else: pos.append(a[i])
        i += 1
    return pos,kw

def _api(a):
    pos,kw = _parse_args(a)
    token = kw.pop('token',None) or os.getenv('GITHUB_TOKEN')
    api = GhApi(token=token, debug=print_summary if kw.pop('debug',None) else None)
    return api,pos,kw

# Cell
def ghapi():
    api,pos,kw = _api(sys.argv)
    if not pos: return print("Usage: `ghapi` operation {params}")
    op = pos.pop(0)
    parts = op.split('.')
    call = api
    for part in parts: call = getattr(call,part)
    if kw.pop('help', None):
        print(call)
        return
    print(call(*pos, **kw))

# Cell
def completion_ghapi():
    "Python backend for `completion-ghapi` command"
    *parts,final = (sys.argv[1] if len(sys.argv)>1 else '').split('.')
    call = GhApi()
    for part in parts: call = getattr(call,part)
    if hasattr(call,final): res = [final]
    else: res = [o for o in dir(call) if o.startswith(final)]
    return '\n'.join(res)