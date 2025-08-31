"""Simplified game launcher functionality.

This module provides basic game launching functionality without complex
network configuration discovery.
"""

import logging
import subprocess
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class SimpleGameLauncher:
    """Simplified game launcher that finds standard launcher executables."""
    
    def __init__(self, game_config):
        self.game_config = game_config
    
    def find_launcher_executable(self) -> Optional[Path]:
        """Find the game's standard launcher executable."""
        game_dir = self.game_config.game_directory
        
        # Common LOTRO launcher filenames
        if self.game_config.game_type == "LOTRO":
            launcher_names = [
                "LotroLauncher.exe",
                "lotrolauncher.exe",
                "TurbineLauncher.exe",
                "turbinelauncher.exe"
            ]
        elif self.game_config.game_type == "DDO":
            launcher_names = [
                "DNDLauncher.exe",
                "dndlauncher.exe",
                "TurbineLauncher.exe",
                "turbinelauncher.exe"
            ]
        else:
            launcher_names = ["TurbineLauncher.exe", "launcher.exe"]
        
        # Try exact filename matches first
        for launcher_name in launcher_names:
            launcher_path = game_dir / launcher_name
            if launcher_path.exists():
                return launcher_path
        
        # Fallback: search for any file ending with "launcher.exe"
        for file_path in game_dir.iterdir():
            if (file_path.is_file() and 
                file_path.name.lower().endswith("launcher.exe")):
                return file_path
        
        return None
    
    def launch_game(self) -> bool:
        """Launch the game's standard launcher."""
        launcher_path = self.find_launcher_executable()
        
        if not launcher_path:
            logger.error(f"No launcher executable found in {self.game_config.game_directory}")
            return False
        
        try:
            logger.info(f"Launching game with: {launcher_path}")
            subprocess.Popen(
                [str(launcher_path)],
                cwd=self.game_config.game_directory
            )
            logger.info("Game launcher started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to launch game: {e}")
            return False