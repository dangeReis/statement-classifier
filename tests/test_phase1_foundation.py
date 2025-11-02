"""Unit tests for Phase 1 foundation components.

Tests verify that the core abstractions and types work correctly.
These tests ensure the black box design principles are maintained.
"""

import unittest
from typing import Dict, Any

from statement_classifier.types import (
    TransactionInput,
    ClassificationResult,
    RuleDict,
    ValidationResult,
    ClassifierException,
    RuleProviderException,
    RuleFormatException,
    ValidationException,
    OrchestrationException,
)
from statement_classifier.providers import RuleProvider
from statement_classifier.normalization import RuleNormalizer


class TestTypes(unittest.TestCase):
    """Test type definitions."""

    def test_transaction_input_creation(self):
        """TransactionInput can be created with required fields."""
        tx: TransactionInput = {
            'description': 'AMAZON MARK* NH4S31RG1',
            'category': 'PURCHASE'
        }
        self.assertEqual(tx['description'], 'AMAZON MARK* NH4S31RG1')
        self.assertEqual(tx['category'], 'PURCHASE')

    def test_classification_result_creation(self):
        """ClassificationResult can be created with all fields."""
        result: ClassificationResult = {
            'purchase_type': 'Personal',
            'category': 'Online Shopping',
            'subcategory': 'General Retail',
            'online': True
        }
        self.assertEqual(result['purchase_type'], 'Personal')
        self.assertTrue(result['online'])

    def test_rule_dict_creation(self):
        """RuleDict can be created with required and optional fields."""
        rule: RuleDict = {
            'id': 'amazon-online-shopping',
            'keywords': ['AMAZON', 'AMZN'],
            'purchase_type': 'Personal',
            'category': 'Online Shopping',
            'subcategory': 'General Retail',
            'online': True,
            'priority': 100,
        }
        self.assertEqual(rule['id'], 'amazon-online-shopping')
        self.assertIn('AMAZON', rule['keywords'])

    def test_validation_result_creation(self):
        """ValidationResult can be created."""
        result: ValidationResult = {
            'is_valid': True,
            'errors': [],
            'warnings': []
        }
        self.assertTrue(result['is_valid'])


class TestExceptionHierarchy(unittest.TestCase):
    """Test exception hierarchy."""

    def test_rule_provider_exception_is_classifier_exception(self):
        """RuleProviderException inherits from ClassifierException."""
        exc = RuleProviderException("test")
        self.assertIsInstance(exc, ClassifierException)

    def test_rule_format_exception_is_classifier_exception(self):
        """RuleFormatException inherits from ClassifierException."""
        exc = RuleFormatException("test")
        self.assertIsInstance(exc, ClassifierException)

    def test_validation_exception_is_classifier_exception(self):
        """ValidationException inherits from ClassifierException."""
        exc = ValidationException("test")
        self.assertIsInstance(exc, ClassifierException)

    def test_orchestration_exception_is_classifier_exception(self):
        """OrchestrationException inherits from ClassifierException."""
        exc = OrchestrationException("test")
        self.assertIsInstance(exc, ClassifierException)

    def test_catching_base_exception(self):
        """Can catch specific exceptions through base ClassifierException."""
        try:
            raise RuleFormatException("Invalid format")
        except ClassifierException as e:
            self.assertIn("Invalid format", str(e))


class TestRuleProvider(unittest.TestCase):
    """Test RuleProvider interface."""

    def test_rule_provider_cannot_be_instantiated(self):
        """RuleProvider is abstract and cannot be instantiated."""
        with self.assertRaises(TypeError):
            RuleProvider()  # type: ignore

    def test_rule_provider_requires_all_methods(self):
        """Subclass of RuleProvider must implement all abstract methods."""

        # This should fail - incomplete implementation
        class IncompleteProvider(RuleProvider):
            def load_rules(self):
                pass

        with self.assertRaises(TypeError):
            IncompleteProvider()  # type: ignore

    def test_complete_provider_can_be_created(self):
        """Concrete implementation of RuleProvider can be instantiated."""

        class MockProvider(RuleProvider):
            def load_rules(self) -> Dict[str, Any]:
                return {
                    'version': '4.0',
                    'rules': [],
                    'fallback_categories': {}
                }

            def get_rule_by_id(self, rule_id: str):
                return None

            def validate(self) -> ValidationResult:
                return {
                    'is_valid': True,
                    'errors': [],
                    'warnings': []
                }

            def get_metadata(self) -> Dict[str, Any]:
                return {
                    'version': '4.0',
                    'rule_count': 0
                }

        provider = MockProvider()
        self.assertIsNotNone(provider)
        self.assertEqual(len(provider.load_rules()['rules']), 0)


