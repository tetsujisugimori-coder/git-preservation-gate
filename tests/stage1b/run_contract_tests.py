import json,sys,pathlib,hashlib,datetime,platform,subprocess
ROOT=pathlib.Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/stage1b'))
from contract import validate_contract,validate_manifest,validate_receipt,Invalid
p=pathlib.Path(__file__).parent;cases=json.loads((p/'contract_cases.json').read_text())['cases'];results=[]
# The frozen original oracle remains unchanged; new expected outputs are additive.
overrides=json.loads((p/'oracle-v020-p2.json').read_text())['case_overrides']
repatch=json.loads((p/'oracle-repatch-overlay.json').read_text())['case_overrides']
start=datetime.datetime.now(datetime.timezone.utc).isoformat()
for x in cases:
 a=validate_contract(x['input']['contract'],x['input']['approval'],x['input']['now'],x['input']['observed_head'],{'version':'0.2.0','commit':'4'*40});e=dict(x['expected']);e.update(overrides.get(x['id'],{}));previous=dict(e);e.update(repatch.get(x['id'],{}));ok=a['contract_status']==e['contract_status'] and e['reason'] in a['reason_codes'] and all(a[k]==e[k] for k in ['CUSTODY_STATUS','VERIFICATION_STATUS','INDEPENDENCE_STATUS','ACCEPTANCE_STATUS']) and a['production_permit'] is False
 results.append({'id':x['id'],'input_sha256':hashlib.sha256(json.dumps(x['input'],sort_keys=True).encode()).hexdigest(),'historical_expected':x['expected'],'previous_expected':previous,'expected':e,'actual':a,'verdict':'PASS' if ok else 'FAIL'})
out={'scope':'synthetic contract validation, not authorization authentication or storage','started_at':start,'ended_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'environment':{'python':platform.python_version(),'system':platform.system()},'command':'python tests/stage1b/run_contract_tests.py','timeout_seconds':20,'retry':0,'checker_sha256':hashlib.sha256((ROOT/'tools/stage1b/contract.py').read_bytes()).hexdigest(),'oracle_sha256':hashlib.sha256((p/'contract_cases.json').read_bytes()).hexdigest(),'v020_p2_oracle_sha256':hashlib.sha256((p/'oracle-v020-p2.json').read_bytes()).hexdigest(),'repatch_oracle_sha256':hashlib.sha256((p/'oracle-repatch-overlay.json').read_bytes()).hexdigest(),'cases':results,'result':'PASS' if all(x['verdict']=='PASS' for x in results) else 'FAIL'}
print(json.dumps(out,indent=2));sys.exit(0 if out['result']=='PASS' else 1)
