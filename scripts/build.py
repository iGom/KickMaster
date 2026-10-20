#!/usr/bin/env python3
"""Build the existing scaffold and compare every byte. No source regeneration."""
import argparse,os,platform,shutil,subprocess
from baseline import ROOT,verified_rom,hashes,write_json,write_csv

def main():
    ap=argparse.ArgumentParser();ap.add_argument('rom');a=ap.parse_args();original,h=verified_rom(a.rom)
    dest=ROOT/'inputs';dest.mkdir(exist_ok=True);(dest/'original.nes').write_bytes(original)
    out=ROOT/'builds';out.mkdir(exist_ok=True)
    def exe(name):
        found=shutil.which(name)
        if found:return found
        bundled=ROOT/'tools/bin'/name
        if platform.system()!='Linux':raise RuntimeError(f'Install {name} on PATH; bundled tool is Linux x86_64')
        bundled.chmod(0o755);return str(bundled)
    ca65,ld65=exe('ca65'),exe('ld65')
    commands=[[ca65,'-g','-I','disassembly','-I','.', 'disassembly/main.asm','-o','builds/main.o','-l','builds/main.lst'],
       [ld65,'-C','disassembly/linker.cfg','builds/main.o','-o','builds/kickmaster-rebuilt.nes','--dbgfile','builds/kickmaster.dbg','-m','builds/kickmaster.map','-Ln','builds/kickmaster.lbl']]
    log=[]
    for command in commands:
        r=subprocess.run(command,cwd=ROOT,capture_output=True,text=True);log.append({'argv':command,'exit_code':r.returncode,'stdout':r.stdout,'stderr':r.stderr})
        if r.returncode:
            write_json(ROOT/'analysis/build_log.json',log);raise RuntimeError(r.stderr)
    rebuilt=(out/'kickmaster-rebuilt.nes').read_bytes()
    equal=rebuilt==original
    write_json(ROOT/'analysis/build_log.json',log)
    result={'status':'PASS' if equal else 'FAIL','comparison':'complete byte-for-byte comparison','requires_original_ROM':True,
            'original':hashes(original),'rebuilt':hashes(rebuilt),'binary_reconstruction_bytes':len(rebuilt) if equal else 0,
            'interpretation':'Input-dependent mixed assembly/incbin scaffold. Exact reconstruction does not establish semantic understanding.',
            'original_and_rebuilt_ROM_in_checkpoint':False}
    write_json(ROOT/'analysis/rebuild_verification.json',result)
    rows=[]
    for i in range(16):
        off=16+i*8192;rows.append({'bank':f'{i:02X}','identical':rebuilt[off:off+8192]==original[off:off+8192],**hashes(rebuilt[off:off+8192])})
    write_csv(ROOT/'analysis/rebuild_prg_banks.csv',rows)
    if not equal:raise AssertionError('Reconstructed ROM mismatch')
    # Preserve lightweight debugger/linker output; exclude actual rebuilt ROM from checkpoints.
    for name in ['kickmaster.dbg','kickmaster.map','kickmaster.lbl']:
        shutil.copyfile(out/name,ROOT/'disassembly/symbols'/name)
    print(result)
if __name__=='__main__':main()
