"""Rule manager - add, remove, update rules."""

import json
from pathlib import Path
from typing import Any, Dict, Optional

from statement_classifier.providers.file import FileRuleProvider
from statement_classifier.types import RuleDict, RuleProviderException


class RuleManager:
    """Manage rules - add, remove, update operations."""

    def __init__(self, rules_path: Path):
        """Initialize with rules file path.

        Args:
            rules_path: Path to rules.json file.
        """
        self.rules_path = Path(rules_path)
        self.provider = FileRuleProvider(v4_path=self.rules_path)

    def add_rule(self, rule: RuleDict) -> bool:
        """Add new rule to rules file.

        Args:
            rule: Rule dict to add.

        Returns:
            True if added successfully.

        Raises:
            RuleProviderException: If operation fails.
        """
        try:
            # Load current rules
            rules_data = self.provider.load_rules()
            rules = rules_data.get('rules', [])

            # Check for duplicate ID
            if any(r['id'] == rule['id'] for r in rules):
                raise ValueError(f"Rule {rule['id']} already exists")

            # Add new rule
            rules.append(rule)

            # Write back
            self._write_rules(rules_data, rules)
            self.provider.invalidate_cache()
            return True

        except Exception as e:
            raise RuleProviderException(f"Failed to add rule: {e}")

    def remove_rule(self, rule_id: str) -> bool:
        """Remove rule by ID.

        Args:
            rule_id: ID of rule to remove.

        Returns:
            True if removed, False if not found.

        Raises:
            RuleProviderException: If operation fails.
        """
        try:
            rules_data = self.provider.load_rules()
            rules = rules_data.get('rules', [])

            original_count = len(rules)
            rules = [r for r in rules if r['id'] != rule_id]

            if len(rules) == original_count:
                return False  # Not found

            self._write_rules(rules_data, rules)
            self.provider.invalidate_cache()
            return True

        except Exception as e:
            raise RuleProviderException(f"Failed to remove rule: {e}")

    def update_rule(self, rule_id: str, updates: Dict[str, Any]) -> bool:
        """Update rule fields.

        Args:
            rule_id: ID of rule to update.
            updates: Dict of fields to update.

        Returns:
            True if updated, False if not found.

        Raises:
            RuleProviderException: If operation fails.
        """
        try:
            rules_data = self.provider.load_rules()
            rules = rules_data.get('rules', [])

            for rule in rules:
                if rule['id'] == rule_id:
                    rule.update(updates)
                    self._write_rules(rules_data, rules)
                    self.provider.invalidate_cache()
                    return True

            return False  # Not found

        except Exception as e:
            raise RuleProviderException(f"Failed to update rule: {e}")

    def get_rule(self, rule_id: str) -> Optional[RuleDict]:
        """Get rule by ID.

        Args:
            rule_id: ID of rule to get.

        Returns:
            Rule dict if found, None otherwise.
        """
        try:
            return self.provider.get_rule_by_id(rule_id)
        except Exception as e:
            raise RuleProviderException(f"Failed to get rule: {e}")

    def _write_rules(self, rules_data: Dict[str, Any], rules: list) -> None:
        """Write rules back to file.

        Args:
            rules_data: Full rules data dict (includes version, fallback, etc).
            rules: Updated rules list.
        """
        rules_data['rules'] = rules
        with open(self.rules_path, 'w') as f:
            json.dump(rules_data, f, indent=2)
