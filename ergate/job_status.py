from enum import IntEnum, auto


class JobStatus(IntEnum):
    SCHEDULED = 1
    PENDING = 7
    QUEUED = 2
    RUNNING = 3
    COMPLETED = 4
    FAILED = 5
    ABORTED = 6
    CANCELLING = 8
    CANCELLED = 9
