"""Minimal configuration reader for patch and launch functionality.

This module provides basic configuration reading without the full OneLauncher
dependency tree.
"""

import logging
import tomllib
from pathlib import Path
from typing import Dict, Any, Optional
import platformdirs

logger = logging.getLogger(__name__)


class SimpleGameConfig:
    """Simplified game configuration for patch and launch."""
    
    def __init__(self, game_directory: Path, game_type: str = "LOTRO", 
                 patch_client_filename: str = "PatchClient.dll",
                 high_res_enabled: bool = True,
                 language: str = "English"):
        self.game_directory = Path(game_directory)
        self.game_type = game_type
        self.patch_client_filename = patch_client_filename
        self.high_res_enabled = high_res_enabled
        self.language = language


def find_onelauncher_config() -> Optional[Path]:
    """Find the OneLauncher configuration file."""
    # Standard OneLauncher config paths
    possible_paths = [
        platformdirs.user_config_path("OneLauncher") / "onelauncher.toml",
        Path.home() / ".config" / "onelauncher.toml",
        Path("onelauncher.toml"),  # Current directory fallback
    ]
    
    for path in possible_paths:
        if path.exists():
            return path
    
    return None


def read_game_config_from_onelauncher() -> Optional[SimpleGameConfig]:
    """Read game configuration from existing OneLauncher config."""
    config_path = find_onelauncher_config()
    if not config_path:
        logger.warning("OneLauncher configuration file not found")
        return None
    
    try:
        with open(config_path, "rb") as f:
            config_data = tomllib.load(f)
        
        # Extract the first LOTRO game configuration
        games = config_data.get("games", {})
        for game_id, game_config in games.items():
            if game_config.get("game_type") == "LOTRO":
                game_dir = game_config.get("game_directory")
                if game_dir:
                    return SimpleGameConfig(
                        game_directory=Path(game_dir),
                        game_type=game_config.get("game_type", "LOTRO"),
                        patch_client_filename=game_config.get("patch_client_filename", "PatchClient.dll"),
                        high_res_enabled=game_config.get("high_res_enabled", True),
                        language=game_config.get("locale", {}).get("game_language_name", "English")
                    )
        
        logger.warning("No LOTRO game configuration found in OneLauncher config")
        return None
        
    except Exception as e:
        logger.error(f"Failed to read OneLauncher configuration: {e}")
        return None


def create_config_from_args(game_directory: str, language: str = "English", 
                           high_res: bool = True) -> SimpleGameConfig:
    """Create game configuration from command line arguments."""
    return SimpleGameConfig(
        game_directory=Path(game_directory),
        language=language,
        high_res_enabled=high_res
    )