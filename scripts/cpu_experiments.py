#!/usr/bin/env python3
"""Isolated py65 experiments; deliberately NOT a NES emulator or timing model."""
import argparse,json,sys
from pathlib import Path
from baseline import ROOT,verified_rom,write_json,write_csv
sys.path.insert(0,str(ROOT/'tools/vendor'))
from py65.devices.mpu6502 import MPU

class Bus:
    def __init__(self,prg,fill=0):
        self.prg=prg;self.ram=bytearray([fill]*2048);self.io={};self.bank_select=0
        self.regs=[0]*8;self.regs[6:]=[4,5];self.writes=[];self.status_reads=0;self.pc=0
    def __getitem__(self,a):
        a&=65535
        if a<0x2000:return self.ram[a&2047]
        if a==0x2002:
            v=0x80 if self.status_reads%2==0 else 0;self.status_reads+=1;return v
        if a>=0x8000:
            mode=(self.bank_select>>6)&1;windows=[self.regs[6],self.regs[7],14,15] if not mode else [14,self.regs[7],self.regs[6],15]
            bank=windows[(a-0x8000)//8192]&15;return self.prg[bank*8192+(a&8191)]
        return self.io.get(a,0)
    def __setitem__(self,a,v):
        a&=65535;v&=255
        if a<0x2000:self.ram[a&2047]=v
        else:
            self.writes.append({'pc':f'0x{self.pc:04X}','address':f'0x{a:04X}','value':f'0x{v:02X}'})
            if a>=0x8000:
                reg=a&0xE001
                if reg==0x8000:self.bank_select=v
                elif reg==0x8001:self.regs[self.bank_select&7]=v
                else:self.io[reg]=v
            else:self.io[a]=v

def setup(prg,pc,fill=0):
    bus=Bus(prg,fill);m=MPU(memory=bus,pc=pc);m.p=0x24;return bus,m
def subroutine_frame(bus,m):
    m.sp=0xFD;bus.ram[0x1FE]=0xFF;bus.ram[0x1FF]=0x7F
def interrupt_frame(bus,m):
    m.sp=0xFC;bus.ram[0x1FD]=0x24;bus.ram[0x1FE]=0;bus.ram[0x1FF]=0x80
def run(bus,m,stop,inject=None,limit=20000):
    trace=[]
    for n in range(limit):
        if m.pc==stop:return trace
        bus.pc=m.pc
        if inject:inject(bus,m)
        trace.append({'step':n,'pc':f'0x{m.pc:04X}','a':m.a,'x':m.x,'y':m.y,'sp':m.sp,'p':m.p,'r6':bus.regs[6],'r7':bus.regs[7]})
        if m.disassemble[bus[m.pc]][0]=='???':raise ValueError(f'Unsupported opcode at {m.pc:X}')
        m.step()
    raise TimeoutError(f'PC={m.pc:04X}; did not reach stop={stop:04X}')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('rom');a=ap.parse_args();b,h=verified_rom(a.rom);prg=b[16:16+131072]
    results=[];all_traces=[]
    def record(name,bus,m,tr,observation):
        results.append({'id':name,'class':'CPU_TEST','status':'PASS','steps':len(tr),'observations':observation,'hardware_writes':bus.writes})
        all_traces.extend(dict(experiment=name,**x) for x in tr)
    bus,m=setup(prg,0xF010,0xA5);tr=run(bus,m,0xF094)
    untouched=[i for i,v in enumerate(bus.ram) if v!=0]
    assert untouched==[0x100]+list(range(0x300,0x308)),untouched
    assert bus.regs[6:]==[4,5] and bus.bank_select==7
    assert bus.io[0xA000]==0 and bus.status_reads==9
    record('CPU01_RESET_TO_RAM_CLEAR',bus,m,tr,{'retained_ram':[f'0x{x:04X}' for x in untouched],'R6':4,'R7':5,'status_reads':bus.status_reads,'stop_before_call':'PRG0F:F094'})
    for marker in (0x68,0xA5):
        bus,m=setup(prg,0xD60C,0xA5);bus.ram[0x100]=marker;tr=run(bus,m,0xD623)
        expected=[0xA5]*6 if marker==0x68 else [0x20]*4+[0x21,0x20]
        assert list(bus.ram[0x300:0x306])==expected
        assert bus.ram[0x100]==0x68
        record(f'CPU02_RETENTION_MARKER_{marker:02X}',bus,m,tr,{'retained_block':expected,'stop_before_unreviewed_call':'PRG0E:D623'})
    points=[None,0xD6C3,0xD6C5,0xD6C7,0xD6CA,0xD6CD,0xD6CF,0xD6D1]
    for selector,val in [(6,12),(7,13)]:
        for point in points:
            bus,m=setup(prg,0xD6C3);subroutine_frame(bus,m);m.a=val;m.x=selector;fired=[False]
            def inject(bus,m):
                if point is not None and m.pc==point and not fired[0]:
                    fired[0]=True;bus[0x8000]=2;bus[0x8001]=0x22;bus.ram[0xA6]=(bus.ram[0xA6]+1)&255
            tr=run(bus,m,0x8000,inject)
            assert bus.regs[selector]==val
            assert (m.a,m.x,m.y)==(val,selector,0)
            assert point is None or fired[0]
            record(f'CPU03_MAPPER_R{selector}_INTERFERENCE_{point:04X}' if point else f'CPU03_MAPPER_R{selector}_BASELINE',bus,m,tr,{'target_register':selector,'final_bank':val,'synthetic_interference_at':f'0x{point:04X}' if point else None,'actual_interrupt_delivery':False})
    for flag in (0,1):
        bus,m=setup(prg,0xF24B);subroutine_frame(bus,m);m.y=0;bus.ram[0x143:0x163]=bytes(range(32));bus.ram[0x6EE]=flag
        tr=run(bus,m,0x8000);values=[int(x['value'],16) for x in bus.writes if x['address']=='0x2007']
        assert values==list(range(32));assert m.sp==0xFF;assert bus.ram[0x6EE]==(0xFF if flag else 0)
        record(f'CPU04_PALETTE_FLAG_{flag}',bus,m,tr,{'ppu_data_sequence':values,'stack_after_return':m.sp,'flag_after':bus.ram[0x6EE]})
    for command in range(32):
        bus,m=setup(prg,0xF156);m.y=0;bus.ram[0xA0]=command
        pc=0xF16A+(command&30);target=bus[pc]|bus[pc+1]<<8
        tr=run(bus,m,target);assert bus.ram[0xA0]==0
        record(f'CPU05_DISPATCH_{command:02X}',bus,m,tr,{'command':command,'target':f'0x{target:04X}','command_after':0})
    for enabled in (0,1):
        bus,m=setup(prg,0xF0BB);interrupt_frame(bus,m);m.a=0x3C;m.x=0x7D;m.y=0xB9
        bus.ram[0x44:0x4A]=bytes([0x10,0x20,0x30,0x40,0x50,0x60]);bus.ram[0x4A]=0x88
        bus.ram[0x5F]=0x1E;bus.ram[0x96]=enabled;bus.ram[0xDC:0xDE]=bytes([0xC2,0xF7]);bus.ram[0xA6]=4
        tr=run(bus,m,0x8000)
        assert (m.a,m.x,m.y)==(0x3C,0x7D,0xB9)
        assert bus.regs==[0x10,0x20,0x30,0x40,0x50,0x60,4,5]
        assert bus.ram[0xA6]==5 and bus.io[0x4014]==2
        if enabled:assert list(bus.ram[0xE5:0xE7])==[0xC2,0xF7] and 0xE001 in bus.io
        record(f'CPU06_NMI_IRQ_ENABLED_{enabled}',bus,m,tr,{'registers_preserved':True,'CHR_registers':bus.regs[:6],'prg_banks_preserved':bus.regs[6:],'epoch_after':bus.ram[0xA6],'OAM_DMA_page':bus.io[0x4014],'conditions':'A0=0,D9=0,68=0,6A=0,96 in {0,1}'})
    bus,m=setup(prg,0xF4CA);subroutine_frame(bus,m);m.a=0x11;m.x=0x22;m.y=0x33
    bus.ram[0x4EA:0x4ED]=bytes([0x00,0x06,0x09])
    stub=bytes.fromhex('A2 06 A9 0C 20 C3 D6 A9 55 A2 66 A0 77 18 60');bus.ram[0x600:0x600+len(stub)]=stub
    tr=run(bus,m,0x8000)
    assert bus.regs[6:]==[4,5] and (m.a,m.x,m.y)==(0x55,0x66,0x77) and not (m.p&1)
    assert list(bus.ram[0x4ED:0x4EF])==[5,4]
    record('CPU07_FAR_CALL_WITH_RAM_STUB',bus,m,tr,{'synthetic_RAM_callee_hex':stub.hex(),'target_bank':9,'restored_banks':bus.regs[6:],'callee_outputs_preserved':[m.a,m.x,m.y],'carry_after':m.p&1,'nesting_tested':False})
    bus,m=setup(prg,0xF7B1);interrupt_frame(bus,m);m.a=0x44;m.x=0x55;m.y=0x66;bus.ram[0xE5:0xE7]=bytes([0x34,0xF8])
    tr=run(bus,m,0x8000)
    assert (m.a,m.x,m.y)==(0x44,0x55,0x66) and bus.ram[0xA6]==1
    assert [w['address'] for w in bus.writes]==['0xE000','0xE001']
    record('CPU08_IRQ_DISPATCH_AND_RETURN',bus,m,tr,{'registers_preserved':True,'dispatch_target':'F834','epoch_after':1})
    write_json(ROOT/'analysis/cpu_experiments.json',{'emulator':'py65 1.2.0 NMOS 6502 core','full_NES_emulation':False,
        'limitations':['No PPU rendering, scanline or APU timing','PPUSTATUS returns alternating 80/00 on reads','Mapper logic is a deliberately bounded test double','Interrupt interference is explicitly injected, not cycle-scheduled','Only selected routines and stated preconditions exercised'],
        'experiment_count':len(results),'passed':len(results),'results':results})
    write_csv(ROOT/'analysis/cpu_trace.csv',all_traces)
    print(json.dumps({'experiments':len(results),'passed':len(results),'trace_rows':len(all_traces),'full_NES_validation':False},indent=2))
if __name__=='__main__':main()
