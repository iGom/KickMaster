#!/usr/bin/env python3
"""Apply manually reviewed Stage02D local RAM roles; idempotent, no CPU execution."""
import csv
from baseline import ROOT,write_csv

def main():
    with (ROOT/'maps/ram/ram_map.csv').open() as f: rows=list(csv.DictReader(f))
    by={int(r['address'],16):r for r in rows}
    def field(address,size,name,description,encoding,routines,caveat='Local role only; other state-dependent uses not excluded.'):
        by[address]={'address':f'0x{address:04X}','size':size,'name':name,'description':description,
          'encoding':encoding,'accessing_routines':routines,'status':'STATIC_REVIEWED_LOCAL_ROLE','alias_caveat':caveat}
    field(0x3DC,1,'QuakeLifetimeCounter','D7E7 starts at 1. D7AD increments to F0; entry D2 adds secondary bit40 to flagged enemies; entry F0 clears counter and bits10/40 in first eight entries. D6F0 calls it only when D8 is odd.','binary counter; 240 handler calls from seed1','0E:D7E7;0E:D7AD;0E:D6F0')
    field(0x3DD,10,'EnemyKind','A354 indexes R6=06 pointer table by enemy kind. Valid kind inventory remains open.','byte array; indexed locally','08:A354')
    for address,name,axis,part in [(0x3E7,'EnemyWorldYLow','Y','low'),(0x3F1,'EnemyWorldYHigh','Y','high'),(0x3FB,'EnemyWorldXLow','X','low'),(0x405,'EnemyWorldXHigh','X','high')]:
        field(address,10,name,f'Enemy world {axis} {part} byte; original knockback computes and commits 16-bit coordinates.','parallel arrays with stride10 decimal','08:A354;0F:E478;0F:E72D')
    field(0x40F,10,'EnemyStateIndex','Normal-state selector used by E2F9 and collision animation indirection in A354. Enemy-specific dispatch remains open.','byte array','0F:E2F9;08:A354')
    field(0x419,10,'EnemyAnimationIndex','A354 indexes the current enemy animation frame within its state definition.','byte array; local lookup role','08:A354')
    field(0x423,10,'EnemyStateCounter','Normal E2F9 path increments it. Hit recovery increments it, acts on odd result and resets it after that work; therefore a zero seed allows work on each recovery call.','byte array; state-dependent counter','0F:E2F9;0F:E35B')
    field(0x437,10,'EnemyHpRaw','E32A subtracts queued damage with unsigned saturation to zero when primary bit40 permits consumption. No HP-unit or complete enemy-population interpretation established.','raw unsigned 8-bit indexed field','0F:E2F9;0F:E32A','Address0440 aliases indexed slot9 and the D6F0 pass accumulator. Ten local test indices do not establish ten independent live enemies.')
    field(0x440,1,'EnemyPassAccumulator','D6F0 clears this byte before the enemy pass, then copies it to06BC. Producer inside unreviewed D759 remains open.','byte; not yet a complete boss-HP interpretation','0E:D6F0','Aliases0437+9. Do not treat as an independently allocated eleventh field.')
    field(0x441,10,'EnemyQueuedDamage','BD1B and A230 queue raw damage. E32A consumes it if bit40 is set; the outer E2F9 path supplies pending-bit20 gating. Consumption leaves the queued byte unchanged.','raw unsigned request array','09:BD1B;08:A230;0F:E32A')
    field(0x455,10,'EnemyHitRecoveryCounter','E32A resets to0. E35B increments on its active phase; equality0A re-arms acceptance, clears pending/reaction flags and resets this counter.','raw byte counter','0F:E32A;0F:E35B')
    field(0x469,10,'EnemyPrimaryFlags','Queue paths require value>=C0. Bit20 is pending hit; E32A clears acceptance bit40 to prevent repeat subtraction; E35B restores40 and clears20 at recovery.','byte flags array','09:BD1B;08:A230;0F:E2F9;0F:E32A;0F:E35B')
    field(0x473,10,'EnemySecondaryFlags','Queue paths require low two bits zero. Quake producer and lifetime handler operate only on first eight entries; bit10 selects the alternate E2F9 path, bit40 is added at D2. Negative value can request knockback terrain adjustment.','byte flags array','09:BD1B;0E:D7E7;0E:D7AD;0F:E2F9;0F:E3FE')
    field(0x47D,10,'EnemyReactionFlags','Low three bits select knockback direction. Projectile queue uses7/1/0 for negative/positive/zero vx. E32A sets bit80; recovery clears it.','byte flags array','09:BD1B;08:A230;0F:E32A;0F:E35B;0F:E3FE')
    field(0x491,10,'EnemyProjectileFlagsAndKind','A305 requires bit80 set and bit40 clear; overlap consumes the projectile before shield/player-damage processing. A404 indexes geometry with low six bits.','flags plus six-bit kind','08:A305;08:A404')
    field(0x49B,10,'EnemyProjectileState','A404 uses low three bits to select a damage/shape pair. Valid kind/state combinations remain unenumerated.','byte; low-three-bit selector','08:A404')
    field(0x4B9,10,'EnemyProjectileYLow','Low Y byte read by A404 collision bounds. This reader does not establish a high-Y field.','8-bit collision coordinate','08:A404')
    field(0x4CD,10,'EnemyProjectileXLow','Low world X byte used for camera-relative collision bounds.','16-bit split coordinate low byte','08:A404')
    field(0x4D7,10,'EnemyProjectileXHigh','High world X byte used for camera-relative collision bounds.','16-bit split coordinate high byte','08:A404')
    by[0x57C]['description']+=' In A230, bit10 preserves a colliding projectile for further enemy hits; a clear bit consumes it.'
    # Avoid repeated suffixes on intentional regeneration.
    suffix=' In A230, bit10 preserves a colliding projectile for further enemy hits; a clear bit consumes it.'
    by[0x57C]['description']=by[0x57C]['description'].split(suffix)[0]+suffix
    by[0x57C]['accessing_routines']='09:BE90;09:BF3E;09:BF68;07:AE3A;08:A14F;08:A230;09:B571'
    by[0x5A4]['description']='Parallel second counter array; selected slot3 at05A7: aim target, timer high part, shield budget or lightning timer. A305 decrements shield seed0A on qualifying enemy-projectile overlaps: ten absorbed, next negative damages player. Side-lightning objects use signed type-step +2/-2.'
    by[0x5A4]['accessing_routines']='09:B747;09:B8B7;09:B964;09:B9E1;08:A305;09:B5EF;09:B620'
    field(0x6BC,1,'EnemyPassAccumulatorCopy','D6F0 copies0440 here after its enemy pass. Display/producer semantics are still incomplete.','raw byte','0E:D6F0')
    field(0x6F8,1,'EnemyCollisionScanCount','A230 scans indices count-1 down to0. Zero/count overflow and complete runtime producer contract are not established by these probes.','unsigned count; tests1/2','08:A230')
    field(0x6F9,1,'EnemyUpdateOrderSelector','D6F0 stores D8&1; controls one of two ten-entry successor cycles.','0 or1 in reviewed scheduler','0E:D6F0')
    write_csv(ROOT/'maps/ram/ram_map.csv',[by[a] for a in sorted(by)])
    print(len(by),'RAM roles')
if __name__=='__main__':main()
