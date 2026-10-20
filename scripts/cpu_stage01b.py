#!/usr/bin/env python3
"""Execute original 6502 bytes against explicit serial-controller and MMC3 test doubles.

No ROM bytes are patched. Skipped callees are listed as boundary stubs in every affected group.
This is not cycle-accurate NES emulation; NMI delivery is injected at selected instruction boundaries.
"""
import argparse,json
from baseline import ROOT,verified_rom,write_json,write_csv
from cpu_experiments import Bus,MPU,subroutine_frame,run

class ControllerBus(Bus):
    def __init__(self,prg,samples=None):
        super().__init__(prg);self.samples=samples or [[0x40]*8];self.sample=-1;self.bit=0
        self.strobe=0;self.controller_reads=[];self.latches=0
    def __getitem__(self,a):
        if a==0x4016:
            assert not self.strobe and self.sample>=0,'Unexpected unstroked/high-strobe read'
            assert self.bit<8,'Unexpected ninth serial read in these routines'
            value=self.samples[min(self.sample,len(self.samples)-1)][self.bit]
            self.controller_reads.append({'sample':self.sample,'serial_index':self.bit,'value':value})
            self.bit+=1;return value
        return super().__getitem__(a)
    def __setitem__(self,a,v):
        super().__setitem__(a,v)
        if a==0x4016:
            if self.strobe and not (v&1):self.sample+=1;self.bit=0;self.latches+=1
            self.strobe=v&1

def serial(mask,line=1):return [0x40|(line if mask&(0x80>>i) else 0) for i in range(8)]
def setup(prg,pc,samples=None,r7=5):
    bus=ControllerBus(prg,samples);bus.regs[7]=r7;m=MPU(memory=bus,pc=pc);m.p=0x24
    subroutine_frame(bus,m);return bus,m
def bank_at(bus,pc):
    return bus.regs[6] if 0x8000<=pc<0xA000 else bus.regs[7] if 0xA000<=pc<0xC000 else 14 if pc<0xE000 else 15
def return_stub(bus,m):
    m.sp=(m.sp+1)&255;lo=bus[0x100+m.sp]
    m.sp=(m.sp+1)&255;hi=bus[0x100+m.sp]
    m.pc=((lo|(hi<<8))+1)&65535
