import pathlib,sys,json
from finite_process import run
b=pathlib.Path(__file__).parent
results=[]
for i,kw in enumerate([{'command_timeout':float('nan')},{'command_timeout':float('inf')},{'command_timeout':-1},{'total_timeout':0},{'stop_wait':121},{'retry':1},{'retry':float('inf')},{'command_timeout':True}]):
 try:run([sys.executable,'-B','-c','pass'],b/('invalid-'+str(i)),**kw);actual='ACCEPTED'
 except ValueError as e:actual=str(e)
 results.append({'case':i,'kwargs':{k:repr(v) for k,v in kw.items()},'actual':actual,'expected':'REJECT','match':actual in ['INVALID_BOUND','RETRY_NOT_IMPLEMENTED'],'root_created':(b/('invalid-'+str(i))).exists()})
r=run([sys.executable,'-B','-c','import time;time.sleep(20)'],b/'overall-deadline01',command_timeout=20,total_timeout=.25,stop_wait=2)
results.append({'case':'overall-deadline','expected':'TIMEOUT then JOB_EMPTY_AFTER_TERMINATE','actual':r,'match':r['reason']=='TIMEOUT' and r['process_state']=='JOB_EMPTY_AFTER_TERMINATE' and r['elapsed']<2.5})
(b/'bounds-results.json').write_text(json.dumps(results,indent=2));print(sum(x['match'] for x in results),len(results))
