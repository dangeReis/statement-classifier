#!/usr/bin/env python3
"""
Validation tool for transaction classification rules.

Checks for:
- Schema compliance
- Duplicate keywords
- Case sensitivity issues
- Rule conflicts
- Missing required fields
"""

import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set, Tuple

try:
    import jsonschema
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False
    print("Warning: jsonschema not installed. Install with: pip install jsonschema")


class RuleValidator:
    """Validates classification rules for duplicates, conflicts, and schema compliance."""

    def __init__(self, rules_file: Path, schema_file: Path = None):
        self.rules_file = rules_file
        self.schema_file = schema_file
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.rules_data = None

    def load_rules(self) -> bool:
        """Load the rules file."""
        try:
            with open(self.rules_file, 'r') as f:
                self.rules_data = json.load(f)
            return True
        except json.JSONDecodeError as e:
            self.errors.append(f"JSON parsing error: {e}")
            return False
        except FileNotFoundError:
            self.errors.append(f"Rules file not found: {self.rules_file}")
            return False

    def validate_schema(self) -> bool:
        """Validate rules against JSON schema if available."""
        if not HAS_JSONSCHEMA:
            self.warnings.append("Skipping schema validation (jsonschema not installed)")
            return True

        if not self.schema_file or not self.schema_file.exists():
            self.warnings.append("Schema file not found, skipping schema validation")
            return True

        try:
            with open(self.schema_file, 'r') as f:
                schema = json.load(f)

            jsonschema.validate(self.rules_data, schema)
            print("✅ Schema validation passed")
            return True
        except jsonschema.ValidationError as e:
            self.errors.append(f"Schema validation error: {e.message}")
            return False
        except json.JSONDecodeError as e:
            self.errors.append(f"Schema file parsing error: {e}")
            return False

    def detect_format(self) -> str:
        """Detect whether this is v3 (array) or v4 (object) format."""
        if isinstance(self.rules_data, dict):
            if 'version' in self.rules_data:
                return f"v{self.rules_data['version']}"
            elif 'transaction_rules' in self.rules_data:
                return "v3"
            elif 'rules' in self.rules_data and isinstance(self.rules_data.get('rules', [])[0], dict):
                return "v4"
        return "unknown"

    def check_v3_duplicates(self) -> bool:
        """Check for duplicate keywords in v3 format."""
        keyword_map: Dict[str, List[int]] = defaultdict(list)
        transaction_rules = self.rules_data.get('transaction_rules', [])

        for idx, rule in enumerate(transaction_rules):
            if len(rule) < 3:
                self.errors.append(f"Rule {idx}: Invalid format (expected [cat, subcat, keywords])")
                continue

            category, subcategory, keywords = rule[0], rule[1], rule[2]

            for kw in keywords:
                keyword_map[kw.upper()].append(idx)

                # Check if keyword is uppercase
                if kw != kw.upper():
                    self.warnings.append(
                        f"Rule {idx} ({category}/{subcategory}): "
                        f"Keyword '{kw}' is not uppercase (should be '{kw.upper()}')"
                    )

        # Find duplicates
        has_duplicates = False
        for keyword, rule_indices in keyword_map.items():
            if len(rule_indices) > 1:
                has_duplicates = True
                rules_info = []
                for idx in rule_indices:
                    rule = transaction_rules[idx]
                    rules_info.append(f"  - Rule {idx}: {rule[0]} / {rule[1]}")

                self.errors.append(
                    f"Duplicate keyword '{keyword}' found in multiple rules:\n" +
                    "\n".join(rules_info)
                )

        if not has_duplicates:
            print(f"✅ No duplicate keywords found ({len(keyword_map)} unique keywords)")

        # Check business keywords
        business_keywords = self.rules_data.get('business_keywords', [])
        for idx, kw in enumerate(business_keywords):
            if kw != kw.upper():
                self.warnings.append(
                    f"business_keywords[{idx}]: '{kw}' is not uppercase (should be '{kw.upper()}')"
                )

        return not has_duplicates

    def check_v4_duplicates(self) -> bool:
        """Check for duplicate keywords in v4 format."""
        keyword_map: Dict[str, List[str]] = defaultdict(list)
        id_set: Set[str] = set()
        rules = self.rules_data.get('rules', [])

        for rule in rules:
            rule_id = rule.get('id', 'unknown')

            # Check for duplicate IDs
            if rule_id in id_set:
                self.errors.append(f"Duplicate rule ID: {rule_id}")
            id_set.add(rule_id)

            # Check keywords
            keywords = rule.get('keywords', [])
            for kw in keywords:
                keyword_map[kw.upper()].append(rule_id)

                # Check if keyword is uppercase
                if kw != kw.upper():
                    self.warnings.append(
                        f"Rule '{rule_id}': Keyword '{kw}' is not uppercase (should be '{kw.upper()}')"
                    )

        # Find duplicates
        has_duplicates = False
        for keyword, rule_ids in keyword_map.items():
            if len(rule_ids) > 1:
                has_duplicates = True
                self.errors.append(
                    f"Duplicate keyword '{keyword}' found in rules: {', '.join(rule_ids)}"
                )

        if not has_duplicates:
            print(f"✅ No duplicate keywords found ({len(keyword_map)} unique keywords)")

        return not has_duplicates

    def check_v3_conflicts(self) -> bool:
        """Check for rule conflicts in v3 format."""
        transaction_rules = self.rules_data.get('transaction_rules', [])

        # Look for rules that might conflict (same category/subcat with overlapping keywords)
        category_map: Dict[Tuple[str, str], List[int]] = defaultdict(list)

        for idx, rule in enumerate(transaction_rules):
            if len(rule) < 3:
                continue
            category, subcategory = rule[0], rule[1]
            category_map[(category, subcategory)].append(idx)

        # Check for rules with generic categories
        generic_categories = ['Business', 'Personal', 'Financial', 'Auto']
        for idx, rule in enumerate(transaction_rules):
            if len(rule) < 3:
                continue
            category = rule[0]
            if category in generic_categories:
                self.warnings.append(
                    f"Rule {idx}: Using generic category '{category}' as primary category. "
                    f"Consider using more specific category."
                )

        return True

    def check_v4_conflicts(self) -> bool:
        """Check for rule conflicts in v4 format."""
        rules = self.rules_data.get('rules', [])

        # Check for rules with same category but different purchase types
        category_purchase_map: Dict[str, Set[str]] = defaultdict(set)

        for rule in rules:
            category = rule.get('category', '')
            purchase_type = rule.get('purchase_type', '')
            category_purchase_map[category].add(purchase_type)

        for category, purchase_types in category_purchase_map.items():
            if len(purchase_types) > 1:
                self.warnings.append(
                    f"Category '{category}' used with multiple purchase types: {purchase_types}. "
                    "This may be intentional but could indicate inconsistency."
                )

        return True

    def validate(self) -> bool:
        """Run all validation checks."""
        print(f"Validating rules file: {self.rules_file}")
        print("=" * 80)

        if not self.load_rules():
            return False

        format_type = self.detect_format()
        print(f"Detected format: {format_type}")
        print()

        # Validate schema if available
        self.validate_schema()
        print()

        # Run format-specific checks
        if format_type == "v3":
            self.check_v3_duplicates()
            self.check_v3_conflicts()
        elif format_type in ["v4", "v4.0"]:
            self.check_v4_duplicates()
            self.check_v4_conflicts()
        else:
            self.errors.append(f"Unknown format: {format_type}")

        # Print summary
        print()
        print("=" * 80)
        print("VALIDATION SUMMARY")
        print("=" * 80)

        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"  • {error}")

        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  • {warning}")

        if not self.errors and not self.warnings:
            print("\n✅ All validation checks passed!")

        return len(self.errors) == 0


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Validate transaction classification rules')
    parser.add_argument('rules_file', type=Path, help='Path to rules JSON file')
    parser.add_argument('--schema', type=Path, help='Path to JSON schema file')

    args = parser.parse_args()

    schema_file = args.schema
    if not schema_file:
        # Try to find schema in same directory
        default_schema = args.rules_file.parent / 'rules_schema.json'
        if default_schema.exists():
            schema_file = default_schema

    validator = RuleValidator(args.rules_file, schema_file)
    success = validator.validate()

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
