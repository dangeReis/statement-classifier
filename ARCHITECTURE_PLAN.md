# Statement Classifier: Black Box Architecture Refactoring Plan

**Version**: 1.0
**Date**: 2025-11-02
**Principle**: Eskil Steenberg's Black Box Design - Replaceability, Single Responsibility, Clear Interfaces

---

## Executive Summary

Refactor statement-classifier to follow black box design principles:
- Each module has ONE clear responsibility
- All modules are independently replaceable using only their interfaces
- Implementation details are completely hidden
- Core primitives flow cleanly through the system
- Threading-safe, observable, and maintainable for 5+ years

**Result**: A system where any component can be rewritten without breaking others.

---

## Core Principles

### 1. Clear Primitives
```python
# Transaction (input primitive)
Transaction = Tuple[str, str]  # (description, merchant_category)

# Classification Result (output primitive)
Classification = Tuple[str, str, str, bool]  # (type, category, subcat, online)

# Rule (data primitive)
Rule = {
    id: str,
    keywords: List[str],
    purchase_type: str,
    category: str,
    subcategory: str,
    online: bool,
    priority: int
}
```

### 2. Black Box Boundaries
- **What**: Clear public interfaces
- **How**: Implementation details hidden
- **Where**: File paths, caching, format conversion all abstracted

### 3. Single Responsibility
- **Classifier**: Only classification logic
- **RuleProvider**: Only rule loading (any source)
- **RuleValidator**: Only validation
- **CLI Tools**: Only user interaction
- **Orchestrator**: Only workflow automation

### 4. Replaceability Test
Could a developer rewrite any module using only its interface? Yes, for all modules.

---

## PHASE 1: Core Black Box Abstractions

### Goal
Create clean interfaces that hide implementation details and allow easy replacement.

### 1.1 RuleProvider Interface
**File**: `statement_classifier/providers/base.py`

```python
from abc import ABC, abstractmethod
from typing import Dict, List, Optional

class RuleProvider(ABC):
    """Abstract interface for rule loading.

    A rule provider supplies rules from any source (file, database, API, etc)
    without the classifier knowing the source.
    """

    @abstractmethod
    def load_rules(self) -> Dict[str, any]:
        """Load rules and metadata.

        Returns:
            {
                'version': '4.0',
                'rules': [Rule],
                'fallback_categories': Dict
            }
        """
        pass

    @abstractmethod
    def get_rule_by_id(self, rule_id: str) -> Optional[Dict]:
        """Get a specific rule by ID."""
        pass

    @abstractmethod
    def validate(self) -> Tuple[bool, List[str]]:
        """Validate that all rules are correct.

        Returns:
            (is_valid: bool, errors: List[str])
        """
        pass
```

**Interface Design**:
- ✅ No mention of files, JSON, databases
- ✅ Returns plain dictionaries (language-agnostic)
- ✅ Can be implemented with file, DB, API, memory
- ✅ Validation is optional but discoverable

### 1.2 FileRuleProvider Implementation
**File**: `statement_classifier/providers/file.py`

```python
class FileRuleProvider(RuleProvider):
    """Rules from JSON file.

    Implementation detail: uses LRU cache and file watching.
    But classifier doesn't know this.
    """

    def __init__(self, v4_path: Path, v3_path: Optional[Path] = None):
        self.v4_path = v4_path
        self.v3_path = v3_path
        self._cache = None
        self._watch_mtime = 0

    def load_rules(self) -> Dict:
        # Implementation: load JSON, detect format, cache
        # But caller just sees: returns rules dict
        pass
```

**Hides**:
- File paths
- LRU cache implementation
- v3 vs v4 detection logic
- JSON parsing details
- Error handling specifics

### 1.3 ClassificationEngine
**File**: `statement_classifier/engine.py`

