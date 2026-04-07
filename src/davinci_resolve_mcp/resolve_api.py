"""
DaVinci Resolve API connector module.

This module provides functions to connect to DaVinci Resolve's Python API
and interact with its various components.
"""

import logging
import os
import platform
import sys
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class ResolveAPI:
    """Class to handle connection and interaction with DaVinci Resolve API."""

    def __init__(self):
        """Initialize the ResolveAPI class and connect to DaVinci Resolve."""
        self.resolve = None
        self.fusion = None
        self.project_manager = None
        self.current_project = None
        self.media_storage = None
        self.media_pool = None

        self._connect_to_resolve()

    def _connect_to_resolve(self) -> None:
        """
        Connect to DaVinci Resolve based on the current operating system.

        This function adds the appropriate paths to sys.path and imports the
        DaVinciResolveScript module to establish a connection to Resolve.
        """
        # Determine the appropriate path based on the operating system
        if platform.system() == "Windows":
            resolve_script_dir = os.path.join(
                os.environ.get("PROGRAMDATA", "C:\\ProgramData"),
                "Blackmagic Design",
                "DaVinci Resolve",
                "Support",
                "Developer",
                "Scripting",
            )
            script_api_path = os.path.join(resolve_script_dir, "Modules")

            # Add the API directory to the system path
            if script_api_path not in sys.path:
                sys.path.append(script_api_path)

            # Import the DaVinciResolveScript module
            try:
                import DaVinciResolveScript as dvr_script

                self.resolve = dvr_script.scriptapp("Resolve")
            except ImportError:
                logger.error("Could not find DaVinciResolveScript module on Windows.")
                self.resolve = None

        elif platform.system() == "Darwin":
            # macOS path
            resolve_script_dir = (
                "/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting"
            )
            script_api_path = os.path.join(resolve_script_dir, "Modules")

            # Add the API directory to the system path
            if script_api_path not in sys.path:
                sys.path.append(script_api_path)

            # Import the DaVinciResolveScript module
            try:
                import DaVinciResolveScript as dvr_script

                self.resolve = dvr_script.scriptapp("Resolve")
            except ImportError:
                # Try the user-specific path if the system-wide path fails
                user_script_api_path = os.path.join(
                    os.path.expanduser("~"),
                    "Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/Modules",
                )
                if user_script_api_path not in sys.path:
                    sys.path.append(user_script_api_path)

                try:
                    import DaVinciResolveScript as dvr_script

                    self.resolve = dvr_script.scriptapp("Resolve")
                except ImportError:
                    logger.error("Could not find DaVinciResolveScript module on macOS.")
                    self.resolve = None

        elif platform.system() == "Linux":
            # Linux path
            resolve_script_dir = "/opt/resolve/Developer/Scripting"
            script_api_path = os.path.join(resolve_script_dir, "Modules")

            # Add the API directory to the system path
            if script_api_path not in sys.path:
                sys.path.append(script_api_path)

            # Import the DaVinciResolveScript module
            try:
                import DaVinciResolveScript as dvr_script

                self.resolve = dvr_script.scriptapp("Resolve")
            except ImportError:
                logger.error("Could not find DaVinciResolveScript module on Linux.")
                self.resolve = None

        # Initialize other components if Resolve is connected
        if self.resolve:
            self.project_manager = self.resolve.GetProjectManager()
            self.current_project = self.project_manager.GetCurrentProject()
            self.media_storage = self.resolve.GetMediaStorage()
            self.fusion = self.resolve.Fusion()

            # Initialize media pool if a project is open
            if self.current_project:
                self.media_pool = self.current_project.GetMediaPool()

    def is_connected(self) -> bool:
        """Check if connected to DaVinci Resolve."""
        return self.resolve is not None

    def get_project_manager(self):
        """Get the project manager object."""
        return self.project_manager

    def get_current_project(self):
        """Get the current project object."""
        if self.project_manager:
            self.current_project = self.project_manager.GetCurrentProject()
        return self.current_project

    def get_media_storage(self):
        """Get the media storage object."""
        return self.media_storage

    def get_media_pool(self):
        """Get the media pool object for the current project."""
        if self.current_project:
            self.media_pool = self.current_project.GetMediaPool()
        return self.media_pool

    def get_fusion(self):
        """Get the Fusion object."""
        return self.fusion

    def open_page(self, page_name: str) -> bool:
        """
        Open a specific page in DaVinci Resolve.

        Args:
            page_name (str): The name of the page to open.
                             Valid values: "media", "edit", "fusion", "color", "fairlight", "deliver"

        Returns:
            bool: True if successful, False otherwise.
        """
        if not self.resolve:
            return False

        valid_pages = ["media", "edit", "fusion", "color", "fairlight", "deliver"]
        if page_name.lower() not in valid_pages:
            return False

        self.resolve.OpenPage(page_name.lower())
        return True

    def create_project(self, project_name: str) -> bool:
        """
        Create a new project with the given name.

        Args:
            project_name (str): The name of the project to create.

        Returns:
            bool: True if successful, False otherwise.
        """
        if not self.project_manager:
            return False

        new_project = self.project_manager.CreateProject(project_name)
        if new_project:
            self.current_project = new_project
            self.media_pool = self.current_project.GetMediaPool()
            return True

        return False

    def load_project(self, project_name: str) -> bool:
        """
        Load an existing project with the given name.

        Args:
            project_name (str): The name of the project to load.

        Returns:
            bool: True if successful, False otherwise.
        """
        if not self.project_manager:
            return False

        loaded_project = self.project_manager.LoadProject(project_name)
        if loaded_project:
            self.current_project = loaded_project
            self.media_pool = self.current_project.GetMediaPool()
            return True

        return False

    def save_project(self) -> bool:
        """
        Save the current project.

        Returns:
            bool: True if successful, False otherwise.
        """
        if not self.current_project:
            return False

        return self.current_project.SaveProject()

    def get_project_name(self) -> Optional[str]:
        """
        Get the name of the current project.

        Returns:
            Optional[str]: The project name, or None if no project is open.
        """
        if not self.current_project:
            return None

        return self.current_project.GetName()

    def create_timeline(self, timeline_name: str) -> bool:
        """
        Create a new timeline with the given name.

        Args:
            timeline_name (str): The name of the timeline to create.

        Returns:
            bool: True if successful, False otherwise.
        """
        if not self.media_pool:
            return False

        new_timeline = self.media_pool.CreateEmptyTimeline(timeline_name)
        return new_timeline is not None

    def get_current_timeline(self):
        """
        Get the current timeline.

        Returns:
            The current timeline object, or None if no timeline is open.
        """
        if not self.current_project:
            return None

        return self.current_project.GetCurrentTimeline()

    def get_timeline_count(self) -> int:
        """
        Get the number of timelines in the current project.

        Returns:
            int: The number of timelines, or 0 if no project is open.
        """
        if not self.current_project:
            return 0

        return self.current_project.GetTimelineCount()

    def get_timeline_by_index(self, index: int):
        """
        Get a timeline by its index.

        Args:
            index (int): The index of the timeline (1-based).

        Returns:
            The timeline object, or None if the index is invalid.
        """
        if not self.current_project:
            return None

        return self.current_project.GetTimelineByIndex(index)

    def set_current_timeline(self, timeline) -> bool:
        """
        Set the current timeline.

        Args:
            timeline: The timeline object to set as current.

        Returns:
            bool: True if successful, False otherwise.
        """
        if not self.current_project:
            return False

        return self.current_project.SetCurrentTimeline(timeline)

    def get_mounted_volumes(self) -> List[str]:
        """
        Get a list of mounted volumes.

        Returns:
            List[str]: A list of mounted volume paths.
        """
        if not self.media_storage:
            return []

        return self.media_storage.GetMountedVolumes()

    def get_sub_folders(self, folder_path: str) -> List[str]:
        """
        Get a list of subfolders in the given folder path.

        Args:
            folder_path (str): The path of the folder to get subfolders from.

        Returns:
            List[str]: A list of subfolder paths.
        """
        if not self.media_storage:
            return []

        return self.media_storage.GetSubFolders(folder_path)

    def get_files(self, folder_path: str) -> List[str]:
        """
        Get a list of files in the given folder path.

        Args:
            folder_path (str): The path of the folder to get files from.

        Returns:
            List[str]: A list of file paths.
        """
        if not self.media_storage:
            return []

        return self.media_storage.GetFiles(folder_path)

    def add_items_to_media_pool(self, file_paths: List[str]) -> List[Any]:
        """
        Add items from the media storage to the media pool.

        Args:
            file_paths (List[str]): A list of file paths to add.

        Returns:
            List[Any]: A list of added media pool items.
        """
        if not self.media_storage or not self.media_pool:
            return []

        return self.media_storage.AddItemsToMediaPool(file_paths)

    def get_root_folder(self):
        """
        Get the root folder of the media pool.

        Returns:
            The root folder object, or None if no media pool is available.
        """
        if not self.media_pool:
            return None

        return self.media_pool.GetRootFolder()

    def get_current_folder(self):
        """
        Get the current folder of the media pool.

        Returns:
            The current folder object, or None if no media pool is available.
        """
        if not self.media_pool:
            return None

        return self.media_pool.GetCurrentFolder()

    def add_sub_folder(self, parent_folder, folder_name: str):
        """
        Add a subfolder to the given parent folder.

        Args:
            parent_folder: The parent folder object.
            folder_name (str): The name of the subfolder to create.

        Returns:
            The created subfolder object, or None if unsuccessful.
        """
        if not self.media_pool:
            return None

        return self.media_pool.AddSubFolder(parent_folder, folder_name)

    def get_folder_clips(self, folder) -> List[Any]:
        """
        Get a list of clips in the given folder.

        Args:
            folder: The folder object.

        Returns:
            List[Any]: A list of media pool items in the folder.
        """
        if not folder:
            return []

        return folder.GetClips()

    def get_folder_name(self, folder) -> Optional[str]:
        """
        Get the name of the given folder.

        Args:
            folder: The folder object.

        Returns:
            Optional[str]: The folder name, or None if the folder is invalid.
        """
        if not folder:
            return None

        return folder.GetName()

    def get_folder_sub_folders(self, folder) -> List[Any]:
        """
        Get a list of subfolders in the given folder.

        Args:
            folder: The folder object.

        Returns:
            List[Any]: A list of subfolder objects.
        """
        if not folder:
            return []

        return folder.GetSubFolders()

    def append_to_timeline(self, clips: List[Any]) -> bool:
        """
        Append the given clips to the current timeline.

        Args:
            clips (List[Any]): A list of media pool items to append.

        Returns:
            bool: True if successful, False otherwise.
        """
        if not self.media_pool:
            return False

        return self.media_pool.AppendToTimeline(clips)

    def create_timeline_from_clips(self, timeline_name: str, clips: List[Any]):
        """
        Create a new timeline with the given name and append the given clips.

        Args:
            timeline_name (str): The name of the timeline to create.
            clips (List[Any]): A list of media pool items to append.

        Returns:
            The created timeline object, or None if unsuccessful.
        """
        if not self.media_pool:
            return None

        return self.media_pool.CreateTimelineFromClips(timeline_name, clips)

    def import_timeline_from_file(self, file_path: str):
        """
        Import a timeline from a file.

        Args:
            file_path (str): The path of the file to import.

        Returns:
            The imported timeline object, or None if unsuccessful.
        """
        if not self.media_pool:
            return None

        return self.media_pool.ImportTimelineFromFile(file_path)

    def execute_lua(self, script: str) -> Any:
        """
        Execute a Lua script in DaVinci Resolve.

        Args:
            script (str): The Lua script to execute.

        Returns:
            Any: The result of the script execution.
        """
        if not self.fusion:
            return None

        return self.fusion.Execute(script)

    def create_fusion_node(self, comp, node_type: str, inputs: Dict[str, Any] = None) -> Any:
        """
        Create a Fusion node in the given composition.

        Args:
            comp: The Fusion composition to add the node to.
            node_type (str): The type of node to create (e.g., 'Blur', 'ColorCorrector').
            inputs (Dict[str, Any], optional): Dictionary of input parameters for the node.

        Returns:
            Any: The created node, or None if unsuccessful.
        """
        if not self.fusion or not comp:
            return None

        try:
            # Create the node in the composition
            node = comp.AddTool(node_type)

            # Set input parameters if provided
            if inputs and node:
                for key, value in inputs.items():
                    node[key] = value

            return node
        except Exception as e:
            logger.exception("Error creating Fusion node: %s", e)
            return None

    def get_current_comp(self) -> Any:
        """
        Get the current Fusion composition.

        Returns:
            Any: The current Fusion composition, or None if not available.
        """
        if not self.fusion:
            return None

        try:
            return self.fusion.CurrentComp
        except Exception as e:
            logger.exception("Error getting current composition: %s", e)
            return None
