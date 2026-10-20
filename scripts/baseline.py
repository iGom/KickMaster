#!/usr/bin/env python3
"""Identify the supplied image; offsets use half-open ranges. Python stdlib only."""
import argparse, csv, hashlib, json, platform, shutil, subprocess, sys, zlib
from pathlib import Path

EXPECTED_SHA256 = '00ad4a0c6612319bb9f918ca36d6e93b4e5d996716c0570a3ec92bd60533881b'
ROOT = Path(__file__).resolve().parents[1]

def hashes(data):
    return {'size':len(data), 'sha256':hashlib.sha256(data).hexdigest(),
            'sha1':hashlib.sha1(data).hexdigest(), 'crc32':f'{zlib.crc32(data):08X}'}

def parse(data):
    if len(data)<16 or data[:4]!=b'NES\x1a': raise ValueError('Invalid/truncated NES header')
    h=data[:16]; nes2=(h[7]&12)==8
    def romsize(lo, hi, unit):
        return (2**(lo>>2))*((lo&3)*2+1) if hi==15 else ((hi<<8)|lo)*unit
    p=romsize(h[4],h[9]&15,16384) if nes2 else h[4]*16384
    c=romsize(h[5],h[9]>>4,8192) if nes2 else h[5]*8192
    trainer=512 if h[6]&4 else 0
    pstart=16+trainer; cstart=pstart+p; end=cstart+c
    if len(data)<end: raise ValueError('Truncated ROM payload')
    ram=lambda n: (64<<n) if n else 0
    return {'format':'NES 2.0' if nes2 else 'iNES (legacy)',
        'header_hex':h.hex(' '),'mapper':(h[6]>>4)|(h[7]&240)|((h[8]&15)<<8 if nes2 else 0),
        'submapper':h[8]>>4 if nes2 else None,'console_type':h[7]&3,
        'header_mirroring':'four-screen' if h[6]&8 else ('vertical' if h[6]&1 else 'horizontal'),
        'mirroring_caveat':'MMC3 A000 controls actual nametable mirroring; the header bit is not a game-wide invariant.',
        'battery':bool(h[6]&2),'trainer_size':trainer,'prg_start':pstart,'prg_size':p,
        'chr_start':cstart,'chr_size':c,'expected_size':end,'trailing_size':len(data)-end,
        'prg_ram':ram(h[10]&15) if nes2 else None,'prg_nvram':ram(h[10]>>4) if nes2 else None,
        'chr_ram':ram(h[11]&15) if nes2 else None,'chr_nvram':ram(h[11]>>4) if nes2 else None,
        'timing':h[12]&3 if nes2 else None,'misc_rom_count':h[14]&3 if nes2 else None,
        'default_expansion_device':h[15]&63 if nes2 else None}

def verified_rom(path):
    b=Path(path).read_bytes()
    if hashes(b)['sha256']!=EXPECTED_SHA256: raise ValueError('Input SHA-256 differs from project identity; no substitution allowed')
    return b,parse(b)

def write_json(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(obj,indent=2)+'\n')

def write_csv(path,rows,fields=None):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields or list(rows[0]));w.writeheader();w.writerows(rows)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('rom');args=ap.parse_args()
    b,h=verified_rom(args.rom); p=b[h['prg_start']:h['chr_start']]; c=b[h['chr_start']:h['expected_size']]
    reference={'source':'https://nescartdb.com/profile/view/2564/kick-master',
       'prg_crc32':'D88D48D7','chr_crc32':'5B03178D','payload_crc32':'5104833E'}
    ident={'original_filename':Path(args.rom).name,'file':hashes(b),'header':h,'prg':hashes(p),'chr':hashes(c),
       'payload':hashes(p+c),'published_reference':reference,
       'reference_crc32_match':hashes(p)['crc32']==reference['prg_crc32'] and hashes(c)['crc32']==reference['chr_crc32'] and hashes(p+c)['crc32']==reference['payload_crc32'],
       'original_rom_in_checkpoint':False,'note':'CRC32 agreement supports dump identity; no independent published SHA-256 was supplied.'}
    write_json(ROOT/'manifests/rom_identity.json',ident)
    banks=[]
    for typ,data,size,start in [('PRG',p,8192,h['prg_start']),('CHR',c,1024,h['chr_start'])]:
        for i in range(len(data)//size):
            row={'type':typ,'bank':f'{i:02X}','bank_size':size,'payload_offset':f'0x{i*size:06X}',
                'file_start':f'0x{start+i*size:06X}','file_end_exclusive':f'0x{start+(i+1)*size:06X}',**hashes(data[i*size:(i+1)*size])}
            banks.append(row)
    write_csv(ROOT/'maps/rom/banks.csv',banks)
    vectors=[]
    for i,name in enumerate(['NMI','RESET','IRQ_BRK']):
        po=len(p)-6+i*2;target=int.from_bytes(p[po:po+2],'little')
        vectors.append({'name':name,'vector_bank':'0F','vector_cpu':f'0x{0xFFFA+i*2:04X}',
            'vector_bank_offset':f'0x{0x1FFA+i*2:04X}','vector_prg_offset':f'0x{po:06X}',
            'vector_file_offset':f'0x{h["prg_start"]+po:06X}','target_bank':'0F' if target>=0xE000 else 'UNRESOLVED',
            'target_cpu':f'0x{target:04X}','target_bank_offset':f'0x{target-0xE000:04X}' if target>=0xE000 else '',
            'target_prg_offset':f'0x{15*8192+target-0xE000:06X}' if target>=0xE000 else '',
            'target_file_offset':f'0x{h["prg_start"]+15*8192+target-0xE000:06X}' if target>=0xE000 else '',
            'mapping_condition':'last 8 KiB bank fixed at E000-FFFF under MMC3'})
    write_csv(ROOT/'analysis/vectors.csv',vectors)
    tools={'python':sys.version,'platform':platform.platform(),'tools':{}}
    for n,argv in {'java':['-version'],'node':['--version'],'git':['--version'],'gcc':['--version'],
                   'pdftotext':['-v'],'pdftoppm':['-v'],'tesseract':['--version'],
                   'ca65':['--version'],'ld65':['--version'],'da65':['--version'],
                   'ghidra':[],'analyzeHeadless':[],'Mesen':[],'mesen':[],'fceux':[]}.items():
        exe=shutil.which(n);out={'path':exe,'status':'available' if exe else 'not_on_PATH'}
        if exe and argv:
            r=subprocess.run([exe]+argv,capture_output=True,text=True)
            out['version_first_line']=(r.stdout+r.stderr).splitlines()[0]
        tools['tools'][n]=out
    write_json(ROOT/'manifests/toolchain.json',tools)
    print(json.dumps({'identity':ident,'vectors':vectors},indent=2))

if __name__=='__main__':main()
