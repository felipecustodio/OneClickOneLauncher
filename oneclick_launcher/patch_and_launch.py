#!/usr/bin/env python3
"""Lightweight patch and launch utility for LOTRO.

This standalone script provides patch and launch functionality without
the full OneLauncher application dependencies, resulting in a much smaller
executable.
"""

import argparse
import logging
import sys
from pathlib import Path

from oneclick_launcher.config import read_game_config_from_onelauncher, create_config_from_args
from oneclick_launcher.patch import SimplePatchClient
from oneclick_launcher.launcher import SimpleGameLauncher


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