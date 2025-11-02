"""Tests for CLI tools."""

import json
import tempfile
import unittest
from pathlib import Path

from bin.cli.rule_analyzer import RuleAnalyzer
from bin.cli.rule_manager import RuleManager
from bin.cli.rule_tester import RuleTestRunner
from bin.cli.rule_validator import RuleValidator
from statement_classifier.types import RuleProviderException


class TestRuleManager(unittest.TestCase):
    """Test RuleManager."""

    def setUp(self):
        """Create temp rules file."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.rules_path = Path(self.temp_dir.name) / 'rules.json'

        self.rules = {
            'version': '4.0',
            'rules': [
                {
                    'id': 'test-1',
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
        with open(self.rules_path, 'w') as f:
            json.dump(self.rules, f)

    def tearDown(self):
        """Clean up."""
        self.temp_dir.cleanup()

    def test_add_rule(self):
        """RuleManager can add rules."""
        manager = RuleManager(self.rules_path)

        new_rule = {
            'id': 'test-2',
            'keywords': ['NEW'],
            'purchase_type': 'Business',
            'category': 'New',
            'subcategory': 'Test',
            'online': True,
            'priority': 90
        }

        result = manager.add_rule(new_rule)
        self.assertTrue(result)

        # Verify it was added
        rule = manager.get_rule('test-2')
        self.assertIsNotNone(rule)
        self.assertEqual(rule['id'], 'test-2')

    def test_remove_rule(self):
        """RuleManager can remove rules."""
        manager = RuleManager(self.rules_path)

        result = manager.remove_rule('test-1')
        self.assertTrue(result)

        # Verify it was removed
        rule = manager.get_rule('test-1')
        self.assertIsNone(rule)

    def test_update_rule(self):
        """RuleManager can update rules."""
        manager = RuleManager(self.rules_path)

        result = manager.update_rule('test-1', {'priority': 50})
        self.assertTrue(result)

        # Verify it was updated
        rule = manager.get_rule('test-1')
        self.assertEqual(rule['priority'], 50)


class TestRuleValidator(unittest.TestCase):
    """Test RuleValidator."""

    def setUp(self):
        """Create temp rules file."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.rules_path = Path(self.temp_dir.name) / 'rules.json'

        self.rules = {
            'version': '4.0',
            'rules': [
                {
                    'id': 'valid-rule',
                    'keywords': ['VALID'],
                    'purchase_type': 'Personal',
                    'category': 'Valid',
                    'subcategory': '',
                    'online': False,
                    'priority': 100
                }
            ],
            'fallback_categories': {}
        }
        with open(self.rules_path, 'w') as f:
            json.dump(self.rules, f)

    def tearDown(self):
        """Clean up."""
        self.temp_dir.cleanup()

    def test_validate_valid_rules(self):
        """Validator passes on valid rules."""
        validator = RuleValidator(self.rules_path)
        result = validator.validate()

        self.assertTrue(result['is_valid'])
        self.assertEqual(len(result['errors']), 0)

    def test_get_report(self):
        """Validator provides readable report."""
        validator = RuleValidator(self.rules_path)
        report = validator.get_report()

        self.assertIn('✅', report)
        self.assertIsInstance(report, str)


class TestRuleAnalyzer(unittest.TestCase):
    """Test RuleAnalyzer."""

    def setUp(self):
        """Create temp rules file."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.rules_path = Path(self.temp_dir.name) / 'rules.json'

        self.rules = {
            'version': '4.0',
            'rules': [
                {
                    'id': 'rule-1',
                    'keywords': ['KEY1', 'KEY2'],
                    'purchase_type': 'Personal',
                    'category': 'Cat1',
                    'subcategory': 'Sub1',
                    'online': True,
                    'priority': 100
                },
                {
                    'id': 'rule-2',
                    'keywords': ['KEY3'],
                    'purchase_type': 'Business',
                    'category': 'Cat1',
                    'subcategory': '',
                    'online': False,
                    'priority': 90
                }
            ],
            'fallback_categories': {'PURCHASE': 'Personal'}
        }
        with open(self.rules_path, 'w') as f:
            json.dump(self.rules, f)

    def tearDown(self):
        """Clean up."""
        self.temp_dir.cleanup()

    def test_get_stats(self):
        """Analyzer provides statistics."""
        analyzer = RuleAnalyzer(self.rules_path)
        stats = analyzer.get_stats()

        self.assertEqual(stats['total_rules'], 2)
        self.assertEqual(stats['total_keywords'], 3)
        self.assertEqual(stats['business_rules'], 1)
        self.assertEqual(stats['personal_rules'], 1)
        self.assertEqual(stats['online_rules'], 1)

    def test_coverage_analysis(self):
        """Analyzer provides coverage metrics."""
        analyzer = RuleAnalyzer(self.rules_path)
        coverage = analyzer.coverage_analysis()

        self.assertEqual(coverage['total_fallback_categories'], 1)
        self.assertEqual(coverage['unique_keywords'], 3)


class TestRuleTestRunner(unittest.TestCase):
    """Test RuleTestRunner."""

    def setUp(self):
        """Create temp rules file."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.rules_path = Path(self.temp_dir.name) / 'rules.json'

        self.rules = {
            'version': '4.0',
            'rules': [
                {
                    'id': 'amazon',
                    'keywords': ['AMAZON'],
                    'purchase_type': 'Personal',
                    'category': 'Online Shopping',
                    'subcategory': 'Retail',
                    'online': True,
                    'priority': 100
                }
            ],
            'fallback_categories': {'PURCHASE': 'Purchase'}
        }
        with open(self.rules_path, 'w') as f:
            json.dump(self.rules, f)

    def tearDown(self):
        """Clean up."""
        self.temp_dir.cleanup()

    def test_classify_with_rule(self):
        """TestRunner classifies with matching rule."""
        runner = RuleTestRunner(self.rules_path)
        result = runner.test_classification('AMAZON PURCHASE', 'PURCHASE')

        self.assertEqual(result['result']['category'], 'Online Shopping')
        self.assertEqual(result['matching_rule'], 'amazon')

    def test_batch_test(self):
        """TestRunner handles batch testing."""
        runner = RuleTestRunner(self.rules_path)
        results = runner.batch_test([
            {'description': 'AMAZON', 'category': 'PURCHASE'},
            {'description': 'UNKNOWN', 'category': 'PURCHASE'}
        ])

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['matching_rule'], 'amazon')
        self.assertIsNone(results[1]['matching_rule'])


if __name__ == '__main__':
    unittest.main()
