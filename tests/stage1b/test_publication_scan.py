"""Synthetic path strings only; not real internal locations."""
import json,pathlib,sys,unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[2]/'tools/stage1b'))
from publication_scan import inspect_text
class Publication(unittest.TestCase):
 def test_safe(self):self.assertTrue(inspect_text(json.dumps({'files':['docs/results.md'],'sha256':'a'*64}))['accepted'])
 def test_git_hint(self):self.assertTrue(inspect_text(json.dumps({'stderr':'hint: choose a name\nrefs: listed'}))['accepted'])
 def test_placeholder(self):self.assertTrue(inspect_text(json.dumps({'path':'<case-workspace>/private/test'}))['accepted'])
 def test_nested(self):self.assertFalse(inspect_text(json.dumps({'nested':[{'source':'C:/Users/example/test.txt'}]}))['accepted'])
 def test_key(self):self.assertFalse(inspect_text(json.dumps({'/home/example/test':'value'}))['accepted'])
 def test_double_json(self):self.assertFalse(inspect_text(json.dumps({'nested':json.dumps({'raw':r'C:\Users\example\file'})}))['accepted'])
 def test_unicode(self):self.assertFalse(inspect_text(r'"\u0043\u003a\u005cUsers\u005cexample"')['accepted'])
 def test_slash(self):self.assertFalse(inspect_text(r'{"source":"\/home\/example\/x"}')['accepted'])
 def test_unc(self):self.assertFalse(inspect_text(r'\\synthetic-server\synthetic-share\sample')['accepted'])
 def test_hex(self):self.assertFalse(inspect_text(r'\x43\x3a\x5cUsers\x5cexample')['accepted'])
if __name__=='__main__':unittest.main()
