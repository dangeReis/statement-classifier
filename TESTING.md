# Testing Guide

This document provides a comprehensive guide to testing the statement classifier.

## Quick Start

```bash
# Run all tests
make test

# Run tests with verbose output
make test-verbose

# Run tests with coverage report
make test-coverage

# Run just the sample data validation tests
make test-samples
```

## Available Test Commands

### Using Make (Recommended)

```bash
make test              # Run all tests
make test-verbose      # Run tests with verbose output
make test-coverage     # Run tests with coverage report
make test-samples      # Test sample transaction data only
make test-integration  # Run integration tests only
make test-phase1       # Run Phase 1 tests (Foundation)
make test-phase2       # Run Phase 2 tests (Engine)
make test-phase3       # Run Phase 3 tests (CLI)
make test-phase4       # Run Phase 4 tests (Orchestration)
make test-all          # Run all test suites sequentially
```

### Using pytest Directly

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_sample_data_validation.py -v

# Run specific test method
pytest tests/test_sample_data_validation.py::TestSampleDataValidation::test_edge_cases -v

# Run with coverage
pytest tests/ --cov=statement_classifier --cov-report=html

# Run with verbose output
pytest tests/ -vv -s
```

## Test Suites

### 1. Sample Data Validation (`test_sample_data_validation.py`)

Tests the classifier against 68 comprehensive sample transactions.

**What it tests:**
- Business income classification (5 cases)
- Business expense classification (10 cases)
- Business taxes (3 cases)
- Business fees (3 cases)
- Personal food & dining (8 cases)
- Personal healthcare (5 cases)
- Personal recreation (6 cases)
- Personal shopping (4 cases)
- Personal services (4 cases)
- Personal financial (5 cases)
- Personal income (3 cases)
- Edge cases (7 cases)
- Priority handling (3 cases)
- Online flag accuracy (4 cases)

**Run it:**
```bash
make test-samples
# or
pytest tests/test_sample_data_validation.py -v
```

### 2. Integration Tests (`test_integration.py`)

End-to-end integration tests for the full classification workflow.

**What it tests:**
- Full workflow: load rules and classify
- Thread-safe rule loading
- Logging integration
- Multiple classifications in sequence
- Provider caching
- Cache invalidation
- Provider validation
- Engine with empty rules

**Run it:**
```bash
make test-integration
# or
pytest tests/test_integration.py -v
```

### 3. Phase Tests

Organized by development phase:

- **Phase 1** (`test_phase1_foundation.py`): Core types and exceptions
- **Phase 2** (`test_phase2_engine.py`): Classification engine logic
- **Phase 3** (`test_phase3_cli.py`): CLI functionality
- **Phase 4** (`test_phase4_orchestration.py`): Workflow automation

**Run them:**
```bash
make test-phase1
make test-phase2
make test-phase3
make test-phase4
# or all at once
make test-all
```

## Test Data

### Location
```
tests/fixtures/
├── sample_transactions.json     # 68 test cases in JSON
├── sample_transactions.csv      # 68 test cases in CSV
├── README.md                    # Full documentation
├── QUICK_REFERENCE.md           # Quick reference guide
└── generate_export_sample.py    # Export sample generator
```

### Test Data Coverage

**Total**: 68 test cases

**By Type:**
- Business: 31 cases (45.6%)
- Personal: 37 cases (54.4%)

**By Transaction Mode:**
- Online: 29 cases (42.6%)
- Offline: 39 cases (57.4%)

**By Category:**
- Business Income: 5 cases
- Business Expenses: 10 cases
- Business Taxes: 3 cases
- Business Fees: 3 cases
- Personal Food: 8 cases
- Personal Healthcare: 5 cases
- Personal Recreation: 6 cases
- Personal Shopping: 4 cases
- Personal Services: 4 cases
- Personal Financial: 5 cases
- Personal Income: 3 cases
- Edge Cases: 7 cases
- Priority Tests: 3 cases
- Online Flag Tests: 4 cases

### Generating Sample Exports

```bash
make generate-samples
# or
python tests/fixtures/generate_export_sample.py
```

This generates:
- `tests/fixtures/sample_exports/classified_transactions.csv`
- `tests/fixtures/sample_exports/classified_transactions.json`
- `tests/fixtures/sample_exports/tax_report.csv`

## Code Coverage

### Generate Coverage Report

```bash
make test-coverage
```

This will:
1. Run all tests with coverage tracking
2. Generate an HTML coverage report in `htmlcov/`
3. Display terminal summary

### View Coverage Report

```bash
make coverage-report
# Opens htmlcov/index.html in your browser
```

### Expected Coverage

Target coverage levels:
- **statement_classifier/**: 95%+
- **statement_classifier/types.py**: 100%
- **statement_classifier/engine.py**: 95%+
- **statement_classifier/providers/**: 90%+
- **Overall**: 90%+

## Running Specific Tests

### Test Specific Transaction Type

```bash
# Business income only
pytest tests/test_sample_data_validation.py::TestSampleDataValidation::test_business_income_transactions -v

