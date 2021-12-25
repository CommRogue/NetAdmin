import unittest
import sys, os
sys.path.insert(1, os.path.join(sys.path[0], '../source/client/main.py'))
import main

class TestClient(unittest.TestCase):
    def test_set_id(self):
        self.assertTrue(False)