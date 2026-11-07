import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import tempfile
import unittest
from unittest.mock import patch
from docguard import extract, check_text, check_links, report, annotations, release_notes, execute

def sample(code='print(4)',expected='4'):
    return f'```python check=demo\n{code}\n```\n```text expect=demo\n{expected}\n```\n'

class Tests(unittest.TestCase):
    def test_extract(self): self.assertEqual(extract(sample())[0]['id'],'demo')
    def test_line(self): self.assertEqual(extract('\n'+sample())[0]['line'],2)
    def test_ignore_normal_fence(self): self.assertEqual(extract('```python\nprint(4)\n```'),[])
    def test_missing_expect(self):
        with self.assertRaises(ValueError): extract('```python check=demo\nprint(4)\n```')
    def test_orphan_expect(self):
        with self.assertRaises(ValueError): extract('```text expect=demo\n4\n```')
    def test_unclosed(self):
        with self.assertRaises(ValueError): extract('```python check=demo\nprint(4)')
    def test_duplicate(self):
        with self.assertRaises(ValueError): extract(sample()+sample())
    def test_invalid_pair(self):
        with self.assertRaises(ValueError): extract('```text check=demo\n4\n```')
    def test_default_does_not_execute(self):
        with patch('docguard.execute',side_effect=AssertionError): self.assertEqual(check_text(sample())[0]['status'],'not_executed')
    def test_syntax(self): self.assertEqual(check_text(sample('print('))[0]['status'],'syntax_error')
    def test_parse_error(self): self.assertEqual(check_text('```python check=demo')[0]['status'],'parse_error')
    def test_pass(self): self.assertEqual(check_text(sample(),True)[0]['status'],'passed')
    def test_mismatch(self): self.assertEqual(check_text(sample(expected='5'),True)[0]['status'],'output_mismatch')
    def test_exception(self): self.assertEqual(check_text(sample('raise ValueError("fixture")'),True)[0]['status'],'execution_error')
    def test_timeout(self): self.assertEqual(execute('import time; time.sleep(1)',.03)[0],'timeout')
    def test_output_limit(self): self.assertEqual(execute('print("x"*9000)')[0],'output_limit')
    def test_hash(self): self.assertNotEqual(check_text(sample())[0]['source_sha256'],check_text(sample('print(5)'))[0]['source_sha256'])
    def test_release(self): self.assertIn('PR 3: Fix docs',release_notes([{'number':3,'title':'Fix\ndocs'}]))
    def test_release_validation(self):
        with self.assertRaises(ValueError):release_notes([{'title':'x'}])
    def test_annotation_escape(self):
        a=annotations({'results':[{'file':'bad,\nname.md','line':2,'id':'x','status':'syntax_error'}]})
        self.assertIn('bad%2C%0Aname.md',a)
    def test_links_and_root_boundary(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); path=root/'a.md'
            path.write_text('# Hello\n[ok](#hello)\n[missing](b.md)\n[bad](#absent)\n[escape](../private.md)\n[external](https://example.com)')
            self.assertEqual([x['status'] for x in check_links(path,root)],['missing_link','missing_anchor','outside_root'])
    def test_report_and_exit_evidence(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); (root/'a.md').write_text(sample(expected='5'))
            data=report(root.rglob('*.md'),root,True)
            self.assertEqual(data['failures'],1)
            self.assertEqual(data['results'][0]['file'],'a.md')

if __name__=='__main__': unittest.main()
