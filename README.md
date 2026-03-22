# affinity-mcp

Affinity CRM을 Claude(MCP)에서 직접 조회·관리할 수 있는 MCP 서버입니다.
[FastMCP](https://github.com/jlowin/fastmcp) 기반으로 구현되었으며, stdio 및 Docker 실행을 모두 지원합니다.

## 제공 기능 (Tools)

| 카테고리 | Tool | 설명 |
|---|---|---|
| **Organizations** | `search_organizations` | 이름/도메인으로 조직 검색 |
| | `get_organization` | 조직 상세 조회 |
| | `create_organization` | 조직 생성 |
| | `update_organization` | 조직 수정 |
| | `delete_organization` | 조직 삭제 |
| **Persons** | `search_persons` | 이름/이메일로 인물 검색 |
| | `get_person` | 인물 상세 조회 |
| | `create_person` | 인물 생성 |
| | `update_person` | 인물 수정 |
| | `delete_person` | 인물 삭제 |
| **Opportunities** | `get_opportunities` | 기회(딜) 목록 조회 |
| | `get_opportunity` | 기회 상세 조회 |
| | `create_opportunity` | 기회 생성 |
| | `update_opportunity` | 기회 수정 |
| | `delete_opportunity` | 기회 삭제 |
| **Lists** | `get_lists` | 전체 리스트 조회 |
| | `get_list` | 리스트 상세 조회 |
| | `get_list_entries` | 리스트 항목 조회 (페이지네이션 지원) |
| | `create_list_entry` | 리스트에 엔티티 추가 |
| | `delete_list_entry` | 리스트 항목 제거 |
| **Notes** | `get_notes` | 노트 조회 (조직/인물/기회 필터) |
| | `create_note` | 노트 작성 |
| | `update_note` | 노트 수정 |
| | `delete_note` | 노트 삭제 |
| **Fields** | `get_fields` | 필드 목록 조회 |
| | `get_field_values` | 엔티티 필드값 조회 |
| | `create_field_value` | 필드값 추가 |
| | `update_field_value` | 필드값 수정 |
| | `delete_field_value` | 필드값 삭제 |
| **Relationships** | `get_relationship_strengths` | 관계 강도 조회 |

## 설치 및 실행

### 사전 요구사항

- Python 3.11+
- [uv](https://github.com/astral-sh/uv)
- Affinity API Key

### 환경 변수 설정

```bash
cp .env.example .env  # 또는 직접 생성
```

`.env` 파일:

```env
AFFINITY_API_KEY=your_api_key_here
READ_ONLY=false   # true로 설정하면 모든 쓰기/삭제 작업 차단
```

### 로컬 실행 (stdio)

```bash
uv sync
python app.py
```

### Docker 실행

```bash
docker build -t affinity-mcp .
docker run -e AFFINITY_API_KEY=your_key affinity-mcp
```

## Claude Code 연동

`~/.claude/settings.json` 또는 프로젝트의 `.claude/settings.json`에 추가:

```json
{
  "mcpServers": {
    "affinity": {
      "command": "uv",
      "args": ["run", "--project", "/path/to/affinity-mcp", "python", "app.py"],
      "env": {
        "AFFINITY_API_KEY": "your_api_key_here",
        "READ_ONLY": "false"
      }
    }
  }
}
```

## 읽기 전용 모드

`READ_ONLY=true`로 설정하면 `create_*`, `update_*`, `delete_*` 계열 tool이 모두 차단됩니다.
조회(read) 목적으로만 사용할 때 안전하게 활용할 수 있습니다.

## 기술 스택

- [FastMCP](https://github.com/jlowin/fastmcp) — MCP 서버 프레임워크
- [httpx](https://www.python-httpx.org/) — Affinity API 비동기 HTTP 클라이언트
- [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) — 환경 변수 관리
- [uv](https://github.com/astral-sh/uv) — 패키지 관리
