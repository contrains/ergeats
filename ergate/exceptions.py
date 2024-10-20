from typing import Any

from pydantic import ValidationError  # noqa: F401


class ErgateError(Exception):
    """Base class for ergate exceptions."""


class InvalidDefinitionError(ErgateError):
    """Raised when a workflow/step definition is invalid."""


class AbortJob(ErgateError):  # noqa: N818
    """Raised from a step to abort a workflow.
    Should be interpreted as an expected failure.
    """

    def __init__(self, message: str) -> None:
        self.message = message


class GoToEnd(ErgateError):  # noqa: N818
    """Raised from a step to immediately complete the job."""

    def __init__(self, retval: Any = None):
        self.retval = retval


class GoToStep(ErgateError):  # noqa: N818
    """Raised from a step to go to a specific step by its index or string label."""

    def __init__(
        self, *, n: int | None = None, label: str | None = None, retval: Any = None
    ):
        self.label = label
        self.n = n
        self.retval = retval

    @property
    def has_step(self) -> bool:
        return self.n is not None or self.label is not None

    @property
    def next_step(self) -> int | str | None:
        if not self.has_step:
            return None

        if self.n is not None:
            return self.n

        return self.label


class SkipNSteps(ErgateError):  # noqa: N818
    """Raised from a step to skip N steps."""

    def __init__(self, n: int, retval: Any = None):
        self.n = n
        self.retval = retval
