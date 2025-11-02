#!/usr/bin/env python3
"""Shared transaction classification utilities.

Supports both v3 (legacy array format) and v4 (structured object format) rules.
v4 format is preferred and will be used if available.
"""

from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Tuple, Optional

# Try v4 first, fallback to v3
RULES_V4_PATH = Path(__file__).resolve().parent / 'classification_rules.v4.json'
RULES_V3_PATH = Path(__file__).resolve().parent / 'classification_rules.v3.json'

FALLBACK_RULES = {
    'Food & Drink': ['RESTAURANT', 'FOOD', 'CAFE', 'FAST FOOD', 'BAKERY', 'ICE CREAM', 'SUSHI'],
    'Health & Wellness': ['HEALTH & WELLNESS'],
    'Education': ['EDUCATION'],
    'Grocery': ['GROCERY', 'SUPERMARKET'],
    'Auto': ['AUTO', 'FUEL', 'GAS', 'SERVICE STATION'],
    'Electronics': ['ELECTRONIC STORES'],
    'Clothing': ['CLOTHING', 'SPORTS APPAREL', 'FAMILY CLOTHING STORE'],
    'Subscriptions': ['COMPUTER SOFTWARE STORE'],
    'Government': ['MISC GOVERNMENT SERVICES'],
    'Recreation': ['SPORTING GOODS STORES', 'MISC AMUSEMENT / RECREATION SERVICES'],
    'Services': ['PHOTOGRAPHIC STUDIOS', 'PROFESSIONAL SERVICES'],
    'Entertainment': ['DANCE HALLS,STUDIOS / SCHOOLS', 'CABLE,SATELLITE,PAY TV/RADIO SERVICES', 'TOURIST ATTRACTIONS AND EXHIBITS'],
    'Pets': ['PET SHOPS-PET FOOD / SUPPLY STORES'],
    'General Merchandise': ['VARIETY STORE', 'DISCOUNT STORE', 'MISCELLANEOUS / SPECIALTY RETAIL STORES', 'BOOK STORES'],
    'Hosting': ['COMPUTER NETWORK/INFO SRVS'],
    'Travel': ['HOTELS, MOTELS, RESORTS', 'BRIDGE AND ROAD FEES, TOLLS', 'LOCAL/SUBURBAN COMMUTER PASSENGER TRANS', 'TAXICAB/LIMOUSINE'],
    'Medical': ['DRUG STORES,PHARMACIES', 'MEDICAL SERVICES', 'OPTOMETRISTS,OPHTHALMOLOGISTS', 'DENTAL/LABORATORY/MEDICAL/OPHTHALMIC HOS'],
    'Home Improvement': ['HOME SUPPLY WAREHOUSE STORES'],
    'Business Inventory': ['STATIONARY, OFFICE SUPPLIES AND PRINTING', 'STATIONARY,OFFICE / SCHOOL SUPPLY STORES', 'INDUSTRIAL SUPPLIES'],
    'Insurance': ['INSURANCE-SALES / UNDERWRITING']
}


@lru_cache(maxsize=1)
def _load_rules() -> dict:
    """Load classification rules, preferring v4 format over v3."""
    # Try v4 first
    if RULES_V4_PATH.exists():
        with open(RULES_V4_PATH, 'r') as f:
            data = json.load(f)
            data['__format__'] = 'v4'
            return data

    # Fallback to v3
    if RULES_V3_PATH.exists():
        with open(RULES_V3_PATH, 'r') as f:
            data = json.load(f)
            data['__format__'] = 'v3'
            return data

    raise FileNotFoundError(f"No rules file found at {RULES_V4_PATH} or {RULES_V3_PATH}")


def _classify_v4(description: str, category: str, rules_data: dict) -> Tuple[str, str, str, bool]:
    """Classify using v4 format rules (structured objects)."""
    rules = rules_data.get('rules', [])
    fallback_categories = rules_data.get('fallback_categories', FALLBACK_RULES)

    # Sort rules by priority (already sorted, but ensure it)
    sorted_rules = sorted(rules, key=lambda r: r.get('priority', 50), reverse=True)

    # Try to match against rules (only if description is not empty)
    if description:
        for rule in sorted_rules:
            keywords = rule.get('keywords', [])
            if any(kw in description for kw in keywords):
                return (
                    rule.get('purchase_type', 'Personal'),
                    rule.get('category', ''),
                    rule.get('subcategory', ''),
                    rule.get('online', False)
                )

    # Fallback to category-based matching (if we have a category)
    if category:
        for cat, keywords in fallback_categories.items():
            if any(kw in category for kw in keywords):
                return 'Personal', cat, '', False

    return 'Personal', '', '', False


def _classify_v3(description: str, category: str, rules_data: dict) -> Tuple[str, str, str, bool]:
    """Classify using v3 format rules (legacy array format)."""
    business_keywords = rules_data.get('business_keywords', [])
    online_purchase_keywords = rules_data.get('online_purchase_keywords', [])
    transaction_rules = rules_data.get('transaction_rules', [])

    purchase_type = 'Business' if any(keyword in description for keyword in business_keywords) else 'Personal'
    transaction_cat = ''
    transaction_subcat = ''

    for cat, subcat, keywords in transaction_rules:
        if any(kw in description for kw in keywords):
            transaction_cat = cat
            transaction_subcat = subcat
            break

    if not transaction_cat:
        for cat, keywords in FALLBACK_RULES.items():
            if any(kw in category for kw in keywords):
                transaction_cat = cat
                break

    online_purchase = any(keyword in description for keyword in online_purchase_keywords)
    return purchase_type, transaction_cat, transaction_subcat, online_purchase


def classify_transaction(description: str, category: str) -> Tuple[str, str, str, bool]:
    """Return (purchase_type, category, subcategory, online_flag) for a transaction.

    Args:
        description: Transaction description (merchant name, etc.)
        category: Merchant category code or category name

    Returns:
        Tuple of (purchase_type, category, subcategory, online_flag)
        - purchase_type: "Business" or "Personal"
        - category: Main transaction category
        - subcategory: Specific subcategory (if applicable)
        - online_flag: True if online purchase, False otherwise
    """
    description = (description or '').upper()
    category = str(category or '').upper()

    rules_data = _load_rules()
    format_version = rules_data.get('__format__', 'v3')

    if format_version == 'v4':
        return _classify_v4(description, category, rules_data)
    else:
        return _classify_v3(description, category, rules_data)
