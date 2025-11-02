"""Rule tester - test classification against rules."""

from pathlib import Path
from typing import Any, Dict, List, Optional

from statement_classifier.engine import ClassificationEngine
from statement_classifier.providers.file import FileRuleProvider


class RuleTestRunner:
    """Test classification against rules."""

    def __init__(self, rules_path: Path):
        """Initialize with rules file path.

        Args:
            rules_path: Path to rules.json file.
        """
        self.rules_path = Path(rules_path)
        self.provider = FileRuleProvider(v4_path=self.rules_path)
        self.engine = ClassificationEngine(self.provider)

    def test_classification(
        self,
        description: str,
        category: str
    ) -> Dict[str, Any]:
        """Test single classification.

        Args:
            description: Transaction description.
            category: Merchant category code.

        Returns:
            Dict with result and matching rule info.
        """
        result = self.engine.classify(description, category)

        # Find which rule matched (if any)
        rules_data = self.provider.load_rules()
        rules = rules_data.get('rules', [])
        matching_rule: Optional[str] = None

        desc_upper = description.upper()
        for rule in sorted(
            rules,
            key=lambda r: r.get('priority', 0),
            reverse=True
        ):
            for kw in rule.get('keywords', []):
                if kw in desc_upper:
                    matching_rule = rule['id']
                    break
            if matching_rule:
                break

        return {
            'description': description,
            'category': category,
            'result': result,
            'matching_rule': matching_rule
        }

    def batch_test(self, test_cases: List[Dict]) -> List[Dict[str, Any]]:
        """Test multiple classifications.

        Args:
            test_cases: List of dicts with description and category.

        Returns:
            List of test results.
        """
        results = []
        for test in test_cases:
            results.append(
                self.test_classification(
                    test.get('description', ''),
                    test.get('category', '')
                )
            )
        return results
