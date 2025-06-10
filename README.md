![version](https://img.shields.io/badge/Version-1.4.3-white.svg)
![license](https://img.shields.io/badge/License-GPL%20v3-blue.svg)
![python](https://img.shields.io/badge/Python-3.12-green.svg)

# AppUsageGUI
### Application Runtime Tracker

This program tracks the runtime of a specified application, logging the duration the application is running over multiple instances, with unique sessions created by the user.

## Features

- Supports tracking the total runtime of any executable
- Supports continuation from previous sessions.
- User customizable tracking rules

## Installation

To install, follow the instructions for your platform found here:

[Windows](docs/install_windows.md) | [macOS](docs/install_macos.md)

## Contributing

### Contributions are welcome and needed! Here is a TODO list:

* Add integrations with professional applications
* Optimize everything
* Add support for tracking more than one executable per session
* Impliment a better way to filter out non-gui apps on macOS

#### Version 2 ('v2-change-to-pyqt6' branch):

> [!WARNING]
> In **macOS**, PyQt6 conflicts with py-objc, leading to a broken venv.
> As a result, v2 is not currently being worked on until this issue is fixed.

* Merge and resolve changes from Develop into v2
* Move to a single QT UI instead of multiple 'screens'
* Add ways to analyze app usage data in the app
