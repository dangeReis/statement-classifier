"""Structured logging with optional output."""

import logging
from typing import Optional


class Logger:
    """Optional structured logging."""

    def __init__(self, name: str = "statement_classifier", enabled: bool = False):
        """Initialize logger.

        Args:
            name: Logger name.
            enabled: Enable logging output.
        """
        self.enabled = enabled
        if enabled:
            self.logger = logging.getLogger(name)
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(levelname)s: %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
        else:
            self.logger = None

    def info(self, msg: str) -> None:
        """Log info."""
        if self.enabled and self.logger:
            self.logger.info(msg)

    def debug(self, msg: str) -> None:
        """Log debug."""
        if self.enabled and self.logger:
            self.logger.debug(msg)

    def error(self, msg: str) -> None:
        """Log error."""
        if self.enabled and self.logger:
            self.logger.error(msg)

    def warning(self, msg: str) -> None:
        """Log warning."""
        if self.enabled and self.logger:
            self.logger.warning(msg)
