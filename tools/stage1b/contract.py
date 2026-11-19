"""Pure trusted-record validation. Does not authenticate approvals or authorize I/O."""
from datetime import datetime
import re
STATES={'PASS','FAIL','PARTIAL','BLOCKED','UNKNOWN','NOT_TESTED'}
APPROVAL_KEYS = frozenset(
    'id scope repositories object_ids classifications destinations actors operations '
    'valid_from valid_until retention_until delete_move_overwrite acl authorization_verified'.split()
)
class Invalid(ValueError): pass
def exact(o,keys):
    if not isinstance(o,dict) or set(o)!=set(keys.split()): raise Invalid('keys')
def string(x):
    if not isinstance(x,str) or not x.strip(): raise Invalid('string')
def strings(x):
    if not isinstance(x,list) or len(x)!=len(set(x)) or any(not isinstance(v,str) or not v.strip() for v in x): raise Invalid('list')
def stamp(x):
    string(x); d=datetime.fromisoformat(x)
    if d.tzinfo is None: raise Invalid('timezone')
    return d
def hexid(x,n):
    if not isinstance(x,str) or not re.fullmatch('[0-9a-f]{'+str(n)+'}',x): raise Invalid('hash')
def state(x):
    if not isinstance(x,str) or x not in STATES: raise Invalid('state')
def boolean(x):
    if type(x) is not bool: raise Invalid('bool')
def schema(c):
    exact(c,'schema_version attempt_id repository ref head tree parents object level risk policy approval_id destination operations actor classification retention_until delete_move_overwrite audit_mode required_checks extra_checks extra_decision observations ci_required sessions'+(' ci_exemption' if isinstance(c,dict) and 'ci_exemption' in c else ''))
    for k in ['attempt_id','repository','ref','approval_id','destination','actor','classification']:string(c[k])
    if c['schema_version']!='1' or type(c['level']) is not int or c['level'] not in (1,2,3):raise Invalid('version/level')
    for k in ['head','tree']:hexid(c[k],40)
    strings(c['parents'])
    for v in c['parents']:hexid(v,40)
    exact(c['object'],'id size sha256 kind');string(c['object']['id']);hexid(c['object']['sha256'],64)
    if type(c['object']['size']) is not int or c['object']['size']<=0:raise Invalid('size')
    if c['object']['kind'] not in ('bundle','zip','evidence','git-document'):raise Invalid('kind')
    exact(c['risk'],'confidential destructive strong_authenticity rationale');string(c['risk']['rationale'])
    for k in ['confidential','destructive','strong_authenticity']:boolean(c['risk'][k])
    exact(c['policy'],'version commit');string(c['policy']['version']);hexid(c['policy']['commit'],40)
    for k in ['operations','required_checks','extra_checks']:strings(c[k])
    if not c['operations'] or not set(c['operations'])<= {'create','read'}:raise Invalid('operations')
    stamp(c['retention_until'])
    if c['delete_move_overwrite']!='prohibited' or c['audit_mode'] not in ('SOLO_STANDARD','STRICT_INDEPENDENT'):raise Invalid('mode')
    d=c['extra_decision']; exact(d,'decision rationale approved'+(' covered_risks' if isinstance(d,dict) and 'covered_risks' in d else '')+(' approval_state' if isinstance(d,dict) and 'approval_state' in d else ''));string(d['rationale']);boolean(d['approved'])
    if 'approval_state' in d:
        if d['approval_state'] not in ('PASS','FAIL','UNKNOWN','NOT_TESTED'):raise Invalid('extra approval state')
        if d['approved'] != (d['approval_state']=='PASS'):raise Invalid('extra approval contradiction')
    if 'covered_risks' in d:
        if isinstance(d['covered_risks'],list) and all(isinstance(v,str) for v in d['covered_risks']) and len(d['covered_risks'])!=len(set(d['covered_risks'])):raise Invalid('risk coverage duplicate')
        strings(d['covered_risks'])
        if not set(d['covered_risks']) <= {'confidential','destructive','strong_authenticity'}:raise Invalid('risk coverage unknown')
        active={k for k in ['confidential','destructive','strong_authenticity'] if c['risk'][k]}
        if set(d['covered_risks'])-active:raise Invalid('risk coverage excess')
    if c['extra_decision']['decision'] not in ('required','not_required','UNKNOWN'):raise Invalid('extra')
    exact(c['observations'],'storage readback size sha256 all_bytes bundle_restore ci review')
    for v in c['observations'].values():state(v)
    boolean(c['ci_required'])
    if 'ci_exemption' in c:
        e=c['ci_exemption'];exact(e,'rationale repository ref head object_id')
        for key in ['rationale','repository','ref','object_id']:string(e[key])
        hexid(e['head'],40)
        if c['ci_required']:raise Invalid('CI exemption conflicts with required CI')
    exact(c['sessions'],'separate_session separate_execution separate_area direct_retrieval human_independent shared_owner')
    for v in c['sessions'].values():
        if v is not None and type(v) is not bool:raise Invalid('session')
