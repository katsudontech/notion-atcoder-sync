import tempfile
import unittest
from pathlib import Path
from sync_notion import export, filename, clean_id

ROOT = "3e29b429-9e61-816a-96ca-d16cbd4d2ca4"
CHILD = "3e29b429-9e61-81b9-8456-d61cd9521edc"

class Dummy:
    def markdown(self, pid):
        return "```python\nprint(1)\n```\n"
    def children(self, pid):
        if pid == ROOT:
            yield {"type": "child_page", "id": CHILD, "child_page": {"title": "9.2 DFS"}}
            yield {"type": "paragraph", "paragraph": {}}

class TestSync(unittest.TestCase):
    def test_filename_safe(self):
        name = filename('  ../a\\b:*?  ', ROOT)
        self.assertNotIn('/', name)
        self.assertNotIn('\\', name)

    def test_tree_export(self):
        with tempfile.TemporaryDirectory() as td:
            output = Path(td) / "notes"
            self.assertEqual(export(Dummy(), ROOT, output), 2)
            notes = list(output.rglob('*.md'))
            self.assertEqual(len(notes), 3)  # root, child, index
            contents = '\n'.join(p.read_text(encoding='utf-8') for p in notes)
            self.assertIn('print(1)', contents)
            self.assertIn('9.2 DFS', contents)
            self.assertEqual(export(Dummy(), ROOT, output), 2)

    def test_id_validation(self):
        with self.assertRaises(ValueError):
            clean_id('not-an-id')

if __name__ == '__main__':
    unittest.main()
