# Statement Classifier - CLI Architecture Analysis

## Current State Overview

The statement-classifier project has a **distributed CLI tool structure** rather than a unified main CLI entry point. Each tool is currently a standalone script with its own entry point.

### Current CLI Tools Structure

#### 1. **bin/manage_rules.py** - Primary Rule Management Tool
- **Entry Point**: `main()` function with argparse
- **Commands**: test, validate, duplicates, stats, add
- **Rule Path Handling**: `--rules` flag with default to bin/classification_rules.v4.json
- **Subparser Pattern**: Uses `parser.add_subparsers(dest='command')` with individual sub-parsers for each command
- **Implementation Classes**: Relies on external classes:
  - RuleValidator (bin/validate_rules.py)
  - classify_transaction (bin/classifier.py)

```python
parser = argparse.ArgumentParser(description='Manage transaction classification rules')
parser.add_argument('--rules', type=Path, default=Path(__file__).parent / 'classification_rules.v4.json')
subparsers = parser.add_subparsers(dest='command', help='Commands')

# test, validate, duplicates, stats, add commands
```

**Current Commands**:
- `test <description>` - Test classification with optional --category flag
- `validate` - Validate rules file (uses external RuleValidator)
- `duplicates` - Find duplicate keywords
- `stats` - Show statistics about rules
- `add` - Interactive rule addition

#### 2. **bin/validate_rules.py** - Standalone Validator
- **Entry Point**: `main()` with argparse
- **Purpose**: Standalone validation of rules files
- **Arguments**: `rules_file` (positional), `--schema` (optional)
- **Implementation**: RuleValidator class with full validation logic
- **Duplicated Logic**: Similar checks to manage_rules.py's validate command

#### 3. **bin/test_classifier.py** - Test Suite
- **Type**: Unit test file, not a CLI tool
- **Framework**: unittest with 33+ test cases
- **Entry Point**: `run_tests()` function

#### 4. **bin/cli/** Directory - Refactored Components
Contains modular CLI classes (Phase 3 refactoring):

**4a. bin/cli/rule_manager.py** - RuleManager Class
- **Purpose**: Core rule CRUD operations
- **Interface**:
  - `add_rule(rule: RuleDict) -> bool`
  - `remove_rule(rule_id: str) -> bool`
  - `update_rule(rule_id: str, updates: Dict) -> bool`
  - `get_rule(rule_id: str) -> Optional[RuleDict]`
- **Integration**: Uses FileRuleProvider for file operations
- **Error Handling**: RuleProviderException for failures

**4b. bin/cli/rule_validator.py** - RuleValidator Class
- **Purpose**: Validation and reporting
- **Interface**:
  - `validate() -> ValidationResult`
  - `get_report() -> str`
  - `summary() -> Tuple[int, int, bool]`
- **Status**: Works with FileRuleProvider, returns human-readable reports

**4c. bin/cli/rule_analyzer.py** - RuleAnalyzer Class
- **Purpose**: Statistics and diagnostics
- **Interface**:
  - `get_stats() -> Dict[str, Any]`
  - `find_duplicates() -> Dict[str, List[str]]`
  - `coverage_analysis() -> Dict[str, Any]`
- **Metrics**: Rules count, keywords, categories, priority distribution

**4d. bin/cli/rule_tester.py** - RuleTestRunner Class
- **Purpose**: Test classification against rules
- **Interface**:
  - `test_classification(description: str, category: str) -> Dict`
  - `batch_test(test_cases: List[Dict]) -> List[Dict]`
- **Integration**: Uses ClassificationEngine + FileRuleProvider

#### 5. **bin/classifier.py** - Legacy Classification Utility
- **Type**: Standalone utility with `classify_transaction()` function
- **Purpose**: File-based classification (loaded at module import)
- **Format Support**: v3 and v4 with format auto-detection
- **Caching**: Uses @lru_cache for rules loading

---

## Core Integration Points

### RuleProvider Architecture (In statement_classifier/)

**statement_classifier/providers/base.py** - Abstract RuleProvider Interface
```python
class RuleProvider(ABC):
    def load_rules() -> Dict[str, Any]
    def get_rule_by_id(rule_id: str) -> Optional[RuleDict]
    def validate() -> ValidationResult
    def get_metadata() -> Dict[str, Any]
```

**statement_classifier/providers/file.py** - FileRuleProvider Implementation
- **Constructor**: `__init__(v4_path=None, v3_path=None, auto_detect=True)`
- **Default Paths**: 
  - v4: `bin/classification_rules.v4.json`
  - v3: `bin/rules.json`
