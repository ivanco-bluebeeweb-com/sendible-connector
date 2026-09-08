"""Resource operation handlers for Sendible Connector."""
from __future__ import annotations
from typing import Any
from app import chat
from imperal_sdk import ActionResult
from sendible_client import SendibleClient
from handlers_connection import resolve_connection
from schemas import (
    ProfileRecord, ProfileList, ListProfilesParams, GetProfileParams,
    MessageRecord, MessageList, ListMessagesParams, GetMessageParams,
    CreateMessageParams, UpdateMessageParams, DeleteMessageParams,
    ActivityRecord, ActivityList, ListActivitiesParams,
    SocialHealthAuditResult, ConnectionIdParams, DeleteResult
)

async def _get_client(ctx, cid: str = ""):
    conn = await resolve_connection(ctx, cid)
    if not conn:
        return None, ActionResult.error("No active Sendible connection", code="UNAUTHORIZED")
    return SendibleClient(access_token=conn.get("access_token") or conn.get("api_key", ""), base_url=conn.get("base_url", "")), None

@chat.function(
    "list_profiles",
    "List social profiles (channels) connected in Sendible.",
    action_type="read",
)
async def list_profiles(ctx, params: ListProfilesParams) -> ActionResult[ProfileList]:
    client, err = await _get_client(ctx, params.connection_id)
    if err: return err
    try:
        raw_items = await client.list_profiles(limit=params.limit)
        items = [
            ProfileRecord(
                id=str(p.get("id", p.get("profile_id", ""))),
                name=str(p.get("name", p.get("title", "Unnamed Profile"))),
                service=str(p.get("service", p.get("type", "social"))),
                status=str(p.get("status", "active")),
                avatar_url=p.get("avatar_url", p.get("image_url")),
                raw=p
            )
            for p in raw_items
        ]
        return ActionResult.success(ProfileList(profiles=items, total=len(items)), summary=f"Found {len(items)} Sendible profiles.")
    except Exception as e:
        return ActionResult.error(f"Failed to list profiles: {e}")

@chat.function(
    "get_profile",
    "Get details of a single Sendible social profile.",
    action_type="read",
)
async def get_profile(ctx, params: GetProfileParams) -> ActionResult[ProfileRecord]:
    client, err = await _get_client(ctx, params.connection_id)
    if err: return err
    try:
        p = await client.get_profile(params.profile_id)
        rec = ProfileRecord(
            id=str(p.get("id", params.profile_id)),
            name=str(p.get("name", p.get("title", "Unnamed Profile"))),
            service=str(p.get("service", p.get("type", "social"))),
            status=str(p.get("status", "active")),
            avatar_url=p.get("avatar_url", p.get("image_url")),
            raw=p
        )
        return ActionResult.success(rec, summary=f"Retrieved profile {rec.name}")
    except Exception as e:
        return ActionResult.error(f"Failed to get profile: {e}")

@chat.function(
    "list_messages",
    "List social messages/posts from Sendible by status (scheduled, sent, draft).",
    action_type="read",
)
async def list_messages(ctx, params: ListMessagesParams) -> ActionResult[MessageList]:
    client, err = await _get_client(ctx, params.connection_id)
    if err: return err
    try:
        raw_items = await client.list_messages(status=params.status, limit=params.limit)
        items = [
            MessageRecord(
                id=str(m.get("id", m.get("message_id", ""))),
                content=str(m.get("content", m.get("message", ""))),
                status=str(m.get("status", params.status)),
                scheduled_for=m.get("scheduled_for", m.get("send_date")),
                profile_ids=[str(pid) for pid in m.get("profiles", [])],
                raw=m
            )
            for m in raw_items
        ]
        return ActionResult.success(MessageList(messages=items, total=len(items)), summary=f"Found {len(items)} {params.status} messages.")
    except Exception as e:
        return ActionResult.error(f"Failed to list messages: {e}")

@chat.function(
    "get_message",
    "Get details of a specific social message/post in Sendible.",
    action_type="read",
)
async def get_message(ctx, params: GetMessageParams) -> ActionResult[MessageRecord]:
    client, err = await _get_client(ctx, params.connection_id)
    if err: return err
    try:
        m = await client.get_message(params.message_id)
        rec = MessageRecord(
            id=str(m.get("id", params.message_id)),
            content=str(m.get("content", m.get("message", ""))),
            status=str(m.get("status", "active")),
            scheduled_for=m.get("scheduled_for"),
            profile_ids=[str(pid) for pid in m.get("profiles", [])],
            raw=m
        )
        return ActionResult.success(rec, summary=f"Retrieved message {rec.id}")
    except Exception as e:
        return ActionResult.error(f"Failed to get message: {e}")

