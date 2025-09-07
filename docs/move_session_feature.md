# Move Session to Project Feature

## Overview
The "Move session to project" feature allows users to associate sessions with "No Project" to any existing project and to move sessions from one project to any other existing project. This feature removes the session from its current location and moves it to the new project that has been selected.

## How to Use

1. **Access the Sessions Window**: Navigate to the Sessions window from the main menu.

2. **Select a Session**: Click on any session in the list to select it.

3. **Click "Move session to project"**: Click the "Move session to project" button.

4. **Choose Target Project**: A dialog window will appear showing:
   - The current project of the selected session
   - A dropdown menu with all available projects (excluding the current project)
   - An option to move to "No Project"

5. **Confirm the Move**: Click "Move Session" to confirm the operation.

6. **Verification**: The session will be moved and the sessions list will refresh to show the updated location.

## Features

- **Move from No Project to Project**: Sessions that are not associated with any project can be moved to an existing project.
- **Move from Project to No Project**: Sessions can be removed from a project and become standalone sessions.
- **Move between Projects**: Sessions can be moved from one project to another.
- **Validation**: The system prevents moving a session to the same project it's already in.
- **Confirmation**: Users must confirm the move operation before it's executed.
- **Automatic Refresh**: The sessions list automatically refreshes after a successful move.

## Technical Implementation

### Files Modified
- `src/core/screens/sessions_window.py`: Added the move session button and dialog
- `src/core/logic/file_handler.py`: Added the `move_session_to_project` method

### Key Methods
- `move_session_to_project()`: Main method that handles the session moving logic
- `show_move_session_dialog()`: Creates the project selection dialog
- `execute_move_session()`: Executes the move operation with confirmation

### Data Handling
- Session data is loaded from the source location
- Project information is updated in the session data
- Files are moved to the target location
- Source files are removed after successful move
- Project metadata is updated for both source and target projects

## Error Handling
- Validates that a session is selected before attempting to move
- Checks if source files exist before attempting to move
- Prevents moving to the same project
- Provides user feedback for all operations
- Handles file system errors gracefully

## Testing
A comprehensive test suite is available in `tests/test_move_session_to_project.py` that covers:
- Moving sessions from No Project to a project
- Moving sessions from a project to No Project
- Moving sessions between different projects
- Error handling for nonexistent sessions
- Edge cases and validation
