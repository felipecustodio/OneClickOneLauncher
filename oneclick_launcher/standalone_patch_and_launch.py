#!/usr/bin/env python3
"""Lightweight standalone patch and launch utility for LOTRO.

This standalone script provides patch and launch functionality without
the full OneLauncher application dependencies, resulting in a much smaller
executable.
"""

import argparse
import logging
import sys
import tomllib
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional
import platformdirs


def setup_logging(verbose: bool = False) -> None:
    """Set up logging configuration."""
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler("patch_and_launch.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )


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
        logging.warning("OneLauncher configuration file not found")
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
        
        logging.warning("No LOTRO game configuration found in OneLauncher config")
        return None
        
    except Exception as e:
        logging.error(f"Failed to read OneLauncher configuration: {e}")
        return None


def create_config_from_args(game_directory: str, language: str = "English", 
                           high_res: bool = True) -> SimpleGameConfig:
    """Create game configuration from command line arguments."""
    return SimpleGameConfig(
        game_directory=Path(game_directory),
        language=language,
        high_res_enabled=high_res
    )


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
            logging.error("Patch client runner not found")
            return False
            
        if not patch_dll:
            logging.error(f"Patch client DLL not found at {self.game_config.game_directory / self.game_config.patch_client_filename}")
            return False
        
        # Build command
        base_cmd = [str(patch_runner), str(patch_dll)]
        args = [patch_server, "--language", self.game_config.language]
        
        if self.game_config.high_res_enabled:
            args.append("--highres")
        
        args.append(phase)
        
        try:
            logging.info(f"Running patch phase {phase} with server {patch_server}")
            result = subprocess.run(
                base_cmd + args,
                check=True,
                cwd=self.game_config.game_directory,
                capture_output=True,
                text=True
            )
            logging.info(f"Patch phase {phase} completed successfully")
            return True
            
        except OSError as e:
            if "Exec format error" in str(e):
                logging.error("Cannot execute Windows patch client on this platform")
            else:
                logging.error(f"Failed to execute patch client: {e}")
            return False
        except subprocess.CalledProcessError as e:
            logging.error(f"Patch phase {phase} failed: {e}")
            logging.error(f"Stdout: {e.stdout}")
            logging.error(f"Stderr: {e.stderr}")
            return False
    
    def patch_game(self) -> bool:
        """Run the complete patching process."""
        logging.info("Starting game patching process")
        
        # Try each patch server until one works
        for patch_server in self.LOTRO_PATCH_SERVERS:
            logging.info(f"Trying patch server: {patch_server}")
            
            # Run both patch phases
            if (self.run_patch_phase(patch_server, "--filesonly") and 
                self.run_patch_phase(patch_server, "--dataonly")):
                logging.info("Patching completed successfully")
                return True
            else:
                logging.warning(f"Patching failed with server {patch_server}, trying next server")
        
        logging.error("All patch servers failed")
        return False


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
            logging.error(f"No launcher executable found in {self.game_config.game_directory}")
            return False
        
        try:
            logging.info(f"Launching game with: {launcher_path}")
            subprocess.Popen(
                [str(launcher_path)],
                cwd=self.game_config.game_directory
            )
            logging.info("Game launcher started successfully")
            return True
            
        except Exception as e:
            logging.error(f"Failed to launch game: {e}")
            return False


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Patch and launch LOTRO game",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                                    # Use OneLauncher config
  %(prog)s -d "C:\\Games\\LOTRO"             # Specify game directory
  %(prog)s -d "C:\\Games\\LOTRO" --no-launch # Patch only, don't launch
        """
    )
    
    parser.add_argument(
        "-d", "--directory",
        type=str,
        help="Game installation directory (if not using OneLauncher config)"
    )
    
    parser.add_argument(
        "-l", "--language",
        type=str,
        default="English",
        help="Game language (default: English)"
    )
    
    parser.add_argument(
        "--no-highres",
        action="store_true",
        help="Disable high resolution assets"
    )
    
    parser.add_argument(
        "--no-patch",
        action="store_true",
        help="Skip patching, only launch game"
    )
    
    parser.add_argument(
        "--no-launch",
        action="store_true",
        help="Only patch, don't launch game"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    return parser.parse_args()


def main() -> int:
    """Main entry point."""
    args = parse_arguments()
    setup_logging(args.verbose)
    
    logger = logging.getLogger(__name__)
    logger.info("Starting OneClick LOTRO Launcher")
    
    # Get game configuration
    if args.directory:
        # Use command line provided directory
        game_config = create_config_from_args(
            game_directory=args.directory,
            language=args.language,
            high_res=not args.no_highres
        )
        logger.info(f"Using game directory from command line: {args.directory}")
    else:
        # Try to read from OneLauncher configuration
        game_config = read_game_config_from_onelauncher()
        if not game_config:
            logger.error(
                "No OneLauncher configuration found and no game directory specified. "
                "Please use -d/--directory to specify the game installation path."
            )
            return 1
        logger.info(f"Using game directory from OneLauncher config: {game_config.game_directory}")
    
    # Verify game directory exists
    if not game_config.game_directory.exists():
        logger.error(f"Game directory does not exist: {game_config.game_directory}")
        return 1
    
    success = True
    
    # Run patching if requested
    if not args.no_patch:
        logger.info("Starting patch process...")
        patch_client = SimplePatchClient(game_config)
        success = patch_client.patch_game()
        
        if not success:
            logger.error("Patching failed")
            return 1
    else:
        logger.info("Skipping patch process")
    
    # Launch game if requested
    if not args.no_launch and success:
        logger.info("Starting game launcher...")
        game_launcher = SimpleGameLauncher(game_config)
        success = game_launcher.launch_game()
        
        if not success:
            logger.error("Failed to launch game")
            return 1
    else:
        logger.info("Skipping game launch")
    
    logger.info("OneClick LOTRO Launcher completed successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())