- **Features**:
  - Thread-safe with RLock
  - Caching with invalidate_cache()
  - Format auto-detection and normalization
  - Comprehensive error handling

### ClassificationEngine (statement_classifier/engine.py)

```python
class ClassificationEngine:
    def __init__(self, rule_provider: RuleProvider)
    def classify(description: str, category: str) -> ClassificationResult
```

**Key Design**:
- Pure business logic - no I/O
- Depends on RuleProvider interface (not implementation)
- Returns ClassificationResult TypedDict
- Supports priority-based rule matching + fallback categories

### Type System (statement_classifier/types.py)

**Key Types**:
- `ClassificationResult` - Output from classification
- `RuleDict` - Rule representation
- `ValidationResult` - Validation output
- **Exceptions**: RuleProviderException, RuleFormatException, ValidationException, OrchestrationException

---

## Current Workflow & Entry Points

### Existing Entry Points (Before Unified CLI)

1. **Direct Python Imports**:
   ```python
   from statement_classifier import ClassificationEngine, FileRuleProvider
   from statement_classifier.providers.file import FileRuleProvider
   from statement_classifier.engine import ClassificationEngine
   ```

2. **Standalone Scripts**:
   ```bash
   python -m bin.manage_rules test "AMAZON MARK*"
   python -m bin.validate_rules bin/classification_rules.v4.json
   python -m unittest bin.test_classifier
   ```

3. **bin/classifier.py Utility** (Old pattern):
   ```python
   from bin.classifier import classify_transaction
   purchase_type, category, subcat, online = classify_transaction(desc, cat)
   ```

### Current Issues

1. **No unified entry point** - Multiple CLI tools that don't coordinate
2. **Inconsistent naming** - manage_rules.py vs validate_rules.py
3. **Duplicated logic** - Validation in both manage_rules.py and validate_rules.py
4. **Poor discoverability** - Users don't know which tool to use
5. **No main CLI program** - Can't do `statement-classifier <command>`
6. **Import duplication** - validate_rules.py and manage_rules.py both import and duplicate RuleValidator

---

## What Needs Implementation

### 1. **Unified Main CLI Entry Point**

Create `bin/statement_classifier.py` or `bin/cli/main.py` that:
- Imports and coordinates all sub-tools
- Uses argparse with a clear command hierarchy
- Routes commands to appropriate tool classes
- Handles common options (--rules, --verbose, --help)
- Provides a single entry point with consistent interface

### 2. **Command Structure**

Proposed unified hierarchy:
```
statement-classifier [global-options] <command> [command-options]

Global Options:
  --rules PATH          Path to rules file (default: bin/classification_rules.v4.json)
  --verbose             Enable verbose output
  --help, -h            Show help

Commands:
  classify              Test classification of a transaction
    --description TEXT
    --category TEXT
  
  rules                 Manage rules
    add                 Add new rule (interactive)
    remove ID           Remove rule by ID
    update ID           Update rule fields
    get ID              Get rule by ID
  
  validate              Validate rules file
    [--rules PATH]      Override default rules path
  
  analyze               Analyze rules statistics
    stats               Show statistics
    duplicates          Find duplicate keywords
    coverage            Coverage analysis
  
  test                  Test rule classifications
    [--batch FILE]      Test multiple cases from JSON file
```

### 3. **Class Organization**

Current classes (in bin/cli/) that should be imported:
- `RuleManager` - from rule_manager.py (CRUD operations)
- `RuleValidator` - from rule_validator.py (validation + reporting)
- `RuleAnalyzer` - from rule_analyzer.py (statistics)
- `RuleTestRunner` - from rule_tester.py (classification testing)

New class to create:
- `StatementClassifierCLI` - Main CLI orchestrator (routes commands to tools)

### 4. **FileRuleProvider Integration**

The unified CLI should:
- Accept `--rules` flag to specify rules file path
- Pass it to FileRuleProvider constructor
- Support both v3 and v4 formats automatically
- Cache rules appropriately

### 5. **setup.py Entry Point Configuration**

Add to setup.py:
```python
entry_points={
    'console_scripts': [
        'statement-classifier=bin.cli.main:main',
    ],
}
```

This enables:
```bash
statement-classifier classify --description "AMAZON MARK*"
statement-classifier rules add
statement-classifier validate
```

---

## Argument Parsing Pattern

### Current Pattern (manage_rules.py)

```python
parser = argparse.ArgumentParser(description='...')
parser.add_argument('--rules', type=Path, default=default_path)

subparsers = parser.add_subparsers(dest='command', help='Commands')

test_parser = subparsers.add_parser('test', help='...')
test_parser.add_argument('description', help='...')
test_parser.add_argument('--category', default='', help='...')

# Then in main():
if args.command == 'test':
    cmd_test(args.description, args.category)
```

