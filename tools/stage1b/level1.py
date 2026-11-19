"""Issue #14: opt-in Level 1 Git-only input. Pure trusted-record evaluation; no I/O."""
from copy import deepcopy

BASE = {'schema_version', 'repository', 'ref', 'head', 'tree', 'parents',
        'object', 'level', 'risk', 'policy', 'observations'}
OPTIONAL = {'attempt_id', 'ci_required', 'ci_exemption', 'archive_request',
            'approval_id', 'destination', 'operations', 'actor', 'classification',
            'retention_until', 'delete_move_overwrite', 'audit_mode',
            'required_checks', 'extra_checks', 'extra_decision', 'sessions'}
ARCHIVE = OPTIONAL - {'ci_required', 'ci_exemption', 'archive_request', 'attempt_id'}
ARCHIVE_OBS = {'storage', 'readback', 'size', 'sha256', 'all_bytes', 'bundle_restore'}
RISK_FLAGS = ('confidential', 'destructive', 'strong_authenticity',
              'important_evidence', 'publicly_retrievable')
REQUIRED_ARCHIVE = ('attempt_id', 'approval_id', 'destination', 'operations',
                    'actor', 'classification', 'retention_until', 'audit_mode')


def is_compact_l1(c):
    """Legacy complete schema stays byte-for-byte semantically compatible."""
    return (isinstance(c, dict) and type(c.get('level')) is int and c['level'] == 1
            and ('archive_request' in c or any(k not in c for k in
                 ('approval_id', 'destination', 'operations', 'actor',
                  'classification', 'retention_until', 'delete_move_overwrite',
                  'audit_mode', 'required_checks', 'extra_checks',
                  'extra_decision', 'sessions'))))


