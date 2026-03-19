"""S3 / MinIO artifact storage."""

from __future__ import annotations

import json
import logging

import boto3
from botocore.config import Config as BotoConfig

from gtm.config import Settings

logger = logging.getLogger(__name__)

_client = None
_bucket: str = ""


def init_s3(settings: Settings) -> None:
    """Initialize the S3 client and ensure the bucket exists."""
    global _client, _bucket

    is_minio = bool(settings.aws_endpoint_url)

    _client = boto3.client(
        "s3",
        endpoint_url=settings.aws_endpoint_url or None,
        aws_access_key_id=settings.aws_access_key_id or None,
        aws_secret_access_key=settings.aws_secret_access_key or None,
        region_name=settings.aws_region,
        config=BotoConfig(signature_version="s3v4"),
    )
    _bucket = settings.s3_bucket

    try:
        _client.head_bucket(Bucket=_bucket)
    except Exception:
        try:
            _client.create_bucket(Bucket=_bucket)
            logger.info("Created S3 bucket: %s", _bucket)
        except Exception as e:
            logger.error("Could not create/access S3 bucket %s: %s", _bucket, e)

    # Block all public access on production S3 (skip for MinIO which may not support it)
    if not is_minio:
        try:
            _client.put_public_access_block(
                Bucket=_bucket,
                PublicAccessBlockConfiguration={
                    "BlockPublicAcls": True,
                    "IgnorePublicAcls": True,
                    "BlockPublicPolicy": True,
                    "RestrictPublicBuckets": True,
                },
            )
            logger.info("Public access block applied to bucket: %s", _bucket)
        except Exception as e:
            logger.warning("Could not set public access block on %s: %s", _bucket, e)


def save_artifact(job_id: str, filename: str, data: str | bytes, content_type: str = "application/json") -> None:
    """Save an artifact to S3."""
    if _client is None:
        logger.warning("S3 not initialized — skipping artifact save")
        return

    key = f"analyses/{job_id}/{filename}"
    body = data if isinstance(data, bytes) else data.encode("utf-8")

    try:
        _client.put_object(
            Bucket=_bucket,
            Key=key,
            Body=body,
            ContentType=content_type,
            ServerSideEncryption="AES256",  # SSE-S3 encryption at rest
        )
    except Exception as e:
        logger.error("Failed to save artifact %s: %s", key, e)


def save_job_artifacts(job_id: str, results: dict) -> None:
    """Save all job artifacts to S3."""
    # Complete results
    save_artifact(job_id, "complete_results.json", json.dumps(results, indent=2))

    # Copy kit as separate artifact
    if "copy_kit" in results:
        save_artifact(job_id, "copy_kit.json", json.dumps(results["copy_kit"], indent=2))

    # Experiments as separate artifact
    if "experiments" in results:
        save_artifact(
            job_id, "experiments.json", json.dumps(results["experiments"], indent=2)
        )
