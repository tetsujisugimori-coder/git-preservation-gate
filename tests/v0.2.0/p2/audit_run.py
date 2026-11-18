import sys,json,pathlib,subprocess,hashlib,datetime,platform
checker=pathlib.Path(sys.argv[1]);cases=pathlib.Path(sys.argv[2]);out=pathlib.Path(sys.argv[3]); rows=[]
for c in json.loads(cases.read_text()):
 data=json.dumps(c['input'],sort_keys=True).encode();start=datetime.datetime.now(datetime.timezone.utc).isoformat()
 try:
  r=subprocess.run([sys.executable,str(checker)],input=data,capture_output=True,timeout=5); code=r.returncode;stdout=r.stdout.decode();stderr=r.stderr.decode(); timed=False
 except subprocess.TimeoutExpired as e: code=None;stdout=(e.stdout or b'').decode();stderr=(e.stderr or b'').decode();timed=True
 try:actual=json.loads(stdout)
 except:actual=None
 rows.append(dict(id=c['id'],input_sha256=hashlib.sha256(data).hexdigest(),expected=c['expected'],actual=actual,match=actual==c['expected'] and code==0,start=start,end=datetime.datetime.now(datetime.timezone.utc).isoformat(),exit_code=code,stdout=stdout,stderr=stderr,timeout_seconds=5,timed_out=timed,retry=0))
result=dict(checker_sha256=hashlib.sha256(checker.read_bytes()).hexdigest(),oracle_sha256=hashlib.sha256(cases.read_bytes()).hexdigest(),python=platform.python_version(),platform=platform.platform(),command='python check.py < canonical case input',count=len(rows),passed=sum(r['match'] for r in rows),rows=rows)
with out.open('x') as f:json.dump(result,f,indent=2)
print(result['passed'],result['count']);print([r['id'] for r in rows if not r['match']])
