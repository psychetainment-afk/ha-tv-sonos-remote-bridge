"""Run isolated reader tests with adb-shell installed; no HA/TV access."""
from pathlib import Path
import sys
import types
import unittest

root = Path(__file__).resolve().parents[1]
module = types.ModuleType("reader_under_test")
sys.modules[module.__name__] = module
source = root / "custom_components/tv_volume_bridge/reader.py"
exec(compile(source.read_text(), str(source), "exec"), module.__dict__)
tests = types.ModuleType("reader_tests")
test_file = Path(__file__).with_name("test_reader.py")
exec(compile(test_file.read_text(), str(test_file), "exec"), tests.__dict__)
suite = unittest.defaultTestLoader.loadTestsFromModule(tests)
cover_tests = types.ModuleType("cover_tests")
cover_tests.COLOR_YAML = (root / "examples/buttons.yaml").read_text()
cover_file = Path(__file__).with_name("test_cover_actions.py")
exec(compile(cover_file.read_text(), str(cover_file), "exec"), cover_tests.__dict__)
suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(cover_tests))
result = unittest.TextTestRunner(verbosity=2).run(suite)
raise SystemExit(not result.wasSuccessful())
