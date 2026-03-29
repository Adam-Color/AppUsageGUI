"""
Settings window for configuring application settings. Created with the help of Claude.
"""

import tkinter as tk
from tkinter import ttk
import os
from core.utils.tk_utils import messagebox
from core.utils.file_utils import read_file, write_file, config_file

import logging
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Settings Schema
# ---------------------------------------------------------------------------
# To add a new setting, append a dict to SETTINGS_SCHEMA.  The UI, load, and
# save logic are all driven from this list — no other method needs touching
# except _apply_runtime_effects() if the setting has an immediate side-effect.
#
# Common fields (all types):
#   tab              str   Tab label the setting appears under.
#   key              str   Key used in the persisted config dict.
#   label            str   Short label shown next to the control.
#   description      str   Explanatory text rendered below the control.
#   type             str   "checkbox" | "spinbox" | "section_header"
#   default                Fallback value when no saved config exists.
#   requires_restart bool  Show a restart notice when this value changes.
#
# Extra fields for "spinbox":
#   min  int   Minimum value.
#   max  int   Maximum value.
#   unit str   Unit label shown after the spinbox (e.g. "seconds").
#
# "section_header" only needs: tab, type, label.
# ---------------------------------------------------------------------------

SETTINGS_SCHEMA: list[dict] = [

    # ── General ──────────────────────────────────────────────────────────────
    {
        "tab": "General",
        "type": "section_header",
        "label": "Updates",
    },
    {
        "tab": "General",
        "key": "auto_update",
        "label": "Check for updates automatically",
        "description": (
            "Automatically check for updates when the application starts (limited to once per day)."
        ),
        "type": "checkbox",
        "default": True,
        "requires_restart": False,
    },

    # ── Tracking ─────────────────────────────────────────────────────────────
    {
        "tab": "Tracking",
        "type": "section_header",
        "label": "Mouse Idle Detection",
    },
    {
        "tab": "Tracking",
        "key": "mouse_tracker_enabled",
        "label": "Enable mouse idle detection",
        "description": (
            "Automatically pause time tracking when the mouse has not moved "
            "for the configured timeout."
        ),
        "type": "checkbox",
        "default": True,
        "requires_restart": False,
    },
    {
        "tab": "Tracking",
        "key": "mouse_idle_time_limit",
        "label": "Idle timeout",
        "description": (
            "How long the mouse must remain still before tracking is paused. Must be between 5 and 3600 seconds."
        ),
        "type": "spinbox",
        "default": 90,
        "min": 5,
        "max": 3600,
        "unit": "seconds",
        "requires_restart": False,
    },

    # ── Filtering ─────────────────────────────────────────────────────────────
    {
        "tab": "Filtering",
        "type": "section_header",
        "label": "Application List",
    },
    {
        "tab": "Filtering",
        "key": "is_filter_enabled",
        "label": "Enable app filtering",
        "description": (
            "Hide background processes and system services from the application "
            "list so only foreground apps are shown. "
            "Requires a restart to take effect."
        ),
        "type": "checkbox",
        "default": True,
        "requires_restart": True,
    },
]


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _validate_numeric(value: str) -> bool:
    """Tkinter validatecommand: accept an empty string or a non-negative number."""
    if value == "":
        return True
    try:
        return float(value) >= 0
    except ValueError:
        return False


def _schema_keys() -> list[str]:
    """Return all setting keys defined in the schema (excludes header rows)."""
    return [s["key"] for s in SETTINGS_SCHEMA if s["type"] != "section_header"]


def _schema_defaults() -> dict:
    """Return a {key: default} dict for every real setting in the schema."""
    return {s["key"]: s["default"] for s in SETTINGS_SCHEMA if s["type"] != "section_header"}


# ---------------------------------------------------------------------------
# Settings Window
# ---------------------------------------------------------------------------

