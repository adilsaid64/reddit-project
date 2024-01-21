import unittest
import sys

sys.path.append('...')
from src.text_processor import *

class TestExpandContractions(unittest.TestCase):
    def test_basic_contraction(self):
        self.assertEqual(expand_contractions("I can't do this"), "I cannot do this")

    def test_no_contraction(self):
        self.assertEqual(expand_contractions("Hello world"), "Hello world")

    def test_multiple_contractions(self):
        self.assertEqual(expand_contractions("You're going to be late if you don't hurry"),
                         "You are going to be late if you do not hurry")
    def test_edge_case(self):
        self.assertEqual(expand_contractions(""), "")

if __name__ == '__main__':
    unittest.main()