# OneLauncher Architecture

This document provides architectural diagrams and documentation for the OneLauncher codebase.

## Repository Structure

The following diagram shows the organization of the codebase and where each functionality lives:

```mermaid
graph TB
    subgraph "Repository Root"
        A[README.md] 
        B[CONTRIBUTING.md]
        C[pyproject.toml]
        D[uv.lock]
    end
    
    subgraph "src/onelauncher/"
        E[__main__.py - Entry Point]
        F[cli.py - CLI Interface]
        G[main_window.py - Main UI]
        
        subgraph "Configuration Management"
            H[config_manager.py]
            I[game_config.py]
            J[program_config.py]
            K[game_account_config.py]
            L[config.py]
        end
        
        subgraph "Addon System"
            M[addon_manager.py]
            N[addons/config.py]
            O[addons/startup_script.py]
            P[addons/schemas/ - XML Schemas]
        end
        
        subgraph "Game Management"
            Q[start_game.py]
            R[game_utilities.py]
            S[game_launcher_local_config.py]
            T[standard_game_launcher.py]
            U[official_clients.py]
        end
        
        subgraph "Network Operations"
            V[network/login_account.py]
            W[network/game_launcher_config.py]
            X[network/game_services_info.py]
            Y[network/world.py]
            Z[network/soap.py]
            AA[network/httpx_client.py]
        end
        
        subgraph "User Interface"
            BB[ui/main_uic.py]
            CC[ui/addon_manager_uic.py]
            DD[ui/settings_uic.py]
            EE[ui/setup_wizard_uic.py]
            FF[ui/custom_widgets.py]
            GG[ui/style.py]
        end
        
        subgraph "Wine Support (Linux)"
            HH[wine/config.py]
            II[wine_environment.py]
        end
        
        subgraph "Core Utilities"
            JJ[resources.py - Localization]
            KK[utilities.py]
            LL[async_utils.py]
            MM[qtapp.py]
            NN[logs.py]
        end
        
        subgraph "Resources"
            OO[images/ - Game Banners & Icons]
            PP[locale/ - Multi-language Support]
            QQ[schemas/ - XML Validation]
        end
    end
    
    subgraph "tests/"
        RR[Unit Tests]
    end
    
    subgraph "External Tools"
        SS[src/run_patch_client/ - C Code]
        TT[patch_and_launch.py - Standalone Script]
    end
    
    E --> F
    F --> G
    G --> H
    G --> M
    G --> Q
    M --> N
    M --> O
    Q --> R
    V --> W
    V --> Z
    G --> BB
    BB --> CC
    BB --> DD
    BB --> EE
```

## Code Flow Sequence Diagram

The following sequence diagram shows the main execution flow of OneLauncher:

```mermaid
sequenceDiagram
    participant User
    participant CLI as cli.py
    participant ConfigMgr as config_manager.py
    participant SetupWiz as setup_wizard.py
    participant MainWin as main_window.py
    participant AddonMgr as addon_manager.py
    participant Network as network/*
    participant GameLauncher as start_game.py
    participant Wine as wine_environment.py
    
    User->>CLI: onelauncher command
    CLI->>CLI: setup_application_logging()
    CLI->>ConfigMgr: create ConfigManager
    
    alt Config Invalid/Missing
        ConfigMgr->>SetupWiz: launch setup wizard
        SetupWiz->>User: collect game directories
        SetupWiz->>ConfigMgr: save initial config
    end
    
    CLI->>MainWin: create MainWindow
    MainWin->>ConfigMgr: load game configs
    MainWin->>MainWin: InitialSetup()
    MainWin->>MainWin: loadAllSavedAccounts()
    MainWin->>MainWin: setup_game()
    
    User->>MainWin: select account & game
    MainWin->>Network: verify account credentials
    Network-->>MainWin: authentication result
    
    alt Manage Addons
        User->>MainWin: open addon manager
        MainWin->>AddonMgr: launch addon manager
        AddonMgr->>Network: check for addon updates
        AddonMgr->>AddonMgr: install/update addons
        AddonMgr->>AddonMgr: process compendium files
    end
    
    User->>MainWin: launch game
    MainWin->>GameLauncher: start_game()
    GameLauncher->>Network: get launcher config
    GameLauncher->>GameLauncher: apply patches
    
    alt Linux Platform
        GameLauncher->>Wine: setup Wine environment
        Wine->>Wine: configure Wine prefix
    end
    
    GameLauncher->>AddonMgr: run startup scripts
    AddonMgr->>AddonMgr: execute Python startup scripts
    GameLauncher->>GameLauncher: launch game executable
    GameLauncher-->>User: game starts
```

## Key Architecture Components

### Entry Points
- **`__main__.py`**: Simple entry point that imports and runs the CLI app
- **`cli.py`**: Main CLI interface using Typer, handles command-line arguments and launches UI

### Configuration System
- **`config_manager.py`**: Central configuration management with TOML files
- **`game_config.py`**: Game-specific configuration (LOTRO/DDO, client types, directories)  
- **`program_config.py`**: Application-wide settings
- **`game_account_config.py`**: User account management with keyring integration

### Addon Management
- **`addon_manager.py`**: Core addon functionality - install, update, manage plugins/skins/music
- **`addons/config.py`**: Addon configuration structures
- **`addons/startup_script.py`**: Python script execution at game launch
- **`addons/schemas/`**: XML schema validation for compendium files

### Game Launching
- **`start_game.py`**: Main game launching logic with patching and Wine support
- **`game_utilities.py`**: Utilities for finding and validating game installations
- **`official_clients.py`**: Definitions for official LOTRO/DDO clients

### Network Layer
- **`network/login_account.py`**: User authentication with game services
- **`network/game_launcher_config.py`**: Download launcher configuration from servers
- **`network/world.py`**: Game world/server management
- **`network/soap.py`**: SOAP service communication

### User Interface
- **`main_window.py`**: Primary application window with account selection and game launching
- **`ui/`**: Qt-based UI components compiled from .ui files
- **`setup_wizard.py`**: First-time setup for new users

### Cross-Platform Support
- **`wine/`**: Wine configuration and environment setup for Linux gaming
- **`resources.py`**: Localization and resource management

### Utilities
- **`async_utils.py`**: Trio-based async helpers for Qt integration
- **`qtapp.py`**: Qt application setup and styling
- **`utilities.py`**: Common utility functions and classes

## Data Flow

1. **Configuration**: TOML files store all settings, managed by ConfigManager
2. **Authentication**: Credentials stored in system keyring, validated via network layer
3. **Addons**: XML compendium files describe addon metadata, installed to game directories
4. **Game Launching**: Patches applied, Wine configured (Linux), startup scripts executed
5. **Network**: HTTPS/SOAP communication with official game services

## Key Design Patterns

- **Configuration as Code**: Strongly-typed configuration with attrs/cattrs
- **Async/Await**: Trio for concurrent operations within Qt event loop
- **Plugin Architecture**: Extensible addon system with startup scripts
- **Cross-Platform**: Abstracted Wine integration for Linux support
- **Type Safety**: Heavy use of mypy and type annotations throughout