"""Affinity MCP Server - FastMCP 기반 Affinity CRM 연동 서버."""

from contextlib import asynccontextmanager
from typing import Any

from fastmcp import FastMCP

from affinity_mcp import client
from affinity_mcp.settings import settings


def _check_write_allowed() -> None:
    if settings.read_only:
        raise PermissionError("서버가 읽기 전용 모드입니다. 쓰기를 허용하려면 READ_ONLY=false 로 설정하세요.")


@asynccontextmanager
async def _lifespan(app: FastMCP):
    yield
    await client.aclose()


mcp = FastMCP(
    "Affinity CRM",
    instructions="""
    이 서버는 Affinity CRM의 데이터를 조회하고 관리합니다.
    조직(Organization), 인물(Person), 기회(Opportunity), 리스트(List), 노트(Note),
    필드값(Field Value) 등을 다룰 수 있습니다.
    """,
    lifespan=_lifespan,
)


# ── Organizations ─────────────────────────────────────────────────────────────

@mcp.tool()
async def search_organizations(term: str, with_interaction_dates: bool = False) -> list[dict[str, Any]]:
    """
    이름 또는 도메인으로 조직(회사)을 검색합니다.

    Args:
        term: 검색어 (회사명, 도메인 등)
        with_interaction_dates: True이면 마지막 상호작용 날짜 포함

    Returns:
        검색된 조직 목록
    """
    return await client.search_organizations(term, with_interaction_dates)


@mcp.tool()
async def get_organization(org_id: int) -> dict[str, Any]:
    """
    조직 ID로 조직 상세 정보를 조회합니다.

    Args:
        org_id: Affinity 조직 ID

    Returns:
        조직 상세 정보 (이름, 도메인, 연결된 인물, 필드값 등)
    """
    return await client.get_organization(org_id)


@mcp.tool()
async def create_organization(
    name: str,
    domain: str | None = None,
    person_ids: list[int] | None = None,
) -> dict[str, Any]:
    """
    새 조직을 생성합니다.

    Args:
        name: 조직명
        domain: 도메인 (예: example.com)
        person_ids: 연결할 인물 ID 목록

    Returns:
        생성된 조직 정보
    """
    _check_write_allowed()
    return await client.create_organization(name, domain, person_ids)


@mcp.tool()
async def update_organization(org_id: int, fields: dict[str, Any]) -> dict[str, Any]:
    """
    조직 정보를 수정합니다.

    Args:
        org_id: 수정할 조직 ID
        fields: 수정할 필드 딕셔너리 (예: {"name": "새이름", "domain": "new.com"})

    Returns:
        수정된 조직 정보
    """
    _check_write_allowed()
    return await client.update_organization(org_id, fields)


@mcp.tool()
async def delete_organization(org_id: int) -> dict[str, Any]:
    """
    조직을 삭제합니다.

    Args:
        org_id: 삭제할 조직 ID

    Returns:
        삭제 결과
    """
    _check_write_allowed()
    return await client.delete_organization(org_id)


# ── Persons ───────────────────────────────────────────────────────────────────

@mcp.tool()
async def search_persons(term: str, with_interaction_dates: bool = False) -> list[dict[str, Any]]:
    """
    이름 또는 이메일로 인물을 검색합니다.

    Args:
        term: 검색어 (이름, 이메일 등)
        with_interaction_dates: True이면 마지막 상호작용 날짜 포함

    Returns:
        검색된 인물 목록
    """
    return await client.search_persons(term, with_interaction_dates)


@mcp.tool()
async def get_person(person_id: int) -> dict[str, Any]:
    """
    인물 ID로 인물 상세 정보를 조회합니다.

    Args:
        person_id: Affinity 인물 ID

    Returns:
        인물 상세 정보 (이름, 이메일, 소속 조직, 필드값 등)
    """
    return await client.get_person(person_id)


@mcp.tool()
async def create_person(
    first_name: str,
    last_name: str,
    emails: list[str] | None = None,
    organization_ids: list[int] | None = None,
) -> dict[str, Any]:
    """
    새 인물을 생성합니다.

    Args:
        first_name: 이름
        last_name: 성
        emails: 이메일 주소 목록
        organization_ids: 연결할 조직 ID 목록

    Returns:
        생성된 인물 정보
    """
    _check_write_allowed()
    return await client.create_person(first_name, last_name, emails, organization_ids)


@mcp.tool()
async def update_person(person_id: int, fields: dict[str, Any]) -> dict[str, Any]:
    """
    인물 정보를 수정합니다.

    Args:
        person_id: 수정할 인물 ID
        fields: 수정할 필드 딕셔너리 (예: {"first_name": "길동", "emails": ["a@b.com"]})

    Returns:
        수정된 인물 정보
    """
    _check_write_allowed()
    return await client.update_person(person_id, fields)


