import unittest

from podium7.document_extraction import extract_ford_dark_horse_document


DOCUMENT = """SOURCE: Ford Brasil newsroom
MODEL: Mustang Dark Horse
ENGINE: Coyote V8 5.0
POWER: 500 cv
TORQUE: 57.8 kgfm
"""


class DocumentExtractionTests(unittest.TestCase):
    def test_schema_extracts_two_candidates(self):
        report = extract_ford_dark_horse_document(DOCUMENT, entity_id="entity-1", evidence_id="evidence-1")
        self.assertEqual(len(report.candidates), 2)

    def test_raw_values_are_preserved_and_normalized(self):
        report = extract_ford_dark_horse_document(DOCUMENT, entity_id="entity-1", evidence_id="evidence-1")
        facts = {fact.attribute: fact for fact in report.candidates}
        self.assertEqual(facts["power"].raw_value, "500 cv")
        self.assertEqual(facts["power"].normalized_value, 367.749375)
        self.assertEqual(facts["torque"].raw_value, "57.8 kgfm")
        self.assertEqual(facts["torque"].normalized_value, 566.82437)

    def test_document_hash_is_reproducible(self):
        first = extract_ford_dark_horse_document(DOCUMENT, entity_id="entity-1", evidence_id="evidence-1")
        second = extract_ford_dark_horse_document(DOCUMENT, entity_id="entity-1", evidence_id="evidence-1")
        self.assertEqual(first.sha256, second.sha256)
        self.assertEqual(first.candidates, second.candidates)

    def test_missing_required_field_is_rejected(self):
        broken = DOCUMENT.replace("TORQUE: 57.8 kgfm\n", "")
        with self.assertRaises(ValueError):
            extract_ford_dark_horse_document(broken, entity_id="entity-1", evidence_id="evidence-1")


if __name__ == "__main__":
    unittest.main()
