import pathlib,sys,json,hashlib,shutil
base=pathlib.Path(r'${WINDOWS_TASK_ROOT}')
sys.path.insert(0,str(base/'submitted/tools/stage1a'))
from synthetic_bundle_gate import Runner,restore
root=base/'readback-self03';root.mkdir(exist_ok=False)
source=base/'bundle-run01/archive'
for n in ['original.bundle','manifest.json']:shutil.copyfile(source/n,root/n)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=Runner(root);result=restore(r,root/'original.bundle',root/'manifest.json',sha(source/'manifest.json'),root/'restored.git')
record={'kind':'same-actor-direct-storage-retrieval-not-independent','match':all((source/n).read_bytes()==(root/n).read_bytes() for n in ['original.bundle','manifest.json']),'sha256':sha(root/'original.bundle'),'size':(root/'original.bundle').stat().st_size,'restore':result,'commands':r.log,'production_permit':False}
(root/'result.json').write_text(json.dumps(record,indent=2));print(json.dumps({'match':record['match'],'sha256':record['sha256'],'size':record['size']}))
