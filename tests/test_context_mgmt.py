import pytest
import os
import tempfile
from src.async_data.context_mgmt import (
    DatabaseSession, 
    ChDir, 
    HTTPSession
)

@pytest.mark.asyncio
class TestDatabaseSession:
    """Тесты DatabaseSession"""
    
    async def test_session_lifecycle(self):
        session = DatabaseSession("test.db")
        
        async with session as conn:
            assert conn == "FAKE_CONNECTION"
            assert session.connection == "FAKE_CONNECTION"
        
        assert session.connection is None
    
    async def test_session_with_exception(self):
        session = DatabaseSession("test.db")
        
        try:
            async with session:
                raise ValueError("Test error")
        except ValueError:
            pass
        
        assert session.connection is None
    
    async def test_multiple_sessions(self):
        session1 = DatabaseSession("db1.db")
        session2 = DatabaseSession("db2.db")
        
        async with session1 as conn1:
            async with session2 as conn2:
                assert conn1 == conn2
                assert session1.connection == "FAKE_CONNECTION"
                assert session2.connection == "FAKE_CONNECTION"


class TestChDir:
    """Тесты ChDir"""
    
    def test_change_directory(self):
        old_dir = os.getcwd()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            with ChDir(tmpdir):
                assert os.getcwd() == tmpdir
            
            assert os.getcwd() == old_dir
    
    def test_change_directory_with_exception(self):
        old_dir = os.getcwd()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            try:
                with ChDir(tmpdir):
                    raise ValueError("Test")
            except ValueError:
                pass
            
            assert os.getcwd() == old_dir


@pytest.mark.asyncio
class TestHTTPSession:
    """Тесты HTTPSession"""
    
    async def test_session_lifecycle(self):
        session = HTTPSession("https://api.example.com")
        
        async with session as http:
            assert http == session
            assert session.connection is not None
        
        assert session.connection is None
    
    async def test_get_request(self):
        
        async with HTTPSession("https://api.example.com") as session:
            response = await session.get("/users", params={"page": 1})
            
            assert response["status"] == "ok"
            assert response["method"] == "GET"
            assert response["url"] == "https://api.example.com/users"
            assert response["params"] == {"page": 1}
    
    async def test_post_request(self):
         
        async with HTTPSession("https://api.example.com") as session:
            response = await session.post(
                "/users",
                json={"name": "John"}
            )
            
            assert response["status"] == "ok"
            assert response["method"] == "POST"
            assert response["json"] == {"name": "John"}
    
    async def test_request_without_connection(self):
        session = HTTPSession("https://api.example.com")
        
        with pytest.raises(RuntimeError, match="No active connection"):
            await session.get("/users")
    
    async def test_session_with_exception(self):
        session = HTTPSession("https://api.example.com")
        
        try:
            async with session:
                raise ValueError("Test error")
        except ValueError:
            pass
        
        assert session.connection is None