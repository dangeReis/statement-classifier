"""Integration tests for Phase 2 - ClassificationEngine and FileRuleProvider."""

import unittest
import tempfile
import json
from pathlib import Path

from statement_classifier.engine import ClassificationEngine
from statement_classifier.providers import RuleProvider
from statement_classifier.providers.file import FileRuleProvider
from statement_classifier.types import (
    ClassificationResult,
    ValidationResult,
    RuleProviderException,
)


class MockRuleProvider(RuleProvider):
    """Mock provider for testing."""

    def __init__(self, rules=None):
        """Initialize mock provider with test rules."""
        self.rules_data = rules or {
            'version': '4.0',
            'rules': [
                {
                    'id': 'amazon',
                    'keywords': ['AMAZON', 'AMZN'],
                    'purchase_type': 'Personal',
                    'category': 'Online Shopping',
                    'subcategory': 'General Retail',
                    'online': True,
                    'priority': 100
                },
                {
                    'id': 'business-bank',
                    'keywords': ['BUSINESS BANK', 'BUSINESS ACH'],
                    'purchase_type': 'Business',
                    'category': 'Banking',
                    'subcategory': 'Bank Fees',
                    'online': False,
                    'priority': 90
                }
            ],
            'fallback_categories': {
                'PURCHASE': 'General Purchase',
                'TRANSFER': 'Banking'
            }
        }

    def load_rules(self):
        return self.rules_data

    def get_rule_by_id(self, rule_id: str):
        for rule in self.rules_data['rules']:
            if rule['id'] == rule_id:
                return rule
        return None

    def validate(self) -> ValidationResult:
        return {'is_valid': True, 'errors': [], 'warnings': []}

    def get_metadata(self):
        return {
            'version': '4.0',
            'rule_count': len(self.rules_data['rules'])
        }


class TestClassificationEngine(unittest.TestCase):
    """Test ClassificationEngine classification logic."""

    def setUp(self):
        """Set up test engine with mock provider."""
        self.provider = MockRuleProvider()
        self.engine = ClassificationEngine(self.provider)

    def test_classify_amazon_online_purchase(self):
        """Engine correctly classifies Amazon online purchases."""
        result = self.engine.classify('AMAZON MARK* NH4S31RG1', 'PURCHASE')

        self.assertEqual(result['purchase_type'], 'Personal')
        self.assertEqual(result['category'], 'Online Shopping')
        self.assertEqual(result['subcategory'], 'General Retail')
        self.assertTrue(result['online'])

    def test_classify_business_bank_fees(self):
        """Engine correctly classifies business bank fees."""
        result = self.engine.classify('BUSINESS ACH PMNTS', 'FEE_TRANSACTION')

        self.assertEqual(result['purchase_type'], 'Business')
        self.assertEqual(result['category'], 'Banking')
        self.assertFalse(result['online'])

    def test_priority_based_matching(self):
        """Higher priority rules are checked first."""
        # Both keywords match, but business rule has lower priority
        result = self.engine.classify('AMAZON BUSINESS BANK', 'PURCHASE')

        # Should match AMAZON (priority 100) not BUSINESS BANK (priority 90)
        self.assertEqual(result['category'], 'Online Shopping')

    def test_fallback_category_matching(self):
        """Falls back to category if no keyword matches."""
        result = self.engine.classify('UNKNOWN TRANSACTION', 'PURCHASE')

        # Should match fallback for PURCHASE
        self.assertEqual(result['category'], 'General Purchase')
        self.assertEqual(result['purchase_type'], 'Personal')

    def test_ultimate_fallback(self):
        """Ultimate fallback when nothing matches."""
        result = self.engine.classify('UNKNOWN', 'UNKNOWN')

        self.assertEqual(result['purchase_type'], 'Personal')
        self.assertEqual(result['category'], '')
        self.assertEqual(result['subcategory'], '')
        self.assertFalse(result['online'])

    def test_case_insensitive_matching(self):
        """Keywords match regardless of case."""
        result = self.engine.classify('amazon mark*', 'purchase')

        self.assertEqual(result['category'], 'Online Shopping')

    def test_empty_description(self):
        """Handles empty description gracefully."""
        result = self.engine.classify('', 'PURCHASE')

        self.assertEqual(result['purchase_type'], 'Personal')
        self.assertIsInstance(result, dict)