class TestRuleNormalizer(unittest.TestCase):
    """Test RuleNormalizer format conversion."""

    def test_normalize_v4_rules(self):
        """normalize() returns v4 rules unchanged."""
        v4_rules = {
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

        result = RuleNormalizer.normalize(v4_rules)
        self.assertEqual(result['version'], '4.0')
        self.assertEqual(len(result['rules']), 1)
        self.assertEqual(result['rules'][0]['id'], 'test-rule')

    def test_normalize_v3_to_v4(self):
        """normalize() converts v3 rules to v4."""
        v3_rules = {
            'version': '3.0',
            'business_keywords': ['BUSINESS BANK'],
            'transaction_rules': {
                'amazon': ('Online Shopping', 'General Retail', ['AMAZON', 'AMZN'])
            },
            'online_purchase_keywords': ['AMAZON'],
            'fallback_categories': {'PURCHASE': 'Personal'}
        }

        result = RuleNormalizer.normalize(v3_rules)
        self.assertEqual(result['version'], '4.0')
        self.assertGreater(len(result['rules']), 0)

        # Check that business keyword was converted
        business_keywords = [
            r['keywords'][0]
            for r in result['rules']
            if r['purchase_type'] == 'Business'
        ]
        self.assertIn('BUSINESS BANK', business_keywords)

    def test_normalize_invalid_v4_format(self):
        """normalize() raises RuleFormatException for invalid v4."""
        invalid = {
            'version': '4.0',
            'rules': 'not-a-list'  # Should be list
        }

        with self.assertRaises(RuleFormatException):
            RuleNormalizer.normalize(invalid)

    def test_normalize_unknown_format(self):
        """normalize() raises RuleFormatException for unknown version."""
        unknown = {
            'version': '99.0'
        }

        with self.assertRaises(RuleFormatException):
            RuleNormalizer.normalize(unknown)

    def test_normalize_auto_detects_v3(self):
        """normalize() auto-detects v3 format by structure."""
        v3_like = {
            'business_keywords': ['TEST'],
            'transaction_rules': {},
            'fallback_categories': {}
        }

        result = RuleNormalizer.normalize(v3_like)
        self.assertEqual(result['version'], '4.0')

    def test_normalize_preserves_fallback_categories(self):
        """normalize() preserves fallback_categories through conversion."""
        v3_rules = {
            'version': '3.0',
            'business_keywords': [],
            'transaction_rules': {},
            'fallback_categories': {
                'PURCHASE': 'Personal',
                'TRANSFER': 'Banking'
            }
        }

        result = RuleNormalizer.normalize(v3_rules)
        self.assertEqual(
            result['fallback_categories']['PURCHASE'],
            'Personal'
        )
        self.assertEqual(
            result['fallback_categories']['TRANSFER'],
            'Banking'
        )


class TestPackageImports(unittest.TestCase):
    """Test that package imports work correctly."""

    def test_can_import_from_package(self):
        """All public APIs can be imported from statement_classifier."""
        from statement_classifier import (
            TransactionInput,
            ClassificationResult,
            RuleDict,
            ValidationResult,
            ClassifierException,
            RuleProviderException,
            RuleFormatException,
            ValidationException,
            OrchestrationException,
            RuleProvider,
        )

        self.assertIsNotNone(TransactionInput)
        self.assertIsNotNone(RuleProvider)
        self.assertIsNotNone(ClassifierException)

    def test_package_version(self):
        """Package has version attribute."""
        import statement_classifier
        self.assertEqual(statement_classifier.__version__, '2.0.0')

    def test_package_author(self):
        """Package has author attribute."""
        import statement_classifier
        self.assertEqual(statement_classifier.__author__, 'Russ Lee')

    def test_no_circular_imports(self):
        """Package imports don't have circular dependencies."""
        # If this test runs without hanging, imports are not circular
        import statement_classifier
        from statement_classifier.providers import base
        from statement_classifier import normalization
        self.assertIsNotNone(statement_classifier)
        self.assertIsNotNone(base)
        self.assertIsNotNone(normalization)


if __name__ == '__main__':
    unittest.main()