def execute(bus,m,stops,stubs=None,before=None,limit=30000,trace=True):
    rows=[];calls=[];stubs=stubs or {}
    for n in range(limit):
        if m.pc in stops:return rows,calls
        if before:before(bus,m)
        bus.pc=m.pc;key=(bank_at(bus,m.pc),m.pc)
        if trace:rows.append({'step':n,'bank':f'{key[0]:02X}','pc':f'0x{m.pc:04X}','a':m.a,'x':m.x,'y':m.y,'sp':m.sp,'p':m.p,'r6':bus.regs[6],'r7':bus.regs[7]})
        if key in stubs:
            calls.append({'bank':f'{key[0]:02X}','cpu':f'0x{key[1]:04X}'})
            callback=stubs[key]
            if callback:callback(bus,m)
            return_stub(bus,m);continue
        assert m.disassemble[bus[m.pc]][0]!='???',key
        m.step()
    raise TimeoutError(f'PC={m.pc:04X}, stops={stops}')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('rom');a=ap.parse_args();b,_=verified_rom(a.rom);prg=b[16:0x20010]
    groups=[];traces=[];vectors=[]
    def add(name,observations,rows=None,stubs=None):
        groups.append({'id':name,'status':'PASS','vector_count':len(observations),'observations':observations,'boundary_stubs':stubs or []})
        for v in observations:vectors.append({'group':name,'data':json.dumps(v,sort_keys=True)})
        if rows:traces.extend(dict(experiment=name,**r) for r in rows)
    def idle_audio(bus,m):
        m.pc=0xCC84;subroutine_frame(bus,m);execute(bus,m,{0x8000},trace=False)
        bus.ram[0]=bus.ram[1]=0xFF;bus.writes=[]

    obs=[];saved=[]
    for mask in range(256):
        bus,m=setup(prg,0xD977,[serial(mask)]);bus.ram[0x1F]=0xA5;m.y=0x77
        rows,_=execute(bus,m,{0x8000},trace=mask in [0,1,0x80,0x91,255])
        assert m.a==bus.ram[0x1F]==mask and m.x==0 and m.y==0x77
        assert bus.latches==1 and len(bus.controller_reads)==8
        assert [int(w['value'],16) for w in bus.writes]==[1,0]
        obs.append({'input_mask':mask,'result':m.a,'reads':8});saved+=rows
    add('B_CPU01_SERIAL_ALL_MASKS',obs,saved)

    obs=[]
    for line in (1,2,3):
        for bit in range(8):
            mask=0x80>>bit;sample=[0xFC|(line if i==bit else 0) for i in range(8)]
            bus,m=setup(prg,0xD977,[sample]);execute(bus,m,{0x8000},trace=False)
            assert m.a==mask;obs.append({'low_bus_bits':line,'serial_index':bit,'mask':m.a})
    bus,m=setup(prg,0xD977,[[0xFC]*8]);execute(bus,m,{0x8000},trace=False);assert m.a==0
    obs.append({'all_high_bus_bits_set':True,'mask':m.a});add('B_CPU02_LOW_TWO_DATA_BITS',obs)

    obs=[];saved=[]
    cases=[(0,0,0),(0,0x91,0x91),(0x91,0x91,0x91),(0x91,0,0),(0x80,0x81,0x81),
           (0,0xFF,0),(0,0xFF,0x81),(0x81,0x81,0x80),(0,1,2),(0xFF,0xFF,0xFF),(0,2,1)]
    for i,(old,s1,s2) in enumerate(cases):
        bus,m=setup(prg,0xCC84,[serial(s1),serial(s2)]);idle_audio(bus,m)
        bus.regs[6:]=[2,13] if i&1 else [4,5];banks=list(bus.regs[6:]);m.pc=0xD90C;subroutine_frame(bus,m)
        m.x=0x55;m.y=0xAA;bus.ram[0x20]=old;bus.ram[0x21]=0x5A;bus.ram[0x713]=0xC3
        rows,_=execute(bus,m,{0x8000},trace=i in (1,5,6))
        held=s1&s2;pressed=held&(~old&255)
        assert bus.ram[0x20]==held and bus.ram[0x1F]==pressed
        assert bus.ram[0x713]==old and bus.ram[0x714]==0xC3
        assert bus.ram[0x21]==((0x5A<<1)|(held>>7))&255
        assert (m.x,m.y)==(0x55,0xAA) and bus.regs[6:]==banks and bus.ram[0x95]==1
        assert bus.latches==2 and len(bus.controller_reads)==16
        obs.append({'old':old,'sample1':s1,'sample2':s2,'held':held,'pressed':pressed,'A_history':bus.ram[0x21],'restored_banks':banks,'all_audio_code_executed':True});saved+=rows
    add('B_CPU03_FULL_UPDATE_IDLE_AUDIO',obs,saved)

    obs=[];saved=[]
    for flag in (0,1):
        for loops in (1,3,17):
            bus,m=setup(prg,0xCC84,[serial(0x10)]*2);idle_audio(bus,m)
            m.pc=0xD90C;subroutine_frame(bus,m);m.x=0x55;m.y=0xAA
            bus.ram[0x95]=1;bus.ram[0x96]=flag;bus.ram[0x97]=0x7E;bus.ram[0xDC:0xDE]=bytes([0x34,0xF8]);count=[0];fired=[False]
            def before(bus,m):
                if m.pc==0xD918 and not fired[0]:
                    count[0]+=1
                    if count[0]==loops:fired[0]=True;m.nmi()
            rows,_=execute(bus,m,{0x8000},before=before)
            expected=0x7E
            for _ in range(loops):z=(expected+1)&255;expected=((z<<1)|(z>>7))&255
            assert fired[0] and bus.ram[0x97]==expected and bus.ram[0x95]==1
            assert (m.x,m.y)==(0x55,0xAA) and bus.ram[0x1F]==0x10
            obs.append({'NMI_96':flag,'wait_updates':loops,'timing_state':expected,'actual_NMI_handler_executed':True,'delivery':'synthetic at D918; no PPU clock'});saved+=rows
    bus,m=setup(prg,0xD90C);bus.ram[0x95]=1
    for _ in range(200):bus.pc=m.pc;m.step()
    assert 0xD910<=m.pc<=0xD91A and not bus.writes
    obs.append({'no_NMI_after_200_instructions':'still waiting','pc':f'{m.pc:04X}'})
    add('B_CPU04_NMI_HANDSHAKE_AND_TIMING',obs,saved)

    obs=[]
    for value in range(256):
        bus,m=setup(prg,0xD910);bus.ram[0x97]=value
        execute(bus,m,{0xD918},trace=False);z=(value+1)&255;expected=((z<<1)|(z>>7))&255
        assert bus.ram[0x97]==expected
        obs.append({'before':value,'after':expected})
    add('B_CPU05_WAIT_MIXER_ALL_STATES',obs)
    obs=[]
    for value in range(256):
        for x in (0,1,0x7F,0x80,0xFE,0xFF):
            bus,m=setup(prg,0xD9CB);bus.ram[0x97]=value;m.x=x;m.y=0x65
            execute(bus,m,{0x8000},trace=False);expected=((((value+x)&255)^0xAA)+0xBD)&255
            assert bus.ram[0x97]==expected and m.x==x and m.y==0x65
            obs.append({'before':value,'x':x,'after':expected})
    add('B_CPU06_X_MIXER_BOUNDARIES',obs)

    obs=[];saved=[]
    for entry,target,r7,r6 in [(0xCF50,0xA499,9,4),(0xD0BA,0xA006,8,3),(0xD0D2,0xA000,9,4),
                              (0xD0DC,0xA078,7,3),(0xD0F3,0xA07B,7,3),(0xD110,0xA00C,8,6)]:
        bus,m=setup(prg,entry);bus.ram[0x3B9]=3
        rows,_=execute(bus,m,{target});assert bus.regs[6:]==[r6,r7]
        obs.append({'entry':f'{entry:04X}','first_switchable_target':f'{target:04X}','R6':r6,'R7':r7});saved+=rows
    add('B_CPU07_BANKED_WRAPPER_ENTRIES',obs,saved)

    expected=[0xD90C,0xD0B7,0xD0BA,0xD0DC,0xD0D2,0xD107,0xD63B,0xD110,
              0xD90C,0xD0B7,0xD0BA,0xD0F3,0xD0D2,0xD107,0xD63B,0xD9CB,0xD110,
              0xD90C,0xD0B7,0xD0BA,0xD0DC,0xD107,0xD0D2,0xD63B,0xD110,
              0xD90C,0xD0B7,0xD0BA,0xD0F3,0xD107,0xD0D2,0xD63B,0xD9CB,0xD110]
    bus,m=setup(prg,0xD046);stubs={(14,x):None for x in set(expected)}
    rows,calls=execute(bus,m,{0xD0B4},stubs=stubs)
    assert [int(x['cpu'],16) for x in calls]==expected
    m.step();assert m.pc==0xD046
    add('B_CPU08_FOUR_PHASE_CALL_ORDER',[{'calls':[f'{x:04X}' for x in expected],'handshakes':4,'mixer_calls':2,'returns_to':'D046','callee_effects_exercised':False}],rows,[f'0E:{x:04X}' for x in sorted(set(expected))])

    obs=[];saved=[]
    for ce,d3,pressed,count,target in [(0,0,0,3,0x8000),(0,0,0x10,3,0xD3C4),(0,0x80,0x10,3,0x8000),(0x80,0,0,2,0xD17A),(0x80,0,0,1,0xD487)]:
        bus,m=setup(prg,0xD39F);bus.ram[0xCE]=ce;bus.ram[0xD3]=d3;bus.ram[0x1F]=pressed;bus.ram[0x30E]=count
        rows,_=execute(bus,m,{0x8000,0xD3C4,0xD17A,0xD487},stubs={(15,0xE154):None})
        assert m.pc==target and bus.ram[0x30E]==count-(1 if ce&128 else 0)
        obs.append({'CE':ce,'D3':d3,'pressed':pressed,'counter_before':count,'counter_after':bus.ram[0x30E],'target':f'{target:04X}'});saved+=rows
    add('B_CPU09_CONTROL_GATE',obs,saved,['0F:E154 palette fade/render disable boundary'])

    obs=[];saved=[]
    for effect in (8,0):
        bus,m=setup(prg,0xD3C4);palette=bytes((i+3)&63 for i in range(32));bus.ram[0x143:0x163]=palette
        bus.ram[0x47]=0x24;bus.ram[0x48]=0x35;bus.ram[0x6BD]=effect
        def scroll_stub(bus,m):m.a=0x2A
        stubs={(15,0xE15E):None,(15,0xE105):None,(7,0xA0B7):None,(7,0xA0B4):None,(15,0xF78B):scroll_stub}
        rows,_=execute(bus,m,{0xD046},stubs=stubs)
        expected=bytearray(palette)
        if effect!=8:expected[0x15]=bus[0xFFB5]
        assert bus.ram[0x143:0x163]==expected and bus.ram[0x47:0x49]==bytes([0x24,0x35])
        assert m.sp==0xFF and bus.ram[0xA1]==1 and bus.ram[0x58]==0x2A
        obs.append({'06BD':effect,'saved_CHR_restored':True,'palette_after':list(expected),'SP_after_discard':m.sp,'target':'D046'});saved+=rows
    add('B_CPU10_OVERLAY_STACK_REENTRY',obs,saved,['0F:E15E','0F:E105','07:A0B7','07:A0B4','0F:F78B returns A=2A'])

    obs=[]
    for entry,stop,table in [(0xD178,0xD182,0xD25F),(0xD19A,0xD1A1,0xD27F),(0xD1AA,0xD1C0,0xD23F)]:
        for index in range(32):
            bus,m=setup(prg,entry);bus.ram[0x9A]=index
            execute(bus,m,{stop},stubs={(15,0xE154):None,(14,0xD36D):None,(14,0xD37F):None},trace=False)
            result=m.a if stop==0xD1C0 else bus.ram[0x9A]
            assert result==bus[table+index]
            obs.append({'entry':f'{entry:04X}','index':index,'mapped':result,'stop':f'{stop:04X}'})
    add('B_CPU11_SCENE_ROUTE_TABLES',obs,stubs=['0F:E154','0E:D36D','0E:D37F; advance path only'])
    obs=[];saved=[]
    for cycle in (0,1,2,3,4):
        bus,m=setup(prg,0xD1AA);bus.ram[0x9A]=0x1B;bus.ram[0x30C]=cycle
        stubs={(15,0xE154):None,(14,0xD36D):None,(14,0xD37F):None,(9,0xA012):None,(8,0xA00F):None,(14,0xD2F7):None}
        rows,calls=execute(bus,m,{0xD1FF},stubs=stubs)
        expected=3 if cycle==3 else cycle+1
        assert bus.ram[0x30C]==expected and bus.ram[0x9A]==0
        assert any(x['bank']=='08' for x in calls)==(expected>=3)
        obs.append({'cycle_before':cycle,'cycle_after':expected,'scene_after':0,'bank08_A00F_called':expected>=3,'cycle4_is_out_of_normal_range_probe':cycle==4});saved+=rows
    add('B_CPU12_END_OF_CYCLE_ROUTE',obs,saved,['0F:E154','0E:D36D','0E:D37F','09:A012','08:A00F','0E:D2F7'])

    obs=[];saved=[]
    for choice in (0,1):
        for pressed in (0,1,2,4,8,0x20,0x40,0x80,0x10,0x0C,0x2C):
            bus,m=setup(prg,0xD535);bus.ram[0x2C]=choice;bus.ram[0x1F]=pressed
            rows,_=execute(bus,m,{0xD585,0xD588},stubs={(14,0xD90C):None,(14,0xD677):None,(14,0xD63B):None})
            if pressed&0xD0:assert m.pc==0xD588;new=choice
            else:
                new=choice
                if pressed&4 and new!=1:new+=1
                if pressed&8 and new!=0:new-=1
                if pressed&0x20:new^=1
                assert m.pc==0xD585 and bus.ram[0x2C]==new
            obs.append({'choice_before':choice,'pressed':pressed,'choice_after':bus.ram[0x2C],'confirm':m.pc==0xD588});saved+=rows
    add('B_CPU13_COUNTER_ZERO_MENU_INPUT',obs,saved,['0E:D90C supplies pre-set 1F','0E:D677 cursor','0E:D63B OAM hide'])
    obs=[];saved=[]
    for choice,target in [(0,0xD19A),(1,0xF010)]:
        bus,m=setup(prg,0xD588);bus.ram[0x2C]=choice
        stubs={(14,0xD62D):None,(15,0xE154):None,(14,0xD90C):None,(14,0xD38B):None,(15,0xED80):None}
        rows,_=execute(bus,m,{0xD19A,0xF010},stubs=stubs);assert m.pc==target
        obs.append({'choice':choice,'terminal_target':f'{target:04X}'});saved+=rows
    add('B_CPU14_COUNTER_ZERO_MENU_CONFIRM',obs,saved,['0E:D62D','0F:E154','0E:D90C','0E:D38B','0F:ED80'])

    obs=[];saved=[]
    for choice in (0,1):
        for pressed in (0,1,2,4,8,0x20,0x40,0x80,0x10,0x23,0x91):
            bus,m=setup(prg,0xA630,r7=9);bus.ram[0x2C]=choice;bus.ram[0x1F]=pressed;bus.ram[0x99]=0x55
            rows,_=execute(bus,m,{0x8000},stubs={(14,0xC74C):None})
            if pressed&0x90:
                assert m.p&1 and bus.ram[0x2C]==choice and bus.ram[0x99]==0x55
            else:
                new=choice^(1 if pressed&0x23 else 0)
                assert not(m.p&1) and bus.ram[0x2C]==new and bus.ram[0x99]==33
                assert list(bus.ram[0x280:0x284])==[0x98,0x2D,1,[0x38,0x88][new]]
            obs.append({'choice_before':choice,'pressed':pressed,'choice_after':bus.ram[0x2C],'carry':m.p&1,'OAM_count':bus.ram[0x99]});saved+=rows
    add('B_CPU15_FRONT_END_CHOICE_CURSOR',obs,saved,['0E:C74C supplies pre-set 1F; actual cursor and OAM hide execute'])

    obs=[]
    for entry,count,press_at,expected in [(0xF6CC,1,None,1),(0xF6CC,2,None,2),(0xF6CC,0,None,256),
                                       (0xF6D3,5,3,3),(0xF6D3,2,None,2),(0xF6D3,0,None,256),(0xF6E0,7,4,4)]:
        bus,m=setup(prg,entry);m.x=count;calls=[0]
        def supply(bus,m):calls[0]+=1;bus.ram[0x1F]=0x10 if calls[0]==press_at else 0
        execute(bus,m,{0x8000},stubs={(14,0xD90C):supply},trace=False)
        assert calls[0]==expected
        obs.append({'entry':f'{entry:04X}','initial_X':count,'press_update':press_at,'updates':calls[0]})
    add('B_CPU16_WAIT_HELPERS',obs,stubs=['0E:D90C scripted newly pressed input'])

    obs=[]
    for flag,timer,mode in [(0,0,0),(1,2,0x10),(0xFF,2,0x10),(0xFF,1,0)]:
        bus,m=setup(prg,0xE2A3);bus.ram[0x6EE]=flag;bus.ram[0x3D5]=timer;bus.ram[0xD9]=mode
        bus.ram[0x1A6:0x1C6]=bytes(range(32));execute(bus,m,{0x8000},trace=False)
        if flag==0xFF:
            assert bus.ram[0x6EE]==0 and bus.ram[0xA0]==0x0E
            assert all(bus.ram[0x143+i]==i for i in range(32) if 0x143+i not in (0x155,0x159))
        else:assert bus.ram[0x6EE]==flag and bus.ram[0xA0]==0
        assert bus.ram[0x3D5]==max(timer-1,0)
        expected1=0x30 if timer and mode&0x10 else bus[0xFFB3]
        expected2=0x30 if timer and mode&0x10 else bus[0xFFB6]
        assert bus.ram[0x155]==expected1 and bus.ram[0x159]==expected2
        obs.append({'flag_before':flag,'timer_before':timer,'mode':mode,'flag_after':bus.ram[0x6EE],'command_after':bus.ram[0xA0],'palette155':expected1,'palette159':expected2})
    add('B_CPU17_PALETTE_EFFECT_HANDSHAKE',obs)
    obs=[]
    for y,expected in [(0,4),(0xEB,0xEF),(0xEC,0),(0xEF,3),(0xF0,4),(0xFB,15),(0xFC,0),(0xFF,3)]:
        for flag in (0,1,2,3):
            bus,m=setup(prg,0xE2E2);bus.ram[0x58]=y;bus.ram[0x3D6]=flag
            execute(bus,m,{0x8000},trace=False);assert bus.ram[0x58]==(expected if flag&1 else y)
            obs.append({'scroll_before':y,'effect_flag':flag,'scroll_after':bus.ram[0x58]})
    add('B_CPU18_SCROLL_WRAP_BOUNDARIES',obs)
    result={'emulator':'py65 1.2.0 NMOS 6502','full_NES_emulation':False,'groups':len(groups),'vectors':len(vectors),'passed_groups':len(groups),
            'limitations':['Serial samples are supplied by a test double; no DMC DMA corruption model','NMI executes original handler but delivery is manually injected, not PPU-timed','Boundary-stub cases prove caller control flow only, not callee gameplay','Audio code runs only for the explicitly initialized idle state','No rendered screen, native emulator state or actual MesenCE import'],
            'results':groups}
    write_json(ROOT/'analysis/cpu_stage01B.json',result);write_csv(ROOT/'analysis/cpu_stage01B_trace.csv',traces);write_csv(ROOT/'analysis/cpu_stage01B_vectors.csv',vectors)
    print(json.dumps({'groups':len(groups),'vectors':len(vectors),'trace_rows':len(traces),'status':'PASS','full_NES':False},indent=2))
if __name__=='__main__':main()