def validate_level1(c, approval, now, observed_head, effective_policy):
    from contract import Invalid, aggregate, boolean, exact, hexid, schema, stamp, state, string, strings, validate_contract

    reasons = []
    invalid_archive_request = False
    out = {
        'contract_status': 'FAIL', 'reason_codes': reasons,
        'CUSTODY_STATUS': 'NOT_TESTED', 'VERIFICATION_STATUS': 'NOT_TESTED',
        'INDEPENDENCE_STATUS': 'NOT_TESTED', 'ACCEPTANCE_STATUS': 'FAIL',
        'human_independence': 'UNKNOWN', 'production_permit': False,
        'archive_applicability': {'required': False, 'reason': 'LEVEL1_GIT_ONLY_NOT_APPLICABLE'},
        'archive_status': 'NOT_TESTED', 'archive_contract_status': 'NOT_TESTED',
        'archive_reason_codes': [],
    }
    try:
        if not isinstance(c, dict) or not BASE <= set(c) or not set(c) <= BASE | OPTIONAL:
            raise Invalid('keys')
        if c['schema_version'] != '1' or c['level'] != 1:
            raise Invalid('version/level')
        for k in ('repository', 'ref'):
            string(c[k])
        for k in ('head', 'tree'):
            hexid(c[k], 40)
        strings(c['parents'])
        for parent in c['parents']:
            hexid(parent, 40)
        obj = c['object']
        if not isinstance(obj, dict) or not {'id', 'kind'} <= set(obj) or not set(obj) <= {'id', 'kind', 'size', 'sha256'}:
            raise Invalid('object keys')
        string(obj['id'])
        if obj['kind'] != 'git-document':
            raise Invalid('L1 object kind')  # no ZIP/bundle/evidence masquerading as Git docs
        if 'size' in obj and (type(obj['size']) is not int or obj['size'] <= 0):
            raise Invalid('size')
        if 'sha256' in obj:
            hexid(obj['sha256'], 64)
        risk = c['risk']
        if not isinstance(risk, dict) or set(risk) != set(RISK_FLAGS) | {'rationale'}:
            raise Invalid('risk keys')
        string(risk['rationale'])
        for k in RISK_FLAGS:
            boolean(risk[k])
        exact(c['policy'], 'version commit')
        string(c['policy']['version'])
        hexid(c['policy']['commit'], 40)
        stamp(now)
        ci_required = c.get('ci_required', True)
        boolean(ci_required)
        if 'attempt_id' in c:
            string(c['attempt_id'])
        if 'ci_exemption' in c:
            ex = c['ci_exemption']
            exact(ex, 'rationale repository ref head object_id')
            for k in ('rationale', 'repository', 'ref', 'object_id'):
                string(ex[k])
            hexid(ex['head'], 40)
            if ci_required:
                raise Invalid('CI exemption conflicts with required CI')
        obs = c['observations']
        if not isinstance(obs, dict) or not set(obs) <= {'ci','review','permissions'} | ARCHIVE_OBS:
            raise Invalid('observations keys')
        for v in obs.values():
            state(v)
        if 'archive_request' in c:
            try:
                exact(c['archive_request'], 'requested_by reason')
                if c['archive_request']['requested_by'] not in ('owner', 'case_contract'):
                    raise Invalid('archive requester')
                string(c['archive_request']['reason'])
            except (ValueError, TypeError, KeyError):
                invalid_archive_request = True
        elif set(c) & ARCHIVE or set(obs) & ARCHIVE_OBS:
            raise Invalid('archive intent must be explicit')
        if 'ci_required' in c and type(c['ci_required']) is not bool:
            raise Invalid('bool')
    except (ValueError, TypeError, KeyError):
        reasons.append('SCHEMA_INVALID')
        return out

    status = 'PASS'
    def fault(s, reason):
        nonlocal status
        status = aggregate([status, s])
        reasons.append(reason)

    if not risk['publicly_retrievable'] or risk['important_evidence'] or any(
        risk[k] for k in ('confidential', 'destructive', 'strong_authenticity')
    ):
        fault('FAIL', 'LEVEL_TOO_LOW')
    if effective_policy is None:
        fault('UNKNOWN', 'POLICY_UNCONFIRMED')
    elif not isinstance(effective_policy, dict) or c['policy'] != effective_policy:
        fault('FAIL', 'POLICY_MISMATCH')
    if observed_head is None:
        fault('UNKNOWN', 'HEAD_UNCONFIRMED')
    elif observed_head != c['head']:
        fault('FAIL', 'HEAD_CHANGED')
    if not ci_required:
        ex = c.get('ci_exemption')
        if ex is None:
            fault('BLOCKED', 'CI_EXEMPTION_MISSING')
        elif any(ex[k] != val for k, val in (
            ('repository', c['repository']), ('ref', c['ref']),
            ('head', c['head']), ('object_id', c['object']['id'])
        )):
            fault('BLOCKED', 'CI_EXEMPTION_SCOPE')
    ci = obs.get('ci', 'NOT_TESTED')
    review = obs.get('review', 'NOT_TESTED')
    permissions = obs.get('permissions', 'NOT_TESTED')
    for label, value in (('CI', ci), ('REVIEW', review), ('PERMISSIONS', permissions)):
        if value == 'FAIL':
            reasons.append(label + '_FAIL')
    required = [status, review, permissions] + ([ci] if ci_required else [])
    out['contract_status'] = status
    out['ACCEPTANCE_STATUS'] = (
        'FAIL' if 'FAIL' in required else
        'BLOCKED' if ('BLOCKED' in required or
                       any(v in reasons for v in ('POLICY_UNCONFIRMED', 'HEAD_UNCONFIRMED'))) else
        'PASS' if all(v == 'PASS' for v in required) else 'PARTIAL')
    if not reasons:
        reasons.append('LEVEL1_GIT_ONLY')

    if 'archive_request' not in c:
        return out

    out['archive_applicability'] = {
        'required': True, 'reason': 'LEVEL1_EXPLICIT_ARCHIVE_REQUEST'
    }
    # Preserve any observed failure even when archive metadata is incomplete.
    out['CUSTODY_STATUS'] = obs.get('storage', 'NOT_TESTED')
    out['VERIFICATION_STATUS'] = aggregate([
        obs.get(k, 'NOT_TESTED') for k in ('readback','size','sha256','all_bytes')
    ])
    archive_failed = ('FAIL' in (out['CUSTODY_STATUS'], out['VERIFICATION_STATUS']))
    if invalid_archive_request:
        out['archive_status'] = 'FAIL' if archive_failed else 'BLOCKED'
        out['archive_contract_status'] = 'BLOCKED'
        out['archive_reason_codes'] = ['ARCHIVE_REQUEST_INVALID']
        return out
    # Missing archive parameters block ONLY the requested archive, not Git.
    missing = [key for key in REQUIRED_ARCHIVE if key not in c]
    missing += ['object.' + key for key in ('size','sha256') if key not in obj]
    if missing:
        out['archive_status'] = 'FAIL' if archive_failed else 'BLOCKED'
        out['archive_contract_status'] = 'BLOCKED'
        out['archive_reason_codes'] = ['ARCHIVE_INPUT_MISSING:' + key for key in missing]
        return out
    if approval is None:
        out['archive_status'] = 'FAIL' if archive_failed else 'BLOCKED'
        out['archive_contract_status'] = 'BLOCKED'
        out['archive_reason_codes'] = ['APPROVAL_MISSING']
        return out

    # Reuse Stage1-B's strict scope checker; a mechanical L2 check is
    # *not* a change to the declared Level 1 classification or real approval.
    extended = deepcopy(c)
    extended.pop('archive_request')
    extended['level'] = 2
    extended['risk'] = {k: risk[k] for k in ('confidential','destructive','strong_authenticity')}
    extended['risk']['rationale'] = risk['rationale']
    extended['ci_required'] = True
    extended.pop('ci_exemption', None)
    extended['delete_move_overwrite'] = c.get('delete_move_overwrite', 'prohibited')
    extended['required_checks'] = c.get('required_checks', ['size','sha256','all_bytes'])
    extended['extra_checks'] = c.get('extra_checks', [])
    extended['extra_decision'] = c.get('extra_decision', {
        'decision': 'not_required', 'rationale': 'No L3 decision asserted by this Level 1 adapter',
        'approved': False,
    })
    extended['sessions'] = c.get('sessions', {
        'separate_session': None, 'separate_execution': None,
        'separate_area': None, 'direct_retrieval': None,
        'human_independent': None, 'shared_owner': None,
    })
    extended['observations'] = {key: obs.get(key, 'NOT_TESTED') for key in
        ('storage','readback','size','sha256','all_bytes','bundle_restore','ci','review')}
    extended['observations']['ci'] = 'NOT_TESTED'  # not used in archive-only evaluation
    extended['observations']['review'] = 'NOT_TESTED'
    try:
        schema(extended)
    except (ValueError, TypeError, KeyError):
        out['archive_status'] = 'BLOCKED'
        out['archive_contract_status'] = 'BLOCKED'
        out['archive_reason_codes'] = ['ARCHIVE_SCHEMA_INVALID']
        return out
    result = validate_contract(extended, approval, now, observed_head, effective_policy)
    out['CUSTODY_STATUS'] = result['CUSTODY_STATUS']
    # Git documents have no bundle-restore requirement. Never promote an unrun check to PASS.
    verification = aggregate([extended['observations'][k] for k in
        ('readback', 'size', 'sha256', 'all_bytes')])
    out['VERIFICATION_STATUS'] = verification
    out['INDEPENDENCE_STATUS'] = result['INDEPENDENCE_STATUS']
    out['human_independence'] = result['human_independence']
    out['archive_contract_status'] = result['contract_status']
    out['archive_reason_codes'] = result['reason_codes']
    indep = ('PASS' if result['INDEPENDENCE_STATUS'] == 'PARTIAL'
             and c['audit_mode'] == 'SOLO_STANDARD' else result['INDEPENDENCE_STATUS'])
    checks = [result['contract_status'], result['CUSTODY_STATUS'],
              verification, indep]
    out['archive_status'] = (
        'FAIL' if 'FAIL' in checks else
        'BLOCKED' if 'BLOCKED' in checks or any(
            v in result['reason_codes'] for v in ('APPROVAL_UNVERIFIED','POLICY_UNCONFIRMED',
                'HEAD_UNCONFIRMED','CHECK_ADAPTER_UNKNOWN','ZIP_ADAPTER_NOT_IMPLEMENTED')
        ) else
        'PASS' if all(v == 'PASS' for v in checks) else 'PARTIAL')
    return out
