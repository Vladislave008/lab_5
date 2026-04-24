import asyncio
import os
from typing import Any
import logging

logger = logging.getLogger(__name__)

class DatabaseSession:
    """Контекстный менеджер для работы с БД"""
    
    def __init__(self, path: str):
        self.path = path
        self.connection = None
    
    async def __aenter__(self) -> str:
        """Открываем соединение"""
        logger.info(f"[DB] Connecting to {self.path}")
        await asyncio.sleep(0.1)
        self.connection = "FAKE_CONNECTION"
        return self.connection
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> bool:
        "Закрываем соединение"
        logger.info("[DB] Closing connection")
        await asyncio.sleep(0.1)
        self.connection = None
        return False



class ChDir:
    """Временно переключается в другую директорию"""
    
    def __init__(self, path: str):
        self.new_path = path
        self.old_path = None
    
    def __enter__(self) -> 'ChDir':
        self.old_path = os.getcwd()
        logger.info(f"[ChDir] from {self.old_path} to {self.new_path}")
        os.chdir(self.new_path)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        os.chdir(self.old_path)
        logger.info(f"[ChDir] back to {self.old_path}")
        return False


class HTTPSession:
    """Контекстный менеджер для HTTP"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.connection = None
    
    async def __aenter__(self) -> 'HTTPSession':
        """Открываем HTTP соединение"""
        logger.info(f"[HTTP] Connecting to {self.base_url}")
        await asyncio.sleep(0.1)
        self.connection = f"HTTP_CONNECTION_TO_{self.base_url}"
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> bool:
        """Закрываем HTTP соединение"""
        logger.info(f"[HTTP] Closing connection {self.connection}")
        await asyncio.sleep(0.1)
        self.connection = None
        if exc_type:
            logger.error(f"[HTTP] Error occurred: {exc_val}")
        return False
    
    async def get(self, path: str = "", params: dict = None) -> dict[str, Any]:
        """GET запрос"""
        if not self.connection:
            raise RuntimeError("No active connection")
        
        url = f"{self.base_url}{path}"
        logger.info(f"[HTTP] GET {url} with params {params}")
        await asyncio.sleep(0.2)
        return {"status": "ok", "method": "GET", "url": url, "params": params}
    
    async def post(self, path: str = "", data: dict = None, json: dict = None) -> dict[str, Any]:
        """POST запрос"""
        if not self.connection:
            raise RuntimeError("No active connection")
        
        url = f"{self.base_url}{path}"
        logger.info(f"[HTTP] POST {url} with data={data} json={json}")
        await asyncio.sleep(0.2)
        return {"status": "ok", "method": "POST", "url": url, "data": data, "json": json}