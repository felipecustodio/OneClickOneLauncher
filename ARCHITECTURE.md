# OneLauncher Architecture

This document provides architectural diagrams and documentation for the OneLauncher codebase.

## Repository Structure

The following diagram shows the organization of the codebase and where each functionality lives:

```mermaid
graph TB
    subgraph "Repository Root"
        A[README.md] 
        B[CONTRIBUTING.md]
        C[pyproject.toml - Project Config]
        D[uv.lock - Dependencies]
        E1[ARCHITECTURE.md - This Document]
    end
    
    subgraph "src/onelauncher/ - Main Application"
        E[__main__.py] --> F[cli.py - CLI Interface]
        F --> G[main_window.py - Main UI Window]
        
        subgraph "Configuration System"
            H[config_manager.py - Central Config Management]
            I[game_config.py - Game Settings] 
            J[program_config.py - App Settings]
            K[game_account_config.py - User Accounts]
            L[config.py - Base Config Classes]
            H --> I
            H --> J
            H --> K
            H --> L
        end
        
        subgraph "Addon Management System"
            M[addon_manager.py - Main Addon UI]
            N[addons/config.py - Addon Config]
            O[addons/startup_script.py - Python Scripts]
            P[addons/schemas/ - XML Validation]
            M --> N
            M --> O
            N --> P
        end
        
        subgraph "Game Launching System"
            Q[start_game.py - Game Launch Logic]
            R[game_utilities.py - Game Detection]
            S[game_launcher_local_config.py]
            T[standard_game_launcher.py]
            U[official_clients.py - Client Definitions]
            Q --> R
            Q --> S
            Q --> T
            Q --> U
        end
        
        subgraph "Network Layer"
            V[network/login_account.py - Authentication]
            W[network/game_launcher_config.py - Config Download]
            X[network/game_services_info.py - Server Info]
            Y[network/world.py - Game Worlds]
            Z[network/soap.py - SOAP Services]
            AA[network/httpx_client.py - HTTP Client]
            V --> Z
            W --> AA
            X --> AA
            Y --> AA
        end
        
        subgraph "User Interface Layer"
            BB[ui/main_uic.py - Main Window UI]
            CC[ui/addon_manager_uic.py - Addon Manager UI]
            DD[ui/settings_uic.py - Settings UI]
            EE[ui/setup_wizard_uic.py - Setup Wizard UI]
            FF[ui/custom_widgets.py - Custom Qt Widgets]
            GG[ui/style.py - UI Styling]
            BB --> FF
            CC --> FF
            DD --> FF
            EE --> FF
            FF --> GG
        end
        
        subgraph "Wine Support (Linux Gaming)"
            HH[wine/config.py - Wine Settings]
            II[wine_environment.py - Wine Setup]
            HH --> II
        end
        
        subgraph "Core Utilities"
            JJ[resources.py - Localization & Resources]
            KK[utilities.py - Common Utils]
            LL[async_utils.py - Async Helpers]
            MM[qtapp.py - Qt Application Setup]
            NN[logs.py - Logging Setup]
        end
        
        subgraph "Static Resources"
            OO[images/ - Game Banners & Icons]
            PP[locale/ - Multi-language Support]
            QQ[schemas/ - XML Schema Files]
        end
    end
    
    subgraph "tests/ - Test Suite"
        RR[Unit Tests]
        SS[Integration Tests]
    end
    
    subgraph "Build & Tools"
        TT[src/run_patch_client/ - C Code for Patching]
        UU[patch_and_launch.py - Standalone Script]
    end
    
    %% Main flow connections
    G --> H
    G --> M  
    G --> Q
    G --> V
    G --> BB
    
    %% Resource connections
    JJ --> PP
    JJ --> OO
    N --> QQ
```

## Code Flow Sequence Diagrams

### Main Application Flow

The following sequence diagram shows the main execution flow of OneLauncher:

