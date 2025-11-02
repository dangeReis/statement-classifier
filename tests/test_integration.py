"""Full integration tests."""

import unittest
import tempfile
import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

from statement_classifier import ClassificationEngine, FileRuleProvider
from statement_classifier.logging import Logger


class TestFullIntegration(unittest.TestCase):
    """End-to-end integration tests."""

    def setUp(self):
        """Create test environment."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.rules_file = Path(self.temp_dir.name) / 'rules.json'

        rules = {
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
                    'id': 'uber',
                    'keywords': ['UBER'],
                    'purchase_type': 'Personal',
                    'category': 'Transportation',
                    'subcategory': 'Rideshare',
                    'online': True,
                    'priority': 95
                }
            ],
            'fallback_categories': {
                'PURCHASE': 'General Purchase',
                'TRANSPORT': 'Transportation'
            }
        }

        with open(self.rules_file, 'w') as f:
            json.dump(rules, f)

    def tearDown(self):
        """Clean up."""
        self.temp_dir.cleanup()

    def test_full_workflow(self):
        """Full workflow: load rules and classify."""
        provider = FileRuleProvider(v4_path=self.rules_file)
        engine = ClassificationEngine(provider)

        # Test keyword match
        result = engine.classify('AMAZON PURCHASE', 'PURCHASE')
        self.assertEqual(result['category'], 'Online Shopping')
        self.assertTrue(result['online'])

        # Test priority - AMAZON priority 100 > UBER priority 95
        result = engine.classify('UBER AMAZON', 'PURCHASE')
        self.assertEqual(result['category'], 'Online Shopping')

        # Test fallback
        result = engine.classify('UNKNOWN', 'PURCHASE')
        self.assertEqual(result['category'], 'General Purchase')

        # Test ultimate fallback
        result = engine.classify('UNKNOWN', 'UNKNOWN')
        self.assertEqual(result['category'], '')

    def test_threading_safety(self):
        """Test thread-safe rule loading."""
        provider = FileRuleProvider(v4_path=self.rules_file)
        engine = ClassificationEngine(provider)

        def classify():
            return engine.classify('AMAZON', 'PURCHASE')

        with ThreadPoolExecutor(max_workers=5) as executor:
            results = list(executor.map(lambda _: classify(), range(10)))

        # All should succeed and return same result
        for result in results:
            self.assertEqual(result['category'], 'Online Shopping')

    def test_logging_integration(self):
        """Test logging with engine."""
        provider = FileRuleProvider(v4_path=self.rules_file)
        engine = ClassificationEngine(provider)
        logger = Logger(enabled=False)

        # Log some operations
        logger.info("Starting classification")
        result = engine.classify('AMAZON', 'PURCHASE')
        logger.info(f"Classification complete: {result['category']}")

        # Should not raise
        self.assertEqual(result['category'], 'Online Shopping')

    def test_multiple_classifications(self):
        """Test multiple classifications in sequence."""
        provider = FileRuleProvider(v4_path=self.rules_file)
        engine = ClassificationEngine(provider)

        test_cases = [
            ('AMAZON PURCHASE', 'PURCHASE', 'Online Shopping'),
            ('UBER TRIP', 'PURCHASE', 'Transportation'),
            ('UNKNOWN MERCHANT', 'PURCHASE', 'General Purchase'),
        ]

        for description, category, expected in test_cases:
            result = engine.classify(description, category)
            self.assertEqual(result['category'], expected)

    def test_provider_caching(self):
        """Test provider cache performance."""
        provider = FileRuleProvider(v4_path=self.rules_file)

        # Load once
        rules1 = provider.load_rules()
        self.assertEqual(len(rules1['rules']), 2)

        # Load again (from cache)
        rules2 = provider.load_rules()
        self.assertEqual(len(rules2['rules']), 2)

        # Both should be identical
        self.assertEqual(rules1, rules2)

    def test_cache_invalidation(self):
        """Test cache can be invalidated."""
        provider = FileRuleProvider(v4_path=self.rules_file)

        # Load once
        rules1 = provider.load_rules()

        # Invalidate cache
        provider.invalidate_cache()

        # Load again (fresh from file)
        rules2 = provider.load_rules()

        # Should be equal
        self.assertEqual(rules1, rules2)

    def test_provider_validation(self):
        """Test provider validates rules on load."""
        provider = FileRuleProvider(v4_path=self.rules_file)
        validation = provider.validate()

        self.assertTrue(validation['is_valid'])
        self.assertEqual(len(validation['errors']), 0)

    def test_engine_with_empty_rules(self):
        """Test engine with no rules."""
        temp_dir = tempfile.TemporaryDirectory()
        rules_file = Path(temp_dir.name) / 'empty_rules.json'

        rules = {
            'version': '4.0',
            'rules': [],
            'fallback_categories': {}
        }

        with open(rules_file, 'w') as f:
            json.dump(rules, f)

        try:
            provider = FileRuleProvider(v4_path=rules_file)
            engine = ClassificationEngine(provider)

            # Should fall back to ultimate default
            result = engine.classify('ANYTHING', 'ANY')
            self.assertEqual(result['category'], '')
            self.assertEqual(result['purchase_type'], 'Personal')
        finally:
            temp_dir.cleanup()


if __name__ == '__main__':
    unittest.main()
