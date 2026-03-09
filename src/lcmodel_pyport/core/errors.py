"""Exception hierarchy for staged LCModel port execution."""


class LcmodelPortError(Exception):
    """Base exception for the project."""


class ValidationError(LcmodelPortError):
    """Raised when explicit type/schema validation fails."""


class ControlParseError(LcmodelPortError):
    """Raised when control parsing cannot continue."""


class InputFormatError(LcmodelPortError):
    """Raised when RAW/CORAW input format is invalid."""


class NumericalConvergenceError(LcmodelPortError):
    """Raised when a numerical search/solver fails to converge."""


class OutputContractError(LcmodelPortError):
    """Raised when output content violates expected contracts."""
