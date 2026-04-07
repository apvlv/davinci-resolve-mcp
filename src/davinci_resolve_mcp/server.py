"""
DaVinci Resolve MCP Server

This module implements a Model Context Protocol (MCP) server for DaVinci Resolve,
allowing AI assistants like Claude to interact with DaVinci Resolve through the MCP protocol.
"""

import logging
import os
import sys
from typing import Any, Dict, List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("resolve_mcp")

logger.debug("Python version: %s", sys.version)
logger.debug("Python executable: %s", sys.executable)
logger.debug("Python path: %s", sys.path)
logger.debug("Current working directory: %s", os.getcwd())

try:
    from mcp.server.fastmcp import FastMCP
except ImportError as e:
    logger.exception("Error importing MCP: %s", e)
    raise

try:
    # Try absolute import first (when installed as a package)
    from davinci_resolve_mcp.resolve_api import ResolveAPI
except ImportError as e:
    logger.warning("Absolute import failed for ResolveAPI: %s", e)
    try:
        # Fall back to relative import (when running from source)
        from .resolve_api import ResolveAPI
    except ImportError as e2:
        logger.exception("Relative import failed for ResolveAPI: %s", e2)
        raise

# Create the MCP server
mcp = FastMCP("DaVinci Resolve")

# Initialize the Resolve API
resolve_api = ResolveAPI()

# Check if connected to Resolve
if not resolve_api.is_connected():
    logger.error("Failed to connect to DaVinci Resolve. Make sure DaVinci Resolve is running.")
else:
    logger.info("Successfully connected to DaVinci Resolve.")

# Define resource and tool functions

# System Information Resources


@mcp.resource("system://status")
def get_system_status() -> str:
    """Get the current status of the DaVinci Resolve connection."""
    if resolve_api.is_connected():
        project_name = resolve_api.get_project_name() or "No project open"
        timeline = resolve_api.get_current_timeline()
        timeline_name = timeline.GetName() if timeline else "No timeline open"

        return f"""
        DaVinci Resolve Status:
        - Connection: Connected
        - Current Project: {project_name}
        - Current Timeline: {timeline_name}
        """
    else:
        return """
        DaVinci Resolve Status:
        - Connection: Not connected
        - Error: DaVinci Resolve is not running or not accessible
        """


# Project Resources


@mcp.resource("project://current")
def get_current_project() -> str:
    """Get information about the current project."""
    if not resolve_api.is_connected():
        return "Error: Not connected to DaVinci Resolve."

    project = resolve_api.get_current_project()
    if not project:
        return "No project is currently open."

    project_name = project.GetName()
    timeline_count = project.GetTimelineCount()

    current_timeline = project.GetCurrentTimeline()
    timeline_name = current_timeline.GetName() if current_timeline else "None"

    return f"""
    Current Project: {project_name}
    Timeline Count: {timeline_count}
    Current Timeline: {timeline_name}
    """


@mcp.resource("project://timelines")
def get_project_timelines() -> str:
    """Get a list of timelines in the current project."""
    if not resolve_api.is_connected():
        return "Error: Not connected to DaVinci Resolve."

    project = resolve_api.get_current_project()
    if not project:
        return "No project is currently open."

    timeline_count = project.GetTimelineCount()
    if timeline_count == 0:
        return "No timelines in the current project."

    timelines = []
    for i in range(1, timeline_count + 1):
        timeline = project.GetTimelineByIndex(i)
        if timeline:
            timelines.append(f"{i}. {timeline.GetName()}")

    return "\n".join(timelines)


@mcp.resource("timeline://current")
def get_current_timeline() -> str:
    """Get information about the current timeline."""
    if not resolve_api.is_connected():
        return "Error: Not connected to DaVinci Resolve."

    project = resolve_api.get_current_project()
    if not project:
        return "No project is currently open."

    timeline = project.GetCurrentTimeline()
    if not timeline:
        return "No timeline is currently open."

    timeline_name = timeline.GetName()
    start_frame = timeline.GetStartFrame()
    end_frame = timeline.GetEndFrame()
    duration = end_frame - start_frame + 1

    video_track_count = timeline.GetTrackCount("video")
    audio_track_count = timeline.GetTrackCount("audio")
    subtitle_track_count = timeline.GetTrackCount("subtitle")

    return f"""
    Timeline: {timeline_name}
    Duration: {duration} frames ({start_frame} - {end_frame})
    Video Tracks: {video_track_count}
    Audio Tracks: {audio_track_count}
    Subtitle Tracks: {subtitle_track_count}
    """


