#!/usr/bin/env python3
"""Idempotent Stage02E bounded RAM-role updates; no CPU tests."""
import csv
from baseline import ROOT,write_csv

def main():
    with (ROOT/'maps/ram/ram_map.csv').open() as f:rows=list(csv.DictReader(f))
    by={int(r['address'],16):r for r in rows}
    def field(address,size,name,description,encoding,routines,caveat='Local role; other caller-dependent uses not excluded.'):
        by[address]={'address':f'0x{address:04X}','size':size,'name':name,'description':description,'encoding':encoding,'accessing_routines':routines,'status':'STATIC_REVIEWED_LOCAL_ROLE','alias_caveat':caveat}
    field(0xD1,1,'PlayerJumpPhase','Normal jump: E7 launch; bit40 ascent; negative phase holds up3 while A held or A-history low2 nonzero. Release seeds40; indexed taper ends0C. Descent uses predecrement low6 index. Landing clears. Forward airborne attack seeds80; not a signed velocity.','phase and flag byte; normal indexed domain0..12','08:BC17;08:BC34;08:BCEF;08:B947','Other attack/alternate-family uses require their own domain; do not index B80A with arbitrary low6 values.')
    field(0x5B8,256,'TerrainCollisionCache','Cache indexed by (linearY mod240 & F0)|(Xlow>>4); valid remainder gives15 rows of16 cells at16-pixel pitch. All256 allocated addresses follow sampler expression; finalrowF0..FF is not reached by valid normalizedY. Actual producers and scrolling refill remain open.','byte attributes; sixteen-column cache,240 valid cells','0E:DAE6;0E:DB02;0E:DBB7','Cache contains current mutable terrain; world page selection belongs to classifier/refill. Do not infer one permanently stored full scene.')
    field(0xB9,2,'ScenePageOrderPointer','Loaded from07:B282. F50D indexes byte page IDs using world Xpage for horizontal lookup or normalized Ypage for vertical lookup. Valid page-count contract not established for all32 scenes.','little-endian pointer to byte page IDs','07:A537;0F:F50D;0E:DA3D')
    field(0xBB,2,'SceneMetatilePagesPointer','Loaded from07:B2C2. F50D adds64*pageID; DA3D reads metatile ID at row*8+column in a32-pixel grid. Full page dimensions/refill and all scene bounds remain open.','little-endian pointer to64-byte pages','07:A537;0F:F50D;0E:DA3D')
    field(0xC1,2,'SceneTerrainAttributesPointer','Loaded from07:B382. DA3D reads four terrain attributes per metatile, selected by16-pixel quadrant. Scene00 samples verified from actual PRG02, not screenshots.','little-endian pointer;4 bytes per metatile','07:A537;0E:DA3D')
    by[0xCF]['description']='Player handler-call counter, reset by AD39. Normal walk advances every8 calls (SBC carry inherited from oldCDbit7); attack periods vary3/4/6 or explicit sequence. Not a universal animation frame timer.'
    by[0xCF]['accessing_routines']='08:AD39;08:AD44;08:B8B5;08:B9D4;08:BA4C;08:BA98'
    by[0xCE]['description']='AB19 retains bit01 selecting alternate family; bit80 terminal; terrain0C. Motion helpers use40 movement marker,20 left,10 up; slow-terrain04 suppresses horizontal translation on oddD8 while still setting40. Not a signed direction or guaranteed displacement indicator.'
    by[0xCE]['accessing_routines']='08:AB19;08:ADCF;08:AE14;08:AEB1;08:AF5A;08:AFBC;0E:DB02'
    write_csv(ROOT/'maps/ram/ram_map.csv',[by[a] for a in sorted(by)]);print(len(by),'RAM entries')
if __name__=='__main__':main()
