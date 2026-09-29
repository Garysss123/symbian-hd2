import importlib.util
from pathlib import Path
import unittest

path = Path(__file__).resolve().parents[1] / 'tools/retire-life-glyph-1035.py'
spec = importlib.util.spec_from_file_location('retirement', path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class RetirementTest(unittest.TestCase):
    def test_rejects_wrong_size(self):
        for data in (b'', bytes(module.SIZE - 1), bytes(module.SIZE + 1)):
            with self.assertRaises(ValueError):
                module.retire(data)

    def test_rejects_wrong_hash_even_with_matching_words(self):
        data = bytearray(module.SIZE)
        for group in module.GROUPS:
            for offset, word in zip(group, module.WORDS):
                module.struct.pack_into('<I', data, offset, word)
        with self.assertRaises(ValueError):
            module.retire(data)

    def test_twenty_unique_aligned_locations(self):
        offsets = [offset for group in module.GROUPS for offset in group]
        self.assertEqual(len(offsets), 20)
        self.assertEqual(len(set(offsets)), 20)
        self.assertTrue(all(offset % 4 == 0 and 0 <= offset <= module.SIZE - 4
                            for offset in offsets))

if __name__ == '__main__':
    unittest.main()
