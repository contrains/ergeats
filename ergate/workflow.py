from typing import Callable, Iterator, ParamSpec, TypeVar

from .exceptions import UnknownStepNameError
from .workflow_step import WorkflowStep

CallableSpec = ParamSpec("CallableSpec")
CallableRetval = TypeVar("CallableRetval")


class Workflow:
    def __init__(self, unique_name: str) -> None:
        self.unique_name = unique_name
        self._steps: list[WorkflowStep] = []
        self._step_names: dict[str, int] = {}

    def __getitem__(self, key: int | str) -> WorkflowStep:
        try:
            index = self.get_index_by_step_name(key) if isinstance(key, str) else key
            return self._steps[index]
        except IndexError:
            raise IndexError(
                f'Workflow "{self.unique_name}" has {len(self)} steps '
                f"- tried to access step #{key}"
            ) from None

    def __iter__(self) -> Iterator[WorkflowStep]:
        return iter(self._steps)

    def __len__(self) -> int:
        return len(self._steps)

    def get_index_by_step_name(self, step_name: str) -> int:
        try:
            return self._step_names[step_name]
        except KeyError:
            raise UnknownStepNameError(
                f'No step named "{step_name}" is registered in '
                f'Workflow "{self.unique_name}"'
            )

    def step(
            self, func: Callable[CallableSpec, CallableRetval]
    ) -> WorkflowStep[CallableSpec, CallableRetval]:
        step = WorkflowStep(self, func)

        self._step_names[step.name] = len(self)

        self._steps.append(step)

        return step
