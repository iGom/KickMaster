#!/usr/bin/env python3
"""Structure user-supplied reference tables; never treat this as ROM verification."""
import csv, hashlib, json, re
from pathlib import Path
from baseline import ROOT,write_csv,write_json

text=(ROOT/'project_specification.md').read_text()
tables=[];current=[]
for line in text.splitlines()+['']:
    if line.startswith('|'):current.append([x.strip() for x in line.strip('|').split('|')])
    elif current:
        tables.append(current);current=[]
def table(first):return next(t for t in tables if t[0]==first)
manual='https://www.digitpress.com/library/manuals/nes/Kickmaster.pdf'
guide='https://gamefaqs.gamespot.com/nes/563430-kickmaster/faqs/19876'
claims=[]
def add(kind,name,expected,source,section,status='DOCUMENTED',origin='user_specification_crosschecked',notes=''):
    claims.append({'id':f'G{len(claims)+1:03d}','category':kind,'name':name,'published_expectation':expected,
        'origin':origin,'source_url':source,'source_location':section,'source_reliability':'primary manual' if source==manual else 'secondary guide',
        'source_read':True,'status':status,'rom_verified':False,'emulator_observed':False,'assembly_confirmed':False,
        'notes':notes})
rows=[]
for level,exp,hp,mp in table(['Level','Cumulative EXP required','Maximum HP','Maximum MP'])[2:]:
    rows.append({'level':int(level),'cumulative_exp':int(exp.replace(',','')),'max_hp_display':int(hp),'max_mp_display':int(mp),'manual_printed_page':8,'pdf_page_1_based':5,'rom_verified':False})
    add('progression',f'Level {level}',f'EXP={exp}; HP={hp}; MP={mp}',manual,'printed p.8 / PDF p.5')
write_csv(ROOT/'research/progression_reference.csv',rows)
controls=['B','Down+B','Up+B','A, then Down+B','Down+(Left|Right)+B','Up+(Left|Right)+B','(Left|Right)+B','A, then (Left|Right)+B','(Left|Right)+B','Up+B']
rows=[]
for i,(level,name) in enumerate(table(['Level','Technique'])[2:]):
    rows.append({'level':int(level),'technique':name,'manual_input':controls[i],'guide_input_conflict':i in (6,8),'rom_internal_id':'','rom_verified':False})
    add('kick',name,f'level={level}; input={controls[i]}',manual,'printed pp.10-11 / PDF p.6',notes='guide says B alone; test both' if i in (6,8) else '')
write_csv(ROOT/'research/kicks_reference.csv',rows)
rows=[]
for name,effect in table(['Pickup','Documented effect'])[2:]:
    rows.append({'pickup':name,'effect':effect,'manual_printed_page':9,'rom_internal_id':'','rom_verified':False})
    add('pickup',name,effect,manual,'printed p.9 / PDF p.5')
write_csv(ROOT/'research/pickups_reference.csv',rows)
rows=[]
aliases={'Bouncing Bulb':'Bouncing Bulb Spirit','Lightning':'Lightning Spirit','Pulse Wave':'Pulse Wave Spirit','Harpy Flying':'Harpy Wings','?? Magic':'??'}
for name,cost,effect in table(['Spell','MP cost','Reference behavior'])[2:]:
    page=12 if name in ('Bouncing Bulb','Life Up 1') else 13 if name in ('Magic Boots','Twin Power','?? Magic','Lightning','Earthquake') else 14
    rows.append({'canonical_name':name,'aliases':aliases.get(name,''),'mp_cost_reference':cost,'effect_reference':effect,'manual_printed_page':page,'rom_internal_id':'','rom_unlock_flag':'','rom_verified':False})
    add('spell',name,f'cost={cost}; {effect}',manual,f'printed p.{page} / PDF p.{page//2+1}',notes='Effect deliberately unresolved; nominal per-second cost needs frame test' if name in ('?? Magic','Harpy Flying') else '')
write_csv(ROOT/'research/spells_reference.csv',rows)
rows=[]
for stage,name,acquisition in table(['Stage','Spell','Acquisition'])[2:]:
    rows.append({'stage':int(stage),'spell':name,'acquisition_reference':acquisition,'rom_offset':'','rom_verified':False})
    add('acquisition',name,f'stage={stage}; {acquisition}',guide,f'Sector {stage}')
write_csv(ROOT/'research/acquisition_reference.csv',rows)
write_csv(ROOT/'research/gameplay_claims.csv',claims)

stages=["The Witches' Forest","The Caverns of No Return","Belzed's First Stronghold","Bottomless Crevasse","Aboard the Ship of Strife","Across the Swamps","A Long Way From Home","Belzed's Haunted Tower"]
checks=['chest, boss reward and three-item drops','horizontal/vertical transitions; hidden boots; breakable terrain','branching hidden path; chests versus mimics; transforming entities','pit boundaries and spell object','ship movement and octopus body-part gating','slow terrain; hidden shield; paired bosses','spawn triggers and multiple boss encounters','vertical camera kill boundary; guardian sequence; final transition']
rows=[]
for i,(name,check) in enumerate(zip(stages,checks),1):
    url=f'https://gamefaqs.gamespot.com/nes/563430-kickmaster/map/{3646+i}-stage-{i}-map'
    rows.append({'stage':i,'name_from_user_specification':name,'map_author':'sprays','map_url':url,'listing_verified':True,'image_inspected':False,'rom_map_extracted':False,'comparison_status':'BLOCKED_IMAGE_RETRIEVAL','guide_section':f'Sector {i}','investigation_focus':check,'coordinate_system':'UNRESOLVED'})
    p=ROOT/f'reports/stages/STAGE_MAP_{i:02d}.md'
    p.write_text(f'# Stage {i}: {name}\n\nStatus: research baseline only; ROM extraction not started.\n\n'
      f'- Reference guide: [Wyrenth, Sector {i}]({guide}).\n- Published map: [sprays, Stage {i}]({url}).\n'
      f'- Map listing verified; image retrieval unsuccessful. No image dimensions or coordinates inferred.\n'
      f'- Priority investigation from the supplied specification: {check}.\n\n'
      'Required outputs remain unknown: ROM tables, dimensions, metatiles, collision, spawn coordinates,\n'
      'subarea links, hidden reward coordinates, boss IDs, camera limits, restart state and transitions.\n'
      'Do not use an image pixel location as a ROM world coordinate without establishing the transform.\n')
write_csv(ROOT/'research/stage_map_index.csv',rows)
print(f'{len(claims)} source-indexed reference claims; {len(rows)} map entries.')
