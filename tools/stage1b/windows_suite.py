"""Portable Windows synthetic finite-process suite, new --root only."""
import argparse,datetime,hashlib,json,pathlib,platform,sys
from finite_process import run,unassigned_stop_state

def main(root):
    started_at=datetime.datetime.now(datetime.timezone.utc).isoformat()
    root=pathlib.Path(root);root.mkdir(parents=True,exist_ok=False)
    py=sys.executable
    grandchild='import time;time.sleep(20)'
    child='import subprocess,sys,time;subprocess.Popen([sys.executable,"-B","-c",'+repr(grandchild)+']);time.sleep(20)'
    parent='import subprocess,sys,time;subprocess.Popen([sys.executable,"-B","-c",'+repr(child)+']);time.sleep(20)'
    cases=[
      ('normal',[py,'-B','-c','print("normal")'],2,None,'PASS','JOB_EMPTY'),
      ('nonzero',[py,'-B','-c','import sys;sys.exit(7)'],2,None,'FAIL','JOB_EMPTY'),
      ('missing',[str(root/'missing-git.exe')],2,None,'BLOCKED','NOT_STARTED'),
      ('hang',[py,'-B','-c',grandchild],.3,None,'UNKNOWN','JOB_EMPTY_AFTER_TERMINATE'),
      ('descendants',[py,'-B','-c',parent],.7,None,'UNKNOWN','JOB_EMPTY_AFTER_TERMINATE'),
      ('parent_exit_child',[py,'-B','-c','import subprocess,sys;subprocess.Popen([sys.executable,"-B","-c",'+repr(grandchild)+'])'],.5,None,'UNKNOWN','JOB_EMPTY_AFTER_TERMINATE'),
      ('query_failure',[py,'-B','-c','import time;time.sleep(1)'],.2,'query','UNKNOWN','RUNNING_IN_OWN_JOB'),
      ('terminate_failure',[py,'-B','-c','import time;time.sleep(1)'],.2,'terminate','UNKNOWN','RUNNING_IN_OWN_JOB'),
      ('parent_nonzero_child',[py,'-B','-c','import subprocess,sys;subprocess.Popen([sys.executable,"-B","-c",'+repr(grandchild)+']);sys.exit(7)'],.5,None,'FAIL','JOB_EMPTY_AFTER_TERMINATE')]
    invalid=[('nan',{'command_timeout':float('nan')}),('inf',{'command_timeout':float('inf')}),('negative',{'command_timeout':-1}),('zero',{'total_timeout':0}),('excessive',{'stop_wait':121}),('retry',{'retry':1}),('infinite_retry',{'retry':float('inf')}),('boolean',{'command_timeout':True})]
    oracle={'execution':cases,'bounds':[{'id':n,'kwargs':{k:repr(v) for k,v in kw.items()},'expected':'REJECT_BEFORE_ROOT'} for n,kw in invalid],'wait_return':[[0,'UNASSIGNED_CHILD_STOPPED'],[258,'UNASSIGNED_CHILD_STOP_UNCONFIRMED'],[0xffffffff,'UNASSIGNED_CHILD_STOP_UNCONFIRMED']],'overall':{'command_timeout':20,'total_timeout':.25,'stop_wait':2,'expected':['UNKNOWN','TIMEOUT','JOB_EMPTY_AFTER_TERMINATE']}}
    (root/'oracle.json').write_text(json.dumps(oracle,indent=2))
    results=[]
    for name,cmd,timeout,fault,status,state in cases:
        r=run(cmd,root/name,command_timeout=timeout,total_timeout=3,stop_wait=2,fault=fault)
        results.append({'id':name,'mode':'windows-owned-job','expected':[status,state],'actual':r,'match':r['status']==status and r['process_state']==state})
    for name,kw in invalid:
        try:run([py,'-B','-c','pass'],root/name,**kw);a='ACCEPTED'
        except ValueError as e:a=str(e)
        results.append({'id':name,'mode':'validation','expected':'REJECT_BEFORE_ROOT','actual':a,'match':a in ['INVALID_BOUND','RETRY_NOT_IMPLEMENTED'] and not (root/name).exists()})
    for value,expected in oracle['wait_return']:
        a=unassigned_stop_state(value);results.append({'id':'wait-'+str(value),'mode':'return-value-injection','expected':expected,'actual':a,'match':a==expected})
    r=run([py,'-B','-c',grandchild],root/'overall',command_timeout=20,total_timeout=.25,stop_wait=2)
    results.append({'id':'overall','mode':'windows-owned-job','expected':oracle['overall']['expected'],'actual':r,'match':[r['status'],r['reason'],r['process_state']]==oracle['overall']['expected'] and r['elapsed']<2.5})
    report={'started_at':started_at,'ended_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'python':sys.version,'platform':platform.platform(),'source_sha256':hashlib.sha256(pathlib.Path(__file__).with_name('finite_process.py').read_bytes()).hexdigest(),'oracle_sha256':hashlib.sha256((root/'oracle.json').read_bytes()).hexdigest(),'cases':results,'production_permit':False,'passed':sum(x['match'] for x in results),'total':len(results)}
    (root/'results.json').write_text(json.dumps(report,indent=2));print(json.dumps({'passed':report['passed'],'total':report['total']}))
    return 0 if report['passed']==report['total'] else 1
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',required=True);args=parser.parse_args();sys.exit(main(args.root))
