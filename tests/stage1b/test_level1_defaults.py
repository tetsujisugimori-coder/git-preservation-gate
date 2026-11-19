"""Issue #14 synthetic counterexamples for compact Level 1, no filesystem writes."""
import copy
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools' / 'stage1b'))
from contract import validate_contract

HEAD = '1' * 40
POLICY = {'version': '0.2.0', 'commit': '4' * 40}
NOW = '2026-11-19T00:00:00+00:00'
RETENTION = '2027-01-01T00:00:00+00:00'
def minimal():
    return {
        'schema_version': '1',
        'repository': 'example/repo',
        'ref': 'refs/heads/topic',
        'head': HEAD, 'tree': '2'*40, 'parents': ['3'*40],
        'object': {'id': 'docs/guide.md', 'kind': 'git-document'},
        'level': 1,
        'risk': {'confidential': False, 'destructive': False,
                 'strong_authenticity': False, 'important_evidence': False,
                 'publicly_retrievable': True,
                 'rationale': 'Public, retrievable ordinary Git document; synthetic'},
        'policy': POLICY.copy(),
        'observations': {'ci': 'PASS', 'review': 'PASS', 'permissions': 'PASS'},
    }

def with_archive(c):
    c['archive_request'] = {'requested_by': 'owner', 'reason': 'Synthetic extra archive'}
    c.update(attempt_id='trial-l1', approval_id='SYNTH-APPROVAL',
             destination='synthetic-store', operations=['create','read'],
             actor='synthetic-actor', classification='public',
             retention_until=RETENTION, audit_mode='SOLO_STANDARD')
    c['object'].update(size=200, sha256='a'*64)
    c['sessions'] = {'separate_session': True, 'separate_execution': True,
                     'separate_area': True, 'direct_retrieval': True,
                     'human_independent': None, 'shared_owner': True}
    c['observations'].update(storage='PASS', readback='PASS', size='PASS',
                             sha256='PASS', all_bytes='PASS')

def approval():
    return {
        'id': 'SYNTH-APPROVAL', 'scope': 'case',
        'repositories': ['example/repo'], 'object_ids': ['docs/guide.md'],
        'classifications': ['public'], 'destinations': ['synthetic-store'],
        'actors': ['synthetic-actor'], 'operations': ['create','read'],
        'valid_from': '2026-01-01T00:00:00+00:00',
        'valid_until': RETENTION, 'retention_until': RETENTION,
        'delete_move_overwrite': 'prohibited', 'acl': 'PASS',
        'authorization_verified': True,
    }

cases = []
def check(name, expected, mutate=None, scope=None, observed=HEAD, policy=POLICY):
    c = minimal()
    if mutate:
        mutate(c)
    actual = validate_contract(c, scope, NOW, observed, policy)
    wrong = {k: {'expected': v, 'actual': actual.get(k)}
             for k, v in expected.items() if actual.get(k) != v}
    cases.append({'case': name, 'verdict': 'PASS' if not wrong else 'FAIL',
                  'mismatches': wrong, 'actual': actual})
    if actual.get('production_permit') is not False:
        cases[-1]['verdict'] = 'FAIL'
        cases[-1]['mismatches']['production_permit'] = actual.get('production_permit')

def edit(key, value):
    return lambda c: c['observations'].__setitem__(key, value)

BASE = {'contract_status': 'PASS', 'ACCEPTANCE_STATUS': 'PASS',
        'CUSTODY_STATUS': 'NOT_TESTED', 'VERIFICATION_STATUS': 'NOT_TESTED',
        'INDEPENDENCE_STATUS': 'NOT_TESTED', 'archive_status': 'NOT_TESTED',
        'archive_applicability': {'required': False, 'reason': 'LEVEL1_GIT_ONLY_NOT_APPLICABLE'}}
