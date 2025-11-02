"""Tests for orchestration and logging."""

import unittest
from unittest.mock import Mock

from statement_classifier.engine import ClassificationEngine
from statement_classifier.orchestration.base import WorkflowProvider
from statement_classifier.coordinator import RuleUpdateOrchestrator
from statement_classifier.logging import Logger
from statement_classifier.providers import RuleProvider
from statement_classifier.types import ValidationResult


class MockRuleProvider(RuleProvider):
    """Mock provider for testing."""

    def load_rules(self):
        return {'version': '4.0', 'rules': [], 'fallback_categories': {}}

    def get_rule_by_id(self, rule_id):
        return None

    def validate(self) -> ValidationResult:
        return {'is_valid': True, 'errors': [], 'warnings': []}

    def get_metadata(self):
        return {'version': '4.0', 'rule_count': 0}


class MockWorkflow(WorkflowProvider):
    """Mock workflow for testing."""

    def create_branch(self, branch_name: str) -> bool:
        return True

    def create_pull_request(self, title: str, body: str) -> int:
        return 123

    def wait_for_approval(self, pr_number: int, timeout: int) -> bool:
        return True

    def merge_pull_request(self, pr_number: int) -> bool:
        return True


class TestLogger(unittest.TestCase):
    """Test Logger."""

    def test_logger_disabled_by_default(self):
        """Logger is disabled by default."""
        logger = Logger()
        self.assertFalse(logger.enabled)

    def test_logger_can_be_enabled(self):
        """Logger can be enabled."""
        logger = Logger(enabled=True)
        self.assertTrue(logger.enabled)
        logger.info("Test message")  # Should not raise

    def test_logger_info(self):
        """Logger info method works."""
        logger = Logger(enabled=False)
        logger.info("Test message")  # Should not raise

    def test_logger_debug(self):
        """Logger debug method works."""
        logger = Logger(enabled=False)
        logger.debug("Test message")  # Should not raise

    def test_logger_error(self):
        """Logger error method works."""
        logger = Logger(enabled=False)
        logger.error("Test message")  # Should not raise

    def test_logger_warning(self):
        """Logger warning method works."""
        logger = Logger(enabled=False)
        logger.warning("Test message")  # Should not raise


class TestOrchestrator(unittest.TestCase):
    """Test RuleUpdateOrchestrator."""

    def setUp(self):
        """Set up test orchestrator."""
        provider = MockRuleProvider()
        self.engine = ClassificationEngine(provider)
        self.workflow = MockWorkflow()
        self.orchestrator = RuleUpdateOrchestrator(self.workflow, self.engine)

    def test_propose_rule_update(self):
        """Orchestrator proposes rule updates."""
        result = self.orchestrator.propose_rule_update([])
        self.assertTrue(result['success'])
        self.assertEqual(result['pr_number'], 123)

    def test_propose_rule_update_branch_creation(self):
        """Orchestrator creates branch for rule updates."""
        result = self.orchestrator.propose_rule_update([])
        self.assertEqual(result['branch'], 'feature/rule-update')

    def test_propose_rule_removal(self):
        """Orchestrator proposes rule removal."""
        result = self.orchestrator.propose_rule_removal(['rule-1'])
        self.assertTrue(result['success'])
        self.assertEqual(result['rule_ids'], ['rule-1'])

    def test_batch_update(self):
        """Orchestrator handles batch updates."""
        result = self.orchestrator.batch_update([{'id': 'test'}])
        self.assertTrue(result['success'])
        self.assertEqual(result['changes'], 1)

    def test_batch_update_multiple(self):
        """Orchestrator handles multiple batch updates."""
        changes = [{'id': 'test1'}, {'id': 'test2'}, {'id': 'test3'}]
        result = self.orchestrator.batch_update(changes)
        self.assertEqual(result['changes'], 3)


if __name__ == '__main__':
    unittest.main()
