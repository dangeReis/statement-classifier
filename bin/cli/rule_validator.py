"""Rule validator - validate rule files."""

from pathlib import Path
from typing import Tuple

from statement_classifier.providers.file import FileRuleProvider
from statement_classifier.types import RuleProviderException, ValidationResult


class RuleValidator:
    """Validate rule files for errors and warnings."""

    def __init__(self, rules_path: Path):
        """Initialize with rules file path.

        Args:
            rules_path: Path to rules.json file.
        """
        self.rules_path = Path(rules_path)
        self.provider = FileRuleProvider(v4_path=self.rules_path)

    def validate(self) -> ValidationResult:
        """Validate all rules.

        Returns:
            ValidationResult with is_valid, errors, warnings.
        """
        try:
            return self.provider.validate()
        except RuleProviderException as e:
            return {
                'is_valid': False,
                'errors': [str(e)],
                'warnings': []
            }

    def get_report(self) -> str:
        """Get human-readable validation report.

        Returns:
            Formatted validation report string.
        """
        result = self.validate()

        lines = []
        if result['is_valid']:
            lines.append("✅ All rules valid")
        else:
            lines.append("❌ Validation failed")

        if result['errors']:
            lines.append(f"\n❌ Errors ({len(result['errors'])}):")
            for error in result['errors']:
                lines.append(f"  - {error}")

        if result['warnings']:
            lines.append(f"\n⚠️  Warnings ({len(result['warnings'])}):")
            for warning in result['warnings']:
                lines.append(f"  - {warning}")

        return '\n'.join(lines)

    def summary(self) -> Tuple[int, int, bool]:
        """Get validation summary.

        Returns:
            Tuple of (error_count, warning_count, is_valid).
        """
        result = self.validate()
        return (
            len(result['errors']),
            len(result['warnings']),
            result['is_valid']
        )