check('L1-01-plain-default', BASE)
check('L1-02-attempt-id-not-archive', BASE, lambda c: c.update(attempt_id='l1-trial'))
check('L1-03-ci-fail', {'ACCEPTANCE_STATUS': 'FAIL'}, edit('ci','FAIL'))
check('L1-04-ci-unknown', {'ACCEPTANCE_STATUS': 'PARTIAL'}, edit('ci','NOT_TESTED'))
check('L1-05-review-fail', {'ACCEPTANCE_STATUS': 'FAIL'}, edit('review','FAIL'))
check('L1-06-review-missing', {'ACCEPTANCE_STATUS': 'PARTIAL'}, lambda c: c['observations'].pop('review'))
check('L1-07-permission-fail', {'ACCEPTANCE_STATUS': 'FAIL'}, edit('permissions','FAIL'))
check('L1-08-permission-not-tested', {'ACCEPTANCE_STATUS': 'PARTIAL'}, lambda c: c['observations'].pop('permissions'))
check('L1-09-head-changed', {'contract_status': 'FAIL', 'ACCEPTANCE_STATUS': 'FAIL'}, observed='f'*40)
check('L1-10-head-unconfirmed', {'contract_status': 'UNKNOWN', 'ACCEPTANCE_STATUS': 'BLOCKED'}, observed=None)
check('L1-11-policy-unconfirmed', {'contract_status': 'UNKNOWN', 'ACCEPTANCE_STATUS': 'BLOCKED'}, policy=None)
check('L1-12-policy-mismatch', {'contract_status': 'FAIL', 'ACCEPTANCE_STATUS': 'FAIL'}, policy={'version':'0.1.0','commit':'5'*40})
check('L1-13-ci-waiver-missing', {'contract_status':'BLOCKED','ACCEPTANCE_STATUS':'BLOCKED'}, lambda c: c.update(ci_required=False))
def waive(c):
    c.update(ci_required=False, ci_exemption={
        'rationale':'Scoped synthetic exemption', 'repository':c['repository'],
        'ref':c['ref'], 'head':c['head'], 'object_id':c['object']['id']})
    c['observations']['ci']='NOT_TESTED'
check('L1-14-scoped-ci-waiver', {'ACCEPTANCE_STATUS':'PASS'}, waive)
check('L1-15-important-evidence-block', {'contract_status':'FAIL','ACCEPTANCE_STATUS':'FAIL'}, lambda c: c['risk'].update(important_evidence=True))
check('L1-16-confidential-block', {'contract_status':'FAIL','ACCEPTANCE_STATUS':'FAIL'}, lambda c: c['risk'].update(confidential=True))
check('L1-17-not-retrievable-block', {'contract_status':'FAIL','ACCEPTANCE_STATUS':'FAIL'}, lambda c: c['risk'].update(publicly_retrievable=False))
check('L1-18-risk-unknown-not-defaulted', {'contract_status':'FAIL','ACCEPTANCE_STATUS':'FAIL'}, lambda c: c['risk'].pop('important_evidence'))
check('L1-19-zip-cannot-be-L1', {'contract_status':'FAIL','ACCEPTANCE_STATUS':'FAIL'}, lambda c: c['object'].update(kind='zip'))
check('L1-20-implicit-storage-rejected', {'contract_status':'FAIL','ACCEPTANCE_STATUS':'FAIL'}, lambda c: c.update(destination='synthetic-store'))
def only_request(c):
    c['archive_request'] = {'requested_by':'owner','reason':'Synthetic only'}
check('L1-21-explicit-save-missing-fields',
      {'contract_status':'PASS','ACCEPTANCE_STATUS':'PASS','archive_status':'BLOCKED',
       'archive_applicability': {'required': True, 'reason':'LEVEL1_EXPLICIT_ARCHIVE_REQUEST'}}, only_request)
check('L1-22-explicit-save-missing-approval',
      {'ACCEPTANCE_STATUS':'PASS','archive_status':'BLOCKED'},
      with_archive)
check('L1-23-explicit-save-success-synthetic',
      {'ACCEPTANCE_STATUS':'PASS','archive_status':'PASS',
       'CUSTODY_STATUS':'PASS','VERIFICATION_STATUS':'PASS',
       'INDEPENDENCE_STATUS':'PARTIAL'}, with_archive, approval())
