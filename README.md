# DaVinci Resolve MCP Server

Model Context Protocol (MCP) server that lets MCP clients control and inspect DaVinci Resolve (including Fusion) through tools and resources.

## What it provides

- Project management (create, load, save)
- Timeline operations (create timeline, switch timeline, build from clips)
- Media pool operations (import media, create folders, inspect folders)
- Fusion helpers (add comp to clip, create nodes, create node chains)
- Resolve page navigation
- Advanced scripting (`execute_python`, `execute_lua`)

## Requirements

- Python 3.10+
- DaVinci Resolve with scripting API available
- An MCP-compatible client (for example Claude Desktop)

## Install

```bash
git clone https://github.com/schoi80/davinci-resolve-mcp.git
cd davinci-resolve-mcp
uv sync --all-extras --dev
```

## Run the server

```bash
uv run davinci-resolve-mcp
```

The server will try to connect to Resolve on startup. Make sure DaVinci Resolve is running.

## MCP client setup

Configure your MCP client to launch the server command:

```json
{
  "mcpServers": {
    "davinci-resolve": {
      "command": "uv",
      "args": ["run", "davinci-resolve-mcp"]
    }
  }
}
```

## Resources

- `system://status`
- `project://current`
- `project://timelines`
- `timeline://current`
- `mediapool://folders`
- `mediapool://current`
- `storage://volumes`

## Tools

### Project

- `create_project(name)`
- `load_project(name)`
- `save_project()`

### Timeline

- `create_timeline(name)`
- `set_current_timeline(index)`

### Media

- `import_media(file_paths)`
- `create_folder(name)`
- `create_timeline_from_clips(name, clip_indices)`

### Fusion

- `add_fusion_comp_to_clip(timeline_index, track_type, track_index, item_index)`
- `create_fusion_node(node_type, parameters)`
- `create_fusion_node_chain(node_chain)`

### Resolve UI

- `open_page(page_name)` where page name is one of:
  - `media`, `edit`, `fusion`, `color`, `fairlight`, `deliver`

### Advanced

- `execute_python(code)`
- `execute_lua(script)`

## Development

```bash
make install      # install deps and pre-commit hooks
make lint-check   # ruff check
make format-check # ruff format check
make test         # pytest with coverage
make check        # lint + format + tests
```

## Example usage ideas

- "Create a project named `My Documentary`"
- "List timelines in the current project"
- "Import these files into the media pool"
- "Open the Color page"
- "Create a Fusion node chain Blur -> ColorCorrector"

## License

MIT (see `LICENSE`)
