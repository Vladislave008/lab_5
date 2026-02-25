import logging
from protocols import TaskProtocol, TaskSourceProtocol
from constants import COLORS
from typing import Any

class TaskModule():
    def __init__(self):
        self.tasks = list()
        self.sources = list()
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(
            level=logging.INFO, 
            format='[%(asctime)s] %(levelname)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            #filename='logger.log',
            #filemode='a'
        )

    def add_task(self, task: Any):
        '''Добавление задачи в модуль (с проверкой контракта)'''
        if self._check_task_contract(task):
            self.tasks.append(task)
            self.logger.info(f"{COLORS.GREEN}Task {task} has been added to module{COLORS.RESET}")
        else:
            self.logger.info(f"{COLORS.RED}Task {task} can't be added to module{COLORS.RESET}")

    def add_source(self, source: Any):
        '''Добавление источника в модуль (с проверкой контракта)'''
        if self._check_task_source_contract(source):
            self.sources.append(source)
            self.logger.info(f"{COLORS.GREEN}Source {source} has been added to module{COLORS.RESET}")
        else:
            self.logger.info(f"{COLORS.RED}Source {source} can't be added to module{COLORS.RESET}")

    def get_tasks_from_sources(self):
        '''Добавление задач из всех источников в модуль'''
        for source in self.sources:
            for task in source.get_tasks():
                self.add_task(task)

    def _check_task_contract(self, obj: Any) -> bool:
        '''Проверка соблюдения контракта для задач'''
        if isinstance(obj, TaskProtocol) and (isinstance(getattr(obj, 'id'), int) or isinstance(getattr(obj, 'id'), str)):
            self.logger.info(f'{COLORS.GRAY}Object {obj} meets task contract{COLORS.RESET}')
            return True
        elif isinstance(obj, dict):
            if 'id' in obj and 'payload' in obj and (isinstance(obj['id'], int) or isinstance(obj['id'], str)):
                self.logger.info(f'{COLORS.GRAY}Object {obj} meets task contract{COLORS.RESET}')
                return True
            else:
                id_type = None
                if 'id' in obj: 
                    id_type = type(obj['id'])
                self.logger.info(f'{COLORS.GRAY}Object {obj} does not meet task contract\n\t\t\t    has id: {'id' in obj}\n\t\t\t    id type (must be int/str): {id_type}\n\t\t\t    has payload: {'payload' in obj}{COLORS.RESET}')
                return False
        else:
            has_id = hasattr(obj, 'id')
            has_payload = hasattr(obj, 'payload')
            id_type = None
            if has_id: 
                id_type = type(getattr(obj, 'id'))
            self.logger.info(f'{COLORS.GRAY}Object {obj} does not meet task contract\n\t\t\t    has id: {has_id}\n\t\t\t    id type (must be int/str): {id_type}\n\t\t\t    has payload: {has_payload}{COLORS.RESET}')
            return False

    def _check_task_source_contract(self, obj: Any) -> bool:
        '''Проверка соблюдения контракта для источников задач'''
        if isinstance(obj, TaskSourceProtocol):
            self.logger.info(f'{COLORS.GRAY}Object {obj} meets task source contract{COLORS.RESET}')
            return True
        else:
            has_getter = hasattr(obj, 'get_tasks')
            self.logger.info(f'{COLORS.GRAY}Object {obj} does not meet task contract\n\t\t\t    has get_tasks() func: {has_getter}{COLORS.RESET}')
            return False
    