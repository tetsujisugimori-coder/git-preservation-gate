"""Host applicability probe. Elevated-host guard success is NOT 43 user tests.
Never fabricates a normal-user token, modifies elevation, or changes suite oracle.
"""
import argparse,json,os,pathlib,subprocess,sys
sys.path.insert(0,str(pathlib.Path(__file__).parent))
from run_suite import a,fixture,environment_observation

def assess_report(result_file,name):
 try:
  oracle_name={'run_suite':'oracle.json','run_boundaries':'boundaries.json','run_risk_schema':'risk-schema-oracle.json'}[name]
  fixed=json.loads(pathlib.Path(__file__).with_name(oracle_name).read_bytes())['cases']
  report=json.loads(pathlib.Path(result_file).read_bytes())
  if not isinstance(report,dict):raise ValueError()
  cases=report.get('cases')
  if not isinstance(cases,list) or any(not isinstance(x,dict) for x in cases):raise ValueError()
  ids=[x.get('id') for x in cases];wanted=[x['id'] for x in fixed]
  if len(ids)!=len(wanted) or len(set(ids))!=len(ids) or set(ids)!=set(wanted):raise ValueError()
  counts={v:0 for v in ['PASS','FAIL','NOT_TESTED']};byid={x['id']:x for x in fixed}
  for case in cases:
   expected=byid[case['id']]
   if any(case.get(k)!=v for k,v in expected.items()):raise ValueError()
   verdict=case.get('test_verdict');actual=case.get('actual')
   if verdict not in counts or not isinstance(actual,dict):raise ValueError()
   counts[verdict]+=1
   if verdict=='NOT_TESTED':
    if name!='run_suite' or case['id']!='B230' or actual.get('status')!='NOT_TESTED' or actual.get('reason')!='LINK_CREATION_NOT_ALLOWED':raise ValueError()
   elif verdict=='PASS':
    if actual.get('status')!=expected.get('expected',expected.get('expected_status')):raise ValueError()
    if 'expected_reason' in expected and actual.get('reason')!=expected['expected_reason']:raise ValueError()
  return {'case_counts':counts,'case_status':'FAIL' if counts['FAIL'] else ('PARTIAL' if counts['NOT_TESTED'] else 'PASS'),'record_validation':'PASS'}
 except (OSError,ValueError,TypeError,KeyError):
  return {'case_counts':{},'case_status':'FAIL','record_validation':'FAIL'}

def main():
 p=argparse.ArgumentParser();p.add_argument('--root',required=True);args=p.parse_args();root=pathlib.Path(args.root).resolve();root.mkdir(parents=True,exist_ok=False)
 oracle=pathlib.Path(__file__).with_name('ci-probe-oracle.json').read_bytes();(root/'oracle.fixed.json').write_bytes(oracle)
 env=environment_observation();admin=env['windows_admin_token'];out={'environment':env,'oracle_sha256':a.digest(oracle),'adapter_sha256':a.digest((pathlib.Path(__file__).parents[2]/'tools/stage1b2/adapter.py').read_bytes()),'production_permit':False,'started_at':a.timestamp(),'retry':0,'status':'BLOCKED','ordinary_suite':'NOT_TESTED','boundaries':'NOT_TESTED','risk_schema':'NOT_TESTED','guard_tests':0}
 print(json.dumps({'environment':env}),flush=True)
 if os.name!='nt' or type(admin) is not bool:
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
    checked=assess_report(result_file,name);case_counts=checked['case_counts'];case_status=checked['case_status']
    print(proc.stdout.decode('utf-8',errors='replace'),end='',flush=True)
   except subprocess.TimeoutExpired as exc:
    (root/(name+'.stdout')).write_bytes(exc.stdout or b'');(root/(name+'.stderr')).write_bytes(exc.stderr or b'');code=None;status='UNKNOWN'
   rows.append({'suite':name,'fixed_case_count':count,'execution_status':status,'exit_code':code,'started_at':start,'ended_at':a.timestamp(),'timeout_seconds':120,'retry':0,'case_counts':case_counts,'case_status':case_status})
   out[{'run_suite':'ordinary_suite','run_boundaries':'boundaries','run_risk_schema':'risk_schema'}[name]]=case_status
  out['runs']=rows
  eligible=all(x['execution_status']=='PASS' and x['case_status'] in ('PASS','PARTIAL') for x in rows)
  out['status']=('PARTIAL' if any(x['case_status']=='PARTIAL' for x in rows) else 'PASS') if eligible else 'FAIL'
  out['reason']='NORMAL_USER_SUITES';exit_code=0 if eligible else 1
 out['ended_at']=a.timestamp();out['exit_code']=exit_code;(root/'probe.json').write_bytes(a.encoded(out));print(json.dumps(out),flush=True);return exit_code
if __name__=='__main__':raise SystemExit(main())
