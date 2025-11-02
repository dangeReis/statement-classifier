"""Abstract base class for rule providers.

A RuleProvider is an abstraction for loading rules from any source.
The classifier depends on this interface, not on any concrete implementation.

This enables loading rules from:
- JSON files (FileRuleProvider)
- Databases (DatabaseRuleProvider - future)
- REST APIs (APIRuleProvider - future)
- In-memory storage (MemoryRuleProvider - for testing)

The classifier has no idea where rules come from - it only knows the interface.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

from statement_classifier.types import ValidationResult, RuleDict


class RuleProvider(ABC):
    """Abstract interface for rule loading from any source.

    All rule providers implement this interface, allowing the classifier
    to work with rules regardless of their origin.

    This is the core of the black box design:
    - The classifier depends on the interface, not the implementation
    - New providers can be added without changing the classifier
    - Providers can be swapped or composed without breaking anything
    """

    @abstractmethod
    def load_rules(self) -> Dict[str, Any]:
        """Load rules and metadata.

        Returns:
            Dict with structure:
            {
                'version': '4.0',
                'rules': [RuleDict, ...],  # List of rule objects
                'fallback_categories': Dict  # Fallback mapping
            }

        Raises:
            RuleProviderException: If rules cannot be loaded for any reason.
        """
        pass

    @abstractmethod
    def get_rule_by_id(self, rule_id: str) -> Optional[RuleDict]:
        """Get a specific rule by ID.

        Args:
            rule_id: The unique rule identifier (lowercase, hyphenated).

        Returns:
            Rule dict if found, None if not found.

        This allows individual rule lookups without loading all rules.
        Useful for debugging, updating, or removing specific rules.
        """
        pass

    @abstractmethod
    def validate(self) -> ValidationResult:
        """Validate that all rules are correct.

        Returns:
            ValidationResult TypedDict with:
            {
                'is_valid': bool,      # True if all validations passed
                'errors': [str],       # Fatal errors (must be fixed)
                'warnings': [str]      # Non-fatal warnings (should review)
            }

        This allows checking rule integrity without using them.
        """
        pass

    @abstractmethod
    def get_metadata(self) -> Dict[str, Any]:
        """Get metadata about the rules.

        Returns:
            Dict with metadata such as:
            {
                'version': '4.0',
                'rule_count': 150,
                'last_updated': '2025-11-02T17:36:00Z',
                'source': 'classification_rules.v4.json'
            }

        Metadata helps understand rule status without loading all data.
        """
        pass
