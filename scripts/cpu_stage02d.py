#!/usr/bin/env python3
"""New02D original-byte probes. No ROM changes/callee stubs; explicit local entry domains.
Uses saved earlier milestones as dependencies; does not execute their test suites.
"""
import argparse,json
from baseline import ROOT,verified_rom,write_json,write_csv,hashes
from cpu_stage01b import setup,execute,subroutine_frame
from cpu_stage02a import putword,word
from cpu_stage02b import putnum

def main():
    ap=argparse.ArgumentParser();ap.add_argument('rom');ap.add_argument('--from-group',type=int,default=1);ap.add_argument('--through-group',type=int,default=16);a=ap.parse_args();assert 1<=a.from_group<=a.through_group<=16
    rom,_=verified_rom(a.rom);prg=rom[16:0x20010];groups=[];vectors=[];traces=[]
    partial=ROOT/'analysis/cpu_stage02D.partial.json'
    if a.from_group>1 or a.through_group<16:
        prev=json.loads(partial.read_text());assert prev['rom_sha256']==hashes(rom)['sha256']
        groups=[g for g in prev['results'] if not a.from_group<=int(g['id'][5:7])<=a.through_group]
        vectors=[{'group':g['id'],'data':json.dumps(v,sort_keys=True)} for g in groups for v in g['observations']]
        traces=[r for r in prev['traces'] if not a.from_group<=int(r['experiment'][5:7])<=a.through_group]
    def add(name,obs,rows=None,scope='original bytes to RTS, no substituted callees'):
        groups.append({'id':name,'status':'PASS','vector_count':len(obs),'observations':obs,'boundary_stubs':[],'scope':scope})
        vectors.extend({'group':name,'data':json.dumps(o,sort_keys=True)} for o in obs)
        if rows:traces.extend(dict(experiment=name,**r) for r in rows)
        write_json(partial,{'rom_sha256':hashes(rom)['sha256'],'results':groups,'traces':traces,'complete':False})
        print(name,len(obs),'PASS',flush=True)
    def run(bus,m,pc,trace=False,stops=None):
        m.pc=pc;subroutine_frame(bus,m);rows,calls=execute(bus,m,stops or {0x8000},trace=trace);assert not calls;return rows
    def base(bank=8):
        bus,m=setup(prg,0x8000,r7=bank);bus.regs[6]=6;bus[0x4EF]=16;bus[0xB8]=255;bus[0x6BD]=12
        putword(bus,0xCB,128);putword(bus,0xC9,128);bus[0x6B9]=bus[0x6BB]=64;bus[0xDB]=4;bus[0xD9]=1;putnum(bus,0xEA,100,3)
        return bus,m
    def pair(bus,lo,hi,slot,value):bus[lo+slot]=value&255;bus[hi+slot]=(value>>8)&255
    def pairval(bus,lo,hi,slot):return bus[lo+slot]|bus[hi+slot]<<8
    def enemy(bus,slot,hp=100):
        bus[0x469+slot]=0xC0;bus[0x437+slot]=hp
        pair(bus,0x3FB,0x405,slot,128);pair(bus,0x3E7,0x3F1,slot,128)
    def projectile(bus,slot,typ=0,flags=0x90,vx=8):
        bus[0x568+slot]=typ;bus[0x57C+slot]=flags;bus[0x540+slot]=vx&255
        pair(bus,0x518,0x52C,slot,128);pair(bus,0x4F0,0x504,slot,128)
    def enemy_bullet(bus,slot=9):
        bus[0x491+slot]=0x80;bus[0x49B+slot]=0
        bus[0x4B9+slot]=128;pair(bus,0x4CD,0x4D7,slot,128)
    def byte(bank,addr):return prg[bank*8192+(addr&8191)]

    if a.from_group<=1<=a.through_group:
        obs=[];saved=[]
        for hp in range(256):
            for dmg in (0,1,2,3,6,15,127,128,254,255):
                for slot in (0,9):
                    bus,m=base();bus[0x437+slot]=hp;bus[0x441+slot]=dmg;bus[0x469+slot]=0xE1;bus[0x47D+slot]=5;bus[0x455+slot]=0xCC;bus[0x2C]=slot;m.x=slot
                    saved+=run(bus,m,0xE32A,trace=slot==0 and hp in (0,1,255) and dmg in (1,255))
                    expected=max(0,hp-dmg)
                    assert (bus[0x437+slot],bus[0x469+slot],bus[0x455+slot],bus[0x47D+slot],bus[1])==(expected,0xA1,0,0x85,0x55)
                    run(bus,m,0xE32A);assert bus[0x437+slot]==expected
                    obs.append({'slot':slot,'HP':hp,'queued_damage':dmg,'HP_after':expected,'second_call_does_not_charge_again':True})
        add('F_CPU01_HP_SATURATION_AND_SINGLE_CONSUMPTION',obs,saved)
    if a.from_group<=2<=a.through_group:
        obs=[]
        for flags in range(256):
            bus,m=base();slot=4;m.x=slot;bus[0x2C]=7;bus[0x437+slot]=20;bus[0x441+slot]=7;bus[0x469+slot]=flags;bus[0x455+slot]=0xBB;bus[0x47D+slot]=0x12;bus[1]=0x99
            run(bus,m,0xE32A);active=bool(flags&0x40)
            assert bus[0x437+slot]==(13 if active else 20) and bus[0x469+slot]==(flags&~0x40 if active else flags)
            assert bus[0x455+slot]==(0 if active else 0xBB) and m.x==(7 if active else slot)
            obs.append({'flags':flags,'consumed':active,'X_after':m.x,'pending_bit_is_not_checked_inside_consumer':True})
        add('F_CPU02_ACCEPTANCE_BIT_DOMAIN',obs)
    if a.from_group<=3<=a.through_group:
        obs=[];saved=[]
        for hp in (0,1,7):
            for flags in (0x80,0xA0,0xC0,0xE0):
                for quake in (0,0x10):
                    for state_base in (0,2,5):
                        bus,m=base();slot=2;m.x=slot;m.y=state_base;m.a=9;bus[0x2C]=slot;bus[0x437+slot]=hp;bus[0x441+slot]=3;bus[0x469+slot]=flags;bus[0x473+slot]=quake;bus[0x40F+slot]=3;bus[0x423+slot]=4
                        dead=hp==0 and state_base!=0;hit=not dead and bool(flags&0x20);frozen=not dead and not hit and bool(quake)
                        state=state_base if dead else state_base+1 if hit else state_base+2 if frozen else 3
                        expected_hp=max(0,hp-3) if hit and flags&0x40 else hp
                        saved+=run(bus,m,0xE2F9,trace=hp==1 and state_base==2)
                        assert (bus[0x2E],bus[0x2F],m.y,bus[0x437+slot])==(9,state,state*2,expected_hp)
                        assert bus[0x423+slot]==(5 if not(dead or hit or frozen) else 4)
                        obs.append({'HP':hp,'flags':flags,'quake_flag':quake,'base_state':state_base,'selected':state,'HP_after':expected_hp})
        add('F_CPU03_DEATH_HIT_QUAKE_NORMAL_PRIORITY',obs,saved,'local inputY=0/2/5; no full enemy-specific state dispatch')
    if a.from_group<=4<=a.through_group:
        bus,m=base(9);hps=[1,5,6,7,10,20,64,127,175,255]
        for i,hp in enumerate(hps):enemy(bus,i,hp)
        m.a=6;rows=run(bus,m,0xBD1B,trace=True);obs=[]
        for i,hp in enumerate(hps):
            assert bus[0x441+i]==6 and bus[0x469+i]==0xE0
            m.x=i;m.y=4;m.a=0;bus[0x2C]=i;rows+=run(bus,m,0xE2F9,trace=i in (0,9))
            assert bus[0x437+i]==max(0,hp-6) and bus[0x469+i]==0xA0
            obs.append({'slot':i,'HP':hp,'HP_after':bus[0x437+i]})
        add('F_CPU04_COLUMN_QUEUE_TO_ACTUAL_HP',obs,rows,'original02C producer used only as dependency in new end-to-end consumer experiment')
    if a.from_group<=5<=a.through_group:
        obs=[];saved=[]
        for phase in (0,1,2,255):
            for counter in (0,8,9):
                for direction in range(8):
                    bus,m=base();slot=3;enemy(bus,slot,20);bus[0x2C]=slot;bus[0x469+slot]=0xA1;bus[0x47D+slot]=0x80|direction;bus[0x423+slot]=phase;bus[0x455+slot]=counter
                    total=10-counter+(phase&1)
                    for tick in range(1,total+1):
                        m.x=slot;saved+=run(bus,m,0xE35B,trace=phase==0 and counter==0 and direction==1 and tick in (1,9,10))
                        assert bool(bus[0x469+slot]&0x20)==(tick<total)
                    dx=(0,2,2,2,0,-2,-2,-2)[direction]*(9-counter)
                    assert pairval(bus,0x3FB,0x405,slot)==(128+dx)&65535 and pairval(bus,0x3E7,0x3F1,slot)==128
                    assert (bus[0x469+slot],bus[0x47D+slot],bus[0x455+slot],bus[0x423+slot],bus[0x437+slot])==(0xC1,direction,0,0,20)
                    obs.append({'starting_phase':phase,'starting_recovery':counter,'direction':direction,'calls_until_rearmed':total,'delta_X':dx})
        add('F_CPU05_HIT_RECOVERY_AND_REAL_KNOCKBACK',obs,saved,'original movement helpers executed; terrain-adjust flag473bit80 clear, scratch36=0')
    if a.from_group<=6<=a.through_group:
        bus,m=base();before=[0,0x20,0x10,0x40,0x70,0xFF,0x81,2,0x10,0xFF]
        for i,v in enumerate(before):bus[0x473+i]=v
        run(bus,m,0xD7E7);marked=[v if v&0x20 else (v&0xAF)|0x10 for v in before[:8]]
        obs=[];saved=[]
        for tick in range(1,241):
            saved+=run(bus,m,0xD7AD,trace=tick in (1,209,210,239,240))
            flags=[v&0xAF if tick==240 else v|0x40 if tick>=210 and v&0x10 else v for v in marked]
            assert list(bus.ram[0x473:0x47B])==flags and list(bus.ram[0x47B:0x47D])==before[8:]
            assert bus[0x3DC]==(0 if tick==240 else tick+1)
            obs.append({'call':tick,'counter':bus[0x3DC],'first8flags':flags})
        add('F_CPU06_QUAKE_REQUEST_TO_EXPIRY',obs,saved,'240 lifetime-handler calls, not seconds; original producer dependency not separately rerun')
    if a.from_group<=7<=a.through_group:
        obs=[]
        for counter in range(241):
            for flag in (0,0x10,0x20,0x30,0x40,0x50,0x60,255):
                bus,m=base();bus[0x3DC]=counter
                for i in range(10):bus[0x473+i]=flag
                run(bus,m,0xD7AD);expected=flag&0xAF if counter==240 else flag|0x40 if counter==210 and flag&0x10 else flag
                assert list(bus.ram[0x473:0x47B])==[expected]*8 and list(bus.ram[0x47B:0x47D])==[flag]*2
                assert bus[0x3DC]==(0 if counter in (0,240) else counter+1)
                obs.append({'counter_before':counter,'flag_before':flag,'counter_after':bus[0x3DC],'flag_after':expected})
        add('F_CPU07_QUAKE_VALID_COUNTER_AND_FLAG_BOUNDARIES',obs)
    if a.from_group<=8<=a.through_group:
        obs=[];saved=[]
        for selected in (0,10,12):
            for budget in (0,1,9,10,127,128,255):
                for invulnerable in (0,1):
                    bus,m=base();bus[0x6BD]=selected;bus[0x5A7]=budget;bus[0xD2]=invulnerable;enemy_bullet(bus)
                    after=(budget-1)&255 if selected==10 else budget;absorbed=selected==10 and after<128
                    saved+=run(bus,m,0xA305,trace=selected==10 and budget in (0,1,10) and not invulnerable)
                    assert bus[0x5A7]==after and bus[0x49A]==0
                    assert bus[0x6B9]==(64 if absorbed or invulnerable else 57)
                    obs.append({'selected':selected,'budget':budget,'invulnerable':invulnerable,'budget_after':after,'HP_after':bus[0x6B9],'synthetic_budget_domain':budget>10})
        bus,m=base(9);bus[0x6BD]=10;bus[0x56B]=0x84;bus[0x1F]=0x20;run(bus,m,0xB8F0);assert bus[0x5A7]==10 and bus[0x56B]==0x8A
        bus.regs[7]=8
        for hit in range(1,12):
            enemy_bullet(bus);saved+=run(bus,m,0xA305,trace=hit in (10,11));assert bus[0x6B9]==(64 if hit<=10 else 57)
            obs.append({'consecutive_intersection':hit,'budget_after':bus[0x5A7],'HP_after':bus[0x6B9]})
        bus.regs[7]=9;m.x=3;run(bus,m,0xB964);assert bus[0x56B]==0x84
        add('F_CPU08_SHIELD_AND_FULL_ENEMY_PROJECTILE_COLLISION',obs,saved,'R6=06 original kind0/state0 shape and player state0; no collision/damage stubs; valid10-hit lifecycle plus explicit synthetic budgets')
    if a.from_group<=9<=a.through_group:
        obs=[]
        for state in range(202):
            idx=state//2;yo=byte(6,0x8000+idx);yh=byte(6,0x8065+idx);s0=byte(6,0x80CA+idx);s1=byte(6,0x812F+idx);side=s1 if state&1 else s0
            h=(10+yh)&255;w=(10+s0+s1)&255
            for dy in sorted({0,(h-1)&255,h,255}):
                for dx in sorted({0,(w-1)&255,w,255}):
                    bus,m=base();bus[0xCD]=state;bus[0x22]=(128-yo+dy)&255;bus[0x23]=10;bus[0x24]=(128-side+dx)&255;bus[0x25]=10
                    run(bus,m,0xA4EC);overlap=dy<h and dx<w
                    assert bool(m.p&1)==(not overlap),(state,dy,dx,h,w)
                    obs.append({'state':state,'mod_delta_y':dy,'mod_delta_x':dx,'overlap':overlap})
        add('F_CPU09_PLAYER_PROFILE_MODULAR_EDGES',obs,scope='helper domain202 state bytes across101 profiles; does not establish all profiles reachable at collision call')
    if a.from_group<=10<=a.through_group:
        obs=[];saved=[]
        for typ in range(64):
            idx=typ//2;yo=byte(6,0x84BC+idx);yh=byte(6,0x84DC+idx);left=byte(6,0x84FC+idx);right=byte(6,0x851C+idx)
            if typ&1:left,right=right,left
            for x in (0,1,4,8,128,247,255):
                l=min(left,x);r=min(right,256-x);h=(10+yh)&255;w=(20+l+r)&255
                for dy in sorted({0,h-1,h,255}):
                    for dx in sorted({0,w-1,w,255}):
                        bus,m=base();putword(bus,0xA7,256);projectile(bus,0,typ);pair(bus,0x518,0x52C,0,256+x);bus[0x22]=(128-yo+dy)&255;bus[0x23]=10;bus[0x24]=(x-l+dx)&255;bus[0x25]=20;m.x=0;m.y=idx
                        saved+=run(bus,m,0xA54D,trace=typ==0 and x in (0,255) and dx==w and dy==0)
                        overlap=dy<h and dx<w;assert bool(m.p&1)==(not overlap),(typ,x,dy,dx,h,w,bus[0x2A],bus[0x2B])
                        obs.append({'type':typ,'camera_relative_X':x,'mod_delta_y':dy,'mod_delta_x':dx,'overlap':overlap,'clipped_left':l,'clipped_right':r})
        add('F_CPU10_PROJECTILE_BOX_FACING_AND_CAMERA_CLIP',obs,saved,'positionsinside camera page; original R6=06 profiles, exact boundary comparisons')
    if a.from_group<=11<=a.through_group:
        obs=[];saved=[]
        for typ in range(64):
            for persistent in (False,True):
                for vx in (-8,0,8):
                    bus,m=base();bus[0x6BD]=5;bus[0x6F8]=1;enemy(bus,0);projectile(bus,2,typ,0x90 if persistent else 0x80,vx)
                    saved+=run(bus,m,0xA230,trace=typ in (0,0x10,0x12,0x28) and vx==8 and not persistent)
                    dmg=byte(6,0x853C+typ//2);reaction=7 if vx<0 else 1 if vx>0 else 0
                    assert (bus[0x441],bus[0x469],bus[0x47D]&7,bus[0x57E])==(dmg,0xE0,reaction,0x90 if persistent else 0),(typ,persistent,vx)
                    bus[0x2C]=0;m.x=0;m.y=4;m.a=0;run(bus,m,0xE2F9);assert bus[0x437]==100-dmg and bus[0x469]==0xA0
                    obs.append({'type':typ,'persistent':persistent,'vx':vx,'queued_damage':dmg,'HP_after':bus[0x437]})
        add('F_CPU11_REAL_COLLISION_QUEUE_AND_HP',obs,saved,'allpaired projectiletypes in localvaliddomain; original enemykind0/frame0 geometry; no AI or fullspawn reachability claim')
    if a.from_group<=12<=a.through_group:
        obs=[];saved=[]
        for persistent in (False,True):
            bus,m=base();bus[0x6BD]=5;bus[0x6F8]=2
            for i in range(2):enemy(bus,i,20)
            projectile(bus,2,0,0x90 if persistent else 0x80)
            saved+=run(bus,m,0xA230,trace=True)
            assert bus[0x469+1]==0xE0 and bus[0x469]==(0xE0 if persistent else 0xC0)
            obs.append({'persistent':persistent,'enemy1_pending':True,'enemy0_pending':persistent,'projectile_flags_after':bus[0x57E]})
        add('F_CPU12_DESCENDING_SCAN_AND_PIERCING',obs,saved)
    if a.from_group<=13<=a.through_group:
        obs=[];saved=[]
        for selected in range(13):
            for slot in range(3):
                bus,m=base();bus[0x6BD]=selected;bus[0x6F8]=1;enemy(bus,0);projectile(bus,slot,0x28,0x90)
                last=byte(8,0xA8E6+selected)
                saved+=run(bus,m,0xA230,trace=selected==3,stops={0x8000,0xA2C3})
                if last:assert bool(bus[0x469]&0x20)==(slot<=last) and m.pc==0x8000
                else:assert m.pc==0xA2C3 and bus[0x469]==0xC0
                obs.append({'selected':selected,'projectile_slot':slot,'last_slot':last,'queued':bool(bus[0x469]&0x20),'body_contact_tail_stopped':not bool(last)})
        add('F_CPU13_SELECTED_EFFECT_SLOT_LIMITS',obs,saved,'zero-limit routes stopbefore bodycontactA2C3; nonzero routes execute complete collision pass')
    if a.from_group<=14<=a.through_group:
        obs=[];saved=[]
        for facing in (0,1):
            bus,m=base(9);projectile(bus,0,facing,0x90,-8 if facing else 8);pair(bus,0x518,0x52C,0,240 if facing else 16)
            for tick in range(1,49):
                saved+=run(bus,m,0xBE90,trace=tick in (1,2,29,30) and facing==0)
                updates=(tick+1)//2;expected_type=min(updates//3,5)*2+facing;expected_x=(240-8*updates if facing else 16+8*updates)
                assert bus[0x568]==expected_type and pairval(bus,0x518,0x52C,0)==expected_x
                obs.append({'facing':facing,'object_loop_calls':tick,'handler_calls':updates,'type':bus[0x568],'X':expected_x})
        add('F_CPU14_PULSE_GROWTH_AND_FULL_OBJECT_MOVEMENT',obs,saved,'original frame/physics/sprite code; flags90 and startingD9=1 select alternating loop calls; camera-interior trajectory, no fullNES timing')
    if a.from_group<=15<=a.through_group:
        obs=[];saved=[]
        for typ in (0x0C,0x10,0x12):
            for vx in (-16,16):
                for vy in (-16,16):
                    for tx in (0,1,2,3):
                        for ty in (0,1,2,3):
                            for center in (0,1,2,3,8):
                                bus,m=base(9);projectile(bus,0,typ,0x80,vx);pair(bus,0x4F0,0x504,0,136);bus[0x554]=vy&255
                                bus[0x5B8+0x88]=center;bus[0x5B8+0x80+(128+vx)//16]=tx;bus[0x5B8+((128+vy)//16)*16+8]=ty;m.x=0
                                saved+=run(bus,m,0xB571,trace=typ==0x10 and vx==16 and vy==16 and tx==3 and ty==0 and center==8)
                                flags=(center&3) if center&3 else 0x80|((center&8)<<2)|(0x10 if typ&0x10==0 else 0)
                                assert bus[0x540]==((-vx if tx&3 else vx)&255) and bus[0x554]==((-vy if ty&3 else vy)&255),(typ,vx,vy,tx,ty,center)
                                assert bus[0x568]==typ^2 and bus[0x57C]==flags and bus.regs[6]==6 and m.x==0
                                obs.append({'type':typ,'vx':vx,'vy':vy,'future_x_cell':tx,'future_y_cell':ty,'current_cell':center,'flags_after':flags})
        add('F_CPU15_BOUNCE_AXES_WITH_REAL_TERRAIN_SAMPLERS',obs,saved,'interior scene0; injectedRAM collisioncache cells00..03/08, no substituted routines; destructible/offscreen terrain notcovered')
    if a.from_group<=16<=a.through_group:
        obs=[];saved=[]
        for typ in (0x18,0x19,0x28,0x29):
            for budget in (0,1,2,8,21):
                bus,m=base(9);projectile(bus,0,typ,0xD4,0);bus[0x590]=budget;bus[0x5A4]=2
                total=1 if budget==0 else 4*budget+8 if typ<0x20 else 3069 if budget==1 else 12*budget-5
                for tick in range(1,total+1):
                    pair(bus,0x518,0x52C,3,256+tick);pair(bus,0x4F0,0x504,3,512+tick);m.x=0
                    saved+=run(bus,m,0xBF3E,trace=typ==0x28 and budget==1)
                    assert bool(bus[0x57C]&0x80)==(tick<total),(typ,budget,tick,total,bus[0x568],bus[0x590])
                    if tick<total:assert pairval(bus,0x518,0x52C,0)==256+tick and pairval(bus,0x4F0,0x504,0)==512+tick
                    obs.append({'initial_type':typ,'initial_counter':budget,'synthetic_counter':(budget!=(21 if typ<0x20 else 8)),'call':tick,'current_type':bus[0x568],'counter':bus[0x590],'active':bool(bus[0x57C]&128)})
        add('F_CPU16_LIGHTNING_SEGMENT_LIFECYCLES',obs,saved,'actual indirect handler dispatch; follows moving selectedslot3; side budget1 is synthetic and wraps before expiry; native rendering/timing notclaimed')
    if len(groups)<16:
        print('Partial results saved; missing groups:',sorted(set(range(1,17))-{int(g['id'][5:7]) for g in groups}));return
    assert sorted(int(g['id'][5:7]) for g in groups)==list(range(1,17))
    groups.sort(key=lambda g:g['id']);vectors.sort(key=lambda r:r['group']);traces.sort(key=lambda r:r['experiment'])
    result={'stage':'02D','model':'py65 original CPU bytes with MMC3/PPU test doubles; no full NES timing','rom_sha256':hashes(rom)['sha256'],'groups':len(groups),'passed_groups':len(groups),'vectors':len(vectors),'trace_rows':len(traces),'results':groups}
    write_json(ROOT/'analysis/cpu_stage02D.json',result);write_csv(ROOT/'analysis/cpu_stage02D_vectors.csv',vectors);write_csv(ROOT/'analysis/cpu_stage02D_trace.csv',traces)
    partial.unlink(missing_ok=True)
    print(json.dumps({k:v for k,v in result.items() if k!='results'},indent=2))
if __name__=='__main__':main()
