#!/usr/bin/env python3
"""Stage02E original-ROM CPU probes; no ROM patches or substituted callees.
Each selected group is written immediately. --groups selects only missing/fixed groups.
Saved historical CPU suites are dependencies, never executed here.
"""
import argparse,json
from baseline import ROOT,verified_rom,write_json,write_csv,hashes
from cpu_stage01b import setup,execute,subroutine_frame
from cpu_stage02a import putword,word

def main():
    ap=argparse.ArgumentParser();ap.add_argument('rom');ap.add_argument('--groups',default='all');a=ap.parse_args()
    chosen=set(range(1,15)) if a.groups=='all' else {int(v) for v in a.groups.split(',')};assert chosen and chosen<=set(range(1,15))
    rom,_=verified_rom(a.rom);prg=rom[16:0x20010];sha=hashes(rom)['sha256'];partial=ROOT/'analysis/cpu_stage02E.partial.json'
    prior=json.loads(partial.read_text()) if partial.exists() else {'rom_sha256':sha,'results':[],'traces':[]};assert prior['rom_sha256']==sha
    groups=[g for g in prior['results'] if int(g['number']) not in chosen];traces=[r for r in prior['traces'] if int(r['group_number']) not in chosen]
    def add(number,name,obs,rows=None,scope='Original bytes through RTS, no substituted callees; controlled RAM fixture.'):
        ident=f'G_CPU{number:02d}_{name}';groups.append({'number':number,'id':ident,'status':'PASS','vector_count':len(obs),'observations':obs,'boundary_stubs':[],'scope':scope})
        if rows:traces.extend(dict(group_number=number,experiment=ident,**r) for r in rows)
        write_json(partial,{'rom_sha256':sha,'results':groups,'traces':traces,'complete':False});print(ident,len(obs),'PASS',flush=True)
    def run(b,m,pc,trace=False):
        m.pc=pc;subroutine_frame(b,m);rows,calls=execute(b,m,{0x8000},trace=trace);assert not calls;return rows
    def base(floor=True):
        b,m=setup(prg,0x8000,r7=8);b.regs[6]=6;b[0xDB]=4;b[0x6BD]=12;b[0x6B9]=b[0x6BB]=64
        putword(b,0xCB,128);putword(b,0xC9,127);b[0xB8]=255;b[0x4EF]=16
        if floor:
            for col in range(16):b[0x5B8+0x80+col]=1
        return b,m
    def byte(bank,addr):return prg[8192*bank+(addr&8191)]
    def romword(bank,addr):return byte(bank,addr)|byte(bank,addr+1)<<8
    def scene0(b):
        for addr,src in [(0xB9,0xB282),(0xBB,0xB2C2),(0xC1,0xB382)]:putword(b,addr,romword(7,src))
        b[0x3B9]=2
    def terrain0(x,y):
        page=byte(2,romword(7,0xB282)+(x//256))
        mt=byte(2,romword(7,0xB2C2)+64*page+(y//32)*8+(x%256)//32)
        addr=romword(7,0xB382)+4*mt+2*((y%32)//16)+(x%32)//16
        return byte(2,addr),page,mt,addr
    def normal(level):return 0x7E if level>=6 else 0x2C if level>=4 else 0x1E
    def up(level,d):return 0x42 if level>=7 else 0x5C if level>=3 and d&3 else 0xAC

    if 1 in chosen:
        obs=[];saved=[]
        for y in (0,15,16,127,239,240,255,256,479,480,719,3839):
            for x in (0,15,16,127,239,255,256,511):
                for dx,dy in ((0,0),(-1,0),(1,0),(0,-1),(0,1),(-9,-28),(9,3)):
                    if not 0<=y+dy<3840:continue
                    b,m=base(False)
                    for i in range(256):b[0x5B8+i]=(i*73+19)&255
                    putword(b,0x26,x);putword(b,0x28,y);m.a=dx&255;m.y=dy&255
                    saved+=run(b,m,0xDAC2,trace=x==255 and y in (239,240) and dx==1)
                    index=((y+dy)%240//16)*16+((x+dx)&255)//16;expected=(index*73+19)&255
                    assert (m.a,b[0x3C],m.y)==(expected,expected,index),(x,y,dx,dy,m.a,expected)
                    obs.append({'x':x,'y':y,'dx':dx,'dy':dy,'cache_index':index,'attribute':m.a})
        add(1,'SIGNED_CACHE_COORDINATES',obs,saved,'DAC2 original signed sampler and F78B; synthetic cache, valid Y0..3839. No scene geometry claim.')
    if 2 in chosen:
        obs=[];saved=[]
        bypass={7,11,14,18,19,22,23,24,25}
        for scene in range(32):
            for db in (0,4):
                for x in (-1,0,7,8,247,248,255,256,511):
                    for y in (-1,0,211,212,239,255,256,479):
                        b,m=base(False);b[0x9A]=scene;b[0xDB]=db;putword(b,0x22,x&65535);putword(b,0x24,y&65535)
                        if scene in bypass:expected=1
                        elif x<0:expected=0
                        elif x>=256:expected=255 if db else 0
                        elif y<0:expected=0
                        elif y>=256:expected=0 if db else 255
                        elif db and x>=248:expected=255
                        else:expected=1
                        saved+=run(b,m,0xDD5F,trace=scene==0 and x in (247,248) and y==239)
                        assert m.a==expected,(scene,db,x,y,m.a,expected)
                        if expected!=1:assert b[0x3C]==3
                        obs.append({'scene':scene,'DB':db,'x':x,'y':y,'selector':expected})
        add(2,'SCENE_DOMAIN_CLASSIFIER',obs,saved,'DD5F at camera0; tests actual32-entry bypass table. DD92 fragment not assumed reachable.')
    if 3 in chosen:
        obs=[];saved=[];export=[]
        for page in range(16):
            for row in range(15):
                for col in range(16):
                    x=page*256+col*16;y=row*16;b,m=base(False);scene0(b);putword(b,0x22,x);putword(b,0x24,y);m.x=0xA5
                    expected,pid,mt,addr=terrain0(x,y)
                    saved+=run(b,m,0xDA3D,trace=(page,row,col) in ((0,0,0),(1,14,15),(15,14,15)))
                    assert (m.a,b[0x3D],b[0x3C],m.x,b.regs[6])==(expected,expected,3,0xA5,6)
                    v={'scene':0,'page_index':page,'x':x,'y':y,'page_id':pid,'metatile_id':mt,'attribute':expected,'attribute_bank':'02','attribute_cpu':f'0x{addr:04X}','attribute_file_offset':f'0x{16+2*8192+addr-0x8000:06X}'}
                    obs.append(v);export.append(v)
        write_csv(ROOT/'analysis/scene00_terrain_samples.csv',export)
        add(3,'ACTUAL_SCENE_ROM_LOOKUP',obs,saved,'DA3D with actual scene00 B9/BB/C1 pointers and PRG02 data; 16 page entries including repeated final page. Does not establish traversable stage length or sector mapping.')
    if 4 in chosen:
        obs=[];saved=[]
        for page in (1,2,14,15):
            for y in (0,80,160,208,224):
                b,m=base(False);scene0(b);x=page*256+80;putword(b,0x26,x);putword(b,0x28,y);expected,*_=terrain0(x,y)
                saved+=run(b,m,0xC75B,trace=page==1);assert m.a==expected and b[0x3C]==3 and b.regs[6]==6
                m.a=0;m.y=0;saved+=run(b,m,0xC767,trace=page==1);assert m.a==3 and b[0x3C]==3 and b.regs[6]==6
                obs.append({'x':x,'y':y,'raw_C75B_result':expected,'classified_C767_result':m.a})
        for attr in (0,1,2,3,4,8,12,0x40,0x80,0xC0):
            b,m=base(False);b[0x5B8+0x78]=attr;putword(b,0x26,128);putword(b,0x28,127);m.a=m.y=0
            run(b,m,0xC767);expected=3 if attr&0x40 else 0 if attr&0x80 else attr
            assert m.a==expected and b[0xCE]==(attr&12 if not attr&0xC0 else 0)
            obs.append({'cache_attribute':attr,'C767_result':m.a,'CE':b[0xCE]})
        add(4,'REAL_SERVICE_CALLER_CONTRACT',obs,saved,'New integration of previously reviewed DB02 with original cache/ROM samplers; dangerous terrain10 excluded (damage handled earlier).')
    if 5 in chosen:
        obs=[];saved=[]
        for facing in (0,1):
            for level in range(8):
                for d in range(16):
                    for pressed in (0,0x40,0x80,0xC0):
                        b,m=base();b[0xCD]=facing;b[0xD3]=level;b[0x20]=d;b[0x1F]=pressed
                        if pressed&0x80:expected=0x0A|facing
                        elif pressed&0x40:expected=(0xA0 if level>=2 else 0x12) if d&4 else up(level,d) if d&8 else normal(level);expected|=facing
                        else:expected={1:2,2:3,4:0x10|facing}.get(d,facing)
                        saved+=run(b,m,0xB81D,trace=level==0 and d in (1,4,12) and facing==0)
                        assert b[0xCD]==expected,(facing,level,d,pressed,b[0xCD],expected)
                        assert word(b,0xC9)==(124 if pressed&0x80 else 127)
                        obs.append({'facing':facing,'level':level,'held':d,'pressed':pressed,'state':b[0xCD],'D1':b[0xD1]})
        add(5,'GROUND_INPUT_PRIORITY',obs,saved,'Standing entry with controlled solid row8 and actualtwo-point terrain calls. A priority/B directional tiers verified; animations not inferred from names.')
    if 6 in chosen:
        obs=[];saved=[]
        for facing in (0,1):
            for level in range(8):
                for d in range(16):
                    b,m=base();b[0xCD]=0x0A|facing;b[0xD1]=0x45;b[0xD3]=level;b[0x20]=d
                    if d==0:expected=normal(level)|facing;phase=0x45
                    elif d in (1,2):
                        forward=level>=5 and ((d==1 and facing==0) or (d==2 and facing==1))
                        expected=(0xA0 if forward else normal(level))|facing;phase=0x80 if forward else 0x45
                    elif d in (4,5,6):expected=(0x1C if level>=1 else 0x0E)|facing;phase=0
                    elif d in (8,9,10):expected=up(level,d)|facing;phase=0x45
                    else:expected=0x0A|facing;phase=0x45
                    saved+=run(b,m,0xB972,trace=level in (0,5,7) and facing==0)
                    assert (b[0xCD],b[0xD1])==(expected,phase),(facing,level,d,b[0xCD],expected,b[0xD1],phase)
                    obs.append({'facing':facing,'level':level,'held':d,'state':b[0xCD],'D1':b[0xD1]})
        write_csv(ROOT/'analysis/player_air_attack_selection.csv',obs)
        add(6,'AIRBORNE_ATTACK_SELECTION',obs,saved)
    if 7 in chosen:
        obs=[];saved=[]
        for level in range(8):
            for d in (0,1,2,3):
                for entry in (0xBC67,0xBCCF,0xBCAE):
                    for facing in (0,1):
                        b,m=base();b[0xCD]=0x10|facing;b[0xD3]=level;b[0x20]=d;b[0xD1]=0x45;b[0xCF]=9
                        expected=(0x2C if level>=4 else 0x1E) if entry==0xBC67 else (0x5C if level>=3 and d else 0xAC) if entry==0xBCCF else 0x12
                        saved+=run(b,m,entry,trace=level==7 and d==1 and facing==0)
                        assert (b[0xCD],b[0xCF],b[0xD1])==(expected|facing,0,0x45)
                        obs.append({'entry':f'{entry:04X}','level':level,'held':d,'facing':facing,'state':b[0xCD]})
        add(7,'REPLACEMENT_BYPASS_ENTRIES',obs,saved,'Local entry contracts only; does not establish which gameplay paths invokeBC67/BCCF.')
    if 8 in chosen:
        obs=[];saved=[]
        for direction in (1,2):
            b,m=base();b[0xCD]=2+(direction==2);b[0x20]=direction
            for tick in range(1,33):
                saved+=run(b,m,0xB8B5,trace=tick in (1,7,8,31,32))
                expected=2+2*((tick//8)%4)+(direction==2)
                assert (b[0xCD],b[0xCF],word(b,0xCB))==(expected,tick%8,128+(tick if direction==1 else -tick))
                obs.append({'direction':direction,'call':tick,'state':b[0xCD],'timer':b[0xCF],'x':word(b,0xCB)})
        for current in range(4):
            for old1 in range(4):
                for old2 in range(4):
                    b,m=base();b[0xCD]=2;b[0x20]=current;b[0x713]=old1;b[0x714]=old2;d=current|old1|old2
                    run(b,m,0xB8B5);expected=0 if not d else 2 if d&1 else 3
                    assert b[0xCD]==expected and word(b,0xCB)==128+(0 if not d else 1 if d&1 else -1)
                    obs.append({'current':current,'old1':old1,'old2':old2,'state':b[0xCD],'x':word(b,0xCB)})
        add(8,'WALK_PERIOD_AND_INPUT_HISTORY',obs,saved)
    if 9 in chosen:
        obs=[];saved=[]
        # Independent expected velocity timelines: hold plateau, ascending taper, zero apex,
        # descending taper. No RAM-step emulation in the oracle.
        for hold in (0,1,5,12,24,30):
            b,m=base(False);putword(b,0xC9,190);b[0x20]=0x80;run(b,m,0xBC17);start=word(b,0xC9);assert start==187
            held_calls=min(hold,24)
            if hold>=24:upsteps=[3]*25+[3]*3+[2]*4+[1]*4+[0]
            else:upsteps=[3]*held_calls+[0]+[3]*3+[2]*4+[1]*4+[0]
            steps=[-v for v in upsteps]+[0]+[1]*4+[2]*4+[3]*4
            pos=start
            for tick,delta in enumerate(steps,1):
                b[0x20]=0x80 if tick<=hold else 0;b[0x21]=0
                saved+=run(b,m,0xBCEF,trace=hold in (0,30) and tick in (1,2,12,25,26,len(upsteps),len(upsteps)+1))
                pos+=delta;assert word(b,0xC9)==pos,(hold,tick,delta,word(b,0xC9),pos,b[0xD1])
                obs.append({'hold_calls':hold,'call':tick,'expected_dy':delta,'y':pos,'phase':b[0xD1]})
        for hist in range(256):
            b,m=base(False);putword(b,0xC9,128);b[0xD1]=0xE7;b[0x21]=hist
            run(b,m,0xBCEF);assert word(b,0xC9)==(125 if hist&3 else 128)
            assert b[0xD1]==(0xE8 if hist&3 else 0x40)
            obs.append({'A_history':hist,'y':word(b,0xC9),'phase':b[0xD1]})
        add(9,'VARIABLE_JUMP_TIMELINES',obs,saved,'Clear controlled cache; startingY190 avoids upper clamp. Holds are calls to physics, not measured video frames; history is independentinput.')
    if 10 in chosen:
        obs=[];saved=[]
        for head in (0,1,2,3):
            for floor in (0,1,2,3):
                for phase in (0xE7,0x40,0x4B,0x4C,0x0C,0x04,0):
                    if phase==0x4C:continue # nextindex13 is outside normal tabledomain
                    b,m=base(False)
                    for col in (7,8):b[0x5B8+0x60+col]=head;b[0x5B8+0x80+col]=floor
                    b[0xD1]=phase;b[0x20]=0x80;start=127
                    saved+=run(b,m,0xBCEF,trace=head==2 and floor==1)
                    if phase&0x40:
                        expected_phase=12 if head&2 or phase==0x4B else 0xE8 if phase==0xE7 else 0x41
                        expected_y=start if head&2 or phase==0x4B else 124
                    else:
                        expected_phase=0 if floor&1 else max(0,phase-1)
                        expected_y=127 if floor&1 else start+{12:0,4:2,0:3}[phase]
                    assert (b[0xD1],word(b,0xC9))==(expected_phase,expected_y),(head,floor,phase,b[0xD1],word(b,0xC9),expected_phase,expected_y)
                    obs.append({'head':head,'floor':floor,'phase':phase,'after':b[0xD1],'y':word(b,0xC9)})
        add(10,'CEILING_AND_LANDING_BITS',obs,saved,'Actualtwo-point sampler: ceilingbit02 andfloorbit01 distinct; normalphaseindicesonly.')
    if 11 in chosen:
        obs=[];saved=[]
        sequences=[(0x12,0xB9D4,3,5,0x10),(0x1E,0xBA38,4,7,0),(0x2C,0xBA42,4,11,0),(0x5C,0xBA84,3,17,0),(0x7E,0xBA8E,3,17,0),(0xAC,0xBB21,3,6,0)]
        for start,entry,period,count,final in sequences:
            for facing in (0,1):
                b,m=base();b[0xCD]=start|facing
                for tick in range(1,period*count+1):
                    saved+=run(b,m,entry,trace=facing==0 and tick in (1,period,period*count))
                    expected=(final if tick==period*count else start+2*(tick//period))|facing
                    assert (b[0xCD],b[0xCF])==(expected,tick%period),(start,tick,b[0xCD],expected)
                    obs.append({'start':start,'facing':facing,'call':tick,'state':b[0xCD],'timer':b[0xCF]})
        sequence=[0x44,0x46,0x48,0x4A,0x4C,0x4E,0x50,0x52,0x54,0x56]*3+[0x5A,0]
        for facing in (0,1):
            b,m=base();b[0xCD]=0x42|facing
            for tick,expected in enumerate(sequence,1):
                run(b,m,0xBA4C);assert (b[0xCD],b[0xCF])==(expected|facing,tick)
                obs.append({'start':0x42,'facing':facing,'call':tick,'state':b[0xCD]})
        for flags in (0x20,0x80,0xA0):
            b,m=base();b[0xCD]=0x42;b[0xD3]=flags;run(b,m,0xBA4C);assert (b[0xCD],b[0xCF])==(0x42,0)
            obs.append({'frozen_D3':flags,'state':b[0xCD]})
        add(11,'ATTACK_STATE_TIMELINES',obs,saved,'Animation calls with groundcache andoriginalphysics; hitboxes, attackdamage, native timing outside scope.')
    if 12 in chosen:
        obs=[];saved=[]
        for d in (1,2):
            for slow in (0,4):
                for parity in (0,1):
                    for wall in (0,1,2,3):
                        b,m=base(False);putword(b,0xCB,136);b[0x20]=d;b[0xCE]=slow;b[0xD8]=parity
                        idxcol=(136+(9 if d==1 else -9))//16
                        for row in (6,7):b[0x5B8+row*16+idxcol]=wall
                        saved+=run(b,m,0xADFD,trace=d==1 and slow==0 and parity==0)
                        skipped=slow and parity;blocked=not skipped and wall
                        expected=136 if skipped or blocked else 136+(1 if d==1 else -1)
                        assert word(b,0xCB)==expected
                        assert bool(b[0xCE]&0x40)==(not blocked)
                        obs.append({'direction':d,'slow':slow,'parity':parity,'wall':wall,'x':word(b,0xCB),'CE':b[0xCE]})
        for d,start,expected in ((2,20,20),(2,21,20),(1,234,235),(1,235,235)):
            b,m=base(False);putword(b,0xCB,start);b[0x20]=d;run(b,m,0xADFD);assert word(b,0xCB)==expected
            obs.append({'screen_clamp_direction':d,'start':start,'x':word(b,0xCB)})
        add(12,'WALL_SLOW_TERRAIN_SCREEN_LIMITS',obs,saved,'Controlledcache, normalpositive coordinates. No claim of full scrolling or terrain destruction.')
    if 13 in chosen:
        obs=[];saved=[]
        for facing in (0,1):
            b,m=base();b[0xCD]=0xA0|facing;putword(b,0xCB,128)
            # Disablecamera movement and permit full localtrajectory by keepingrelativeXnearcenter.
            displacement=0
            for tick in range(1,37):
                phase=(tick-1)//6;speed=(2,3,3,3,3,2)[phase];displacement+=speed*(1 if facing==0 else -1)
                putword(b,0xA7,displacement&65535)
                saved+=run(b,m,0xBA98,trace=tick in (1,6,30,36))
                expected=(0x0A if tick==36 else 0xA0+2*(tick//6))|facing
                assert b[0xCD]==expected and word(b,0xCB)==128+displacement,(facing,tick,b[0xCD],expected,word(b,0xCB),128+displacement)
                obs.append({'facing':facing,'call':tick,'state':b[0xCD],'x':word(b,0xCB),'speed':speed})
        add(13,'FORWARD_ATTACK_MOTION',obs,saved,'Controlledcamera fixture follows trajectory toavoid clamp; not testing scrolling. Sixphases36calls, net96pixels absentcollision.')
    if 14 in chosen:
        obs=[];saved=[]
        # Original state dispatcher ensures table pointer, facing and physics work together.
        for direction in (0,1,2):
            b,m=base();b[0x20]=direction;b[0x1F]=0
            m.a=0;saved+=run(b,m,0xACF7,trace=True);expected={0:0,1:2,2:3}[direction];assert b[0xCD]==expected
            b[0x1F]=0x80;b[0x20]=0x80|direction
            m.a=0;saved+=run(b,m,0xACF7,trace=True);assert b[0xCD]==(0x0A|(direction==2)) and b[0xD1]==0xE7 and word(b,0xC9)==124
            b[0x1F]=0;b[0x20]=direction;b[0x21]=0
            m.a=0;saved+=run(b,m,0xACF7,trace=True);assert b[0xD1]==0x40 and word(b,0xC9)==124
            obs.append({'direction':direction,'state':b[0xCD],'phase':b[0xD1],'x':word(b,0xCB),'y':word(b,0xC9)})
        add(14,'STATE_DISPATCH_TO_JUMP',obs,saved,'Original ACF7 normal-family dispatcher to newlyreviewed handlers andactualterrain; doesnot execute fullAB19 render/contactpipeline.')
    groups.sort(key=lambda g:g['number']);complete=[g['number'] for g in groups]==list(range(1,15))
    write_json(partial,{'rom_sha256':sha,'results':groups,'traces':traces,'complete':complete})
    if complete:
        result={'stage':'02E','rom_sha256':sha,'groups':len(groups),'passed_groups':len(groups),'vectors':sum(g['vector_count'] for g in groups),'trace_rows':len(traces),'results':groups,'native_NES':'NOT_TESTED','old_suites_rerun':False}
        write_json(ROOT/'analysis/cpu_stage02E.json',result)
        write_csv(ROOT/'analysis/cpu_stage02E_vectors.csv',[{'group':g['id'],'data':json.dumps(v,sort_keys=True)} for g in groups for v in g['observations']])
        write_csv(ROOT/'analysis/cpu_stage02E_trace.csv',traces)
        print(json.dumps({k:v for k,v in result.items() if k!='results'},indent=2))
if __name__=='__main__':main()
