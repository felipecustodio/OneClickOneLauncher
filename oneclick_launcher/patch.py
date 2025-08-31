"""Simplified patch client functionality.

This module provides basic patching functionality without the complex
network service discovery from OneLauncher.
"""

import logging
import subprocess
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class SimplePatchClient:
    """Simplified patch client that uses hardcoded patch servers."""
    
    # Known LOTRO patch servers (these are the most commonly used)
    LOTRO_PATCH_SERVERS = [
        "http://patchdata.lotrocloud.com",
        "http://proddata.ddo.com/lotro",
    ]
    
    def __init__(self, game_config):
        self.game_config = game_config
        
    def find_patch_client_runner(self) -> Optional[Path]:
        """Find the patch client runner executable."""
        # First try relative to this script (bundled with PyInstaller)
        script_dir = Path(__file__).parent if "__file__" in globals() else Path(".")
        possible_paths = [
            script_dir / "run_patch_client" / "run_ptch_client.exe",
            script_dir.parent / "run_patch_client" / "run_ptch_client.exe",
            script_dir.parent / "src" / "run_patch_client" / "run_ptch_client.exe",
            Path("run_ptch_client.exe"),  # Current directory
        ]
        
        for path in possible_paths:
            if path.exists():
                return path
        
        return None
    
    def find_patch_client_dll(self) -> Optional[Path]:
        """Find the game's patch client DLL."""
        patch_client_path = self.game_config.game_directory / self.game_config.patch_client_filename
        return patch_client_path if patch_client_path.exists() else None
    
    def run_patch_phase(self, patch_server: str, phase: str) -> bool:
        """Run a single patch phase."""
        patch_runner = self.find_patch_client_runner()
        patch_dll = self.find_patch_client_dll()
        
        if not patch_runner:
            logger.error("Patch client runner not found")
            return False
            
        if not patch_dll:
            logger.error(f"Patch client DLL not found at {self.game_config.game_directory / self.game_config.patch_client_filename}")
            return False
        
        # Build command
        base_cmd = [str(patch_runner), str(patch_dll)]
        args = [patch_server, "--language", self.game_config.language]
        
        if self.game_config.high_res_enabled:
            args.append("--highres")
        
        args.append(phase)
        
        try:
            logger.info(f"Running patch phase {phase} with server {patch_server}")
            result = subprocess.run(
                base_cmd + args,
                check=True,
                cwd=self.game_config.game_directory,
                capture_output=True,
                text=True
            )
            logger.info(f"Patch phase {phase} completed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Patch phase {phase} failed: {e}")
            logger.error(f"Stdout: {e.stdout}")
            logger.error(f"Stderr: {e.stderr}")
            return False
    
    def patch_game(self) -> bool:
        """Run the complete patching process."""
        logger.info("Starting game patching process")
        
        # Try each patch server until one works
        for patch_server in self.LOTRO_PATCH_SERVERS:
            logger.info(f"Trying patch server: {patch_server}")
            
            # Run both patch phases
            if (self.run_patch_phase(patch_server, "--filesonly") and 
                self.run_patch_phase(patch_server, "--dataonly")):
                logger.info("Patching completed successfully")
                return True
            else:
                logger.warning(f"Patching failed with server {patch_server}, trying next server")
        
        logger.error("All patch servers failed")
        return False