import sys
import json
import pyperclip

from util.org_util import from_replicate

_arg_i = 0


def _next_arg():
    global _arg_i
    _arg_i += 1
    if len(sys.argv) > _arg_i:
        return sys.argv[_arg_i]
    return None

obj = from_replicate(sys.argv[1:])
print(json.dumps(obj, indent=4))
print(json.dumps(obj))

pyperclip.copy(json.dumps(obj, indent=4))