class TestFileRuleProvider(unittest.TestCase):
    """Test FileRuleProvider."""

    def setUp(self):
        """Create temporary test rules file."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

        # Create v4 rules file
        self.v4_file = self.temp_path / 'rules.v4.json'
        self.v4_rules = {
            'version': '4.0',
            'rules': [
                {
                    'id': 'test-rule',
                    'keywords': ['TEST'],
                    'purchase_type': 'Personal',
                    'category': 'Testing',
                    'subcategory': 'Test',
                    'online': False,
                    'priority': 100
                }
            ],
            'fallback_categories': {}
        }
        with open(self.v4_file, 'w') as f:
            json.dump(self.v4_rules, f)

    def tearDown(self):
        """Clean up temporary files."""
        self.temp_dir.cleanup()

    def test_load_v4_rules(self):
        """FileRuleProvider loads v4 format rules."""
        provider = FileRuleProvider(v4_path=self.v4_file)
        rules = provider.load_rules()

        self.assertEqual(rules['version'], '4.0')
        self.assertEqual(len(rules['rules']), 1)

    def test_get_rule_by_id(self):
        """FileRuleProvider retrieves rule by ID."""
        provider = FileRuleProvider(v4_path=self.v4_file)
        rule = provider.get_rule_by_id('test-rule')

        self.assertIsNotNone(rule)
        self.assertEqual(rule['id'], 'test-rule')

    def test_validate_rules(self):
        """FileRuleProvider validates rules."""
        provider = FileRuleProvider(v4_path=self.v4_file)
        result = provider.validate()

        self.assertTrue(result['is_valid'])
        self.assertEqual(len(result['errors']), 0)

    def test_get_metadata(self):
        """FileRuleProvider returns metadata."""
        provider = FileRuleProvider(v4_path=self.v4_file)
        metadata = provider.get_metadata()

        self.assertEqual(metadata['version'], '4.0')
        self.assertEqual(metadata['rule_count'], 1)

    def test_cache_invalidation(self):
        """FileRuleProvider cache can be invalidated."""
        provider = FileRuleProvider(v4_path=self.v4_file)

        # Load once
        rules1 = provider.load_rules()

        # Invalidate cache
        provider.invalidate_cache()

        # Load again (should reload from file)
        rules2 = provider.load_rules()

        self.assertEqual(rules1, rules2)

    def test_missing_rules_file(self):
        """FileRuleProvider raises error for missing files."""
        provider = FileRuleProvider(
            v4_path='/nonexistent/path/rules.json',
            v3_path='/nonexistent/path/v3.json'
        )

        with self.assertRaises(RuleProviderException):
            provider.load_rules()


class TestEngineWithFileProvider(unittest.TestCase):
    """Integration tests - Engine with FileRuleProvider."""

    def setUp(self):
        """Create test setup with real file provider."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

        # Create rules file
        self.rules_file = self.temp_path / 'rules.json'
        self.rules = {
            'version': '4.0',
            'rules': [
                {
                    'id': 'amazon',
                    'keywords': ['AMAZON', 'AMZN'],
                    'purchase_type': 'Personal',
                    'category': 'Online Shopping',
                    'subcategory': 'General Retail',
                    'online': True,
                    'priority': 100
                }
            ],
            'fallback_categories': {'PURCHASE': 'General Purchase'}
        }
        with open(self.rules_file, 'w') as f:
            json.dump(self.rules, f)

        # Create engine with file provider
        self.provider = FileRuleProvider(v4_path=self.rules_file)
        self.engine = ClassificationEngine(self.provider)

    def tearDown(self):
        """Clean up."""
        self.temp_dir.cleanup()

    def test_end_to_end_classification(self):
        """Full workflow: load rules from file and classify."""
        result = self.engine.classify('AMAZON PURCHASE', 'PURCHASE')

        self.assertEqual(result['purchase_type'], 'Personal')
        self.assertEqual(result['category'], 'Online Shopping')
        self.assertTrue(result['online'])


if __name__ == '__main__':
    unittest.main()
