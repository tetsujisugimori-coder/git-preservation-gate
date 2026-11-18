"""Conservative pre-publication path detector. Does not rewrite or delete evidence.
Scan text/JSON including keys, nested JSON strings and escaped separators.
A clean result is not proof that all secrets are absent; human scope review remains.
"""
import json
import re

PATH = re.compile(r'(?<![\w>./-])(?:[A-Za-z]:[\\/]|\\\\[^\\\s]+[\\/]|/(?:workspace|home|Users|private|tmp|root)/)', re.I)
ESCAPE = re.compile(r'\\u([0-9a-fA-F]{4})|\\x([0-9a-fA-F]{2})')

def contains_private_path(value):
    if isinstance(value, dict):
        return any(contains_private_path(k) or contains_private_path(v) for k,v in value.items())
    if isinstance(value, (list,tuple)):
        return any(contains_private_path(v) for v in value)
    if not isinstance(value,str):return False
    current=value
    # Bounded decoding: never evaluate code, and refuse excessive nesting/encoding.
    for _ in range(8):
        if PATH.search(current):return True
        decoded=ESCAPE.sub(lambda m:chr(int(m.group(1) or m.group(2),16)),current)
        decoded=decoded.replace('\\/','/').replace('\\\\','\\')
        if decoded==current:return False
        current=decoded
    return True

def inspect_text(text):
    """Return only verdict; never echo potentially private matched values."""
    if contains_private_path(text):return {'accepted':False,'reason':'PRIVATE_PATH_DETECTED'}
    try:value=json.loads(text)
    except (ValueError,TypeError):value=text
    return {'accepted':not contains_private_path(value),'reason':'REVIEW_REQUIRED' if contains_private_path(value) else 'NO_KNOWN_PATH_PATTERN'}
