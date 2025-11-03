"""Unified CLI entry point for Statement Classifier.

Main command-line interface providing access to all classification and rule management tools.

Usage:
    statement-classifier [--rules PATH] [--verbose] <command> [args]

Commands:
    classify            Classify a transaction
    rules               Manage rules (add, remove, update, get)
    validate            Validate rules file
    analyze             Analyze rules (stats, duplicates, coverage)
    test                Test classifications from CSV file
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

from statement_classifier.logging import Logger
from statement_classifier.providers.file import FileRuleProvider
from statement_classifier.engine import ClassificationEngine
from statement_classifier.types import RuleProviderException

from .rule_manager import RuleManager
from .rule_validator import RuleValidator
from .rule_analyzer import RuleAnalyzer
from .rule_tester import RuleTestRunner


# Default rules path
DEFAULT_RULES_PATH = Path(__file__).parents[2] / "bin" / "classification_rules.v4.json"


class CLI:
    """Main CLI coordinator."""

    def __init__(self, rules_path: Optional[Path] = None, verbose: bool = False):
        """Initialize CLI.

        Args:
            rules_path: Path to rules.json file. Defaults to DEFAULT_RULES_PATH.
            verbose: Enable verbose output and logging.
        """
        self.rules_path = Path(rules_path or DEFAULT_RULES_PATH)
        self.verbose = verbose
        self.logger = Logger(enabled=verbose)

        # Verify rules file exists
        if not self.rules_path.exists():
            raise FileNotFoundError(f"Rules file not found: {self.rules_path}")

        # Initialize shared components
        self.provider = FileRuleProvider(v4_path=self.rules_path)
        self.engine = ClassificationEngine(self.provider)

        # Initialize tools
        self.manager = RuleManager(self.rules_path)
        self.validator = RuleValidator(self.rules_path)
        self.analyzer = RuleAnalyzer(self.rules_path)
        self.tester = RuleTestRunner(self.rules_path)

    def classify(self, description: str, category: str) -> int:
        """Classify a transaction.

        Args:
            description: Transaction description.
            category: Merchant category code.

        Returns:
            Exit code (0 for success).
        """
        try:
            result = self.tester.test_classification(description, category)
            purchase_type = result.get('purchase_type', 'Unknown')
            cat = result.get('category', 'Unknown')
            subcat = result.get('subcategory', '')
            online = result.get('online', False)
            matching_rule = result.get('matching_rule', 'None')

            print(f"Classification Result:")
            print(f"  Purchase Type: {purchase_type}")
            print(f"  Category: {cat}")
            if subcat:
                print(f"  Subcategory: {subcat}")
            print(f"  Online: {online}")
            print(f"  Matching Rule: {matching_rule}")
            return 0
        except Exception as e:
            print(f"Error classifying transaction: {e}", file=sys.stderr)
            return 1

    def rules_add(self, rule_id: str, keywords: str, purchase_type: str,
                  category: str, subcategory: str = "", online: bool = False) -> int:
        """Add a new rule.

        Args:
            rule_id: Rule ID.
            keywords: Comma-separated keywords.
            purchase_type: Business or Personal.
            category: Category name.
            subcategory: Subcategory (optional).
            online: Whether rule is for online purchases.

        Returns:
            Exit code.
        """
        try:
            rule = {
                'id': rule_id,
                'keywords': [kw.strip().upper() for kw in keywords.split(',')],
                'purchase_type': purchase_type,
                'category': category,
                'subcategory': subcategory,
                'online': online,
                'priority': 1000,
            }
            self.manager.add_rule(rule)
            print(f"✅ Added rule {rule_id}")
            return 0
        except Exception as e:
            print(f"Error adding rule: {e}", file=sys.stderr)
            return 1

    def rules_remove(self, rule_id: str) -> int:
        """Remove a rule.

        Args:
            rule_id: Rule ID to remove.

        Returns:
            Exit code.
        """
        try:
            self.manager.remove_rule(rule_id)
            print(f"✅ Removed rule {rule_id}")
            return 0
        except Exception as e:
            print(f"Error removing rule: {e}", file=sys.stderr)
            return 1

    def rules_get(self, rule_id: str) -> int:
        """Get a rule by ID.

        Args:
            rule_id: Rule ID.

        Returns:
            Exit code.
        """
        try:
            rule = self.manager.get_rule(rule_id)
            if rule:
                import json
                print(json.dumps(rule, indent=2))
                return 0
            else:
                print(f"Rule {rule_id} not found", file=sys.stderr)
                return 1
        except Exception as e:
            print(f"Error getting rule: {e}", file=sys.stderr)
            return 1

    def validate(self) -> int:
        """Validate rules file.

        Returns:
            Exit code (0 if valid).
        """
        try:
            report = self.validator.get_report()
            print(report)
            result = self.validator.validate()
            return 0 if result['is_valid'] else 1
        except Exception as e:
            print(f"Error validating rules: {e}", file=sys.stderr)
            return 1

    def analyze_stats(self) -> int:
        """Show rule statistics.

        Returns:
            Exit code.
        """
        try:
            stats = self.analyzer.get_stats()
            print(f"Rule Statistics:")
            print(f"  Total Rules: {stats.get('total_rules', 0)}")
            print(f"  Total Keywords: {stats.get('total_keywords', 0)}")
            print(f"  Business Rules: {stats.get('business_rules', 0)}")
            print(f"  Personal Rules: {stats.get('personal_rules', 0)}")
            print(f"  Online Rules: {stats.get('online_rules', 0)}")
            categories = stats.get('categories', {})
            if categories:
                print(f"  Categories: {', '.join(categories.keys())}")
            return 0
        except Exception as e:
            print(f"Error getting stats: {e}", file=sys.stderr)
            return 1

    def analyze_duplicates(self) -> int:
        """Find duplicate keywords.

        Returns:
            Exit code.
        """
        try:
            duplicates = self.analyzer.find_duplicates()
            if duplicates:
                print(f"Found {len(duplicates)} duplicate keyword groups:")
                for dup_group in duplicates:
                    keyword = dup_group.get('keyword', 'Unknown')
                    rule_ids = dup_group.get('rule_ids', [])
                    print(f"  {keyword}: {', '.join(rule_ids)}")
                return 1
            else:
                print("✅ No duplicate keywords found")
                return 0
        except Exception as e:
            print(f"Error finding duplicates: {e}", file=sys.stderr)
            return 1

    def analyze_coverage(self) -> int:
        """Show coverage analysis.

        Returns:
            Exit code.
        """
        try:
            coverage = self.analyzer.coverage_analysis()
            print(f"Coverage Analysis:")
            print(f"  Categories Covered: {coverage.get('categories_covered', 0)}")
            print(f"  Total Keywords: {coverage.get('total_keywords', 0)}")
            missing = coverage.get('missing_categories', [])
            if missing:
                print(f"  Missing Categories: {', '.join(missing)}")
            return 0
        except Exception as e:
            print(f"Error getting coverage: {e}", file=sys.stderr)
            return 1

    def test_batch(self, csv_path: str) -> int:
        """Test classifications from CSV file.

        Args:
            csv_path: Path to CSV file.

        Returns:
            Exit code.
        """
        try:
            results = self.tester.batch_test(Path(csv_path))
            for result in results:
                print(f"{result.get('description', '')}: "
                      f"{result.get('category', '')} -> "
                      f"{result.get('purchase_type', '')}")
            print(f"✅ Tested {len(results)} transactions")
            return 0
        except Exception as e:
            print(f"Error testing batch: {e}", file=sys.stderr)
            return 1


def main():
    """Main CLI entry point."""
    # Parse arguments
    parser = argparse.ArgumentParser(
        description="Statement Classifier - Classify financial transactions",
        prog="statement-classifier"
    )

    # Global options
    parser.add_argument(
        "--rules",
        type=Path,
        default=None,
        help=f"Path to rules.json file (default: {DEFAULT_RULES_PATH})"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output and logging"
    )

    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Classify command
    classify_parser = subparsers.add_parser(
        "classify",
        help="Classify a transaction"
    )
    classify_parser.add_argument("description", help="Transaction description")
    classify_parser.add_argument("category", help="Merchant category code")

    # Rules command
    rules_parser = subparsers.add_parser("rules", help="Manage rules")
    rules_sub = rules_parser.add_subparsers(dest="rules_command", required=True)

    # Rules add
    add_parser = rules_sub.add_parser("add", help="Add a new rule")
    add_parser.add_argument("--id", required=True, help="Rule ID")
    add_parser.add_argument("--keywords", required=True, help="Comma-separated keywords")
    add_parser.add_argument("--type", required=True, choices=["Business", "Personal"],
                            help="Purchase type")
    add_parser.add_argument("--category", required=True, help="Category name")
    add_parser.add_argument("--subcategory", default="", help="Subcategory (optional)")
    add_parser.add_argument("--online", action="store_true", help="Mark as online")

    # Rules remove
    remove_parser = rules_sub.add_parser("remove", help="Remove a rule")
    remove_parser.add_argument("rule_id", help="Rule ID to remove")

    # Rules get
    get_parser = rules_sub.add_parser("get", help="Get a rule by ID")
    get_parser.add_argument("rule_id", help="Rule ID")

    # Validate command
    validate_parser = subparsers.add_parser("validate", help="Validate rules file")

    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze rules")
    analyze_sub = analyze_parser.add_subparsers(dest="analyze_command", required=True)
    analyze_sub.add_parser("stats", help="Show statistics")
    analyze_sub.add_parser("duplicates", help="Find duplicate keywords")
    analyze_sub.add_parser("coverage", help="Show coverage analysis")

    # Test command
    test_parser = subparsers.add_parser("test", help="Test classifications")
    test_parser.add_argument("csv_file", help="CSV file with transactions")

    args = parser.parse_args()

    # Show help if no command
    if not args.command:
        parser.print_help()
        return 1

    try:
        # Initialize CLI
        cli = CLI(rules_path=args.rules, verbose=args.verbose)

        # Route to appropriate command
        if args.command == "classify":
            return cli.classify(args.description, args.category)

        elif args.command == "rules":
            if args.rules_command == "add":
                return cli.rules_add(
                    args.id,
                    args.keywords,
                    args.type,
                    args.category,
                    args.subcategory,
                    args.online
                )
            elif args.rules_command == "remove":
                return cli.rules_remove(args.rule_id)
            elif args.rules_command == "get":
                return cli.rules_get(args.rule_id)

        elif args.command == "validate":
            return cli.validate()

        elif args.command == "analyze":
            if args.analyze_command == "stats":
                return cli.analyze_stats()
            elif args.analyze_command == "duplicates":
                return cli.analyze_duplicates()
            elif args.analyze_command == "coverage":
                return cli.analyze_coverage()

        elif args.command == "test":
            return cli.test_batch(args.csv_file)

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except RuleProviderException as e:
        print(f"Rule provider error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
