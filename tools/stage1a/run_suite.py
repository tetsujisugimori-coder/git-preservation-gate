#!/usr/bin/env python3
"""Bounded local synthetic test suite; expected outcomes are separate JSON, never auto-updated."""
import argparse
import copy
import json
from pathlib import Path
import platform
import sys
import time
import synthetic_bundle_gate as g


def expected(status='PASS', reason='OK'):
    return dict(status=status, reason=reason)


def scenario(name, r, area, pristine):
    source, bundle, manifest, target = pristine
    manifest_sha = g.sha256(manifest)
    if name in ('normal', 'normal_repeat'):
        store, back = area/'store', area/'back'
        store.mkdir(); back.mkdir()
        for src, fn in ((bundle,'data.bundle'), (manifest,'manifest.json')):
            g.copy_new(src, store/fn, 'STORAGE_UNAVAILABLE')
            g.copy_new(store/fn, back/fn, 'RETRIEVAL_UNAVAILABLE')
            if not g.same_bytes(src, back/fn):
                raise g.Rejected('READBACK_BYTES')
        actual = g.restore(r, back/'data.bundle', back/'manifest.json', manifest_sha, area/'restored.git')
        if actual != target:
            raise g.Rejected('SOURCE_TARGET_CHANGED')
        g.save(area/'verified-inventory.json', actual)
    elif name in ('missing_bundle','empty_bundle','truncated_bundle','modified_byte'):
        bad = area/'fault.bundle'
        if name != 'missing_bundle':
            data = bundle.read_bytes()
            data = b'' if name == 'empty_bundle' else data[:len(data)//2] if name == 'truncated_bundle' else data[:-1]+bytes([data[-1]^1])
            bad.write_bytes(data)
        g.restore(r, bad, manifest, manifest_sha, area/'restore.git')
    elif name in ('wrong_sha','missing_manifest','invalid_manifest','replaced_manifest','schema_manifest'):
        bad = area/'fault-manifest.json'
        m = json.loads(manifest.read_text())
        if name == 'invalid_manifest':
            bad.write_text('{')
        elif name == 'schema_manifest':
            g.save(bad, {})
            manifest_sha = g.sha256(bad)
        elif name != 'missing_manifest':
            m['bundle_sha256'] = '0'*64
            g.save(bad, m)
            if name == 'wrong_sha':
                manifest_sha = g.sha256(bad) # deliberately trusted wrong SHA; bundle still fails
        g.restore(r, bundle, bad, manifest_sha, area/'restore.git')
    elif name == 'prerequisite_bundle':
        bad = area/'incremental.bundle'
        r.git('-C', source, 'bundle', 'create', bad, 'main~1..main')
        m = json.loads(manifest.read_text())
        m.update(bundle_size=bad.stat().st_size, bundle_sha256=g.sha256(bad))
        mp=area/'incremental.json'; g.save(mp,m)
        g.restore(r,bad,mp,g.sha256(mp),area/'restore.git')
    elif name in ('shallow_source','partial_source','alternates_source','dirty_source','untracked_source'):
        clone = area/'source-copy'
        r.git('clone','--no-local',source,clone)
        if name == 'shallow_source':
            (clone/'.git/shallow').write_text(r.git('-C',clone,'rev-parse','HEAD')+'\n')
        elif name == 'partial_source':
            r.git('-C',clone,'config','remote.origin.promisor','true')
        elif name == 'alternates_source':
            (clone/'.git/objects/info/alternates').write_text(str(source/'.git/objects')+'\n')
        elif name == 'dirty_source':
            (clone/'sample.txt').write_text('uncommitted\n')
        else:
            (clone/'untracked.txt').write_text('untracked\n')
        g.source_preflight(r, clone)
    elif name == 'dirty_restore':
        dest=area/'existing.git'; dest.mkdir(); (dest/'keep.txt').write_text('must remain')
        g.restore(r,bundle,manifest,manifest_sha,dest)
    elif name == 'storage_unreachable':
        g.copy_new(bundle,area/'absent-parent/data.bundle','STORAGE_UNAVAILABLE')
    elif name == 'retrieval_unavailable':
        g.copy_new(area/'absent-storage.bundle',area/'back.bundle','RETRIEVAL_UNAVAILABLE')
    elif name == 'git_unlaunchable':
        r.run([str(area/'nonexistent-git'),'--version'])
    elif name == 'git_nonzero':
        r.git('stage1a-command-does-not-exist')
    elif name == 'timeout':
        r.run([sys.executable,'-c','import time; print("before-timeout",flush=True); time.sleep(60)'], timeout=0.2)
    elif name == 'exception':
        raise ValueError('synthetic exception injection')
    elif name == 'process_end_unknown':
        # Classification injection only, not an uncontrolled live process.
        now=g.utc()
        record=dict(case_id=name,scenario=name,mode='state-contract-injection',
                    expected={'status':'PASS','reason':'OK'},actual={'status':'PASS','reason':'OK'},verdict='PASS',
                    started_at=now,ended_at=now,production_permit=False,
                    commands=[dict(command=['synthetic-no-process'],started_at=now,ended_at=now,
                                   timeout_seconds=1,retry=0,exit_code=None,stdout='',stderr='',process_state='UNKNOWN')])
        g.validate_record(record)
    elif name == 'missing_record':
        g.validate_record({})
    elif name == 'existing_root':
        g.fresh_root(area)
    elif name == 'wrong_inventory':
        m=json.loads(manifest.read_text()); m['target']['refs'][0] = 'refs/heads/wrong '+ '0'*40
        mp=area/'wrong.json'; g.save(mp,m)
        g.restore(r,bundle,mp,g.sha256(mp),area/'restore.git')
    elif name == 'corrupt_pack_with_updated_sha':
        data=bundle.read_bytes(); bad=area/'fault.bundle'; bad.write_bytes(data[:-1]+bytes([data[-1]^1]))
        m=json.loads(manifest.read_text()); m.update(bundle_sha256=g.sha256(bad))
        mp=area/'fault.json'; g.save(mp,m)
        g.restore(r,bad,mp,g.sha256(mp),area/'restore.git')
    elif name.startswith('axes_'):
        vals = {'axes_provenance_unknown': ('PASS','UNKNOWN','NOT_TESTED','PARTIAL'),
                'axes_corrupt_unknown': ('FAIL','UNKNOWN','NOT_TESTED','PARTIAL'),
                'axes_unrecovered': ('UNKNOWN','UNKNOWN','NOT_TESTED','UNKNOWN')}
        value=g.axes(*vals[name]); g.save(area/'axes.json',value)
        return dict(status='PASS',reason='OK',axes=value)
    else:
        raise ValueError('unknown case: '+name)
    return expected()


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root',type=Path,required=True)
    ap.add_argument('--cases',type=Path,default=Path(__file__).with_name('cases.json'))
    args=ap.parse_args()
    root=g.fresh_root(args.root)
    casebytes=args.cases.read_bytes(); cases=json.loads(casebytes)
    if not isinstance(cases,list) or not cases or any(not isinstance(x,dict) or set(x)!={'id','scenario','expected','mode'} for x in cases):
        raise g.Rejected('INVALID_CASE_SET')
    if len({x['id'] for x in cases}) != len(cases):
        raise g.Rejected('DUPLICATE_CASE_ID')
    setup=g.Runner(root); begun=g.utc(); records=[]
    report=dict(kind='SYNTHETIC_LOCAL_EXECUTION',started_at=begun,production_permit=False,
                environment=dict(platform=platform.platform(),python=sys.version),
                checker_sha256=g.sha256(Path(g.__file__)),runner_sha256=g.sha256(Path(__file__)),
                oracle_sha256=g.digest(casebytes),setup_commands=setup.log,cases=records,
                timeout_per_command_seconds=8,retries=0,
                limits=['no durable archive or ACL test','same host/account',
                        'timeout tests only known direct child; general descendant containment UNKNOWN'])
    try:
        pristine=g.generate(setup,root)
        report['git_version']=setup.git('--version')
        anchors={str(p.relative_to(root)):g.sha256(p) for p in pristine[1:3]}
        report['original_anchors']=anchors
        for case in cases:
            area=root/case['id']; area.mkdir()
            r=g.Runner(area); start=g.utc(); tick=time.monotonic()
            try:
                actual=scenario(case['scenario'],r,area,pristine)
            except g.Rejected as exc:
                actual=dict(status=exc.status,reason=exc.reason)
            except Exception as exc:
                actual=dict(status='UNKNOWN',reason='UNEXPECTED_EXCEPTION',error=repr(exc))
            # Compare only declared fields; extra error details remain evidence.
            matched=all(actual.get(k)==v for k,v in case['expected'].items())
            rec=dict(case_id=case['id'],scenario=case['scenario'],mode=case['mode'],
                     input_sha256=g.digest(json.dumps(case,sort_keys=True,separators=(',',':')).encode()),
                     expected=case['expected'],actual=actual,verdict='PASS' if matched else 'FAIL',
                     started_at=start,ended_at=g.utc(),elapsed_seconds=time.monotonic()-tick,
                     commands=r.log,production_permit=False,retries=0)
            g.validate_record(rec); g.save(area/'result.json',rec); records.append(rec)
        report['originals_unchanged']=all(g.sha256(root/p)==h for p,h in anchors.items())
        report['passed']=sum(x['verdict']=='PASS' for x in records)
        report['count']=len(cases)
        report['result']='PASS' if report['passed']==len(cases) and report['originals_unchanged'] else 'FAIL'
    except Exception as exc:
        report.update(result='UNKNOWN',error=repr(exc))
    finally:
        report['ended_at']=g.utc(); g.save(root/'suite.json',report)
    print(json.dumps({k:report.get(k) for k in ('result','count','passed','production_permit')}))
    return 0 if report['result']=='PASS' else 1


if __name__=='__main__':
    sys.exit(main())
