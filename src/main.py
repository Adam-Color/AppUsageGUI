"""
    Application runtime tracker.

    Copyright (C) 2025 Adam Blair-Smith

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import tkinter as tk
import tkinter.font as tkfont
import os
import sys
import platform

from core.screens.splash_screen import splash_screen
from core.utils.tk_utils import is_dark_mode, set_main_window, messagebox
from _logging import setup_logging
from _path import resource_path

from _version import __version__

def apply_dark_theme(root):
    dark_bg = "#2E2E2E"  # Dark gray background
    dark_fg = "#FFFFFF"  # White text

    root.tk_setPalette(background=dark_bg, foreground=dark_fg)

def set_default_font(root):
    system = platform.system()

    if system == "Windows":
        family = ("Segoe UI Semibold", 12)
    elif system == "Darwin":  # macOS
        family = ("Helvetica", 14)
    else:  # Linux/Other
        family = ("DejaVu Sans", 12)

    default_font = tkfont.nametofont("TkDefaultFont")
    default_font.configure(family=family[0], size=family[1])
    root.option_add("*Font", default_font)


def main():
    try:
        setup_logging()
        import logging
        logger = logging.getLogger(__name__)
        logger.info("Starting AppUsageGUI...")

        root = tk.Tk()
        root.withdraw()

        if is_dark_mode():
            apply_dark_theme(root)

        set_default_font(root)

        if os.name == 'nt':
            icon_name = "core\\resources\\icon.ico"
        elif sys.platform == 'darwin':  # macOS
            icon_name = "core/resources/icon.icns"
        else:  # Linux or other Unix-like systems
            icon_name = "core/resources/icon.png"

        icon_path = resource_path(icon_name)

        root.iconbitmap(icon_path)
        root.title(f"AppUsageGUI - v{__version__}")

        # Set the main window reference for centering dialogs
        set_main_window(root)

        splash_screen(root)
        root.mainloop()
    except Exception as e:
        from traceback import format_exc
        error_message = f"An unexpected error occurred:\n{str(e)}\n\n{format_exc()}"
        import logging
        logger = logging.getLogger(__name__)
        logger.error(error_message)
         
        messagebox.showerror("Error", error_message)

if __name__ == "__main__":
    main()
