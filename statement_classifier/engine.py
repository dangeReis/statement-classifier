"""Core classification engine - pure business logic.

The engine contains the core classification algorithm and depends only on
the RuleProvider interface. It has no knowledge of where rules come from
or how they're stored.
"""

from typing import Dict, Any, Optional

from statement_classifier.types import (
    ClassificationResult,
    RuleProviderException,
    RuleFormatException,
)
from statement_classifier.providers import RuleProvider
from statement_classifier.normalization import RuleNormalizer


class ClassificationEngine:
    """Pure classification logic using rules from any provider.

    The engine doesn't know or care where rules come from.
    It only knows:
    1. How to get rules from a RuleProvider
    2. How to match rules by priority
    3. How to return a ClassificationResult

    This is the core of the black box design - the engine is completely
    independent of rule sources, formats, or storage mechanisms.
    """

    def __init__(self, rule_provider: RuleProvider):
        """Initialize engine with a rule provider.

        Args:
            rule_provider: Any RuleProvider implementation.
                          Could be file, database, API, or mock.
        """
        self.provider = rule_provider
        self._rules_cache: Optional[Dict[str, Any]] = None

    def classify(self, description: str, category: str) -> ClassificationResult:
        """Classify a transaction.

        Args:
            description: Transaction description (any case).
            category: Merchant category code.

        Returns:
            ClassificationResult with:
            - purchase_type: "Business" or "Personal"
            - category: Classification category
            - subcategory: Specific subcategory
            - online: Whether transaction is online
        """
        # Normalize inputs
        desc_upper = description.upper().strip() if description else ""
        cat_upper = category.upper().strip() if category else ""

        # Load rules
        rules_data = self._load_rules()
        rules = rules_data.get('rules', [])
        fallback = rules_data.get('fallback_categories', {})

        # Try keyword matching (highest priority first)
        result = self._match_rules(desc_upper, rules)
        if result:
            return result

        # Fall back to category-based matching
        result = self._match_fallback(cat_upper, fallback)
        if result:
            return result

        # Ultimate fallback: Personal with no category
        return {
            'purchase_type': 'Personal',
            'category': '',
            'subcategory': '',
            'online': False
        }

    def _load_rules(self) -> Dict[str, Any]:
        """Load and normalize rules from provider.

        Returns:
            Normalized rules dict in v4 format.

        Raises:
            RuleProviderException: If rules cannot be loaded.
            RuleFormatException: If rules are malformed.
        """
        try:
            rules_data = self.provider.load_rules()
            normalized = RuleNormalizer.normalize(rules_data)
            return normalized
        except RuleProviderException:
            raise
        except RuleFormatException:
            raise
        except Exception as e:
            raise RuleProviderException(f"Failed to load rules: {e}")

    def _match_rules(
        self,
        description: str,
        rules: list
    ) -> Optional[ClassificationResult]:
        """Match description against rules by priority.

        Rules are sorted by priority (higher first), so first match wins.

        Args:
            description: Normalized (uppercase) transaction description.
            rules: List of rule dicts in v4 format.

        Returns:
            ClassificationResult if matched, None otherwise.
        """
        # Sort rules by priority descending (highest priority first)
        sorted_rules = sorted(
            rules,
            key=lambda r: r.get('priority', 0),
            reverse=True
        )

        for rule in sorted_rules:
            keywords = rule.get('keywords', [])

            # Check if ANY keyword matches the description
            for keyword in keywords:
                if keyword in description:
                    # Match found - return rule's classification
                    return {
                        'purchase_type': rule.get('purchase_type', 'Personal'),
                        'category': rule.get('category', ''),
                        'subcategory': rule.get('subcategory', ''),
                        'online': rule.get('online', False)
                    }

        return None

    def _match_fallback(
        self,
        category: str,
        fallback_map: Dict[str, str]
    ) -> Optional[ClassificationResult]:
        """Match using fallback category mapping.

        Used when no keyword rules match. Provides a baseline
        classification based on merchant category code.

        Args:
            category: Merchant category code (uppercase).
            fallback_map: Dict mapping category codes to category names.

        Returns:
            ClassificationResult if matched, None otherwise.
        """
        if not category or not fallback_map:
            return None

        # Direct category match when map is code -> category string
        if category in fallback_map and isinstance(fallback_map[category], str):
            return {
                'purchase_type': 'Personal',
                'category': fallback_map[category],
                'subcategory': '',
                'online': False
            }

        # Support v4 rules where fallback map stores category -> [codes]
        for fallback_category, codes in fallback_map.items():
            if not isinstance(codes, (list, tuple)):
                continue

            normalized_codes = [code.upper().strip() for code in codes if code]
            if category in normalized_codes:
                return {
                    'purchase_type': 'Personal',
                    'category': fallback_category,
                    'subcategory': '',
                    'online': False
                }

        return None
