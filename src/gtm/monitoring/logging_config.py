"""Structured JSON logging configuration."""

from __future__ import annotations

import logging
import sys

from gtm.config import Settings


def configure_logging(settings: Settings) -> None:
    """Set up structured logging for the application."""
    level = getattr(logging, settings.log_level.upper(), logging.INFO)

    if settings.environment == "production":
        # JSON format for production (easy to parse in log aggregators)
        fmt = (
            '{"time":"%(asctime)s","level":"%(levelname)s",'
            '"logger":"%(name)s","message":"%(message)s"}'
        )
    else:
        fmt = "%(asctime)s %(levelname)-8s %(name)s | %(message)s"

    logging.basicConfig(
        level=level,
        format=fmt,
        datefmt="%Y-%m-%dT%H:%M:%S",
        stream=sys.stdout,
        force=True,
    )

    # Quiet noisy libraries
    for lib in ("httpx", "httpcore", "urllib3", "boto3", "botocore", "s3transfer"):
        logging.getLogger(lib).setLevel(logging.WARNING)
