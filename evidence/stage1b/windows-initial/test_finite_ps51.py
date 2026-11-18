import pathlib,sys,json,hashlib,time
from finite_process import run
source=pathlib.Path(__file__).parent
root=source/'v3-ps51';root.mkdir(exist_ok=False)
py=sys.executable
cases=[
 ('normal',[py,'-B','-c','print("normal")'],2,None,'PASS','JOB_EMPTY'),
 ('nonzero',[py,'-B','-c','import sys;print("bad");sys.exit(7)'],2,None,'FAIL','JOB_EMPTY'),
 ('missing',[str(root/'absent-git.exe')],2,None,'BLOCKED','NOT_STARTED'),
 ('hang',[py,'-B','-c','import time;print("hang",flush=True);time.sleep(20)'],.3,None,'UNKNOWN','JOB_EMPTY_AFTER_TERMINATE'),
 ('descendants',[py,'-B','-c','import subprocess,sys,time;subprocess.Popen([sys.executable,"-B","-c","import subprocess,sys,time;subprocess.Popen([sys.executable,\"-B\",\"-c\",\"import time;time.sleep(20)\"]);time.sleep(20)"]);time.sleep(20)'],.7,None,'UNKNOWN','JOB_EMPTY_AFTER_TERMINATE'),
 ('parent_exit_child',[py,'-B','-c','import subprocess,sys;subprocess.Popen([sys.executable,"-B","-c","import time;time.sleep(20)"])'],.5,None,'UNKNOWN','JOB_EMPTY_AFTER_TERMINATE'),
 ('query_failure',[py,'-B','-c','import time;time.sleep(1)'],.2,'query','UNKNOWN','RUNNING_IN_OWN_JOB'),
 ('terminate_failure',[py,'-B','-c','import time;time.sleep(1)'],.2,'terminate','UNKNOWN','RUNNING_IN_OWN_JOB')]
(root/'finite-oracle.json').write_text(json.dumps(cases,indent=2))
grandchild='import time;time.sleep(20)'
child='import subprocess,sys,time;subprocess.Popen([sys.executable,"-B","-c",'+repr(grandchild)+']);time.sleep(20)'
parent='import subprocess,sys,time;subprocess.Popen([sys.executable,"-B","-c",'+repr(child)+']);time.sleep(20)'
cases[4]=('descendants',[py,'-B','-c',parent],.7,None,'UNKNOWN','JOB_EMPTY_AFTER_TERMINATE')
(root/'finite-oracle-corrected.json').write_text(json.dumps(cases,indent=2))
results=[]
for name,cmd,timeout,fault,status,state in cases:
 r=run(cmd,root/('test-'+name),command_timeout=timeout,total_timeout=3,stop_wait=2,fault=fault)
 results.append({'id':name,'expected_status':status,'expected_state':state,'actual':r,'match':r['status']==status and r['process_state']==state})
(root/'finite-results.json').write_text(json.dumps({'checker_sha256':hashlib.sha256((source/'finite_process.py').read_bytes()).hexdigest(),'cases':results},indent=2))
print(json.dumps({'passed':sum(x['match'] for x in results),'total':len(results),'descendant_peak':max(x['active'] for x in results[4]['actual']['observations'])}))
assert all(x['match'] for x in results)