def approval_schema(a):
    if not isinstance(a,dict) or set(a)!=APPROVAL_KEYS:raise Invalid('keys')
    string(a['id'])
    if a['scope'] not in ('case','reusable'):raise Invalid('scope')
    for k in ['repositories','object_ids','classifications','destinations','actors','operations']:strings(a[k])
    if a['scope']=='case' and (len(a['repositories'])!=1 or len(a['object_ids'])!=1):raise Invalid('case scope')
    for k in ['valid_from','valid_until','retention_until']:stamp(a[k])
    if stamp(a['valid_from'])>=stamp(a['valid_until']):raise Invalid('interval')
    state(a['acl']);boolean(a['authorization_verified'])
    if a['delete_move_overwrite']!='prohibited':raise Invalid('destruction policy')
def aggregate(values):
    """v0.2.0: known FAIL, then BLOCKED, singleton non-PASS, else PARTIAL."""
    if not values or any(v not in STATES for v in values):raise Invalid('aggregate status')
    if 'FAIL' in values:return 'FAIL'
    if 'BLOCKED' in values:return 'BLOCKED'
    pending={v for v in values if v!='PASS'}
    return 'PASS' if not pending else (next(iter(pending)) if len(pending)==1 else 'PARTIAL')
def validate_contract(c,a,now,observed_head=None,effective_policy=None):
    """Eligibility only; approval provenance must be checked outside this pure function."""
    reasons=[];out={'contract_status':'FAIL','reason_codes':reasons,'CUSTODY_STATUS':'UNKNOWN','VERIFICATION_STATUS':'UNKNOWN','INDEPENDENCE_STATUS':'UNKNOWN','ACCEPTANCE_STATUS':'FAIL','human_independence':'UNKNOWN','production_permit':False}
    # Issue #14: compact L1 uses a separate Git-only acceptance axis.
    # Legacy full contracts and all Level 2/3 records keep the prior evaluator.
    if __package__:
        from .level1 import is_compact_l1, validate_level1
    else:
        from level1 import is_compact_l1, validate_level1
    if is_compact_l1(c):
        return validate_level1(c, a, now, observed_head, effective_policy)
    # Retain separately typed observations even if another contract field is invalid.
    if isinstance(c,dict) and isinstance(c.get('observations'),dict):
        raw=c['observations']
        if isinstance(raw.get('storage'),str) and raw['storage'] in STATES:out['CUSTODY_STATUS']=raw['storage']
        vals=[raw.get(k) for k in ['readback','size','sha256','all_bytes','bundle_restore']]
        if all(isinstance(v,str) and v in STATES for v in vals):out['VERIFICATION_STATUS']=aggregate(vals)
        elif 'FAIL' in [v for v in vals if isinstance(v,str)]:out['VERIFICATION_STATUS']='FAIL'
    try:schema(c);n=stamp(now)
    except (ValueError,TypeError,KeyError) as exc:
        reasons.append('SCHEMA_INVALID')
        risk_errors={'risk coverage unknown':'RISK_UNKNOWN_NAME','risk coverage excess':'RISK_NOT_APPLICABLE','risk coverage duplicate':'RISK_DUPLICATE'}
        if str(exc) in risk_errors:reasons.append(risk_errors[str(exc)])
        return out
    o=c['observations'];s=c['sessions'];out['CUSTODY_STATUS']=o['storage']
    minlevel=3 if any(c['risk'][k] for k in ['confidential','destructive','strong_authenticity']) else (1 if c['object']['kind']=='git-document' else 2)
    archive_required=max(c['level'],minlevel)>=2
    out['archive_applicability']={'required':archive_required,'reason':'LEVEL2_3_REQUIRED' if archive_required else 'LEVEL1_GIT_ONLY_NOT_APPLICABLE'}
    out['archive_observations']=dict(o)
    out['VERIFICATION_STATUS']=aggregate([o[k] for k in ['readback','size','sha256','all_bytes','bundle_restore']])
    required=['separate_session','separate_execution','separate_area','direct_retrieval']
    if c['audit_mode']=='STRICT_INDEPENDENT':required+=['human_independent']
    out['INDEPENDENCE_STATUS']='BLOCKED' if any(s[k] is False for k in required) else ('UNKNOWN' if any(s[k] is None for k in required) else ('UNKNOWN' if s['shared_owner'] is None else ('PARTIAL' if s['shared_owner'] else 'PASS')))
    if c['audit_mode']=='STRICT_INDEPENDENT' and s['shared_owner'] is True:
        out['INDEPENDENCE_STATUS']='BLOCKED'
        reasons.append('STRICT_SHARED_OWNER')
    if not archive_required:
        for axis in ['CUSTODY_STATUS','VERIFICATION_STATUS','INDEPENDENCE_STATUS']:out[axis]='NOT_TESTED'
    out['human_independence']='LIMITED_SHARED_OWNER' if s['shared_owner'] else ('PASS' if s['human_independent'] is True else 'UNKNOWN')
    status='PASS'
    def fault(st,reason):
        nonlocal status
        status=aggregate([status,st]);reasons.append(reason)
    if effective_policy is None:fault('UNKNOWN','POLICY_UNCONFIRMED')
    elif not isinstance(effective_policy,dict) or c['policy']!=effective_policy:fault('FAIL','POLICY_MISMATCH')
    supported={'size','sha256','all_bytes','bundle_restore','zip_crc','zip_manifest','zip_paths'}
    if not set(c['required_checks'])<=supported:
        fault('UNKNOWN','CHECK_ADAPTER_UNKNOWN')
        if out['VERIFICATION_STATUS']!='FAIL':out['VERIFICATION_STATUS']='NOT_TESTED'
    if c['object']['kind']=='zip' and out['VERIFICATION_STATUS']!='FAIL':
        out['VERIFICATION_STATUS']='NOT_TESTED'
        reasons.append('ZIP_ADAPTER_NOT_IMPLEMENTED')
    if c['level']<minlevel:fault('FAIL','LEVEL_TOO_LOW')
    if observed_head is None:fault('UNKNOWN','HEAD_UNCONFIRMED')
    elif observed_head!=c['head']:fault('FAIL','HEAD_CHANGED')
    if c['level']>=2:
        requiredchecks={'size','sha256','all_bytes'}
        if c['object']['kind']=='bundle':requiredchecks.add('bundle_restore')
        if c['object']['kind']=='zip':requiredchecks.update(['zip_crc','zip_manifest','zip_paths'])
        if not requiredchecks<=set(c['required_checks']):fault('FAIL','CHECKS_MISSING')
        if a is None:fault('BLOCKED','APPROVAL_MISSING')
        else:
            try:approval_schema(a)
            except (ValueError,TypeError,KeyError):fault('FAIL','APPROVAL_SCHEMA_INVALID')
            else:
                if not a['authorization_verified']:fault('UNKNOWN','APPROVAL_UNVERIFIED')
                if c['approval_id']!=a['id']:fault('BLOCKED','APPROVAL_ID')
                if not stamp(a['valid_from'])<=n<stamp(a['valid_until']):fault('BLOCKED','APPROVAL_EXPIRED')
                for key,collection,code in [('repository','repositories','REPOSITORY'),('destination','destinations','DESTINATION'),('actor','actors','ACTOR'),('classification','classifications','CLASSIFICATION')]:
                    if c[key] not in a[collection]:fault('BLOCKED','SCOPE_'+code)
                if c['object']['id'] not in a['object_ids']:fault('BLOCKED','SCOPE_OBJECT')
                if not set(c['operations'])<=set(a['operations']):fault('BLOCKED','SCOPE_OPERATION')
                if stamp(c['retention_until'])<=n or stamp(a['retention_until'])<=n:fault('BLOCKED','RETENTION_EXPIRED')
                if stamp(c['retention_until'])>stamp(a['retention_until']):fault('BLOCKED','RETENTION_SCOPE')
                if a['acl']!='PASS':fault('BLOCKED' if a['acl']=='FAIL' else 'UNKNOWN','ACL_'+a['acl'])
    if not c['ci_required']:
        e=c.get('ci_exemption')
        if e is None:fault('BLOCKED','CI_EXEMPTION_MISSING')
        elif any(e[key]!=value for key,value in [('repository',c['repository']),('ref',c['ref']),('head',c['head']),('object_id',c['object']['id'])]):
            fault('BLOCKED','CI_EXEMPTION_SCOPE')
    if c['level']==3:
        d=c['extra_decision']
        risks={k for k in ['confidential','destructive','strong_authenticity'] if c['risk'][k]}
        approval_state=d.get('approval_state','PASS' if d['approved'] else 'FAIL')
        if approval_state!='PASS':
            fault(approval_state,{'FAIL':'EXTRA_APPROVAL_DENIED','UNKNOWN':'EXTRA_APPROVAL_UNKNOWN','NOT_TESTED':'EXTRA_APPROVAL_NOT_TESTED'}[approval_state])
            out['VERIFICATION_STATUS']=aggregate([out['VERIFICATION_STATUS'],approval_state])
        if not risks<=set(d.get('covered_risks',[])) or d['decision']=='UNKNOWN' or (d['decision']=='required' and not c['extra_checks']) or (d['decision']=='not_required' and c['extra_checks']):
            fault('UNKNOWN','EXTRA_CONTRACT_UNKNOWN')
            out['VERIFICATION_STATUS']=aggregate([out['VERIFICATION_STATUS'],'UNKNOWN'])
    if not reasons:reasons.append('LEVEL1_GIT_ONLY' if c['level']==1 else 'CONTRACT_VALID')
    out['contract_status']=status
    for axis,key in [('CUSTODY','storage'),('VERIFICATION','sha256'),('CI','ci'),('REVIEW','review')]:
        if o[key]=='FAIL':reasons.append(axis+'_FAIL')
    # Preserve evidence failures on their axes. Contract errors never erase observed facts.
    acceptance=[status,o['review']]
    if c['level']==3 and c['extra_checks']:acceptance.append('NOT_TESTED') # extra execution evidence is not implemented
    if c['ci_required']:acceptance.append(o['ci'])
    if c['level']>=2:acceptance += [out['CUSTODY_STATUS'],out['VERIFICATION_STATUS'], 'PASS' if out['INDEPENDENCE_STATUS']=='PARTIAL' and c['audit_mode']=='SOLO_STANDARD' else out['INDEPENDENCE_STATUS']]
    blockers={'POLICY_UNCONFIRMED','APPROVAL_UNVERIFIED','HEAD_UNCONFIRMED',
              'CHECK_ADAPTER_UNKNOWN','EXTRA_CONTRACT_UNKNOWN','EXTRA_APPROVAL_UNKNOWN',
              'ZIP_ADAPTER_NOT_IMPLEMENTED'}
    blocked=(status=='BLOCKED' or (archive_required and out['INDEPENDENCE_STATUS']=='BLOCKED')
             or any(code in blockers or code.startswith('ACL_') for code in reasons))
    out['ACCEPTANCE_STATUS']=('FAIL' if 'FAIL' in acceptance else
                              'BLOCKED' if blocked or 'BLOCKED' in acceptance else
                              'PASS' if all(x=='PASS' for x in acceptance) else 'PARTIAL')
    return out

