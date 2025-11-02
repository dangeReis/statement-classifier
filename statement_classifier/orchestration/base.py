"""Abstract workflow provider interface."""

from abc import ABC, abstractmethod
from typing import Dict, Any


class WorkflowProvider(ABC):
    """Abstract interface for workflow automation."""

    @abstractmethod
    def create_branch(self, branch_name: str) -> bool:
        """Create feature branch."""
        pass

    @abstractmethod
    def create_pull_request(self, title: str, body: str) -> int:
        """Create PR, return PR number."""
        pass

    @abstractmethod
    def wait_for_approval(self, pr_number: int, timeout: int) -> bool:
        """Wait for PR approval."""
        pass

    @abstractmethod
    def merge_pull_request(self, pr_number: int) -> bool:
        """Merge approved PR."""
        pass