@chat.function(
    "create_message",
    "Create or schedule a new social post across Sendible profiles.",
    action_type="write",
)
async def create_message(ctx, params: CreateMessageParams) -> ActionResult[MessageRecord]:
    client, err = await _get_client(ctx, params.connection_id)
    if err: return err
    try:
        m = await client.create_message(
            content=params.content,
            profile_ids=params.profile_ids,
            scheduled_for=params.scheduled_for,
            image_url=params.image_url
        )
        rec = MessageRecord(
            id=str(m.get("id", m.get("message_id", "created"))),
            content=params.content,
            status="scheduled" if params.scheduled_for else "published",
            scheduled_for=params.scheduled_for,
            profile_ids=params.profile_ids,
            raw=m
        )
        return ActionResult.success(rec, summary=f"Created social post {rec.id}")
    except Exception as e:
        return ActionResult.error(f"Failed to create message: {e}")

@chat.function(
    "update_message",
    "Update an existing scheduled post in Sendible.",
    action_type="write",
)
async def update_message(ctx, params: UpdateMessageParams) -> ActionResult[MessageRecord]:
    client, err = await _get_client(ctx, params.connection_id)
    if err: return err
    try:
        m = await client.update_message(
            message_id=params.message_id,
            content=params.content,
            scheduled_for=params.scheduled_for
        )
        rec = MessageRecord(
            id=params.message_id,
            content=params.content or "",
            status="updated",
            scheduled_for=params.scheduled_for,
            raw=m
        )
        return ActionResult.success(rec, summary=f"Updated message {params.message_id}")
    except Exception as e:
        return ActionResult.error(f"Failed to update message: {e}")

@chat.function(
    "delete_message",
    "Permanently delete a scheduled or draft message in Sendible.",
    action_type="destructive",
    )
async def delete_message(ctx, params: DeleteMessageParams) -> ActionResult[DeleteResult]:
    client, err = await _get_client(ctx, params.connection_id)
    if err: return err
    try:
        await client.delete_message(params.message_id)
        return ActionResult.success(DeleteResult(success=True, message=f"Message {params.message_id} deleted."), summary=f"Deleted message {params.message_id}")
    except Exception as e:
        return ActionResult.error(f"Failed to delete message: {e}")

@chat.function(
    "list_activities",
    "List social stream activity and mentions from Sendible.",
    action_type="read",
)
async def list_activities(ctx, params: ListActivitiesParams) -> ActionResult[ActivityList]:
    client, err = await _get_client(ctx, params.connection_id)
    if err: return err
    try:
        raw_items = await client.list_activities(limit=params.limit)
        items = [
            ActivityRecord(
                id=str(a.get("id", "")),
                type=str(a.get("type", "mention")),
                sender=str(a.get("sender", a.get("user", "unknown"))),
                content=str(a.get("content", a.get("text", ""))),
                timestamp=str(a.get("timestamp", a.get("created_at", ""))),
                raw=a
            )
            for a in raw_items
        ]
        return ActionResult.success(ActivityList(activities=items, total=len(items)), summary=f"Found {len(items)} activity items.")
    except Exception as e:
        return ActionResult.error(f"Failed to list activities: {e}")

@chat.function(
    "audit_social_health",
    "Audit health of connected Sendible social accounts and scheduled message queues.",
    action_type="read",
)
async def audit_social_health(ctx, params: ConnectionIdParams) -> ActionResult[SocialHealthAuditResult]:
    client, err = await _get_client(ctx, params.connection_id)
    if err: return err
    try:
        profiles = await client.list_profiles(limit=100)
        scheduled = await client.list_messages(status="scheduled", limit=100)
        undelivered = await client.list_messages(status="undelivered", limit=100)
        res = SocialHealthAuditResult(
            connected=True,
            total_profiles=len(profiles),
            scheduled_messages=len(scheduled),
            undelivered_messages=len(undelivered),
            health_status="healthy" if len(undelivered) == 0 else "attention_needed",
            details={
                "profiles_count": len(profiles),
                "scheduled_count": len(scheduled),
                "undelivered_count": len(undelivered)
            }
        )
        return ActionResult.success(res, summary=f"Sendible health: {res.health_status} ({len(profiles)} profiles, {len(scheduled)} scheduled, {len(undelivered)} errors)")
    except Exception as e:
        return ActionResult.error(f"Health audit failed: {e}")
