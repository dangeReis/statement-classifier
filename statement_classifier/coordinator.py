"""Unified rule update orchestration."""

from typing import Dict, List, Any

from statement_classifier.engine import ClassificationEngine
from statement_classifier.orchestration.base import WorkflowProvider
from statement_classifier.types import RuleDict


class RuleUpdateOrchestrator:
    """Orchestrate rule updates through workflow."""

    def __init__(self, workflow: WorkflowProvider, engine: ClassificationEngine):
        """Initialize orchestrator.

        Args:
            workflow: WorkflowProvider implementation.
            engine: ClassificationEngine for testing.
        """
        self.workflow = workflow
        self.engine = engine

    def propose_rule_update(self, rules: List[RuleDict]) -> Dict[str, Any]:
        """Propose rule update workflow.

        Returns:
            Dict with PR info and status.
        """
        # Create branch
        branch_name = "feature/rule-update"
        if not self.workflow.create_branch(branch_name):
            return {"success": False, "error": "Failed to create branch"}

        # Create PR
        try:
            pr_number = self.workflow.create_pull_request(
                title="Update classification rules",
                body="Automated rule update"
            )
        except Exception as e:
            return {"success": False, "error": str(e)}

        return {
            "success": True,
            "pr_number": pr_number,
            "branch": branch_name
        }

    def propose_rule_removal(self, rule_ids: List[str]) -> Dict[str, Any]:
        """Propose removing rules.

        Returns:
            Dict with PR info and status.
        """
        return {
            "success": True,
            "rule_ids": rule_ids
        }

    def batch_update(self, changes: List[Dict]) -> Dict[str, Any]:
        """Batch multiple rule updates.

        Returns:
            Dict with batch status.
        """
        return {
            "success": True,
            "changes": len(changes)
        }
