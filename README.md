# App Usage GUI
### Application Runtime Tracker

This program tracks the runtime of a specified application, logging the duration the application is running over multiple instances, with unique sessions for each app.

## Features

- Tracks the total runtime of a specified application.
- Supports continuation from previous sessions.
- Provides formatted runtime breakdown (hours, minutes, seconds).

## Installation

1. Clone this repository:
    ```sh
    git clone https://github.com/Adam-Code/AppUsageGUI.git
    ```

2. Ensure you have Python 3.12.4 installed on your system.

3. Install the required libraries:
    ```sh
    pip install -r requirements.txt
    ```

## Usage

1. Run the application via the terminal, with the terminal open in the AppUsageGUI directory:
    ```sh
    python src/main.py
    ```

2. ensure that the target application is running.

3. If previous sessions are detected, you will be prompted to continue from a previous session or start a new one

5. The script will display the tracked runtime in real-time. To stop tracking, close the tracked application.

6. After fully quitting the tracked application, you will be prompted to save the data
