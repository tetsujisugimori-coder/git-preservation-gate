"""Windows synthetic process gate. No production permit; owned Job only."""
import ctypes as C
from ctypes import wintypes as W
import os, sys, time, json, pathlib, subprocess, datetime, math

class BasicLimit(C.Structure):
    _fields_=[('PerProcessUserTimeLimit',C.c_longlong),('PerJobUserTimeLimit',C.c_longlong),('LimitFlags',W.DWORD),('MinimumWorkingSetSize',C.c_size_t),('MaximumWorkingSetSize',C.c_size_t),('ActiveProcessLimit',W.DWORD),('Affinity',C.c_size_t),('PriorityClass',W.DWORD),('SchedulingClass',W.DWORD)]
class IOCounters(C.Structure):
    _fields_=[(n,C.c_ulonglong) for n in ['ReadOperationCount','WriteOperationCount','OtherOperationCount','ReadTransferCount','WriteTransferCount','OtherTransferCount']]
class Extended(C.Structure):
    _fields_=[('BasicLimitInformation',BasicLimit),('IoInfo',IOCounters),('ProcessMemoryLimit',C.c_size_t),('JobMemoryLimit',C.c_size_t),('PeakProcessMemoryUsed',C.c_size_t),('PeakJobMemoryUsed',C.c_size_t)]
class Accounting(C.Structure):
    _fields_=[(n,C.c_longlong) for n in ['TotalUserTime','TotalKernelTime','ThisPeriodTotalUserTime','ThisPeriodTotalKernelTime']]+[(n,W.DWORD) for n in ['TotalPageFaultCount','TotalProcesses','ActiveProcesses','TotalTerminatedProcesses']]

def unassigned_stop_state(wait_result):
    return 'UNASSIGNED_CHILD_STOPPED' if wait_result==0 else 'UNASSIGNED_CHILD_STOP_UNCONFIRMED'