@mcp.tool()
async def delete_person(person_id: int) -> dict[str, Any]:
    """
    인물을 삭제합니다.

    Args:
        person_id: 삭제할 인물 ID

    Returns:
        삭제 결과
    """
    _check_write_allowed()
    return await client.delete_person(person_id)


# ── Opportunities ─────────────────────────────────────────────────────────────

@mcp.tool()
async def get_opportunities(list_id: int | None = None) -> list[dict[str, Any]]:
    """
    기회(딜) 목록을 조회합니다.

    Args:
        list_id: 특정 리스트의 기회만 조회할 때 사용

    Returns:
        기회 목록
    """
    return await client.get_opportunities(list_id)


@mcp.tool()
async def get_opportunity(opportunity_id: int) -> dict[str, Any]:
    """
    기회 ID로 기회 상세 정보를 조회합니다.

    Args:
        opportunity_id: Affinity 기회 ID

    Returns:
        기회 상세 정보
    """
    return await client.get_opportunity(opportunity_id)


@mcp.tool()
async def create_opportunity(name: str, list_id: int) -> dict[str, Any]:
    """
    새 기회(딜)를 생성합니다.

    Args:
        name: 기회명
        list_id: 기회를 추가할 리스트 ID

    Returns:
        생성된 기회 정보
    """
    _check_write_allowed()
    return await client.create_opportunity(name, list_id)


@mcp.tool()
async def update_opportunity(opportunity_id: int, fields: dict[str, Any]) -> dict[str, Any]:
    """
    기회 정보를 수정합니다.

    Args:
        opportunity_id: 수정할 기회 ID
        fields: 수정할 필드 딕셔너리 (예: {"name": "새 딜명"})

    Returns:
        수정된 기회 정보
    """
    _check_write_allowed()
    return await client.update_opportunity(opportunity_id, fields)


@mcp.tool()
async def delete_opportunity(opportunity_id: int) -> dict[str, Any]:
    """
    기회를 삭제합니다.

    Args:
        opportunity_id: 삭제할 기회 ID

    Returns:
        삭제 결과
    """
    _check_write_allowed()
    return await client.delete_opportunity(opportunity_id)


# ── Lists ─────────────────────────────────────────────────────────────────────

@mcp.tool()
async def get_lists() -> list[dict[str, Any]]:
    """
    Affinity의 모든 리스트를 조회합니다.

    Returns:
        리스트 목록 (이름, 타입, ID 등)
    """
    return await client.get_lists()


@mcp.tool()
async def get_list(list_id: int) -> dict[str, Any]:
    """
    리스트 ID로 리스트 상세 정보를 조회합니다.

    Args:
        list_id: Affinity 리스트 ID

    Returns:
        리스트 상세 정보 (필드 포함)
    """
    return await client.get_list(list_id)


@mcp.tool()
async def get_list_entries(
    list_id: int,
    page_size: int = 100,
    page_token: str | None = None,
) -> dict[str, Any]:
    """
    리스트의 항목(엔트리) 목록을 조회합니다.

    Args:
        list_id: 조회할 리스트 ID
        page_size: 한 페이지당 항목 수 (기본 100, 최대 500)
        page_token: 다음 페이지 토큰 (이전 응답의 next_page_token 값)

    Returns:
        list_entries(항목 목록)와 next_page_token 포함 딕셔너리
    """
    return await client.get_list_entries(list_id, page_size, page_token)


@mcp.tool()
async def create_list_entry(list_id: int, entity_id: int) -> dict[str, Any]:
    """
    리스트에 기존 엔티티(조직/인물/기회)를 추가합니다.

    Args:
        list_id: 추가할 리스트 ID
        entity_id: 추가할 엔티티 ID (조직, 인물, 기회 ID)

    Returns:
        생성된 리스트 엔트리 정보
    """
    _check_write_allowed()
    return await client.create_list_entry(list_id, entity_id)


@mcp.tool()
async def delete_list_entry(list_id: int, list_entry_id: int) -> dict[str, Any]:
    """
    리스트에서 엔트리를 제거합니다.

    Args:
        list_id: 리스트 ID
        list_entry_id: 제거할 리스트 엔트리 ID

    Returns:
        삭제 결과
    """
    _check_write_allowed()
    return await client.delete_list_entry(list_id, list_entry_id)


# ── Notes ─────────────────────────────────────────────────────────────────────

@mcp.tool()
async def get_notes(
    person_id: int | None = None,
    organization_id: int | None = None,
    opportunity_id: int | None = None,
) -> list[dict[str, Any]]:
    """
    노트를 조회합니다. 조건 없이 호출하면 전체 노트를 반환합니다.

    Args:
        person_id: 특정 인물의 노트만 조회
        organization_id: 특정 조직의 노트만 조회
        opportunity_id: 특정 기회의 노트만 조회

    Returns:
        노트 목록 (내용, 작성자, 날짜 등)
    """
    return await client.get_notes(person_id, organization_id, opportunity_id)


