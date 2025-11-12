# Quick Reference - Sample Transaction Data

## Test Data Overview

**Total Test Cases**: 68 transactions
**File Formats**: JSON, CSV
**Categories Covered**: 14 major categories
**Test Suites**: 12 specialized test suites

## File Locations

```
tests/fixtures/
├── README.md                          # Full documentation
├── QUICK_REFERENCE.md                 # This file
├── sample_transactions.json           # JSON test data
├── sample_transactions.csv            # CSV test data
├── generate_export_sample.py          # Export generator script
└── sample_exports/                    # Generated exports
    ├── classified_transactions.csv
    ├── classified_transactions.json
    └── tax_report.csv
```

## Quick Start

### 1. Run All Tests
```bash
cd /Users/russ/Projects/statement-classifier
python -m pytest tests/test_sample_data_validation.py -v
```

### 2. Run Specific Test Suite
```bash
# Business transactions only
python -m pytest tests/test_sample_data_validation.py::TestSampleDataValidation::test_business_income_transactions -v

# Edge cases only
python -m pytest tests/test_sample_data_validation.py::TestSampleDataValidation::test_edge_cases -v
```

### 3. Generate Sample Exports
```bash
cd tests/fixtures
python generate_export_sample.py
```

### 4. View Coverage Report
```bash
python -m pytest tests/test_sample_data_validation.py::TestSampleDataValidation::test_coverage_report -v -s
```

## Test Suites Breakdown

| Suite | Cases | Description |
|-------|-------|-------------|
| business_income | 5 | Amazon, eBay, AdSense, domain sales |
| business_expenses | 10 | Purchases, tolls, insurance, utilities |
| business_taxes | 3 | Federal and state tax payments |
| business_fees | 3 | Bank fees, government fees |
| personal_food | 8 | Groceries, restaurants, liquor |
| personal_healthcare | 5 | Medical, dental, pharmacy, vet |
| personal_recreation | 6 | Sports, movies, subscriptions |
| personal_shopping | 4 | Clothing, general merchandise |
| personal_services | 4 | Haircuts, rides, professional |
| personal_financial | 5 | Transfers, payments, investments |
| personal_income | 3 | Payroll, unemployment, refunds |
| edge_cases | 7 | Empty inputs, special chars, normalization |
| priority_testing | 3 | Priority 999-1000 rules |
| online_flag_testing | 4 | Online vs in-store detection |

## Common Test Patterns

### Test a Single Transaction
```python
from statement_classifier import ClassificationEngine, FileRuleProvider

provider = FileRuleProvider(v4_path='bin/classification_rules.v4.json')
engine = ClassificationEngine(provider)

result = engine.classify('AMAZON.COM*12345', 'PURCHASE')
# Expected: Business, General Merchandise, Online Purchases, online=true
```

### Load and Test All CSV Data
```python
import csv
from pathlib import Path

csv_path = Path('tests/fixtures/sample_transactions.csv')
with open(csv_path, 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        result = engine.classify(row['description'], row['category'])
        assert result['purchase_type'] == row['expected_purchase_type']
```

### Load and Test JSON Data
```python
import json
from pathlib import Path

json_path = Path('tests/fixtures/sample_transactions.json')
with open(json_path, 'r') as f:
    data = json.load(f)

for suite_name, test_cases in data['test_suites'].items():
    for test_case in test_cases:
        result = engine.classify(
            test_case['description'],
            test_case['category']
        )
        assert result == test_case['expected']
```

## Expected Results Cheat Sheet

### Business Income
- Amazon Associates → Income / Associate Programs
- Amazon FBA → Business Income / Amazon FBA
- eBay Sales → Business Income / eBay Sales
- AdSense → Business Income / AdSense Revenue
- GoDaddy → Business Income / Domain Reseller Revenue

### Business Expenses
- AMAZON.COM* → General Merchandise / Online Purchases
- E-Z*PASS → Auto & Travel / Tolls
- GEICO → Auto & Travel / Auto Insurance
- LOWES → Home Office / Home Improvement
- STAPLES → Business Inventory / Office Supplies

### Personal Food
- AMAZON FRESH → Food & Dining / Groceries
- SHOPRITE → Grocery / Supermarket
- MCDONALDS → Food & Drink / Restaurant
- SAKE RESTAURANT → Food and Drink Sushi / Sushi Restaurant

