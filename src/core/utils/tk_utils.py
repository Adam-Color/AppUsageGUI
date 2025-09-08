import tkinter as tk
import tkinter.messagebox as messagebox
import os
import sys

# https://stackoverflow.com/questions/3352918/how-to-center-a-window-on-the-screen-in-tkinter
def center(win):
    """
    centers a tkinter window
    :param win: the main window or Toplevel window to center
    """
    win.update_idletasks()
    width = win.winfo_width()
    frm_width = win.winfo_rootx() - win.winfo_x()
    win_width = width + 2 * frm_width
    height = win.winfo_height()
    titlebar_height = win.winfo_rooty() - win.winfo_y()
    win_height = height + titlebar_height + frm_width
    x = win.winfo_screenwidth() // 2 - win_width // 2
    y = win.winfo_screenheight() // 2 - win_height // 2
    win.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    win.deiconify()

def center_relative_to_parent(win, parent):
    """
    centers a tkinter window relative to its parent window
    :param win: the window to center
    :param parent: the parent window to center relative to
    """
    win.update_idletasks()
    parent.update_idletasks()
    
    # Get window dimensions
    width = win.winfo_width()
    height = win.winfo_height()
    
    # Get parent window position and dimensions
    parent_x = parent.winfo_x()
    parent_y = parent.winfo_y()
    parent_width = parent.winfo_width()
    parent_height = parent.winfo_height()
    
    # Calculate center position relative to parent
    x = parent_x + (parent_width - width) // 2
    y = parent_y + (parent_height - height) // 2
    
    # Ensure window stays on screen
    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()
    
    if x < 0:
        x = 0
    elif x + width > screen_width:
        x = screen_width - width
    
    if y < 0:
        y = 0
    elif y + height > screen_height:
        y = screen_height - height
    
    win.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    win.deiconify()

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
        icon_color = "blue"
    else:  # question, yesno, okcancel
        icon_text = "?"
        icon_color = "blue"
    
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