@mcp.resource("mediapool://folders")
def get_media_pool_folders() -> str:
    """Get a list of folders in the media pool."""
    if not resolve_api.is_connected():
        return "Error: Not connected to DaVinci Resolve."

    media_pool = resolve_api.get_media_pool()
    if not media_pool:
        return "No media pool available."

    root_folder = media_pool.GetRootFolder()
    if not root_folder:
        return "No root folder available."

    def get_folder_structure(folder, indent=""):
        result = []
        name = folder.GetName()
        result.append(f"{indent}- {name}")

        subfolders = folder.GetSubFolders()
        for subfolder in subfolders:
            result.extend(get_folder_structure(subfolder, indent + "  "))

        return result

    folder_structure = get_folder_structure(root_folder)
    return "\n".join(folder_structure)


@mcp.resource("mediapool://current")
def get_current_media_pool_folder() -> str:
    """Get information about the current media pool folder."""
    if not resolve_api.is_connected():
        return "Error: Not connected to DaVinci Resolve."

    media_pool = resolve_api.get_media_pool()
    if not media_pool:
        return "No media pool available."

    current_folder = media_pool.GetCurrentFolder()
    if not current_folder:
        return "No current folder available."

    folder_name = current_folder.GetName()
    clips = current_folder.GetClips()
    clip_count = len(clips) if clips else 0

    clip_info = []
    if clips:
        for i, clip in enumerate(clips, 1):
            if i > 10:  # Limit to 10 clips to avoid overwhelming response
                clip_info.append(f"... and {clip_count - 10} more clips")
                break
            clip_info.append(f"{i}. {clip.GetName()}")

    clips_text = "No clips in this folder." if clip_count == 0 else "\n".join(clip_info)

    return f"Current Folder: {folder_name}\nClip Count: {clip_count}\nClips:\n{clips_text}"


@mcp.resource("storage://volumes")
def get_mounted_volumes() -> str:
    """Get a list of mounted volumes in the media storage."""
    if not resolve_api.is_connected():
        return "Error: Not connected to DaVinci Resolve."

    media_storage = resolve_api.get_media_storage()
    if not media_storage:
        return "No media storage available."

    volumes = media_storage.GetMountedVolumes()
    if not volumes:
        return "No mounted volumes available."

    volume_list = []
    for i, volume in enumerate(volumes, 1):
        volume_list.append(f"{i}. {volume}")

    return "\n".join(volume_list)


# Tools for Project Management


@mcp.tool()
def create_project(name: str) -> str:
    """
    Create a new DaVinci Resolve project.

    Args:
        name: The name of the project to create

    Returns:
        A message indicating success or failure
    """
    if not resolve_api.is_connected():
        return "Error: Not connected to DaVinci Resolve."

    success = resolve_api.create_project(name)
    if success:
        return f"Successfully created project '{name}'."
    else:
        return f"Failed to create project '{name}'. The project may already exist."


@mcp.tool()
def load_project(name: str) -> str:
    """
    Load an existing DaVinci Resolve project.

    Args:
        name: The name of the project to load

    Returns:
        A message indicating success or failure
    """
    if not resolve_api.is_connected():
        return "Error: Not connected to DaVinci Resolve."

    success = resolve_api.load_project(name)
    if success:
        return f"Successfully loaded project '{name}'."
    else:
        return f"Failed to load project '{name}'. The project may not exist."


