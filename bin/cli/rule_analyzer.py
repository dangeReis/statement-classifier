"""Rule analyzer - statistics and diagnostics."""

from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Set

from statement_classifier.providers.file import FileRuleProvider
from statement_classifier.types import RuleProviderException


class RuleAnalyzer:
    """Analyze rules for statistics and diagnostics."""

    def __init__(self, rules_path: Path):
        """Initialize with rules file path.

        Args:
            rules_path: Path to rules.json file.
        """
        self.rules_path = Path(rules_path)
        self.provider = FileRuleProvider(v4_path=self.rules_path)

    def get_stats(self) -> Dict[str, Any]:
        """Get rule statistics.

        Returns:
            Dict with counts, distribution, etc.
        """
        try:
            rules_data = self.provider.load_rules()
            rules = rules_data.get('rules', [])

            total_keywords = sum(len(r.get('keywords', [])) for r in rules)

            business_count = sum(
                1 for r in rules
                if r.get('purchase_type') == 'Business'
            )
            personal_count = len(rules) - business_count

            online_count = sum(
                1 for r in rules
                if r.get('online', False)
            )

            categories = defaultdict(int)
            for rule in rules:
                cat = rule.get('category', 'Unknown')
                categories[cat] += 1

            return {
                'total_rules': len(rules),
                'total_keywords': total_keywords,
                'business_rules': business_count,
                'personal_rules': personal_count,
                'online_rules': online_count,
                'categories': dict(categories),
                'avg_keywords_per_rule': (
                    total_keywords / len(rules) if rules else 0
                )
            }

        except Exception as e:
            raise RuleProviderException(f"Failed to get stats: {e}")

    def find_duplicates(self) -> Dict[str, List[str]]:
        """Find duplicate keywords across rules.

        Returns:
            Dict mapping keyword to rule IDs that have it.
        """
        try:
            rules_data = self.provider.load_rules()
            rules = rules_data.get('rules', [])

            keyword_rules = defaultdict(list)
            for rule in rules:
                for kw in rule.get('keywords', []):
                    keyword_rules[kw].append(rule['id'])

            # Return only duplicates
            return {
                kw: rule_ids
                for kw, rule_ids in keyword_rules.items()
                if len(rule_ids) > 1
            }

        except Exception as e:
            raise RuleProviderException(f"Failed to find duplicates: {e}")

    def coverage_analysis(self) -> Dict[str, Any]:
        """Analyze rule coverage.

        Returns:
            Dict with coverage metrics.
        """
        try:
            rules_data = self.provider.load_rules()
            rules = rules_data.get('rules', [])
            fallback = rules_data.get('fallback_categories', {})

            all_keywords: Set[str] = set()
            for rule in rules:
                all_keywords.update(rule.get('keywords', []))

            return {
                'total_fallback_categories': len(fallback),
                'unique_keywords': len(all_keywords),
                'rules_with_subcategory': sum(
                    1 for r in rules
                    if r.get('subcategory')
                ),
                'avg_priority': (
                    sum(r.get('priority', 0) for r in rules) / len(rules)
                    if rules else 0
                )
            }

        except Exception as e:
            raise RuleProviderException(f"Failed to analyze coverage: {e}")
