from __future__ import annotations

from collections.abc import Generator
from contextlib import ExitStack, contextmanager
from typing import TYPE_CHECKING, Any, Callable, Generic, ParamSpec, TypeVar

from .depends_cache import DependsCache
from .inspect import build_function_arg_info
from .paths import NextStepPath, WorkflowPath

if TYPE_CHECKING:
    from .workflow import Workflow


CallableSpec = ParamSpec("CallableSpec")
CallableRetval = TypeVar("CallableRetval")


class WorkflowStep(Generic[CallableSpec, CallableRetval]):
    def __init__(
        self,
        workflow: Workflow,
        callable: Callable[CallableSpec, CallableRetval],
    ) -> None:
        self.workflow = workflow
        self.callable = callable
        self.arg_info = build_function_arg_info(callable)
        # TODO: do we need this default value, or will get_type_hints inspection work?
        self.paths: list[WorkflowPath] = [NextStepPath()]

    @property
    def name(self) -> str:
        return self.callable.__name__

    @contextmanager
    def build_args(
        self, user_context: Any, last_return_value: Any
    ) -> Generator[tuple[list[Any], dict[str, Any]], None, None]:
        with ExitStack() as stack:
            yield self.arg_info.build_args(
                stack,
                DependsCache(),
                user_context,
                last_return_value,
            )

    def __call__(
        self,
        *args: CallableSpec.args,
        **kwargs: CallableSpec.kwargs,
    ) -> CallableRetval:
        return self.callable(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.workflow.unique_name}.{self.callable.__name__}"
