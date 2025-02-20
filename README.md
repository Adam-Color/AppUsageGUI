# App Usage GUI
### Application Runtime Tracker

This program tracks the runtime of a specified application, logging the duration the application is running over multiple instances, with unique sessions created by the user.

## Features

- Tracks the total runtime of a specified application.
- Supports continuation from previous sessions.
- Provides formatted runtime breakdown (hours, minutes, seconds).

## Installation

1. Clone this repository into your preferred directory via the terminal:
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

5. AppUsageGUI will display the tracked runtime in real-time. To stop tracking, close the tracked application.

6. After fully quitting the tracked application, you will be prompted to save the data

## Contributing

Contributions are welcome and needed on the Develop branch! Here is a TODO list:

1. Someone to build the application into cross-platform executables (exe, dmg, etc.)

2. Adding user-customizable pause conditions (i.e: the user's mouse hasn't moved for a full minute, time tracking pauses)

3. Add ways to analyze app usage data in the app