@mcp.tool()
def save_project() -> str:
    """
    Save the current DaVinci Resolve project.

    Returns:
        A message indicating success or failure
    """
    if not resolve_api.is_connected():
        return "Error: Not connected to DaVinci Resolve."

    project = resolve_api.get_current_project()
    if not project:
        return "No project is currently open."

    success = resolve_api.save_project()
    if success:
        return f"Successfully saved project '{project.GetName()}'."
    else:
        return f"Failed to save project '{project.GetName()}'."


# Tools for Timeline Management


@mcp.tool()
def create_timeline(name: str) -> str:
    """
    Create a new timeline in the current project.

    Args:
        name: The name of the timeline to create

    Returns:
        A message indicating success or failure
    """
    if not resolve_api.is_connected():
        return "Error: Not connected to DaVinci Resolve."

    project = resolve_api.get_current_project()
    if not project:
        return "No project is currently open."

    media_pool = resolve_api.get_media_pool()
    if not media_pool:
        return "No media pool available."

    timeline = media_pool.CreateEmptyTimeline(name)
    if timeline:
        project.SetCurrentTimeline(timeline)
        return f"Successfully created timeline '{name}'."
    else:
        return f"Failed to create timeline '{name}'. The timeline may already exist."


@mcp.tool()
def set_current_timeline(index: int) -> str:
    """
    Set the current timeline by index.

    Args:
        index: The index of the timeline (1-based)

    Returns:
        A message indicating success or failure
    """
    if not resolve_api.is_connected():
        return "Error: Not connected to DaVinci Resolve."

    project = resolve_api.get_current_project()
    if not project:
        return "No project is currently open."

    timeline_count = project.GetTimelineCount()
    if index < 1 or index > timeline_count:
        return f"Invalid timeline index. Valid range is 1-{timeline_count}."

    timeline = project.GetTimelineByIndex(index)
    if not timeline:
        return f"Failed to get timeline at index {index}."

    success = project.SetCurrentTimeline(timeline)
    if success:
        return f"Successfully set current timeline to '{timeline.GetName()}'."
    else:
        return f"Failed to set current timeline to '{timeline.GetName()}'."


# Tools for Media Management


@mcp.tool()
def import_media(file_paths: List[str]) -> str:
    """
    Import media files into the current media pool folder.

    Args:
        file_paths: A list of file paths to import

    Returns:
        A message indicating success or failure
    """
    if not resolve_api.is_connected():
        return "Error: Not connected to DaVinci Resolve."

    media_storage = resolve_api.get_media_storage()
    if not media_storage:
        return "No media storage available."

    media_pool = resolve_api.get_media_pool()
    if not media_pool:
        return "No media pool available."

    clips = media_storage.AddItemsToMediaPool(file_paths)
    if clips:
        return f"Successfully imported {len(clips)} media files."
    else:
        return "Failed to import media files. Check that the file paths are valid."


@mcp.tool()
def create_folder(name: str) -> str:
    """
    Create a new folder in the current media pool folder.

    Args:
        name: The name of the folder to create

    Returns:
        A message indicating success or failure
    """
    if not resolve_api.is_connected():
        return "Error: Not connected to DaVinci Resolve."

    media_pool = resolve_api.get_media_pool()
    if not media_pool:
        return "No media pool available."

    current_folder = media_pool.GetCurrentFolder()
    if not current_folder:
        return "No current folder available."

    new_folder = media_pool.AddSubFolder(current_folder, name)
    if new_folder:
        return f"Successfully created folder '{name}'."
    else:
        return f"Failed to create folder '{name}'. The folder may already exist."


@mcp.tool()
def create_timeline_from_clips(name: str, clip_indices: List[int]) -> str:
    """
    Create a new timeline from clips in the current media pool folder.

    Args:
        name: The name of the timeline to create
        clip_indices: A list of clip indices (1-based) to include in the timeline

    Returns:
        A message indicating success or failure
    """
    if not resolve_api.is_connected():
        return "Error: Not connected to DaVinci Resolve."

    media_pool = resolve_api.get_media_pool()
    if not media_pool:
        return "No media pool available."

    current_folder = media_pool.GetCurrentFolder()
    if not current_folder:
        return "No current folder available."

    clips = current_folder.GetClips()
    if not clips:
        return "No clips in the current folder."

    clips_list = list(clips.values())
    selected_clips = []

    for index in clip_indices:
        if index < 1 or index > len(clips_list):
            return f"Invalid clip index {index}. Valid range is 1-{len(clips_list)}."
        selected_clips.append(clips_list[index - 1])

    timeline = media_pool.CreateTimelineFromClips(name, selected_clips)
    if timeline:
        return f"Successfully created timeline '{name}' with {len(selected_clips)} clips."
    else:
        return f"Failed to create timeline '{name}'."


