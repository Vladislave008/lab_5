from datetime import datetime, timedelta
from constants import TASK_STATUS_VALUES, TASK_PRIORITY_LOWER, TASK_PRIORITY_UPPER, ALLOWED_TASK_ATTRIBUTES
from typing import Any
import logging


logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)


class TaskException(Exception):
    pass

    
class PriorityAttr:
    """Data дескриптор для работы с приоритетом задачи"""
    def __get__(self, obj, objtype=None) -> int:
        if obj is None:
            return self
        return getattr(obj, "_priority", None)
    
    def __set__(self, obj, value):
        if not isinstance(value, int):
            raise TypeError("Task 'priority' attribute must be int")
        if value < TASK_PRIORITY_LOWER or value > TASK_PRIORITY_UPPER:
            raise ValueError(f"Invalid task 'priority' value: '{value}'. Must be from {TASK_PRIORITY_LOWER} to {TASK_PRIORITY_UPPER}")
        setattr(obj, "_priority", value)


class PlannedTimeAttr:
    """Data дескриптор для работы с запланированным временем задачи"""
    def __get__(self, obj, objtype=None) -> timedelta | None:
        if obj is None:
            return self
        return getattr(obj, "_planned_time", None)
    
    def __set__(self, obj, value):
        if value is not None:
            if isinstance(value, timedelta):
                pass
            elif isinstance(value, (int, float)):
                value = timedelta(seconds=value)
            else:
                raise TypeError("Task 'planned_time' attribute must be timedelta, seconds, or None")
            if value.total_seconds() <= 0:
                raise ValueError("Task 'planned_time' attribute must be positive")
        setattr(obj, "_planned_time", value)


class IdAttr:
    """Data дескриптор для работы с ID задачи"""
    def __get__(self, obj, objtype=None) -> int | str:
        if obj is None:
            return self
        return getattr(obj, "_id", None)
    
    def __set__(self, obj, value):
        if value is None:
            raise TypeError("Task must have an ID")
        if not isinstance(value, (str, int)):
            raise TypeError("Task 'ID' attribute must be str | int")
        cls = obj.__class__
        if value in cls._all_ids:
            raise TaskException(f"Task with ID '{value}' already exists")
        cls._all_ids.discard(getattr(obj, "_id", None))
        cls._all_ids.add(value)
        setattr(obj, "_id", value)


class DescriptionAttr:
    """Data дескриптор для работы с описанием задачи"""
    def __get__(self, obj, objtype=None) -> str:
        if obj is None:
            return self
        return getattr(obj, "_description", "")
    
    def __set__(self, obj, value):
        if not isinstance(value, str):
            raise TypeError("Task 'description' attribute must be str")
        setattr(obj, "_description", value)


class CreatedAtAttr:
    """Data дескриптор для работы со временем создания задачи (read-only)"""
    def __get__(self, obj, objtype=None) -> datetime:
        if obj is None:
            return self
        return getattr(obj, "_created_at", None)
    
    def __set__(self, obj, value):
        if getattr(obj, "_created_at", None) is not None:
            raise AttributeError("Task 'created_at' attribute is read-only")
        if not isinstance(value, datetime):
            raise TypeError("Task 'created_at' attribute must be datetime")
        setattr(obj, "_created_at", value)



class DurationAttr:
    """Data дескриптор для рассчета времени выполнения задачи с кэшированием"""
    def __get__(self, obj, objtype=None) -> timedelta | None:
        if obj is None:
            return self
        if obj.status == "created":
            return None
        if obj.status == "started":
            return datetime.now() - obj._started_at
        elif obj.status == "finished":
            if not hasattr(obj, "_duration") or getattr(obj, "_duration") is None:
                obj._duration = obj._finished_at - obj._started_at
            return obj._duration
    def __set__(self, obj, value):
        raise AttributeError("Task 'duration' attribute is read-only")


