import pathlib,sys,json,copy,hashlib,datetime
ROOT=pathlib.Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/stage1b'));from contract import validate_contract
p=pathlib.Path(__file__).parent;base=json.loads((p/'contract_cases.json').read_text())['cases'][0]['input'];results=[]
for case in json.loads((p/'contract_boundary_oracle.json').read_text())['cases']:
 x=copy.deepcopy(base);c=x['contract'];c['observations']={k:'PASS' for k in c['observations']};c['sessions'].update(separate_session=True,separate_execution=True,separate_area=True,direct_retrieval=True);policy={'version':'0.2.0','commit':'4'*40};s=case['scenario']
 if s.startswith('zip'):
  c['object']['kind']='zip';c['required_checks']=['size','sha256','all_bytes','zip_crc','zip_manifest','zip_paths']
 if s=='unknown_required_check':c['required_checks'].append('unknown_adapter')
 if s=='policy_unconfirmed':policy=None
 if s=='policy_mismatch':policy={'version':'0.1.0','commit':'5'*40}
 if s=='zip_known_hash_fail':c['observations']['sha256']='FAIL'
 actual=validate_contract(c,x['approval'],x['now'],x['observed_head'],policy);ok=all(actual[k]==case[e] for k,e in [('contract_status','expected_contract'),('VERIFICATION_STATUS','expected_verification'),('ACCEPTANCE_STATUS','expected_acceptance')]);results.append({'id':case['id'],'input':x,'effective_policy':policy,'expected':case,'actual':actual,'verdict':'PASS' if ok else 'FAIL'})
out={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checker_sha256':hashlib.sha256((ROOT/'tools/stage1b/contract.py').read_bytes()).hexdigest(),'oracle_sha256':hashlib.sha256((p/'contract_boundary_oracle.json').read_bytes()).hexdigest(),'cases':results,'result':'PASS' if all(x['verdict']=='PASS' for x in results) else 'FAIL'};print(json.dumps(out,indent=2));sys.exit(0 if out['result']=='PASS' else 1)
