# Statement Classifier: Black Box Architecture

## Overview

The Statement Classifier implements Eskil Steenberg's black box design principles for maintainable, modular software.

## Core Components

### Types (statement_classifier/types.py)

- `TransactionInput`: Input primitives
- `ClassificationResult`: Output primitives
- Exception hierarchy: `ClassifierException` + 4 specific types

### Providers (statement_classifier/providers/)

- `RuleProvider`: Abstract interface (any source)
- `FileRuleProvider`: JSON file implementation
- Supports v3/v4 format auto-detection

### Engine (statement_classifier/engine.py)

- `ClassificationEngine`: Pure logic, no I/O
- Priority-based rule matching
- Three-level fallback chain
- Uses `RuleNormalizer` for format handling

### Normalization (statement_classifier/normalization.py)

- `RuleNormalizer`: Format abstraction
- Transparent v3→v4 conversion
- No classifier coupling

### CLI Tools (bin/cli/)

- `RuleManager`: CRUD operations
- `RuleValidator`: Rule validation
- `RuleAnalyzer`: Statistics
- `RuleTestRunner`: Classification testing

### Orchestration (statement_classifier/orchestration/)

- `WorkflowProvider`: Abstract workflow interface
- `RuleUpdateOrchestrator`: Unified rule update workflow

### Logging (statement_classifier/logging.py)

- Optional structured logging
- No required dependencies

## Design Principles

### Black Box Design

Each module is replaceable using only its interface. Implementation details are completely hidden.

### Single Responsibility

Each module has one clear job. No mixing of concerns.

### Type Safety

Full type hints throughout. TypedDict for primitives.

### Threading Safety

Thread-safe operations using RLock where needed.

### Observable

Comprehensive logging and error handling.

## Test Coverage

- Phase 1: 22 tests (types, interfaces, normalization)
- Phase 2: 14 tests (engine, file provider, integration)
- Phase 3: 9 tests (CLI tools)
- Phase 4: 9 tests (orchestration, logging)
- Phase 5: 7 tests (full integration)
- Total: 61 tests, 100% pass rate

## Usage Example

```python
from statement_classifier import ClassificationEngine, FileRuleProvider

# Create provider
provider = FileRuleProvider('path/to/rules.json')

# Create engine
engine = ClassificationEngine(provider)

# Classify transaction
result = engine.classify(
    description='AMAZON MARK* NH4S31RG1',
    category='PURCHASE'
)

print(result['purchase_type'])  # 'Personal'
print(result['category'])       # 'Online Shopping'
```

## Thread Safety

The system is thread-safe:

- `FileRuleProvider` uses `RLock` for concurrent access
- `Engine` is stateless (pure logic)
- Safe for multi-threaded applications

## Extending the System

### Adding a New Rule Provider

```python
from statement_classifier.providers import RuleProvider

class DatabaseRuleProvider(RuleProvider):
    def load_rules(self):
        # Load from database
        pass

    # Implement other abstract methods
```

Engine works unchanged with any `RuleProvider` implementation.

### Adding Workflow Automation

```python
from statement_classifier.orchestration.base import WorkflowProvider

class GitLabWorkflow(WorkflowProvider):
    def create_branch(self, branch_name):
        # Implement using GitLab API
        pass

    # Implement other abstract methods
```

Orchestrator works unchanged with any `WorkflowProvider` implementation.

## Architecture Benefits

1. **Replaceability**: Replace any component without changing others
2. **Testability**: Swap implementations with mocks
3. **Maintainability**: Each module is independently understandable
4. **Extensibility**: Add new implementations via interfaces
5. **Clarity**: Clear separation of concerns

## Module Dependencies

```
types.py
├── normalization.py
├── providers/base.py
│   └── providers/file.py
├── engine.py
├── logging.py
├── orchestration/base.py
└── coordinator.py
```

## Black Box Principle in Practice

### Before (Coupled)

```python
# Old way - tightly coupled
engine = Engine(rules_file_path='./rules.json')
# Hard to test, hard to extend
```

### After (Black Box)

```python
# New way - loosely coupled via interface
provider = FileRuleProvider(v4_path=rules_file)
engine = ClassificationEngine(provider)
# Easy to test (mock provider), easy to extend (new provider)
```

## Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific phase
python -m pytest tests/test_phase1_foundation.py -v
python -m pytest tests/test_phase2_engine.py -v
python -m pytest tests/test_phase3_cli.py -v
python -m pytest tests/test_phase4_orchestration.py -v
python -m pytest tests/test_integration.py -v

# Run with coverage
python -m pytest tests/ --cov=statement_classifier
```

## Package Structure

```
statement_classifier/
├── __init__.py              # Package exports
├── types.py                 # Type definitions
├── engine.py                # Classification logic
├── logging.py               # Logging utility
├── normalization.py         # Format handling
├── coordinator.py           # Orchestration
├── providers/
│   ├── __init__.py
│   ├── base.py              # RuleProvider interface
│   └── file.py              # File implementation
└── orchestration/
    ├── __init__.py
    └── base.py              # WorkflowProvider interface

bin/
└── cli/
    ├── __init__.py
    ├── rule_manager.py      # CRUD operations
    ├── rule_validator.py    # Validation
    ├── rule_analyzer.py     # Statistics
    └── rule_tester.py       # Testing

tests/
├── test_phase1_foundation.py
├── test_phase2_engine.py
├── test_phase3_cli.py
├── test_phase4_orchestration.py
└── test_integration.py
```

## Key Features

### Format Abstraction

The system transparently handles v3 and v4 rule formats:

```python
provider = FileRuleProvider(v4_path='v4.json', v3_path='v3.json')
# Automatically loads v4 if available, falls back to v3
```

### Priority-Based Matching

Rules are evaluated in priority order:

```python
# Higher priority rules checked first
result = engine.classify('AMAZON UBER', 'PURCHASE')
# Returns AMAZON (priority 100) not UBER (priority 95)
```

### Three-Level Fallback

Classification falls back gracefully:

1. Keyword matching (highest specificity)
2. Category fallback (medium specificity)
3. Ultimate fallback (default)

### Optional Logging

Logging is disabled by default (zero overhead):

```python
logger = Logger(enabled=True)  # Enable for debugging
logger.info("Processing started")
```

## Security Considerations

- No external dependencies (except standard library)
- Type checking prevents common errors
- All inputs validated
- Thread-safe for concurrent use

## Performance

- In-memory caching for rules
- LRU cache prevents unbounded memory growth
- Stateless engine for parallel classification
- Thread-safe without locks in hot path

## Future Extensions

The architecture supports:

- Database rule providers
- Remote rule sources
- Custom classification strategies
- GitHub/GitLab workflow integrations
- Advanced logging and monitoring
