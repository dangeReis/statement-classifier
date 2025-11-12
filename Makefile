.PHONY: help install test test-verbose test-coverage lint fmt clean build docs

# Python command (use python3 by default)
PYTHON := python3

# Default target
help:
	@echo "Statement Classifier - Available Make Targets"
	@echo ""
	@echo "Development:"
	@echo "  make install        Install dependencies"
	@echo "  make test           Run all tests"
	@echo "  make test-verbose   Run tests with verbose output"
	@echo "  make test-coverage  Run tests with coverage report"
	@echo "  make lint           Run linters (flake8, pylint)"
	@echo "  make fmt            Format code with black"
	@echo ""
	@echo "Validation:"
	@echo "  make validate       Validate classification rules"
	@echo "  make test-samples   Test sample transaction data"
	@echo ""
	@echo "Build:"
	@echo "  make build          Build package"
	@echo "  make clean          Clean build artifacts"
	@echo ""
	@echo "Documentation:"
	@echo "  make docs           Generate documentation"
	@echo ""

# Install dependencies
install:
	@echo "Installing dependencies..."
	pip install -e .
	pip install pytest pytest-cov black flake8 pylint
	@echo "✓ Dependencies installed"

# Run all tests
test:
	@echo "Running tests..."
	$(PYTHON) -m pytest tests/ -v
	@echo "✓ All tests passed"

# Run tests with verbose output
test-verbose:
	@echo "Running tests with verbose output..."
	$(PYTHON) -m pytest tests/ -vv -s

# Run tests with coverage report
test-coverage:
	@echo "Running tests with coverage..."
	$(PYTHON) -m pytest tests/ --cov=statement_classifier --cov-report=term-missing --cov-report=html
	@echo "✓ Coverage report generated in htmlcov/"

# Run just the sample data validation tests
test-samples:
	@echo "Testing sample transaction data..."
	$(PYTHON) -m pytest tests/test_sample_data_validation.py -v
	@echo "✓ Sample data tests passed"

# Run integration tests
test-integration:
	@echo "Running integration tests..."
	$(PYTHON) -m pytest tests/test_integration.py -v
	@echo "✓ Integration tests passed"

# Run specific test phases
test-phase1:
	@echo "Running Phase 1 tests (Foundation)..."
	$(PYTHON) -m pytest tests/test_phase1_foundation.py -v

test-phase2:
	@echo "Running Phase 2 tests (Engine)..."
	$(PYTHON) -m pytest tests/test_phase2_engine.py -v

test-phase3:
	@echo "Running Phase 3 tests (CLI)..."
	$(PYTHON) -m pytest tests/test_phase3_cli.py -v

test-phase4:
	@echo "Running Phase 4 tests (Orchestration)..."
	$(PYTHON) -m pytest tests/test_phase4_orchestration.py -v

# Lint code
lint:
	@echo "Running linters..."
	@echo "→ flake8..."
	flake8 statement_classifier/ bin/ tests/ --max-line-length=100 --extend-ignore=E203,W503
	@echo "→ pylint..."
	pylint statement_classifier/ bin/*.py --max-line-length=100 --disable=C0114,C0115,C0116
	@echo "✓ Linting complete"

# Format code with black
fmt:
	@echo "Formatting code with black..."
	black statement_classifier/ bin/ tests/ --line-length=100
	@echo "✓ Code formatted"

# Validate classification rules
validate:
	@echo "Validating classification rules..."
	$(PYTHON) bin/validate_rules.py bin/classification_rules.v4.json
	@echo "✓ Rules validated"

# Generate sample exports
generate-samples:
	@echo "Generating sample export files..."
	$(PYTHON) tests/fixtures/generate_export_sample.py
	@echo "✓ Sample exports generated"

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf tests/fixtures/sample_exports/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	@echo "✓ Clean complete"

# Build package
build: clean
	@echo "Building package..."
	$(PYTHON) setup.py sdist bdist_wheel
	@echo "✓ Package built"

# Install package in editable mode
dev-install:
	@echo "Installing in development mode..."
	pip install -e .
	@echo "✓ Development installation complete"

# Generate documentation
docs:
	@echo "Generating documentation..."
	@echo "Documentation targets:"
	@echo "  - README.md (exists)"
	@echo "  - README_ARCHITECTURE.md (exists)"
	@echo "  - tests/fixtures/README.md (exists)"
	@echo "  - tests/fixtures/QUICK_REFERENCE.md (exists)"
	@echo "✓ Documentation available"

# Quick check - run formatting, linting, and tests
check: fmt lint test
	@echo "✓ All checks passed!"

# CI/CD target - run all validation
ci: lint test-coverage validate
	@echo "✓ CI checks complete"

# Show test coverage report
coverage-report:
	@echo "Opening coverage report..."
	@command -v open >/dev/null 2>&1 && open htmlcov/index.html || \
	command -v xdg-open >/dev/null 2>&1 && xdg-open htmlcov/index.html || \
	echo "Coverage report available at htmlcov/index.html"

# Run the classifier on sample data
demo:
	@echo "Running classifier demo..."
	@echo "Test 1: Amazon purchase"
	$(PYTHON) -c "from statement_classifier import ClassificationEngine, FileRuleProvider; \
		provider = FileRuleProvider(v4_path='bin/classification_rules.v4.json'); \
		engine = ClassificationEngine(provider); \
		result = engine.classify('AMAZON.COM*12345', 'PURCHASE'); \
		print(f\"  Purchase Type: {result['purchase_type']}\"); \
		print(f\"  Category: {result['category']}\"); \
		print(f\"  Subcategory: {result['subcategory']}\"); \
		print(f\"  Online: {result['online']}\")"
	@echo ""
	@echo "Test 2: Grocery store"
	$(PYTHON) -c "from statement_classifier import ClassificationEngine, FileRuleProvider; \
		provider = FileRuleProvider(v4_path='bin/classification_rules.v4.json'); \
		engine = ClassificationEngine(provider); \
		result = engine.classify('SHOPRITE LODI', 'GROCERY'); \
		print(f\"  Purchase Type: {result['purchase_type']}\"); \
		print(f\"  Category: {result['category']}\"); \
		print(f\"  Subcategory: {result['subcategory']}\"); \
		print(f\"  Online: {result['online']}\")"
	@echo ""

# Watch tests (requires pytest-watch)
watch:
	@echo "Watching for changes and running tests..."
	@command -v ptw >/dev/null 2>&1 && ptw tests/ || \
	echo "Install pytest-watch first: pip install pytest-watch"

# All tests with full output
test-all: test-phase1 test-phase2 test-phase3 test-phase4 test-integration test-samples
	@echo "✓ All test suites passed!"
