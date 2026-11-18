"""Stage 0 synthetic decision model. No filesystem, Git, network or storage adapter.
Input status labels represent synthetic observations, not authenticated evidence.
Real permits are unconditionally false. Never use this module as an operation gate.
"""
import json
import sys

STATES = {'PASS', 'FAIL', 'PARTIAL', 'BLOCKED', 'UNKNOWN', 'NOT_TESTED'}
CHECKS = ('git_trace change_control ci review original approval storage receipt retrieval size sha256 bytes crc manifest archive_safety acl retention bundle_restore object_integrity').split()
CONTEXT = ('session_separated execution_separated workspace_separated direct_storage independent_input human_independent credential_independent').split()
RISKS = ('confidential irrecoverable destructive strong_authenticity').split()
FLAGS = ('regenerated retroactive_pass level_downgrade claims_third_party').split()


def combine(values):
    if 'FAIL' in values: return 'FAIL'
    if 'BLOCKED' in values: return 'BLOCKED'
    other = set(values) - {'PASS'}
    return 'PASS' if not other else next(iter(other)) if len(other) == 1 else 'PARTIAL'


def shape(d):
    if type(d) is not dict: return False
    required = {'artifact_kind','level','risk','mode','checks','context','authorization','flags','ci_required','extra_checks','contract_extra_required'}
    if set(d) != required: return False
    if d['artifact_kind'] not in ('ordinary','evidence','zip','bundle'): return False
    if not (type(d['level']) is int and d['level'] in (1,2,3) or d['level'] == 'UNKNOWN'): return False
    if d['mode'] not in ('SOLO_STANDARD','STRICT_INDEPENDENT'): return False
    if type(d['ci_required']) is not bool: return False
    for name, keys, allowed in [('risk',RISKS,(True,False,None)),('context',CONTEXT,(True,False,None)),('flags',FLAGS,(True,False)),('authorization',['scope_matches','valid','adopted','individual'],(True,False))]:
        obj=d[name]
        if type(obj) is not dict or set(obj)!=set(keys): return False
        if any(not (type(v) is bool or v is None and None in allowed) for v in obj.values()): return False
    if type(d['checks']) is not dict or set(d['checks']) != set(CHECKS): return False
    if any(type(v) is not str or v not in STATES for v in d['checks'].values()): return False
    extras=d['extra_checks']; required_extras=d['contract_extra_required']
    if type(extras) is not dict or any(type(k) is not str or not k or not k.isascii() or not k.replace('_','').isalnum() or type(v) is not str or v not in STATES for k,v in extras.items()): return False
    if type(required_extras) is not list or any(type(k) is not str or not k or not k.isascii() or not k.replace('_','').isalnum() for k in required_extras): return False
    if len(required_extras)!=len(set(required_extras)): return False
    return True


def result(custody, verification, independence, acceptance, applicable, gates, reasons):
    return {'CUSTODY_STATUS':custody,'VERIFICATION_STATUS':verification,'INDEPENDENCE_STATUS':independence,'ACCEPTANCE_STATUS':acceptance,'applicability':dict.fromkeys(['custody','verification','independence'],applicable),'gate_eligibility':dict(zip('ABC',gates)),'permit':dict.fromkeys('ABC',False),'reason_codes':sorted(set(reasons))}


