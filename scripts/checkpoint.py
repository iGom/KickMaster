#!/usr/bin/env python3
"""Build a manifest-verified, deterministic ZIP. Receipt is outside the archive."""
import argparse, hashlib, json, tempfile, zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
def digest(b):return hashlib.sha256(b).hexdigest()
def eligible(p):
    rel=p.relative_to(ROOT)
    return p.is_file() and not any(s in {'checkpoints','inputs','builds','__pycache__','.git'} for s in rel.parts) and rel.as_posix()!='manifests/SHA256SUMS'
def verify(path):
    with zipfile.ZipFile(path) as z:
        if z.testzip() is not None:raise ValueError('ZIP CRC failure')
        prefix=ROOT.name+'/'
        text=z.read(prefix+'manifests/SHA256SUMS').decode()
        listed={}
        for line in text.splitlines():
            h,n=line.split('  ',1)
            if digest(z.read(prefix+n))!=h:raise ValueError('Manifest mismatch: '+n)
            listed[prefix+n]=h
        actual=set(z.namelist())-{prefix+'manifests/SHA256SUMS'}
        if actual!=set(listed):raise ValueError('Manifest member set mismatch')
        for name in z.namelist():
            if Path(name).is_absolute() or '..' in Path(name).parts:raise ValueError('Unsafe archive path')
        samples=['README.md','RESUME.md','manifests/rom_identity.json','scripts/baseline.py']
        with tempfile.TemporaryDirectory() as td:
            for name in samples:
                z.extract(prefix+name,td)
                if digest((Path(td)/prefix/name).read_bytes())!=listed[prefix+name]:raise ValueError('Sample extraction mismatch')
    return {'archive':str(path.name),'sha256':digest(path.read_bytes()),'size_bytes':path.stat().st_size,
            'zip_crc_test':'PASS','manifest_verification':'PASS','manifest_file_count':len(listed),
            'sample_extraction':'PASS','sample_paths':samples,'latest_resume_present':True}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('stage',nargs='?');ap.add_argument('--verify',type=Path);a=ap.parse_args()
    if a.verify:print(json.dumps(verify(a.verify),indent=2));return
    if not a.stage:ap.error('stage is required')
    files=sorted([p for p in ROOT.rglob('*') if eligible(p)])
    manifest=ROOT/'manifests/SHA256SUMS'
    manifest.write_text(''.join(digest(p.read_bytes())+'  '+p.relative_to(ROOT).as_posix()+'\n' for p in files))
    dest=ROOT/'checkpoints';dest.mkdir(exist_ok=True)
    path=dest/f'kickmaster-ntscu-checkpoint-stage{a.stage}.zip'
    if path.exists():raise FileExistsError('Do not overwrite a previous checkpoint')
    with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in files+[manifest]:
            zi=zipfile.ZipInfo(ROOT.name+'/'+p.relative_to(ROOT).as_posix(),date_time=(2026,10,19,0,0,0));zi.compress_type=zipfile.ZIP_DEFLATED
            zi.external_attr=(p.stat().st_mode & 0xFFFF)<<16;z.writestr(zi,p.read_bytes())
    receipt=verify(path)
    path.with_suffix('.verification.json').write_text(json.dumps(receipt,indent=2)+'\n')
    path.with_suffix('.sha256').write_text(receipt['sha256']+'  '+path.name+'\n')
    print(json.dumps(receipt,indent=2))
if __name__=='__main__':main()