def run(command, root, command_timeout=5., total_timeout=10., stop_wait=2., retry=0, fault=None):
    """One attempt, new evidence directory. fault only for safe synthetic tests."""
    if os.name!='nt': raise RuntimeError('WINDOWS_REQUIRED')
    if retry != 0: raise ValueError('RETRY_NOT_IMPLEMENTED')
    for x in [command_timeout,total_timeout,stop_wait]:
        if isinstance(x,bool) or not isinstance(x,(int,float)) or not math.isfinite(x) or x<=0 or x>120: raise ValueError('INVALID_BOUND')
    if not isinstance(command,list) or not command or not all(isinstance(v,str) and v for v in command): raise ValueError('INVALID_COMMAND')
    if fault not in [None,'query','terminate']: raise ValueError('INVALID_FAULT')
    import _winapi as win
    root=pathlib.Path(root);root.mkdir(parents=True,exist_ok=False)
    r={'command':command,'started_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'UNKNOWN','reason':'NOT_FINISHED','process_state':'NOT_STARTED','production_permit':False,'retry':0,'command_timeout':command_timeout,'total_timeout':total_timeout,'stop_wait':stop_wait,'fault':fault,'observations':[]}
    (root/'started.json').write_text(json.dumps(r,indent=2))
    t=time.monotonic(); deadline=t+min(command_timeout,total_timeout)
    k=C.WinDLL('kernel32',use_last_error=True)
    k.CreateJobObjectW.argtypes=[C.c_void_p,W.LPCWSTR];k.CreateJobObjectW.restype=W.HANDLE
    k.SetInformationJobObject.argtypes=[W.HANDLE,C.c_int,C.c_void_p,W.DWORD];k.SetInformationJobObject.restype=W.BOOL
    k.AssignProcessToJobObject.argtypes=[W.HANDLE,W.HANDLE];k.AssignProcessToJobObject.restype=W.BOOL
    k.QueryInformationJobObject.argtypes=[W.HANDLE,C.c_int,C.c_void_p,W.DWORD,C.c_void_p];k.QueryInformationJobObject.restype=W.BOOL
    k.TerminateJobObject.argtypes=[W.HANDLE,W.UINT];k.TerminateJobObject.restype=W.BOOL
    k.ResumeThread.argtypes=[W.HANDLE];k.ResumeThread.restype=W.DWORD
    k.CloseHandle.argtypes=[W.HANDLE];k.CloseHandle.restype=W.BOOL
    job=None; hp=ht=None; assigned=False
    def ck(v):
        if not v: raise C.WinError(C.get_last_error())
        return v
    def account():
        if fault=='query': raise OSError('INJECTED_QUERY_FAILURE')
        a=Accounting();ck(k.QueryInformationJobObject(job,1,C.byref(a),C.sizeof(a),None))
        r['observations'].append({'elapsed':time.monotonic()-t,'active':a.ActiveProcesses,'total':a.TotalProcesses,'terminated':a.TotalTerminatedProcesses})
        return a.ActiveProcesses
    try:
        job=ck(k.CreateJobObjectW(None,None));lim=Extended();lim.BasicLimitInformation.LimitFlags=0x2000
        ck(k.SetInformationJobObject(job,9,C.byref(lim),C.sizeof(lim)))
        # Files stay on disk even if controller stops; handles explicitly inherited.
        with open(root/'stdout.bin','xb') as out,open(root/'stderr.bin','xb') as err,open(os.devnull,'rb') as inp:
            import msvcrt
            handles=[msvcrt.get_osfhandle(f.fileno()) for f in [inp,out,err]]
            for h in handles:os.set_handle_inheritable(h,True)
            si=subprocess.STARTUPINFO();si.dwFlags=0x100;si.hStdInput,si.hStdOutput,si.hStdError=handles;si.lpAttributeList={'handle_list':handles}
            try:
                hp,ht,pid,tid=win.CreateProcess(None,subprocess.list2cmdline(command),None,None,True,0x4|0x08000000,None,None,si)
            finally:
                for h in handles:os.set_handle_inheritable(h,False)
            r['pid']=pid;r['process_state']='SUSPENDED'
            ck(k.AssignProcessToJobObject(job,hp));assigned=True
            if k.ResumeThread(ht)==0xffffffff:raise C.WinError(C.get_last_error())
            r['process_state']='RUNNING_IN_OWN_JOB'
            while True:
                active=account()
                current_exit=win.GetExitCodeProcess(hp)
                if current_exit!=259:r['observed_parent_exit']=current_exit
                if active==0:
                    r['exit_code']=win.GetExitCodeProcess(hp);r['process_state']='JOB_EMPTY'
                    r['status']='PASS' if r['exit_code']==0 else 'FAIL';r['reason']='OK' if r['exit_code']==0 else 'COMMAND_NONZERO';break
                if time.monotonic()>=deadline:
                    r['status']='FAIL' if r.get('observed_parent_exit',0)!=0 else 'UNKNOWN';r['reason']='COMMAND_NONZERO_WITH_TIMEOUT' if r['status']=='FAIL' else 'TIMEOUT'
                    if fault=='terminate':raise OSError('INJECTED_TERMINATE_FAILURE')
                    ck(k.TerminateJobObject(job,124));until=time.monotonic()+stop_wait
                    while time.monotonic()<until:
                        if account()==0:r['process_state']='JOB_EMPTY_AFTER_TERMINATE';break
                        time.sleep(.01)
                    if r['process_state']!='JOB_EMPTY_AFTER_TERMINATE':r['reason']='STOP_UNCONFIRMED'
                    r['exit_code']=win.GetExitCodeProcess(hp);break
                time.sleep(.01)
    except Exception as e:
        r['error']=repr(e);r['status']='BLOCKED' if hp is None else ('FAIL' if r.get('observed_parent_exit',0)!=0 else 'UNKNOWN');r['reason']='SPAWN_OR_SETUP_FAILED' if hp is None else 'CONTROL_FAILED'
        # Never terminate unrelated PIDs. Suspended unassigned child is ours.
        if hp is not None and not assigned:
            try:win.TerminateProcess(hp,125);wait_result=win.WaitForSingleObject(hp,int(stop_wait*1000));r['cleanup_wait_result']=wait_result;r['process_state']=unassigned_stop_state(wait_result)
            except Exception as cleanup:r['cleanup_error']=repr(cleanup)
    finally:
        if job:k.CloseHandle(job) # kill-on-close is fallback, NOT observed-empty proof
        if ht:win.CloseHandle(ht)
        if hp:win.CloseHandle(hp)
        r['elapsed']=time.monotonic()-t;r['ended_at']=datetime.datetime.now(datetime.timezone.utc).isoformat()
        for n in ['stdout','stderr']:
            f=root/(n+'.bin');r[n]=f.read_bytes().decode('utf8',errors='replace') if f.exists() else None
        (root/'result.json').write_text(json.dumps(r,indent=2))
    return r

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--root',required=True);p.add_argument('--timeout',type=float,default=5);p.add_argument('command',nargs=argparse.REMAINDER);a=p.parse_args()
    result=run(a.command,a.root,a.timeout);print(json.dumps(result));sys.exit(0 if result['status']=='PASS' else 1)
