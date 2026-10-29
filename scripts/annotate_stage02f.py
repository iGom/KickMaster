#!/usr/bin/env python3
"""Idempotent Stage02F RAM-role refinements; preserves all earlier rows."""
import csv
from baseline import ROOT,write_csv
def main():
    rows=list(csv.DictReader((ROOT/'maps/ram/ram_map.csv').open()));by={int(r['address'],16):r for r in rows}
    changes={
      0x3DD:('Kind indexes99-entry collision-pointer table00..62; AI tables have64 ordinary00..3F and29 special46..62 entries. Scheduler threshold46 does not validate gap40..45. Native kind reachability remains open.','08:A354;08:A0B0;0A:8000;0B:8000;0E:D759'),
      0x40F:('Enemy-specific state selects little-endian frame-array pointer via06:855C kind table. State/frame counts remain open; state0/frame0 data exported for99 kinds.','0F:E2F9;08:A354;08:A0B0'),
      0x419:('Index into four-byte collision frame: primary damage,body shape,secondary damage,attack shape. Animation/collision synchronization and full frame domains remain open.','08:A354;08:A0B0'),
      0x440:('Cleared before D6F0 pass. D78B adds0437,X for kind>=50 excluding5B/60, saturating atAF including carry. Copied to06BC. Slot9 aliases this accumulator and doubles it locally. Display semantics remain open.','0E:D6F0;0E:D78B'),
      0x441:('A197 queues melee damage from06:8328[CD>>1] for first overlap; no local level multiplier. BD1B/A230 queue projectile damage. E32A consumes if469bit40; E2F9 supplies pending-bit20 gate. Queued byte retained.','08:A197;09:BD1B;08:A230;0F:E32A'),
      0x47D:('Low3 bits hold hit direction. A197/A5EC selects using signed low-byte player-minus-enemy delta ratios, preserving high5. Projectile queue uses7/1/0 for negative/positive/zero vx. E32A sets80; recovery clears it.','08:A197;08:A5EC;09:BD1B;08:A230;0F:E32A;0F:E35B;0F:E3FE'),
      0x6BC:('D6F0 copies0440 after enemy pass. D78B producer now known as selected-kind saturating raw-HP aggregate. UI use not yet traced; do not equate unconditionally with boss HP.','0E:D6F0;0E:D78B'),
      0x6F8:('Descending count-1 collision scans. A075/A197 guard count0; A2C3 does not. Body-contact probes cover1..10; global producer and independent slot count remain open.','08:A075;08:A197;08:A230;08:A2C3'),
      0x6F9:('D6F0 storesD8&1 and chooses successor cycle. D759 compares slot parity: matching phase skips AI but still aggregates/render-tails; opposite phase runs selected AI.','0E:D6F0;0E:D759')}
    for addr,(description,routines) in changes.items():by[addr]['description']=description;by[addr]['accessing_routines']=routines
    by[0x6F8]['encoding']='unsigned count; path-specific zero guard'
    write_csv(ROOT/'maps/ram/ram_map.csv',[by[k] for k in sorted(by)]);print(len(by),'RAM entries;9 roles refined')
if __name__=='__main__':main()
