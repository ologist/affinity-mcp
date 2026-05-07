"""Affinity API HTTP client (v1)."""

import asyncio
import base64
import logging
from typing import Any

import httpx

from affinity_mcp.settings import settings

logger = logging.getLogger(__name__)

_BASE_V1 = "https://api.affinity.co"

# Shared client for connection pooling (one TLS handshake per process)
_http_v1 = httpx.AsyncClient(base_url=_BASE_V1, timeout=30)

# Rate limiting: max 10 concurrent outbound requests
_rate_limit = asyncio.Semaphore(10)


async def aclose() -> None:
    """Close shared HTTP client. Call on server shutdown."""
    await _http_v1.aclose()


def _auth_header() -> dict[str, str]:
    """Basic auth: empty username, API key as password."""
    token = base64.b64encode(f":{settings.affinity_api_key}".encode()).decode()
    return {"Authorization": f"Basic {token}"}


async def _get_v1(path: str, params: dict | None = None) -> Any:
    async with _rate_limit:
        try:
            r = await _http_v1.get(path, headers=_auth_header(), params=params)
            r.raise_for_status()
            return r.json()
        except httpx.HTTPStatusError as e:
            raise RuntimeError(f"Affinity API error: {e.response.status_code} on GET {path}") from None
        except httpx.RequestError:
            raise RuntimeError(f"Affinity API connection error on GET {path}") from None


async def _post_v1(path: str, body: dict) -> Any:
    logger.info("POST %s", path)
    async with _rate_limit:
        try:
            r = await _http_v1.post(path, headers=_auth_header(), json=body)
            r.raise_for_status()
            return r.json()
        except httpx.HTTPStatusError as e:
            raise RuntimeError(f"Affinity API error: {e.response.status_code} on POST {path}") from None
        except httpx.RequestError:
            raise RuntimeError(f"Affinity API connection error on POST {path}") from None


async def _put_v1(path: str, body: dict) -> Any:
    logger.info("PUT %s", path)
    async with _rate_limit:
        try:
            r = await _http_v1.put(path, headers=_auth_header(), json=body)
            r.raise_for_status()
            return r.json()
        except httpx.HTTPStatusError as e:
            raise RuntimeError(f"Affinity API error: {e.response.status_code} on PUT {path}") from None
        except httpx.RequestError:
            raise RuntimeError(f"Affinity API connection error on PUT {path}") from None


async def _delete_v1(path: str) -> Any:
    logger.warning("DELETE %s", path)
    async with _rate_limit:
        try:
            r = await _http_v1.delete(path, headers=_auth_header())
            r.raise_for_status()
            return r.json()
        except httpx.HTTPStatusError as e:
            raise RuntimeError(f"Affinity API error: {e.response.status_code} on DELETE {path}") from None
        except httpx.RequestError:
            raise RuntimeError(f"Affinity API connection error on DELETE {path}") from None


# ── Organizations (v1) ────────────────────────────────────────────────────────

async def search_organizations(term: str, with_interaction_dates: bool = False) -> Any:
    params: dict[str, Any] = {"term": term}
    if with_interaction_dates:
        params["with_interaction_dates"] = "true"
    data = await _get_v1("/organizations", params)
    return data.get("organizations", data) if isinstance(data, dict) else data


async def get_organization(org_id: int) -> Any:
    return await _get_v1(f"/organizations/{org_id}")


async def create_organization(name: str, domain: str | None = None, person_ids: list[int] | None = None) -> Any:
    body: dict[str, Any] = {"name": name}
    if domain:
        body["domain"] = domain
    if person_ids:
        body["person_ids"] = person_ids
    return await _post_v1("/organizations", body)


async def update_organization(org_id: int, fields: dict[str, Any]) -> Any:
    return await _put_v1(f"/organizations/{org_id}", fields)


async def delete_organization(org_id: int) -> Any:
    return await _delete_v1(f"/organizations/{org_id}")


# ── Persons (v1) ─────────────────────────────────────────────────────────────

async def search_persons(term: str, with_interaction_dates: bool = False) -> Any:
    params: dict[str, Any] = {"term": term}
    if with_interaction_dates:
        params["with_interaction_dates"] = "true"
    data = await _get_v1("/persons", params)
    return data.get("persons", data) if isinstance(data, dict) else data


async def get_person(person_id: int) -> Any:
    return await _get_v1(f"/persons/{person_id}")


async def create_person(
    first_name: str,
    last_name: str,
    emails: list[str] | None = None,
    organization_ids: list[int] | None = None,
) -> Any:
    body: dict[str, Any] = {"first_name": first_name, "last_name": last_name}
    if emails:
        body["emails"] = emails
    if organization_ids:
        body["organization_ids"] = organization_ids
    return await _post_v1("/persons", body)


async def update_person(person_id: int, fields: dict[str, Any]) -> Any:
    return await _put_v1(f"/persons/{person_id}", fields)


async def delete_person(person_id: int) -> Any:
    return await _delete_v1(f"/persons/{person_id}")


# ── Opportunities (v1) ────────────────────────────────────────────────────────

