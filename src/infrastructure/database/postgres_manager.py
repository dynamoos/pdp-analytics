from contextlib import asynccontextmanager
from typing import Any, AsyncIterator, List, Optional

import asyncpg
from loguru import logger

from src.shared.exceptions import DatabaseException


class PostgresManager:
    """PostgreSQL connection pool manager with async support"""

    def __init__(
        self, connection_string: str = None, min_size: int = 5, max_size: int = 20
    ):
        self.connection_string = connection_string
        self.min_size = min_size
        self.max_size = max_size
        self.pool: Optional[asyncpg.Pool] = None
        self._initialized = False
        logger.info(f"PostgreSQL manager configured - Pool size: {min_size}-{max_size}")

    async def initialize(self) -> None:
        if self._initialized:
            logger.debug("Connection pool already initialized")
            return
        try:
            logger.info("Initializing PostgreSQL connection pool...")

            self.pool = await asyncpg.create_pool(
                self.connection_string,
                min_size=self.min_size,
                max_size=self.max_size,
            )

            self._initialized = True
            logger.info(
                f"PostgreSQL connection pool initialized successfully - "
                f"Active connections: {self.pool.get_size()}"
            )
        except Exception as e:
            logger.error(f"Failed to initialize connection pool: {str(e)}")
            raise DatabaseException(
                f"PostgreSQL pool initialization failed: {str(e)}"
            ) from e

    @asynccontextmanager
    async def get_connection(self) -> AsyncIterator[asyncpg.Connection]:
        if not self._initialized:
            await self.initialize()

        try:
            logger.debug("Acquiring connection from pool...")
            async with self.pool.acquire() as connection:
                logger.debug(
                    f"Connection acquired - "
                    f"Pool: {self.pool.get_size()}/{self.pool.get_max_size()}"
                )
                yield connection
        except Exception as e:
            logger.error(f"Failed to acquire connection: {str(e)}")
            raise DatabaseException(f"Connection acquisition failed: {str(e)}") from e

    @asynccontextmanager
    async def get_transaction(self) -> AsyncIterator[asyncpg.Connection]:
        if not self._initialized:
            await self.initialize()

        async with self.pool.acquire() as connection:
            transaction = connection.transaction()
            try:
                logger.debug("Starting transaction...")
                await transaction.start()

                yield connection

                await transaction.commit()
                logger.debug("Transaction committed successfully")

            except Exception as e:
                logger.error(f"Transaction failed, rolling back: {str(e)}")
                await transaction.rollback()
                raise DatabaseException(f"Transaction failed: {str(e)}") from e

    async def fetch_all(self, query: str, *args) -> List:
        async with self.get_connection() as conn:
            results = await conn.fetch(query, *args)
            logger.debug(f"Query returned {len(results)} rows")
            return results

    async def fetch_one(self, query: str, *args) -> Optional[Any]:
        async with self.get_connection() as conn:
            result = await conn.fetchrow(query, *args)
            logger.debug(f"Query returned: {'1 row' if result else 'no rows'}")
            return result

    async def execute_query(self, query: str, *args) -> str:
        async with self.get_transaction() as conn:
            status = await conn.execute(query, *args)
            logger.info(f"Query executed successfully: {status}")
            return status

    async def close_pool(self) -> None:
        if self.pool:
            logger.info("Closing PostgreSQL connection pool...")
            await self.pool.close()
            self._initialized = False
            self.pool = None
            logger.info("PostgreSQL connection pool closed successfully")
        else:
            logger.debug("Connection pool already closed or not initialized")
