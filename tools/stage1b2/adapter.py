"""One-shot, create-only synthetic pilot. Not an authorization authenticator.
No service, scheduler, ACL change, elevation, overwrite or production permit.
Caller must authenticate the separate approval record before invoking this module.
"""
import argparse
import ctypes
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import time
from datetime import datetime, timezone

MAX_BYTES = 16 * 1024 * 1024
class Rejected(Exception):
    def __init__(self, reason, status='FAIL'):
        self.reason, self.status = reason, status
        super().__init__(reason)

def digest(b): return hashlib.sha256(b).hexdigest()
def encoded(x): return (json.dumps(x, ensure_ascii=False, sort_keys=True, indent=2)+'\n').encode('utf-8')
def timestamp(): return datetime.now(timezone.utc).isoformat()
def identifier(s):
    if not isinstance(s,str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,79}',s): raise Rejected('INVALID_ID')
    return s

def safe_name(s):
    if not isinstance(s,str) or not s or '\\' in s or ':' in s or '\x00' in s: raise Rejected('UNSAFE_PATH')
    p=PurePosixPath(s)
    if p.is_absolute() or str(p)!=s or any(x in ('','.','..') for x in p.parts): raise Rejected('UNSAFE_PATH')
    for x in p.parts:
        if x.endswith((' ','.')) or any(ord(c)<32 for c in x) or any(c in '<>"|?*' for c in x): raise Rejected('UNSAFE_PATH')
        if re.match(r'^(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\.|$)',x,re.I): raise Rejected('UNSAFE_PATH')
    return s

def no_links(p):
    p=Path(p).absolute()
    for q in [p,*p.parents]:
        try:s=q.lstat()
        except FileNotFoundError:continue
        if stat.S_ISLNK(s.st_mode) or getattr(s,'st_file_attributes',0)&0x400: raise Rejected('LINK_OR_REPARSE')
    return p

def plain_directory(p):
    p=no_links(p)
    if not p.is_dir(): raise Rejected('DIRECTORY_UNAVAILABLE','BLOCKED')
    return p

def regular_bytes(p, limit=MAX_BYTES):
    p=no_links(p)
    flags=os.O_RDONLY|getattr(os,'O_BINARY',0)|getattr(os,'O_NOFOLLOW',0)
    fd=os.open(p,flags)
    try:
        s=os.fstat(fd)
        if not stat.S_ISREG(s.st_mode) or s.st_size>limit: raise Rejected('NOT_BOUNDED_REGULAR_FILE')
        with os.fdopen(fd,'rb',closefd=False) as f:b=f.read(limit+1)
        t=os.fstat(fd)
        if len(b)>limit or (s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns)!=(t.st_dev,t.st_ino,t.st_size,t.st_mtime_ns):raise Rejected('SOURCE_CHANGED')
    finally:os.close(fd)
    no_links(p)
    return b

def non_elevated():
    # Root is valid in the Linux synthetic harness but never a Windows normal-user claim.
    if os.name=='nt' and ctypes.windll.shell32.IsUserAnAdmin():raise Rejected('ELEVATED_WINDOWS_TOKEN','BLOCKED')

def result(status, reason, **more):
    return dict(status=status,reason=reason,production_permit=False,**more)

def deadline(start,seconds):
    if time.monotonic()-start>seconds: raise Rejected('DEADLINE','UNKNOWN')

def dates(s):
    try:
        t=datetime.fromisoformat(s)
        if t.tzinfo is None: raise ValueError()
        return t
    except (ValueError,TypeError):raise Rejected('INVALID_TIME')

