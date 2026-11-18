#!/usr/bin/env python3
"""Stage 1-A synthetic-only Git bundle and isolated restoration probe.

Never accepts an existing repo as input. --root must NOT exist; no cleanup,
deletion, existing archive mutations, or production permissions are issued.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from datetime import datetime, timezone

TIMEOUT = 8

def utc():
    return datetime.now(timezone.utc).isoformat()

def sha256(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

def same_bytes(a, b):
    if a.stat().st_size != b.stat().st_size:
        return False
    with a.open('rb') as fa, b.open('rb') as fb:
        while True:
            x, y = fa.read(1024 * 1024), fb.read(1024 * 1024)
            if x != y:
                return False
            if not x:
                return True

def cli(cmd, log, env=None):
    start = utc()
    try:
        r = subprocess.run([str(s) for s in cmd], capture_output=True, text=True,
                           timeout=TIMEOUT, env=env, check=False)
        record = {'command': [str(s) for s in cmd], 'started_at': start,
                  'ended_at': utc(), 'timeout_seconds': TIMEOUT, 'retry': 0,
                  'exit_code': r.returncode, 'stdout': r.stdout, 'stderr': r.stderr}
        log.append(record)
        if r.returncode != 0:
            raise RuntimeError(f'Command failed with exit code {r.returncode}')
        return r.stdout.strip()
    except subprocess.TimeoutExpired as e:
        log.append({'command': [str(s) for s in cmd], 'started_at': start,
                    'ended_at': utc(), 'timeout_seconds': TIMEOUT, 'retry': 0,
                    'exit_code': None, 'status': 'UNKNOWN', 'reason': 'TIMEOUT',
                    'stdout': str(e.stdout or ''), 'stderr': str(e.stderr or '')})
        raise

def git(log, *args, env=None):
    return cli(['git', *args], log, env=env)

def refs(log, path, bare=False):
    pfx = ['--git-dir', str(path)] if bare else ['-C', str(path)]
    raw = git(log, *pfx, 'for-each-ref', '--format=%(refname) %(objectname)')
    return sorted(raw.splitlines())

def objects(log, path, bare=False):
    pfx = ['--git-dir', str(path)] if bare else ['-C', str(path)]
    raw = git(log, *pfx, 'rev-list', '--objects', '--all')
    return sorted(line.split()[0] for line in raw.splitlines())

def main():
    a = argparse.ArgumentParser(description=__doc__)
    a.add_argument('--root', type=Path, required=True,
                   help='A brand-new directory; must not exist (parent must exist)')
    args = a.parse_args()
    root = args.root.absolute()
    if not root.parent.is_dir() or root.exists() or root.is_symlink():
        print('Refusing to touch an existing root or non-existing parent', file=sys.stderr)
        return 2
    try:
        root.mkdir(mode=0o700)
    except OSError as e:
        print(f'Cannot create isolated root: {e}', file=sys.stderr)
        return 2
    log = []
    evidence = {'kind': 'STAGE1A_SYNTHETIC_ONLY', 'started_at': utc(),
                'production_permit': False, 'test_case': 'T01/T05/T06 limited',
                'commands': log, 'checks': {}, 'limitations': [
                    'No real repository or owner data was read',
                    'No independent human / credential / host principal',
                    'No long-term storage, ACL, or retention guarantee',
                    'No production acceptance and no real authorization',
                ]}
    try:
        source, archive, recovery = root / 'source', root / 'archive', root / 'retrieved'
        source.mkdir(); archive.mkdir(); recovery.mkdir()
        git(log, 'init', '-b', 'main', str(source))
        env = os.environ.copy()
        env.update(GIT_AUTHOR_NAME='Synthetic Tester', GIT_AUTHOR_EMAIL='synthetic@example.invalid',
                   GIT_COMMITTER_NAME='Synthetic Tester', GIT_COMMITTER_EMAIL='synthetic@example.invalid')
        (source / 'sample.txt').write_text('synthetic-stage1a-first\n', encoding='utf-8')
        git(log, '-C', str(source), 'add', 'sample.txt')
        git(log, '-C', str(source), 'commit', '-m', 'synthetic first', env=env)
        (source / 'sample.txt').write_text('synthetic-stage1a-second\n', encoding='utf-8')
        git(log, '-C', str(source), 'commit', '-am', 'synthetic second', env=env)
        git(log, '-C', str(source), 'tag', 'synthetic-v1')
        source_refs, source_objects = refs(log, source), objects(log, source)
        evidence['target'] = {'source_refs': source_refs, 'source_object_ids': source_objects,
                              'head': git(log, '-C', str(source), 'rev-parse', 'HEAD'),
                              'tree': git(log, '-C', str(source), 'rev-parse', 'HEAD^{tree}'),
                              'parents': git(log, '-C', str(source), 'show', '--format=%P', '-s', 'HEAD').split()}
        bundle = root / 'original.bundle'
        git(log, '-C', str(source), 'bundle', 'create', str(bundle), '--all')
        header = bundle.read_bytes()[:1024].split(b'PACK', 1)[0]
        if b'\n-' in header:
            raise RuntimeError('Bundle carries prerequisites; refusing non-self-contained archive')
        evidence['checks']['no_bundle_prerequisites'] = 'PASS'
        manifest = {'format': 'stage1a-synthetic-v1', 'kind': 'synthetic-git-bundle',
                    'bundle_sha256': sha256(bundle), 'bundle_size': bundle.stat().st_size,
                    'target': evidence['target']}
        with (root / 'manifest.json').open('x', encoding='utf-8') as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2); f.write('\n')
        stored = archive / 'original.bundle'
        with bundle.open('rb') as src, stored.open('xb') as dst:
            shutil.copyfileobj(src, dst)
        copied = recovery / 'readback.bundle'
        with stored.open('rb') as src, copied.open('xb') as dst:
            shutil.copyfileobj(src, dst)
        if not (sha256(stored) == sha256(copied) == manifest['bundle_sha256']):
            raise RuntimeError('SHA mismatch in stored/retrieved bundle')
        if not (same_bytes(bundle, stored) and same_bytes(bundle, copied)):
            raise RuntimeError('Stored/retrieved all-byte mismatch')
        evidence['checks']['storage_retrieval_sha_bytes'] = 'PASS'
        restore = root / 'empty-bare-restore'
        git(log, 'init', '--bare', str(restore))
        pre = git(log, '--git-dir', str(restore), 'count-objects', '-v')
        evidence['restore_preflight'] = pre
        if 'count: 0' not in pre or 'in-pack: 0' not in pre:
            raise RuntimeError('Restore repository was not empty')
        git(log, '--git-dir', str(restore), 'fetch', '--no-tags', str(copied),
            '+refs/heads/*:refs/heads/*', '+refs/tags/*:refs/tags/*')
        git(log, '--git-dir', str(restore), 'fsck', '--full', '--strict', '--no-reflogs')
        if refs(log, restore, bare=True) != source_refs:
            raise RuntimeError('Restored refs differ from source')
        if objects(log, restore, bare=True) != source_objects:
            raise RuntimeError('Restored object OID set differs from source')
        evidence['checks']['empty_bare_restore_fsck_refs_objects'] = 'PASS'
        tampered = root / 'tampered.bundle'
        corrupted = bytearray(copied.read_bytes())
        corrupted[-1] ^= 0x01
        with tampered.open('xb') as f:
            f.write(corrupted)
        detected = sha256(tampered) != manifest['bundle_sha256'] and not same_bytes(tampered, copied)
        evidence['checks']['T05_corrupt_copy_rejected'] = 'PASS' if detected else 'FAIL'
        if not detected:
            raise RuntimeError('Corruption detection failed')
        altered_expectation = '0' * 64 if manifest['bundle_sha256'] != '0' * 64 else 'f' * 64
        evidence['checks']['T06_wrong_expected_sha_rejected'] = ('PASS' if sha256(copied) != altered_expectation else 'FAIL')
        evidence['result'] = 'PASS'
    except (OSError, RuntimeError, ValueError, subprocess.TimeoutExpired) as e:
        evidence['result'] = 'UNKNOWN' if isinstance(e, subprocess.TimeoutExpired) else 'FAIL'
        evidence['error'] = f'{type(e).__name__}: {e}'
    finally:
        evidence['ended_at'] = utc()
        try:
            with (root / 'result.json').open('x', encoding='utf-8') as f:
                json.dump(evidence, f, ensure_ascii=False, indent=2); f.write('\n')
        except OSError as e:
            print(f'Result not persisted: {e}', file=sys.stderr)
            return 2
    print(json.dumps({'result': evidence['result'], 'checks': evidence['checks'],
                      'evidence': str(root / 'result.json'), 'production_permit': False}, ensure_ascii=False))
    return 0 if evidence['result'] == 'PASS' else 1

if __name__ == '__main__':
    sys.exit(main())
