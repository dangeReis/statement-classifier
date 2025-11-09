#!/usr/bin/env python3
"""Generate sample export files from test data.

This script reads the sample transaction data, classifies each transaction,
and generates sample export files in various formats (CSV, JSON, Excel-ready).
"""

import json
import csv
from pathlib import Path
from datetime import datetime, timedelta
import random


def load_test_data():
    """Load sample transaction data."""
    json_path = Path(__file__).parent / 'sample_transactions.json'
    with open(json_path, 'r') as f:
        return json.load(f)


def generate_transaction_dates(count, start_date=None):
    """Generate realistic transaction dates."""
    if start_date is None:
        start_date = datetime.now() - timedelta(days=90)

    dates = []
    current_date = start_date

    for _ in range(count):
        # Random 1-5 days between transactions
        current_date += timedelta(days=random.randint(1, 5))
        dates.append(current_date)

    return dates


def generate_transaction_amounts():
    """Generate realistic transaction amounts."""
    # Common amount patterns
    patterns = [
        (5, 25),      # Small purchases
        (25, 100),    # Medium purchases
        (100, 500),   # Large purchases
        (500, 2000),  # Very large purchases
    ]

    # Weighted selection
    weights = [50, 30, 15, 5]

    amounts = []
    for _ in range(68):  # Total test cases
        pattern = random.choices(patterns, weights=weights)[0]
        amount = round(random.uniform(*pattern), 2)
        amounts.append(amount)

    return amounts


def flatten_test_data(test_data):
    """Flatten test suite data into single list."""
    flattened = []

    for suite_name, test_cases in test_data['test_suites'].items():
        for test_case in test_cases:
            flattened.append({
                'description': test_case['description'],
                'category': test_case['category'],
                'expected': test_case['expected'],
                'notes': test_case.get('notes', ''),
                'test_suite': suite_name
            })

    return flattened


def generate_csv_export(test_cases, output_path):
    """Generate CSV export sample."""
    dates = generate_transaction_dates(len(test_cases))
    amounts = generate_transaction_amounts()

    with open(output_path, 'w', newline='') as f:
        fieldnames = [
            'transaction_date',
            'post_date',
            'description',
            'category',
            'amount',
            'purchase_type',
            'classified_category',
            'classified_subcategory',
            'online',
            'test_suite'
        ]

        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for i, test_case in enumerate(test_cases):
            transaction_date = dates[i]
            post_date = transaction_date + timedelta(days=random.randint(1, 3))
            amount = amounts[i]

            # Negative for expenses, positive for income
            if 'income' in test_case['test_suite'].lower():
                amount = abs(amount)
            else:
                amount = -abs(amount)

            writer.writerow({
                'transaction_date': transaction_date.strftime('%Y-%m-%d'),
                'post_date': post_date.strftime('%Y-%m-%d'),
                'description': test_case['description'],
                'category': test_case['category'],
                'amount': f"{amount:.2f}",
                'purchase_type': test_case['expected']['purchase_type'],
                'classified_category': test_case['expected']['category'],
                'classified_subcategory': test_case['expected']['subcategory'],
                'online': str(test_case['expected']['online']).lower(),
                'test_suite': test_case['test_suite']
            })

    print(f"✓ Generated CSV export: {output_path}")


def generate_json_export(test_cases, output_path):
    """Generate JSON export sample."""
    dates = generate_transaction_dates(len(test_cases))
    amounts = generate_transaction_amounts()

    transactions = []

    for i, test_case in enumerate(test_cases):
        transaction_date = dates[i]
        post_date = transaction_date + timedelta(days=random.randint(1, 3))
        amount = amounts[i]

        # Negative for expenses, positive for income
        if 'income' in test_case['test_suite'].lower():
            amount = abs(amount)
        else:
            amount = -abs(amount)

        transactions.append({
            'transaction_id': f"TXN-{i+1:04d}",
            'transaction_date': transaction_date.isoformat(),
            'post_date': post_date.isoformat(),
            'description': test_case['description'],
            'merchant_category': test_case['category'],
            'amount': round(amount, 2),
            'classification': {
                'purchase_type': test_case['expected']['purchase_type'],
                'category': test_case['expected']['category'],
                'subcategory': test_case['expected']['subcategory'],
                'online': test_case['expected']['online']
            },
            'metadata': {
                'test_suite': test_case['test_suite'],
                'notes': test_case['notes']
            }
        })

    export_data = {
        'export_date': datetime.now().isoformat(),
        'total_transactions': len(transactions),
        'date_range': {
            'start': dates[0].isoformat(),
            'end': dates[-1].isoformat()
        },
        'summary': {
            'total_business': sum(1 for t in transactions if t['classification']['purchase_type'] == 'Business'),
            'total_personal': sum(1 for t in transactions if t['classification']['purchase_type'] == 'Personal'),
            'total_income': sum(t['amount'] for t in transactions if t['amount'] > 0),
            'total_expenses': sum(abs(t['amount']) for t in transactions if t['amount'] < 0),
        },
        'transactions': transactions
    }

    with open(output_path, 'w') as f:
        json.dump(export_data, f, indent=2)

    print(f"✓ Generated JSON export: {output_path}")


