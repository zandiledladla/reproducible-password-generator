"""Run from the project folder: python -m unittest discover -s tests -v."""
import unittest
from password_core import derive_password, CATEGORIES, CHARSET, validate_inputs


class CoreTests(unittest.TestCase):
    def test_reproducibility(self):
        self.assertEqual(derive_password('StudyDemo2026', 24), derive_password('StudyDemo2026', 24))

    def test_lengths_and_categories(self):
        for length in (8, 9, 16, 24, 64, 128):
            for source in ('StudyDemo2026', 'x', 'Demo 🔐 é'):
                with self.subTest(length=length, source=source):
                    result = derive_password(source, length)
                    self.assertEqual(len(result), length)
                    self.assertTrue(set(result) <= set(CHARSET))
                    for category in CATEGORIES:
                        self.assertTrue(any(c in category for c in result))

    def test_invalid_lengths(self):
        for length in (-1, 0, 7, 129, 24.0, True, '24', None):
            with self.subTest(length=length), self.assertRaises(ValueError):
                derive_password('demo', length)

    def test_invalid_memorable(self):
        for source in ('', '   ', '\t\n', 'é' * 513):
            with self.subTest(source=repr(source[:10])), self.assertRaises(ValueError):
                derive_password(source, 24)

    def test_input_boundary(self):
        validate_inputs('é' * 512, 24)

    def test_inputs_are_not_normalised(self):
        original = derive_password('Demo', 24)
        for other in ('demo', 'Demo ', ' Demo'):
            self.assertNotEqual(original, derive_password(other, 24))
        self.assertNotEqual(derive_password('é', 24), derive_password('e\u0301', 24))

    def test_length_is_part_of_derivation(self):
        self.assertNotEqual(derive_password('Demo', 24)[:16], derive_password('Demo', 16))


if __name__ == '__main__':
    unittest.main()