def validate(request, approval):
    if not isinstance(request,dict) or not isinstance(approval,dict):raise Rejected('SCHEMA')
    if request.get('synthetic_only') is not True:raise Rejected('NON_SYNTHETIC_NOT_SUPPORTED','BLOCKED')
    if any(request.get('risk',{}).get(k) is not False for k in ('confidential','destructive','strong_authenticity')):raise Rejected('RISK_UNSUPPORTED','BLOCKED')
    if type(request.get('level')) is not int or request['level'] not in (1,2):raise Rejected('LEVEL_UNSUPPORTED','BLOCKED')
    if request.get('object_kind') not in ('git-document','synthetic-evidence'):raise Rejected('OBJECT_KIND')
    if request['level']==1 and request['object_kind']!='git-document':raise Rejected('LEVEL_TOO_LOW')
    if request.get('archive_required') is not True:
        if request['level']==2:raise Rejected('LEVEL2_ARCHIVE_REQUIRED')
        return None
    identifier(request.get('attempt_id'));identifier(request.get('object_id'))
    if request.get('mode') not in ('direct','handoff'):raise Rejected('MODE')
    if not isinstance(request.get('actor'),str) or not request['actor']:raise Rejected('ACTOR')
    if approval.get('authorization_verified') is not True:raise Rejected('APPROVAL_NOT_VERIFIED','BLOCKED')
    if approval.get('synthetic_only') is not True or approval.get('production_permit') is not False:raise Rejected('APPROVAL_SCOPE')
    for k in ('object_id','actor','source_root','destination','mode'):
        if request.get(k)!=approval.get(k):raise Rejected('APPROVAL_SCOPE')
    if approval.get('request_sha256')!=digest(encoded(request)):raise Rejected('REQUEST_NOT_BOUND')
    now=datetime.now(timezone.utc)
    if not dates(approval.get('valid_from'))<=now<dates(approval.get('valid_until')):raise Rejected('APPROVAL_EXPIRED','BLOCKED')
    if dates(approval.get('retention_until'))<=now:raise Rejected('RETENTION_EXPIRED','BLOCKED')
    if approval.get('operations')!=['create','read'] or approval.get('delete_move_overwrite')!='prohibited':raise Rejected('APPROVAL_OPERATIONS')
    if approval.get('acl_status')!='PASS':raise Rejected('ACL_UNCONFIRMED','BLOCKED')
    files=request.get('files')
    if not isinstance(files,list) or not files or len(files)>64:raise Rejected('FILE_SET')
    seen=set();total=0
    for f in files:
        if not isinstance(f,dict) or set(f)!= {'path','size','sha256'}:raise Rejected('FILE_SCHEMA')
        name=safe_name(f['path']);key=name.casefold()
        if key in seen:raise Rejected('DUPLICATE_PATH')
        seen.add(key)
        if type(f['size']) is not int or not 0<=f['size']<=MAX_BYTES:raise Rejected('SIZE')
        if not isinstance(f['sha256'],str) or not re.fullmatch('[0-9a-f]{64}',f['sha256']):raise Rejected('SHA_SCHEMA')
        total+=f['size']
    if total>MAX_BYTES:raise Rejected('TOTAL_SIZE')
    return files

def publish_new(path, data):
    """Reserve no-replace name and fsync. Receipt last is completion marker.
    A failure leaves reserved incomplete bytes; never retries or overwrites them.
    OS power-loss and directory durability are not claimed.
    """
    no_links(path.parent)
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|getattr(os,'O_BINARY',0)|getattr(os,'O_NOFOLLOW',0),0o600)
    try:
        with os.fdopen(fd,'wb',closefd=False) as f:
            f.write(data);f.flush();os.fsync(f.fileno())
    finally:os.close(fd)
    if regular_bytes(path)!=data:raise Rejected('WRITE_READBACK_MISMATCH')

