import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bibparse import core


class BibparseTest(unittest.TestCase):
    def test_single_entry_kind(self):
        db = core.parse("@article{k, title = {Hello}}\n", core.Counter())
        self.assertEqual(db.entries[0].kind, "article")

    def test_entry_count(self):
        db = core.parse("@article{k, title = {Hello}}\n", core.Counter())
        self.assertEqual(len(db.entries), 1)

    def test_lookup_exact_lower_field(self):
        db = core.parse("@article{k, title = {Hello}}\n", core.Counter())
        self.assertEqual(core.lookup(db, "k", core.Counter()).fields["title"], "Hello")

    def test_lookup_missing_key(self):
        db = core.parse("@article{k, title = {Hello}}\n", core.Counter())
        self.assertIsNone(core.lookup(db, "nope", core.Counter()))

    def test_string_is_recorded(self):
        db = core.parse('@string{jn = "J"}\n', core.Counter())
        self.assertEqual(db.strings["jn"], "J")

    def test_counter_counts(self):
        counter = core.Counter()
        core.parse("@article{k, title = {Hello}}\n", counter)
        self.assertGreater(counter.scanned, 0)


if __name__ == "__main__":
    unittest.main()