def validate_manifest(m):
    exact(m,'schema_version files');
    if m['schema_version']!='1' or not isinstance(m['files'],list) or not m['files']:raise Invalid('manifest')
    seen=set()
    for f in m['files']:
        exact(f,'path size sha256');p=f['path'];string(p)
        if p.startswith('/') or '\\' in p or ':' in p or any(x in ('','..','.') for x in p.split('/')) or p in seen:raise Invalid('unsafe/duplicate path')
        seen.add(p);hexid(f['sha256'],64)
        if type(f['size']) is not int or f['size']<0:raise Invalid('size')
    return True

def validate_receipt(r,c):
    exact(r,'schema_version attempt_id object_id sha256 size destination stored_at operation storage_status readback_status')
    if r['schema_version']!='1':raise Invalid('receipt version')
    for k in ['storage_status','readback_status']:state(r[k])
    stamp(r['stored_at'])
    if r['operation']!='create' or r['attempt_id']!=c['attempt_id'] or r['destination']!=c['destination'] or r['object_id']!=c['object']['id'] or r['sha256']!=c['object']['sha256'] or type(r['size']) is not int or r['size']!=c['object']['size']:raise Invalid('receipt identity')
    return True


def claim_attempt(ledger_path, attempt_id):
    """Create-only local receipt reservation. No resume/overwrite; interrupted claims remain."""
    import pathlib, json
    if not isinstance(attempt_id,str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,100}',attempt_id):raise Invalid('attempt id')
    root=pathlib.Path(ledger_path)
    if not root.is_dir() or root.is_symlink():raise Invalid('ledger')
    path=root/(attempt_id+'.json')
    try:
        with path.open('x',encoding='utf-8') as f:json.dump({'attempt_id':attempt_id,'state':'PENDING','production_permit':False},f)
    except FileExistsError:raise Invalid('ATTEMPT_ALREADY_EXISTS')
    return path
