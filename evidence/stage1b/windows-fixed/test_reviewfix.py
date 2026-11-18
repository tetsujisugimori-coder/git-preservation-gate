import pathlib,sys,json,hashlib
from finite_process_v2 import run,unassigned_stop_state
b=pathlib.Path(__file__).parent
oracle={'wait_cases':[[0,'UNASSIGNED_CHILD_STOPPED'],[258,'UNASSIGNED_CHILD_STOP_UNCONFIRMED'],[0xffffffff,'UNASSIGNED_CHILD_STOP_UNCONFIRMED']],'parent_nonzero_child':['FAIL','COMMAND_NONZERO_WITH_TIMEOUT','JOB_EMPTY_AFTER_TERMINATE']}
(b/'reviewfix-oracle.json').write_text(json.dumps(oracle,indent=2))
waits=[{'input':x,'expected':e,'actual':unassigned_stop_state(x),'match':unassigned_stop_state(x)==e,'mode':'return-value-contract-injection'} for x,e in oracle['wait_cases']]
cmd=[sys.executable,'-B','-c','import subprocess,sys;subprocess.Popen([sys.executable,"-B","-c","import time;time.sleep(20)"]);sys.exit(7)']
r=run(cmd,b/'parent-nonzero-child01',command_timeout=.4,total_timeout=2,stop_wait=2)
actual=[r['status'],r['reason'],r['process_state']]
res={'source_sha256':hashlib.sha256((b/'finite_process_v2.py').read_bytes()).hexdigest(),'waits':waits,'parent_case':r,'expected':oracle['parent_nonzero_child'],'match':actual==oracle['parent_nonzero_child']}
(b/'reviewfix-results.json').write_text(json.dumps(res,indent=2));print(json.dumps({'wait_pass':sum(x['match'] for x in waits),'parent_pass':res['match'],'parent_exit':r.get('observed_parent_exit')}))
