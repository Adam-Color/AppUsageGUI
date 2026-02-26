import tkinter as tk
import tkinter.messagebox as messagebox
import os
import sys
import ctypes
from ctypes import wintypes

import logging
logger = logging.getLogger(__name__)

class ctypesRECT(ctypes.Structure):
    _fields_ = [
        ("left", ctypes.c_long),
        ("top", ctypes.c_long),
        ("right", ctypes.c_long),
        ("bottom", ctypes.c_long)
    ]

class MONITORINFO(ctypes.Structure):
    _fields_ = [
        ("cbSize", ctypes.c_ulong),
        ("rcMonitor", ctypesRECT),
        ("rcWork", ctypesRECT),
        ("dwFlags", ctypes.c_ulong)
    ]

def get_monitor_info(win):
    if sys.platform == "win32":
        return get_monitor_info_win32(win)
    elif sys.platform == 'darwin':
        from AppKit import NSScreen
        screens = NSScreen.screens()
        parent_x = int(win.winfo_rootx())
        parent_y = int(win.winfo_rooty())

        for screen in screens:
            frame = screen.frame()
            origin_x = getattr(frame.origin, 'x', 0)
            origin_y = getattr(frame.origin, 'y', 0)
            width = getattr(frame.size, 'width', 0)
            height = getattr(frame.size, 'height', 0)

            origin_x = int(origin_x)
            origin_y = int(origin_y)
            width = int(width)
            height = int(height)

            if origin_x <= parent_x < origin_x + width and \
               origin_y <= parent_y < origin_y + height:
                return origin_x, origin_y, width, height

        return 0, 0, win.winfo_screenwidth(), win.winfo_screenheight()
    else:
        # Fallback for Linux/Other
        return 0, 0, win.winfo_screenwidth(), win.winfo_screenheight()

def center(win):
    """
    Center a Tkinter window on the screen with optional percentage offsets.

    Args:
        win (tk.Tk or tk.Toplevel): The window to center.
        offset_x (float): Horizontal offset as a percentage of the screen width.
                                  Positive = move right, negative = move left.
        offset_y (float): Vertical offset as a percentage of the screen height.
                                  Positive = move down, negative = move up.
    """
    win.update_idletasks()

    # Get actual window and screen sizes
    width = win.winfo_width()
    logger.info(f"width={width}")
    height = win.winfo_height()
    logger.info(f"height={height}")
    screen_width = win.winfo_screenwidth()
    logger.info(f"screen_width={screen_width}")
    screen_height = win.winfo_screenheight()
    logger.info(f"screen_height={screen_height}")

    # Convert percentage offsets to pixels

    # Compute center position
    x = int((screen_width / 2) - (width / 2))
    y = int((screen_height / 2) - (height / 2))
    logger.info(f"x={x}, y={y}")

    win.geometry(f"{width}x{height}+{x}+{y}")

def center_relative_to_parent(win, parent):
    win.withdraw()
    win.update_idletasks()
    parent.update_idletasks()

    width = win.winfo_reqwidth()
    height = win.winfo_reqheight()

    parent_x = parent.winfo_rootx()
    parent_y = parent.winfo_rooty()
    parent_width = parent.winfo_width()
    parent_height = parent.winfo_height()

    x = parent_x + (parent_width - width) // 2
    y = parent_y + (parent_height - height) // 2

    # Get monitor info
    monitor_x, monitor_y, monitor_width, monitor_height = get_monitor_info(parent)

    # Clamp to monitor bounds
    x = max(monitor_x, min(x, monitor_x + monitor_width - width))
    y = max(monitor_y, min(y, monitor_y + monitor_height - height))

    win.geometry(f'{width}x{height}+{x}+{y}')
    win.deiconify()
    win.update_idletasks()

def is_dark_mode():
    """Check if the system is in dark mode"""
    if os.name == 'nt':  # Windows
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                r"Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize") as key:
                value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
                return value == 0
        except Exception:
            return False
    elif sys.platform == 'darwin':  # macOS
        try:
            from AppKit import NSUserDefaults
            defaults = NSUserDefaults.standardUserDefaults()
            return defaults.boolForKey_("AppleInterfaceStyle") == "Dark"
        except ImportError:
            return False
    elif sys.platform.startswith('linux'):  # Linux
        try:
            with open(os.path.expanduser("~/.config/gtk-3.0/settings.ini"), 'r') as f:
                for line in f:
                    if "gtk-theme-name" in line:
                        return "dark" in line.lower()
        except FileNotFoundError:
            return False

# Global variable to store the main window reference for centering dialogs
_main_window = None

def set_main_window(window):
    """Set the main window reference for centering dialogs"""
    global _main_window
    _main_window = window

