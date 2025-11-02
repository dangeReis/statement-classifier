#!/usr/bin/env python3
"""
Management CLI for transaction classification rules.

Commands:
  test        - Test classification for a description
  validate    - Validate rules file
  duplicates  - Find duplicate keywords
  stats       - Show statistics about rules
  add         - Add a new rule (interactive)
"""

import json
import sys
from pathlib import Path
from typing import Optional

try:
    from .classifier import classify_transaction
    from .validate_rules import RuleValidator
except ImportError:
    sys.path.append(str(Path(__file__).resolve().parent))
    from classifier import classify_transaction
    from validate_rules import RuleValidator


def cmd_test(description: str, category: str = ""):
    """Test classification for a transaction description."""
    print(f"Testing classification for: {description}")
    print(f"Merchant category: {category or '(none)'}")
    print()

    purchase_type, trans_cat, trans_subcat, online = classify_transaction(description, category)

    print("Classification Results:")
    print(f"  Purchase Type:    {purchase_type}")
    print(f"  Category:         {trans_cat}")
    print(f"  Subcategory:      {trans_subcat}")
    print(f"  Online Purchase:  {online}")


def cmd_validate(rules_file: Path):
    """Validate rules file."""
    schema_file = rules_file.parent / 'rules_schema.json'
    validator = RuleValidator(rules_file, schema_file if schema_file.exists() else None)
    success = validator.validate()
    return 0 if success else 1


def cmd_duplicates(rules_file: Path):
    """Find duplicate keywords in rules."""
    try:
        with open(rules_file, 'r') as f:
            data = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error loading rules: {e}")
        return 1

    format_version = data.get('version', 'unknown')
    print(f"Checking for duplicates in {format_version} format...")
    print()

    if 'rules' in data and isinstance(data['rules'], list) and isinstance(data['rules'][0], dict):
        # v4 format
        keyword_map = {}
        for rule in data['rules']:
            rule_id = rule.get('id', 'unknown')
            for kw in rule.get('keywords', []):
                kw_upper = kw.upper()
                if kw_upper in keyword_map:
                    print(f"❌ Duplicate: '{kw}' in rules '{keyword_map[kw_upper]}' and '{rule_id}'")
                else:
                    keyword_map[kw_upper] = rule_id

        if len(keyword_map) == sum(len(r.get('keywords', [])) for r in data['rules']):
            print("✅ No duplicates found!")
    else:
        print("⚠️  v3 format not supported in this command. Use validate_rules.py instead.")
        return 1

    return 0


def cmd_stats(rules_file: Path):
    """Show statistics about rules."""
    try:
        with open(rules_file, 'r') as f:
            data = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error loading rules: {e}")
        return 1

    if 'rules' in data and isinstance(data['rules'], list):
        rules = data['rules']
        print(f"Rules Statistics")
        print("=" * 60)
        print(f"Total rules:           {len(rules)}")
        print(f"Total keywords:        {sum(len(r.get('keywords', [])) for r in rules)}")
        print()

        # Count by purchase type
        business = sum(1 for r in rules if r.get('purchase_type') == 'Business')
        personal = sum(1 for r in rules if r.get('purchase_type') == 'Personal')
        print(f"Business rules:        {business} ({business/len(rules)*100:.1f}%)")
        print(f"Personal rules:        {personal} ({personal/len(rules)*100:.1f}%)")
        print()

        # Count by category
        from collections import Counter
        categories = Counter(r.get('category', 'Unknown') for r in rules)
        print(f"Categories ({len(categories)}):")
        for cat, count in categories.most_common(10):
            print(f"  {cat:30s} {count:3d} rules")
        if len(categories) > 10:
            print(f"  ... and {len(categories) - 10} more")

        # Online vs offline
        online = sum(1 for r in rules if r.get('online', False))
        print()
        print(f"Online purchases:      {online} ({online/len(rules)*100:.1f}%)")
    else:
        print("⚠️  v3 format not supported. Migrate to v4 first.")
        return 1

    return 0


def cmd_add(rules_file: Path):
    """Add a new rule interactively."""
    print("Add New Rule")
    print("=" * 60)

    try:
        with open(rules_file, 'r') as f:
            data = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error loading rules: {e}")
        return 1

    if 'rules' not in data or not isinstance(data['rules'], list):
        print("⚠️  v3 format not supported. Migrate to v4 first.")
        return 1

    # Interactive prompts
    rule_id = input("Rule ID (lowercase-with-hyphens): ").strip()
    keywords_str = input("Keywords (comma-separated): ").strip()
    purchase_type = input("Purchase Type (Business/Personal) [Personal]: ").strip() or "Personal"
    category = input("Category: ").strip()
    subcategory = input("Subcategory (optional): ").strip()
    online_str = input("Online purchase? (y/n) [n]: ").strip().lower()
    priority_str = input("Priority (1-1000) [50]: ").strip() or "50"

    # Create rule
    new_rule = {
        'id': rule_id,
        'keywords': [kw.strip().upper() for kw in keywords_str.split(',')],
        'purchase_type': purchase_type,
        'category': category,
        'subcategory': subcategory,
        'online': online_str == 'y',
        'priority': int(priority_str)
    }

    print()
    print("New rule:")
    print(json.dumps(new_rule, indent=2))
    print()

    confirm = input("Add this rule? (y/n): ").strip().lower()
    if confirm == 'y':
        data['rules'].append(new_rule)
        # Sort by priority
        data['rules'].sort(key=lambda r: r.get('priority', 50), reverse=True)

        with open(rules_file, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"✅ Rule added to {rules_file}")
        return 0
    else:
        print("❌ Cancelled")
        return 1


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Manage transaction classification rules')
    parser.add_argument('--rules', type=Path,
                       default=Path(__file__).parent / 'classification_rules.v4.json',
                       help='Path to rules file')

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Test command
    test_parser = subparsers.add_parser('test', help='Test classification')
    test_parser.add_argument('description', help='Transaction description')
    test_parser.add_argument('--category', default='', help='Merchant category')

    # Validate command
    subparsers.add_parser('validate', help='Validate rules file')

    # Duplicates command
    subparsers.add_parser('duplicates', help='Find duplicate keywords')

    # Stats command
    subparsers.add_parser('stats', help='Show statistics')

    # Add command
    subparsers.add_parser('add', help='Add a new rule interactively')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    if args.command == 'test':
        cmd_test(args.description, args.category)
        return 0
    elif args.command == 'validate':
        return cmd_validate(args.rules)
    elif args.command == 'duplicates':
        return cmd_duplicates(args.rules)
    elif args.command == 'stats':
        return cmd_stats(args.rules)
    elif args.command == 'add':
        return cmd_add(args.rules)

    return 0


if __name__ == '__main__':
    sys.exit(main())
