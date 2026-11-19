import argparse,json,pathlib,sys
sys.path.insert(0,str(pathlib.Path(__file__).parent))
from run_suite import a,fixture,bind

def main():
 p=argparse.ArgumentParser();p.add_argument('--root',required=True);x=p.parse_args();root=pathlib.Path(x.root).absolute();root.mkdir(parents=True,exist_ok=False)
 oracle=pathlib.Path(__file__).with_name('boundaries.json').read_bytes();(root/'oracle.fixed.json').write_bytes(oracle);rows=[]
 for c in json.loads(oracle)['cases']:
  d,src,dst,r,ap=fixture(root,c['id']);n=int(c['id'][1:])
  if n==1:
   r['source_root']='relative';ap['source_root']='relative';bind(r,ap);v=a.save(r,ap)
  else:
   result=a.save(r,ap);assert result['status']=='PASS';saved=dst/'trial';receipt=json.loads((saved/'receipt.json').read_bytes());m=json.loads((saved/'manifest.json').read_bytes())
   if n in (2,3):
    if n==2:m['files']=[None]
    else:m['files'][0]['size']=True
    mb=a.encoded(m);(saved/'manifest.json').write_bytes(mb);receipt['manifest_sha256']=a.digest(mb);(saved/'receipt.json').write_bytes(a.encoded(receipt))
   if n==4:(saved/'data'/'extra-empty-dir').mkdir()
   if n==5:(saved/'receipt.json').write_bytes(b'[]')
   v=a.retrieve(saved,src,a.digest((saved/'receipt.json').read_bytes()))
  rows.append(dict(**c,actual=v,test_verdict='PASS' if v['status']==c['expected'] else 'FAIL'))
 report=dict(oracle_sha256=a.digest(oracle),source_sha256=a.digest((pathlib.Path(__file__).parents[2]/'tools/stage1b2/adapter.py').read_bytes()),cases=rows,production_permit=False);(root/'results.json').write_bytes(a.encoded(report));print(json.dumps({'PASS':sum(r['test_verdict']=='PASS' for r in rows),'FAIL':sum(r['test_verdict']=='FAIL' for r in rows)}));return int(any(r['test_verdict']=='FAIL' for r in rows))
if __name__=='__main__':raise SystemExit(main())
