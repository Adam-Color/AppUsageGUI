![version](https://img.shields.io/badge/Version-1.5.1-white.svg)
![license](https://img.shields.io/badge/License-GPL%20v3-blue.svg)
![python](https://img.shields.io/badge/Python-3.12-green.svg)

# AppUsageGUI
### Application Runtime Tracker

This program tracks the runtime of a specified application, logging the duration the application is running over multiple instances, with unique sessions created by the user.

## How It Works

AppUsageGUI is a cross-platform desktop application built with Python and Tkinter that monitors application usage time. The application works by:

1. **Process Monitoring**: Uses the `psutil` library to detect running applications and monitor their process status
2. **Time Tracking**: Implements a precise time tracker that runs in a separate thread, capable of pausing and resuming
3. **Session Management**: Creates named sessions that can be saved, loaded, and continued across application restarts
4. **Data Persistence**: Saves session data with integrity checking using hash verification
5. **Cross-Platform Support**: Handles Windows and macOS differences in process detection and GUI application filtering

The application follows a Model-View-Controller (MVC) architecture with separate logic and GUI components, ensuring clean separation of concerns and maintainable code.

## Features

- Supports tracking the total runtime of any executable
- Supports continuation from previous sessions
- User customizable tracking rules
- Cross-platform support (Windows and macOS) - macOS installation is janky because of permissions required
- Session data integrity with hash verification
- Pause/resume functionality during tracking
- Automatic detection of GUI applications vs background processes

## Installation

To install, follow the instructions for your platform found here:

[Windows](docs/install_windows.md) | [macOS](docs/install_macos.md)

## Contributing

### Contributions are welcome and needed! Here is a TODO list:

* Add integrations with professional applications
* Optimize everything
* Add support for tracking more than one executable per session
* Add a better way to filter out non-GUI apps on macOS

## Code Structure

### Core Application Files

- **`src/main.py`** - Application entry point that initializes the Tkinter root window, applies dark mode theming, sets up the application icon, and launches the splash screen
- **`src/_version.py`** - Contains the application version number
- **`src/_path.py`** - Handles resource path resolution for bundled applications

### Core Logic (`src/core/`)

#### Main Controllers
- **`gui_root.py`** - Main GUI controller that manages the application's window system, initializes all screens, and handles navigation between different windows
- **`logic_root.py`** - Central logic controller that coordinates all tracking components (AppTracker, TimeTracker, FileHandler, MouseTracker)

#### Logic Components (`src/core/logic/`)
- **`app_tracker.py`** - Monitors running processes using psutil, filters GUI applications from background processes, and maintains lists of available applications for tracking
- **`time_tracker.py`** - Implements precise time tracking with pause/resume functionality, runs in a separate thread for accuracy, and captures timing data for analysis
- **`file_handler.py`** - Manages session data persistence, handles file I/O operations with pickle serialization, and implements data integrity checking using hash verification
- **`user_trackers.py`** - Contains additional tracking modules like MouseTracker for user activity monitoring and ResolveProjectTracker for specific application integration

#### User Interface (`src/core/screens/`)
- **`main_window.py`** - Main menu screen providing options to start new sessions, continue previous sessions, or configure settings
- **`select_app_window.py`** - Application selection interface with search functionality and real-time app list updates
- **`tracker_window.py`** - Active tracking display showing elapsed time, pause/resume controls, and stop functionality
- **`sessions_window.py`** - Session management interface for loading, analyzing, and deleting saved sessions
- **`create_session_window.py`** - Session creation dialog with name validation and confirmation
- **`save_window.py`** - Session saving interface with data confirmation
- **`session_total_window.py`** - Session summary display showing total tracked time and statistics
- **`tracker_settings_window.py`** - Configuration interface for custom tracking rules and application filtering
- **`splash_screen.py`** - Application startup splash screen with loading animation

#### Utilities (`src/core/utils/`)
- **`file_utils.py`** - File system operations, directory management, session file handling, and data integrity functions
- **`time_utils.py`** - Time formatting utilities for displaying elapsed time in human-readable format
- **`logic_utils.py`** - Threading utilities and decorators for running functions in separate threads
- **`tk_utils.py`** - Tkinter-specific utilities including window centering and dark mode detection

### Resources (`src/core/resources/`)
- **`icon.ico`** / **`icon.icns`** - Application icons for Windows and macOS respectively
- **`icon-resources/`** - Source files for application icons

### Development and Build Files
- **`setup.py`** - Python package configuration and installation setup
- **`build.py`** - Build script for creating distributable packages
- **`requirements.txt`** - Python dependencies list
- **`pytest.ini`** - Testing configuration
- **`tests/`** - Unit tests for application components


