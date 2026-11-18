#!/usr/bin/env python3
"""Synthetic-only bundle probe. No existing repository input or production permit.
Each run uses a new root; never cleans up, overwrites, or deletes evidence.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import signal
import subprocess
import sys
from datetime import datetime, timezone

TIMEOUT = 8


def utc():
    return datetime.now(timezone.utc).isoformat()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def sha256(path):
    return digest(Path(path).read_bytes())


def same_bytes(a, b):
    return Path(a).read_bytes() == Path(b).read_bytes()


def save(path, value):
    with Path(path).open('x', encoding='utf-8') as f:
        json.dump(value, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write('\n')


class Rejected(Exception):
    def __init__(self, reason, status='FAIL'):
        super().__init__(reason)
        self.reason, self.status = reason, status


def isolated_env(root):
    env = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}
    env.update(GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL=os.devnull,
               GIT_TERMINAL_PROMPT='0', GIT_ALLOW_PROTOCOL='file',
               GIT_AUTHOR_NAME='Synthetic Tester', GIT_AUTHOR_EMAIL='synthetic@example.invalid',
               GIT_COMMITTER_NAME='Synthetic Tester', GIT_COMMITTER_EMAIL='synthetic@example.invalid',
               GIT_AUTHOR_DATE='2026-11-18T00:00:00+00:00',
               GIT_COMMITTER_DATE='2026-11-18T00:00:00+00:00',
               GIT_CONFIG_COUNT='2', GIT_CONFIG_KEY_0='core.hooksPath',
               GIT_CONFIG_VALUE_0=os.devnull, GIT_CONFIG_KEY_1='commit.gpgSign',
               GIT_CONFIG_VALUE_1='false')
    return env


class Runner:
    def __init__(self, root, git_executable='git'):
        self.env = isolated_env(root)
        self.git_executable = git_executable
        self.log = []

    def run(self, command, timeout=TIMEOUT):
        command = [str(x) for x in command]
        record = dict(command=command, started_at=utc(), timeout_seconds=timeout,
                      retry=0, exit_code=None, stdout='', stderr='', process_state='NOT_STARTED')
        self.log.append(record)
        proc = None
        try:
            proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    env=self.env, start_new_session=(os.name == 'posix'))
            record['pid'] = proc.pid
            record['process_state'] = 'RUNNING'
            try:
                out, err = proc.communicate(timeout=timeout)
            except subprocess.TimeoutExpired as exc:
                record['stdout'] = (exc.output or b'').decode('utf-8', 'replace')
                record['stderr'] = (exc.stderr or b'').decode('utf-8', 'replace')
                if os.name == 'posix':
                    os.killpg(proc.pid, signal.SIGKILL)
                else:
                    proc.kill()
                try:
                    out, err = proc.communicate(timeout=2)
                    record.update(stdout=out.decode('utf-8', 'replace'),
                                  stderr=err.decode('utf-8', 'replace'), exit_code=proc.returncode,
                                  process_state='DIRECT_CHILD_REAPED')
                except subprocess.TimeoutExpired:
                    record['process_state'] = 'UNKNOWN'
                    raise Rejected('PROCESS_END_UNKNOWN', 'UNKNOWN')
                record['descendant_state'] = 'NOT_INDEPENDENTLY_AUDITED'
                raise Rejected('TIMEOUT', 'UNKNOWN')
            record.update(stdout=out.decode('utf-8', 'replace'), stderr=err.decode('utf-8', 'replace'),
                          exit_code=proc.returncode, process_state='DIRECT_CHILD_REAPED')
            if proc.returncode:
                raise Rejected('COMMAND_NONZERO')
            return out
        except OSError as exc:
            record['error'] = type(exc).__name__ + ': ' + str(exc)
            if proc is not None:
                # A kill/audit failure is not a known stopped process.
                record['process_state'] = 'UNKNOWN'
                raise Rejected('PROCESS_END_UNKNOWN', 'UNKNOWN') from exc
            raise Rejected('SPAWN_FAILED', 'BLOCKED') from exc
        finally:
            record['ended_at'] = utc()

    def git(self, *args):
        return self.run([self.git_executable, *args]).decode('utf-8').strip()


def fresh_root(path):
    path = Path(path).absolute()
    if path.exists() or path.is_symlink() or not path.parent.is_dir():
        raise Rejected('ROOT_NOT_NEW', 'BLOCKED')
    path.mkdir(mode=0o700)
    return path


def copy_new(source, destination, reason):
    try:
        if Path(source).is_symlink() or Path(destination).is_symlink():
            raise Rejected(reason, 'BLOCKED')
        with Path(source).open('rb') as src, Path(destination).open('xb') as dst:
            shutil.copyfileobj(src, dst)
    except OSError as exc:
        raise Rejected(reason, 'BLOCKED') from exc


def source_preflight(r, source):
    gd = Path(r.git('-C', source, 'rev-parse', '--absolute-git-dir'))
    if (gd / 'shallow').exists():
        raise Rejected('SHALLOW_SOURCE', 'BLOCKED')
    if (gd / 'objects/info/alternates').exists():
        raise Rejected('ALTERNATES_SOURCE', 'BLOCKED')
    config = r.git('-C', source, 'config', '--local', '--list').lower()
    if 'extensions.partialclone=' in config or re.search(r'remote\..*\.(promisor|partialclonefilter)=', config):
        raise Rejected('PARTIAL_SOURCE', 'BLOCKED')
    if r.git('-C', source, 'status', '--porcelain'):
        raise Rejected('DIRTY_OR_UNTRACKED_SOURCE', 'BLOCKED')
    return gd


def inventory(r, path, bare=False):
    pfx = ['--git-dir', path] if bare else ['-C', path]
    refs = r.git(*pfx, 'for-each-ref', '--format=%(refname) %(objectname)').splitlines()
    ids = sorted(set(x.split()[0] for x in r.git(*pfx, 'rev-list', '--objects', '--all').splitlines()))
    if not refs or not ids:
        raise Rejected('EMPTY_INVENTORY')
    entries = []
    for oid in ids:
        kind = r.git(*pfx, 'cat-file', '-t', oid)
        raw = r.run([r.git_executable, *pfx, 'cat-file', kind, oid])
        calculated = hashlib.sha1(f'{kind} {len(raw)}\0'.encode() + raw).hexdigest()
        if calculated != oid:
            raise Rejected('OBJECT_ID_MISMATCH')
        item = dict(oid=oid, type=kind, size=len(raw), sha256=digest(raw))
        if kind == 'commit':
            header = raw.split(b'\n\n', 1)[0].decode()
            item['tree'] = next(x[5:] for x in header.splitlines() if x.startswith('tree '))
            item['parents'] = [x[7:] for x in header.splitlines() if x.startswith('parent ')]
        entries.append(item)
    return dict(refs=sorted(refs), objects=entries)


def generate(r, root):
    source = root / 'source'
    r.git('init', '--object-format=sha1', '-b', 'main', source)
    (source / 'sample.txt').write_text('synthetic first\n')
    r.git('-C', source, 'add', 'sample.txt')
    r.git('-C', source, 'commit', '-m', 'synthetic first')
    (source / 'sample.txt').write_text('synthetic second\n')
    r.git('-C', source, 'commit', '-am', 'synthetic second')
    r.git('-C', source, 'checkout', '-b', 'feature')
    (source / 'feature.txt').write_text('synthetic branch\n')
    r.git('-C', source, 'add', 'feature.txt')
    r.git('-C', source, 'commit', '-m', 'synthetic feature')
    r.git('-C', source, 'tag', '-a', 'synthetic-v1', '-m', 'synthetic annotated tag')
    r.git('-C', source, 'checkout', 'main')
    source_preflight(r, source)
    target = inventory(r, source)
    bundle = root / 'original.bundle'
    r.git('-C', source, 'bundle', 'create', bundle, '--all')
    manifest = dict(format='stage1a-synthetic-v2', kind='synthetic-git-bundle',
                    bundle_size=bundle.stat().st_size, bundle_sha256=sha256(bundle), target=target)
    mp = root / 'manifest.json'
    save(mp, manifest)
    return source, bundle, mp, target


def validate_payload(bundle, manifest_path, expected_manifest_sha):
    try:
        mb = Path(manifest_path).read_bytes()
    except OSError as exc:
        raise Rejected('MANIFEST_MISSING') from exc
    try:
        m = json.loads(mb)
    except (ValueError, UnicodeError) as exc:
        raise Rejected('MANIFEST_INVALID') from exc
    if digest(mb) != expected_manifest_sha:
        raise Rejected('MANIFEST_CHANGED')
    if (not isinstance(m, dict) or set(m) != {'format','kind','bundle_size','bundle_sha256','target'}
            or m['format'] != 'stage1a-synthetic-v2' or m['kind'] != 'synthetic-git-bundle'
            or type(m['bundle_size']) is not int or m['bundle_size'] <= 0
            or not isinstance(m['bundle_sha256'], str) or not re.fullmatch('[0-9a-f]{64}', m['bundle_sha256'])
            or not isinstance(m['target'], dict) or not m['target'].get('objects') or not m['target'].get('refs')):
        raise Rejected('MANIFEST_INVALID')
    try:
        data = Path(bundle).read_bytes()
    except OSError as exc:
        raise Rejected('BUNDLE_MISSING') from exc
    if len(data) != m['bundle_size'] or digest(data) != m['bundle_sha256']:
        raise Rejected('BUNDLE_INTEGRITY')
    # Header terminates at a blank line. This intentionally only supports SHA-1 v2.
    if not data.startswith(b'# v2 git bundle\n') or b'\n\n' not in data:
        raise Rejected('BUNDLE_HEADER')
    header = data.split(b'\n\n', 1)[0].splitlines()[1:]
    if any(line.startswith(b'-') for line in header):
        raise Rejected('BUNDLE_PREREQUISITES', 'BLOCKED')
    if not header or any(not re.fullmatch(rb'[0-9a-f]{40} [^\x00-\x20]+', line) for line in header):
        raise Rejected('BUNDLE_HEADER')
    return m


def restore(r, bundle, manifest_path, manifest_sha, destination):
    m = validate_payload(bundle, manifest_path, manifest_sha)
    destination = Path(destination)
    if destination.exists() or destination.is_symlink():
        raise Rejected('RESTORE_NOT_NEW', 'BLOCKED')
    r.git('init', '--bare', '--object-format=sha1', destination)
    r.git('--git-dir', destination, 'bundle', 'verify', bundle)
    r.git('--git-dir', destination, 'fetch', '--no-tags', bundle, 'refs/*:refs/*')
    if (destination / 'objects/info/alternates').exists() or (destination / 'shallow').exists():
        raise Rejected('RESTORE_EXTERNAL_DEPENDENCY')
    r.git('--git-dir', destination, 'fsck', '--full', '--strict', '--no-reflogs')
    actual = inventory(r, destination, True)
    if actual != m['target']:
        raise Rejected('RESTORE_INVENTORY_MISMATCH')
    # Count every stored object, not just reachable IDs. No hidden missing/extra objects.
    all_objects = r.git('--git-dir', destination, 'cat-file', '--batch-all-objects', '--batch-check=%(objectname)').splitlines()
    if sorted(all_objects) != sorted(x['oid'] for x in actual['objects']):
        raise Rejected('RESTORE_OBJECT_SET')
    return actual


def axes(content='NOT_TESTED', provenance='UNKNOWN', restoration='NOT_TESTED', independence='UNKNOWN'):
    allowed = {'PASS','FAIL','UNKNOWN','NOT_TESTED','BLOCKED','PARTIAL'}
    if any(x not in allowed for x in (content, provenance, restoration, independence)):
        raise Rejected('AXIS_VALUE_INVALID')
    return dict(CONTENT_INTEGRITY=content, PROVENANCE_STATUS=provenance,
                RESTORE_STATUS=restoration, INDEPENDENCE_STATUS=independence, production_permit=False)


def validate_record(record):
    required = {'case_id','scenario','mode','expected','actual','verdict','started_at','ended_at','commands','production_permit'}
    if not isinstance(record, dict) or not required <= record.keys() or record['production_permit'] is not False:
        raise Rejected('RECORD_MISSING')
    for key in ('case_id','scenario','started_at','ended_at'):
        if not isinstance(record[key], str) or not record[key]:
            raise Rejected('RECORD_MISSING')
    try:
        start, end = (datetime.fromisoformat(record[k]) for k in ('started_at','ended_at'))
        if start.tzinfo is None or end.tzinfo is None or end < start:
            raise ValueError('time order')
    except ValueError as exc:
        raise Rejected('RECORD_TIME_INVALID') from exc
    for key in ('expected','actual'):
        obj=record[key]
        if not isinstance(obj,dict) or obj.get('status') not in {'PASS','FAIL','UNKNOWN','NOT_TESTED','BLOCKED','PARTIAL'} or not isinstance(obj.get('reason'),str):
            raise Rejected('RECORD_STATE_INVALID')
    state_scenarios={'process_end_unknown','missing_record','axes_provenance_unknown',
                     'axes_corrupt_unknown','axes_unrecovered'}
    operation_scenarios={'normal','normal_repeat','missing_bundle','empty_bundle','truncated_bundle',
        'modified_byte','wrong_sha','missing_manifest','invalid_manifest','replaced_manifest',
        'schema_manifest','prerequisite_bundle','shallow_source','partial_source','alternates_source',
        'dirty_source','untracked_source','dirty_restore','storage_unreachable','retrieval_unavailable',
        'git_unlaunchable','git_nonzero','timeout','exception','existing_root','wrong_inventory',
        'corrupt_pack_with_updated_sha'}
    if record['scenario'] not in state_scenarios | operation_scenarios:
        raise Rejected('RECORD_SCENARIO_INVALID')
    required_mode='state-contract-injection' if record['scenario'] in state_scenarios else 'local-synthetic-operation'
    if record['mode'] != required_mode:
        raise Rejected('RECORD_MODE_INVALID')
    commands=record['commands']
    if not isinstance(commands,list):
        raise Rejected('RECORD_COMMAND_INVALID')
    needs_commands={'normal','normal_repeat','prerequisite_bundle','shallow_source','partial_source',
                    'alternates_source','dirty_source','untracked_source','git_unlaunchable',
                    'git_nonzero','timeout','wrong_inventory','corrupt_pack_with_updated_sha'}
    if record['mode']=='local-synthetic-operation' and record['scenario'] in needs_commands and not commands:
        raise Rejected('RECORD_COMMAND_MISSING')
    for c in commands:
        fields={'command','started_at','ended_at','timeout_seconds','retry','exit_code','stdout','stderr','process_state'}
        if not isinstance(c,dict) or not fields <= c.keys():
            raise Rejected('RECORD_COMMAND_INVALID')
        if (not isinstance(c['command'],list) or not c['command'] or any(not isinstance(x,str) for x in c['command'])
                or not isinstance(c['stdout'],str) or not isinstance(c['stderr'],str)
                or type(c['retry']) is not int or c['retry']!=0
                or type(c['timeout_seconds']) not in (int,float) or not 0<c['timeout_seconds']<=TIMEOUT
                or (c['exit_code'] is not None and type(c['exit_code']) is not int)):
            raise Rejected('RECORD_COMMAND_INVALID')
        try:
            cs,ce=(datetime.fromisoformat(c[k]) for k in ('started_at','ended_at'))
            if cs.tzinfo is None or ce.tzinfo is None or ce<cs:
                raise ValueError('command time')
        except (ValueError,TypeError) as exc:
            raise Rejected('RECORD_TIME_INVALID') from exc
        if c['process_state'] in ('UNKNOWN','RUNNING'):
            if record['actual']['status'] != 'UNKNOWN':
                raise Rejected('PROCESS_END_UNKNOWN','UNKNOWN')
        elif c['process_state']=='DIRECT_CHILD_REAPED':
            if c['exit_code'] is None:
                raise Rejected('RECORD_COMMAND_INVALID')
        elif c['process_state']=='NOT_STARTED':
            if c['exit_code'] is not None or record['actual']['status']=='PASS':
                raise Rejected('RECORD_COMMAND_INVALID')
        else:
            raise Rejected('RECORD_COMMAND_INVALID')
        if record['actual']['status']=='PASS' and (c['exit_code']!=0 or c['process_state']!='DIRECT_CHILD_REAPED'):
            raise Rejected('RECORD_FALSE_PASS')
    matched=all(record['actual'].get(k)==v for k,v in record['expected'].items())
    if record['verdict'] != ('PASS' if matched else 'FAIL'):
        raise Rejected('RECORD_VERDICT_MISMATCH')
    return True


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root', type=Path, required=True)
    args = ap.parse_args()
    try:
        root = fresh_root(args.root)
    except Rejected as exc:
        print(exc.reason, file=sys.stderr)
        return 2
    r = Runner(root)
    result = dict(kind='STAGE1A_SYNTHETIC_ONLY', started_at=utc(), production_permit=False,
                  environment=dict(python=sys.version, platform=platform.platform()), commands=r.log)
    try:
        source, bundle, manifest, target = generate(r, root)
        archive, retrieved = root/'archive', root/'retrieved'
        archive.mkdir(); retrieved.mkdir()
        for src, name in ((bundle,'original.bundle'), (manifest,'manifest.json')):
            copy_new(src, archive/name, 'STORAGE_UNAVAILABLE')
            copy_new(archive/name, retrieved/name, 'RETRIEVAL_UNAVAILABLE')
            if not same_bytes(src, retrieved/name):
                raise Rejected('READBACK_BYTES')
        actual = restore(r, retrieved/'original.bundle', retrieved/'manifest.json', sha256(manifest), root/'restore.git')
        result.update(status='PASS', target=actual, bundle_size=bundle.stat().st_size, bundle_sha256=sha256(bundle),
                      manifest_sha256=sha256(manifest), axes=axes('PASS','PASS','PASS','NOT_TESTED'))
    except Rejected as exc:
        result.update(status=exc.status, reason=exc.reason)
    except Exception as exc:
        result.update(status='UNKNOWN', reason='UNEXPECTED_EXCEPTION', error=repr(exc))
    result['ended_at'] = utc()
    save(root/'result.json', result)
    print(json.dumps({k: result[k] for k in ('status','production_permit')}))
    return 0 if result['status'] == 'PASS' else 1


if __name__ == '__main__':
    sys.exit(main())
