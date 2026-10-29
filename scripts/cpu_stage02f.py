#!/usr/bin/env python3
"""Stage02F: original-byte melee/contact and bounded dispatch contracts.
No ROM patches, callee stubs, prior-suite execution or full-NES timing claims.
Each group is saved immediately; --groups resumes only selected groups.
"""
import argparse,json
from baseline import ROOT,verified_rom,write_json,write_csv,hashes
from cpu_stage01b import setup,execute,subroutine_frame
from cpu_stage02a import putword,word

def main():
    ap=argparse.ArgumentParser();ap.add_argument('rom');ap.add_argument('--groups',default='all');a=ap.parse_args()
    chosen=set(range(1,13)) if a.groups=='all' else {int(v) for v in a.groups.split(',')};assert chosen and chosen<=set(range(1,13))
    rom,_=verified_rom(a.rom);prg=rom[16:0x20010];sha=hashes(rom)['sha256'];partial=ROOT/'analysis/cpu_stage02F.partial.json'
    prior=json.loads(partial.read_text()) if partial.exists() else {'rom_sha256':sha,'results':[],'traces':[]};assert prior['rom_sha256']==sha
    groups=[g for g in prior['results'] if int(g['number']) not in chosen];traces=[r for r in prior['traces'] if int(r['group_number']) not in chosen]
    def add(number,name,obs,rows=None,scope='Original bytes through RTS; controlled RAM fixture; no callee substitution.'):
        ident=f'H_CPU{number:02d}_{name}';groups.append({'number':number,'id':ident,'status':'PASS','vector_count':len(obs),'observations':obs,'boundary_stubs':[],'scope':scope})
        if rows:traces.extend(dict(group_number=number,experiment=ident,**r) for r in rows)
        write_json(partial,{'rom_sha256':sha,'results':groups,'traces':traces,'complete':False});print(ident,len(obs),'PASS',flush=True)
    def run(b,m,pc,trace=False,stops=None):
        m.pc=pc;subroutine_frame(b,m);rows,calls=execute(b,m,{0x8000} if stops is None else stops,trace=trace);assert not calls;return rows
    def base():
        b,m=setup(prg,0x8000,r7=8);b.regs[6]=6;b[0x6B9]=64;b[0x6F8]=1
        putword(b,0xCB,128);putword(b,0xC9,128);return b,m
    def enemy(b,slot=0,kind=0,state=0,frame=0,x=128,y=108,flags=0xC1):
        for addr,value in [(0x3DD,kind),(0x40F,state),(0x419,frame),(0x3FB,x&255),(0x405,x>>8),(0x3E7,y&255),(0x3F1,y>>8),(0x469,flags),(0x437,64),(0x47D,0xA8)]:b[addr+slot]=value
    def byte(bank,addr):return prg[8192*bank+(addr&8191)]
    def rw(bank,addr):return byte(bank,addr)|(byte(bank,addr+1)<<8)
    def signed(v):return v if v<128 else v-256
    def attack(state,px,py,camera,rect):
        i=state//2;vo,ve,minus,plus=[byte(6,t+i) for t in (0x8194,0x81F9,0x825E,0x82C3)]
        if state&1:minus,plus=plus,minus
        if not 0<=((px+signed(plus)-camera)&65535)<256:plus=(camera-px)&255
        if not 0<=((px-signed(minus)-camera)&65535)<256:minus=(px-camera)&255
        ey,eh,ex,ew=rect
        return ((ey+vo-py)&255)<((eh+ve)&255) and ((ex+minus-px)&255)<((ew+plus+minus)&255)
    def direction(dx,dy):
        dx=signed(dx&255);dy=signed(dy&255);ax=abs(dx);ay=abs(dy)
        bucket=(0 if ay<ax//2 else 1) if ay<ax else (2 if ay<((ax*2)&255) else 3)
        return (6,7,7,0,6,5,5,4,2,1,1,0,2,3,3,4)[(8 if dx<0 else 0)+(4 if dy<0 else 0)+bucket]
    if 1 in chosen:
        obs=[];saved=[]
        for state in range(202):
            i=state//2
            for px,camera in ((128,0),(0,0),(255,0),(256,0),(512,384),(65530,65500)):
                for dx,dy in ((-33,0),(-1,0),(0,0),(1,0),(33,0),(0,-1),(0,1),(0,31),(0,32)):
                    py=128;rect=((py-byte(6,0x8194+i)+dy)&255,32,(px+dx)&255,24)
                    b,m=base();b[0xCD]=state;putword(b,0xCB,px);putword(b,0xA7,camera)
                    for addr,v in zip(range(0x22,0x26),rect):b[addr]=v
                    saved+=run(b,m,0xA452,trace=state in (0x22,0x23,0x34) and dx==0 and dy==0)
                    hit=attack(state,px,py,camera,rect);assert (not bool(m.p&1))==hit,(state,px,camera,dx,dy)
                    assert m.y==i
                    obs.append({'state':state,'player_x':px,'camera':camera,'dx':dx,'dy':dy,'overlap':hit})
        add(1,'MELEE_GEOMETRY_BOUNDARIES',obs,saved,'101 physical state pairs, two facings, six camera/world positions and nine edge probes; strict modular overlap oracle. Reachability of all states not claimed.')
    if 2 in chosen:
        obs=[];saved=[];values=(-128,-127,-64,-33,-32,-17,-16,-2,-1,0,1,2,16,17,32,33,64,127)
        for dx in values:
            for dy in values:
                for high in (0,7):
                    b,m=base();enemy(b,x=(high<<8)|128,y=(high<<8)|128);putword(b,0xCB,(128+dx)&255);putword(b,0xC9,(128+dy)&255);m.y=0
                    saved+=run(b,m,0xA5EC,trace=high==7 and dx in (-128,0,127) and dy in (-128,0,127))
                    assert m.a==direction(dx,dy) and m.y==0
                    obs.append({'dx':dx,'dy':dy,'enemy_high':high,'direction':m.a})
        add(2,'HIT_DIRECTION_LOW_BYTES',obs,saved)
    if 3 in chosen:
        obs=[];saved=[]
        for kind in range(99):
            record=rw(6,rw(6,0x855C+2*kind));damage=byte(6,record+2);shape=byte(6,record+3)
            for facing in (0,1):
                for x,y in ((128,108),(384,364),(65530,250)):
                    b,m=base();enemy(b,kind=kind,x=x,y=y,flags=0xC0|facing);b[0x3C]=0;m.y=0
                    saved+=run(b,m,0xA0B0,trace=kind in (0,0x50,0x62) and facing==0 and x==384)
                    assert bool(m.p&1)==(damage==0)
                    actual=None
                    if damage:
                        assert shape<48
                        vo,ve,p,q=[byte(6,t+shape) for t in (0x9554,0x9584,0x95B4,0x95E4)]
                        if not facing:p,q=q,p
                        actual=[b[i] for i in range(0x22,0x26)]
                        assert actual==[(y+vo)&255,ve,(x+p)&255,(p+q)&255] and b[0x26]==damage
                    obs.append({'kind':kind,'state':0,'frame':0,'facing':facing,'x':x,'y':y,'secondary_damage':damage,'shape':shape,'bounds':actual})
        add(3,'SECONDARY_SCHEMA_AND_HIGH_COORDS',obs,saved,'Actual state0/frame0 record of all99 collision-table kinds. Does not assert gameplay reachability or other frame counts; high coordinates do not reject secondary bounds.')
    if 4 in chosen:
        obs=[];saved=[]
        for state in range(202):
            i=state//2;minus=byte(6,(0x82C3 if state&1 else 0x825E)+i);ex=128-signed(minus)-12;ey=(128-byte(6,0x8194+i))&255
            for level in (0,7):
                b,m=base();b[0xCD]=state;b[0xD3]=level;enemy(b,x=ex,y=ey);b[0x455]=9
                hit=attack(state,128,128,0,(ey,32,(ex+12)&255,24));damage=byte(6,0x8328+i) if hit else 0
                saved+=run(b,m,0xA197,trace=state in (0x22,0x34,0x6C) and level==0)
                assert b[0x441]==damage and bool(b[0x469]&0x20)==bool(damage),(state,level,ex,ey,damage,b[0x441])
                if damage:
                    assert b[0x47D]==(0xA8|direction(128-ex,128-ey))
                    m.x=0;b[0x2C]=0;saved+=run(b,m,0xE32A,trace=state in (0x22,0x34,0x6C) and level==0)
                    assert b[0x437]==64-damage and b[0x469]&0x40==0 and b[0x455]==0
                obs.append({'state':state,'level':level,'queued_damage':damage,'enemy_HP':b[0x437],'reaction':b[0x47D]})
        add(4,'MELEE_QUEUE_TO_ORIGINAL_HP_CONSUMER',obs,saved,'New producer A197 through original A354/A452/A5EC, then existing E32A consumer. Harmless primary body damage0 still receives melee. Levels0/7 prove no local level multiplier, not global technique equivalence.')
    if 5 in chosen:
        obs=[];saved=[]
        for count in range(10):
            for flags in (0,0x40,0x80,0xC0,0xC1,0xE1):
                for secondary in (0,1,2,3,4):
                    for ce in (0,1):
                        b,m=base();b[0xCD]=0x22;b[0xCE]=ce;b[0x6F8]=count
                        for slot in range(count):enemy(b,slot,x=124,y=96);b[0x473+slot]=0
                        if count:b[0x469+count-1]=flags;b[0x473+count-1]=secondary
                        saved+=run(b,m,0xA197,trace=count==3 and flags==0x80 and secondary==0 and ce==0)
                        target=None if ce or count==0 else count-1 if flags&0xC0==0xC0 and secondary&3==0 else count-2 if count>=2 else None
                        actual=[i for i in range(count) if b[0x441+i]];assert actual==([] if target is None else [target]),(count,flags,secondary,ce,actual,target)
                        obs.append({'count':count,'last_flags':flags,'last_secondary':secondary,'CE':ce,'queued_slots':actual})
        # CD0 has zero damage; overlapping highest slot must terminate scan there.
        b,m=base();b[0x6F8]=3
        for slot in range(3):enemy(b,slot,x=116,y=128)
        saved+=run(b,m,0xA197,trace=True);assert b[0x3C]==2 and all(b[0x441+i]==0 for i in range(3))
        obs.append({'zero_damage_first_overlap_slot':b[0x3C],'queue_unchanged':True})
        add(5,'FIRST_TARGET_AND_ELIGIBILITY',obs,saved,'Counts0..9 avoid HPslot9 alias; descending scan chooses at most one eligible overlap; alternate family suppresses it. Zero-damage first overlap ends the scan.')
    if 6 in chosen:
        obs=[];saved=[]
        for phase_entry in (0xA2C3,0xA012):
            for count in (1,3,10):
                for flags in (0,0x40,0x80,0xC0,0xC1):
                    for block in ('none','D2','shield','D3hurt','D3dead','secondary'):
                        b,m=base();b[0x6F8]=count;b[0xA1]=2;enemy(b,count-1,state=1,flags=flags)
                        if block=='D2':b[0xD2]=1
                        if block=='shield':b[0x1A4]=1
                        if block=='D3hurt':b[0xD3]=0x20
                        if block=='D3dead':b[0xD3]=0x80
                        if block=='secondary':b[0x473+count-1]=1
                        saved+=run(b,m,phase_entry,trace=count==1 and flags==0xC1 and block=='none')
                        hit=flags&0xC0==0xC0 and block=='none';assert b[0x6B9]==64-(6 if hit else 0),(phase_entry,count,flags,block,b[0x6B9])
                        obs.append({'entry':hex(phase_entry),'count':count,'flags':flags,'block':block,'HP':b[0x6B9]})
        add(6,'BODY_CONTACT_AND_PHASE2_INTEGRATION',obs,saved,'Direct A2C3 and original A012 phase2 to contact then zero-damage melee; count is always1..10. Does not test or claim safe count0 for A2C3.')
    if 7 in chosen:
        obs=[];saved=[]
        for entry in (0xA075,0xA012):
            for count in (0,1,3):
                for kind,state in ((0,0),(0,1),(1,0),(5,0),(0x62,0)):
                    for ex in (120,128,384):
                        for protect in (0,1):
                            b,m=base();b[0x6F8]=count;b[0xA1]=1;b[0x1A4]=protect
                            if count:enemy(b,count-1,kind=kind,state=state,x=ex)
                            record=rw(6,rw(6,0x855C+2*kind)+2*state);damage=byte(6,record+2);shape=byte(6,record+3)
                            vo,ve,p,q=[byte(6,t+shape) for t in (0x9554,0x9584,0x95B4,0x95E4)] if damage else (0,0,0,0)
                            hit=count>0 and damage>0 and not protect and ((108+vo+28-128)&255)<((ve+28)&255) and ((ex+p+4-128)&255)<((p+q+8)&255)
                            expected=64-(damage if hit else 0)
                            saved+=run(b,m,entry,trace=count==1 and kind==0 and state==0 and protect==0)
                            assert b[0x6B9]==expected,(entry,count,kind,state,ex,protect,b[0x6B9],expected)
                            obs.append({'entry':hex(entry),'count':count,'kind':kind,'state':state,'enemy_x':ex,'protection':protect,'HP':b[0x6B9]})
        add(7,'SECONDARY_CONTACT_AND_PHASE1_INTEGRATION',obs,saved,'A075 and original A012 phase1, scene0 feet probe disabled by actual scene flag; compares actual secondary records with independent hurtbox overlap. Includes X-page aliasing and zero-count guard.')
    if 8 in chosen:
        obs=[];saved=[]
        for kind in range(99):
            for total in (0,1,174,175,176,255):
                for hp in (0,1,10,174,175,255):
                    b,m=base();enemy(b,kind=kind);b[0x440]=total;b[0x437]=hp;m.x=0
                    saved+=run(b,m,0xD78B,trace=kind in (0x50,0x5B,0x60) and total==174 and hp==10)
                    expected=min(175,total+hp) if kind>=0x50 and kind not in (0x5B,0x60) else total
                    assert b[0x440]==expected
                    obs.append({'kind':kind,'total':total,'HP':hp,'aggregate':expected})
        for total in (0,1,87,88,175,255):
            b,m=base();enemy(b,9,kind=0x50);b[0x440]=total;m.x=9
            saved+=run(b,m,0xD78B,trace=True);assert b[0x440]==min(175,total*2)
            obs.append({'slot':9,'aliased_total_and_HP':total,'aggregate':b[0x440]})
        add(8,'SPECIAL_HP_AGGREGATE_AND_ALIAS',obs,saved,'D78B local raw-byte arithmetic, saturating atAF; slot9 doubles aliased0440. No display-name/boss-health or global live-slot-count claim.')
    if 9 in chosen:
        obs=[];saved=[]
        for slot in range(9):
            for kind in (0,0x3F,0x46,0x50,0x5B,0x60,0x62):
                for phase in (0,1):
                    for active in (0,1):
                        b,m=base();b.regs[7]=13;enemy(b,slot,kind=kind,flags=0x80 if active else 0);b[0x2C]=slot;b[0x6F9]=phase;b[0x440]=0;m.x=slot
                        saved+=run(b,m,0xD759,trace=slot==0 and kind in (0,0x50),stops={0x8000,0xA000})
                        ai=active and slot%2!=phase
                        target=0x8000 if ai or not active else 0xA000
                        assert m.pc==target
                        assert b.regs[6]==(11 if kind<0x46 else 10) if ai else b.regs[6]==6
                        expected=64 if active and not ai and kind>=0x50 and kind not in (0x5B,0x60) else 0
                        assert b[0x440]==expected and b.regs[7]==13
                        obs.append({'slot':slot,'kind':kind,'phase':phase,'active':active,'stop':hex(m.pc),'AI_entered':bool(ai),'R6':b.regs[6],'aggregate':b[0x440]})
        add(9,'SCHEDULER_AI_OR_RENDER_BOUNDARY',obs,saved,'Stop before original AI8000 or rendererA000. Inactive RTS also lands on sentinel8000 with unchanged R6. Callees not executed; no substituted return. Kinds40..45 excluded.')
    if 10 in chosen:
        obs=[];saved=[]
        for bank,start,kinds in ((11,0x8011,range(64)),(10,0x8017,range(0x46,0x63))):
            for index,kind in enumerate(kinds):
                target=(rw(bank,start+index*2)+1)&65535;b,m=base();b.regs[6]=bank;enemy(b,3,kind=kind);b[0x2C]=3;m.x=0xF0
                saved+=run(b,m,0x8000,trace=True,stops={target})
                assert m.pc==target and m.x==3 and m.sp==0xFD
                assert b[0x1FE]==0xFF and b[0x1FF]==0x7F
                obs.append({'bank':bank,'kind':kind,'target':hex(target),'slot':m.x,'SP':m.sp})
        add(10,'AI_RETURN_ADDRESS_TABLES',obs,saved,'All93 physical pointers executed through push/push/RTS to first target instruction only. Handler bodies and native-kind reachability are NOT_TESTED; ordinary40..45 absent.')
    if 11 in chosen:
        obs=[];saved=[]
        for scene in range(32):
            for state in range(202):
                b,m=base();b[0x9A]=scene;b[0xCD]=state;i=state//2;strength=byte(6,0x8457+i);enabled=bool(byte(8,0xA8A6+scene) and strength)
                saved+=run(b,m,0xA1E8,trace=scene==3 and state in (0,0x22,0x23),stops={0x8000,0xC773})
                assert m.pc==(0xC773 if enabled else 0x8000)
                if enabled:
                    x=byte(6,0x83F2+i);expected=(-x)&255 if state&1 else x
                    assert (m.a,m.y,b[0x2C],word(b,0x26),word(b,0x28))==(expected,byte(6,0x838D+i),strength,128,128)
                obs.append({'scene':scene,'state':state,'C773_called':enabled,'strength':strength if enabled else None})
        add(11,'ATTACK_TERRAIN_ARGUMENT_BOUNDARY',obs,saved,'All32 scene flags and101 physical state pairs, two facings. Stops before C773, so no terrain mutation/reward/refill claim.')
    if 12 in chosen:
        obs=[];saved=[]
        for scene in range(32):
            for state in range(0,202,2):
                b,m=base();b[0x9A]=scene;b[0xCD]=state;enabled=bool(byte(8,0xA8C6+scene) and byte(8,0xA8F2+state//2))
                saved+=run(b,m,0xA120,trace=scene==3 and state==0,stops={0x8000,0xC776})
                assert m.pc==(0xC776 if enabled else 0x8000)
                if enabled:assert (m.a,m.y,word(b,0x26),word(b,0x28))==(250,2,128,128)
                obs.append({'scene':scene,'state':state,'first_C776_called':enabled})
        add(12,'FOOT_TERRAIN_FIRST_CALL_BOUNDARY',obs,saved,'All32scene/101state-pair flags. Only first C776 call reached; second +6/+2 call is static evidence, not dynamically claimed. Original shared A8F2 byte preserved.')
    groups.sort(key=lambda g:g['number']);complete=[g['number'] for g in groups]==list(range(1,13))
    write_json(partial,{'rom_sha256':sha,'results':groups,'traces':traces,'complete':complete})
    if complete:
        result={'stage':'02F','rom_sha256':sha,'groups':len(groups),'passed_groups':len(groups),'vectors':sum(g['vector_count'] for g in groups),'trace_rows':len(traces),'results':groups,'native_NES':'NOT_TESTED','old_suites_rerun':False}
        write_json(ROOT/'analysis/cpu_stage02F.json',result)
        write_csv(ROOT/'analysis/cpu_stage02F_vectors.csv',[{'group':g['id'],'data':json.dumps(v,sort_keys=True)} for g in groups for v in g['observations']])
        write_csv(ROOT/'analysis/cpu_stage02F_trace.csv',traces)
        print(json.dumps({k:v for k,v in result.items() if k!='results'},indent=2))
if __name__=='__main__':main()
