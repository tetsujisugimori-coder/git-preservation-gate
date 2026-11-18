"""Replay fixed report mutations through actual old/new probe main.
Subprocess return data are synthetic; never Windows execution evidence.
"""
import argparse,contextlib,copy,importlib.util,io,json,pathlib,sys,types
from unittest.mock import patch
sys.path.insert(0,str(pathlib.Path(__file__).parent))
from run_suite import a
def main():
 p=argparse.ArgumentParser();p.add_argument('--root',required=True);p.add_argument('--probe',required=True);args=p.parse_args();root=pathlib.Path(args.root).resolve();root.mkdir(parents=True,exist_ok=False)
 source=pathlib.Path(args.probe).resolve();fixed_root=pathlib.Path(__file__).parent
 oracle=(fixed_root/'ci-probe-report-oracle.json').read_bytes();rows=[]
 for test in json.loads(oracle)['cases']:
  spec=importlib.util.spec_from_file_location('probe_subject',source);subject=importlib.util.module_from_spec(spec);spec.loader.exec_module(subject)
  # Source remains identified separately; logical oracle directory is fixed.
  subject.__file__=str(fixed_root/'ci_probe.py')
  def fake_run(cmd,**kw):
   name=pathlib.Path(cmd[1]).stem;target=pathlib.Path(cmd[3]);target.mkdir(parents=True,exist_ok=False)
   filename={'run_suite':'oracle.json','run_boundaries':'boundaries.json','run_risk_schema':'risk-schema-oracle.json'}[name]
   fixed=json.loads((fixed_root/filename).read_bytes())['cases']
   cases=[{**x,'actual':{'status':x.get('expected',x.get('expected_status')),'reason':x.get('expected_reason','synthetic-report-fixture')},'test_verdict':'PASS'} for x in fixed]
   mutation=test['mutation'] if name=='run_suite' else 'normal'
   if mutation=='short':cases.pop()
   if mutation=='duplicate':cases[-1]=cases[0]
   if mutation=='extra':cases.append(copy.deepcopy(cases[0]))
   if mutation=='wrong-id':cases[0]['id']='WRONG'
   if mutation=='unknown-verdict':cases[0]['test_verdict']='UNKNOWN'
   if mutation=='link-not-tested':cases[29]['test_verdict']='NOT_TESTED';cases[29]['actual']={'status':'NOT_TESTED','reason':'LINK_CREATION_NOT_ALLOWED'}
   if mutation=='other-not-tested':cases[0]['test_verdict']='NOT_TESTED';cases[0]['actual']={'status':'NOT_TESTED','reason':'LINK_CREATION_NOT_ALLOWED'}
   if mutation=='wrong-actual':cases[0]['actual']['status']='FAIL'
   if mutation!='missing':(target/'results.json').write_bytes(b'bad-json' if mutation=='malformed' else a.encoded({'cases':cases}))
   return types.SimpleNamespace(returncode=0,stdout=b'',stderr=b'')
  out=io.StringIO();target=root/test['id']
  with patch.object(subject,'os',types.SimpleNamespace(name='nt')),patch.object(subject,'environment_observation',return_value={'platform':'synthetic-Windows-token','python':'synthetic','windows_admin_token':False}),patch.object(subject.subprocess,'run',side_effect=fake_run),patch.object(sys,'argv',['probe','--root',str(target)]),contextlib.redirect_stdout(out):
   try:exit_code=subject.main();result=json.loads((target/'probe.json').read_bytes());status=result['status']
   except Exception as exc:exit_code=None;status='UNCAUGHT_EXCEPTION';result={'reason':type(exc).__name__}
  (root/(test['id']+'.stdout')).write_text(out.getvalue())
  expected_exit=0 if test['expected'] in ('PASS','PARTIAL') else 1
  rows.append({**test,'actual_status':status,'exit_code':exit_code,'test_verdict':'PASS' if status==test['expected'] and exit_code==expected_exit else 'FAIL'})
 result={'source_sha256':a.digest(source.read_bytes()),'oracle_sha256':a.digest(oracle),'synthetic_subprocess_only':True,'cases':rows,'production_permit':False};(root/'results.json').write_bytes(a.encoded(result));print(json.dumps({'PASS':sum(x['test_verdict']=='PASS' for x in rows),'FAIL':sum(x['test_verdict']=='FAIL' for x in rows)}));return int(any(x['test_verdict']=='FAIL' for x in rows))
if __name__=='__main__':raise SystemExit(main())