def no_readback(c):
    with_archive(c)
    c['observations']['readback']='NOT_TESTED'
check('L1-24-explicit-save-readback-pending',
      {'ACCEPTANCE_STATUS':'PASS','archive_status':'PARTIAL',
       'VERIFICATION_STATUS':'NOT_TESTED'}, no_readback, approval())
def sha_bad(c):
    with_archive(c)
    c['observations']['sha256']='FAIL'
check('L1-25-explicit-save-known-fail',
      {'ACCEPTANCE_STATUS':'PASS','archive_status':'FAIL',
       'VERIFICATION_STATUS':'FAIL'}, sha_bad, approval())
def wrong_destination(c):
    with_archive(c)
    c['destination']='unauthorized'
check('L1-26-scope-mismatch',
      {'ACCEPTANCE_STATUS':'PASS','archive_status':'BLOCKED',
       'archive_contract_status':'BLOCKED'}, wrong_destination, approval())
def missing_archive_destination(c):
    with_archive(c)
    c.pop('destination')
check('L1-27-archive-input-missing-git-still-pass',
      {'ACCEPTANCE_STATUS':'PASS','archive_status':'BLOCKED'}, missing_archive_destination, approval())
def missing_sessions(c):
    with_archive(c)
    c.pop('sessions')
check('L1-28-independent-read-not-asserted',
      {'ACCEPTANCE_STATUS':'PASS','archive_status':'PARTIAL',
       'INDEPENDENCE_STATUS':'UNKNOWN'}, missing_sessions, approval())
def ci_failure_archive(c):
    with_archive(c)
    c['observations']['ci']='FAIL'
check('L1-29-git-fail-does-not-rewrite-archive',
      {'ACCEPTANCE_STATUS':'FAIL','archive_status':'PASS'}, ci_failure_archive, approval())
def wrongful_waiver(c):
    waive(c)
    c['ci_exemption']['object_id']='another-object'
check('L1-30-wrong-scoped-waiver',
      {'contract_status':'BLOCKED','ACCEPTANCE_STATUS':'BLOCKED'}, wrongful_waiver)

def malformed_archive_request(c):
    c['archive_request'] = {'requested_by':'owner'}
check('L1-31-invalid-archive-request-isolated',
      {'contract_status':'PASS','ACCEPTANCE_STATUS':'PASS','archive_status':'BLOCKED'},
      malformed_archive_request)
def failed_custody_missing_destination(c):
    with_archive(c)
    c.pop('destination')
    c['observations']['storage']='FAIL'
check('L1-32-known-fail-survives-missing-archive-metadata',
      {'ACCEPTANCE_STATUS':'PASS','archive_status':'FAIL','CUSTODY_STATUS':'FAIL'},
      failed_custody_missing_destination, approval())

def observed_fail_without_opt_in(c):
    c['observations']['storage'] = 'FAIL'
check('L1-33-rejected-archive-evidence-retains-known-fail',
      {'contract_status':'FAIL','CUSTODY_STATUS':'FAIL'}, observed_fail_without_opt_in)
bad_acl = approval()
bad_acl['acl'] = 'UNKNOWN'
check('L1-34-unverified-acl-blocks-only-archive',
      {'ACCEPTANCE_STATUS':'PASS','archive_status':'BLOCKED'}, with_archive, bad_acl)
def malformed_request_known_fail(c):
    malformed_archive_request(c)
    c['observations']['storage']='FAIL'
check('L1-35-malformed-archive-retains-known-fail',
      {'ACCEPTANCE_STATUS':'PASS','archive_status':'FAIL',
       'CUSTODY_STATUS':'FAIL'}, malformed_request_known_fail)

failures = [x['case'] for x in cases if x['verdict'] != 'PASS']
print(json.dumps({'suite':'issue14-compact-level1-synthetic', 'total':len(cases),
                  'pass':len(cases)-len(failures), 'failures':failures,
                  'cases':cases, 'production_permit':False}, ensure_ascii=False, indent=2))
sys.exit(1 if failures else 0)
