"""Host applicability probe. Elevated-host guard success is NOT 43 user tests.
Never fabricates a normal-user token, modifies elevation, or changes suite oracle.
"""
import argparse,json,os,pathlib,subprocess,sys
sys.path.insert(0,str(pathlib.Path(__file__).parent))
from run_suite import a,fixture,environment_observation

def main():
 p=argparse.ArgumentParser();p.add_argument('--root',required=True);args=p.parse_args();root=pathlib.Path(args.root).resolve();root.mkdir(parents=True,exist_ok=False)
 oracle=pathlib.Path(__file__).with_name('ci-probe-oracle.json').read_bytes();(root/'oracle.fixed.json').write_bytes(oracle)
 env=environment_observation();admin=env['windows_admin_token'];out={'environment':env,'oracle_sha256':a.digest(oracle),'adapter_sha256':a.digest((pathlib.Path(__file__).parents[2]/'tools/stage1b2/adapter.py').read_bytes()),'production_permit':False,'started_at':a.timestamp(),'retry':0,'status':'BLOCKED','ordinary_suite':'NOT_TESTED','boundaries':'NOT_TESTED','risk_schema':'NOT_TESTED','guard_tests':0}
 print(json.dumps({'environment':env}),flush=True)
 if os.name!='nt' or admin not in (True,False):
  out['reason']='WINDOWS_TOKEN_NOT_CONFIRMED';exit_code=1
 elif admin:
  _,src,dst,request,approval=fixture(root,'admin-guard')
  before={x.relative_to(src).as_posix():a.digest(x.read_bytes()) for x in src.rglob('*') if x.is_file()}
  actual=a.save(request,approval)
  after={x.relative_to(src).as_posix():a.digest(x.read_bytes()) for x in src.rglob('*') if x.is_file()}
  matched=actual.get('status')=='BLOCKED' and actual.get('reason')=='ELEVATED_WINDOWS_TOKEN' and not list(dst.iterdir()) and before==after
  out.update(status='PASS' if matched else 'FAIL',reason='ADMIN_REJECTION_ONLY',guard_tests=1,guard_actual=actual,destination_entries=len(list(dst.iterdir())),source_unchanged=before==after)
  exit_code=0 if matched else 1
 else:
  rows=[]
  for name,count in [('run_suite',34),('run_boundaries',5),('run_risk_schema',4)]:
   cmd=[sys.executable,str(pathlib.Path(__file__).with_name(name+'.py')),'--root',str(root/name)]
   start=a.timestamp();case_counts={};case_status='NOT_TESTED'
   try:
    proc=subprocess.run(cmd,capture_output=True,timeout=120);(root/(name+'.stdout')).write_bytes(proc.stdout);(root/(name+'.stderr')).write_bytes(proc.stderr)
    code=proc.returncode;status='PASS' if code==0 else 'FAIL'
    result_file=root/name/'results.json'
    if result_file.exists():
     rows_of_cases=json.loads(result_file.read_bytes()).get('cases',[])
     case_counts={v:sum(x.get('test_verdict')==v for x in rows_of_cases) for v in ['PASS','FAIL','NOT_TESTED']}
     case_status='FAIL' if case_counts['FAIL'] else ('PARTIAL' if case_counts['NOT_TESTED'] else ('PASS' if len(rows_of_cases)==count else 'UNKNOWN'))
    print(proc.stdout.decode('utf-8',errors='replace'),end='',flush=True)
   except subprocess.TimeoutExpired as exc:
    (root/(name+'.stdout')).write_bytes(exc.stdout or b'');(root/(name+'.stderr')).write_bytes(exc.stderr or b'');code=None;status='UNKNOWN'
   rows.append({'suite':name,'fixed_case_count':count,'execution_status':status,'exit_code':code,'started_at':start,'ended_at':a.timestamp(),'timeout_seconds':120,'retry':0,'case_counts':case_counts,'case_status':case_status})
   out[{'run_suite':'ordinary_suite','run_boundaries':'boundaries','run_risk_schema':'risk_schema'}[name]]=case_status
  out['runs']=rows;out['status']='PASS' if all(x['execution_status']=='PASS' for x in rows) else 'FAIL';out['reason']='NORMAL_USER_SUITES';exit_code=0 if out['status']=='PASS' else 1
 out['ended_at']=a.timestamp();out['exit_code']=exit_code;(root/'probe.json').write_bytes(a.encoded(out));print(json.dumps(out),flush=True);return exit_code
if __name__=='__main__':raise SystemExit(main())