class SettingsWindow(tk.Frame):
    """
    Settings screen organised into tabs.  The layout and save/load logic are
    driven entirely by SETTINGS_SCHEMA — add new settings there.

    The only place that may need manual updates when adding a new setting is
    _apply_runtime_effects(), if the setting needs an immediate side-effect
    (e.g. toggling a background thread).
    """

    def __init__(self, parent, controller, logic_controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.logic = logic_controller

        # ── Load persisted config, fill gaps with schema defaults ─────────
        self._settings: dict = _schema_defaults()
        if os.path.exists(config_file()):
            saved = read_file(config_file())
            logger.info("Loaded config: %s", saved)
            if saved:
                self._settings.update({k: saved[k] for k in saved if k in _schema_keys()})

        # One tk Variable per setting key, populated during _build_notebook().
        self._vars: dict[str, tk.Variable] = {}

        self._build_ui()

    # ── UI construction ────────────────────────────────────────────────────

    def _build_ui(self):
        self._build_header()
        self._build_notebook()
        self._build_footer()

    # -- Header --------------------------------------------------------------

    def _build_header(self):
        header = tk.Frame(self)
        header.pack(side="top", fill="x", padx=20, pady=(12, 4))

        tk.Label(
            header,
            text="Settings",
            font=("TkDefaultFont", 14, "bold"),
            anchor="w",
        ).pack(side="left")

    # -- Notebook ------------------------------------------------------------

    def _build_notebook(self):
        """Create one tab per unique tab name found in SETTINGS_SCHEMA."""
        self._notebook = ttk.Notebook(self)
        self._notebook.pack(side="top", fill="both", expand=True, padx=14, pady=(2, 0))

        # Build an ordered, deduplicated list of tab names.
        tab_names: list[str] = list(dict.fromkeys(
            s["tab"] for s in SETTINGS_SCHEMA
        ))

        # Create a scrollable canvas inside each tab so content is never clipped.
        tab_frames: dict[str, tk.Frame] = {}
        for name in tab_names:
            outer = tk.Frame(self._notebook)
            self._notebook.add(outer, text=f"  {name}  ")

            canvas = tk.Canvas(outer, bd=0, highlightthickness=0)
            scrollbar = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
            inner = tk.Frame(canvas)

            inner.bind(
                "<Configure>",
                lambda e, c=canvas: c.configure(scrollregion=c.bbox("all"))
            )
            canvas.create_window((0, 0), window=inner, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)

            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

            # Only show scrollbar when content actually overflows.
            inner.bind(
                "<Configure>",
                lambda e, c=canvas, sb=scrollbar: self._toggle_scrollbar(c, sb)
            )

            tab_frames[name] = inner

        # Populate each tab with widgets from the schema.
        for schema in SETTINGS_SCHEMA:
            self._add_row(tab_frames[schema["tab"]], schema)

        # Add a spacer at the bottom of each tab for breathing room.
        for frame in tab_frames.values():
            tk.Frame(frame, height=12).pack()

    @staticmethod
    def _toggle_scrollbar(canvas: tk.Canvas, scrollbar: ttk.Scrollbar):
        """Show the scrollbar only when content exceeds the visible area."""
        canvas.update_idletasks()
        if canvas.winfo_height() >= canvas.winfo_reqheight():
            scrollbar.pack_forget()
        else:
            if not scrollbar.winfo_ismapped():
                scrollbar.pack(side="right", fill="y")

    # -- Row factories -------------------------------------------------------

    def _add_row(self, parent: tk.Frame, schema: dict):
        """Dispatch to the correct widget factory based on schema['type']."""
        stype = schema["type"]
        if stype == "section_header":
            self._add_section_header(parent, schema)
        elif stype == "checkbox":
            self._add_checkbox(parent, schema)
        elif stype == "spinbox":
            self._add_spinbox(parent, schema)
        else:
            logger.warning("Unknown setting type %r — skipped.", stype)

    def _add_section_header(self, parent: tk.Frame, schema: dict):
        """Bold section heading with a horizontal rule underneath."""
        wrapper = tk.Frame(parent)
        wrapper.pack(fill="x", padx=18, pady=(16, 0))

        tk.Label(
            wrapper,
            text=schema["label"],
            font=("TkDefaultFont", 10, "bold"),
            anchor="w",
        ).pack(fill="x")

        ttk.Separator(wrapper, orient="horizontal").pack(fill="x", pady=(4, 0))

    def _add_checkbox(self, parent: tk.Frame, schema: dict):
        """Checkbox control with a description line underneath."""
        key = schema["key"]
        var = tk.BooleanVar(value=bool(self._settings.get(key, schema["default"])))
        self._vars[key] = var

        restart_note = "  ⟳" if schema.get("requires_restart") else ""

        wrapper = tk.Frame(parent)
        wrapper.pack(fill="x", padx=24, pady=(10, 0))

        ttk.Checkbutton(
            wrapper,
            text=schema["label"] + restart_note,
            variable=var,
        ).pack(anchor="w")

        if schema.get("description"):
            tk.Label(
                wrapper,
                text=schema["description"],
                font=("TkDefaultFont", 9),
                fg="gray",
                wraplength=460,
                justify="left",
                anchor="w",
            ).pack(anchor="w", padx=(22, 0), pady=(2, 0))

    def _add_spinbox(self, parent: tk.Frame, schema: dict):
        """Label + spinbox + unit on one line, with a description below."""
        key = schema["key"]
        raw = self._settings.get(key, schema["default"])
        var = tk.StringVar(value=str(int(raw)))
        self._vars[key] = var

        restart_note = "  ⟳" if schema.get("requires_restart") else ""
        vcmd = (self.register(_validate_numeric), "%P")

        wrapper = tk.Frame(parent)
        wrapper.pack(fill="x", padx=24, pady=(10, 0))

        ctrl_row = tk.Frame(wrapper)
        ctrl_row.pack(fill="x")

        tk.Label(ctrl_row, text=schema["label"] + restart_note).pack(side="left")

        tk.Spinbox(
            ctrl_row,
            from_=schema.get("min", 0),
            to=schema.get("max", 9999),
            textvariable=var,
            validate="key",
            validatecommand=vcmd,
            width=6,
            justify="center",
        ).pack(side="left", padx=(8, 4))

        unit = schema.get("unit", "")
        if unit:
            tk.Label(ctrl_row, text=unit, fg="gray").pack(side="left")

        if schema.get("description"):
            tk.Label(
                wrapper,
                text=schema["description"],
                font=("TkDefaultFont", 9),
                fg="gray",
                wraplength=460,
                justify="left",
                anchor="w",
            ).pack(anchor="w", pady=(2, 0))

    # -- Footer --------------------------------------------------------------

    def _build_footer(self):
        """Thin separator + action buttons pinned to the bottom of the frame."""
        ttk.Separator(self, orient="horizontal").pack(side="bottom", fill="x")

        footer = tk.Frame(self, pady=8)
        footer.pack(side="bottom", fill="x", padx=16)

        # Left side: passive restart notice (always visible so the layout is stable)
        self._restart_label = tk.Label(
            footer,
            text="  \u27f3  Some changes require a restart.",
            font=("TkDefaultFont", 9),
            fg="gray",
            anchor="w",
        )
        self._restart_label.pack(side="left")

        # Right side: action buttons (KDE convention — primary action rightmost)
        btn_area = tk.Frame(footer)
        btn_area.pack(side="right")

        tk.Button(
            btn_area,
            text="Discard Changes",
            command=self._discard,
            width=16,
        ).pack(side="left", padx=(0, 6))

        tk.Button(
            btn_area,
            text="Save Changes",
            command=self._save,
            width=16,
        ).pack(side="left")

    # ── Actions ────────────────────────────────────────────────────────────

    def _save(self):
        """
        Read every widget variable, update self._settings, persist to disk,
        apply runtime effects, then navigate back to the main window.
        """
        restart_needed = False

        for schema in SETTINGS_SCHEMA:
            if schema["type"] == "section_header":
                continue

            key = schema["key"]
            var = self._vars.get(key)
            if var is None:
                continue

            # Coerce value to the correct Python type.
            stype = schema["type"]
            if stype == "checkbox":
                new_val = var.get()                                 # bool
            elif stype == "spinbox":
                try:
                    new_val = int(var.get())
                    # Clamp to schema bounds — the keystroke validator only
                    # ensures the value is a non-negative number; the min/max
                    # limits are enforced here so intermediate typing states
                    # (e.g. typing "1" on the way to "15") are never rejected.
                    lo = schema.get("min")
                    hi = schema.get("max")
                    if lo is not None:
                        new_val = max(lo, new_val)
                    if hi is not None:
                        new_val = min(hi, new_val)
                except (ValueError, tk.TclError):
                    new_val = schema["default"]
            else:
                continue

            # Check if a restart-required setting actually changed.
            if schema.get("requires_restart") and new_val != self._settings.get(key):
                restart_needed = True

            self._settings[key] = new_val

        self._apply_runtime_effects()

        write_file(config_file(), self._settings)
        logger.info("Settings saved: %s", self._settings)

        self.controller.reset_frames()

        if restart_needed:
            messagebox.showinfo(
                "Restart Required",
                "One or more changes will take effect after restarting the application.",
            )

        self.controller.show_frame("MainWindow")

    def _discard(self):
        """Abandon any unsaved changes and return to the main window."""
        self.controller.reset_frames()
        self.controller.show_frame("MainWindow")

    def _apply_runtime_effects(self):
        """
        Push setting values into live objects that need immediate updates.

        When adding a new setting that has a runtime side-effect (e.g. enabling
        a background thread), add the relevant call here keyed on its schema key.
        Settings that only take effect on restart do not need an entry.
        """
        mouse = self.logic.mouse_tracker
        mouse.set_enabled(self._settings["mouse_tracker_enabled"])
        mouse.set_idle_time_limit(self._settings["mouse_idle_time_limit"])
