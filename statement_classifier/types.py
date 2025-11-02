"""Type definitions and exception hierarchy for statement classifier.

This module defines all the core data types and exceptions used throughout
the classifier. By centralizing types here, we ensure consistency and make
it easy to understand the data flow through the system.
"""

from typing import TypedDict, List, Dict, Any


# Core Primitives - Data that flows through the system


class TransactionInput(TypedDict):
    """Input to classification function.

    Attributes:
        description: Transaction description (e.g., "AMAZON MARK* NH4S31RG1")
        category: Merchant category code (e.g., "PURCHASE")
    """
    description: str
    category: str


class ClassificationResult(TypedDict):
    """Output from classification function.

    Attributes:
        purchase_type: "Business" or "Personal"
        category: High-level category (e.g., "Online Shopping")
        subcategory: Specific subcategory (e.g., "General Retail")
        online: Whether transaction is online
    """
    purchase_type: str
    category: str
    subcategory: str
    online: bool


class RuleDict(TypedDict, total=False):
    """Rule definition (v4 format).

    Attributes:
        id: Unique rule identifier (lowercase, hyphenated)
        keywords: List of keywords to match against transaction description
        purchase_type: "Business" or "Personal"
        category: Rule's category
        subcategory: Rule's subcategory
        online: Whether this rule applies to online transactions
        priority: Rule priority (higher = checked first), 1-1000
        notes: Optional documentation
        tags: Optional tags for organization
    """
    id: str
    keywords: List[str]
    purchase_type: str
    category: str
    subcategory: str
    online: bool
    priority: int
    notes: str
    tags: List[str]


class ValidationResult(TypedDict):
    """Result of rule validation.

    Attributes:
        is_valid: Whether rules passed validation
        errors: List of validation errors (fatal)
        warnings: List of validation warnings (non-fatal)
    """
    is_valid: bool
    errors: List[str]
    warnings: List[str]


# Exception Hierarchy - Clear error handling


class ClassifierException(Exception):
    """Base exception for all classifier errors.

    All exceptions raised by the classifier inherit from this,
    making it easy to catch classifier-specific errors.
    """
    pass


class RuleProviderException(ClassifierException):
    """Rule provider failed to load or provide rules.

    Raised when:
    - File cannot be read
    - Database connection fails
    - API request fails
    - Rules cannot be accessed
    """
    pass


class RuleFormatException(ClassifierException):
    """Rule format is invalid or corrupted.

    Raised when:
    - JSON is malformed
    - Required fields are missing
    - Field types are incorrect
    - Format version is unknown
    """
    pass


class ValidationException(ClassifierException):
    """Rule validation failed.

    Raised when:
    - Duplicate rules found
    - Required fields missing
    - Category conflicts exist
    - Other validation errors
    """
    pass


class OrchestrationException(ClassifierException):
    """Workflow automation (PR, branching, etc) failed.

    Raised when:
    - Git operations fail
    - GitHub API calls fail
    - Branch creation fails
    - PR creation fails
    """
    pass
