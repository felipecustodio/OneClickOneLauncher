# Decoupled Exe Generation

This directory contains the decoupled executable generation for OneLauncher's patch and launch functionality.

## Background

The original exe generation process bundled the entire OneLauncher application into a single executable, resulting in:
- Large executable size (50+ MB)
- Download errors during patching
- Complex dependency management
- Slow build times

## Solution

The exe generation has been decoupled into its own Python project with:
- Minimal dependencies (only `platformdirs`, `defusedxml`, `httpx`)
- Self-contained functionality
- Much smaller executable size (~7MB)
- Improved reliability

## Files

- `standalone_patch_and_launch.py` - Main script with all functionality in one file
- `standalone.spec` - PyInstaller specification for building the executable
- `run_patch_client/` - Copy of the Windows patch client runner
- `pyproject.toml` - Project configuration for the decoupled project

## Usage

### Command Line
```bash
cd oneclick_launcher
python standalone_patch_and_launch.py --help
```

### Building Executable
```bash
cd oneclick_launcher
pyinstaller standalone.spec
```

The built executable will be in `dist/oneclick_launcher.exe` (on Windows) or `dist/oneclick_launcher` (on Linux).

## Features

- Automatic detection of OneLauncher configuration
- Command-line override options
- Support for multiple patch servers
- Comprehensive error handling and logging
- Minimal memory footprint

## Compatibility

The decoupled version maintains full compatibility with existing OneLauncher configurations while providing the option to specify game directories manually via command-line arguments.