import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from sync_notion import NotionClient, export

ROOT = '00000000-0000-0000-0000-000000000001'
DB = '00000000-0000-0000-0000-000000000002'
DS = '00000000-0000-0000-0000-000000000003'
ROW = '00000000-0000-0000-0000-000000000004'

def row(pid=ROW):
    return {'object': 'page', 'id': pid, 'properties': {'問題名': {'type': 'title', 'title': [{'plain_text': '001 - Yokan Party'}]}}}

class DatabaseTests(unittest.TestCase):
    def test_post_pagination_multiple_sources(self):
        responses = [
            {'data_sources': [{'id': DS}, {'id': DB}]},
            {'results': [row()] * 100, 'has_more': True, 'next_cursor': 'next'},
            {'results': [row()], 'has_more': False},
            {'results': [dict(row(), archived=True)], 'has_more': False},
        ]
        with patch('sync_notion.urlopen', side_effect=[io.BytesIO(json.dumps(r).encode()) for r in responses]) as call:
            self.assertEqual(len(list(NotionClient('test').database_pages(DB))), 101)
            req = call.call_args_list[2].args[0]
            self.assertEqual(req.get_method(), 'POST')
            self.assertEqual(json.loads(req.data), {'page_size': 100, 'start_cursor': 'next'})
            self.assertEqual(call.call_args_list[3].args[0].full_url, f'https://api.notion.com/v1/data_sources/{DB}/query')

    def test_bad_pagination_fails(self):
        client = NotionClient('test')
        with patch.object(client, 'get', return_value={'data_sources': [{'id': DS}]}), patch.object(client, 'request', return_value={'results': [], 'has_more': True}):
            with self.assertRaisesRegex(RuntimeError, 'pagination'):
                list(client.database_pages(DB))

    def test_export_and_failure_preserves_snapshot(self):
        class Client:
            def markdown(self, pid):
                return '本文\n```python\nprint(90)\n```'
            def children(self, pid):
                if pid == ROOT:
                    yield {'id': DB, 'type': 'child_database', 'child_database': {'title': '典型90'}}
                if pid == ROW:
                    yield {'id': DS, 'type': 'child_page', 'child_page': {'title': '解説'}}
            def database_pages(self, pid):
                yield row()
        with tempfile.TemporaryDirectory() as td:
            output = Path(td) / 'notes'
            client = Client()
            self.assertEqual(export(client, ROOT, output), 3)
            snapshot = {p.relative_to(output): p.read_bytes() for p in output.rglob('*.md')}
            self.assertTrue(any('典型90' in str(p) and 'Yokan' in str(p) for p in snapshot))
            self.assertTrue(any('解説' in str(p) for p in snapshot))
            with patch.object(client, 'database_pages', side_effect=RuntimeError('403')):
                with self.assertRaisesRegex(RuntimeError, '403'):
                    export(client, ROOT, output)
            self.assertEqual(snapshot, {p.relative_to(output): p.read_bytes() for p in output.rglob('*.md')})
            self.assertFalse(output.with_name('notes-staging').exists())

    def test_duplicate_routes_and_cycle_export_once(self):
        class Client:
            def __init__(self):
                self.fetched = []
            def markdown(self, pid):
                self.fetched.append(pid)
                return 'body'
            def children(self, pid):
                if pid == ROOT:
                    yield {'id': ROW, 'type': 'child_page', 'child_page': {'title': '問題'}}
                    yield {'id': DB, 'type': 'child_database', 'child_database': {'title': '典型90'}}
                if pid == ROW:
                    yield {'id': ROOT, 'type': 'child_page', 'child_page': {'title': '親への参照'}}
            def database_pages(self, pid):
                for _ in range(501):
                    yield row()
        with tempfile.TemporaryDirectory() as td:
            output = Path(td) / 'notes'
            client = Client()
            self.assertEqual(export(client, ROOT, output), 2)
            self.assertEqual(client.fetched, [ROOT, ROW])
            self.assertEqual(len(list(output.rglob('*.md'))), 3)
            index = (output / 'README.md').read_text()
            self.assertIn('001 - Yokan Party', index)
            import re
            for target in re.findall(r'\(<(.*?)>\)', index):
                self.assertTrue((output / target).is_file(), target)