```python
class ClassificationEngine:
    """Pure classification logic, no I/O.

    Takes rules and classifies transactions.
    """

    def __init__(self, rule_provider: RuleProvider):
        self.provider = rule_provider

    def classify(self, description: str, category: str) -> Classification:
        """Classify a transaction.

        Args:
            description: Transaction description (any case)
            category: Merchant category code

        Returns:
            (purchase_type, category, subcategory, online_flag)
        """
        rules = self.provider.load_rules()
        # Pure classification logic here
        return self._match_rules(description, category, rules)

    def _match_rules(self, description: str, category: str, rules: Dict) -> Classification:
        """Format-agnostic classification logic."""
        # No knowledge of v3 vs v4
        # No knowledge of file I/O
        # No knowledge of caching
        pass
```

**Hides**:
- Rule format (v3 vs v4)
- Matching algorithm
- Fallback logic
- Caching strategy

**Depends On**:
- RuleProvider interface (not implementation)
- Classification primitives

### 1.4 RuleNormalizer
**File**: `statement_classifier/normalization.py`

```python
class RuleNormalizer:
    """Convert between rule formats.

    Hides v3/v4 compatibility logic from classifier.
    """

    @staticmethod
    def normalize_to_v4(rules: Dict) -> List[Dict]:
        """Convert any format to v4 internal representation."""
        if rules.get('version') == '4.0':
            return rules['rules']
        elif rules.get('version') == '3.0':
            return RuleNormalizer._v3_to_v4(rules)
        else:
            raise ValueError(f"Unknown rule format: {rules.get('version')}")

    @staticmethod
    def _v3_to_v4(v3_rules: Dict) -> List[Dict]:
        """Convert v3 format to v4."""
        # Conversion logic hidden here
        pass
```

**Hides**:
- Format differences
- Mapping logic
- Field transformations

---

## PHASE 2: Decompose manage_rules.py

**Current Problem**: Single 235-line file with 5 different concerns.

### New Structure

```
bin/
├── cli/
│   ├── __init__.py
│   ├── rule_manager.py      # CRUD operations for rules
│   ├── rule_validator.py    # Validation and conflict checking
│   ├── rule_analyzer.py     # Stats, diagnostics, duplicates
│   └── rule_tester.py       # Test classification, view results
└── cli_main.py              # Entry point routing
```

### 2.1 RuleManager
**File**: `bin/cli/rule_manager.py`

```python
class RuleManager:
    """Manage rules (add, update, delete).

    Interface:
        python -m bin.cli.rule_manager add [--interactive]
        python -m bin.cli.rule_manager remove <rule-id>
        python -m bin.cli.rule_manager update <rule-id> --keyword ...
    """

    def __init__(self, provider: RuleProvider):
        self.provider = provider

    def add_rule(self, rule: Dict) -> bool:
        """Add new rule with validation."""
        pass

    def remove_rule(self, rule_id: str) -> bool:
        """Remove rule by ID."""
        pass

    def update_rule(self, rule_id: str, updates: Dict) -> bool:
        """Update rule fields."""
        pass
```

**Responsibility**: Only rule CRUD operations.

### 2.2 RuleValidator (Clean Up)
**File**: `bin/cli/rule_validator.py`

```python
class RuleValidator:
    """Validate rule format and integrity.

    Interface:
        python -m bin.cli.rule_validator <rules-file>
    """

    def __init__(self, provider: RuleProvider):
        self.provider = provider

    def validate(self) -> ValidationResult:
        """Run all validation checks."""
        # Schema validation
        # Duplicate detection
        # Conflict detection
        # Case sensitivity
        pass
```

**Responsibility**: Only validation.

### 2.3 RuleAnalyzer
**File**: `bin/cli/rule_analyzer.py`

```python
class RuleAnalyzer:
    """Analyze rules for statistics and diagnostics.

    Interface:
        python -m bin.cli.rule_analyzer stats [--format json]
        python -m bin.cli.rule_analyzer duplicates
        python -m bin.cli.rule_analyzer coverage
    """

    def __init__(self, provider: RuleProvider):
        self.provider = provider

    def get_stats(self) -> Dict:
        """Rule statistics (counts, distribution, etc)."""
        pass

    def find_duplicates(self) -> List[DuplicateGroup]:
        """Find duplicate keywords."""
        pass

    def coverage_analysis(self) -> Dict:
        """Analyze rule coverage."""
        pass
```