```mermaid
sequenceDiagram
    participant User
    participant CLI as cli.py
    participant ConfigMgr as config_manager.py
    participant SetupWiz as setup_wizard.py
    participant MainWin as main_window.py
    participant Network as network/*
    participant GameLauncher as start_game.py
    participant Wine as wine_environment.py
    
    User->>CLI: onelauncher command
    CLI->>CLI: setup_application_logging()
    CLI->>ConfigMgr: create ConfigManager
    CLI->>ConfigMgr: verify_configs()
    
    alt Config Invalid/Missing
        ConfigMgr->>SetupWiz: launch setup wizard
        SetupWiz->>User: collect game directories
        SetupWiz->>SetupWiz: detect LOTRO/DDO installations
        SetupWiz->>ConfigMgr: save initial config
    end
    
    CLI->>MainWin: create MainWindow(config_manager)
    MainWin->>MainWin: InitialSetup() [async]
    MainWin->>ConfigMgr: get_game_config_ids()
    MainWin->>MainWin: loadAllSavedAccounts()
    MainWin->>MainWin: setup_game()
    
    par Network Setup
        MainWin->>Network: GameServicesInfo.from_url()
        Network-->>MainWin: game services info
        MainWin->>MainWin: load_worlds_list()
        MainWin->>Network: GameLauncherConfig.from_url()
        Network-->>MainWin: launcher config
        MainWin->>Network: load_newsfeed()
    end
    
    User->>MainWin: select account & launch game
    MainWin->>GameLauncher: start_game()
    GameLauncher->>Network: get_launch_args()
    GameLauncher->>GameLauncher: apply_patches()
    
    alt Linux Platform
        GameLauncher->>Wine: edit_qprocess_to_use_wine()
        Wine->>Wine: setup Wine environment
    end
    
    GameLauncher->>GameLauncher: run startup scripts
    GameLauncher->>GameLauncher: launch game executable
    GameLauncher-->>User: game starts
```

### Addon Management Flow

The following diagram shows the detailed addon management workflow:

```mermaid
sequenceDiagram
    participant User
    participant MainWin as main_window.py
    participant AddonMgr as addon_manager.py
    participant Network as network/httpx_client.py
    participant FileSystem as File System
    participant Compendium as addons/config.py
    participant StartupScript as addons/startup_script.py
    
    User->>MainWin: click "Manage Add-ons"
    MainWin->>AddonMgr: AddonManagerWindow()
    AddonMgr->>AddonMgr: setupUi()
    AddonMgr->>AddonMgr: populate_tables()
    
    par Load Installed Addons
        AddonMgr->>FileSystem: scan addon directories
        FileSystem-->>AddonMgr: installed addon files
        AddonMgr->>Compendium: parse .compendium files
        Compendium-->>AddonMgr: addon metadata
    and Load Remote Addons
        AddonMgr->>Network: fetch LOTROInterface feed
        Network-->>AddonMgr: XML addon list
        AddonMgr->>AddonMgr: parse remote addon data
    end
    
    User->>AddonMgr: select addon to install
    AddonMgr->>Network: download addon archive
    Network-->>AddonMgr: addon .zip file
    AddonMgr->>FileSystem: extract to game directory
    AddonMgr->>Compendium: validate compendium file
    
    alt Has Dependencies
        AddonMgr->>AddonMgr: resolve dependencies
        loop Each Dependency
            AddonMgr->>Network: download dependency
            AddonMgr->>FileSystem: install dependency
        end
    end
    
    alt Has Startup Script
        AddonMgr->>StartupScript: register startup script
        Note over StartupScript: Script will run at game launch
    end
    
    AddonMgr->>AddonMgr: refresh_ui_data()
    AddonMgr-->>User: installation complete
```

### Configuration Management Flow

The following diagram shows how configuration is managed throughout the application:

```mermaid
sequenceDiagram
    participant App as Application Startup
    participant CM as ConfigManager
    participant Files as Config Files (TOML)
    participant Keyring as System Keyring
    participant SetupWiz as Setup Wizard
    
    App->>CM: ConfigManager()
    CM->>Files: load program config
    CM->>Files: load game configs
    
    alt Config Missing/Invalid
        CM->>SetupWiz: launch setup wizard
        SetupWiz->>SetupWiz: detect game installations
        SetupWiz->>CM: create initial configs
        CM->>Files: save new configs
    end
    
    CM->>CM: verify_configs()
    CM->>Keyring: load saved passwords
    
    loop For Each Game Config
        CM->>Files: load game-specific settings
        CM->>CM: validate game directory
        CM->>CM: load addon configurations
    end
    
    CM-->>App: ready for use
    
    Note over CM: Configuration is live-reloaded<br/>when files change on disk
```

## Async Architecture

OneLauncher uses a sophisticated async architecture combining Qt's event loop with Trio for structured concurrency:

```mermaid
graph TB
    subgraph "Qt Event Loop"
        A[QApplication.exec]
        B[Qt Events]
        C[UI Updates]
    end
    
    subgraph "Trio Async Layer"
        D[AsyncHelper]
        E[trio.open_nursery]
        F[Network Operations]
        G[File Operations]
    end
    
    subgraph "Integration Bridge"
        H[async_utils.py]
        I[Event Loop Integration]
        J[Signal/Slot Bridges]
    end
    
    A --> B
    B --> C
    D --> E
    E --> F
    E --> G
    H --> I
    I --> J
    D --> H
    H --> A
    
    F --> |Network Results| C
    G --> |File Results| C
```

## Key Architecture Components

### Entry Points
- **`__main__.py`**: Simple entry point that imports and runs the CLI app
- **`cli.py`**: Main CLI interface using Typer, handles command-line arguments and launches UI

### Configuration System
- **`config_manager.py`**: Central configuration management with TOML files and live reloading
- **`game_config.py`**: Game-specific configuration (LOTRO/DDO, client types, directories)  
- **`program_config.py`**: Application-wide settings and preferences
- **`game_account_config.py`**: User account management with secure keyring integration

### Addon Management
- **`addon_manager.py`**: Core addon functionality - install, update, manage plugins/skins/music
- **`addons/config.py`**: Addon configuration structures and compendium parsing
- **`addons/startup_script.py`**: Python script execution at game launch with sandboxed globals
- **`addons/schemas/`**: XML schema validation for compendium files and addon metadata

### Game Launching
- **`start_game.py`**: Main game launching logic with patching and Wine support
- **`game_utilities.py`**: Utilities for finding and validating game installations
- **`official_clients.py`**: Definitions for official LOTRO/DDO clients and their capabilities

### Network Layer  
- **`network/login_account.py`**: User authentication with game services via SOAP
- **`network/game_launcher_config.py`**: Download launcher configuration from official servers
- **`network/world.py`**: Game world/server management and selection
- **`network/soap.py`**: SOAP service communication with authentication servers

### User Interface
- **`main_window.py`**: Primary application window with account selection and game launching
- **`ui/`**: Qt-based UI components compiled from .ui files using pyside6-uic
- **`setup_wizard.py`**: First-time setup wizard for new users

### Cross-Platform Support
- **`wine/`**: Wine configuration and environment setup for Linux gaming
- **`resources.py`**: Localization and resource management with multi-language support

### Utilities
- **`async_utils.py`**: Trio-based async helpers for Qt integration using structured concurrency
- **`qtapp.py`**: Qt application setup, styling, and theme management
- **`utilities.py`**: Common utility functions and classes including path helpers

## File Organization Patterns

The codebase follows clear organizational patterns:

### Configuration Files
```
~/.config/onelauncher.toml          # Main program configuration
~/.local/share/OneLauncher/games/   # Game-specific configurations
```

### Addon Structure
```
Documents/The Lord of the Rings Online/
├── Plugins/
│   ├── PluginName/
│   │   ├── PluginName.plugin
│   │   └── PluginName.plugincompendium
│   └── ...
├── Skins/
└── Music/
```

### UI Component Organization
```
ui/
├── *.ui                 # Qt Designer files
├── *_uic.py            # Compiled UI files (auto-generated)
├── custom_widgets.py   # Custom Qt components
└── style.py           # Theming and styling
```

## Data Flow

1. **Configuration**: TOML files store all settings, managed centrally by ConfigManager
2. **Authentication**: Credentials stored securely in system keyring, validated via SOAP services
3. **Addons**: XML compendium files describe addon metadata, installed to game directories
4. **Game Launching**: Patches applied, Wine configured (Linux), startup scripts executed
5. **Network**: HTTPS/SOAP communication with official game services for auth and updates

## Key Design Patterns

- **Configuration as Code**: Strongly-typed configuration with attrs/cattrs for serialization
- **Async/Await**: Trio for concurrent operations within Qt event loop using structured concurrency
- **Plugin Architecture**: Extensible addon system with startup scripts and dependency resolution
- **Cross-Platform**: Abstracted Wine integration for seamless Linux gaming support
- **Type Safety**: Heavy use of mypy and type annotations throughout for reliability
- **Separation of Concerns**: Clear module boundaries between UI, business logic, and data access