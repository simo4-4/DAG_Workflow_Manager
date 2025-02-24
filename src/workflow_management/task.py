from abc import ABC, abstractmethod
import logging
import time
import asyncio
from typing import List, Tuple
from urllib import request
import aiohttp
import polars as pl
import requests

logger = logging.getLogger(__name__)

class Task(ABC):
    def __init__(self, name, func, dependencies=None):
        self.name = name
        self.func = func
        self.dependencies = dependencies or []
        self.result = None
        self.result_count = 0
        self.failure_count = 0
        self.execution_time = None

    @abstractmethod
    def execute(self, dependency_results) -> List:
        raise NotImplementedError("execute() must be implemented")

class SyncTask(Task):
    def execute(self, dependency_results) -> List:
        start_time = time.time()
        try:
            logger.info(f"Executing task: {self.name}")
            self.result, self.result_count, self.failure_count = self.func(*dependency_results)
            logger.info(f"Task {self.name} completed successfully")
        except Exception as e:
            logger.error(f"Task {self.name} failed with error: {e}")
            self.result = None
        finally:
            self.execution_time = time.time() - start_time
        return self.result
    
class AsyncTask(Task):
    def execute(self, dependency_results) -> List:
        start_time = time.time()
        try:
            logger.info(f"Executing task: {self.name}")
            self.result, self.result_count, self.failure_count = asyncio.run(self.func(*dependency_results))
            logger.info(f"Task {self.name} completed successfully")
        except Exception as e:
            logger.error(f"Task {self.name} failed with error: {e}")
            self.result = None
        finally:
            self.execution_time = time.time() - start_time
        return self.result
    
class RequestTask(AsyncTask):
    def __init__(self, name, api_url, max_concurrent_requests=100, dependencies=None):
        super().__init__(name, self.network_task, dependencies)
        self.api_url = api_url
        self.max_concurrent_requests = max_concurrent_requests
        
    async def network_task(self,transformed_data) -> Tuple[List, int, int]:            
        async with aiohttp.ClientSession() as session:
            if isinstance(transformed_data, pl.DataFrame):
                tasks = [self._post_data_with_semaphore(session, self.api_url, row, asyncio.Semaphore(value=self.max_concurrent_requests)) for row in transformed_data.iter_rows(named=True)]
            else:
                tasks = [self._post_data_with_semaphore(session,self.api_url, row, asyncio.Semaphore(value=self.max_concurrent_requests)) for row in transformed_data]
            results = await asyncio.gather(*tasks)
            return results, len(results), self.failure_count
    
    async def _post_data(self,session: aiohttp.ClientSession, api_url: str, data: dict):
        try:
            async with session.post(api_url, json=data) as response:
                response.raise_for_status() 
                result = await response.json()
                return list(result.values())[0]
        except Exception as e:
            self.failure_count += 1
            logger.error(f"Error for data {data} for api {api_url}: {e}")
            return None

    async def _post_data_with_semaphore(self, session: aiohttp.ClientSession, api_url: str, data: dict, semaphore: asyncio.Semaphore):
        async with semaphore:
            return await self._post_data(session, api_url, data)
        
class MultiRequestTask(AsyncTask):
    def __init__(self, name, api_urls: List, max_concurrent_requests=1000, dependencies=None):
        super().__init__(name, self.network_task, dependencies)
        self.api_urls = api_urls
        self.max_concurrent_requests = max_concurrent_requests
        
    async def network_task(self,transformed_data) -> Tuple[List, int, int]:            
        async with aiohttp.ClientSession() as session:
            if isinstance(transformed_data, pl.DataFrame):
                tasks = [self._combiner([self._post_data_with_semaphore(session, api_url, row, asyncio.Semaphore(value=self.max_concurrent_requests)) for api_url in self.api_urls]) for row in transformed_data.iter_rows(named=True)]
            else:
                tasks = [self._combiner([self._post_data_with_semaphore(session, api_url, row, asyncio.Semaphore(value=self.max_concurrent_requests)) for api_url in self.api_urls]) for row in transformed_data]
            results = await asyncio.gather(*tasks)
            return results, len(results), self.failure_count
    
    async def _post_data(self,session: aiohttp.ClientSession, api_url: str, data: dict):
        try:
            async with session.post(api_url, json=data) as response:
                response.raise_for_status() 
                result = await response.json()
                return list(result.values())[0]
        except Exception as e:
            self.failure_count += 1
            logger.error(f"Error for data {data} for api {api_url}: {e}")
            return None

    async def _post_data_with_semaphore(self, session: aiohttp.ClientSession, api_url: str, data: dict, semaphore: asyncio.Semaphore):
        async with semaphore:
            return await self._post_data(session, api_url, data)
        
    async def _combiner(self, tasks):
        return await asyncio.gather(*tasks)
    
class SyncRequestTask(SyncTask):
    def __init__(self, name, api_url, dependencies=None):
        super().__init__(name, self.network_task, dependencies)
        self.api_url = api_url
        
    def network_task(self,transformed_data) -> Tuple[List, int, int]:            
        with requests.Session() as session:
            if isinstance(transformed_data, pl.DataFrame):
                tasks = [self._post_data(session, self.api_url, row) for row in transformed_data.iter_rows(named=True)]
            else:
                tasks = [self._post_data(session,self.api_url, row) for row in transformed_data]
            results = tasks
            return results, len(results), self.failure_count
    
    def _post_data(self,session, api_url: str, data: dict):
        try:
            with session.post(api_url, json=data) as response:
                response.raise_for_status() 
                result = response.json()
                return list(result.values())[0]
        except Exception as e:
            self.failure_count += 1
            logger.error(f"Error for data {data} for api {api_url}: {e}")
            return None