**Responsibility**: Only analysis and statistics.

### 2.4 RuleTestRunner
**File**: `bin/cli/rule_tester.py`

```python
class RuleTestRunner:
    """Test classification against rules.

    Interface:
        python -m bin.cli.rule_tester classify <description> [<category>]
        python -m bin.cli.rule_tester batch <csv-file>
    """

    def __init__(self, engine: ClassificationEngine):
        self.engine = engine

    def test_classification(self, description: str, category: str) -> Dict:
        """Test single classification, show matching rule."""
        pass

    def batch_test(self, csv_path: Path) -> List[Dict]:
        """Test multiple classifications from CSV."""
        pass
```

**Responsibility**: Only testing and interactive use.

### 2.5 CLI Entry Point
**File**: `bin/cli_main.py`

```python
"""Main CLI router - simple dispatch to subcommands."""

def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='command')

    # Route to appropriate handler
    if command == 'add':
        RuleManager(provider).add_rule_interactive()
    elif command == 'validate':
        RuleValidator(provider).validate()
    elif command == 'stats':
        RuleAnalyzer(provider).get_stats()
    elif command == 'test':
        RuleTestRunner(engine).test_classification()
    # ... etc

if __name__ == '__main__':
    main()
```

**Responsibility**: Only routing and argument parsing.

---

## PHASE 3: Unified Orchestration

**Current Problem**: Orchestrator is separate from rules system. They should coordinate.

### New Structure

```
statement_classifier/
├── orchestration/
│   ├── __init__.py
│   ├── base.py              # WorkflowProvider interface
│   ├── github.py            # GitHub workflow implementation
│   └── local.py             # Local workflow (for testing)
└── coordinator.py           # Coordinates rules + models
```

### 3.1 WorkflowProvider Interface
**File**: `statement_classifier/orchestration/base.py`

```python
class WorkflowProvider(ABC):
    """Abstract workflow automation.

    Implementations: GitHub, GitLab, local execution, etc.
    """

    @abstractmethod
    def create_branch(self, branch_name: str) -> bool:
        """Create feature branch."""
        pass

    @abstractmethod
    def create_pull_request(self, title: str, body: str) -> int:
        """Create PR, return PR number."""
        pass

    @abstractmethod
    def wait_for_approval(self, pr_number: int, timeout: int) -> bool:
        """Wait for PR approval or completion."""
        pass

    @abstractmethod
    def merge_pull_request(self, pr_number: int) -> bool:
        """Merge approved PR."""
        pass
```

**Hides**:
- GitHub API details
- PR polling logic
- Merge strategies
- Auth mechanisms

### 3.2 Unified Coordinator
**File**: `statement_classifier/coordinator.py`

```python
class RuleUpdateOrchestrator:
    """Orchestrate rule updates through workflow.

    Unified interface for:
    - Planning rule changes
    - Validating changes
    - Creating PRs
    - Testing changes
    - Merging when approved
    """

    def __init__(self, workflow: WorkflowProvider, engine: ClassificationEngine):
        self.workflow = workflow
        self.engine = engine

    def propose_rule_update(self, rules: List[Dict]) -> Dict:
        """Propose rule update workflow."""
        # 1. Validate rules
        # 2. Create branch and PR
        # 3. Wait for approval
        # 4. Run tests
        # 5. Merge
        pass

    def propose_rule_removal(self, rule_ids: List[str]) -> Dict:
        """Propose removing rules."""
        pass

    def batch_update(self, changes: List[Change]) -> Dict:
        """Batch multiple rule updates."""
        pass
```

**Hides**:
- Workflow implementation details
- Step orchestration logic
- Error recovery

---

## PHASE 4: Logging, Safety, Threading

### 4.1 Logging Abstraction
**File**: `statement_classifier/logging.py`

```python
class Logger:
    """Optional structured logging."""

    def __init__(self, enabled: bool = False):
        self.enabled = enabled
        self.logger = logging.getLogger(__name__) if enabled else None

    def info(self, msg: str, **kwargs):
        """Log info message."""
        if self.enabled:
            self.logger.info(msg, **kwargs)

    def debug(self, msg: str, **kwargs):
        """Log debug message."""
        if self.enabled:
            self.logger.debug(msg, **kwargs)
```

