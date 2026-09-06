"""Pydantic schemas for Sendible Connector (C31. Social Media Management)."""
from __future__ import annotations
from typing import Any, Optional, List, Dict
from pydantic import BaseModel, Field

class NoParams(BaseModel):
    """Empty parameters model."""
    pass

class ConnectParams(BaseModel):
    label: str = Field(default="", description="Friendly connection label, e.g. Acme Social.")
    access_token: str = Field(description="Sendible OAuth 2.0 Access Token.")
    base_url: str = Field(default="https://api.sendible.com/api/v1", description="Sendible API base URL.")

class ConnectionIdParams(BaseModel):
    connection_id: str = Field(default="", description="Connection identifier (empty uses active connection).")

class ConnectionRecord(BaseModel):
    id: str
    label: str
    masked_key: str
    base_url: str
    is_active: bool

class ConnectionList(BaseModel):
    connections: list[ConnectionRecord]
    total: int

class DeleteResult(BaseModel):
    success: bool
    message: str

class ProfileRecord(BaseModel):
    id: str
    name: str
    service: str
    status: str
    avatar_url: Optional[str] = None
    raw: Dict[str, Any] = Field(default_factory=dict)

class ProfileList(BaseModel):
    profiles: list[ProfileRecord]
    total: int

class ListProfilesParams(BaseModel):
    connection_id: str = Field(default="", description="Optional connection ID.")
    limit: int = Field(default=20, ge=1, le=100, description="Max profiles to return.")

class GetProfileParams(BaseModel):
    connection_id: str = Field(default="", description="Optional connection ID.")
    profile_id: str = Field(description="Sendible profile ID.")

class MessageRecord(BaseModel):
    id: str
    content: str
    status: str
    scheduled_for: Optional[str] = None
    profile_ids: list[str] = Field(default_factory=list)
    raw: Dict[str, Any] = Field(default_factory=dict)

class MessageList(BaseModel):
    messages: list[MessageRecord]
    total: int

class ListMessagesParams(BaseModel):
    connection_id: str = Field(default="", description="Optional connection ID.")
    status: str = Field(default="scheduled", description="Status filter: scheduled, sent, draft, undelivered.")
    limit: int = Field(default=20, ge=1, le=100, description="Max messages to return.")

class GetMessageParams(BaseModel):
    connection_id: str = Field(default="", description="Optional connection ID.")
    message_id: str = Field(description="Sendible message ID.")

class CreateMessageParams(BaseModel):
    connection_id: str = Field(default="", description="Optional connection ID.")
    content: str = Field(description="Social post body text.")
    profile_ids: list[str] = Field(description="List of profile IDs to publish to.")
    scheduled_for: Optional[str] = Field(default=None, description="ISO timestamp for scheduled publication.")
    image_url: Optional[str] = Field(default=None, description="Optional image URL to attach.")

class UpdateMessageParams(BaseModel):
    connection_id: str = Field(default="", description="Optional connection ID.")
    message_id: str = Field(description="Sendible message ID to update.")
    content: Optional[str] = Field(default=None, description="Updated message text.")
    scheduled_for: Optional[str] = Field(default=None, description="Updated schedule time.")

class DeleteMessageParams(BaseModel):
    connection_id: str = Field(default="", description="Optional connection ID.")
    message_id: str = Field(description="Sendible message ID to delete.")

class ActivityRecord(BaseModel):
    id: str
    type: str
    sender: str
    content: str
    timestamp: str
    raw: Dict[str, Any] = Field(default_factory=dict)

class ActivityList(BaseModel):
    activities: list[ActivityRecord]
    total: int

class ListActivitiesParams(BaseModel):
    connection_id: str = Field(default="", description="Optional connection ID.")
    limit: int = Field(default=20, ge=1, le=100, description="Max activity events to return.")

class SocialHealthAuditResult(BaseModel):
    connected: bool
    total_profiles: int
    scheduled_messages: int
    undelivered_messages: int
    health_status: str
    details: Dict[str, Any] = Field(default_factory=dict)