def save(request, approval, timeout=30, _fault=None):
    """_fault is only a local synthetic-test injection hook, never a CLI input."""
    start=time.monotonic();attempt=None;reserved=False
    try:
        if type(timeout) not in (int,float) or not 0<timeout<=120:raise Rejected('TIMEOUT_RANGE')
        non_elevated();files=validate(request,approval)
        if files is None:return result('NOT_TESTED','LEVEL1_ARCHIVE_NOT_APPLICABLE')
        for key in ('source_root','destination'):
            root=Path(request[key])
            if not root.is_absolute() or '..' in root.parts:raise Rejected('ROOT_NOT_ABSOLUTE')
        source=plain_directory(request['source_root']);dest=plain_directory(request['destination'])
        # No storage inside source or source inside storage: source must remain immutable.
        if source==dest or source in dest.parents or dest in source.parents:raise Rejected('SOURCE_DESTINATION_OVERLAP')
        initial={}
        for f in files:
            deadline(start,timeout);b=regular_bytes(source/f['path'])
            if len(b)!=f['size'] or digest(b)!=f['sha256']:raise Rejected('SOURCE_MISMATCH')
            initial[f['path']]=b
        attempt=dest/request['attempt_id'];no_links(attempt)
        attempt.mkdir(mode=0o700);reserved=True # create-only reservation; any existing attempt fails
        staging=attempt/'staging';staging.mkdir(mode=0o700)
        for f in files:
            deadline(start,timeout);p=staging/f['path'];p.parent.mkdir(parents=True,exist_ok=True)
            if _fault:_fault('before_write',p)
            publish_new(p,initial[f['path']])
        if _fault:_fault('after_copy',source)
        for f in files:
            deadline(start,timeout)
            if regular_bytes(source/f['path'])!=initial[f['path']]:raise Rejected('SOURCE_CHANGED')
        # Directory rename is only within a newly reserved private attempt.
        # Detect any injected collision rather than replacing an existing directory.
        data=attempt/'data'
        if data.exists() or data.is_symlink():raise Rejected('DATA_COLLISION')
        no_links(attempt);os.rename(staging,data)
        manifest={'schema':'stage1b2-manifest-1','object_id':request['object_id'],'attempt_id':request['attempt_id'],'files':files}
        mb=encoded(manifest);publish_new(attempt/'manifest.json',mb)
        receipt={'schema':'stage1b2-receipt-1','object_id':request['object_id'],'attempt_id':request['attempt_id'],'actor':request['actor'],'mode':request['mode'],'request_sha256':digest(encoded(request)),'approval_sha256':digest(encoded(approval)),'manifest_sha256':digest(mb),'created_at':timestamp(),'retention_until':approval['retention_until'],'delete_move_overwrite':'prohibited','synthetic_only':True,'production_permit':False,'CUSTODY_STATUS':'PASS','VERIFICATION_STATUS':'NOT_TESTED','INDEPENDENCE_STATUS':'NOT_TESTED','ACCEPTANCE_STATUS':'PARTIAL'}
        # Actual destination contents must match before receipt/completion.
        verify_files(data,files)
        deadline(start,timeout);publish_new(attempt/'receipt.json',encoded(receipt))
        return result('PASS','SAVED_SYNTHETIC_ONLY',receipt_sha256=digest(encoded(receipt)),manifest_sha256=digest(mb),attempt_id=request['attempt_id'],elapsed=time.monotonic()-start)
    except (Rejected,OSError,ValueError,TypeError,KeyError) as exc:
        code=exc.reason if isinstance(exc,Rejected) else ('ATTEMPT_EXISTS' if isinstance(exc,FileExistsError) else 'IO_OR_SCHEMA_ERROR')
        status=exc.status if isinstance(exc,Rejected) else 'BLOCKED'
        out=result(status,code,receipt_complete=False,elapsed=time.monotonic()-start)
        if reserved and attempt is not None and attempt.is_dir():
            try:publish_new(attempt/'failure.json',encoded(out))
            except (OSError,Rejected):pass # immutable existing failure/receipt never overwritten
        return out

def verify_files(data,files):
    plain_directory(data);actual=[]
    expected_dirs=set()
    for f in files:
        for parent in PurePosixPath(f['path']).parents:
            if str(parent)!='.':expected_dirs.add(str(parent))
    for p in data.rglob('*'):
        no_links(p)
        if p.is_file():actual.append(p.relative_to(data).as_posix())
        elif not p.is_dir():raise Rejected('UNEXPECTED_FILE_TYPE')
        elif p.relative_to(data).as_posix() not in expected_dirs:raise Rejected('UNEXPECTED_DIRECTORY')
    if set(actual)!={f['path'] for f in files} or len(actual)!=len(files):raise Rejected('FILE_SET_MISMATCH')
    for f in files:
        b=regular_bytes(data/f['path'])
        if len(b)!=f['size'] or digest(b)!=f['sha256']:raise Rejected('CONTENT_MISMATCH')

