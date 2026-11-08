"""Test the production reader in isolation; no HA/TV access."""
from pathlib import Path
import sys
import types
import unittest
root=Path(__file__).resolve().parents[1]
reader=types.ModuleType("reader_under_test")
sys.modules[reader.__name__]=reader
path=root/"custom_components/tv_volume_bridge/reader.py"
exec(compile(path.read_text(),str(path),"exec"),reader.__dict__)
tests=types.ModuleType("reader_tests")
path=root/"tests/test_reader.py"
exec(compile(path.read_text(),str(path),"exec"),tests.__dict__)
result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(tests))
raise SystemExit(not result.wasSuccessful())
