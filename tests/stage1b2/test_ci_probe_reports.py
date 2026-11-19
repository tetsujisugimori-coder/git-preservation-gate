import argparse,copy,json,pathlib,sys
sys.path.insert(0,str(pathlib.Path(__file__).parent))
import ci_probe as c

def main():
 p=argparse.ArgumentParser();p.add_argument('--root',required=True);args=p.parse_args();root=pathlib.Path(args.root).resolve();root.mkdir(parents=True,exist_ok=False)
 oracle=pathlib.Path(__file__).with_name('ci-probe-report-oracle.json').read_bytes();(root/'oracle.fixed.json').write_bytes(oracle)
 fixed=json.loads(pathlib.Path(__file__).with_name('oracle.json').read_bytes())['cases'];normal={'cases':[{**x,'actual':{'status':x['expected'],'reason':'synthetic-report-fixture'},'test_verdict':'PASS'} for x in fixed]};rows=[]
 for test in json.loads(oracle)['cases']:
  r=copy.deepcopy(normal);cs=r['cases'];mutation=test['mutation'];dest=root/(test['id']+'.json')
  if mutation=='short':cs.pop()
  if mutation=='duplicate':cs[-1]=cs[0]
  if mutation=='extra':cs.append(copy.deepcopy(cs[0]))
  if mutation=='wrong-id':cs[0]['id']='WRONG'
  if mutation=='unknown-verdict':cs[0]['test_verdict']='UNKNOWN'
  if mutation=='link-not-tested':cs[29]['test_verdict']='NOT_TESTED';cs[29]['actual']={'status':'NOT_TESTED','reason':'LINK_CREATION_NOT_ALLOWED'}
  if mutation=='other-not-tested':cs[0]['test_verdict']='NOT_TESTED';cs[0]['actual']={'status':'NOT_TESTED','reason':'LINK_CREATION_NOT_ALLOWED'}
  if mutation=='wrong-actual':cs[0]['actual']['status']='FAIL'
  if mutation!='missing':dest.write_bytes(b'bad-json' if mutation=='malformed' else c.a.encoded(r))
  actual=c.assess_report(dest,'run_suite');rows.append({**test,'actual':actual,'test_verdict':'PASS' if actual['case_status']==test['expected'] else 'FAIL'})
 result={'oracle_sha256':c.a.digest(oracle),'probe_sha256':c.a.digest(pathlib.Path(c.__file__).read_bytes()),'cases':rows,'production_permit':False};(root/'results.json').write_bytes(c.a.encoded(result));print(json.dumps({'PASS':sum(x['test_verdict']=='PASS' for x in rows),'FAIL':sum(x['test_verdict']=='FAIL' for x in rows)}));return int(any(x['test_verdict']=='FAIL' for x in rows))
if __name__=='__main__':raise SystemExit(main())