def retrieve(saved, original, expected_receipt_sha256, timeout=30):
    """Read destination directly. Original is a comparison source, not substitute."""
    start=time.monotonic()
    try:
        if type(timeout) not in (int,float) or not 0<timeout<=120:raise Rejected('TIMEOUT_RANGE')
        saved=plain_directory(saved);original=plain_directory(original)
        if saved==original or saved in original.parents or original in saved.parents:raise Rejected('RETRIEVAL_NOT_SEPARATE')
        if set(p.name for p in saved.iterdir())!={'data','manifest.json','receipt.json'}:raise Rejected('INCOMPLETE_OR_EXTRA')
        rb=regular_bytes(saved/'receipt.json')
        if digest(rb)!=expected_receipt_sha256:raise Rejected('RECEIPT_MISMATCH')
        r=json.loads(rb);mb=regular_bytes(saved/'manifest.json');m=json.loads(mb)
        if not isinstance(r,dict) or not isinstance(m,dict):raise Rejected('RECORD_SCHEMA')
        if r.get('schema')!='stage1b2-receipt-1' or m.get('schema')!='stage1b2-manifest-1':raise Rejected('RECORD_SCHEMA')
        if r['manifest_sha256']!=digest(mb):raise Rejected('MANIFEST_MISMATCH')
        if r['production_permit'] is not False or r['synthetic_only'] is not True or r['CUSTODY_STATUS']!='PASS':raise Rejected('RECEIPT_INVALID')
        if r['object_id']!=m['object_id'] or r['attempt_id']!=m['attempt_id']:raise Rejected('OBJECT_BINDING')
        files=m['files']
        if not isinstance(files,list) or not files:raise Rejected('EMPTY_MANIFEST')
        for f in files:
            if not isinstance(f,dict) or set(f)!= {'path','size','sha256'}:raise Rejected('FILE_SCHEMA')
            safe_name(f['path'])
            if type(f['size']) is not int or not 0<=f['size']<=MAX_BYTES or not isinstance(f['sha256'],str) or not re.fullmatch('[0-9a-f]{64}',f['sha256']):raise Rejected('FILE_SCHEMA')
        if len({f['path'].casefold() for f in files})!=len(files):raise Rejected('DUPLICATE_PATH')
        verify_files(saved/'data',files)
        for f in files:
            deadline(start,timeout)
            if regular_bytes(original/f['path'])!=regular_bytes(saved/'data'/f['path']):raise Rejected('ORIGINAL_BYTE_MISMATCH')
        return result('PASS','DIRECT_RETRIEVAL_ALL_BYTES',count=len(files),object_id=m['object_id'],receipt_sha256=digest(rb),manifest_sha256=digest(mb),elapsed=time.monotonic()-start)
    except (Rejected,OSError,ValueError,TypeError,KeyError) as exc:
        return result(exc.status if isinstance(exc,Rejected) else 'BLOCKED',exc.reason if isinstance(exc,Rejected) else 'IO_OR_SCHEMA_ERROR',elapsed=time.monotonic()-start)

def main():
    p=argparse.ArgumentParser();sub=p.add_subparsers(dest='command',required=True)
    s=sub.add_parser('save');s.add_argument('--request',required=True);s.add_argument('--approval',required=True)
    g=sub.add_parser('retrieve');g.add_argument('--saved',required=True);g.add_argument('--original',required=True);g.add_argument('--receipt-sha256',required=True)
    a=p.parse_args()
    try:
        if a.command=='save':r=save(json.loads(regular_bytes(a.request)),json.loads(regular_bytes(a.approval)))
        else:r=retrieve(a.saved,a.original,a.receipt_sha256)
    except (Rejected,OSError,ValueError) as e:r=result('BLOCKED','INPUT_UNAVAILABLE')
    print(json.dumps(r,ensure_ascii=False));return 0 if r['status'] in ('PASS','NOT_TESTED') else 1
if __name__=='__main__':raise SystemExit(main())
