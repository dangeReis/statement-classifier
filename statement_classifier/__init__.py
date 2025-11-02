"""Statement Classifier: Rule-based transaction classification.

A modular, testable transaction classifier using black box design principles
inspired by Eskil Steenberg's architecture philosophy.

Core Design Principles:
- Clear Primitives: Well-defined data types that flow through the system
- Black Box Interfaces: Each module hides implementation details
- Single Responsibility: Each component has one clear job
- Replaceability: Any module can be rewritten using only its interface
- Observable: Comprehensive logging and error handling

Core Components:
- Engine: Classification logic (pure function, no I/O)
- Providers: Rule loading abstraction (file, DB, API agnostic)
- Types: Type definitions and exception hierarchy
- CLI: Command-line tools for rule management
- Orchestration: Workflow automation (PR, branching, etc)

Architecture Layers:
```
    User/Application
            ↓
    ClassificationEngine (pure logic)
            ↓
    RuleProvider (interface)
            ↓
    Concrete Provider (File/DB/API)
            ↓
    Rule Data (normalized v4 format)
```

Basic Usage Example:
```python
from statement_classifier import ClassificationEngine, FileRuleProvider

# Create provider (file-based in this example)
provider = FileRuleProvider('path/to/rules.json')

# Create engine (pure classification logic)
engine = ClassificationEngine(provider)

# Classify a transaction
result = engine.classify(
    description='AMAZON MARK* NH4S31RG1 SEATTLE WA',
    category='PURCHASE'
)

# Result is a ClassificationResult TypedDict
print(result['purchase_type'])  # 'Personal'
print(result['category'])       # 'Online Shopping'
print(result['subcategory'])    # 'General Retail'
print(result['online'])         # True
```

Architecture Philosophy:
This system follows Eskil Steenberg's principles for building large-scale
software that lasts years. The key insight is that good architecture makes
it possible to replace any component without changing others.

Each module is designed so that:
1. Someone could rewrite it from scratch using only its interface
2. The rest of the system wouldn't know or care that it changed
3. Complexity is hidden behind simple, consistent interfaces

This enables:
- Easy testing (swap real providers with mocks)
- Easy replacement (switch from file to database rules)
- Easy maintenance (understand one module without understanding all)
- Easy evolution (add new providers without touching the classifier)

For full architecture documentation, see ARCHITECTURE_PLAN.md
"""

__version__ = '2.0.0'
__author__ = 'Russ Lee'

from statement_classifier.types import (
    TransactionInput,
    ClassificationResult,
    RuleDict,
    ValidationResult,
    ClassifierException,
    RuleProviderException,
    RuleFormatException,
    ValidationException,
    OrchestrationException
)

from statement_classifier.providers import RuleProvider
from statement_classifier.engine import ClassificationEngine
from statement_classifier.providers.file import FileRuleProvider

__all__ = [
    # Types - primitives and results
    'TransactionInput',
    'ClassificationResult',
    'RuleDict',
    'ValidationResult',

    # Exceptions - error handling
    'ClassifierException',
    'RuleProviderException',
    'RuleFormatException',
    'ValidationException',
    'OrchestrationException',

    # Interfaces - abstractions
    'RuleProvider',

    # Implementations - core engine and file provider
    'ClassificationEngine',
    'FileRuleProvider',
]
