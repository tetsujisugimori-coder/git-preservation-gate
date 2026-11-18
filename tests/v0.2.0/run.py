"""Finite offline runner: fixed external oracle, one subprocess per input."""
import argparse,datetime,hashlib,json,platform,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def main():
    p=argparse.ArgumentParser(); p.add_argument('--log',required=True); a=p.parse_args()
    log={'started_at':now(),'environment':{'python':sys.version,'platform':platform.platform()},'kind':'SYNTHETIC_ONLY','production_permit':False,'runs':[]}
    try:
        raw=(ROOT/'cases.json').read_bytes(); cases=json.loads(raw)
        log['inputs']={f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in ('cases.json','check.py','run.py','oracle-lock.json')}
        lock=json.loads((ROOT/'oracle-lock.json').read_text())
        if not cases or len({c['id'] for c in cases})!=len(cases): raise ValueError('case inventory invalid')
        if hashlib.sha256(raw).hexdigest()!=lock['files']['cases.json']: raise ValueError('oracle digest mismatch')
        if any(set(c)!= {'id','title','input','expected','rationale'} for c in cases): raise ValueError('case shape invalid')
    except (OSError,ValueError,TypeError,KeyError) as exc:
        log.update(preflight_error=type(exc).__name__+': '+str(exc),test_status='NOT_TESTED',ended_at=now())
        with open(a.log,'x',encoding='utf-8') as h: json.dump(log,h,ensure_ascii=False,indent=2); h.write('\n')
        print('preflight failed; no checker execution',file=sys.stderr); return 2
    for c in cases:
        entry={'id':c['id'],'title':c['title'],'input':c['input'],'expected':c['expected'],'rationale':c['rationale'],'started_at':now(),'command':['python','-I','check.py'],'timeout_seconds':5,'retry':0}
        try:
            r=subprocess.run([sys.executable,'-I',str(ROOT/'check.py')],input=json.dumps(c['input']),text=True,capture_output=True,timeout=5)
            entry.update(exit_code=r.returncode,stdout=r.stdout,stderr=r.stderr)
            try: actual=json.loads(r.stdout)
            except ValueError: actual=None
            entry['actual']=actual; entry['test_status']='PASS' if r.returncode==0 and not r.stderr and actual==c['expected'] else 'FAIL'
        except subprocess.TimeoutExpired as e:
            entry.update(test_status='UNKNOWN',exit_code=None,stdout=str(e.stdout),stderr=str(e.stderr),error='TIMEOUT')
        entry['ended_at']=now(); log['runs'].append(entry)
    log['ended_at']=now(); log['counts']={s:sum(x['test_status']==s for x in log['runs']) for s in ['PASS','FAIL','UNKNOWN','NOT_TESTED']}
    with open(a.log,'x',encoding='utf-8') as h: json.dump(log,h,ensure_ascii=False,indent=2); h.write('\n')
    print(json.dumps(log['counts'])); return 0 if all(x['test_status']=='PASS' for x in log['runs']) else 1
if __name__=='__main__': sys.exit(main())
