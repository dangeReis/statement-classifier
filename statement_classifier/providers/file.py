"""File-based rule provider - load rules from JSON files.

Implements the RuleProvider interface for loading rules from JSON files.
Supports both v4 and v3 formats with automatic format detection.
"""

import json
from pathlib import Path
from threading import RLock
from typing import Dict, Any, Optional, Union

from statement_classifier.types import (
    RuleDict,
    ValidationResult,
    RuleProviderException,
    RuleFormatException,
)
from statement_classifier.providers.base import RuleProvider
from statement_classifier.normalization import RuleNormalizer


class FileRuleProvider(RuleProvider):
    """Load rules from JSON files.

    Tries to load rules in this order:
    1. v4 format (preferred): classification_rules.v4.json
    2. v3 format (fallback): rules.json

    Caches loaded rules in memory for performance.
    Thread-safe with RLock for concurrent access.
    """

    def __init__(
        self,
        v4_path: Optional[Union[Path, str]] = None,
        v3_path: Optional[Union[Path, str]] = None,
        auto_detect: bool = True
    ):
        """Initialize file rule provider.

        Args:
            v4_path: Path to v4 format rules file.
                    Defaults to bin/classification_rules.v4.json
            v3_path: Path to v3 format rules file (fallback).
                    Defaults to bin/rules.json
            auto_detect: If True, automatically detect format version.
        """
        self._lock = RLock()
        self._cache: Optional[Dict[str, Any]] = None
        self._cache_valid = False

        # Set default paths relative to project root
        if v4_path is None:
            v4_path = (
                Path(__file__).parent.parent.parent
                / 'bin'
                / 'classification_rules.v4.json'
            )
        if v3_path is None:
            v3_path = (
                Path(__file__).parent.parent.parent
                / 'bin'
                / 'rules.json'
            )

        self.v4_path = Path(v4_path)
        self.v3_path = Path(v3_path)
        self.auto_detect = auto_detect

    def load_rules(self) -> Dict[str, Any]:
        """Load rules from file.

        Tries v4 first, then v3, raises if neither available.

        Returns:
            Rules dict in v4 format (after normalization).

        Raises:
            RuleProviderException: If rules cannot be loaded.
        """
        with self._lock:
            # Return cached if available
            if self._cache_valid and self._cache is not None:
                return self._cache

            # Try v4 first (preferred)
            if self.v4_path.exists():
                try:
                    rules = self._load_json(self.v4_path)
                    self._cache = rules
                    self._cache_valid = True
                    return rules
                except Exception as e:
                    raise RuleProviderException(
                        f"Failed to load v4 rules from {self.v4_path}: {e}"
                    )

            # Fall back to v3
            if self.v3_path.exists():
                try:
                    rules = self._load_json(self.v3_path)
                    self._cache = rules
                    self._cache_valid = True
                    return rules
                except Exception as e:
                    raise RuleProviderException(
                        f"Failed to load v3 rules from {self.v3_path}: {e}"
                    )

            # No rules file found
            raise RuleProviderException(
                f"No rules files found. Tried: {self.v4_path}, {self.v3_path}"
            )

    def get_rule_by_id(self, rule_id: str) -> Optional[RuleDict]:
        """Get a specific rule by ID.

        Args:
            rule_id: The rule ID to find.

        Returns:
            Rule dict if found, None otherwise.
        """
        try:
            rules_data = self.load_rules()
            # Normalize v3 to v4 format if needed
            normalized_data = RuleNormalizer.normalize(rules_data)
            rules = normalized_data.get('rules', [])

            for rule in rules:
                if rule.get('id') == rule_id:
                    return rule

            return None
        except Exception as e:
            raise RuleProviderException(f"Failed to get rule {rule_id}: {e}")

    def validate(self) -> ValidationResult:
        """Validate rules.

        Returns:
            ValidationResult with any errors/warnings found.
        """
        errors = []
        warnings = []

        try:
            rules_data = self.load_rules()
            # Normalize v3 to v4 format if needed
            normalized_data = RuleNormalizer.normalize(rules_data)
            rules = normalized_data.get('rules', [])

            # Basic structure validation
            if not isinstance(rules, list):
                errors.append("'rules' must be a list")
                return {
                    'is_valid': False,
                    'errors': errors,
                    'warnings': warnings
                }

            # Check each rule
            seen_ids = set()
            for i, rule in enumerate(rules):
                # Check required fields
                if 'id' not in rule:
                    errors.append(f"Rule {i} missing 'id' field")
                elif rule['id'] in seen_ids:
                    errors.append(f"Duplicate rule ID: {rule['id']}")
                else:
                    seen_ids.add(rule['id'])

                if 'keywords' not in rule:
                    errors.append(f"Rule {rule.get('id', i)} missing 'keywords'")
                elif not isinstance(rule['keywords'], list):
                    errors.append(
                        f"Rule {rule.get('id', i)} keywords must be list"
                    )
                else:
                    # Check keywords are uppercase
                    for kw in rule['keywords']:
                        if kw != kw.upper():
                            warnings.append(
                                f"Rule {rule.get('id', i)} "
                                f"keyword '{kw}' not uppercase"
                            )

                # Check purchase_type
                if rule.get('purchase_type') not in ('Business', 'Personal'):
                    errors.append(
                        f"Rule {rule.get('id', i)} invalid purchase_type: "
                        f"{rule.get('purchase_type')}"
                    )

            return {
                'is_valid': len(errors) == 0,
                'errors': errors,
                'warnings': warnings
            }

        except RuleProviderException as e:
            return {
                'is_valid': False,
                'errors': [str(e)],
                'warnings': []
            }

    def get_metadata(self) -> Dict[str, Any]:
        """Get metadata about the rules.

        Returns:
            Metadata dict with version, count, path info.
        """
        try:
            rules_data = self.load_rules()
            # Normalize v3 to v4 format if needed
            normalized_data = RuleNormalizer.normalize(rules_data)
            rules = normalized_data.get('rules', [])

            return {
                'version': normalized_data.get('version', '4.0'),
                'rule_count': len(rules),
                'v4_path': str(self.v4_path),
                'v3_path': str(self.v3_path),
                'source': 'file'
            }
        except Exception as e:
            return {
                'version': '4.0',
                'rule_count': 0,
                'error': str(e),
                'source': 'file'
            }

    def invalidate_cache(self) -> None:
        """Invalidate the cache to force reload.

        Useful after rules files are updated.
        """
        with self._lock:
            self._cache_valid = False
            self._cache = None

    def _load_json(self, path: Path) -> Dict[str, Any]:
        """Load and parse JSON file.

        Args:
            path: Path to JSON file.

        Returns:
            Parsed JSON as dict.

        Raises:
            RuleFormatException: If JSON is invalid.
        """
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise RuleFormatException(f"Invalid JSON in {path}: {e}")
        except FileNotFoundError:
            raise RuleProviderException(f"File not found: {path}")
        except IOError as e:
            raise RuleProviderException(f"Cannot read {path}: {e}")
