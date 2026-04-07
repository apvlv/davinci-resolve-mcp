# PROJECT KNOWLEDGE BASE

**Generated:** 2026-02-08 13:48:19 America/New_York
**Commit:** d6e393d
**Branch:** main

## OVERVIEW
Python MCP server exposing DaVinci Resolve and Fusion operations as MCP resources/tools.
Single runtime package under `src/davinci_resolve_mcp`; CI/release automated via GitHub Actions.

## STRUCTURE
```text
./
├── src/davinci_resolve_mcp/   # Runtime server + Resolve API bridge
├── tests/                     # Minimal import smoke tests
├── .github/workflows/         # CI + semantic-release/publish
├── pyproject.toml
├── Makefile
└── README.md
```

## WHERE TO LOOK
| Task | Location | Notes |
|------|----------|-------|
| Add/modify MCP resource/tool surface | `src/davinci_resolve_mcp/server.py` | `@mcp.resource` and `@mcp.tool` definitions |
| Resolve API wrappers / platform-specific connect logic | `src/davinci_resolve_mcp/resolve_api.py` | OS-dependent `DaVinciResolveScript` import paths |
| Package entrypoint/version | `pyproject.toml`, `src/davinci_resolve_mcp/__init__.py` | Script entrypoint is `davinci_resolve_mcp.server:main` |
| Dev workflow commands | `Makefile`, `README.md` | `uv`-based local workflow |
| CI/release behavior | `.github/workflows/ci.yml`, `.github/workflows/release.yml` | PR lint/test; push-to-main semantic release + PyPI publish |

## CODE MAP
LSP unavailable in this environment (`basedpyright-langserver` missing), so map is AST/grep-derived.

| Symbol | Type | Location | Refs | Role |
|--------|------|----------|------|------|
| `ResolveAPI` | class | `src/davinci_resolve_mcp/resolve_api.py` | n/a | Resolve/Fusion connection and wrapper methods |
| `mcp = FastMCP("DaVinci Resolve")` | server object | `src/davinci_resolve_mcp/server.py` | n/a | MCP app container |
| `main` | function | `src/davinci_resolve_mcp/server.py` | n/a | CLI entrypoint used by project script |

## CONVENTIONS
- `uv` is the default package/env/task runner; commands in docs and workflows assume `uv`.
- Lint/format standardized on Ruff; lint ignores E501 and line length is 100.
- MCP endpoints return user-facing strings rather than structured JSON payloads.
- `server.py` is intentionally monolithic: resources/tools colocated in a single file.

## ANTI-PATTERNS (THIS PROJECT)
- Do not change `project.scripts.davinci-resolve-mcp` target without updating docs and client setup examples.
- Do not split connection bootstrap away from `ResolveAPI._connect_to_resolve` without preserving OS path fallbacks.
- Do not assume Resolve is present in tests/CI; current tests are import-level only.

## UNIQUE STYLES
- Extensive defensive early returns with human-readable error strings.
- Runtime connection attempted at module import (`resolve_api = ResolveAPI()` in `server.py`).
- Includes privileged scripting tools (`execute_python`, `execute_lua`) as first-class MCP tools.

## COMMANDS
```bash
make install
make lint-check
make format-check
make test
make check
uv run davinci-resolve-mcp
```

## NOTES
- `Makefile:test` uses `--cov=src/resolve_mcp`, while package path is `src/davinci_resolve_mcp` (coverage path mismatch to keep in mind).
- Release workflow requires `SEMANTIC_RELEASE_TOKEN` and tags published versions before PyPI publish.
