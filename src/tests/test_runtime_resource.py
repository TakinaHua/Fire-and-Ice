"""Runtime camera internals must stay outside CMU's recursive state inspection."""
import importlib.util
from pathlib import Path
import unittest
from input.runtime_resource import RuntimeResource


class ResourceTests(unittest.TestCase):
    def test_resource_methods_remain_available(self):
        class Camera:
            def isOpened(self): return True
        self.assertTrue(RuntimeResource(Camera()).isOpened())

    def test_native_dictionary_is_never_inspected(self):
        class NativeResource:
            def __getattribute__(self, name):
                if name == '__dict__':
                    raise RuntimeError('Native symbols must not be introspected')
                return object.__getattribute__(self, name)
        resource = RuntimeResource(NativeResource())
        self.assertFalse(hasattr(resource, '__dict__'))
        self.assertIn('RuntimeResource', repr(resource))

    def test_cmu_hash_stays_stable_while_resource_changes(self):
        # Load the pure checker directly; importing CMU itself would start GUI setup.
        path = Path(importlib.util.find_spec('cmu_graphics').origin).parent/'mvc_checker.py'
        spec = importlib.util.spec_from_file_location('mvc_checker_test',path)
        checker = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(checker)
        class Resource: pass
        native = Resource()
        native.timestamp = 1
        resource = RuntimeResource(native)
        before = checker.deepHash(resource,{})
        native.timestamp = 900
        native.module = unittest
        self.assertEqual(before,checker.deepHash(resource,{}))
