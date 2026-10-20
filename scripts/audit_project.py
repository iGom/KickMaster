#!/usr/bin/env python3
"""Check address domains, complete range coverage and evidence/artifact consistency."""
import argparse,csv,hashlib,json,re
from baseline import ROOT,verified_rom,write_json
def rows(rel):
    with (ROOT/rel).open() as f:return list(csv.DictReader(f))
def main():
    ap=argparse.ArgumentParser();ap.add_argument('rom');a=ap.parse_args();rom,_=verified_rom(a.rom)
    ranges=rows('analysis/reviewed_ranges.csv');instructions=rows('analysis/reviewed_instructions.csv')
    cov=json.loads((ROOT/'analysis/coverage.json').read_text());checks=[];all_bytes=set();code=set();data=set();regions={}
    for r in ranges:
        po=int(r['prg_offset'],16);fo=int(r['file_offset'],16);bo=int(r['bank_offset'],16);bank=int(r['bank'],16);size=int(r['size'])
        assert po==8192*bank+bo and fo==po+16 and bo+size<=8192
        assert int(r['end_cpu_exclusive'],16)-int(r['cpu'],16)==size
        span=set(range(po,po+size));assert not all_bytes&span;all_bytes|=span
        (code if r['classification']=='code' else data).update(span);regions[r['id']]=r
    checks+=['reviewed ranges non-overlapping and physical/CPU offsets consistent']
    decoded=set();keys=set()
    for r in instructions:
        fo=int(r['file_offset'],16);po=fo-16;size=int(r['size']);region=regions[r['region_id']]
        assert region['classification']=='code'
        assert rom[fo:fo+size]==bytes.fromhex(r['bytes'])
        assert int(region['prg_offset'],16)<=po and po+size<=int(region['prg_offset'],16)+int(region['size'])
        span=set(range(po,po+size));assert not decoded&span;decoded|=span;keys.add((r['bank'],r['cpu']))
    assert decoded==code
    checks+=['every reviewed instruction matches original bytes and exactly covers reviewed code']
    assert len(code)==cov['reviewed_code_bytes'] and len(data)==cov['reviewed_data_bytes']
    assert len(all_bytes)==cov['reviewed_code_plus_data_bytes']
    assert cov['explicit_source_bytes']==16+len(all_bytes) and cov['input_incbin_bytes']==len(rom)-16-len(all_bytes)
    sizes=[]
    for p in (ROOT/'disassembly').rglob('*.asm'):
        if p.name.endswith('_reviewed.asm'):continue
        sizes.extend(int(x,16) for x in re.findall(r'\.incbin "inputs/original\.nes", \$[0-9A-F]+, \$([0-9A-F]+)',p.read_text()))
    assert sum(sizes)==cov['input_incbin_bytes']
    checks+=['coverage totals agree with emitted assembly and incbin byte counts']
    for r in rows('analysis/fixed_window_candidates.csv'):
        if r['status']=='REVIEWED':assert (r['bank'],r['cpu']) in keys
    for r in rows('analysis/cross_references.csv'):
        if r['status']=='STATIC_REVIEWED_SOURCE':assert (r['from_bank'],r['from_cpu']) in keys
    checks+=['candidate/source status does not promote reviewed data to code']
    symbols=rows('analysis/symbols.csv');assert len({r['name'] for r in symbols})==len(symbols)
    mlb=(ROOT/'MesenCE/kickmaster.mlb').read_text().splitlines();assert len(mlb)==len(symbols)
    blocks={r['name']:int(r['cpu_base'],16) for r in rows('ghidra/prg_memory_blocks.csv')}
    for r in ranges:assert int(r['cpu'],16)-int(r['bank_offset'],16)==blocks['PRG'+r['bank']]
    checks+=['symbol names unique; MLB count and Ghidra bank bases match current indexes']
    classes=rows('maps/rom/classification.csv');cursor=0
    for r in classes:
        assert int(r['file_start'])==cursor and int(r['size'])==int(r['file_end_exclusive'])-cursor
        cursor=int(r['file_end_exclusive'])
    assert cursor==len(rom)
    checks+=['complete file classification without gaps or overlaps']
    pointers=rows('analysis/scene_configuration_pointers.csv');assert len(pointers)==192
    for r in pointers:
        source=int(r['source_file_offset'],16);target=int(r['target_cpu'],16);bank=int(r['target_bank'],16)
        assert int.from_bytes(rom[source:source+2],'little')==target
        base=0x8000 if target<0xA000 else 0xA000 if target<0xC000 else 0xC000 if target<0xE000 else 0xE000
        assert int(r['target_prg_offset'],16)==bank*8192+target-base
        assert int(r['target_file_offset'],16)==16+int(r['target_prg_offset'],16)
        assert ('R6=' in r['target_mapping_condition'])==(target<0xA000)
    states=rows('analysis/player_state_dispatch.csv');assert len(states)==116
    assert sum(r['family']=='0' for r in states)==111 and sum(r['family']=='1' for r in states)==5
    for r in states:
        source=int(r['handler_pointer_source'].split(':')[1],16);off=16+8*8192+source-0xA000
        assert int.from_bytes(rom[off:off+2],'little')==int(r['handler_cpu'],16)
    checks+=['192 scene pointers retain correct R6/R7 address domains; 116 state-table rows match original pointer bytes']
    build=json.loads((ROOT/'analysis/rebuild_verification.json').read_text());assert build['status']=='PASS' and build['original']==build['rebuilt']
    old=json.loads((ROOT/'analysis/cpu_experiments.json').read_text());new=json.loads((ROOT/'analysis/cpu_stage01B.json').read_text())
    assert old['passed']==57 and new['groups']==new['passed_groups']==18 and new['vectors']==2295
    current=json.loads((ROOT/'analysis/cpu_stage02A.json').read_text())
    assert current['groups']==current['passed_groups']==18 and current['vectors']==10137
    assert current['vectors']==sum(g['vector_count'] for g in current['results'])
    assert len(rows('analysis/cpu_stage02A_vectors.csv'))==current['vectors']
    assert len(rows('analysis/cpu_stage02A_trace.csv'))==current['trace_rows']
    checks+=['preserved stage01A/01B/02A CPU results pass; complete rebuilt image matches']
    current=json.loads((ROOT/'analysis/cpu_stage02B.json').read_text())
    assert current['groups']==current['passed_groups']==16 and current['vectors']==52382
    assert current['rom_sha256']==hashlib.sha256(rom).hexdigest()
    assert current['vectors']==sum(g['vector_count'] for g in current['results'])
    assert all(g['status']=='PASS' and not g['boundary_stubs'] for g in current['results'])
    assert len(rows('analysis/cpu_stage02B_vectors.csv'))==current['vectors']
    assert len(rows('analysis/cpu_stage02B_trace.csv'))==current['trace_rows']
    levels=rows('analysis/progression_levels.csv');pickups=rows('analysis/pickup_effects.csv');spells=rows('analysis/selected_spell_dispatch.csv')
    assert len(levels)==8 and len(pickups)==24 and len(spells)==13
    def raw(bank,cpu,n):return rom[16+bank*8192+(cpu&8191):16+bank*8192+(cpu&8191)+n]
    def number(bs,bias):
        ds=[b-bias for b in bs];assert all(0<=d<=9 for d in ds)
        return int(''.join(map(str,ds)))
    for r in levels:
        i=int(r['level']);assert number(raw(15,0xFDA8+4*i,4),0x60)==int(r['next_EXP_decimal'])
        assert number(raw(15,0xFDC8+3*i,3),0x60)==int(r['maximum_MP_decimal'])
        assert raw(15,0xFDE0+i,1)[0]==int(r['maximum_HP_raw'],16)
    for r in pickups:
        source=int(r['source_file_offset'],16);target=int(r['target_cpu'],16)
        assert int.from_bytes(rom[source:source+2],'little')==target
        assert int(r['target_file_offset'],16)==16+8*8192+(target&8191)
    for r in spells:
        encoded=int(r['encoded_type'],16);assert rom[int(r['source_file_offset'],16)]==encoded
        if encoded:
            assert int.from_bytes(raw(9,0xAB87+(encoded&0xFE),2),'little')==int(r['handler_cpu'],16)
            assert int.from_bytes(raw(9,0xAAA5+(encoded&0xFE),2),'little')==int(r['sprite_pointer_cpu'],16)
    thresholds=rows('analysis/score_thresholds.csv');assert len(thresholds)==6
    for r in thresholds:assert number(raw(15,0xFDE8+6*int(r['index']),6),0x20)==int(r['score_decimal'])
    indirect=rows('analysis/indirect_dispatch_tables.csv')
    assert len(indirect)==180 and sum(r['group'].startswith('D_') for r in indirect)==42
    assert all((r['dispatch_bank'],r['dispatch_cpu']) in keys for r in indirect)
    assert len(rows('analysis/numeric_formats.csv'))==5 and len(rows('analysis/progression_snapshot_layout.csv'))==5
    checks+=['stage02B: 16 groups/52382 CPU vectors pass with no callee stubs; bounded dispatch stops explicitly recorded',
             '8 progression rows,24 pickup pairs,13 selected effects,6 score thresholds and180 indirect edges match original ROM domains']
    prior={
      '00':'6c3b48030b66ae25e6fad9b21ca7c42904b1448a4c70d50d077df2ff45678e9f',
      '00A':'88779ce28f16092345a6d87a084855b6b96731d8f75471a2228cfc6e1a82debf',
      '01A':'d4cf1e4e2e0f80f30e88545d574d5f57107498eb8654037f21e16e160a6d2c3a',
      '01B':'a0c1d35ed1d82a0a12db9ff25d4f625ffad5382f535908b3fbfc56d03847992d',
      '02A':'1dfbc341acfa500072f21a1533ba6108088976ea03b1dbbcb3cceb141c2ee4e4'}
    preserved=[]
    for stage,h in prior.items():
        p=ROOT/f'checkpoints/kickmaster-ntscu-checkpoint-stage{stage}.zip'
        if p.exists():assert hashlib.sha256(p.read_bytes()).hexdigest()==h;preserved.append(stage)
    result={'result':'PASS','checks':checks,'reviewed_bytes':len(all_bytes),'reviewed_instructions':len(instructions),'symbols':len(symbols),'ram_entries':len(rows('maps/ram/ram_map.csv')),'classification_ranges':len(classes),'previous_local_archives_unchanged':preserved,'full_Ghidra_Mesen_import':'NOT_TESTED'}
    write_json(ROOT/'analysis/dataset_audit.json',result);print(json.dumps(result,indent=2))
if __name__=='__main__':main()
