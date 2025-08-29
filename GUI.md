# OneLauncher GUI Architecture Documentation

This document provides comprehensive documentation about OneLauncher's Graphical User Interface (GUI) architecture, implementation, and styling system.

## Table of Contents

1. [Overview](#overview)
2. [GUI Libraries and Dependencies](#gui-libraries-and-dependencies)
3. [UI Component Structure](#ui-component-structure)
4. [Styling System](#styling-system)
5. [GUI Code Flow](#gui-code-flow)
6. [Custom Widgets](#custom-widgets)
7. [UI Development Workflow](#ui-development-workflow)
8. [Async GUI Architecture](#async-gui-architecture)

## Overview

OneLauncher's GUI is built using **PySide6** (Qt6 for Python) with a sophisticated async architecture that combines Qt's event loop with Trio for structured concurrency. The application features a modern, responsive design with a custom Tailwind-like styling system and frameless window design.

### Key Features

- **Modern Qt6/PySide6 Interface**: Native desktop application with cross-platform support
- **Frameless Window Design**: Custom window decorations for a modern look
- **Responsive Styling**: Tailwind CSS-inspired QSS (Qt Style Sheet) system
- **Async Architecture**: Non-blocking UI with Trio-based concurrency
- **Custom Widgets**: Specialized components for game launcher functionality
- **Live Style Preview**: Real-time styling updates in Qt Designer

## GUI Libraries and Dependencies

### Core GUI Libraries

```toml
# Main GUI framework
"PySide6-Essentials>=6.7.2"          # Qt6 Python bindings

# UI Enhancement libraries  
"qtawesome>=1.3.1"                   # Font Awesome icons for Qt
"pysidesix-frameless-window>=0.3.12"  # Modern frameless window support

# Additional UI-related dependencies
"Babel>=2.16.0"                       # Internationalization support
```

### Library Purposes

| Library | Purpose | Usage in OneLauncher |
|---------|---------|---------------------|
| **PySide6-Essentials** | Core Qt6 framework | Main UI framework, widgets, layouts, events |
| **qtawesome** | Icon management | Provides Font Awesome icons throughout the interface |
| **pysidesix-frameless-window** | Modern window design | Creates frameless windows with custom title bars |
| **Babel** | Internationalization | Multi-language support for UI text |

### Qt Modules Used

```python
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt, QTimer, QEventLoop
from PySide6.QtGui import QIcon, QPixmap, QFont
from PySide6.QtWidgets import QApplication, QMainWindow, QDialog
```

## UI Component Structure

OneLauncher's UI follows a structured organization pattern with clear separation between design files, compiled UI code, and custom logic.

### File Organization

```mermaid
graph TB
    subgraph "UI Directory Structure"
        A["src/onelauncher/ui/"]
        
        subgraph "Design Files"
            B["*.ui - Qt Designer files"]
            B1["main.ui"]
            B2["addon_manager.ui"] 
            B3["settings.ui"]
            B4["setup_wizard.ui"]
            B5["about.ui"]
        end
        
        subgraph "Compiled UI"
            C["*_uic.py - Generated Python"]
            C1["main_uic.py"]
            C2["addon_manager_uic.py"]
            C3["settings_uic.py"] 
            C4["setup_wizard_uic.py"]
            C5["about_uic.py"]
        end
        
        subgraph "Custom Components"
            D["custom_widgets.py"]
            E["style.py"] 
            F["qtdesigner/"]
        end
        
        subgraph "Window Classes"
            G["../main_window.py"]
            H["../addon_manager.py"]
            I["../settings_window.py"]
        end
    end
    
    B --> C
    C --> G
    C --> H
    C --> I
    D --> G
    E --> D
    F --> D
```

### Main UI Components

#### 1. Main Window (`main.ui` / `main_window.py`)
- **Purpose**: Primary application interface
- **Features**: Game selection, account management, news feed, launch controls
- **Custom Elements**: Game banner, world selection, login controls

#### 2. Addon Manager (`addon_manager.ui` / `addon_manager.py`)
- **Purpose**: Plugin/addon management interface
- **Features**: Install, update, remove addons; browse addon catalog
- **Custom Elements**: Addon tables, dependency resolution UI

#### 3. Settings Window (`settings.ui` / `settings_window.py`)
- **Purpose**: Application configuration interface
- **Features**: Game settings, UI preferences, account management
- **Custom Elements**: Tabbed settings interface

#### 4. Setup Wizard (`setup_wizard.ui`)
- **Purpose**: First-time setup and game detection
- **Features**: Game directory detection, initial configuration
- **Custom Elements**: Multi-step wizard interface

## Styling System

OneLauncher implements a sophisticated styling system inspired by Tailwind CSS, using Qt Style Sheets (QSS) with dynamic properties.

### QSS Class System

OneLauncher uses a system similar to [Tailwind CSS](https://tailwindcss.com/) for styling UIs responsively. This system provides a utility-first approach to styling widgets.

#### How It Works

The QSS class system works through Qt's dynamic property system:

1. **Dynamic Property**: The `qssClass` dynamic property is added to widgets that need styling
2. **Property Type**: This property should always be of the type **StringList** in Qt Designer
3. **Class Selection**: Each string in `qssClass` is a "class" that affects the widget's styling
4. **QSS Generation**: Classes work by being selected in dynamically generated [Qt Style Sheets](https://doc.qt.io/qt-6/stylesheet.html)
5. **Live Preview**: Changes can be previewed live in pyside6-designer when using the `onelauncher designer` command

```python
# Dynamic property used for styling, like the class attribute in HTML
CLASS_PROPERTY: str = "qssClass"
```

#### Adding QSS Classes in Qt Designer

1. Select the widget you want to style
2. In the Property Editor, right-click and select "Add Dynamic Property"
3. Choose "StringList" as the property type
4. Set the property name to `qssClass`
5. Add class names (one per line) such as:
   - `px-4` (padding-x: 1rem)
   - `py-2` (padding-y: 0.5rem)  
   - `text-lg` (font-size: large)

#### Supported Class Types

The classes are mainly used to set sizes and margins relative to the system font size. OneLauncher currently supports the following Tailwind CSS-inspired class types:

| Class Type | Purpose | Tailwind Documentation |
|------------|---------|------------------------|
| **Padding** | Internal spacing around content | [Padding Docs](https://tailwindcss.com/docs/padding) |
| **Margin** | External spacing around element | [Margin Docs](https://tailwindcss.com/docs/margin) |
| **Width** | Element width sizing | [Width Docs](https://tailwindcss.com/docs/width) |
| **Min-Width** | Minimum width constraints | [Min-Width Docs](https://tailwindcss.com/docs/min-width) |
| **Max-Width** | Maximum width constraints | [Max-Width Docs](https://tailwindcss.com/docs/max-width) |
| **Height** | Element height sizing | [Height Docs](https://tailwindcss.com/docs/height) |
| **Min-Height** | Minimum height constraints | [Min-Height Docs](https://tailwindcss.com/docs/min-height) |
| **Max-Height** | Maximum height constraints | [Max-Height Docs](https://tailwindcss.com/docs/max-height) |
| **Font-Size** | Text size styling | [Font-Size Docs](https://tailwindcss.com/docs/font-size) |
| **Icon-Size** | Custom icon sizing | OneLauncher specific |

See the [Tailwind Utility-First Documentation](https://tailwindcss.com/docs/utility-first) for more information about the utility-first approach to styling.

#### Supported Style Classes

```python
# Spacing system (rem-based)
SPACING: Final[dict[str, Rem]] = {
    "0": 0.0, "0.5": 0.125, "1": 0.25, "1.5": 0.375,
    "2": 0.5, "2.5": 0.625, "3": 0.75, "3.5": 0.875,
    "4": 1.0, "5": 1.25, "6": 1.5, "7": 1.75,
    "8": 2.0, "9": 2.25, "10": 2.5, "11": 2.75,
    "12": 3.0, "14": 3.5, "16": 4.0, "20": 5.0,
    # ... continues to "72": 18.0
}
```

#### Available Style Types

| Type | Purpose | Example Classes |
|------|---------|----------------|
| **Padding** | Internal spacing | `p-4`, `px-2`, `py-6` |
| **Margin** | External spacing | `m-4`, `mx-2`, `my-6` |
| **Width** | Element width | `w-32`, `w-full` |
| **Height** | Element height | `h-16`, `h-auto` |
| **Font Size** | Text sizing | `text-sm`, `text-lg`, `text-xl` |
| **Icon Size** | Icon dimensions | `icon-sm`, `icon-lg` |

#### Example Usage in Qt Designer

When designing a UI in Qt Designer with the QSS class system:

```xml
<!-- In .ui file -->
<widget class="QPushButton" name="btnLogin">
    <property name="qssClass" stdset="0">
        <stringlist>
            <string>px-4</string>
            <string>py-2</string>
            <string>text-lg</string>
        </stringlist>
    </property>
</widget>
```

This button will have:
- `px-4`: 1rem horizontal padding
- `py-2`: 0.5rem vertical padding  
- `text-lg`: Large font size

The `stdset="0"` attribute indicates this is a dynamic property, not a standard Qt property.

### Style Generation

```mermaid
graph LR
    A[ApplicationStyle] --> B[generate_stylesheet]
    B --> C[Font Size Classes]
    B --> D[Icon Size Classes] 
    B --> E[Spacing Classes]
    B --> F[Compiled QSS]
    F --> G[Applied to QApplication]
    
    H[Font Change Event] --> A
    I[Color Scheme Change] --> A
```

#### ApplicationStyle Class

```python
class ApplicationStyle(QtCore.QObject):
    """
    Manages app stylesheet.
    There should only ever be one instance of this class for every QApplication
    """
    
    def __init__(self, qapp: QApplication) -> None:
        super().__init__()
        self.qapp = qapp
        self.update_app_stylesheet()
        qapp.fontChanged.connect(self.update_base_font)
        qapp.styleHints().colorSchemeChanged.connect(self.update_app_stylesheet)
    
    def rem_to_px(self, rem: Rem) -> int:
        """Convert rem units to pixels based on base font size"""
        return round(self._base_font_metrics.height() * rem)
```

## GUI Code Flow

### Application Startup Flow

```mermaid
sequenceDiagram
    participant User
    participant CLI as cli.py
    participant QApp as qtapp.py
    participant Style as ApplicationStyle
    participant MainWin as MainWindow
    participant UI as main_uic.py
    
    User->>CLI: onelauncher command
    CLI->>QApp: get_qapp()
    QApp->>QApp: _setup_qapplication()
    QApp->>Style: ApplicationStyle(qapp)
    Style->>Style: generate_stylesheet()
    Style->>QApp: setStyleSheet(stylesheet)
    
    CLI->>MainWin: MainWindow(config_manager)
    MainWin->>UI: Ui_winMain()
    UI->>MainWin: setupUi(self)
    MainWin->>MainWin: InitialSetup() [async]
    
    Note over MainWin: UI setup complete
    User->>MainWin: interact with GUI
```

### UI Update Flow

```mermaid
sequenceDiagram
    participant User
    participant Widget as Qt Widget
    participant MainWin as MainWindow
    participant Network as Network Layer
    participant UI as UI Elements
    
    User->>Widget: click button/select option
    Widget->>MainWin: signal emitted
    
    alt Async Operation Needed
        MainWin->>Network: start async operation
        Network-->>MainWin: result available
        MainWin->>UI: update UI elements
    else Sync Operation
        MainWin->>UI: immediate update
    end
    
    UI-->>User: visual feedback
```

### Style Update Flow

```mermaid
sequenceDiagram
    participant System
    participant QApp as QApplication
    participant Style as ApplicationStyle
    participant Widgets as All Widgets
    
    System->>QApp: font/theme change event
    QApp->>Style: fontChanged/colorSchemeChanged signal
    Style->>Style: update_app_stylesheet()
    Style->>Style: generate_stylesheet()
    Style->>QApp: setStyleSheet(new_stylesheet)
    QApp->>Widgets: style update applied
    Widgets-->>System: visual update complete
```

### Addon Manager GUI Flow

```mermaid
sequenceDiagram
    participant User
    participant MainWin as Main Window
    participant AddonMgr as Addon Manager
    participant UI as Addon UI
    participant Network as Network
    participant FileSystem as File System
    
    User->>MainWin: click "Manage Add-ons"
    MainWin->>AddonMgr: AddonManagerWindow()
    AddonMgr->>UI: setupUi()
    AddonMgr->>UI: populate_tables()
    
    par Load Local Addons
        AddonMgr->>FileSystem: scan addon directories
        FileSystem-->>UI: update installed table
    and Load Remote Addons
        AddonMgr->>Network: fetch addon catalog
        Network-->>UI: update available table
    end
    
    User->>UI: select addon to install
    UI->>AddonMgr: install_addon()
    AddonMgr->>Network: download addon
    AddonMgr->>FileSystem: extract & install
    AddonMgr->>UI: refresh_ui_data()
    UI-->>User: installation complete
```

## Custom Widgets

OneLauncher implements several custom widgets to enhance the user experience beyond standard Qt widgets.

### FramelessQMainWindowWithStylePreview

```python
class FramelessQMainWindowWithStylePreview(
    FramelessMainWindow, QMainWindowWithStylePreview
): ...
```

**Purpose**: Combines frameless window functionality with style preview capabilities

**Features**:
- Modern frameless window design
- Custom title bar implementation
- Live style preview in Qt Designer
- Cross-platform window management

### GameNewsfeedBrowser

```python
class GameNewsfeedBrowser(QtWidgets.QTextBrowser):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.setOpenExternalLinks(True)
        self.setOpenLinks(True)
        self.html: str | None = None
        get_qapp().styleHints().colorSchemeChanged.connect(self.updateStyling)
```

**Purpose**: Specialized browser for displaying game news feeds

**Features**:
- Automatic external link handling
- Theme-aware CSS styling
- Dynamic style updates on system theme changes
- Custom news feed formatting

### NoOddSizesQToolButton

```python
class NoOddSizesQToolButton(QtWidgets.QToolButton):
    """
    Helps icon only buttons keep their icon better centered.
    """
```

**Purpose**: Improved icon-only button with better centering

**Features**:
- Better icon alignment
- Consistent sizing behavior
- Improved visual appearance

### Qt Designer Plugins

#### StylePreviewPlugin

```python
class CustomStylesheetPlugin(QtDesigner.QDesignerCustomWidgetInterface):
    def initialize(self, form_editor: QtDesigner.QDesignerFormEditorInterface) -> None:
        self._app_stylesheet = ApplicationStyle(qapp).generate_stylesheet(
            qtdesigner_version=True
        )
```

**Purpose**: Enables live style preview in Qt Designer

**Features**:
- Real-time style updates in designer
- Custom widget support
- QSS class preview functionality

## UI Development Workflow

### Creating New UI Components

#### 1. Design in Qt Designer

User interfaces are defined in `.ui` files that can be visually edited in pyside6-designer. OneLauncher provides a convenient command to launch Qt Designer with all plugins enabled:

```bash
onelauncher designer  # Launch Qt Designer with OneLauncher plugins enabled
```

This command ensures that:
- OneLauncher's custom widgets are available in the designer
- The QSS class system can be previewed live
- All styling functionality works correctly during design

#### 2. Compile UI to Python

UI files must be compiled into Python modules to be used in OneLauncher. This is done using the `pyside6-uic` tool:

```bash
pyside6-uic src/onelauncher/ui/example_window.ui -o src/onelauncher/ui/example_window_uic.py
```

**Important**: Replace "example_window" with the actual name of the UI file being updated. The compiled Python file should always have the `_uic.py` suffix to distinguish it from the hand-written window classes.

#### 3. Create Window Class

```python
from .ui.example_window_uic import Ui_exampleWindow

class ExampleWindow(FramelessQDialogWithStylePreview):
    def __init__(self):
        super().__init__()
        self.ui = Ui_exampleWindow()
        self.ui.setupUi(self)
```

### Styling Workflow

#### 1. Add QSS Classes in Qt Designer

- Launch Qt Designer with OneLauncher plugins: `onelauncher designer`
- Select the widget you want to style
- Add dynamic property `qssClass` with type **StringList**
- Add class names like `px-4`, `py-2`, `text-lg` (one class per line)
- Classes update live in Qt Designer for immediate preview

#### 2. Preview Styles

- Styles update live in Qt Designer when using OneLauncher plugins
- Test different responsive breakpoints by resizing the designer window
- Verify cross-platform appearance with different system themes
- Use Font Awesome icons through the qtawesome integration

#### 3. Custom Styles

For styles not covered by the Tailwind-like classes, add custom QSS:

```python
# Add custom styles to ApplicationStyle.generate_stylesheet()
stylesheet += """
QWidget#myCustomWidget {
    background-color: palette(window);
    border-radius: 4px;
}
"""
```

### Testing UI Changes

```bash
# Run application to test changes
python -m onelauncher

# Test with different system themes
# Test with different font sizes
# Test window resizing behavior
```

## Async GUI Architecture

OneLauncher uses a sophisticated async architecture that combines Qt's event loop with Trio for structured concurrency.

### Architecture Overview

```mermaid
graph TB
    subgraph "Qt Event Loop Layer"
        A[QApplication.exec]
        B[Qt Events & Signals]
        C[UI Updates]
        D[User Interactions]
    end
    
    subgraph "Trio Async Layer"
        E[AsyncHelper]
        F[trio.open_nursery]
        G[Network Operations]
        H[File I/O Operations]
        I[Background Tasks]
    end
    
    subgraph "Integration Bridge"
        J[async_utils.py]
        K[Event Loop Integration]
        L[Signal/Slot Bridges]
        M[Async Context Management]
    end
    
    A --> B
    B --> C
    B --> D
    D --> E
    E --> F
    F --> G
    F --> H
    F --> I
    
    J --> K
    K --> L
    L --> M
    E --> J
    J --> A
    
    G --> C
    H --> C
    I --> C
```

### Key Components

#### AsyncHelper Integration

```python
# In cli.py
async_helper = AsyncHelper(partial(_main, entry=entry))
QtCore.QTimer.singleShot(0, async_helper.launch_guest_run)
# qapp.exec() won't return until trio event loop finishes
sys.exit(qapp.exec())
```

#### Async UI Operations

```python
# In MainWindow
async def InitialSetup(self) -> None:
    # UI state management
    self.ui.cboAccount.setEnabled(False)
    self.ui.txtPassword.setEnabled(False)
    
    # Async network operations
    async with trio.open_nursery() as self.network_setup_nursery:
        self.network_setup_nursery.start_soon(self.game_initial_network_setup)
```

#### Non-blocking UI Updates

```python
async def game_initial_network_setup(self) -> None:
    try:
        # Async network call
        game_services_info = await GameServicesInfo.from_url(...)
        
        # UI updates on main thread
        self.load_worlds_list(game_services_info)
        self.ui.cboWorld.setEnabled(True)
        self.ui.btnLogin.setEnabled(True)
    except httpx.HTTPError:
        logger.exception("Network error...")
```

### Benefits

1. **Responsive UI**: Network operations don't block the interface
2. **Structured Concurrency**: Trio's nursery pattern for safe async operations
3. **Error Handling**: Proper exception handling across async boundaries
4. **Resource Management**: Automatic cleanup of async operations

---

This documentation provides a comprehensive overview of OneLauncher's GUI architecture. For implementation details, refer to the source code in `src/onelauncher/ui/` and related modules.