**Hides**: Logging implementation from all classes.

### 4.2 Type Safety
```python
from typing import TypedDict, Tuple, List

class TransactionInput(TypedDict):
    description: str
    category: str

class ClassificationResult(TypedDict):
    purchase_type: str
    category: str
    subcategory: str
    online: bool

# Functions use these types
def classify(input: TransactionInput) -> ClassificationResult:
    pass
```

### 4.3 Exception Hierarchy
**File**: `statement_classifier/exceptions.py`

```python
class ClassifierException(Exception):
    """Base exception for classifier."""
    pass

class RuleProviderException(ClassifierException):
    """Rule loading/providing failed."""
    pass

class RuleFormatException(ClassifierException):
    """Rule format is invalid."""
    pass

class ValidationException(ClassifierException):
    """Validation failed."""
    pass

class OrchestrationException(ClassifierException):
    """Workflow automation failed."""
    pass
```

### 4.4 Threading Safety
**File**: `statement_classifier/providers/file.py`

```python
from threading import RLock

class FileRuleProvider(RuleProvider):
    """Thread-safe file rule provider."""

    def __init__(self, v4_path: Path, v3_path: Optional[Path] = None):
        self._lock = RLock()
        self._cache = None

    def load_rules(self) -> Dict:
        with self._lock:
            # Cache and file I/O protected by lock
            pass
```

---

## Integration Architecture

### Dependency Graph (CLEAN)

```
User/External System
    │
    ├─→ RuleManager (add/remove rules)
    ├─→ RuleValidator (validate)
    ├─→ RuleAnalyzer (stats)
    ├─→ RuleTestRunner (test)
    │
    └─→ ClassificationEngine
        │
        └─→ RuleProvider (interface)
            ├─→ FileRuleProvider (file-based)
            ├─→ DatabaseRuleProvider (future)
            └─→ APIRuleProvider (future)

RuleUpdateOrchestrator
    ├─→ ClassificationEngine
    └─→ WorkflowProvider (interface)
        ├─→ GitHubWorkflow (GitHub API)
        ├─→ GitLabWorkflow (future)
        └─→ LocalWorkflow (testing)
```

**Key Property**: Each module depends only on interfaces, not implementations.

---

## Refactoring Phases Summary

| Phase | Duration | Components | Test Requirements |
|-------|----------|------------|-------------------|
| 1 | 2-3 hours | Interfaces, Engine, Provider | Unit tests for primitives |
| 2 | 2-3 hours | CLI decomposition | CLI integration tests |
| 3 | 2-3 hours | Orchestration | Workflow mocking tests |
| 4 | 1-2 hours | Logging, safety, threading | Thread safety tests |

**Total**: ~8-10 hours of focused implementation

---

## Success Criteria

✅ **Replaceability**: Any module can be rewritten using only its interface
✅ **Single Responsibility**: Each module has one clear job
✅ **Interface-First**: All dependencies are interfaces, not implementations
✅ **Observable**: Logging and error handling provide visibility
✅ **Thread-Safe**: Concurrent access is safe
✅ **Type-Safe**: Full type hints throughout
✅ **Testable**: Each component can be tested in isolation
✅ **Maintainable**: Clear code that explains intent, not implementation

---

## Backward Compatibility

All public APIs remain compatible:
```python
# Old code still works
from bin.classifier import classify_transaction
purchase_type, category, subcat, online = classify_transaction(desc, cat)

# New code can use new interfaces
from statement_classifier import ClassificationEngine, FileRuleProvider
engine = ClassificationEngine(FileRuleProvider(path))
result = engine.classify(desc, cat)
```

---

## Next Steps

1. **Jules Implementation**: Run full Phase 1-4 with Jules orchestration
2. **Validation**: Ensure all tests pass
3. **Documentation**: Update README with new architecture
4. **Migration**: Gradual migration of existing code to new interfaces
5. **Optimization**: Profile and optimize if needed