# Tools for Fusion Integration


@mcp.tool()
def add_fusion_comp_to_clip(
    timeline_index: int, track_type: str, track_index: int, item_index: int
) -> str:
    """
    Add a Fusion composition to a clip in the timeline.

    Args:
        timeline_index: The index of the timeline (1-based)
        track_type: The type of track ("video", "audio", or "subtitle")
        track_index: The index of the track (1-based)
        item_index: The index of the item in the track (1-based)

    Returns:
        A message indicating success or failure
    """
    if not resolve_api.is_connected():
        return "Error: Not connected to DaVinci Resolve."

    project = resolve_api.get_current_project()
    if not project:
        return "No project is currently open."

    timeline_count = project.GetTimelineCount()
    if timeline_index < 1 or timeline_index > timeline_count:
        return f"Invalid timeline index. Valid range is 1-{timeline_count}."

    timeline = project.GetTimelineByIndex(timeline_index)
    if not timeline:
        return f"Failed to get timeline at index {timeline_index}."

    if track_type not in ["video", "audio", "subtitle"]:
        return "Invalid track type. Valid types are 'video', 'audio', or 'subtitle'."

    track_count = timeline.GetTrackCount(track_type)
    if track_index < 1 or track_index > track_count:
        return f"Invalid track index. Valid range is 1-{track_count}."

    items = timeline.GetItemsInTrack(track_type, track_index)
    if not items:
        return f"No items in {track_type} track {track_index}."

    if item_index < 1 or item_index > len(items):
        return f"Invalid item index. Valid range is 1-{len(items)}."

    item = items[item_index - 1]
    fusion_comp = item.AddFusionComp()

    if fusion_comp:
        # Switch to the Fusion page to edit the composition
        resolve_api.open_page("fusion")
        return f"Successfully added Fusion composition to {track_type} track {track_index}, item {item_index}."
    else:
        return f"Failed to add Fusion composition to {track_type} track {track_index}, item {item_index}."


@mcp.tool()
def create_fusion_node(node_type: str, parameters: Dict[str, Any] = None) -> str:
    """
    Create a Fusion node in the current composition.

    Args:
        node_type: The type of node to create (e.g., 'Blur', 'ColorCorrector', 'Text')
        parameters: Optional dictionary of parameters to set on the node

    Returns:
        A message indicating success or failure
    """
    if not resolve_api.is_connected():
        return "Error: Not connected to DaVinci Resolve."

    # Get the current Fusion composition
    comp = resolve_api.get_current_comp()
    if not comp:
        return "No active Fusion composition. Please open the Fusion page and select a composition first."

    # Create the node
    node = resolve_api.create_fusion_node(comp, node_type, parameters)
    if node:
        return f"Successfully created {node_type} node in the Fusion composition."
    else:
        return f"Failed to create {node_type} node. Check that the node type is valid."


