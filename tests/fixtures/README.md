# Test Fixtures - Sample Transaction Data

This directory contains comprehensive sample transaction data for testing the statement classifier system.

## Files

### 1. `sample_transactions.json`
Complete test data in JSON format with detailed test suites organized by transaction type.

**Structure:**
```json
{
  "test_suites": {
    "business_income": [...],
    "business_expenses": [...],
    "business_taxes": [...],
    "personal_food": [...],
    "personal_healthcare": [...],
    "edge_cases": [...],
    "priority_testing": [...],
    "online_flag_testing": [...]
  }
}
```

Each test case includes:
- `description`: Transaction description (merchant name)
- `category`: Merchant category code
- `expected`: Expected classification output
  - `purchase_type`: "Business" or "Personal"
  - `category`: Main category
  - `subcategory`: Specific subcategory
  - `online`: Boolean flag for online transactions
- `notes`: Optional test case notes

### 2. `sample_transactions.csv`
Same test data in CSV format for easier import into spreadsheets or databases.

**Columns:**
- `description`: Transaction description
- `category`: Merchant category code
- `expected_purchase_type`: Expected purchase type
- `expected_category`: Expected category
- `expected_subcategory`: Expected subcategory
- `expected_online`: Expected online flag (true/false)
- `notes`: Test case notes
- `test_suite`: Which test suite this belongs to

## Test Suites

### Business Income (5 test cases)
Tests business income classification including:
- Amazon Associates revenue
- Amazon FBA revenue
- eBay sales
- Google AdSense
- Domain reseller income

### Business Expenses (10 test cases)
Tests business expense classification including:
- Online purchases (Amazon, eBay)
- Tolls and auto insurance
- Home improvement
- Office supplies
- Cloud hosting (AWS)
- Advertising (Google Ads)
- Shipping (USPS)
- Utilities (water, electric)

### Business Taxes (3 test cases)
Tests tax payment classification:
- Federal income tax
- State income tax (NY, NJ)

### Business Fees (3 test cases)
Tests bank and government fee classification:
- ACH transaction fees
- Payment return fees
- Government fees (DMV)

