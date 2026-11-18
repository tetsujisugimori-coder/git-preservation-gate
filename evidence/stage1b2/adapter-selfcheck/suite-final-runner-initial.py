"""Frozen-oracle synthetic pilot. Fresh root required, no existing evidence changes.
Injection != real disk-full/ACL/lock. This runner records that distinction.
"""
import argparse,copy,errno,hashlib,json,os,pathlib,shutil,subprocess,sys,time,uuid
from datetime import datetime,timezone,timedelta
from unittest.mock import patch
ROOT=pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/stage1b2'))
import adapter as a

def fixture(root, name, mode='direct'):
    d=root/name;d.mkdir();src=d/'source';dst=d/'store';src.mkdir();dst.mkdir()
    (src/'hello.txt').write_bytes(b'stage1b2 synthetic only\n')
    (src/'data.bin').write_bytes(bytes(range(256)))
    (src/'数式.txt').write_bytes('非機密の合成原物\n'.encode())
    fs=[dict(path=p.name,size=len(p.read_bytes()),sha256=a.digest(p.read_bytes())) for p in sorted(src.iterdir())]
    r=dict(synthetic_only=True,risk=dict(confidential=False,destructive=False,strong_authenticity=False),level=2,object_kind='synthetic-evidence',archive_required=True,attempt_id='trial',object_id='synthetic-three',mode=mode,actor='synthetic-test-actor',source_root=str(src),destination=str(dst),files=fs)
    now=datetime.now(timezone.utc)
    ap=dict(authorization_verified=True,synthetic_only=True,production_permit=False,**{k:r[k] for k in ['object_id','actor','source_root','destination','mode']},request_sha256=a.digest(a.encoded(r)),valid_from=(now-timedelta(days=1)).isoformat(),valid_until=(now+timedelta(days=1)).isoformat(),retention_until=(now+timedelta(days=365)).isoformat(),operations=['create','read'],delete_move_overwrite='prohibited',acl_status='PASS')
    return d,src,dst,r,ap

def bind(r,ap):ap['request_sha256']=a.digest(a.encoded(r))
def frozen_source(src):return {p.name:a.digest(p.read_bytes()) for p in src.iterdir()}
def invoke(d,r,ap):
    rp=d/'request.json';pp=d/'approval.json';rp.write_bytes(a.encoded(r));pp.write_bytes(a.encoded(ap))
    cmd=[sys.executable,str(ROOT/'tools/stage1b2/adapter.py'),'save','--request',str(rp),'--approval',str(pp)]
    p=subprocess.run(cmd,capture_output=True,timeout=40)
    (d/'receiver.stdout').write_bytes(p.stdout);(d/'receiver.stderr').write_bytes(p.stderr)
    return json.loads(p.stdout),p.returncode

def independent_check(saved,src,sha):
    # Distinct verification method (not itself an independent person).
    rb=(saved/'receipt.json').read_bytes();assert a.digest(rb)==sha
    receipt=json.loads(rb);mb=(saved/'manifest.json').read_bytes();assert a.digest(mb)==receipt['manifest_sha256']
    manifest=json.loads(mb);assert len(manifest['files'])==3
    for f in manifest['files']:
        x=(saved/'data'/f['path']).read_bytes();assert x==(src/f['path']).read_bytes();assert len(x)==f['size'] and a.digest(x)==f['sha256']
    return a.retrieve(saved,src,sha)