def _create_centered_dialog(title, message, dialog_type, buttons):
    """Create a custom dialog centered relative to main window"""
    if not _main_window:
        # Fallback to regular messagebox if no main window is set
        if dialog_type == "info":
            return messagebox.showinfo(title, message)
        elif dialog_type == "warning":
            return messagebox.showwarning(title, message)
        elif dialog_type == "error":
            return messagebox.showerror(title, message)
        elif dialog_type == "question":
            return messagebox.askquestion(title, message)
        elif dialog_type == "yesno":
            return messagebox.askyesno(title, message)
        elif dialog_type == "okcancel":
            return messagebox.askokcancel(title, message)
    
    # Create custom dialog
    dialog = tk.Toplevel(_main_window)
    dialog.title(title)
    dialog.resizable(False, False)
    dialog.transient(_main_window)
    dialog.grab_set()
    
    # Create main frame
    frame = tk.Frame(dialog)
    frame.pack(padx=20, pady=20)
    
    # Add icon and message
    icon_frame = tk.Frame(frame)
    icon_frame.pack(side="left", padx=(0, 15))
    
    # Simple text-based icons
    if dialog_type == "error":
        icon_text = "✕"
        icon_color = "red"
    elif dialog_type == "warning":
        icon_text = "⚠"
        icon_color = "orange"
    elif dialog_type == "info":
        icon_text = "ℹ"
        icon_color = "cyan"
    else:  # question, yesno, okcancel
        icon_text = "?"
        icon_color = "cyan"
    
    icon_label = tk.Label(icon_frame, text=icon_text, font=("Arial", 24), fg=icon_color)
    icon_label.pack()
    
    # Message
    message_frame = tk.Frame(frame)
    message_frame.pack(side="right", fill="both", expand=True)
    
    message_label = tk.Label(message_frame, text=message, wraplength=300, justify="left")
    message_label.pack(anchor="w")
    
    # Buttons
    button_frame = tk.Frame(dialog)
    button_frame.pack(pady=(10, 0))
    
    result = None
    
    def button_click(value):
        nonlocal result
        result = value
        dialog.destroy()
    
    if buttons == ["OK"]:
        tk.Button(button_frame, text="OK", command=lambda: button_click(True), width=10).pack()
    elif buttons == ["Yes", "No"]:
        tk.Button(button_frame, text="Yes", command=lambda: button_click(True), width=10).pack(side="left", padx=5)
        tk.Button(button_frame, text="No", command=lambda: button_click(False), width=10).pack(side="left", padx=5)
    elif buttons == ["OK", "Cancel"]:
        tk.Button(button_frame, text="OK", command=lambda: button_click(True), width=10).pack(side="left", padx=5)
        tk.Button(button_frame, text="Cancel", command=lambda: button_click(False), width=10).pack(side="left", padx=5)
    
    # Center the dialog
    center_relative_to_parent(dialog, _main_window)
    
    # Wait for dialog to close
    dialog.wait_window()
    
    return result

def get_monitor_info_win32(win):
    """
    Get monitor info for Windows.
    Returns: (monitor_x, monitor_y, monitor_width, monitor_height)
    """
    user32 = ctypes.windll.user32

    # Get window rect
    rect = ctypesRECT()
    hwnd = win.winfo_id()
    user32.GetWindowRect(hwnd, ctypes.byref(rect))

    # Get monitor info
    hmonitor = user32.MonitorFromWindow(hwnd, 2)  # MONITOR_DEFAULTTONEAREST
    if not hmonitor:
        return 0, 0, win.winfo_screenwidth(), win.winfo_screenheight()

    # Get monitor info
    monitor_info = MONITORINFO()
    monitor_info.cbSize = ctypes.sizeof(MONITORINFO)
    user32.GetMonitorInfoW(hmonitor, ctypes.byref(monitor_info))

    # Return monitor rect
    return (
        monitor_info.rcMonitor.left,
        monitor_info.rcMonitor.top,
        monitor_info.rcMonitor.right - monitor_info.rcMonitor.left,
        monitor_info.rcMonitor.bottom - monitor_info.rcMonitor.top
    )

def showinfo(title, message, **kwargs):
    """Show info dialog centered relative to main window"""
    return _create_centered_dialog(title, message, "info", ["OK"])

def showwarning(title, message, **kwargs):
    """Show warning dialog centered relative to main window"""
    return _create_centered_dialog(title, message, "warning", ["OK"])

def showerror(title, message, **kwargs):
    """Show error dialog centered relative to main window"""
    return _create_centered_dialog(title, message, "error", ["OK"])

def askquestion(title, message, **kwargs):
    """Show question dialog centered relative to main window"""
    return _create_centered_dialog(title, message, "question", ["Yes", "No"])

def askyesno(title, message, **kwargs):
    """Show yes/no dialog centered relative to main window"""
    return _create_centered_dialog(title, message, "yesno", ["Yes", "No"])

def askokcancel(title, message, **kwargs):
    """Show ok/cancel dialog centered relative to main window"""
    return _create_centered_dialog(title, message, "okcancel", ["OK", "Cancel"])
