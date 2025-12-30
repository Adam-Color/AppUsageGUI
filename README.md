![version](https://img.shields.io/badge/Version-1.8.2-white.svg)
![license](https://img.shields.io/badge/License-GPL%20v3-blue.svg)
![python](https://img.shields.io/badge/Python-3.13-green.svg)

# AppUsageGUI
### Application Runtime Tracker

This program tracks the runtime of specified applications, organizing sessions into projects. Users can create multiple projects, each containing multiple tracking sessions, providing comprehensive time tracking and data analysis.

## Installation

To install, follow the instructions for your platform found here:

[Windows](docs/install_windows.md) | [macOS](docs/install_macos.md)

## Contributing

### Contributions are welcome and needed! Here is a TODO list:

* Add integrations with professional applications
* Detach the GIL for windows version
* Find a better way to filter out non-GUI apps
* Full linux support with packages

NOTE: GIL is detached for the macOS build; use Python 3.13.7t

## Building

For building, it is recommended to use Python 3.13.7 for Windows/Linux, and 3.13.7t for macOS in a virtual enviroment.

Install requirents:
`pip install -r requirements.txt`

Run build script:
`python build.py`

The resulting AppUsageGUI folder will be created in dist/

Scripts to create macOS/Windows installers are located in dev/

## How It Works

AppUsageGUI is a cross-platform desktop application built with Python and Tkinter that monitors application usage time with project-based organization. The application works by:

1. **Project Organization**: Users create projects to organize related tracking sessions, with each project containing multiple sessions
2. **Session Creation**: Before tracking begins, users select a project and name their session
3. **Process Monitoring**: Uses the `psutil` library to detect running applications and monitor their process status
4. **Time Tracking**: Implements a precise time tracker that runs in a separate thread, capable of pausing and resuming
5. **Session Management**: Creates named sessions within projects that can be saved, loaded, and continued across application restarts
6. **Data Persistence**: Saves session data with integrity checking using hash verification, organized by project directories
7. **Cross-Platform Support**: Handles Windows and macOS differences in process detection and GUI application filtering

The application follows a Model-View-Controller (MVC) architecture with separate logic and GUI components.

### Key Concepts

- **Projects**: Top-level containers that group related sessions together, stored in the `Projects/` directory
- **Standalone Sessions**: Sessions not assigned to any project, stored directly in the `Sessions/` directory
- **"No Project"**: A UI label for sessions that aren't assigned to any project (not an actual project directory)
- **Sessions**: Individual time tracking instances that can belong to a project or exist standalone
- **Session Files**: Each session consists of a `.dat` file (data) and `.hash` file (integrity check)
- **Metadata**: Project information is stored in `projects_metadata.json` including creation dates and session counts

## Features

- **Project Management**: Organize sessions into projects for organization and management
- **Session Tracking**: Track the total runtime of any executable with named sessions
- **Session Continuation**: Continue from previous sessions within any project
- **User Customizable Rules**: Configure custom tracking rules and application filtering
- **Cross-Platform Support**: Works on Windows and macOS (macOS installation requires permissions)
- **Data Integrity**: Session data integrity with hash verification
- **Pause/Resume**: Pause and resume functionality during active tracking
- **Smart Detection**: Automatic detection of GUI applications vs background processes
- **Project Analytics**: View total time spent across all sessions within a project
- **Migration Support**: Automatic migration of existing sessions to the new project structure

## User Workflow

### New Session Creation
The application now uses a streamlined workflow where users select their project and session name before starting the timer:

1. **Main Menu** → "Start new session"
2. **Create Session Window** → Select project and enter session name
3. **Select App Window** → Choose application to track
4. **Tracker Window** → Timer runs with pause/resume controls
5. **Save Window** → Save session data
6. **Session Total Window** → View results and statistics

### Project Management
- **Main Menu** → "Manage Projects" → View all projects with session counts and total time
- **Create New Project** → Set up new project containers
- **View Project Sessions** → Manage sessions within specific projects
- **Delete Projects** → Remove projects and all associated sessions (with confirmation)

### Continuing Existing Sessions
- **Main Menu** → "Continue previous session" → Navigate through projects to find and resume sessions
- Sessions can be continued across application restarts with full state preservation