# Edge cases only
pytest tests/test_sample_data_validation.py::TestSampleDataValidation::test_edge_cases -v

# Priority testing only
pytest tests/test_sample_data_validation.py::TestSampleDataValidation::test_priority_handling -v
```

### Test Specific Functionality

```bash
# Test input normalization
pytest tests/test_sample_data_validation.py::TestSampleDataValidation::test_input_normalization -v

# Test empty inputs
pytest tests/test_sample_data_validation.py::TestSampleDataValidation::test_empty_inputs -v

# Test classification consistency
pytest tests/test_sample_data_validation.py::TestSampleDataValidation::test_classification_consistency -v
```

## Code Quality Checks

### Formatting

```bash
make fmt
# Formats code with black
```

### Linting

```bash
make lint
# Runs flake8 and pylint
```

### Full Check

```bash
make check
# Runs: format → lint → test
```

## CI/CD

### CI Target

```bash
make ci
# Runs: lint → test-coverage → validate
```

This is suitable for continuous integration pipelines.

## Validation

### Validate Classification Rules

```bash
make validate
# Validates bin/classification_rules.v4.json
```

Checks for:
- Valid JSON format
- Required fields present
- No duplicate rule IDs
- Valid priority values
- Valid purchase types
- Valid online flags

## Demo

### Run Quick Demo

```bash
make demo
```

Tests two sample transactions and displays results:
1. Amazon purchase (business, online)
2. Grocery store (personal, offline)

## Troubleshooting

### Tests Failing?

1. **Check dependencies:**
   ```bash
   make install
   ```

2. **Verify rules file:**
   ```bash
   make validate
   ```

3. **Run with verbose output:**
   ```bash
   make test-verbose
   ```

4. **Check specific test:**
   ```bash
   pytest tests/test_sample_data_validation.py::TestSampleDataValidation::test_edge_cases -vv -s
   ```

### Coverage Too Low?

1. Check which files are not covered:
   ```bash
   make test-coverage
   ```

2. Add tests for uncovered lines

3. Re-run coverage report

### Import Errors?

Install package in development mode:
```bash
make dev-install
```

## Performance Testing

### Run Performance Benchmarks

```bash
# Test classification speed
pytest tests/test_sample_data_validation.py::TestSampleDataValidation::test_classification_consistency -v -s

# Test with large dataset
python -m timeit -s "from statement_classifier import ClassificationEngine, FileRuleProvider; provider = FileRuleProvider(v4_path='bin/classification_rules.v4.json'); engine = ClassificationEngine(provider)" "engine.classify('AMAZON.COM*12345', 'PURCHASE')"
```

Expected performance:
- Classification time: < 1ms per transaction
- Rule loading: < 100ms
- 68 test cases: < 1 second total

## Continuous Testing

### Watch Mode

Install pytest-watch and run:
```bash
pip install pytest-watch
make watch
```

This will re-run tests automatically when files change.

## Test Organization

```
tests/
├── __init__.py
├── test_integration.py              # Integration tests
├── test_phase1_foundation.py        # Phase 1: Types & exceptions
├── test_phase2_engine.py            # Phase 2: Engine logic
├── test_phase3_cli.py               # Phase 3: CLI
├── test_phase4_orchestration.py     # Phase 4: Orchestration
├── test_sample_data_validation.py   # Sample data validation
├── test_cli_main.py                 # CLI main tests
└── fixtures/
    ├── sample_transactions.json
    ├── sample_transactions.csv
    ├── README.md
    ├── QUICK_REFERENCE.md
    └── generate_export_sample.py
```

## Best Practices

1. **Run tests before committing:**
   ```bash
   make check
   ```

2. **Add tests for new rules:**
   - Add test cases to `tests/fixtures/sample_transactions.json`
   - Add test cases to `tests/fixtures/sample_transactions.csv`
   - Run `make test-samples`

3. **Validate rules after changes:**
   ```bash
   make validate
   ```

4. **Keep coverage high:**
   ```bash
   make test-coverage
   ```
   Target: 90%+ coverage

5. **Test edge cases:**
   - Empty inputs
   - Special characters
   - Case sensitivity
   - Whitespace
   - Multiple keyword matches

## Documentation

- **Full test data documentation**: `tests/fixtures/README.md`
- **Quick reference**: `tests/fixtures/QUICK_REFERENCE.md`
- **Architecture**: `README_ARCHITECTURE.md`
- **Main README**: `README.md`

## Getting Help

1. Check test output with `-v` flag
2. Review test data documentation
3. Check classification rules file
4. Run validation: `make validate`
5. Check GitHub issues

---

**Last Updated**: 2025-01-09
**Test Framework**: pytest
**Total Test Cases**: 68 sample transactions + integration tests
**Expected Pass Rate**: 100%