def generate_tax_report(test_cases, output_path):
    """Generate tax-ready export sample."""
    dates = generate_transaction_dates(len(test_cases))
    amounts = generate_transaction_amounts()

    business_transactions = []
    personal_transactions = []

    for i, test_case in enumerate(test_cases):
        transaction_date = dates[i]
        amount = amounts[i]

        # Negative for expenses, positive for income
        if 'income' in test_case['test_suite'].lower():
            amount = abs(amount)
        else:
            amount = -abs(amount)

        transaction = {
            'date': transaction_date.strftime('%Y-%m-%d'),
            'description': test_case['description'],
            'category': test_case['expected']['category'],
            'subcategory': test_case['expected']['subcategory'],
            'amount': round(amount, 2),
            'online': test_case['expected']['online']
        }

        if test_case['expected']['purchase_type'] == 'Business':
            business_transactions.append(transaction)
        else:
            personal_transactions.append(transaction)

    # Group by category
    business_by_category = {}
    for txn in business_transactions:
        cat = txn['category'] or 'Uncategorized'
        if cat not in business_by_category:
            business_by_category[cat] = []
        business_by_category[cat].append(txn)

    personal_by_category = {}
    for txn in personal_transactions:
        cat = txn['category'] or 'Uncategorized'
        if cat not in personal_by_category:
            personal_by_category[cat] = []
        personal_by_category[cat].append(txn)

    with open(output_path, 'w', newline='') as f:
        writer = csv.writer(f)

        # Business section
        writer.writerow(['BUSINESS TRANSACTIONS'])
        writer.writerow([])

        for category in sorted(business_by_category.keys()):
            writer.writerow([f"Category: {category}"])
            writer.writerow(['Date', 'Description', 'Subcategory', 'Amount', 'Online'])

            txns = business_by_category[category]
            for txn in txns:
                writer.writerow([
                    txn['date'],
                    txn['description'],
                    txn['subcategory'],
                    f"${txn['amount']:.2f}",
                    'Yes' if txn['online'] else 'No'
                ])

            total = sum(txn['amount'] for txn in txns)
            writer.writerow(['', '', 'TOTAL', f"${total:.2f}", ''])
            writer.writerow([])

        business_total = sum(txn['amount'] for txn in business_transactions)
        writer.writerow(['BUSINESS TOTAL', '', '', f"${business_total:.2f}", ''])
        writer.writerow([])
        writer.writerow([])

        # Personal section
        writer.writerow(['PERSONAL TRANSACTIONS'])
        writer.writerow([])

        for category in sorted(personal_by_category.keys()):
            writer.writerow([f"Category: {category}"])
            writer.writerow(['Date', 'Description', 'Subcategory', 'Amount', 'Online'])

            txns = personal_by_category[category]
            for txn in txns:
                writer.writerow([
                    txn['date'],
                    txn['description'],
                    txn['subcategory'],
                    f"${txn['amount']:.2f}",
                    'Yes' if txn['online'] else 'No'
                ])

            total = sum(txn['amount'] for txn in txns)
            writer.writerow(['', '', 'TOTAL', f"${total:.2f}", ''])
            writer.writerow([])

        personal_total = sum(txn['amount'] for txn in personal_transactions)
        writer.writerow(['PERSONAL TOTAL', '', '', f"${personal_total:.2f}", ''])

    print(f"✓ Generated tax report: {output_path}")


def main():
    """Generate all export samples."""
    print("Generating sample export files...")
    print()

    # Load test data
    test_data = load_test_data()
    test_cases = flatten_test_data(test_data)

    print(f"Loaded {len(test_cases)} test transactions")
    print()

    # Output directory
    output_dir = Path(__file__).parent / 'sample_exports'
    output_dir.mkdir(exist_ok=True)

    # Generate exports
    generate_csv_export(
        test_cases,
        output_dir / 'classified_transactions.csv'
    )

    generate_json_export(
        test_cases,
        output_dir / 'classified_transactions.json'
    )

    generate_tax_report(
        test_cases,
        output_dir / 'tax_report.csv'
    )

    print()
    print("✓ All exports generated successfully!")
    print(f"  Output directory: {output_dir}")
    print()
    print("Generated files:")
    print("  - classified_transactions.csv (full transaction export)")
    print("  - classified_transactions.json (JSON format export)")
    print("  - tax_report.csv (tax-ready summary report)")


if __name__ == '__main__':
    main()
