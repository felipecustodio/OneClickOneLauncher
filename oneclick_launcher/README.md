# OneClick Launcher

A lightweight standalone executable for patching and launching LOTRO games.

This is a decoupled version of the patch and launch functionality from OneLauncher, 
designed to create a small, standalone executable without bundling the entire 
OneLauncher application.

## Features

- Reads existing OneLauncher configuration
- Patches LOTRO game files
- Launches the standard game launcher
- Minimal dependencies for small executable size

## Building

Use PyInstaller to build the standalone executable:

```bash
pyinstaller patch_and_launch.spec
```