class StatusAttr:
    """Data дескриптор для работы со статусом задачи"""
    def __get__(self, obj, objtype=None) -> str:
        if obj is None:
            return self
        return getattr(obj, "_status", None)
    
    def __set__(self, obj, value):
        if not isinstance(value, str):
            raise TypeError("Task 'status' attribute must be str")
        if value not in TASK_STATUS_VALUES:
            raise ValueError(f"Invalid task 'status' value: '{value}'. Existing values: {TASK_STATUS_VALUES}")
        if value == "created":
            if hasattr(obj, "_status") and getattr(obj, "_status", None) != "created":
                logger.info("Task status reset to 'created', state nullified")
            obj._duration = None
            obj._started_at = None
            obj._finished_at = None
        elif value == "started":
            if getattr(obj, "_status", None) == "started":
                raise TaskException("Task is already started")
            obj._duration = None
            obj._started_at = datetime.now()
            obj._finished_at = None
        elif value == "finished":
            if getattr(obj, "_status", None) == "created":
                raise TaskException("Task can't be finished because it is not started yet")
            elif getattr(obj, "_status", None) == "finished":
                raise TaskException("Task is already finished")
            obj._finished_at = datetime.now()
        setattr(obj, "_status", value)


class IsReadyAttr:
    """Non-data дескриптор для работы с готовностью задачи"""
    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return (obj.payload is not None and 
                obj._id is not None and 
                obj._status in ["created", "finished"])


class IsValidAttr:
    """Non-data дескриптор для работы с атрибутом процента валидности задачи"""
    def __get__(self, obj, objtype=None) -> str:
        if obj is None:
            return self
        empty_attributes = []
        filled_attributes = []
        if obj._id is not None: 
            filled_attributes.append("id")
        else:
            empty_attributes.append("id")
        if obj.payload is not None: 
            filled_attributes.append("payload")
        else:
            empty_attributes.append("payload")
        if obj._description != "": 
            filled_attributes.append("description")  
        else:
            empty_attributes.append("description")
        if obj._priority is not None and TASK_PRIORITY_LOWER < obj._priority <= TASK_PRIORITY_UPPER: 
            filled_attributes.append("priority")  
        else:
            empty_attributes.append("priority")
        if obj._status in TASK_STATUS_VALUES: 
            filled_attributes.append("status")  
        else:
            empty_attributes.append("status")
        if obj._planned_time is not None: 
            filled_attributes.append("planned_time")  
        else:
            empty_attributes.append("planned_time")
        
        res = f"\nTask '{obj._id}' validity:\n    - Attribute filling percentage: {round(len(filled_attributes)/(len(filled_attributes) + len(empty_attributes))*100, 2)}%\n    - Filled attributes: {filled_attributes}\n    - Empty attributes: {empty_attributes}\n"
        return res
    

class Task:
    created_at = CreatedAtAttr()
    status = StatusAttr()
    priority = PriorityAttr()
    id = IdAttr()
    description = DescriptionAttr()
    planned_time = PlannedTimeAttr()
    duration = DurationAttr()
    is_ready = IsReadyAttr()
    is_valid = IsValidAttr()
    _all_ids = set()


    def __init__(self, id: str| int = None, payload: Any = None, description: str = "", 
                 priority: int = 0, status: str = "created", planned_time: int | float | timedelta | None = None):
        self.created_at = datetime.now()
        self.id = id
        self.payload = payload
        self.priority = priority
        self.status = status
        self.planned_time = planned_time
        self.description = description


    def __setattr__(self, name, value):
        """Запрет на установку неизвестных атрибутов"""
        if not (name.startswith("_") or name in ALLOWED_TASK_ATTRIBUTES):
            raise TaskException(f"Unknown attribute '{name}' can't be added to task")
        super().__setattr__(name, value)
    

    def __del__(self):
        """Удаление объекта задачи (системное)"""
        Task._all_ids.discard(getattr(self, "_id", None))

    def __repr__(self):
        return f"Task '{self._id}'"

    def delete(self):
        """Удаление объекта задачи"""
        Task._all_ids.discard(getattr(self, "_id", None))

    @classmethod
    def get_all_ids(cls):
        """Получить все ID"""
        return cls._all_ids.copy()
    
    @property
    def started_at(self):
        """Дескриптор для отображения времени начала выполнения задачи"""
        return getattr(self, "_started_at", None)

    @property
    def finished_at(self):
        """Дескриптор для отображения времени окончания выполнения задачи"""
        return getattr(self, "_finished_at", None)