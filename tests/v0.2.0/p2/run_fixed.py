"""Finite offline comparison. External immutable fixture, never an operation permit."""
import sys,json,hashlib,platform,datetime,subprocess,pathlib

def main():
 checker,fixture,out=sys.argv[1:];p=pathlib.Path
 sha=lambda b:hashlib.sha256(b).hexdigest()
 now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
 log={'started_at':now(),'kind':'SYNTHETIC_ONLY','environment':{'python':sys.version,'platform':platform.platform()},'rows':[]}
 # Refuse overwriting any prior record before invoking the checker.
 with open(out,'x',encoding='utf-8') as target:
  try:
   raw=p(fixture).read_bytes();cases=json.loads(raw)
   log.update(checker_sha256=sha(p(checker).read_bytes()),oracle_sha256=sha(raw))
   if type(cases) is not list or not cases: raise ValueError('empty or invalid case inventory')
   if any(type(c) is not dict or set(c)!={'id','title','input','expected','rationale'} or type(c['id']) is not str or not c['id'] or type(c['expected']) is not dict for c in cases): raise ValueError('case shape invalid')
   if len({c['id'] for c in cases})!=len(cases): raise ValueError('duplicate case ID')
  except (OSError,ValueError,TypeError,KeyError) as exc:
   log.update(test_status='NOT_TESTED',preflight_error=type(exc).__name__+': '+str(exc),ended_at=now())
   json.dump(log,target,ensure_ascii=False,indent=2);target.write('\n')
   print('preflight failed; no checker execution',file=sys.stderr);return 2
  for c in cases:
   raw=json.dumps(c['input'],sort_keys=True).encode()
   r={'id':c['id'],'input':c['input'],'input_sha256':sha(raw),'expected':c['expected'],'started_at':now(),'timeout_seconds':5,'retry':0,'command':['python','-I','check.py']}
   try:
    a=subprocess.run([sys.executable,'-I',checker],input=raw,capture_output=True,timeout=5)
    r.update(exit_code=a.returncode,stdout=a.stdout.decode(errors='replace'),stderr=a.stderr.decode(errors='replace'))
    try: actual=json.loads(r['stdout'])
    except ValueError: actual=None
    r.update(actual=actual,status='PASS' if actual==c['expected'] and a.returncode==0 and not a.stderr else 'FAIL')
   except subprocess.TimeoutExpired as e:
    r.update(status='UNKNOWN',exit_code=None,stdout=(e.stdout or b'').decode(errors='replace'),stderr=(e.stderr or b'').decode(errors='replace'),error='TIMEOUT')
   except OSError as e:
    r.update(status='UNKNOWN',exit_code=None,stdout='',stderr=str(e),error='EXECUTION_ERROR')
   r['ended_at']=now();log['rows'].append(r)
  log['ended_at']=now();log['counts']={k:sum(x['status']==k for x in log['rows']) for k in ['PASS','FAIL','UNKNOWN']}
  json.dump(log,target,ensure_ascii=False,indent=2);target.write('\n')
 print(log['counts']);return 0 if log['counts']['PASS']==len(log['rows']) else 1
if __name__=='__main__':sys.exit(main())
