"""Re-run fixed B10 oracle (not a newly independent review)."""
import hashlib,json,pathlib,sys
ROOT=pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/stage1b'))
from contract import validate_contract
oracle=ROOT/'evidence/stage1b/contract-review/oracle.json'
cases=json.loads(oracle.read_text(encoding='utf-8'));results=[]
for item in cases:
    d=item['input'];actual=validate_contract(d['contract'],d['approval'],d['now'],d['observed_head'],{'version':'0.2.0','commit':'4'*40})
    exp=item['expected_acceptance'];ok=(actual['ACCEPTANCE_STATUS']!='PASS' if exp=='NOT_PASS' else actual['ACCEPTANCE_STATUS']==exp)
    ok=ok and actual['production_permit'] is False
    results.append({'id':item['id'],'expected':exp,'actual':actual['ACCEPTANCE_STATUS'],'match':ok})
out={'suite':'independent-10-fixed-oracle-rerun','count':len(results),'passed':sum(x['match'] for x in results),
     'oracle_sha256':hashlib.sha256(oracle.read_bytes()).hexdigest(),'production_permit':False,
     'independent_new_review':False,'cases':results}
print(json.dumps(out,indent=2))
sys.exit(0 if len(results)==10 and all(x['match'] for x in results) else 1)
