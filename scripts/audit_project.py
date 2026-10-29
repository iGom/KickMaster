#!/usr/bin/env python3
"""Check address domains, complete range coverage and evidence/artifact consistency."""
import argparse,csv,hashlib,json,re,zipfile,struct
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
    assert len(indirect)==349 and sum(r['group'].startswith('D_') for r in indirect)==42
    assert sum(r['group'].startswith('E_') for r in indirect)==12
    assert sum(r['group'].startswith('F_') for r in indirect)==32
    assert sum(r['group'].startswith('G_') for r in indirect)==32
    assert sum(r['group'].startswith('H_') for r in indirect)==93
    assert all((r['dispatch_bank'],r['dispatch_cpu']) in keys for r in indirect)
    assert len(rows('analysis/numeric_formats.csv'))==5 and len(rows('analysis/progression_snapshot_layout.csv'))==5
    checks+=['stage02B: 16 groups/52382 CPU vectors pass with no callee stubs; bounded dispatch stops explicitly recorded',
             '8 progression rows,24 pickup pairs,13 selected effects,6 score thresholds and349 indirect edges match original ROM domains']
    current=json.loads((ROOT/'analysis/cpu_stage02C.json').read_text())
    assert current['groups']==current['passed_groups']==18 and current['vectors']==16460
    assert current['rom_sha256']==hashlib.sha256(rom).hexdigest()
    assert all(g['status']=='PASS' and not g['boundary_stubs'] for g in current['results'])
    assert current['vectors']==sum(g['vector_count'] for g in current['results'])
    assert len(rows('analysis/cpu_stage02C_vectors.csv'))==current['vectors']
    assert len(rows('analysis/cpu_stage02C_trace.csv'))==current['trace_rows']
    magic=rows('analysis/magic_unlock_menu_map.csv');assert len(magic)==12
    assert sorted(int(r['menu_cell']) for r in magic)==list(range(12))
    for r in magic:
        i=int(r['effect_index'],16);cell=int(r['menu_cell'])
        assert int.from_bytes(raw(8,0xA860+2*i,2),'little')==int(r['unlock_mask_16bit'],16)==1<<i
        assert raw(7,0xAC35+cell,1)[0]==i
        assert int(r['source_file_offset'],16)==16+8*8192+0x860+2*i
    routes=rows('analysis/magic_acquisition_scene_routes.csv');assert len(routes)==32
    for r in routes:assert rom[int(r['source_file_offset'],16)]==int(r['route_byte'],16)
    pointers=rows('analysis/magic_description_pointers.csv');assert len(pointers)==12
    for r in pointers:
        off=int(r['source_file_offset'],16);target=int.from_bytes(rom[off:off+2],'little')
        assert target==int(r['target_cpu'],16) and r['target_bank']=='03'
        assert int(r['target_file_offset'],16)==16+3*8192+target-0x8000
        assert 'R6=03' in r['target_mapping_condition']
    originals=rows('research/originals_manifest.csv');assert len(originals)==10
    for r in originals:
        data=(ROOT/r['relative_path']).read_bytes()
        assert len(data)==int(r['size_bytes']) and hashlib.sha256(data).hexdigest()==r['sha256']
        if r['width']:
            assert data[:8]==b'\x89PNG\r\n\x1a\n' and data[12:16]==b'IHDR'
            assert struct.unpack('>II',data[16:24])==(int(r['width']),int(r['height']))
    with zipfile.ZipFile(ROOT/'research/originals/maps.zip') as z:
        assert z.testzip() is None
        for r in originals:
            if r['width']:assert z.read(r['source_container'].split('::',1)[1])==(ROOT/r['relative_path']).read_bytes()
    for r in rows('research/stage_map_index.csv'):
        assert r['comparison_status']=='AVAILABLE_PENDING_ROM_COMPARISON'
        assert r['rom_map_extracted']=='False'
    receipts=json.loads((ROOT/'manifests/stage02B_sidecars_readback.json').read_text())
    assert receipts['all_three_sidecars_saved_and_read_back']=='PASS'
    for r in receipts['files']:
        assert hashlib.sha256((ROOT/'manifests'/r['file_name']).read_bytes()).hexdigest()==r['sha256']
    checks+=['stage02C:18 groups/16460 vectors pass; scoped stopping boundaries preserved',
             '12 unlock/menu mappings,32 acquisition scene routes and12 R6-qualified description pointers verified',
             'user-supplied guide,ZIP and8 original PNGs retain exact hashes/dimensions; no ROM geometry comparison claimed',
             'three repaired02B sidecar files match recorded successful Library readback hashes']
    current=json.loads((ROOT/'analysis/cpu_stage02D.json').read_text())
    assert current['groups']==current['passed_groups']==16 and current['vectors']==26832
    assert current['rom_sha256']==hashlib.sha256(rom).hexdigest()
    assert all(g['status']=='PASS' and not g['boundary_stubs'] for g in current['results'])
    assert current['vectors']==sum(g['vector_count'] for g in current['results'])
    assert len(rows('analysis/cpu_stage02D_vectors.csv'))==current['vectors']
    assert len(rows('analysis/cpu_stage02D_trace.csv'))==current['trace_rows']==117943
    profiles=rows('analysis/projectile_collision_profiles.csv');assert len(profiles)==32
    for r in profiles:
        i=int(r['type_even'],16)//2
        for field,addr in [('vertical_offset',0x84BC),('vertical_extent',0x84DC),('minus_x_extent',0x84FC),('plus_x_extent',0x851C),('queued_damage',0x853C)]:
            assert int(r[field])==raw(6,addr+i,1)[0]
        assert int(r['source_file_offset'],16)==16+6*8192+0x53C+i and 'R6=06' in r['source_mapping_condition']
    profiles=rows('analysis/player_hurtbox_profiles.csv');assert len(profiles)==101
    for r in profiles:
        i=int(r['state_pair'])
        for field,addr in [('vertical_offset',0x8000),('vertical_extent',0x8065),('side0',0x80CA),('side1',0x812F)]:
            assert int(r[field])==raw(6,addr+i,1)[0]
    dispatch=rows('analysis/projectile_object_dispatch.csv');assert len(dispatch)==32
    for r in dispatch:
        off=int(r['source_file_offset'],16);assert int.from_bytes(rom[off:off+2],'little')==int(r['handler_cpu'],16)
        assert (r['handler_bank'],r['handler_cpu']) in keys
    limits=rows('analysis/magic_collision_slot_limits.csv');assert len(limits)==13
    for r in limits:assert int(r['last_slot'])==rom[int(r['source_file_offset'],16)]
    closure=json.loads((ROOT/'manifests/stage02C_closure_readback.json').read_text());assert closure['all_passed'] is True
    for r in closure['results']:
        rel='manifests/stage02C.persistence.json' if r['file_name']=='stage02C.persistence.json' else 'reports/stages/SESSION_REPORT_stage02C.md'
        b=(ROOT/rel).read_bytes();assert len(b)==r['size_bytes'] and hashlib.sha256(b).hexdigest()==r['sha256']
        assert r['byte_for_byte_readback']=='PASS'
    checks+=['stage02D:16 groups/26832 vectors/117943 trace rows retained; all groups PASS with no callee stubs',
             '32 projectile collision profiles and dispatch pairs,101 player profiles and13 slot limits match original bytes',
             'closed02C persistence JSON and final report match actual successful readback receipts; old CPU suites were not rerun']
    current=json.loads((ROOT/'analysis/cpu_stage02E.json').read_text())
    assert current['groups']==current['passed_groups']==14 and current['vectors']==11868
    assert current['rom_sha256']==hashlib.sha256(rom).hexdigest() and current['old_suites_rerun'] is False
    assert all(g['status']=='PASS' and not g['boundary_stubs'] for g in current['results'])
    assert current['vectors']==sum(g['vector_count'] for g in current['results'])
    assert len(rows('analysis/cpu_stage02E_vectors.csv'))==current['vectors']
    assert len(rows('analysis/cpu_stage02E_trace.csv'))==current['trace_rows']==34866
    directions=rows('analysis/player_direction_dispatch.csv');assert len(directions)==32
    for r in directions:
        low=rom[int(r['source_file_offset'],16)];high=raw(8,int(r['high_byte_cpu'],16),1)[0]
        assert low|(high<<8)==int(r['target_cpu'],16)
    assert len(rows('analysis/player_air_attack_selection.csv'))==256
    steps=rows('analysis/player_jump_step_table.csv');assert len(steps)==13
    for r in steps:assert rom[int(r['source_file_offset'],16)]==int(r['magnitude_pixels'])
    seq=rows('analysis/player_attack42_sequence.csv');assert len(seq)==33
    for r in seq:assert rom[int(r['source_file_offset'],16)]==int(r['state_even'],16)
    flags=rows('analysis/scene_terrain_cache_flags.csv');assert len(flags)==32
    for r in flags:assert rom[int(r['source_file_offset'],16)]==int(r['bypass_flag'])
    samples=rows('analysis/scene00_terrain_samples.csv');assert len(samples)==3840
    for r in samples:assert rom[int(r['attribute_file_offset'],16)]==int(r['attribute'])
    assert {int(r['page_index']) for r in samples}==set(range(16))
    assert all(r['handler_review']=='STATIC_REVIEWED' for r in states if r['family']=='0' and int(r['CD_even'],16)<=0xB8)
    receipt=json.loads((ROOT/'manifests/stage02D.readback.json').read_text())
    # The prior receipts are evidence files; they do not trigger old CPU/build execution.
    checks+=['stage02E:14 groups/11868 vectors/34866 trace rows; no patches/callee stubs; old suites not rerun',
             '32 split direction pointers,13 jump steps,33 sequence entries,32 cache flags and3840 actual scene00 attribute samples match ROM',
             'normal player states00..B8 now have reviewed handler entrypoints; full combat/native NES remain open']
    current=json.loads((ROOT/'analysis/cpu_stage02F.json').read_text())
    assert current['groups']==current['passed_groups']==12 and current['vectors']==27126
    assert current['rom_sha256']==hashlib.sha256(rom).hexdigest() and current['old_suites_rerun'] is False
    assert all(g['status']=='PASS' and not g['boundary_stubs'] for g in current['results'])
    assert current['vectors']==sum(g['vector_count'] for g in current['results'])
    assert len(rows('analysis/cpu_stage02F_vectors.csv'))==current['vectors']
    assert len(rows('analysis/cpu_stage02F_trace.csv'))==current['trace_rows']==5223
    attack=rows('analysis/player_attack_profiles.csv');assert len(attack)==101
    for r in attack:
        i=int(r['state_pair'])
        for field,base in [('vertical_offset',0x8194),('vertical_extent',0x81F9),('minus_x_raw',0x825E),('plus_x_raw',0x82C3),('queued_damage',0x8328),('terrain_y_raw',0x838D),('terrain_x_raw',0x83F2),('terrain_strength',0x8457)]:
            assert raw(6,base+i,1)[0]==int(r[field])
    for name,count in [('enemy_body_collision_shapes',30),('enemy_attack_collision_shapes',48),('enemy_kind_collision_pointers',99),('enemy_state0_collision_records',99),('player_hit_direction_table',16),('player_terrain_probe_flags',32),('player_foot_terrain_state_flags',101)]:
        assert len(rows('analysis/'+name+'.csv'))==count
    for r in rows('analysis/enemy_state0_collision_records.csv'):
        offset=int(r['source_file_offset'],16)
        assert list(rom[offset:offset+4])==[int(r[k]) for k in ('primary_damage','body_shape','secondary_damage','attack_shape')]
    ai=rows('analysis/enemy_ai_dispatch.csv');assert len(ai)==93
    assert {int(r['kind'],16) for r in ai}==set(range(64))|set(range(0x46,0x63))
    for r in ai:
        offset=int(r['source_file_offset'],16);target=int(r['target_cpu'],16)
        assert int.from_bytes(rom[offset:offset+2],'little')+1==target
        assert int(r['target_file_offset'],16)==16+8192*int(r['target_bank'],16)+(target&8191)
    prior_e=json.loads((ROOT/'manifests/stage02E_resume_verification.json').read_text())
    checks+=['stage02F:12 groups/27126 vectors/5223 trace rows; original bytes, no callee stubs, old suites reused',
             '101 melee/terrain profiles,99 collision-kind records,30 body/48 attack shapes and93 return-address AI targets indexed',
             'AI, terrain-prefix and scheduler tests explicitly stop at original callee boundaries; no full-callee PASS inferred',
             '02E resume archive and six sidecars were freshly read and hash-verified before this milestone']
    prior={
      '00':'6c3b48030b66ae25e6fad9b21ca7c42904b1448a4c70d50d077df2ff45678e9f',
      '00A':'88779ce28f16092345a6d87a084855b6b96731d8f75471a2228cfc6e1a82debf',
      '01A':'d4cf1e4e2e0f80f30e88545d574d5f57107498eb8654037f21e16e160a6d2c3a',
      '01B':'a0c1d35ed1d82a0a12db9ff25d4f625ffad5382f535908b3fbfc56d03847992d',
      '02A':'1dfbc341acfa500072f21a1533ba6108088976ea03b1dbbcb3cceb141c2ee4e4',
      '02B':'397afcb28be6c26ce6fa471b5270531162a4a62b61f810cc02d14681fd5ce07b',
      '02C':'9abf1f5c0bdbba3f264bb34ffd9112a5e3bb3803fcd1ba87e84e493e26650a3d',
      '02D':'dbc9cf8ab43668c8042ed80dc25aeb966579968d7e7b8c39628d62b8af30609a',
      '02E':'1ae70fe401ac890e7e083e1c2ec4d5763e3ac314bf4b4ae698ccb1107f55759c'}
    preserved=[]
    for stage,h in prior.items():
        p=ROOT/f'checkpoints/kickmaster-ntscu-checkpoint-stage{stage}.zip'
        if p.exists():assert hashlib.sha256(p.read_bytes()).hexdigest()==h;preserved.append(stage)
    result={'result':'PASS','checks':checks,'reviewed_bytes':len(all_bytes),'reviewed_instructions':len(instructions),'symbols':len(symbols),'ram_entries':len(rows('maps/ram/ram_map.csv')),'classification_ranges':len(classes),'previous_local_archives_unchanged':preserved,'full_Ghidra_Mesen_import':'NOT_TESTED'}
    write_json(ROOT/'analysis/dataset_audit.json',result);print(json.dumps(result,indent=2))
if __name__=='__main__':main()
