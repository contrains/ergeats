from typing import (
    Callable,
    Iterator,
    ParamSpec,
    TypeAlias,
    TypeVar,
    overload,
)

from .exceptions import UnknownStepError
from .log import LOG
from .paths import GoToEndPath, GoToStepPath, NextStepPath, SkipNStepsPath, WorkflowPath
from .workflow_step import WorkflowStep

CallableSpec = ParamSpec("CallableSpec")
CallableRetval = TypeVar("CallableRetval")
CallableTypeHint: TypeAlias = Callable[CallableSpec, CallableRetval]
WorkflowStepTypeHint: TypeAlias = WorkflowStep[CallableSpec, CallableRetval]
WorkflowPathTypeHint: TypeAlias = tuple[WorkflowPath, int]


class Workflow:
    def __init__(self, unique_name: str) -> None:
        self.unique_name = unique_name
        self._steps: list[WorkflowStep] = []
        self._paths: dict[int, list[list[WorkflowPathTypeHint]]] = {}

    def __getitem__(self, index: int) -> WorkflowStep:
        try:
            return self._steps[index]
        except IndexError:
            raise UnknownStepError(
                f'Workflow "{self.unique_name}" has {len(self)} steps '
                f"- tried to access step #{index}"
            ) from None

    def __iter__(self) -> Iterator[WorkflowStep]:
        return iter(self._steps)

    def __len__(self) -> int:
        return len(self._steps)

    @property
    def paths(self) -> dict[int, list[list[WorkflowPathTypeHint]]]:
        return self._paths

    def _calculate_paths(
        self,
        index: int,
        *,
        depth: int = 0,
        initial: bool = False,
        path: WorkflowPath | None = None,
    ) -> list[list[WorkflowPathTypeHint]]:
        print("===111.01===", [index, depth])

        if not initial:
            print("===111.02===", [index, depth])

            if path is None:
                print("===111.03===", [index, depth])

                err = (
                    f"Failed to calculate workflow path from step {index}: "
                    f"path cannot be null."
                )
                raise ValueError(err)

            print("===111.04===", [index, depth])

            if path not in self[index].paths:
                print("===111.05===", [index, depth])

                err = (
                    f"Failed to calculate workflow path from step {index}: "
                    f"path not registered: {path}"
                )
                raise ValueError(err)

            print("===111.06===", [index, depth])

            next_index = self._find_next_step(index, path)
        else:
            print("===111.07===", [index, depth])

            path = NextStepPath()
            next_index = index

        print("===111.08===", [index, depth], next_index)

        current_step = (path, index)
        paths: list[list[WorkflowPathTypeHint]] = []

        print("===111.09===", [index, depth], current_step)

        if depth >= max(len(self) * 3, 30):
            print("===111.10===", [index, depth], max(len(self) * 3, 30))
            LOG.warning(
                "Aborting current path calculation due to potential infinite loop: "
                f"(depth: {depth})"
            )
            print("===411.1===", [index, depth], len(paths), [[p[1] for p in path] for path in paths])
            return paths

        if next_index >= len(self):
            print("===111.11===", [index, depth])

            paths.append([current_step])
            print("===411.2===", [index, depth], len(paths), [[p[1] for p in path] for path in paths])
            print("===111.12===", [index, depth], paths)
            return paths

        for ii, next_path in enumerate(self[next_index].paths):
            print("===111.13===", [index, depth], ii, next_path)
            print("===421.1===", [index, depth], "next_path:", next_path)

            # TODO: Should there be an `if not already in self._paths` to avoid duplicate calculations?
            print("===421.2===", list(self.paths.keys()))
            if next_path in self.paths:
                paths += self.paths[next_path]
                print("===111.14===", [index, depth], len(paths))
            else:
                paths += self._calculate_paths(next_index, path=next_path, depth=depth + 1)
                print("===111.15===", [index, depth], len(paths))

        if not initial:
            paths = [[current_step, *next_path] for next_path in paths]
            print("===111.16===", [index, depth], len(paths))

        print("===111.17===", [index, depth], len(paths))
        print("===411.3===", [index, depth], len(paths), [[p[1] for p in path] for path in paths])
        return paths

    def calculate_paths(self, index: int) -> list[list[WorkflowPathTypeHint]]:

        print("===110.1===", index)
        paths = self._calculate_paths(index, initial=True)
        print("===110.2===", index, len(paths), [[p[1] for p in path] for path in paths])
        return paths

    def update_paths(self) -> None:
        self._paths = {}

        for step in self:
            pass

        for step in reversed(self):
            self.paths[step.index] = self.calculate_paths(step.index)

    def _find_next_step(self, index: int, path: WorkflowPath) -> int:
        if isinstance(path, GoToEndPath):
            return len(self)

        if isinstance(path, GoToStepPath):
            return self.get_step_index_by_name(path.step_name)

        if isinstance(path, SkipNStepsPath):
            return index + 1 + path.n

        return index + 1

    def get_step_index_by_name(self, step_name: str) -> int:
        try:
            return next(step.index for step in self if step.name == step_name)
        except StopIteration:
            raise UnknownStepError(
                f'No step named "{step_name}" is registered in '
                f'Workflow "{self.unique_name}"'
            )

    def finalize(self) -> None:
        self.update_paths()

    @overload
    def step(self, func: CallableTypeHint) -> WorkflowStepTypeHint: ...

    @overload
    def step(
        self,
        *,
        paths: list[WorkflowPath] | None = None,
    ) -> CallableTypeHint: ...

    def step(
        self,
        func: CallableTypeHint | None = None,
        *,
        paths: list[WorkflowPath] | None = None,
    ) -> CallableTypeHint | WorkflowStepTypeHint:
        def _decorate(func: CallableTypeHint) -> WorkflowStepTypeHint:
            step = WorkflowStep(self, func, len(self), paths=paths)
            self._steps.append(step)
            return step

        if func is None:
            return _decorate

        return _decorate(func)