def evaluate(d):
    if not shape(d): return result('FAIL','FAIL','FAIL','FAIL',True,[False]*3,['SCHEMA_INVALID'])
    checks=d['checks']; reasons=[]
    level=d['level']
    if level in (1,2) and (any(v is True for v in d['risk'].values()) or d['artifact_kind']!='ordinary' and level<2):
        return result('UNKNOWN','UNKNOWN','UNKNOWN','FAIL',True,[False]*3,['LEVEL_TOO_LOW'])
    if level=='UNKNOWN' or any(v is None for v in d['risk'].values()):
        reasons=['LEVEL_UNKNOWN']
        custody_names=['original','approval','storage','receipt','acl','retention']
        verify_names=['retrieval','size','sha256','bytes']
        if d['artifact_kind']=='zip': verify_names += ['crc','manifest','archive_safety']
        if d['artifact_kind']=='bundle': verify_names += ['bundle_restore','object_integrity']
        relevant=custody_names+verify_names+['git_trace','change_control','review']+(['ci'] if d['ci_required'] else [])
        for name in relevant:
            if checks[name]=='FAIL': reasons.append('CHECK_'+name.upper()+'_FAIL')
        custody_fail=any(checks[x]=='FAIL' for x in custody_names)
        verify_fail=any(checks[x]=='FAIL' for x in verify_names)
        for key in d['contract_extra_required']:
            if d['extra_checks'].get(key)=='FAIL': verify_fail=True; reasons.append('CHECK_EXTRA_'+key+'_FAIL')
        flag_fail=False
        for flag,code in [('regenerated','ORIGINAL_SUBSTITUTED'),('retroactive_pass','HISTORY_REWRITTEN'),('level_downgrade','LEVEL_DOWNGRADE')]:
            if d['flags'][flag]: flag_fail=True; reasons.append(code)
        if d['flags']['regenerated']: custody_fail=True; verify_fail=True
        if d['flags']['claims_third_party'] and d['context']['human_independent'] is False: flag_fail=True; reasons.append('THIRD_PARTY_OVERCLAIM')
        failed=custody_fail or verify_fail or flag_fail or any(checks[x]=='FAIL' for x in relevant)
        return result('FAIL' if custody_fail else 'UNKNOWN','FAIL' if verify_fail else 'UNKNOWN','UNKNOWN','FAIL' if failed else 'PARTIAL',True,[False]*3,reasons)
    invalid=[]
    for flag,code in [('regenerated','ORIGINAL_SUBSTITUTED'),('retroactive_pass','HISTORY_REWRITTEN'),('level_downgrade','LEVEL_DOWNGRADE')]:
        if d['flags'][flag]: invalid.append(code)
    third_unverified=d['flags']['claims_third_party'] and d['context']['human_independent'] is None
    if d['flags']['claims_third_party'] and d['context']['human_independent'] is False: invalid.append('THIRD_PARTY_OVERCLAIM')
    reasons += invalid
    if third_unverified: reasons.append('THIRD_PARTY_UNVERIFIED')
    auth=[]
    auth_fields=[('adopted','POLICY_NOT_ADOPTED')] + ([] if level==1 else [('scope_matches','AUTH_SCOPE_MISMATCH'),('valid','AUTH_EXPIRED')])
    for key,code in auth_fields:
        if not d['authorization'][key]: auth.append(code)
    if level==3 and not d['authorization']['individual']: auth.append('INDIVIDUAL_APPROVAL_REQUIRED')
    reasons += auth
    global_states=(['FAIL'] if invalid else []) + (['BLOCKED'] if auth else []) + (['UNKNOWN'] if third_unverified else [])
    def check(names):
        vals=[]
        for name in names:
            v=checks[name]; vals.append(v)
            if v!='PASS': reasons.append('CHECK_'+name.upper()+'_'+v)
        return combine(vals)
    a_names=['git_trace','change_control'] + ([] if level==1 else ['original'])
    a=check(a_names)
    acceptance_parts=global_states + [a, check(['review'] + (['ci'] if d['ci_required'] else []))]
    extra_states=[]
    for key in d['contract_extra_required']:
        if key not in d['extra_checks']:
            reasons.append('EXTRA_CHECK_MISSING_'+key); extra_states.append('BLOCKED')
        else:
            v=d['extra_checks'][key]; extra_states.append(v)
            if v!='PASS': reasons.append('CHECK_EXTRA_'+key+'_'+v)
    extra=combine(extra_states)
    acceptance_parts.append(extra)
    if level==1:
        reasons.append('ARCHIVE_NOT_REQUIRED')
        acc=combine(acceptance_parts)
        if acc not in ('PASS','FAIL','BLOCKED'): acc='PARTIAL'
        return result('NOT_TESTED','NOT_TESTED','NOT_TESTED',acc,False,[a=='PASS' and not global_states,a=='PASS' and not global_states,acc=='PASS'],reasons)
    custody=combine([check(['original','approval','storage','receipt','acl','retention'])] + (['BLOCKED'] if any(x!='POLICY_NOT_ADOPTED' for x in auth) else []))
    v_names=['retrieval','size','sha256','bytes']
    if d['artifact_kind']=='zip': v_names += ['crc','manifest','archive_safety']
    if d['artifact_kind']=='bundle': v_names += ['bundle_restore','object_integrity']
    verify_parts=[check(v_names),extra]
    context=d['context']; independent=[]
    for key in ['session_separated','execution_separated','workspace_separated','direct_storage','independent_input']:
        value=context[key]
        if value is not True:
            status='UNKNOWN' if value is None else 'BLOCKED'
            code=key.upper()+('_UNKNOWN' if value is None else '_MISSING')
            if key=='direct_storage' and value is False: verify_parts.append('FAIL')
            else: verify_parts.append(status)
            independent.append(status); reasons.append(code)
    if d['flags']['regenerated']:
        custody='FAIL'; verify_parts.append('FAIL')
    verification=combine(verify_parts)
    if d['mode']=='SOLO_STANDARD':
        independence=combine(independent) if independent else 'LIMITED_SHARED_OWNER'
        reasons.append('SOLO_LIMITED')
    else:
        human=context['human_independent']
        if human is not True:
            independent.append('UNKNOWN' if human is None else 'BLOCKED')
            reasons.append('HUMAN_INDEPENDENT_UNKNOWN' if human is None else 'HUMAN_INDEPENDENT_MISSING')
        independence=combine(independent)
    if third_unverified: independence='UNKNOWN'
    mode_ok=independence in ('PASS','LIMITED_SHARED_OWNER')
    b= not global_states and a=='PASS' and custody=='PASS' and verification=='PASS' and mode_ok and extra=='PASS'
    acceptance_parts += [custody,verification,'PASS' if mode_ok else independence]
    acc=combine(acceptance_parts)
    if acc not in ('PASS','FAIL','BLOCKED'): acc='PARTIAL'
    return result(custody,verification,independence,acc,True,[a=='PASS' and not global_states,b,acc=='PASS'],reasons)

if __name__=='__main__':
    try: print(json.dumps(evaluate(json.load(sys.stdin)),sort_keys=True))
    except (ValueError,TypeError,KeyError):
        print(json.dumps(result('FAIL','FAIL','FAIL','FAIL',True,[False]*3,['SCHEMA_INVALID']),sort_keys=True))