@mcp.tool()
async def create_note(
    content: str,
    person_ids: list[int] | None = None,
    organization_id: int | None = None,
    opportunity_id: int | None = None,
) -> dict[str, Any]:
    """
    새 노트를 작성합니다.

    Args:
        content: 노트 내용
        person_ids: 연결할 인물 ID 목록
        organization_id: 연결할 조직 ID
        opportunity_id: 연결할 기회 ID

    Returns:
        생성된 노트 정보
    """
    _check_write_allowed()
    return await client.create_note(content, person_ids, organization_id, opportunity_id)


@mcp.tool()
async def update_note(note_id: int, content: str) -> dict[str, Any]:
    """
    노트 내용을 수정합니다.

    Args:
        note_id: 수정할 노트 ID
        content: 새 노트 내용

    Returns:
        수정된 노트 정보
    """
    _check_write_allowed()
    return await client.update_note(note_id, content)


@mcp.tool()
async def delete_note(note_id: int) -> dict[str, Any]:
    """
    노트를 삭제합니다.

    Args:
        note_id: 삭제할 노트 ID

    Returns:
        삭제 결과
    """
    _check_write_allowed()
    return await client.delete_note(note_id)


# ── Fields & Field Values ─────────────────────────────────────────────────────

@mcp.tool()
async def get_fields(list_id: int | None = None) -> list[dict[str, Any]]:
    """
    Affinity의 필드 목록을 조회합니다.

    Args:
        list_id: 특정 리스트의 필드만 조회할 때 사용

    Returns:
        필드 목록 (ID, 이름, 타입, 허용값 등)
    """
    return await client.get_fields(list_id)


@mcp.tool()
async def get_field_values(
    person_id: int | None = None,
    organization_id: int | None = None,
    opportunity_id: int | None = None,
    list_entry_id: int | None = None,
) -> list[dict[str, Any]]:
    """
    엔티티의 필드값을 조회합니다.

    Args:
        person_id: 인물 ID
        organization_id: 조직 ID
        opportunity_id: 기회 ID
        list_entry_id: 리스트 엔트리 ID

    Returns:
        필드값 목록 (field_id, value, 엔티티 연결 정보 등)
    """
    return await client.get_field_values(person_id, organization_id, opportunity_id, list_entry_id)


@mcp.tool()
async def create_field_value(
    field_id: int,
    entity_id: int,
    value: Any,
    list_entry_id: int | None = None,
) -> dict[str, Any]:
    """
    엔티티에 필드값을 추가합니다.

    Args:
        field_id: 필드 ID (get_fields로 조회)
        entity_id: 값을 설정할 엔티티(조직/인물/기회) ID
        value: 설정할 값 (필드 타입에 따라 문자열, 숫자, 날짜 등)
        list_entry_id: 리스트 엔트리 ID (리스트 전용 필드일 때 필요)

    Returns:
        생성된 필드값 정보
    """
    _check_write_allowed()
    return await client.create_field_value(field_id, entity_id, value, list_entry_id)


@mcp.tool()
async def update_field_value(field_value_id: int, value: Any) -> dict[str, Any]:
    """
    기존 필드값을 수정합니다.

    Args:
        field_value_id: 수정할 필드값 ID (get_field_values로 조회)
        value: 새 값

    Returns:
        수정된 필드값 정보
    """
    _check_write_allowed()
    return await client.update_field_value(field_value_id, value)


@mcp.tool()
async def delete_field_value(field_value_id: int) -> dict[str, Any]:
    """
    필드값을 삭제합니다.

    Args:
        field_value_id: 삭제할 필드값 ID

    Returns:
        삭제 결과
    """
    _check_write_allowed()
    return await client.delete_field_value(field_value_id)


# ── Relationship Strengths ────────────────────────────────────────────────────

@mcp.tool()
async def get_relationship_strengths(
    internal_id: int,
    external_id: int | None = None,
    type_: int | None = None,
) -> list[dict[str, Any]]:
    """
    내부 팀원과 외부 엔티티 사이의 관계 강도를 조회합니다.

    Args:
        internal_id: 내부 팀원(Person) ID
        external_id: 외부 인물/조직 ID (생략 시 모든 관계 반환)
        type_: 관계 타입 (1: 인물↔인물, 2: 인물↔조직)

    Returns:
        관계 강도 목록 (strength 점수 포함)
    """
    return await client.get_relationship_strengths(internal_id, external_id, type_)


def main() -> None:
    mcp.run(transport="stdio")