async def get_opportunities(list_id: int | None = None) -> Any:
    params = {}
    if list_id:
        params["list_id"] = list_id
    return await _get_v1("/opportunities", params or None)


async def get_opportunity(opportunity_id: int) -> Any:
    return await _get_v1(f"/opportunities/{opportunity_id}")


async def create_opportunity(name: str, list_id: int) -> Any:
    return await _post_v1("/opportunities", {"name": name, "list_id": list_id})


async def update_opportunity(opportunity_id: int, fields: dict[str, Any]) -> Any:
    return await _put_v1(f"/opportunities/{opportunity_id}", fields)


async def delete_opportunity(opportunity_id: int) -> Any:
    return await _delete_v1(f"/opportunities/{opportunity_id}")


# ── Lists (v1) ────────────────────────────────────────────────────────────────

async def get_lists() -> Any:
    return await _get_v1("/lists")


async def get_list(list_id: int) -> Any:
    return await _get_v1(f"/lists/{list_id}")


async def get_list_entries(list_id: int, page_size: int = 100, page_token: str | None = None) -> Any:
    params: dict[str, Any] = {"page_size": page_size}
    if page_token:
        params["page_token"] = page_token
    return await _get_v1(f"/lists/{list_id}/list-entries", params)


async def create_list_entry(list_id: int, entity_id: int) -> Any:
    return await _post_v1(f"/lists/{list_id}/list-entries", {"entity_id": entity_id})


async def delete_list_entry(list_id: int, list_entry_id: int) -> Any:
    return await _delete_v1(f"/lists/{list_id}/list-entries/{list_entry_id}")


# ── Notes (v1) ────────────────────────────────────────────────────────────────

async def get_notes(
    person_id: int | None = None,
    organization_id: int | None = None,
    opportunity_id: int | None = None,
    creator_id: int | None = None,
    page_size: int = 500,
    page_token: str | None = None,
) -> Any:
    params: dict[str, Any] = {"page_size": page_size}
    if person_id:
        params["person_id"] = person_id
    if organization_id:
        params["organization_id"] = organization_id
    if opportunity_id:
        params["opportunity_id"] = opportunity_id
    if creator_id:
        params["creator_id"] = creator_id
    if page_token:
        params["page_token"] = page_token
    data = await _get_v1("/notes", params)
    # Normalize plain array → paginated dict for consistency with get_list_entries
    if isinstance(data, list):
        return {"notes": data, "next_page_token": None}
    return data


async def create_note(
    content: str,
    person_ids: list[int] | None = None,
    organization_id: int | None = None,
    opportunity_id: int | None = None,
    creator_id: int | None = None,
) -> Any:
    body: dict[str, Any] = {"content": content}
    if person_ids:
        body["person_ids"] = person_ids
    if organization_id:
        body["organization_id"] = organization_id
    if opportunity_id:
        body["opportunity_id"] = opportunity_id
    if creator_id:
        body["creator_id"] = creator_id
    return await _post_v1("/notes", body)


async def update_note(note_id: int, content: str) -> Any:
    return await _put_v1(f"/notes/{note_id}", {"content": content})


async def delete_note(note_id: int) -> Any:
    return await _delete_v1(f"/notes/{note_id}")


# ── Fields (v1) ───────────────────────────────────────────────────────────────

async def get_fields(list_id: int | None = None) -> Any:
    params = {}
    if list_id:
        params["list_id"] = list_id
    return await _get_v1("/fields", params or None)


# ── Field Values (v1) ─────────────────────────────────────────────────────────

async def get_field_values(
    person_id: int | None = None,
    organization_id: int | None = None,
    opportunity_id: int | None = None,
    list_entry_id: int | None = None,
) -> Any:
    params: dict[str, Any] = {}
    if person_id:
        params["person_id"] = person_id
    if organization_id:
        params["organization_id"] = organization_id
    if opportunity_id:
        params["opportunity_id"] = opportunity_id
    if list_entry_id:
        params["list_entry_id"] = list_entry_id
    return await _get_v1("/field-values", params or None)


async def create_field_value(field_id: int, entity_id: int, value: Any, list_entry_id: int | None = None) -> Any:
    body: dict[str, Any] = {"field_id": field_id, "entity_id": entity_id, "value": value}
    if list_entry_id:
        body["list_entry_id"] = list_entry_id
    return await _post_v1("/field-values", body)


async def update_field_value(field_value_id: int, value: Any) -> Any:
    return await _put_v1(f"/field-values/{field_value_id}", {"value": value})


async def delete_field_value(field_value_id: int) -> Any:
    return await _delete_v1(f"/field-values/{field_value_id}")


# ── Relationship Strengths (v1) ───────────────────────────────────────────────

async def get_relationship_strengths(
    internal_id: int,
    external_id: int | None = None,
    type_: int | None = None,
) -> Any:
    params: dict[str, Any] = {"internal_id": internal_id}
    if external_id:
        params["external_id"] = external_id
    if type_:
        params["type"] = type_
    return await _get_v1("/relationship-strengths", params)
