"""
Updates the current project info. Used only in the resolve script directory. An injected script of AppUsageGUI.

export RESOLVE_SCRIPT_API="/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting"
export RESOLVE_SCRIPT_LIB="/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Libraries/Fusion/fusionscript.so"
export PYTHONPATH="$RESOLVE_SCRIPT_API/Modules:$PYTHONPATH"
"""

import os
import pickle
import sys

resolve_api = "/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting"
resolve_modules = os.path.join(resolve_api, "Modules")

if resolve_modules not in sys.path:
    sys.path.insert(0, resolve_modules)

import DaVinciResolveScript as dvr_script

resolve = dvr_script.scriptapp("Resolve")

project_manager = resolve.GetProjectManager()

current_project = project_manager.GetCurrentProject()

project_data = {"name": current_project.GetName()}

def write_file(file_path, data):
    """Serialize and write data to a .dat file"""
    with open(file_path, 'wb') as f:
        f.truncate(0)
        pickle.dump(data, f)

write_file("project.dat", project_data)
