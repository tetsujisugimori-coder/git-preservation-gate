"""Finite outer execution record; no retries, no overwrite or cleanup."""
import pathlib,sys,json,subprocess,datetime,platform,hashlib
root=pathlib.Path(__file__).resolve().parents[2];out=pathlib.Path(sys.argv[1]);out.mkdir(exist_ok=False)
jobs=[['tests/stage1b/run_contract_tests.py'],['tests/stage1b/run_record_tests.py',str((out/'ledger').resolve())],['tests/stage1b/run_boundary_tests.py']];records=[]
for index,args in enumerate(jobs):
 start=datetime.datetime.now(datetime.timezone.utc).isoformat();code=None;err='';timed=False
 try:
  r=subprocess.run([sys.executable,*args],cwd=root,capture_output=True,text=True,timeout=20);stdout=r.stdout;err=r.stderr;code=r.returncode
 except subprocess.TimeoutExpired as e:stdout=(e.stdout or b'').decode() if isinstance(e.stdout,bytes) else (e.stdout or '');err=(e.stderr or b'').decode() if isinstance(e.stderr,bytes) else (e.stderr or '');timed=True
 (out/f'{index}.stdout.json').write_text(stdout);(out/f'{index}.stderr.txt').write_text(err)
 records.append({'command':['python',*args[:1]]+(['<new-ledger>'] if len(args)>1 else []),'started_at':start,'ended_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'exit_code':code,'timeout_seconds':20,'timed_out':timed,'retry':0,'stdout':f'{index}.stdout.json','stderr':f'{index}.stderr.txt','result':'PASS' if code==0 else 'FAIL'})
d={'environment':{'python':platform.python_version(),'system':platform.system()},'commands':records,'production_permit':False};(out/'execution.json').write_text(json.dumps(d,indent=2)+'\n');print(json.dumps(d));sys.exit(0 if all(x['result']=='PASS' for x in records) else 1)