### Recommended Pattern for Unified CLI

```python
def main():
    parser = argparse.ArgumentParser(
        prog='statement-classifier',
        description='Manage and test transaction classification rules'
    )
    
    # Global options
    parser.add_argument(
        '--rules',
        type=Path,
        default=Path(__file__).parent.parent / 'bin' / 'classification_rules.v4.json',
        help='Path to rules file'
    )
    parser.add_argument('--verbose', '-v', action='store_true')
    
    # Create subparsers
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Command groups
    _add_classify_commands(subparsers)
    _add_rules_commands(subparsers, parser)
    _add_analyze_commands(subparsers)
    _add_test_commands(subparsers)
    
    args = parser.parse_args()
    
    # Route to handlers
    if not args.command:
        parser.print_help()
        return 1
    
    # Initialize provider with args.rules
    provider = FileRuleProvider(v4_path=args.rules)
    
    # Dispatch commands
    return dispatch_command(args, provider)
```

---

## Integration with ClassificationEngine

The unified CLI should:

1. **Create provider instance** from --rules path:
   ```python
   provider = FileRuleProvider(v4_path=args.rules)
   ```

2. **Use for all operations**:
   - `RuleManager(args.rules)` - for add/remove/update
   - `RuleValidator(args.rules)` - for validation
   - `RuleAnalyzer(args.rules)` - for analytics
   - `ClassificationEngine(provider)` - for testing/classification

3. **Consistent error handling**:
   - Catch RuleProviderException
   - Catch RuleFormatException
   - Catch ValidationException
   - Print user-friendly errors

---

## Summary: What Exists vs What's Needed

### ✅ What Exists

1. **Core Engine** (statement_classifier/engine.py)
   - Pure classification logic
   - Depends on RuleProvider interface

2. **Provider** (statement_classifier/providers/file.py)
   - FileRuleProvider implementation
   - Thread-safe, cached, handles v3/v4

3. **CLI Tool Classes** (bin/cli/)
   - RuleManager - CRUD operations
   - RuleValidator - validation + reports
   - RuleAnalyzer - statistics
   - RuleTestRunner - classification testing

4. **Type System** (statement_classifier/types.py)
   - Well-defined types and exceptions
   - Clear data flow contracts

### 🔴 What's Missing

1. **Unified Main CLI** 
   - No single entry point
   - No command routing/dispatch
   - No global option handling

2. **setup.py Entry Point**
   - No console_scripts entry point
   - Can't run `statement-classifier` from anywhere

3. **CLI Orchestrator Class**
   - No class to coordinate the tool classes
   - No centralized error handling
   - No verbose output support

4. **Integration Code**
   - CLI tools created in isolation
   - No passing of provider to all tools
   - No consistent --rules path handling

---

## Key Files & Locations

### CLI Tool Classes (Existing)
- `/Users/russ/Projects/statement-classifier/bin/cli/rule_manager.py`
- `/Users/russ/Projects/statement-classifier/bin/cli/rule_validator.py`
- `/Users/russ/Projects/statement-classifier/bin/cli/rule_analyzer.py`
- `/Users/russ/Projects/statement-classifier/bin/cli/rule_tester.py`

### Core System Classes
- `/Users/russ/Projects/statement-classifier/statement_classifier/engine.py`
- `/Users/russ/Projects/statement-classifier/statement_classifier/providers/file.py`
- `/Users/russ/Projects/statement-classifier/statement_classifier/types.py`

### Current Standalone Scripts
- `/Users/russ/Projects/statement-classifier/bin/manage_rules.py`
- `/Users/russ/Projects/statement-classifier/bin/validate_rules.py`
- `/Users/russ/Projects/statement-classifier/bin/classifier.py`

### Setup Configuration
- `/Users/russ/Projects/statement-classifier/setup.py`

---

## Implementation Approach

### Phase 1: Create Main CLI Orchestrator
Create `bin/cli/main.py` that:
- Imports all tool classes
- Uses argparse for command routing
- Handles global options
- Provides consistent error handling

### Phase 2: Setup Entry Points
Update `setup.py` to add console_scripts entry point:
```python
entry_points={
    'console_scripts': [
        'statement-classifier=bin.cli.main:main',
    ],
}
```

### Phase 3: Integrate Tool Classes
Wire up CLI to use:
- FileRuleProvider for all operations
- Tool classes for business logic
- Consistent error/output handling

### Phase 4: Deprecate Old Scripts
Keep for backward compatibility but redirect to new main CLI.

