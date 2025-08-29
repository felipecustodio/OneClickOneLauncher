# OneLauncher Development Instructions

OneLauncher is a Python GUI application built with PySide6 (Qt) that serves as an enhanced launcher for LOTRO and DDO games with addon management capabilities. The application compiles to native executables using Nuitka.

Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.

## Working Effectively

### Bootstrap and Install Dependencies
- `sudo apt-get install -y mingw-w64 libgl1 libegl1 libxrandr2 libxss1 libxcursor1 libxcomposite1 libasound2t64 libxi6 libxtst6 qt6-qpa-plugins libxcb-cursor0 xvfb` -- Install required system dependencies for Linux development (includes GUI libraries and cross-compilation tools)
- `pip install uv` -- Install uv package manager if not already available
- `uv sync` -- Install Python dependencies from lock file (takes about 6 seconds)

### Development and Testing
- `uv run onelauncher --help` -- Test that the application runs correctly (requires `export DISPLAY=:99 && xvfb-run -a` prefix in headless environments)
- `uv run onelauncher` -- Start the application in development mode
- `uv run pytest tests/ -v` -- Run test suite (takes about 3-4 seconds, 49 tests). NEVER CANCEL.
- `uv run ruff check` -- Run linting (takes less than 1 second)
- `uv run ruff check --fix` -- Auto-fix linting issues
- `uv run mypy` -- Run type checking (takes less than 1 second)

### Build Process
- `make -C src/run_patch_client` -- Compile C code for game patching (requires mingw-w64, takes less than 1 second)
- `uv run python -m build` -- Build complete application with Nuitka compilation. **NEVER CANCEL: Takes 15-20 minutes. Set timeout to 25+ minutes.** Outputs to `build/out/onelauncher.bin`

### UI Development
- `uv run onelauncher designer` -- Launch pyside6-designer with OneLauncher plugins enabled
- `uv run pyside6-uic src/onelauncher/ui/example_window.ui -o src/onelauncher/ui/example_window_uic.py` -- Compile .ui files to Python (replace "example_window" with actual file name)

## Validation

### Manual Testing Requirements
- **ALWAYS** test the application help command after making changes: `export DISPLAY=:99 && xvfb-run -a uv run onelauncher --help`
- Test the compiled binary after building: `export DISPLAY=:99 && xvfb-run -a ./build/out/onelauncher.bin --help`
- **CRITICAL**: After GUI changes, always start the application to verify it launches without errors
- You can build and run both the development version and compiled version, but GUI interaction requires a display server
- Test with virtual display in headless environments: `export DISPLAY=:99 && xvfb-run -a [command]`

### Pre-commit Validation
- **ALWAYS** run `uv run ruff check --fix` and `uv run mypy` before committing changes
- **ALWAYS** run `uv run pytest tests/ -v` to ensure tests pass
- The application uses strict type checking with Mypy and strict linting with Ruff

## Critical Timing and Timeout Information

### Build Commands (NEVER CANCEL)
- `uv run python -m build` -- **NEVER CANCEL: Takes 15-20 minutes.** Use timeout of 25+ minutes minimum
- Nuitka compilation is CPU-intensive and may appear to hang but is working normally
- The build creates a 60MB+ binary executable

### Fast Commands (Under 10 seconds)
- `uv sync` -- 6 seconds
- `uv run pytest tests/ -v` -- 3-4 seconds  
- `make -C src/run_patch_client` -- Less than 1 second
- `uv run ruff check` -- Less than 1 second
- `uv run mypy` -- Less than 1 second

## Common Tasks and File Locations

### Key Project Directories
```
src/onelauncher/           # Main application source code
src/onelauncher/ui/        # UI files (.ui) and compiled Python UI files (*_uic.py)
src/run_patch_client/      # C code for game patching functionality
tests/                     # pytest test suite
build/                     # Build scripts and output directory
locale/                    # Translation files
.github/workflows/         # CI/CD pipelines
```

### Critical Files
- `pyproject.toml` -- Project configuration, dependencies, and tool settings
- `src/onelauncher/cli.py` -- Command-line interface entry point
- `src/onelauncher/main_window.py` -- Main GUI window
- `src/run_patch_client/Makefile` -- C code build configuration
- `build/__main__.py` -- Main build script that orchestrates Nuitka compilation

### Dependency Management
- The project uses `uv` for Python dependency management with a lockfile
- Some dependencies are from custom Git forks (zeep, asyncache)
- GUI requires PySide6-Essentials, Qt6 platform plugins, and system graphics libraries

### Architecture Notes
- Python 3.12+ application with strict type checking
- Qt6/PySide6 for cross-platform GUI
- Nuitka for native executable compilation
- mingw-w64 for Windows-compatible C code compilation on Linux
- Supports both LOTRO and DDO games with WINE integration for Linux

## Troubleshooting

### Common Issues
- **GUI fails to start**: Ensure all system graphics libraries are installed, especially `libxcb-cursor0`
- **Build takes too long**: This is normal - Nuitka compilation is very slow. Never cancel builds.
- **C compilation fails**: Ensure mingw-w64 is installed with i686 support
- **Tests fail in headless environment**: Use xvfb virtual display: `export DISPLAY=:99 && xvfb-run -a [command]`

### Linting Errors
- Run `uv run ruff check --fix` to auto-fix many issues (fixes about 34 of 50 typical issues)
- The project uses strict linting rules - some UP040 (TypeAlias), ANN (annotations), and S603 (subprocess) warnings may remain unfixable
- All code must pass both Ruff and Mypy checks for CI/CD

This application compiles and runs successfully on Linux. The development workflow is reliable when proper timeouts are used for the build process.