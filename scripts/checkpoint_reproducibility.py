#!/usr/bin/env python3
"""Fully extract a checkpoint into a fresh directory and build its saved sources once.

Does not regenerate sources or execute any CPU suite. Original ROM remains external.
"""
import argparse,hashlib,json,platform,subprocess,sys,zipfile
from datetime import datetime,timezone
from pathlib import Path

def sha(data):return hashlib.sha256(data).hexdigest()
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('archive',type=Path);ap.add_argument('rom',type=Path)
    ap.add_argument('destination',type=Path);ap.add_argument('report',type=Path)
    ap.add_argument('--stage',required=True);a=ap.parse_args()
    archive=a.archive.resolve();rom=a.rom.resolve();destination=a.destination.resolve()
    assert not destination.exists(),'Use a new destination; never overwrite a prior clean extraction.'
    expected=rom.read_bytes();assert sha(expected)=='00ad4a0c6612319bb9f918ca36d6e93b4e5d996716c0570a3ec92bd60533881b'
    prefix='kickmaster-ntscu-re/';manifest_name=prefix+'manifests/SHA256SUMS'
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        names=z.namelist();assert len(names)==len(set(names))
        for name in names:
            p=Path(name);assert name.startswith(prefix) and not p.is_absolute() and '..' not in p.parts
            assert (z.getinfo(name).external_attr>>16)&0o170000 != 0o120000,'Symlink not permitted'
        pairs=[line.split('  ',1) for line in z.read(manifest_name).decode().splitlines()]
        listed={prefix+name:h for h,name in pairs};assert len(listed)==len(pairs)
        assert set(names)==set(listed)|{manifest_name}
        for name,h in listed.items():assert sha(z.read(name))==h,name
        destination.mkdir(parents=True)
        z.extractall(destination)
        for name,h in listed.items():assert sha((destination/name).read_bytes())==h,name
    root=destination/prefix.rstrip('/')
    command=[sys.executable,'scripts/build.py',str(rom)]
    process=subprocess.run(command,cwd=root,capture_output=True,text=True)
    assert process.returncode==0,process.stderr
    rebuilt=(root/'builds/kickmaster-rebuilt.nes').read_bytes();assert rebuilt==expected
    versions=[]
    for executable in ('ca65','ld65'):
        path=root/'tools/bin'/executable
        r=subprocess.run([str(path),'--version'],capture_output=True,text=True)
        versions.append({'executable':str(path),'version_exit_code':r.returncode,'version':(r.stdout+r.stderr).strip()})
    result={'schema':'kickmaster-checkpoint-reproducibility/v1','stage':a.stage,
      'verified_utc':datetime.now(timezone.utc).isoformat(),'archive':archive.name,
      'archive_sha256':sha(archive.read_bytes()),'fresh_extraction_directory':str(root),
      'zip_crc':'PASS','complete_archive_manifest':'PASS','full_extracted_manifest':'PASS',
      'manifest_file_count':len(listed),'build_performed_this_session':True,'command':command,
      'working_directory':str(root),'exit_code':process.returncode,'source_regeneration_performed':False,
      'previous_cpu_suites_rerun':False,'any_cpu_suite_rerun':False,'python':platform.python_version(),
      'tool_versions':versions,'build_commands':json.loads((root/'analysis/build_log.json').read_text()),
      'rebuild_verification':json.loads((root/'analysis/rebuild_verification.json').read_text()),
      'full_byte_comparison':'PASS','compared_bytes':len(expected),'rom_required_separately':True,
      'native_NES_emulator_validation':'NOT_TESTED',
      'reason':'Required clean-extraction gate for this new checkpoint; build uses only saved assembly plus exact external ROM.'}
    a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('stage','archive_sha256','manifest_file_count','full_extracted_manifest','full_byte_comparison','compared_bytes')},indent=2))
if __name__=='__main__':main()
