import os, asyncio, re, io, traceback, sys
ALT = os.environ.get('AW_SHELL', '')
def log(m):
    print(m, flush=True)
def patch():
    import aardwolf
    p = os.path.join(os.path.dirname(aardwolf.__file__), 'connection.py')
    s = io.open(p, encoding='utf-8', errors='ignore').read()
    if 'AW_SHELL' in s:
        return 'already'
    pat = re.compile(r"(?P<i>[ \t]*)info\.AlternateShell\s*=\s*''[ \t]*")
    m = pat.search(s)
    if not m:
        return 'pattern-missing'
    ind = m.group('i')
    rep = (ind + "info.AlternateShell = __import__('os').environ.get('AW_SHELL','')\n"
           + ind + "info.WorkingDir = __import__('os').environ.get('AW_WD','')\n")
    io.open(p, 'w', encoding='utf-8').write(s[:m.start()] + rep + s[m.end():])
    return 'patched'
async def main():
    from aardwolf.commons.target import RDPTarget
    from aardwolf.commons.iosettings import RDPIOSettings
    from aardwolf.commons.factory import RDPConnectionFactory
    from asyauth.common.credentials.ntlm import NTLMCredential
    from asyauth.common.constants import asyauthSecret
    cred = NTLMCredential(os.environ['RDP_PASS'], 'Administrator', '', asyauthSecret.PASSWORD)
    target = RDPTarget(ip='212.43.149.118')
    st = RDPIOSettings()
    conn = RDPConnectionFactory(st, target, cred).get_connection(st)
    ok, err = await conn.connect()
    log('connect ok=%s err=%s' % (ok, err))
    if not ok:
        return
    for _ in range(20):
        await asyncio.sleep(2)
        try:
            while not conn.ext_in_queue.empty():
                conn.ext_in_queue.get_nowait()
        except Exception:
            pass
    try:
        await asyncio.wait_for(conn.terminate(), timeout=6)
    except Exception:
        pass
    log('done')
log('patch=' + patch())
try:
    asyncio.run(main())
except Exception:
    log('EXC ' + traceback.format_exc())