@mcp.tool()
def create_fusion_node_chain(node_chain: List[Dict[str, Any]]) -> str:
    """
    Create a chain of connected Fusion nodes in the current composition.

    Args:
        node_chain: A list of dictionaries, each containing:
                    - 'type': The type of node to create
                    - 'name': Optional name for the node
                    - 'params': Optional dictionary of parameters to set on the node

    Returns:
        A message indicating success or failure
    """
    if not resolve_api.is_connected():
        return "Error: Not connected to DaVinci Resolve."

    # Get the current Fusion composition
    comp = resolve_api.get_current_comp()
    if not comp:
        return "No active Fusion composition. Please open the Fusion page and select a composition first."

    if not node_chain or len(node_chain) == 0:
        return "No nodes specified in the chain."

    try:
        # Create the first node
        prev_node = None
        nodes_created = []

        for node_info in node_chain:
            node_type = node_info.get("type")
            if not node_type:
                continue

            # Create the node
            node = resolve_api.create_fusion_node(comp, node_type, node_info.get("params"))

            if not node:
                continue

            # Set the node name if provided
            if "name" in node_info and node_info["name"]:
                node.SetAttrs({"TOOLS_Name": node_info["name"]})

            # Connect to previous node if this isn't the first node
            if prev_node:
                # Connect the main output of the previous node to the main input of this node
                node.ConnectInput("Input", prev_node)

            prev_node = node
            nodes_created.append(node_type)

        if not nodes_created:
            return "Failed to create any nodes in the chain."

        return f"Successfully created node chain: {' -> '.join(nodes_created)}"
    except Exception as e:
        return f"Error creating node chain: {str(e)}"


# Tools for Page Navigation


@mcp.tool()
def open_page(page_name: str) -> str:
    """
    Open a specific page in DaVinci Resolve.

    Args:
        page_name: The name of the page to open (media, edit, fusion, color, fairlight, deliver)

    Returns:
        A message indicating success or failure
    """
    if not resolve_api.is_connected():
        return "Error: Not connected to DaVinci Resolve."

    valid_pages = ["media", "edit", "fusion", "color", "fairlight", "deliver"]
    if page_name.lower() not in valid_pages:
        return f"Invalid page name. Valid pages are: {', '.join(valid_pages)}."

    success = resolve_api.open_page(page_name.lower())
    if success:
        return f"Successfully opened the {page_name.capitalize()} page."
    else:
        return f"Failed to open the {page_name.capitalize()} page."


# Tools for Advanced Operations


@mcp.tool()
def execute_python(code: str) -> str:
    """
    Execute arbitrary Python code in DaVinci Resolve.

    Args:
        code: The Python code to execute

    Returns:
        The result of the code execution
    """
    if not resolve_api.is_connected():
        return "Error: Not connected to DaVinci Resolve."

    # Create a local namespace with access to the Resolve API
    local_namespace = {
        "resolve_api": resolve_api,
        "resolve": resolve_api.resolve,
        "fusion": resolve_api.fusion,
        "project_manager": resolve_api.project_manager,
        "current_project": resolve_api.current_project,
        "media_storage": resolve_api.media_storage,
        "media_pool": resolve_api.media_pool,
    }

    try:
        # Execute the code in the local namespace
        exec(code, globals(), local_namespace)

        # Update the Resolve API objects with any changes made in the code
        resolve_api.resolve = local_namespace.get("resolve", resolve_api.resolve)
        resolve_api.fusion = local_namespace.get("fusion", resolve_api.fusion)
        resolve_api.project_manager = local_namespace.get(
            "project_manager", resolve_api.project_manager
        )
        resolve_api.current_project = local_namespace.get(
            "current_project", resolve_api.current_project
        )
        resolve_api.media_storage = local_namespace.get("media_storage", resolve_api.media_storage)
        resolve_api.media_pool = local_namespace.get("media_pool", resolve_api.media_pool)

        # Check for a result variable
        if "result" in local_namespace:
            result = local_namespace["result"]
            return str(result)

        return "Code executed successfully."
    except Exception as e:
        return f"Error executing code: {str(e)}"


@mcp.tool()
def execute_lua(script: str) -> str:
    """
    Execute a Lua script in DaVinci Resolve's Fusion.

    Args:
        script: The Lua script to execute

    Returns:
        The result of the script execution
    """
    if not resolve_api.is_connected():
        return "Error: Not connected to DaVinci Resolve."

    if not resolve_api.fusion:
        return "Fusion is not available."

    try:
        result = resolve_api.execute_lua(script)
        return str(result) if result is not None else "Script executed successfully."
    except Exception as e:
        return f"Error executing Lua script: {str(e)}"


# Main entry point function for the MCP server
def main():
    """Main entry point for the MCP server."""
    return mcp.run()


if __name__ == "__main__":
    main()
