# MODULE KNOWLEDGE BASE

## OVERVIEW
Runtime package for the DaVinci Resolve MCP server: one API wrapper (`resolve_api.py`) and one MCP surface (`server.py`).

## WHERE TO LOOK
| Task | Location | Notes |
|------|----------|-------|
| Add/update MCP resources | `src/davinci_resolve_mcp/server.py` | Resource URIs currently under `system://`, `project://`, `timeline://`, `mediapool://`, `storage://` |
| Add/update MCP tools | `src/davinci_resolve_mcp/server.py` | 14 `@mcp.tool()` functions; keep return type as user-facing `str` |
| Resolve/Fusion primitive ops | `src/davinci_resolve_mcp/resolve_api.py` | Thin wrappers over Resolve scripting API objects |
| OS bootstrap or import fallback behavior | `src/davinci_resolve_mcp/resolve_api.py` | Windows/macOS/Linux path handling for `DaVinciResolveScript` |
| Package version metadata | `src/davinci_resolve_mcp/__init__.py` | `__version__` mirrored by release automation |

## LOCAL STRUCTURE
```text
src/davinci_resolve_mcp/
├── __init__.py
├── resolve_api.py
└── server.py
```

## CONVENTIONS (LOCAL)
- `server.py` imports `ResolveAPI`, instantiates it at import time, then exposes resources/tools.
- Guard style is repetitive and explicit: check connectivity/object existence first, then return string errors.
- Tools/resources do not raise for normal failure conditions; they return descriptive failure text.
- Side-effect operations generally route through `ResolveAPI`; keep server-layer logic thin.

## CURRENT MCP SURFACE
- Resources: `system://status`, `project://current`, `project://timelines`, `timeline://current`, `mediapool://folders`, `mediapool://current`, `storage://volumes`.
- Tools: `create_project`, `load_project`, `save_project`, `create_timeline`, `set_current_timeline`, `import_media`, `create_folder`, `create_timeline_from_clips`, `add_fusion_comp_to_clip`, `create_fusion_node`, `create_fusion_node_chain`, `open_page`, `execute_python`, `execute_lua`.

## ANTI-PATTERNS (LOCAL)
- Do not move Resolve connection setup out of `ResolveAPI._connect_to_resolve` unless all platform fallbacks are preserved.
- Do not replace user-facing string responses with raw object returns in tool/resource functions.
- Do not remove runtime import fallback (`absolute` then `relative`) in `server.py`; it supports both installed and source execution.
- Do not silently narrow valid Resolve page names or track types without updating validation/error messages.

## GOTCHAS
- `execute_python` intentionally executes arbitrary code with direct object handles; treat as privileged surface.
- `create_fusion_node_chain` currently catches broad exceptions and returns errors as text; keep behavior consistent unless changing API contract.
