"""Format normalization - abstract away v3/v4 differences.

This module handles converting between rule formats, allowing the system
to support multiple versions without the classifier knowing about it.

All rules are normalized to v4 format internally, giving the classifier
a consistent interface regardless of source format.
"""

from typing import Dict, Any

from statement_classifier.types import RuleFormatException


class RuleNormalizer:
    """Normalize rules from any format to internal v4 representation.

    This class hides format version differences from the classifier.
    The classifier always works with normalized (v4) rules.

    Supported formats:
    - v4.0: Native format with priority-ordered rules
    - v3.0: Legacy format with separate business/transaction rules
    """

    @staticmethod
    def normalize(rules_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize rules to v4 format.

        Accepts rules in any format and returns them in normalized v4 format.
        This allows the classifier to work with rules regardless of how they're stored.

        Args:
            rules_data: Raw rules loaded from any provider.
                Should be a dict with 'version' key or detectable format.

        Returns:
            Normalized rules in v4 format:
            {
                'version': '4.0',
                'rules': List[RuleDict],
                'fallback_categories': Dict
            }

        Raises:
            RuleFormatException: If rules are malformed or format is unknown.
        """
        version = rules_data.get('version')

        if version == '4.0':
            return RuleNormalizer._validate_v4(rules_data)
        elif version == '3.0' or 'business_keywords' in rules_data:
            # Auto-detect v3 format by structure
            return RuleNormalizer._v3_to_v4(rules_data)
        else:
            raise RuleFormatException(
                f"Unknown rule format version: {version}. "
                "Expected '3.0' or '4.0'."
            )

    @staticmethod
    def _validate_v4(rules_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and return v4 format rules.

        Args:
            rules_data: Rules dict claiming to be v4.0

        Returns:
            Same rules dict if valid.

        Raises:
            RuleFormatException: If v4 structure is invalid.
        """
        if 'rules' not in rules_data:
            raise RuleFormatException("v4 rules must have 'rules' key")

        if not isinstance(rules_data['rules'], list):
            raise RuleFormatException("v4 'rules' must be a list")

        return rules_data

    @staticmethod
    def _v3_to_v4(v3_rules: Dict[str, Any]) -> Dict[str, Any]:
        """Convert v3 format to v4.

        v3 format structure:
        {
            'business_keywords': ['KEYWORD1', 'KEYWORD2'],
            'transaction_rules': {
                'rule_id': (category, subcategory, [keywords])
            },
            'online_purchase_keywords': ['KEYWORD'],
            'fallback_categories': {
                'CODE': 'Category'
            }
        }

        v4 format is a list of prioritized rule objects.
        This conversion preserves all data while adding structure.

        Args:
            v3_rules: Rules dict in v3 format.

        Returns:
            Normalized rules dict in v4 format.
        """
        v4_rules = []
        priority = 1000  # Start high, decrease for lower priority

        # Convert v3 business rules
        if 'business_keywords' in v3_rules:
            for keyword in v3_rules.get('business_keywords', []):
                v4_rules.append({
                    'id': f'v3-business-{keyword.lower().replace(" ", "-")}',
                    'keywords': [keyword.upper()],
                    'purchase_type': 'Business',
                    'category': 'Business',
                    'subcategory': '',
                    'online': False,
                    'priority': priority,
                    'notes': 'Converted from v3 business_keywords'
                })
                priority -= 1

        # Convert v3 transaction rules
        if 'transaction_rules' in v3_rules:
            for rule_id, rule_data in v3_rules.get('transaction_rules', {}).items():
                if len(rule_data) >= 3:
                    category, subcategory, keywords = (
                        rule_data[0],
                        rule_data[1],
                        rule_data[2]
                    )
                    # Normalize keywords to uppercase for case-insensitive matching
                    normalized_keywords = []
                    if isinstance(keywords, list):
                        normalized_keywords = [kw.upper() for kw in keywords]
                    else:
                        normalized_keywords = [keywords.upper()]

                    v4_rules.append({
                        'id': f'v3-{rule_id}',
                        'keywords': normalized_keywords,
                        'purchase_type': 'Personal',
                        'category': category,
                        'subcategory': subcategory,
                        'online': False,
                        'priority': priority,
                        'notes': f'Converted from v3 rule {rule_id}'
                    })
                    priority -= 1

        # Convert v3 online purchase keywords if present
        if 'online_purchase_keywords' in v3_rules:
            for keyword in v3_rules.get('online_purchase_keywords', []):
                # Normalize keyword to uppercase for matching
                normalized_keyword = keyword.upper()
                # Find existing rules with this keyword and mark as online
                for rule in v4_rules:
                    if normalized_keyword in rule.get('keywords', []):
                        rule['online'] = True

        return {
            'version': '4.0',
            'rules': v4_rules,
            'fallback_categories': v3_rules.get('fallback_categories', {})
        }
