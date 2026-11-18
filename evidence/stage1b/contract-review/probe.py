import sys,json,copy,pathlib,hashlib,datetime
repo=pathlib.Path(__file__).resolve().parents[1]/'repo'
sys.path.insert(0,str(repo/'tools/stage1b'));import contract
base=json.loads((repo/'tests/stage1b/contract_cases.json').read_text())['cases'][0]['input']
base['contract']['observations']={k:'PASS' for k in base['contract']['observations']}
base['contract']['sessions'].update(separate_session=True,separate_execution=True,separate_area=True,direct_retrieval=True)
cases=[]
def add(i,mut,expect):
 x=copy.deepcopy(base);mut(x);cases.append({'id':i,'input':x,'expected_acceptance':expect})
add('B01-normal',lambda x:None,'PASS')
add('B02-risk-uncovered',lambda x:(x['contract'].update(level=3),x['contract']['risk'].update(destructive=True,strong_authenticity=True)),'NOT_PASS')
add('B03-retention-expired',lambda x:(x['contract'].update(retention_until='2026-01-02T00:00:00+00:00'),x['approval'].update(retention_until='2026-01-02T00:00:00+00:00')),'NOT_PASS')
add('B04-storagefail',lambda x:x['contract']['observations'].update(storage='FAIL'),'FAIL')
add('B05-shafail',lambda x:x['contract']['observations'].update(sha256='FAIL'),'FAIL')
add('B06-unknown-owner',lambda x:x['contract']['sessions'].update(shared_owner=None),'NOT_PASS')
add('B07-strict-same-owner',lambda x:(x['contract'].update(audit_mode='STRICT_INDEPENDENT'),x['contract']['sessions'].update(human_independent=True)),'NOT_PASS')
add('B08-wrongscope',lambda x:x['approval'].update(destinations=['other']),'NOT_PASS')
add('B09-unverified',lambda x:x['approval'].update(authorization_verified=False),'NOT_PASS')
add('B10-zip',lambda x:(x['contract']['object'].update(kind='zip'),x['contract'].update(required_checks=['size','sha256','all_bytes','zip_crc','zip_manifest','zip_paths'])),'NOT_PASS')
# fixed oracle saved before calls
out=pathlib.Path(__file__).parent;(out/'oracle.json').write_text(json.dumps(cases,indent=2))
results=[]
for c in cases:
 x=c['input'];a=contract.validate_contract(x['contract'],x['approval'],x['now'],x['observed_head'],{'version':'0.2.0','commit':'4'*40});e=c['expected_acceptance'];results.append(dict(c,actual=a,verdict='PASS' if (a['ACCEPTANCE_STATUS']!='PASS' if e=='NOT_PASS' else a['ACCEPTANCE_STATUS']==e) else 'FAIL'))
(out/'results.json').write_text(json.dumps({'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checker_sha256':hashlib.sha256((repo/'tools/stage1b/contract.py').read_bytes()).hexdigest(),'cases':results},indent=2))
for r in results:print(r['id'],r['verdict'],r['actual'])