def run_case(c,root):
    n=int(c['id'][1:])-200;d,src,dst,r,ap=fixture(root,c['id'],'handoff' if n in (2,9) else 'direct');before=frozen_source(src)
    if n==1:
        v=a.save(r,ap);assert v['status']=='PASS';v=independent_check(dst/'trial',src,v['receipt_sha256']);assert frozen_source(src)==before;return v
    if n in (2,3):
        if n==3:r['attempt_id']='unicode';bind(r,ap)
        v,code=invoke(d,r,ap);assert code==0;return independent_check(dst/r['attempt_id'],src,v['receipt_sha256'])
    if n==4:r['destination']=str(d/'absent');ap['destination']=r['destination'];bind(r,ap)
    if n==5:r['destination']=str(d/'elsewhere')
    if n==6:ap['authorization_verified']=False
    if n==7:ap['valid_until']='2000-01-01T00:00:00+00:00'
    if n==8:
        v=a.save(r,ap);assert v['status']=='PASS';files={p.relative_to(dst).as_posix():p.read_bytes() for p in dst.rglob('*') if p.is_file()};v=a.save(r,ap);assert files=={p.relative_to(dst).as_posix():p.read_bytes() for p in dst.rglob('*') if p.is_file()};return v
    if n==9:
        rp=d/'request.json';pp=d/'approval.json';rp.write_bytes(a.encoded(r));pp.write_bytes(a.encoded(ap));cmd=[sys.executable,str(ROOT/'tools/stage1b2/adapter.py'),'save','--request',str(rp),'--approval',str(pp)]
        ps=[subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE) for _ in range(2)];rows=[]
        for i,p in enumerate(ps):
            out,err=p.communicate(timeout=40);(d/f'concurrent{i}.stdout').write_bytes(out);(d/f'concurrent{i}.stderr').write_bytes(err);rows.append(json.loads(out))
        assert sorted(v['status'] for v in rows)==['BLOCKED','PASS'];v=next(v for v in rows if v['status']=='PASS');return independent_check(dst/'trial',src,v['receipt_sha256'])
    if n==10:r['files'][0]['sha256']='0'*64;bind(r,ap)
    if n==11:
        def hook(phase,path):
            if phase=='after_copy':(path/'hello.txt').write_bytes(b'changed synthetic fault')
        return a.save(r,ap,_fault=hook)
    if n in (12,13,14,16):
        def hook(phase,path):
            if phase=='before_write':
                if n==12:path.write_bytes(b'partial synthetic fault')
                raise OSError(errno.ENOSPC if n==13 else errno.EACCES,'injected synthetic error')
        v=a.save(r,ap,_fault=hook);assert not (dst/'trial'/'receipt.json').exists();return v
    if n==15:
        with patch.object(a,'regular_bytes',side_effect=PermissionError('injected read denied')):return a.save(r,ap)
    if n in (17,18,19,20,21,31):
        v=a.save(r,ap);assert v['status']=='PASS';target=d/'fault-copy';shutil.copytree(dst/'trial',target)
        if n==17:(target/'receipt.json').unlink()
        if n==18:(target/'receipt.json').write_bytes(b'{}')
        if n==19:(target/'manifest.json').write_bytes(b'{}')
        if n==20:(target/'data'/'hello.txt').write_bytes(b'changed fault')
        if n==21:(target/'data'/'hello.txt').unlink()
        if n==31:(target/'data'/'unexpected').write_bytes(b'new fault')
        return a.retrieve(target,src,v['receipt_sha256'])
    if n==22:return a.retrieve(d/'missing-store',src,'0'*64)
    if n==23:
        try:subprocess.run([str(d/'missing-receiver-executable')],capture_output=True,timeout=1)
        except FileNotFoundError:return a.result('BLOCKED','RECEIVER_UNAVAILABLE')
        raise AssertionError('unexpected receiver')
    if n==24:r['actor']='other-actor';bind(r,ap)
    if n==25:r['files'][0]['path']='../escape';bind(r,ap)
    if n==26:r['level']=1;r['object_kind']='git-document';r['archive_required']=False;ap={}
    if n==27:r['archive_required']=False;bind(r,ap)
    if n==28:r['level']=3;bind(r,ap)
    if n==29:
        with patch.object(a.time,'monotonic',side_effect=[0,999,999]):return a.save(r,ap,timeout=1)
    if n==30:
        link=src/'linked.txt'
        try:link.symlink_to(src/'hello.txt')
        except OSError:return a.result('NOT_TESTED','LINK_CREATION_NOT_ALLOWED')
        r['files'][0]['path']='linked.txt';bind(r,ap)
    if n==32:r['files'].append(dict(r['files'][0]));bind(r,ap)
    if n==33:r['attempt_id']='substituted'
    if n==34:r['level']=1;bind(r,ap)
    return a.save(r,ap)

def main():
    p=argparse.ArgumentParser();p.add_argument('--root',required=True);args=p.parse_args();root=pathlib.Path(args.root).absolute();root.mkdir(parents=True,exist_ok=False)
    oracle=(pathlib.Path(__file__).with_name('oracle.json')).read_bytes();(root/'oracle.fixed.json').write_bytes(oracle)
    start=a.timestamp();rows=[]
    for c in json.loads(oracle)['cases']:
        t=time.monotonic()
        try:
            r=run_case(c,root);verdict='PASS' if r['status']==c['expected'] else ('NOT_TESTED' if r['status']=='NOT_TESTED' else 'FAIL')
        except Exception as e:r=dict(status='ERROR',reason=type(e).__name__);verdict='FAIL'
        row={**c,'actual':r,'test_verdict':verdict,'elapsed':time.monotonic()-t};rows.append(row);(root/(c['id']+'.json')).write_bytes(a.encoded(row))
    report=dict(schema='stage1b2-suite-1',started_at=start,ended_at=a.timestamp(),python=sys.version,platform=sys.platform,oracle_sha256=a.digest(oracle),source_sha256=a.digest((ROOT/'tools/stage1b2/adapter.py').read_bytes()),runner_sha256=a.digest(pathlib.Path(__file__).read_bytes()),production_permit=False,retry=0,receiver_timeout_seconds=40,cases=rows,counts={k:sum(x['test_verdict']==k for x in rows) for k in ['PASS','FAIL','NOT_TESTED']})
    (root/'results.json').write_bytes(a.encoded(report));print(json.dumps(report['counts']));return 1 if report['counts']['FAIL'] else 0
if __name__=='__main__':raise SystemExit(main())
