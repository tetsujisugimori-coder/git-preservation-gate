import argparse,importlib.util,json,pathlib,sys
sys.path.insert(0,str(pathlib.Path(__file__).parent))
from run_suite import fixture,bind

def main():
 p=argparse.ArgumentParser();p.add_argument('--root',required=True);p.add_argument('--adapter');args=p.parse_args();root=pathlib.Path(args.root).resolve();root.mkdir(parents=True,exist_ok=False)
 source=pathlib.Path(args.adapter) if args.adapter else pathlib.Path(__file__).parents[2]/'tools/stage1b2/adapter.py'
 spec=importlib.util.spec_from_file_location('risk_subject',source);a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
 oracle=pathlib.Path(__file__).with_name('risk-schema-oracle.json').read_bytes();(root/'oracle.fixed.json').write_bytes(oracle);rows=[]
 for c in json.loads(oracle)['cases']:
  d,src,dst,r,ap=fixture(root,c['id']);r['risk']=c['risk'];bind(r,ap)
  try:v=a.save(r,ap)
  except Exception as e:v={'status':'UNCAUGHT_EXCEPTION','reason':type(e).__name__}
  good=v['status']==c['expected_status'] and v['reason']==c['expected_reason'] and not list(dst.iterdir())
  rows.append({**c,'actual':v,'destination_unmodified':not list(dst.iterdir()),'test_verdict':'PASS' if good else 'FAIL'})
 result={'oracle_sha256':a.digest(oracle),'adapter_sha256':a.digest(source.read_bytes()),'cases':rows,'production_permit':False};(root/'results.json').write_bytes(a.encoded(result));print(json.dumps({'PASS':sum(r['test_verdict']=='PASS' for r in rows),'FAIL':sum(r['test_verdict']=='FAIL' for r in rows)}));return int(any(r['test_verdict']=='FAIL' for r in rows))
if __name__=='__main__':raise SystemExit(main())
