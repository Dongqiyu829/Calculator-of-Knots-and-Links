"""Structured errors exposed by the application service boundary."""

from __future__ import annotations


class ApplicationServiceError(ValueError):
    """Base class for errors that application frontends can handle uniformly."""


class BraidInputError(ApplicationServiceError):
    """Base class for parsing or validation errors in a braid input."""


class GeneratorParseError(BraidInputError):
    """Raised when generator text cannot be parsed as signed integers."""


class QParameterParseError(ApplicationServiceError):
    """Raised when a frontend q parameter is not SymPy-compatible text."""


class BraidInputValidationError(BraidInputError):
    """Raised when parsed input violates the existing BraidWord validation rules."""


class UnknownCatalogExampleError(ApplicationServiceError):
    """Raised when an application caller requests a catalog label that does not exist."""


class UnknownEvaluationBranchError(ApplicationServiceError):
    """Raised when a caller requests an unsupported internal evaluation branch."""


class UnknownEvaluationModelError(ApplicationServiceError):
    """Raised when a caller requests an unsupported frontend-facing model id."""


class CustomMatrixInputError(ApplicationServiceError):
    """Raised when custom R/check-R input cannot form a validated local model."""


class CustomBraidOperatorError(ApplicationServiceError):
    """Raised when a custom local model cannot evaluate the requested braid word."""
