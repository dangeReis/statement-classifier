# Statement Classifier

A Python library for classifying financial transactions from bank statements.

## Features

- **Transaction Classification**: Automatically classify transactions into categories (Business, Personal, etc.)
- **Rule-Based System**: Configurable JSON-based classification rules
- **Tax Categories**: Integrated tax category support for business accounting
- **Flexible Format Support**: Handles both v3 (legacy) and v4 (structured) rule formats
- **Comprehensive Tests**: 33+ test cases covering real-world scenarios

## Installation

```bash
pip install statement-classifier
```

## Quick Start

```python
from bin.classifier import classify_transaction

# Classify a transaction
purchase_type, category, subcategory, is_online = classify_transaction(
    description="Amazon AMZN.COM",
    transaction_type="PURCHASE"
)

print(f"Category: {category}")  # Output: General Merchandise
print(f"Online: {is_online}")   # Output: True
```

## Core Components

### classifier.py
Main classification engine supporting both transaction classification and online detection.

### manage_rules.py
CLI tool for managing classification rules - add, remove, and update rules easily.

### validate_rules.py
Validates rule JSON files against the schema before deployment.

### tax_categories.json
Complete tax category mapping for business expense categorization.

## Rules Format

Classification rules are defined in `bin/classification_rules.v4.json`:

```json
{
  "categoryName": {
    "rules": [
      {
        "patterns": ["pattern1", "pattern2"],
        "type": "PURCHASE|TRANSFER|FEE|INCOME"
      }
    ]
  }
}
```

## Testing

Run the full test suite:

```bash
python -m pytest bin/test_classifier.py -v
```

All 33 tests should pass with no errors.

## License

MIT

## Author

Created by Russ Reis
