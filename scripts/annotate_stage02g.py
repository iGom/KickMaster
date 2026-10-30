#!/usr/bin/env python3
"""Stage02G local RAM roles; no CPU execution."""
import csv
from baseline import ROOT,write_csv
def main():
    rows=list(csv.DictReader((ROOT/'maps/ram/ram_map.csv').open()));by={int(r['address'],16):r for r in rows}
    def field(a,n,name,description,routines,encoding='state-dependent binary bytes',caveat='Local verified role; no exhaustive global inventory claim.'):
        by[a]={'address':f'0x{a:04X}','size':n,'name':name,'description':description,'encoding':encoding,'accessing_routines':routines,'status':'STATIC_REVIEWED_LOCAL_ROLE','alias_caveat':caveat}
    field(0xF8,1,'GameFlowFlagsLocal','Special death5B delay sets20 in scene1B. Death60 sets80 unless reaction08; all other bits retained. Global producer/consumer meanings remain open.','0A:8A43;0A:8B1A')
    field(0x189,4,'SpecialDeathSharedAnchor','Two16-bit coordinates Y thenX, copied/clamped by80A1 relative camera Y30..B0,X30..D0; restored by8AA9 before scatter movement. Shared across slots, not a per-object anchor.','0A:80A1;0A:8AA9','little-endian Y thenX')
    field(0x42D,10,'EnemyPhaseOrDeathCycle','Special death5B/60 increments every eight animation calls;16 cycles end burst. First cycle0 permits drop generation. Other alive-kind uses are not fully mapped.','0A:8061;0A:8A12;0A:8AA9;0A:8B1A')
    field(0x45F,10,'EnemyEncodedScoreAward','Passed to C746 on first ordinary/special death entry. Low3 selects score digit, high nibble gives amount. Constructor copies source value to death object. Suppression47D10 skips ordinary score and drops.','0B:80D5;0A:8061;0A:8A12;0A:8B1A;0E:D8B5','packed digit index and amount')
    field(0x487,10,'EnemyDeathSoundFlags','Ordinary death80D5 suppresses sound51 when bit40 set; other bits and producers remain open.','0B:80D5')
    field(0x70A,2,'SpecialDeathClearedState','Kind60 terminal path clears both bytes after deactivation. Producer and full gameplay meaning unresolved.','0A:8B1A')
    by[0xD4]['name']='EnemyTargetPositionSnapshot'
    by[0xD4]['description']='Copy of playerC9..CC unless selected06BD=0B and0593 nonzero. E393 subtracts it from enemy coordinates to form AI distance masks. Hold condition uses0593, not decoy-slot3 counter0596; complete Twin Power target provenance remains open.'
    by[0xD4]['accessing_routines']='08:ABA8;0F:E393'
    def append(addr,text):
        if text not in by[addr]['description']:by[addr]['description']+=text
    append(0x2C,' Enemy dispatch8000 reloads this as current slot; death/score/drop callers restore X from it after helpers clobber X.')
    append(0x437,' Kind5B repurposes this field as originalkind-50 reward-table subtype, not HP; its dispatcher bypasses E2F9.')
    append(0x40F,' Kind00 has six normal collision states0..5; virtual AI selections6/7/8 mean death/hit/quake. Death handler stores6 but collision arrays do not gain three additional states.')
    append(0x419,' Kind00 normal frame counts8,1,9,9,9,9. Death5B/60 uses eight-frame cycles with separate042D repeat count.')
    append(0x423,' Ordinary8091 gate does not reset timer; special8051 gate resets on threshold. Both may unwind caller stack before threshold.')
    append(0x47D,' Ordinary bit10 suppresses score/drop;40 supports movement/fall state; special60 bit08 suppresses terminalF8bit80. Meanings depend on kind/lifecycle.')
    append(0x4EF,' New drop/reward probes useN20; allocator excludes0 and may use1. Forced reward path overwrites1 regardless of free-slot count.')
    write_csv(ROOT/'maps/ram/ram_map.csv',[by[k] for k in sorted(by)]);print(len(by),'RAM roles')
if __name__=='__main__':main()