### Personal Healthcare
- PHR*ENTANDALLERGY → Health & Wellness / Allergy Care
- STEVE D KIM DDS → Healthcare / Dental Care
- CVS/PHARMACY → Medical / Pharmacy

### Edge Cases
- Empty description → Personal / empty / empty
- Unknown merchant → Personal / empty / empty
- Multiple keywords → Highest priority wins
- Lowercase → Normalized to uppercase
- Whitespace → Trimmed automatically

## Priority Rules to Remember

| Priority | Example | Category |
|----------|---------|----------|
| 1000 | PHR*ENTANDALLERGY | Health & Wellness |
| 1000 | STANDARD ACH PMNTS | Bank Fees |
| 999 | RIVERSIDE NISSAN | Car Maintenance |
| 999 | FROM: AMAZON.COM | Income (Associates) |
| 998 | AMAZON.COM* | General Merchandise |

**Rule**: Higher priority always wins when multiple keywords match

## Online Flag Rules

| Pattern | Online Flag |
|---------|-------------|
| AMAZON.COM* | true |
| WALMART.COM | true |
| EBAY C | true |
| TARGET (store) | false |
| SHOPRITE | false |
| Most .COM | true |
| Most physical stores | false |

## Common Issues & Solutions

### Test Fails: "Category mismatch"
- Check if rule still exists in classification_rules.v4.json
- Verify rule priority hasn't changed
- Check for typos in expected category name

### Test Fails: "Online flag mismatch"
- Verify rule's online field in classification_rules.v4.json
- Online should be true for .com domains
- Online should be false for physical stores

### Test Fails: "Purchase type mismatch"
- Check if transaction should be Business or Personal
- Verify rule's purchase_type field
- Income transactions may be Business or Personal

### All Tests Fail
- Verify rules file path is correct
- Check rules file format (must be v4.0)
- Ensure rules file is valid JSON

## Export Format Examples

### CSV Export Format
```csv
transaction_date,post_date,description,category,amount,purchase_type,classified_category,classified_subcategory,online
2024-01-15,2024-01-16,AMAZON.COM*12345,PURCHASE,-45.99,Business,General Merchandise,Online Purchases,true
```

### JSON Export Format
```json
{
  "transaction_id": "TXN-0001",
  "transaction_date": "2024-01-15T00:00:00",
  "description": "AMAZON.COM*12345",
  "amount": -45.99,
  "classification": {
    "purchase_type": "Business",
    "category": "General Merchandise",
    "subcategory": "Online Purchases",
    "online": true
  }
}
```

### Tax Report Format
```csv
BUSINESS TRANSACTIONS

Category: General Merchandise
Date,Description,Subcategory,Amount,Online
2024-01-15,AMAZON.COM*12345,Online Purchases,$-45.99,Yes
,,,TOTAL,$-45.99,
```

## Performance Benchmarks

Expected performance with sample data:

- **Load time**: < 100ms for all 68 cases
- **Classification time**: < 1ms per transaction
- **Total test time**: < 1 second for all tests
- **Memory usage**: < 10MB for test data

## Need Help?

1. Read full documentation: `tests/fixtures/README.md`
2. Check test implementation: `tests/test_sample_data_validation.py`
3. Review classification rules: `bin/classification_rules.v4.json`
4. Check test output with `-v` flag for details

## Quick Commands Reference

```bash
# Run all tests
pytest tests/test_sample_data_validation.py -v

# Run with output
pytest tests/test_sample_data_validation.py -v -s

# Run specific test
pytest tests/test_sample_data_validation.py::TestSampleDataValidation::test_edge_cases -v

# Generate exports
python tests/fixtures/generate_export_sample.py

# Check coverage
pytest tests/test_sample_data_validation.py::TestSampleDataValidation::test_coverage_report -v -s
```

## Data Statistics

- **Business Transactions**: 31 (45.6%)
- **Personal Transactions**: 37 (54.4%)
- **Online Transactions**: 29 (42.6%)
- **Offline Transactions**: 39 (57.4%)
- **Income Transactions**: 8 (11.8%)
- **Expense Transactions**: 60 (88.2%)
- **Edge Cases**: 7 (10.3%)
- **Priority Tests**: 3 (4.4%)

---

**Last Updated**: 2025-01-09
**Version**: 1.0
**Total Test Cases**: 68