### Personal Food (8 test cases)
Tests personal food and dining classification:
- Online grocery (Amazon Fresh)
- Supermarkets (ShopRite, H Mart)
- Fast food (McDonald's)
- Restaurants (sushi, bakery)
- Ice cream shops
- Liquor stores

### Personal Healthcare (5 test cases)
Tests personal healthcare classification:
- Allergy treatment
- Dental care
- Pharmacy
- Eye care
- Veterinary

### Personal Recreation (6 test cases)
Tests personal recreation classification:
- Sports programs (soccer, swimming, pickleball)
- Chess classes
- Movie streaming
- Subscription services (Hulu)

### Personal Shopping (4 test cases)
Tests personal shopping classification:
- Clothing (Gap, Nike)
- General merchandise (Target, Costco)

### Personal Services (4 test cases)
Tests personal services classification:
- Haircuts
- Ride share (Uber)
- Auto fuel
- Professional services (LinkedIn)

### Personal Financial (5 test cases)
Tests personal financial transactions:
- Savings transfers
- Credit card payments
- ATM withdrawals
- Interest income
- IRA contributions

### Personal Income (3 test cases)
Tests personal income classification:
- Payroll deposits
- Unemployment benefits
- Tax refunds

### Edge Cases (7 test cases)
Tests boundary conditions and edge cases:
- Empty description
- Unknown merchants
- Multiple keywords (priority testing)
- Lowercase inputs (normalization)
- Whitespace handling
- Partial keyword matching
- Special characters

### Priority Testing (3 test cases)
Tests rule priority handling:
- Priority 1000 (highest)
- Priority 999 (very high)
- Ensures correct rule wins when multiple match

### Online Flag Testing (4 test cases)
Tests online transaction flag accuracy:
- Online purchases (Amazon.com, Walmart.com)
- In-store purchases (Target, ShopRite)

## Usage

### Running the Test Suite

```bash
# Run all validation tests
python -m pytest tests/test_sample_data_validation.py -v

# Run specific test suite
python -m pytest tests/test_sample_data_validation.py::TestSampleDataValidation::test_business_income_transactions -v

# Run with coverage report
python -m pytest tests/test_sample_data_validation.py::TestSampleDataValidation::test_coverage_report -v -s
```

### Using in Your Own Tests

#### Load JSON Data
```python
import json
from pathlib import Path

fixtures_path = Path(__file__).parent / 'fixtures' / 'sample_transactions.json'
with open(fixtures_path, 'r') as f:
    test_data = json.load(f)

# Access specific test suite
business_income_tests = test_data['test_suites']['business_income']

# Iterate through test cases
for test_case in business_income_tests:
    description = test_case['description']
    category = test_case['category']
    expected = test_case['expected']
    # Run your classification
```

#### Load CSV Data
```python
import csv
from pathlib import Path

fixtures_path = Path(__file__).parent / 'fixtures' / 'sample_transactions.csv'
with open(fixtures_path, 'r') as f:
    reader = csv.DictReader(f)
    test_cases = list(reader)

# Filter by test suite
business_tests = [
    tc for tc in test_cases
    if tc['test_suite'].startswith('business_')
]

# Run classification
for test_case in business_tests:
    description = test_case['description']
    category = test_case['category']
    # Convert string to bool
    expected_online = test_case['expected_online'].lower() == 'true'
```

### Manual Testing

You can also use this data for manual testing:

```python
from statement_classifier import ClassificationEngine, FileRuleProvider

# Initialize engine
provider = FileRuleProvider(v4_path='bin/classification_rules.v4.json')
engine = ClassificationEngine(provider)

# Test a specific transaction
result = engine.classify('AMAZON.COM* NH4S31RG1', 'PURCHASE')

print(f"Purchase Type: {result['purchase_type']}")
print(f"Category: {result['category']}")
print(f"Subcategory: {result['subcategory']}")
print(f"Online: {result['online']}")
```

## Test Coverage

The test data provides comprehensive coverage:

- **Total Test Cases**: 68
- **Business Transactions**: ~31 (45.6%)
- **Personal Transactions**: ~37 (54.4%)
- **Online Transactions**: ~29 (42.6%)
- **Offline Transactions**: ~39 (57.4%)

Coverage by category:
- Business Income: 5 cases
- Business Expenses: 10 cases
- Business Taxes: 3 cases
- Business Fees: 3 cases
- Personal Food & Dining: 8 cases
- Personal Healthcare: 5 cases
- Personal Recreation: 6 cases
- Personal Shopping: 4 cases
- Personal Services: 4 cases
- Personal Financial: 5 cases
- Personal Income: 3 cases
- Edge Cases: 7 cases
- Priority Tests: 3 cases
- Online Flag Tests: 4 cases

## Expected Test Results

All test cases should pass when run against the current classification rules (v4.0). If any tests fail:

1. **Check rule file**: Ensure `classification_rules.v4.json` is up to date
2. **Check priority**: Higher priority rules should always win
3. **Check keywords**: Keywords must match exactly (case-insensitive)
4. **Check normalization**: Inputs should be normalized (uppercase, trimmed)

## Adding New Test Cases

To add new test cases:

1. **JSON Format**:
   - Add to appropriate test suite in `sample_transactions.json`
   - Include all required fields: description, category, expected
   - Add optional notes field for documentation

2. **CSV Format**:
   - Add new row to `sample_transactions.csv`
   - Fill in all columns
   - Use consistent formatting

3. **Run Tests**:
   ```bash
   python -m pytest tests/test_sample_data_validation.py -v
   ```

## Export Testing

This test data can also be used to validate export functionality:

```python
# Classify all test transactions
results = []
for test_case in test_data:
    result = engine.classify(
        test_case['description'],
        test_case['category']
    )
    results.append({
        'description': test_case['description'],
        'purchase_type': result['purchase_type'],
        'category': result['category'],
        'subcategory': result['subcategory'],
        'online': result['online']
    })

# Export to CSV
import csv
with open('classified_transactions.csv', 'w', newline='') as f:
    fieldnames = ['description', 'purchase_type', 'category', 'subcategory', 'online']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(results)
```

## Notes

- All test cases are based on real transaction patterns from the classification rules
- Priority values range from 920-1000 to ensure consistent matching
- Edge cases test boundary conditions and error handling
- Online flag tests verify correct detection of online vs in-store purchases
- Special characters in merchant names are preserved and tested

## Troubleshooting

### Tests Failing?

1. **Rule file not found**: Check path to `classification_rules.v4.json`
2. **Wrong results**: Verify rules haven't changed since test data was created
3. **Priority issues**: Higher priority rules should always match first
4. **Case sensitivity**: All matching is case-insensitive (uppercase normalization)
5. **Whitespace**: Leading/trailing whitespace should be trimmed

### Need More Test Data?

Generate additional test cases based on:
- New rules added to classification_rules.v4.json
- Real transaction data from bank statements
- Specific edge cases you want to test
- Performance testing (bulk transactions)

## License

This test data is part of the statement-classifier project and follows the same license.
