import pathlib,sys,json,hashlib,datetime,copy
ROOT=pathlib.Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/stage1b'))
from contract import validate_manifest,validate_receipt,claim_attempt,Invalid
p=pathlib.Path(__file__).parent;ledger=pathlib.Path(sys.argv[1]);ledger.mkdir(exist_ok=False)
c=json.loads((p/'contract_cases.json').read_text())['cases'][0]['input']['contract'];m={'schema_version':'1','files':[{'path':'sample.bundle','size':200,'sha256':'a'*64}]};r={'schema_version':'1','attempt_id':c['attempt_id'],'object_id':c['object']['id'],'sha256':'a'*64,'size':200,'destination':c['destination'],'stored_at':'2026-11-18T00:00:00+00:00','operation':'create','storage_status':'PASS','readback_status':'PASS'}
results=[];start=datetime.datetime.now(datetime.timezone.utc).isoformat()
for id,scenario,expected in json.loads((p/'record_oracle.json').read_text())['cases']:
 x=copy.deepcopy(m if 'manifest' in scenario else r);err=None
 if scenario=='empty_manifest':x['files']=[]
 if scenario=='duplicate_manifest':x['files']*=2
 if scenario=='traversal_manifest':x['files'][0]['path']='../bad'
 if scenario=='absolute_manifest':x['files'][0]['path']='/bad'
 if scenario=='bad_hash_manifest':x['files'][0]['sha256']='bad'
 if scenario=='wrong_attempt_receipt':x['attempt_id']='other'
 if scenario=='wrong_sha_receipt':x['sha256']='b'*64
 if scenario=='wrong_size_receipt':x['size']=201
 if scenario=='custody_only_receipt':x['readback_status']='NOT_TESTED'
 if scenario=='failed_receipt':x.update(storage_status='FAIL',readback_status='NOT_TESTED')
 if scenario=='unknown_receipt_field':x['unexpected']=True
 try:
  if scenario.endswith('attempt'):x={'attempt_id':'../bad' if scenario=='unsafe_attempt' else 'new'};claim_attempt(ledger,x['attempt_id'])
  elif 'manifest' in scenario:validate_manifest(x)
  else:validate_receipt(x,c)
  actual=True
 except (Invalid,ValueError) as e:actual=False;err=str(e)
 results.append({'id':id,'scenario':scenario,'input':x,'input_sha256':hashlib.sha256(json.dumps(x,sort_keys=True).encode()).hexdigest(),'expected_accept':expected,'actual_accept':actual,'error':err,'verdict':'PASS' if actual==expected else 'FAIL'})
out={'started_at':start,'ended_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checker_sha256':hashlib.sha256((ROOT/'tools/stage1b/contract.py').read_bytes()).hexdigest(),'oracle_sha256':hashlib.sha256((p/'record_oracle.json').read_bytes()).hexdigest(),'cases':results,'result':'PASS' if all(x['verdict']=='PASS' for x in results) else 'FAIL','production_permit':False};print(json.dumps(out,indent=2));sys.exit(0 if out['result']=='PASS' else 1)
