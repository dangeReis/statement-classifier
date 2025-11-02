#!/usr/bin/env python3
"""Setup configuration for statement-classifier package."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
README_PATH = Path(__file__).resolve().parent / "README.md"
LONG_DESCRIPTION = README_PATH.read_text(encoding="utf-8") if README_PATH.exists() else ""

setup(
    name="statement-classifier",
    version="1.0.0",
    description="Transaction classification for financial statements",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    author="Russ Reis",
    url="https://github.com/dangeReis/statement-classifier",
    packages=find_packages(),
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Office/Business :: Financial",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="transaction classification finance accounting",
)
