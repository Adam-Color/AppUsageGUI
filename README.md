# App Usage GUI
### Application Runtime Tracker

This program tracks the runtime of a specified application, logging the duration the application is running over multiple instances, with unique sessions for each app.

## Features

- Tracks the total runtime of a specified application.
- Supports continuation from previous sessions.
- Provides formatted runtime breakdown (hours, minutes, seconds).

## Requirements

- Python 3.12.3

## LTS Installation (stable, windows only for now)

1. Check [releases](https://github.com/Techi-Joe/AppUsageGUI/releases)
2. download the latest version

## Installation (latest features, may be unstable)

1. Clone this repository:
    ```sh
    git clone https://github.com/Techi-Joe/app_usage
    ```

2. Ensure you have Python 3.12 installed on your system.
3. Install the required libraries:
    ```sh
    pip install -r requirements.txt
    ```

## Usage

1. Run the script (for LTS versions, simply double-click the exe):
    ```sh
    python src/AppUsageGUI.py
    ```

2. The script will prompt you to ensure that the target application is running. After a short delay, it will proceed.

3. If previous sessions are detected, you will be prompted to continue from a previous session or start a new one:
    - **Continue**: The script will add time to a previous session's runtime, which you select from a list.
    - **New**: The script will start a new tracking session.

4. If starting a new session, enter the exact name of the executable you want to track. For Windows, this should be the executable name (e.g., `app_usage-2.0.exe` for `App Usage`).

5. The script will display the tracked runtime in real-time. To stop tracking, close the tracked application.

6. After fully quitting the tracked application, you will be prompted to save the data


## Notes

- Ensure the application to be tracked is running before you start the script.
- The program saves runtime data in `data/[app name]_data.dat`.
