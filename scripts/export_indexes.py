#!/usr/bin/env python3
"""Regenerate integration indexes from reviewed ROM ranges and the manually maintained RAM map."""
import csv,re,shutil
from baseline import ROOT,write_csv,write_json

def read(path):
    with (ROOT/path).open() as f:return list(csv.DictReader(f))
def main():
    ranges=read('analysis/reviewed_ranges.csv');ram=read('maps/ram/ram_map.csv')
    symbols=[]
    for x in ranges:
        symbols.append({'name':x['symbol'],'type':x['classification'],**{k:x[k] for k in ['bank','cpu','bank_offset','prg_offset','file_offset','mapping_condition','size','description','status']},'evidence':x['id']})
    for x in ram:
        symbols.append({'name':x['name'],'type':'ram','bank':'','cpu':x['address'],'bank_offset':'','prg_offset':'','file_offset':'','mapping_condition':'internal RAM; state-specific role','size':x['size'],'description':x['description'],'status':x['status'],'evidence':x['accessing_routines']})
    write_csv(ROOT/'analysis/symbols.csv',symbols)
    write_csv(ROOT/'analysis/data_structures.csv',[x for x in symbols if x['type']=='data' or x['type']=='ram' and int(x['size'])>1])
    lines=[]
    for x in symbols:
        typ='NesInternalRam' if x['type']=='ram' else 'NesPrgRom';adr=int(x['cpu'] if x['type']=='ram' else x['prg_offset'],16)
        lines.append(f'{typ}:{adr:X}:{x["name"]}:{x["evidence"]}; {x["description"]}')
    (ROOT/'MesenCE/kickmaster.mlb').write_text('\n'.join(lines)+'\n')
    for line in lines:
        a=line.split(':',3);assert len(a)==4 and a[0] in ('NesPrgRom','NesInternalRam')
        assert re.fullmatch('[0-9A-F]+',a[1]) and re.fullmatch('[A-Za-z_][A-Za-z0-9_]*',a[2])
    write_json(ROOT/'MesenCE/format_check.json',{'rows_checked':len(lines),'subset_syntax_check':'PASS','actual_MesenCE_import':'NOT_TESTED','source_commit':'4b8a196e299b3de297b204fd1208d2981562c89b','source_file':'UI/Debugger/Labels/CodeLabel.cs','ROM_address_domain':'PRG offsets excluding 16-byte header; not CPU addresses'})
    shutil.copyfile(ROOT/'analysis/symbols.csv',ROOT/'ghidra/symbols.csv')
    (ROOT/'disassembly/symbols/ram.inc').write_text('; RAM symbols; see maps/ram/ram_map.csv for evidence.\n'+'\n'.join(f'{x["name"]} = ${int(x["address"],16):04X}' for x in ram)+'\n')
    classification=[{'file_start':0,'file_end_exclusive':16,'size':16,'type':'HEADER','bank':'','status':'FILE_STRUCTURE_VERIFIED','evidence':'rom_identity.json'}]
    for bank in range(16):
        cursor=16+bank*8192;end=cursor+8192
        def append(lo,hi,status,evidence):
            if hi>lo:classification.append({'file_start':lo,'file_end_exclusive':hi,'size':hi-lo,'type':'PRG','bank':f'{bank:02X}','status':status,'evidence':evidence})
        for x in sorted([x for x in ranges if int(x['bank'],16)==bank],key=lambda x:int(x['file_offset'],16)):
            lo=int(x['file_offset'],16);hi=lo+int(x['size']);assert cursor<=lo<=hi<=end
            append(cursor,lo,'UNREVIEWED','');append(lo,hi,'STATIC_REVIEWED_'+x['classification'].upper(),x['id']);cursor=hi
        append(cursor,end,'UNREVIEWED','')
    classification.append({'file_start':0x20010,'file_end_exclusive':0x40010,'size':0x20000,'type':'CHR','bank':'all','status':'SEMANTICS_UNREVIEWED','evidence':'header layout only'})
    assert sum(x['size'] for x in classification)==262160
    assert all(a['file_end_exclusive']==b['file_start'] for a,b in zip(classification,classification[1:]))
    write_csv(ROOT/'maps/rom/classification.csv',classification)
    def owner(bank,pc):
        return next((x['symbol'] for x in ranges if x['classification']=='code' and x['bank']==bank and int(x['cpu'],16)<=pc<int(x['end_cpu_exclusive'],16)),f'Unresolved_{bank}_{pc:04X}')
    edges=set()
    for x in read('analysis/cross_references.csv'):
        pc=int(x['from_cpu'],16)
        if x['status']=='STATIC_REVIEWED_SOURCE' and x['kind'] in ('call','jump'):
            edges.add((owner(x['from_bank'],pc),owner(x['to_bank'],int(x['to_cpu'],16)),x['kind']))
    for x in read('analysis/ppu_task_table.csv'):
        edges.add(('DispatchPpuTask',owner(x['target_bank'],int(x['target_cpu'],16)),'table'))
    indirect_path=ROOT/'analysis/indirect_dispatch_tables.csv'
    if indirect_path.exists():
        for x in read('analysis/indirect_dispatch_tables.csv'):
            edges.add((owner(x['dispatch_bank'],int(x['dispatch_cpu'],16)),owner(x['target_bank'],int(x['target_cpu'],16)),'table'))
    lines=['digraph ReviewedCalls {','  rankdir=TB;','  node [shape=box];']
    for a,b,k in sorted(edges):lines.append(f'  "{a}" -> "{b}" [label="{k}"];')
    lines.append('}');(ROOT/'analysis/reviewed_call_graph.dot').write_text('\n'.join(lines)+'\n')
    print(f'{len(symbols)} symbols; {len(classification)} exhaustive file ranges; {len(edges)} reviewed call/table edges.')
if __name__=='__main__':main()
