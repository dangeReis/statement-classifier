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

### Using the CLI

```bash
# Install the package
pip install -e .

# Classify a transaction
statement-classifier classify "Amazon AMZN.COM" "5411"

# Validate rules file
statement-classifier validate

# View rule statistics
statement-classifier analyze stats

# Find duplicate keywords
statement-classifier analyze duplicates

# Add a new rule
statement-classifier rules add \
  --id "my-rule" \
  --keywords "TEST,EXAMPLE" \
  --type "Personal" \
  --category "Testing"

# Remove a rule
statement-classifier rules remove "my-rule"

# Get a specific rule
statement-classifier rules get "amazon-general"

# Use a custom rules file
statement-classifier --rules /path/to/rules.json classify "Amazon" "5411"

# Enable verbose logging
statement-classifier --verbose validate
```

### Using the Python API

```python
from statement_classifier import ClassificationEngine, FileRuleProvider

# Initialize provider and engine
provider = FileRuleProvider(v4_path="bin/classification_rules.v4.json")
engine = ClassificationEngine(provider)

# Classify a transaction
purchase_type, category, subcategory, is_online = engine.classify(
    description="Amazon AMZN.COM",
    category="5411"
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

## CLI Commands Reference

The `statement-classifier` command provides the following subcommands:

### classify
Classify a transaction and show the result.
```bash
statement-classifier classify <description> <category_code>
```

### rules add
Add a new classification rule.
```bash
statement-classifier rules add \
  --id <rule_id> \
  --keywords <comma_separated_keywords> \
  --type <Business|Personal> \
  --category <category_name> \
  [--subcategory <subcategory>] \
  [--online]
```

### rules remove
Remove a rule by ID.
```bash
statement-classifier rules remove <rule_id>
```

### rules get
Get a rule by ID and display as JSON.
```bash
statement-classifier rules get <rule_id>
```

### validate
Validate the rules file for errors and warnings.
```bash
statement-classifier validate
```

### analyze stats
Display statistics about the rules.
```bash
statement-classifier analyze stats
```

### analyze duplicates
Find duplicate keywords across rules.
```bash
statement-classifier analyze duplicates
```

### analyze coverage
Show coverage analysis of the rules.
```bash
statement-classifier analyze coverage
```

### test
Test classifications from a CSV file.
```bash
statement-classifier test <csv_file>
```

### Global Options

- `--rules <path>`: Use a custom rules file (default: bin/classification_rules.v4.json)
- `--verbose, -v`: Enable verbose output and logging
- `--help, -h`: Show help message

## Testing

Run the full test suite:

```bash
python -m pytest tests/ -v
```

All tests should pass with no errors. This includes:
- 64 core library tests
- 27 CLI tests
- Unit and integration tests

## License

MIT

## Author

Created by Russ Reis
