"""Issue #14: opt-in Level 1 Git-only input. Pure trusted-record evaluation; no I/O."""
from copy import deepcopy

BASE = {'schema_version', 'repository', 'ref', 'head', 'tree', 'parents',
        'object', 'level', 'risk', 'policy', 'observations'}
OPTIONAL = {'attempt_id', 'ci_required', 'ci_exemption', 'archive_request',
            'approval_id', 'destination', 'operations', 'actor', 'classification',
            'retention_until', 'delete_move_overwrite', 'audit_mode',
            'required_checks', 'extra_checks', 'extra_decision', 'sessions'}
ARCHIVE = OPTIONAL - {'ci_required', 'ci_exemption', 'archive_request', 'attempt_id'}
GIT_OBS = ('ci', 'review', 'permissions')
CONTENT_OBS = ('readback', 'size', 'sha256', 'all_bytes')
ARCHIVE_OBS = {'storage', 'bundle_restore', *CONTENT_OBS}
GIT_DOCUMENT_CHECKS = {'size', 'sha256', 'all_bytes'}
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
    if __package__:
        from . import contract
    else:
        import contract

    reasons = []
    archive_requested = 'archive_request' in c
    applicability = (
        'LEVEL1_EXPLICIT_ARCHIVE_REQUEST' if archive_requested else 'LEVEL1_GIT_ONLY_NOT_APPLICABLE'
    )
    out = {
        'contract_status': 'FAIL', 'reason_codes': reasons,
        'CUSTODY_STATUS': 'NOT_TESTED', 'VERIFICATION_STATUS': 'NOT_TESTED',
        'INDEPENDENCE_STATUS': 'NOT_TESTED', 'ACCEPTANCE_STATUS': 'FAIL',
        'human_independence': 'UNKNOWN', 'production_permit': False,
        'archive_applicability': {'required': archive_requested, 'reason': applicability},
        'archive_status': 'NOT_TESTED', 'archive_contract_status': 'NOT_TESTED',
        'archive_reason_codes': [], 'GIT_PERMISSIONS_STATUS': 'NOT_TESTED',
    }

    obs = c.get('observations')
    if isinstance(obs, dict):
        if obs.get('storage') == 'FAIL':
            out['CUSTODY_STATUS'] = 'FAIL'
        if any(obs.get(key) == 'FAIL' for key in CONTENT_OBS):
            out['VERIFICATION_STATUS'] = 'FAIL'
    archive_failed = 'FAIL' in (out['CUSTODY_STATUS'], out['VERIFICATION_STATUS'])

    def block_archive(*codes):
        out['archive_status'] = 'FAIL' if archive_failed else 'BLOCKED'
        out['archive_contract_status'] = 'BLOCKED'
        out['archive_reason_codes'] = list(codes)
        return out

    try:
        if not BASE <= set(c) or not set(c) <= BASE | OPTIONAL:
            raise contract.Invalid('keys')
        if c['schema_version'] != '1' or c['level'] != 1:
            raise contract.Invalid('version/level')
        for k in ('repository', 'ref'):
            contract.string(c[k])
        for k in ('head', 'tree'):
            contract.hexid(c[k], 40)
        contract.strings(c['parents'])
        for parent in c['parents']:
            contract.hexid(parent, 40)
        obj = c['object']
        if not isinstance(obj, dict) or not {'id', 'kind'} <= set(obj) or not set(obj) <= {'id', 'kind', 'size', 'sha256'}:
            raise contract.Invalid('object keys')
        contract.string(obj['id'])
        if obj['kind'] != 'git-document':
            raise contract.Invalid('L1 object kind')
        risk = c['risk']
        if not isinstance(risk, dict) or set(risk) != set(RISK_FLAGS) | {'rationale'}:
            raise contract.Invalid('risk keys')
        contract.string(risk['rationale'])
        for k in RISK_FLAGS:
            contract.boolean(risk[k])
        contract.exact(c['policy'], 'version commit')
        contract.string(c['policy']['version'])
        contract.hexid(c['policy']['commit'], 40)
        contract.stamp(now)
        ci_required = c.get('ci_required', True)
        contract.boolean(ci_required)
        if 'ci_exemption' in c:
            ex = c['ci_exemption']
            contract.exact(ex, 'rationale repository ref head object_id')
            for k in ('rationale', 'repository', 'ref', 'object_id'):
                contract.string(ex[k])
            contract.hexid(ex['head'], 40)
            if ci_required:
                raise contract.Invalid('CI exemption conflicts with required CI')
        if not isinstance(obs, dict) or not set(obs) <= set(GIT_OBS) | ARCHIVE_OBS:
            raise contract.Invalid('observations keys')
        for key in GIT_OBS:
            contract.state(obs.get(key, 'NOT_TESTED'))
        if not archive_requested:
            if set(c) & ARCHIVE or set(obs) & ARCHIVE_OBS:
                raise contract.Invalid('archive intent must be explicit')
            if 'attempt_id' in c:
                contract.string(c['attempt_id'])
            if 'size' in obj and (type(obj['size']) is not int or obj['size'] <= 0):
                raise contract.Invalid('size')
            if 'sha256' in obj:
                contract.hexid(obj['sha256'], 64)
    except (ValueError, TypeError, KeyError):
        reasons.append('SCHEMA_INVALID')
        if archive_requested:
            return block_archive('GIT_INPUT_INVALID')
        return out

    status = 'PASS'
    def fault(s, reason):
        nonlocal status
        status = contract.aggregate([status, s])
        reasons.append(reason)

    if not risk['publicly_retrievable'] or risk['important_evidence'] or any(
        risk[k] for k in ('confidential', 'destructive', 'strong_authenticity')
    ):
        fault('FAIL', 'LEVEL_TOO_LOW')
        if not archive_requested:
            out['archive_applicability'] = {'required': True, 'reason': 'LEVEL2_3_REQUIRED'}
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
    out['GIT_PERMISSIONS_STATUS'] = permissions
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

    if not archive_requested:
        return out

    if 'LEVEL_TOO_LOW' in reasons:
        out.update(archive_status='FAIL', archive_contract_status='FAIL',
                   archive_reason_codes=['LEVEL_TOO_LOW'])
        return out

    try:
        request = c['archive_request']
        contract.exact(request, 'requested_by reason')
        if request['requested_by'] not in ('owner', 'case_contract'):
            raise contract.Invalid('archive requester')
        contract.string(request['reason'])
    except (ValueError, TypeError, KeyError):
        return block_archive('ARCHIVE_REQUEST_INVALID')

    try:
        for key in ARCHIVE_OBS:
            contract.state(obs.get(key, 'NOT_TESTED'))
    except ValueError:
        return block_archive('ARCHIVE_OBSERVATION_INVALID')
    out['CUSTODY_STATUS'] = obs.get('storage', 'NOT_TESTED')
    out['VERIFICATION_STATUS'] = contract.aggregate(
        [obs.get(key, 'NOT_TESTED') for key in CONTENT_OBS]
    )

    missing = [key for key in REQUIRED_ARCHIVE if key not in c]
    missing += ['object.' + key for key in ('size','sha256') if key not in obj]
    if missing:
        return block_archive(*('ARCHIVE_INPUT_MISSING:' + key for key in missing))
    if approval is None:
        return block_archive('APPROVAL_MISSING')
    if isinstance(approval, dict):
        missing = sorted(key for key in contract.APPROVAL_KEYS if approval.get(key) is None)
        if missing:
            return block_archive(*('APPROVAL_INPUT_MISSING:' + key for key in missing))

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
        contract.schema(extended)
    except (ValueError, TypeError, KeyError):
        return block_archive('ARCHIVE_SCHEMA_INVALID')
    result = contract.validate_contract(extended, approval, now, observed_head, effective_policy)
    verification = out['VERIFICATION_STATUS']
    unavailable_check = (
        set(extended['required_checks']) - GIT_DOCUMENT_CHECKS
        or extended['extra_checks']
        or extended['extra_decision']['decision'] != 'not_required'
    )
    if unavailable_check:
        result['reason_codes'].append('ARCHIVE_CHECK_UNAVAILABLE')
        if verification != 'FAIL':
            verification = 'NOT_TESTED'
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
        'BLOCKED' if 'BLOCKED' in checks or unavailable_check or any(
            v in result['reason_codes'] for v in ('APPROVAL_UNVERIFIED','POLICY_UNCONFIRMED',
                'HEAD_UNCONFIRMED','CHECK_ADAPTER_UNKNOWN','ZIP_ADAPTER_NOT_IMPLEMENTED')
        ) or any(code.startswith('ACL_') for code in result['reason_codes']) else
        'PASS' if all(v == 'PASS' for v in checks) else 'PARTIAL')
    return out
