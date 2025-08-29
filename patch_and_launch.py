"""Patch and launch LOTRO in one step.

This helper script reads existing OneLauncher configuration to find the
installed game, runs the game's patch client and then starts the standard
launcher.  It can be bundled with PyInstaller to create a stand‑alone
executable.
"""

from __future__ import annotations

import asyncio
import logging
import subprocess
from pathlib import Path

from onelauncher.config_manager import ConfigManager
from onelauncher.game_config import GameConfig, GameType
from onelauncher.network.game_services_info import GameServicesInfo
from onelauncher.resources import data_dir
from onelauncher.standard_game_launcher import get_standard_game_launcher_path


logging.basicConfig(
    filename="patch_and_launch.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    filemode="a",
)
logger = logging.getLogger(__name__)


def _identity(config):
    return config


async def patch_game(
    game_config: GameConfig, *, config_manager: ConfigManager
) -> None:
    """Run the game's patch client."""
    game_services_info = await GameServicesInfo.from_game_config(game_config)
    if game_services_info is None:
        raise RuntimeError("Unable to determine patch server")

    patch_client_runner = data_dir.parent / "run_patch_client" / "run_ptch_client.exe"
    patch_client = game_config.game_directory / game_config.patch_client_filename
    if not patch_client_runner.exists():
        raise FileNotFoundError(patch_client_runner)
    if not patch_client.exists():
        raise FileNotFoundError(patch_client)

    language = (
        game_config.locale.game_language_name
        if game_config.locale
        else config_manager.get_program_config().default_locale.game_language_name
    )
    base_cmd = [str(patch_client_runner), str(patch_client)]
    args = [game_services_info.patch_server, "--language", language]
    if game_config.high_res_enabled:
        args.append("--highres")

    for phase in ("--filesonly", "--dataonly"):
        subprocess.run(
            base_cmd + args + [phase],
            check=True,
            cwd=game_config.game_directory,
        )


async def launch_game(game_config: GameConfig) -> None:
    """Start the game's standard launcher."""
    launcher_path = await get_standard_game_launcher_path(game_config)
    if launcher_path is None:
        raise RuntimeError("Unable to locate game launcher")
    subprocess.Popen([str(launcher_path)], cwd=game_config.game_directory)


async def main() -> None:
    config_manager = ConfigManager(
        get_merged_program_config=_identity,
        get_merged_game_config=_identity,
        get_merged_game_accounts_config=_identity,
    )
    config_manager.verify_configs()

    lotro_games = config_manager.get_games_by_game_type(GameType.LOTRO)
    if not lotro_games:
        logger.error("No LOTRO game configuration found")
        return

    game_id = lotro_games[0]
    game_config = config_manager.get_game_config(game_id)
    await patch_game(game_config, config_manager=config_manager)
    await launch_game(game_config)


if __name__ == "__main__":
    asyncio.run(main())
