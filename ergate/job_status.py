from enum import IntEnum, auto


class JobStatus(IntEnum):
    SCHEDULED = auto()
    PENDING = auto()
    QUEUED = auto()
    RUNNING = auto()
    COMPLETED = auto()
    FAILED = auto()
    ABORTED = auto()
