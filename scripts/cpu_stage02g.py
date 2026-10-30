#!/usr/bin/env python3
"""Stage02G original-ROM tests. No patches/stubs; selective groups preserve prior successes.
Original routines run in controlled RAM; no PPU/APU/timing/native-NES claim.
"""
import argparse,json
from baseline import ROOT,verified_rom,write_json,write_csv,hashes
from cpu_stage01b import setup,execute
from cpu_stage02a import putword,word

def main():
    ap=argparse.ArgumentParser();ap.add_argument('rom');ap.add_argument('--groups',default='all');a=ap.parse_args()
    chosen=set(range(1,16)) if a.groups=='all' else {int(v) for v in a.groups.split(',')};assert chosen and chosen<=set(range(1,16))
    rom,_=verified_rom(a.rom);prg=rom[16:0x20010];sha=hashes(rom)['sha256'];partial=ROOT/'analysis/cpu_stage02G.partial.json'
    prior=json.loads(partial.read_text()) if partial.exists() else {'rom_sha256':sha,'results':[],'traces':[]};assert prior['rom_sha256']==sha
    groups=[g for g in prior['results'] if g['number'] not in chosen];traces=[r for r in prior['traces'] if r['group_number'] not in chosen]
    def add(n,name,obs,rows=None,scope='Original bytes through RTS with controlled RAM, no substituted callees.'):
        ident=f'I_CPU{n:02d}_{name}';groups.append({'number':n,'id':ident,'status':'PASS','vector_count':len(obs),'observations':obs,'boundary_stubs':[],'scope':scope})
        if rows:traces.extend(dict(group_number=n,experiment=ident,**r) for r in rows)
        write_json(partial,{'rom_sha256':sha,'results':groups,'traces':traces,'complete':False});print(ident,len(obs),'PASS',flush=True)
    def byte(bank,addr):return prg[bank*8192+(addr&8191)]
    def run(b,m,pc,trace=False):
        m.pc=pc;m.sp=0xFD;b[0x1FE]=0xFC;b[0x1FF]=0x7F
        rows,calls=execute(b,m,{0x7FFD},trace=trace);assert not calls and m.sp==255;return rows
    def base(bank=11,slot=0):
        b,m=setup(prg,0x7FFD,r7=13);b.regs[6]=bank;b[0x2C]=slot;m.x=slot;b[0x6F8]=9;b[0x4EF]=20;b[0xDA]=1;b[0xD9]=4
        for i in range(6):b[0x306+i]=0x20
        for i in range(4):b[0xED+i]=0x60
        b[0x6B9]=64;b[0x437+slot]=64;b[0x469+slot]=0xC1;b[0x45F+slot]=0x21
        enemypos(b,slot,128,128);putword(b,0xD6,0);putword(b,0xD4,128);return b,m
    def enemypos(b,slot,x,y):
        b[0x3FB+slot]=x&255;b[0x405+slot]=x>>8;b[0x3E7+slot]=y&255;b[0x3F1+slot]=y>>8
    def pos(b,slot):return b[0x3FB+slot]|b[0x405+slot]<<8,b[0x3E7+slot]|b[0x3F1+slot]<<8
    def pool(b,free):
        for i in range(20):b[0x57F+i]=0x80;b[0x56B+i]=0xAA
        for i in range(19,19-free,-1):b[0x57F+i]=0
    def spawned(b):return [(i,b[0x56B+i]) for i in range(19,0,-1) if b[0x56B+i]!=0xAA]
    def score(b):return sum((b[0x306+i]-0x20)*10**i for i in range(6))
    types=(0x46,0x48,0x4B,0x43,0x44,0x4C,0x41,0x69)
    def triple(boss,seed):return [types[byte(14,(0xDF9B if boss else 0xDF7B)+((seed+10*k)&31))&7] for k in range(3)]
    def band(delta,yaxis=False):
        if yaxis:
            return 7 if delta< -32 else 6 if delta< -16 else 5 if delta< -1 else 4 if delta<0 else 3 if delta<1 else 2 if delta<8 else 1 if delta<16 else 0
        return 7 if delta< -40 else 6 if delta< -32 else 5 if delta< -24 else 4 if delta<0 else 3 if delta<24 else 2 if delta<32 else 1 if delta<40 else 0
    if 1 in chosen:
        obs=[];saved=[]
        for boss in (False,True):
            for d8 in range(256):
                for free in (0,1,2,3,4):
                    b,m=base();pool(b,free);b[0xD8]=d8
                    saved+=run(b,m,0xDF37 if boss else 0xDFCB,trace=d8 in (0,62) and free in (1,3))
                    expected=triple(boss,(d8>>1)&31)[:free];actual=spawned(b)
                    assert [t for i,t in actual]==expected,(boss,d8,free,actual,expected)
                    for j,(slot,t) in enumerate(actual):
                        assert (b[0x543+slot],b[0x557+slot])==((255,250) if j==0 else (1,250) if j==1 else (0,249))
                        assert b[0x4F3+slot]==112 and b[0x51B+slot]==128
                    assert m.x==0 and all(b[0xED+i]==0x60 for i in range(4))
                    obs.append({'special_death_table':boss,'D8':d8,'free_slots':free,'spawned':actual})
        add(1,'CORRELATED_DROPS_AND_POOL_PRESSURE',obs,saved,'Two triple paths over all D8 bytes and0..4 free slots; ordinary rare gate deliberately false. No collection/EXP occurs here. Trace includes real DFFF cross-bank instruction.')
    if 2 in chosen:
        obs=[];saved=[]
        for da in (0,1,2,3,4,252,255):
            for d9 in (0,1,2,3,4,5,252,255):
                for d8 in (0,1,62,255):
                    b,m=base();pool(b,3);b[0xDA]=da;b[0xD9]=d9;b[0xD8]=d8
                    saved+=run(b,m,0xDFCB,trace=da==0 and d9 in (3,4) and d8==62)
                    rare=not da&3 and not d9&0xFC;expected=[0x6A] if rare else triple(False,(d8>>1)&31)
                    actual=spawned(b);assert [t for _,t in actual]==expected
                    if rare:assert b[0x543+19]==0 and b[0x557+19]==249
                    obs.append({'DA':da,'D9':d9,'D8':d8,'single_extra_attempt':rare,'types':expected})
        add(2,'SINGLE_EXTRA_ATTEMPT_TIME_GATE',obs,saved,'Exact predicate (DA&03)==0 and(D9&FC)==0; not a measured random chance. Original pickup collector mapping identifies6A as extra attempt; collection not rerun.')
    if 3 in chosen:
        obs=[];saved=[]
        for entry,t in ((0xE01B,0x6A),(0xE01F,0x46),(0xE023,0x48),(0xE027,0x4B),(0xE02B,0x43),(0xE02F,0x44),(0xE033,0x41),(0xE037,0x69),(0xE03B,0x4C)):
            for x,y in ((0,0),(255,15),(256,16),(511,257),(65535,65535)):
                for free in (0,1):
                    b,m=base(slot=2);pool(b,free);enemypos(b,2,x,y);b[0x593+19]=77;b[0x5A7+19]=88
                    saved+=run(b,m,entry,trace=entry==0xE01B and y==0)
                    assert bool(m.p&1)==(not free) and m.x==2
                    if free:
                        assert b[0x56B+19]==t and b[0x57F+19]==byte(15,0xFEDE+(t-0x40)//2)
                        assert (b[0x4F3+19]|b[0x507+19]<<8)==((y-16)&65535)
                        assert (b[0x51B+19]|b[0x52F+19]<<8)==x
                        assert (b[0x543+19],b[0x557+19],b[0x593+19],b[0x5A7+19])==(0,249,0,7)
                    else:assert spawned(b)==[]
                    obs.append({'entry':hex(entry),'type':t,'x':x,'y':y,'free':free,'spawned':spawned(b)})
        add(3,'DROP_SPAWNER_POSITION_AND_FIELDS',obs,saved)
    if 4 in chosen:
        obs=[];saved=[]
        for i in range(24):
            for free in (0,1,3):
                b,m=base(slot=2);pool(b,free);t=0x40+2*i;m.a=t
                for slot in range(20):b[0x593+slot]=77;b[0x5A7+slot]=88
                forced=bool(byte(15,0xE0D5+i));target=1 if forced else 19 if free else None
                saved+=run(b,m,0xE08D,trace=i in (8,21) and free==0)
                actual=spawned(b);assert actual==([] if target is None else [(target,t)])
                if target is not None:
                    assert (b[0x57F+target],b[0x543+target],b[0x557+target],b[0x593+target],b[0x5A7+target])==(byte(15,0xFEDE+i)|0x40,0,0,77,88)
                    assert m.x==i
                obs.append({'type':t,'free_slots':free,'forced_slot1':forced,'target':target})
        add(4,'REWARD_SLOT1_REPLACEMENT_AND_RETAINED_FIELDS',obs,saved,'All24 physical profiles. Forced allocation overwrites active slot1 and leaves0593/05A7 untouched. X becomes type index on success; caller must restore slot.')
    if 5 in chosen:
        obs=[];saved=[]
        for suppress in (0,0x10):
            for quiet in (0,0x40):
                for free in (0,3):
                    b,m=base();pool(b,free);b[0x437]=0;b[0x40F]=2;b[0x419]=4;b[0x423]=5;b[0x47D]=suppress;b[0x487]=quiet;b[0x01]=0xAA
                    for call in range(1,9):
                        saved+=run(b,m,0x814C,trace=free==3 and suppress==0 and quiet==0)
                        assert score(b)==(0 if suppress else 20)
                        assert len(spawned(b))==(0 if suppress else min(free,3))
                        assert b[0x40F]==6 and b[0x419]==call%8 and b[0x423]==0
                        assert bool(b[0x469]&0x80)==(call<8)
                        obs.append({'suppressed':bool(suppress),'quiet':bool(quiet),'free':free,'call':call,'state':b[0x40F],'frame':b[0x419],'score':score(b),'drop_count':len(spawned(b))})
                    assert b[0x469]==b[0x473]==b[0x47D]==0 and b[0x01]==(0xAA if quiet else 0x51)
        add(5,'ORDINARY_DEATH_ONCE_ONLY_AND_EIGHT_CALLS',obs,saved,'Original kind00 state dispatcher to death handler and actual score/drop code. Suppression47D10 covers both score and drops;0487bit40 independently silences sound51.')
    if 6 in chosen:
        obs=[];saved=[]
        for hp,damage in ((1,1),(4,8),(64,64)):
            b,m=base();pool(b,3);b[0x437]=hp;b[0x441]=damage;b[0x469]=0xE1
            saved+=run(b,m,0x814C,trace=True);assert b[0x437]==0 and score(b)==0 and spawned(b)==[]
            for call in range(1,9):saved+=run(b,m,0x814C,trace=call in (1,8))
            assert b[0x469]==0 and score(b)==20 and len(spawned(b))==3
            obs.append({'HP':hp,'queued_damage':damage,'death_begins_following_call':True,'death_calls':8,'score':score(b),'drops':spawned(b)})
        add(6,'KILLING_HIT_TO_DEATH_AND_DROPS',obs,saved,'New full integration through previously reviewed hit consumer/recovery, then new death lifecycle. Existing standalone hit tests were not rerun.')
    if 7 in chosen:
        obs=[];saved=[]
        for state in (2,3,4):
            b,m=base();b[0x40F]=state
            for call in range(1,28):
                saved+=run(b,m,0x814C,trace=state==2 and call in (1,3,27))
                assert (b[0x419],b[0x423],b[0x40F])==((call//3)%9,call%3,0 if call==27 else state)
                obs.append({'initial_state':state,'call':call,'state':b[0x40F],'frame':b[0x419]})
        b,m=base();b[0x40F]=5;b[0x469]=0xC3;b[0x47D]=0x40;x=y=128
        xs=(0,2,3,4,5,6,7,8,8);ys=(-8,-6,-4,-2,0,2,4,6,8)
        for call in range(1,19):
            if call%2==0:x+=xs[call//2-1];y+=ys[call//2-1]
            saved+=run(b,m,0x814C,trace=True)
            assert pos(b,0)==(x,y) and b[0x419]==(call//2)%9 and b[0x423]==call%2
            assert b[0x40F]==(1 if call==18 else 5)
            obs.append({'initial_state':5,'call':call,'state':b[0x40F],'frame':b[0x419],'x':x,'y':y})
        assert b[0x47D]&0x40==0
        b,m=base()
        for call in range(1,7):
            saved+=run(b,m,0x814C,trace=True)
            expected=(128,128) if call<3 else (127,128+max(0,call-3)*5)
            assert pos(b,0)==expected and b[0x419]==0 and b[0x40F]==(0 if call<3 else 1),(call,pos(b,0),b[0x419],b[0x40F])
            obs.append({'initial_state':0,'target_x':0,'call':call,'state':b[0x40F],'x':pos(b,0)[0],'y':pos(b,0)[1],'frame':b[0x419]})
        add(7,'KIND00_FRAME_AND_MOVEMENT_TIMELINES',obs,saved,'Normal states2/3/4 each27 selected-AI calls; state5 arcing18 calls,netX43,Y0; state0 walks oncall3 then enters state1 fall because movement36=0.473bit80=0 bypasses unreviewed terrain; not native video-frame timing.')
    if 8 in chosen:
        obs=[];saved=[]
        xs=(-512,-256,-255,-41,-40,-33,-32,-25,-24,-1,0,1,23,24,31,32,39,40,255,256,511)
        ys=(-256,-33,-32,-17,-16,-9,-8,-2,-1,0,1,7,8,15,16,255,256)
        xm=(0x44,0x44,4,0x80,0x40,8,0x88,0x88);ym=(0x11,0x11,1,0x20,0x10,2,0x22,0x22)
        for dx in xs:
            for dy in ys:
                b,m=base();enemypos(b,0,(1024+dx)&65535,(1024+dy)&65535);putword(b,0xD6,1024);putword(b,0xD4,1024)
                saved+=run(b,m,0xE393,trace=dx in (-25,-24,24,32) and dy==0)
                expected=xm[band(dx)]|ym[band(dy,True)];assert b[0x3F]==expected,(dx,dy,b[0x3F],expected)
                obs.append({'dx':dx,'dy':dy,'mask':expected})
        add(8,'TARGET_SNAPSHOT_DISTANCE_BANDS',obs,saved)
    if 9 in chosen:
        obs=[];saved=[];choices=(2,3,2,4,2,3,2,2,5,2,3,2,3,2,4,2)
        for slot in (0,2,7):
            for seed in range(16):
                for dx in (-25,25):
                    b,m=base(slot=slot);b[0x97]=seed;b[0x423+slot]=2;putword(b,0xD6,128-dx);b[0x469+slot]=0xC5
                    saved+=run(b,m,0x814C,trace=slot==2 and seed in (0,6))
                    expected=choices[(seed+slot)&15];assert b[0x40F+slot]==expected and b[0x419+slot]==b[0x423+slot]==0 and b[0x97]==seed
                    assert pos(b,slot)==(128,128)
                    if expected==5:assert b[0x47D+slot]&0x40 and b[0x469+slot]&2
                    obs.append({'slot':slot,'seed97':seed,'dx':dx,'selected_state':expected})
        add(9,'KIND00_BAND_ATTACK_CHOICE',obs,saved,'Signed enemy-minus-target X bands-32..-25 or24..31 choose state via(97+slot)&15; no RNG97 advance or movement in this branch. Explicit slot/seed fixtures, no native distribution claim.')
    if 10 in chosen:
        obs=[];saved=[]
        for count in (1,3,9):
            current=count-1
            for free in (None,0,current):
                for x,y in ((0,0),(47,47),(48,48),(128,128),(208,176),(255,255),(384,384)):
                    b,m=base(10,current);b[0x6F8]=count
                    for i in range(count):b[0x469+i]=0xC0;b[0x47D+i]=0x18
                    if free is not None:b[0x469+free]=0
                    b[0x3DD+current]=0x50;enemypos(b,current,x,y);b[0x45F+current]=0x21
                    saved+=run(b,m,0x8061,trace=count==3 and free is None and x==255)
                    target=current if free is None else free
                    assert m.y==target and b[0x3DD+target]==0x5B and b[0x437+target]==0
                    assert b[0x469+target]==0x90 and b[0x47D+target]==0x18 and b[0x45F+target]==0x21
                    assert all(b[a+target]==0 for a in (0x419,0x42D,0x423,0x40F,0x473))
                    assert word(b,0x189)==min(176,max(48,y)) and word(b,0x18B)==min(208,max(48,x))
                    obs.append({'count':count,'free_slot':free,'target_slot':target,'source_x':x,'source_y':y,'anchor_x':word(b,0x18B),'anchor_y':word(b,0x189)})
        add(10,'SPECIAL_DEATH_ALLOCATION_AND_ANCHOR',obs,saved,'Constructor kind50→5B subtype0; counts1/3/9, camera0 and nonwrapped positive coordinates. Full pool reuses source slot. Reaction flags remain unchanged; coordinates initialize later from shared anchor.')
    if 11 in chosen:
        obs=[];saved=[]
        for companion in (0,1):
            for free in (None,0):
                b,m=base(10,2);b[0x6F8]=3
                for i in range(3):b[0x469+i]=0xC0;b[0x3DD+i]=1
                b[0x3DD+2]=0x50;b[0x437+2]=0
                if companion:b[0x3DD+1]=0x50
                if free is not None:b[0x469+free]=0
                saved+=run(b,m,0x816E,trace=True)
                target=2 if free is None else free;assert b[0x3DD+target]==(0x60 if companion else 0x5B)
                assert bool(b[0x47D+target]&8)==bool(companion) and b[0x01]==0xD2
                if target!=2:assert b[0x469+2]==0
                obs.append({'companion_kind50':bool(companion),'free_slot':free,'target_slot':target,'new_kind':b[0x3DD+target],'reaction':b[0x47D+target]})
        add(11,'KIND50_DEATH_DISPATCH_AND_COMPANION',obs,saved,'Original kind50 dispatcher selects death from HP0, then constructor/scan. Does not execute alive kind50 attack handlers.')
    if 12 in chosen:
        obs=[];saved=[]
        for subtype in (0,1,2,3,4,7,8,9,10,11):
            for scene in (0,0x1B):
                b,m=base(10);pool(b,19);b[0x3DD]=0x5B;b[0x437]=subtype;b[0x469]=0x90;b[0x9A]=scene;b[0xF8]=1;putword(b,0x189,128);putword(b,0x18B,128)
                for call in range(1,129):
                    saved+=run(b,m,0x8000,trace=subtype==0 and scene==0 and call in (1,2,8,128))
                    assert score(b)==20 and b[0x419]==call%8 and b[0x42D]==call//8
                    assert b[0x40F]==(1 if call==128 else 0)
                    if call in (1,2,8,127,128):obs.append({'subtype':subtype,'scene':scene,'call':call,'phase':b[0x40F],'frame':b[0x419],'cycles':b[0x42D],'objects':len(spawned(b))})
                t=byte(10,0x8A91+subtype);assert len(spawned(b))==12+bool(t)
                assert pos(b,0)==(208,byte(10,0x8A9D+subtype))
                if t:assert b[0x56B+1]==t and b[0x57F+1]==byte(15,0xFEDE+(t-0x40)//2)|0x40
                for call in range(1,101):
                    saved+=run(b,m,0x8000,trace=subtype==0 and scene==0x1B and call in (1,99,100))
                    assert bool(b[0x469]&0x80)==(call<100)
                assert b[0xF8]==(0x21 if scene==0x1B else 1)
                obs.append({'subtype':subtype,'scene':scene,'delay_calls':100,'deactivated':True,'reward_type':t,'F8':b[0xF8]})
        add(12,'SPECIAL5B_FULL_BURST_REWARD_AND_DELAY',obs,saved,'Actual top-level AI dispatcher→kind5B full128+100-call lifecycle, scoreonce, four triple attempts in firstcycle, optional forcedslot1 reward. Controlled D8/97/OAM, no native timing or boss-name claim.')
    if 13 in chosen:
        obs=[];saved=[]
        for suppress in (0,8):
            for free in (0,3,19):
                b,m=base(10);pool(b,free);b[0x3DD]=0x60;b[0x469]=0x90;b[0x47D]=suppress;b[0xF8]=0x25;b[0x70A]=5;b[0x70B]=9;putword(b,0x189,128);putword(b,0x18B,128)
                for call in range(1,129):
                    saved+=run(b,m,0x8000,trace=free==19 and call in (1,8,128))
                    assert score(b)==20 and b[0x419]==call%8 and b[0x42D]==call//8
                    if call in (1,8,128):obs.append({'suppress':suppress,'free':free,'call':call,'objects':len(spawned(b))})
                assert len(spawned(b))==min(free,24) and b[0x469]==b[0x70A]==b[0x70B]==0
                assert b[0xF8]==(0x25 if suppress else 0xA5)
                obs.append({'suppress':suppress,'free':free,'F8':b[0xF8],'objects':len(spawned(b)),'deactivated':True})
        add(13,'SPECIAL60_FULL_LIFECYCLE_AND_CAPACITY',obs,saved,'Eight triple attempts in first eight-callcycle; at most19 poolslots.128calls; bit08 suppressesF8bit80. No final reward table. Full original lifecycle in controlled non-terrain fixture.')
    if 14 in chosen:
        obs=[];saved=[]
        for selected in (0,0x0B,0x0C):
            for slot0counter in (0,1):
                for slot3counter in (0,0xC9):
                    b,m=base();b.regs[7]=8;b[0x6BD]=selected;b[0x593]=slot0counter;b[0x596]=slot3counter;putword(b,0xD6,96);putword(b,0xD4,128);putword(b,0xCB,128);putword(b,0xC9,128)
                    hold=selected==0x0B and slot0counter!=0
                    saved+=run(b,m,0xABA8,trace=True);assert word(b,0xD6)==(96 if hold else 128)
                    saved+=run(b,m,0xE393,trace=True);assert b[0x3F]==(0x64 if hold else 0xA0)
                    obs.append({'selected':selected,'counter0593':slot0counter,'counter0596':slot3counter,'target_held':hold,'distance_mask':b[0x3F]})
        add(14,'PLAYER_SNAPSHOT_TO_AI_TARGET',obs,saved,'New integration of already-reviewed snapshot tail with newly reviewed AI distance consumer. Hold condition uses0593, not decoy-slot3 counter0596; does not prove all Twin Power targeting behavior.')
    if 15 in chosen:
        obs=[];saved=[]
        dirs=(2,0,3,1)
        for d8 in range(4):
            for seed in range(32):
                for carry in (0,1):
                    b,m=base(10);b[0x42D]=1;b[0xD8]=d8;b[0x97]=seed;b[0x24D]=0x10;b[0x469]=0x90;putword(b,0x189,128);putword(b,0x18B,128);m.p=(m.p&~1)|carry
                    idx=((d8|0x10)+seed+carry)&31;dx=byte(10,0x8AF5+idx);dy=byte(10,0x8AF6+idx);direction=dirs[d8]
                    expected=(128+(dx if direction&1 else -dx),128+(-dy if direction&2 else dy))
                    saved+=run(b,m,0x8AA9,trace=seed in (0,31) and d8==0)
                    assert pos(b,0)==expected and b[0x469]&3==direction,(d8,seed,carry,idx,pos(b,0),expected)
                    obs.append({'D8':d8,'seed97':seed,'incoming_carry':carry,'offset_pair_index':idx,'x':expected[0],'y':expected[1]})
        add(15,'SCATTER_OVERLAPPING_PAIRS_AND_CARRY',obs,saved,'Cycle042D=1 avoids dropcallee so entrycarry reaches ADC unchanged. All32 overlapping bytepairs addressed, two carry values; explicit024D OAMbyte input, no random-independence claim.')
    groups.sort(key=lambda g:g['number']);complete=[g['number'] for g in groups]==list(range(1,16));write_json(partial,{'rom_sha256':sha,'results':groups,'traces':traces,'complete':complete})
    if complete:
        result={'stage':'02G','rom_sha256':sha,'groups':len(groups),'passed_groups':len(groups),'vectors':sum(g['vector_count'] for g in groups),'trace_rows':len(traces),'results':groups,'native_NES':'NOT_TESTED','old_suites_rerun':False}
        write_json(ROOT/'analysis/cpu_stage02G.json',result)
        write_csv(ROOT/'analysis/cpu_stage02G_vectors.csv',[{'group':g['id'],'data':json.dumps(v,sort_keys=True)} for g in groups for v in g['observations']]);write_csv(ROOT/'analysis/cpu_stage02G_trace.csv',traces)
        print(json.dumps({k:v for k,v in result.items() if k!='results'},indent=2))
if __name__=='__main__':main()
