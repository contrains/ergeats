from typing import Callable, Iterator, ParamSpec, TypeVar

from .workflow_step import WorkflowStep

CallableSpec = ParamSpec("CallableSpec")
CallableRetval = TypeVar("CallableRetval")


class Workflow:
    def __init__(self, unique_name: str) -> None:
        self.unique_name = unique_name
        self._steps: list[WorkflowStep] = []
        self._labels: dict[str, int] = {}

    def __getitem__(self, key: int | str) -> WorkflowStep:
        try:
            if isinstance(key, int):
                return self._steps[key]
            else:
                idx = self._labels[key]
                return self._steps[idx]
        except IndexError:
            raise IndexError(
                f'Workflow "{self.unique_name}" has {len(self)} steps '
                f"- tried to access step #{key}"
            ) from None
        except KeyError:
            raise KeyError(
                f'No label named "{key}" is registered in '
                f'Workflow "{self.unique_name}"'
            )

    def __iter__(self) -> Iterator[WorkflowStep]:
        return iter(self._steps)

    def __len__(self) -> int:
        return len(self._steps)

    def get_label_index(self, label: str) -> int:
        try:
            return self._labels[label]
        except KeyError:
            raise KeyError(
                f'No label named "{label}" is registered in '
                f'Workflow "{self.unique_name}"'
            )

    def label(self, label: str) -> Callable[CallableSpec, CallableRetval]:
        def _decorate(
            func: WorkflowStep[CallableSpec, CallableRetval],
        ) -> WorkflowStep[CallableSpec, CallableRetval]:
            if not isinstance(func, WorkflowStep):
                # This guard clause isn't strictly necessary with the type hints.
                # It is included as a helpful hint to the developer.
                err = (
                    "@label decorator method must be called on a WorkflowStep.  "
                    "Did you remember to invoke @step first?"
                )
                raise ValueError(err)

            if label in self._labels:
                err = (
                    f'A workflow step with label "{label}" '
                    "is already registered."
                )
                raise ValueError(err)

            self._labels[label] = len(self._steps) - 1

            return func

        return _decorate

    def step(
        self, func: Callable[CallableSpec, CallableRetval]
    ) -> WorkflowStep[CallableSpec, CallableRetval]:
        step = WorkflowStep(self, func)
        self._steps.append(step)
        return step