"""Test suite to validate sample transaction data against classification engine.

This test suite loads the sample transaction data and verifies that the
classification engine produces the expected results for all test cases.
"""

import unittest
import json
import csv
from pathlib import Path

from statement_classifier import ClassificationEngine, FileRuleProvider


class TestSampleDataValidation(unittest.TestCase):
    """Validate sample transaction data produces expected classifications."""

    @classmethod
    def setUpClass(cls):
        """Set up classification engine once for all tests."""
        rules_path = Path(__file__).parent.parent / 'bin' / 'classification_rules.v4.json'
        provider = FileRuleProvider(v4_path=rules_path)
        cls.engine = ClassificationEngine(provider)

        # Load test fixtures
        fixtures_dir = Path(__file__).parent / 'fixtures'

        # Load JSON test data
        json_path = fixtures_dir / 'sample_transactions.json'
        with open(json_path, 'r') as f:
            cls.json_data = json.load(f)

        # Load CSV test data
        csv_path = fixtures_dir / 'sample_transactions.csv'
        cls.csv_data = []
        with open(csv_path, 'r') as f:
            reader = csv.DictReader(f)
            cls.csv_data = list(reader)

    def _validate_classification(self, description, category, expected, notes=""):
        """Helper to validate a single classification."""
        result = self.engine.classify(description, category)

        with self.subTest(description=description, notes=notes):
            self.assertEqual(
                result['purchase_type'],
                expected['purchase_type'],
                f"Purchase type mismatch for '{description}'"
            )
            self.assertEqual(
                result['category'],
                expected['category'],
                f"Category mismatch for '{description}'"
            )
            self.assertEqual(
                result['subcategory'],
                expected['subcategory'],
                f"Subcategory mismatch for '{description}'"
            )
            self.assertEqual(
                result['online'],
                expected['online'],
                f"Online flag mismatch for '{description}'"
            )

    def test_business_income_transactions(self):
        """Test business income transactions."""
        test_suite = self.json_data['test_suites']['business_income']
        for test_case in test_suite:
            self._validate_classification(
                test_case['description'],
                test_case['category'],
                test_case['expected']
            )

    def test_business_expense_transactions(self):
        """Test business expense transactions."""
        test_suite = self.json_data['test_suites']['business_expenses']
        for test_case in test_suite:
            self._validate_classification(
                test_case['description'],
                test_case['category'],
                test_case['expected']
            )

    def test_business_tax_transactions(self):
        """Test business tax transactions."""
        test_suite = self.json_data['test_suites']['business_taxes']
        for test_case in test_suite:
            self._validate_classification(
                test_case['description'],
                test_case['category'],
                test_case['expected']
            )

    def test_business_fee_transactions(self):
        """Test business fee transactions."""
        test_suite = self.json_data['test_suites']['business_fees']
        for test_case in test_suite:
            self._validate_classification(
                test_case['description'],
                test_case['category'],
                test_case['expected']
            )

    def test_personal_food_transactions(self):
        """Test personal food and dining transactions."""
        test_suite = self.json_data['test_suites']['personal_food']
        for test_case in test_suite:
            self._validate_classification(
                test_case['description'],
                test_case['category'],
                test_case['expected']
            )

    def test_personal_healthcare_transactions(self):
        """Test personal healthcare transactions."""
        test_suite = self.json_data['test_suites']['personal_healthcare']
        for test_case in test_suite:
            self._validate_classification(
                test_case['description'],
                test_case['category'],
                test_case['expected']
            )

    def test_personal_recreation_transactions(self):
        """Test personal recreation transactions."""
        test_suite = self.json_data['test_suites']['personal_recreation']
        for test_case in test_suite:
            self._validate_classification(
                test_case['description'],
                test_case['category'],
                test_case['expected']
            )

    def test_personal_shopping_transactions(self):
        """Test personal shopping transactions."""
        test_suite = self.json_data['test_suites']['personal_shopping']
        for test_case in test_suite:
            self._validate_classification(
                test_case['description'],
                test_case['category'],
                test_case['expected']
            )

    def test_personal_services_transactions(self):
        """Test personal services transactions."""
        test_suite = self.json_data['test_suites']['personal_services']
        for test_case in test_suite:
            self._validate_classification(
                test_case['description'],
                test_case['category'],
                test_case['expected']
            )

    def test_personal_financial_transactions(self):
        """Test personal financial transactions."""
        test_suite = self.json_data['test_suites']['personal_financial']
        for test_case in test_suite:
            self._validate_classification(
                test_case['description'],
                test_case['category'],
                test_case['expected']
            )

    def test_personal_income_transactions(self):
        """Test personal income transactions."""
        test_suite = self.json_data['test_suites']['personal_income']
        for test_case in test_suite:
            self._validate_classification(
                test_case['description'],
                test_case['category'],
                test_case['expected']
            )

    def test_edge_cases(self):
        """Test edge cases and boundary conditions."""
        test_suite = self.json_data['test_suites']['edge_cases']
        for test_case in test_suite:
            self._validate_classification(
                test_case['description'],
                test_case['category'],
                test_case['expected'],
                notes=test_case.get('notes', '')
            )

    def test_priority_handling(self):
        """Test priority-based rule matching."""
        test_suite = self.json_data['test_suites']['priority_testing']
        for test_case in test_suite:
            self._validate_classification(
                test_case['description'],
                test_case['category'],
                test_case['expected'],
                notes=test_case.get('notes', '')
            )

    def test_online_flag_accuracy(self):
        """Test online flag is set correctly."""
        test_suite = self.json_data['test_suites']['online_flag_testing']
        for test_case in test_suite:
            self._validate_classification(
                test_case['description'],
                test_case['category'],
                test_case['expected'],
                notes=test_case.get('notes', '')
            )

    def test_csv_data_matches_json(self):
        """Verify CSV test data matches JSON test data."""
        # Count total test cases
        json_count = sum(
            len(suite)
            for suite in self.json_data['test_suites'].values()
        )
        csv_count = len(self.csv_data)

        # Should have same number of test cases
        self.assertEqual(
            json_count,
            csv_count,
            "CSV and JSON should have same number of test cases"
        )

    def test_all_csv_transactions(self):
        """Test all transactions from CSV file."""
        for row in self.csv_data:
            expected = {
                'purchase_type': row['expected_purchase_type'],
                'category': row['expected_category'],
                'subcategory': row['expected_subcategory'],
                'online': row['expected_online'].lower() == 'true'
            }

            self._validate_classification(
                row['description'],
                row['category'],
                expected,
                notes=row.get('notes', '')
            )

    def test_input_normalization(self):
        """Test that inputs are properly normalized."""
        # Test lowercase normalization
        result1 = self.engine.classify('amazon.com*12345', 'purchase')
        result2 = self.engine.classify('AMAZON.COM*12345', 'PURCHASE')

        self.assertEqual(result1, result2, "Lowercase should be normalized")

        # Test whitespace trimming
        result3 = self.engine.classify('  AMAZON.COM*12345  ', '  PURCHASE  ')

        self.assertEqual(result2, result3, "Whitespace should be trimmed")

    def test_empty_inputs(self):
        """Test handling of empty inputs."""
        # Empty description
        result = self.engine.classify('', 'PURCHASE')
        self.assertIsNotNone(result)

        # Empty category
        result = self.engine.classify('AMAZON.COM', '')
        self.assertIsNotNone(result)

        # Both empty
        result = self.engine.classify('', '')
        self.assertIsNotNone(result)
        self.assertEqual(result['purchase_type'], 'Personal')

    def test_fallback_categories(self):
        """Test fallback category matching."""
        # Test with a category that should match fallback
        result = self.engine.classify(
            'UNKNOWN MERCHANT',
            'GROCERY'
        )

        # Should use fallback category
        self.assertEqual(result['category'], 'Grocery')

    def test_keyword_priority(self):
        """Test that higher priority keywords win."""
        # AMAZON (priority 998) should beat lower priority rules
        result = self.engine.classify(
            'AMAZON.COM* WALMART.COM',
            'PURCHASE'
        )

        self.assertEqual(result['category'], 'General Merchandise')
        self.assertTrue(result['online'])

    def test_classification_consistency(self):
        """Test that same input produces same output."""
        description = 'AMAZON.COM*12345'
        category = 'PURCHASE'

        # Run classification 10 times
        results = [
            self.engine.classify(description, category)
            for _ in range(10)
        ]

        # All results should be identical
        first_result = results[0]
        for result in results[1:]:
            self.assertEqual(result, first_result)

    def test_special_characters(self):
        """Test handling of special characters in descriptions."""
        test_cases = [
            'ORIG CO NAME:AMAZON.COM, INC.',
            'SQ *ENVISION EYE CARE',
            'E-Z*PASSNY',
            'PHR*ENTANDALLERGYASSOCIAT',
            'TST* THE BRICKERY'
        ]

        for desc in test_cases:
            with self.subTest(description=desc):
                result = self.engine.classify(desc, 'PURCHASE')
                self.assertIsNotNone(result)
                self.assertIn('purchase_type', result)

    def test_coverage_report(self):
        """Generate coverage report for test data."""
        # Count classifications by type
        business_count = 0
        personal_count = 0
        online_count = 0
        offline_count = 0

        for row in self.csv_data:
            if row['expected_purchase_type'] == 'Business':
                business_count += 1
            else:
                personal_count += 1

            if row['expected_online'].lower() == 'true':
                online_count += 1
            else:
                offline_count += 1

        total = len(self.csv_data)

        # Print coverage report
        print(f"\n{'='*60}")
        print("Test Data Coverage Report")
        print(f"{'='*60}")
        print(f"Total test cases: {total}")
        print(f"Business transactions: {business_count} ({business_count/total*100:.1f}%)")
        print(f"Personal transactions: {personal_count} ({personal_count/total*100:.1f}%)")
        print(f"Online transactions: {online_count} ({online_count/total*100:.1f}%)")
        print(f"Offline transactions: {offline_count} ({offline_count/total*100:.1f}%)")
        print(f"{'='*60}\n")

        # Ensure good coverage
        self.assertGreater(business_count, 0, "Should have business transactions")
        self.assertGreater(personal_count, 0, "Should have personal transactions")
        self.assertGreater(online_count, 0, "Should have online transactions")
        self.assertGreater(offline_count, 0, "Should have offline transactions")


if __name__ == '__main__':
    unittest.main(verbosity=2)
