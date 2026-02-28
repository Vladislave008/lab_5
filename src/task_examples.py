from typing import Any
from dataclasses import dataclass
from collections import namedtuple

class TaskClass:
    def __init__(self, id: int | str, payload: Any):
        self.id = id
        self.payload = payload

@dataclass
class TaskDataclass:
    id: int | str
    payload: Any

TaskNamedTuple = namedtuple('TaskNamedTuple', ['id', 'payload'])
