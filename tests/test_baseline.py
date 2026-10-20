import sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from baseline import parse

class HeaderTests(unittest.TestCase):
    def test_supplied_header_semantics(self):
        b=bytes.fromhex('4e45531a081040080000000000000001')+bytes(262144)
        h=parse(b)
        self.assertEqual((h['format'],h['mapper'],h['submapper']),('NES 2.0',4,0))
        self.assertEqual((h['prg_start'],h['chr_start'],h['expected_size']),(16,131088,262160))
        self.assertEqual((h['prg_ram'],h['chr_ram'],h['default_expansion_device']),(0,0,1))
    def test_rejects_truncation(self):
        with self.assertRaises(ValueError):parse(bytes.fromhex('4e45531a081040080000000000000001'))
    def test_trainer_moves_offsets(self):
        h=bytearray.fromhex('4e45531a010004080000000000000000')
        x=parse(bytes(h)+bytes(512+16384))
        self.assertEqual((x['trainer_size'],x['prg_start']),(512,528))
    def test_nes2_exponent_encoding(self):
        h=bytearray.fromhex('4e45531a38000808000f000000000000')
        self.assertEqual(parse(bytes(h)+bytes(16384))['prg_size'],16384)
    def test_invalid_magic(self):
        with self.assertRaises(ValueError):parse(bytes(16))

if __name__=='__main__':unittest.main()
