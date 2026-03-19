"""Health checker for use outside the API (e.g., from Celery workers)."""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


class HealthChecker:
    """Checks connectivity to all dependent services."""

    @staticmethod
    def check_database() -> bool:
        try:
            from gtm.storage.database import get_engine

            engine = get_engine()
            if engine is None:
                return False
            with engine.connect() as conn:
                conn.exec_driver_sql("SELECT 1")
            return True
        except Exception as e:
            logger.warning("Database health check failed: %s", e)
            return False

    @staticmethod
    def check_redis() -> bool:
        try:
            from gtm.storage.redis_client import get_redis

            get_redis().ping()
            return True
        except Exception as e:
            logger.warning("Redis health check failed: %s", e)
            return False

    @staticmethod
    def check_s3() -> bool:
        try:
            from gtm.storage.s3 import _client, _bucket

            if _client is None:
                return False
            _client.head_bucket(Bucket=_bucket)
            return True
        except Exception as e:
            logger.warning("S3 health check failed: %s", e)
            return False

    def check_all(self) -> dict[str, bool]:
        return {
            "database": self.check_database(),
            "redis": self.check_redis(),
            "s3": self.check_s3(),
        }

    def is_healthy(self) -> bool:
        checks = self.check_all()
        return checks["database"] and checks["redis"]
