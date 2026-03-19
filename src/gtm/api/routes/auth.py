"""API key management endpoints."""

from __future__ import annotations

import hashlib
import secrets
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from gtm.api.deps import get_current_tenant, get_db
from gtm.models.user import APIKey

router = APIRouter(prefix="/auth", tags=["auth"])


class CreateKeyRequest(BaseModel):
    name: str


class CreateKeyResponse(BaseModel):
    key_id: str
    api_key: str
    name: str


class KeyListItem(BaseModel):
    key_id: str
    name: str
    is_active: bool
    last_used_at: str | None = None
    created_at: str | None = None


@router.post("/keys", response_model=CreateKeyResponse)
async def create_api_key(
    request: CreateKeyRequest,
    tenant_id: Annotated[str, Depends(get_current_tenant)],
    db: Annotated[Session, Depends(get_db)],
):
    """Create a new API key. The raw key is only shown once."""
    raw_key = f"gtm_{secrets.token_urlsafe(32)}"
    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
    key_id = str(uuid.uuid4())

    api_key = APIKey(
        id=key_id,
        user_id=tenant_id,
        key_hash=key_hash,
        name=request.name,
    )
    db.add(api_key)
    db.commit()

    return CreateKeyResponse(key_id=key_id, api_key=raw_key, name=request.name)


@router.get("/keys", response_model=list[KeyListItem])
async def list_api_keys(
    tenant_id: Annotated[str, Depends(get_current_tenant)],
    db: Annotated[Session, Depends(get_db)],
):
    """List all API keys for the authenticated user."""
    keys = db.query(APIKey).filter_by(user_id=tenant_id).all()
    return [
        KeyListItem(
            key_id=k.id,
            name=k.name,
            is_active=k.is_active,
            last_used_at=k.last_used_at.isoformat() if k.last_used_at else None,
            created_at=k.created_at.isoformat() if k.created_at else None,
        )
        for k in keys
    ]


@router.delete("/keys/{key_id}")
async def revoke_api_key(
    key_id: str,
    tenant_id: Annotated[str, Depends(get_current_tenant)],
    db: Annotated[Session, Depends(get_db)],
):
    """Revoke (deactivate) an API key."""
    api_key = db.query(APIKey).filter_by(id=key_id, user_id=tenant_id).first()
    if not api_key:
        raise HTTPException(status_code=404, detail="API key not found")

    api_key.is_active = False
    db.commit()
    return {"status": "revoked"}
