"""Re-execute unchanged reviewer inputs; outputs are synthetic, not permission."""
import datetime, hashlib, json, pathlib, sys
ROOT=pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/stage1b'))
if '--contract-source' in sys.argv:
 import importlib.util
 spec=importlib.util.spec_from_file_location('baseline_contract',sys.argv[sys.argv.index('--contract-source')+1]);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);validate_contract=module.validate_contract
else:
 from contract import validate_contract
cases=json.loads((ROOT/'tests/stage1b/review12-fixed.json').read_text())+[json.loads((ROOT/'tests/stage1b/review-new13-fixed.json').read_text())]
if '--additional' in sys.argv:cases=json.loads((ROOT/'tests/stage1b/repatch-boundaries-fixed.json').read_text())
rows=[]
for z in cases:
 x=z['input'];before=json.dumps(x,sort_keys=True)
 a=validate_contract(x['contract'],x['approval'],x['now'],x['observed_head'],{'version':'0.2.0','commit':'4'*40})
 rows.append({'id':z['id'],'input_sha256':hashlib.sha256(before.encode()).hexdigest(),'expected':z['expected'],'actual':a,'match':all(a.get(k)==v for k,v in z['expected'].items()) and before==json.dumps(x,sort_keys=True) and a['production_permit'] is False})
print(json.dumps({'cases':rows,'total':len(rows),'matched':sum(r['match'] for r in rows),'production_permit':False},indent=2))
sys.exit(0 if all(r['match'] for r in rows) else 1)
