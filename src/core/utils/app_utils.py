from core.utils.tk_utils import messagebox

def new_updates(manual_check=False):
    """Check for new updates on GitHub. Returns a boolean"""
    import os
    from core.utils.file_utils import read_file, write_file, config_file
    import time
    from _version import __version__
    global RELEASE_DATA
    if os.path.exists(config_file()):
        try:
            last_update_check = read_file(config_file())["last_update_check"]
            settings = read_file(config_file())
        except (KeyError):
         # If the config file doesn't have the key
            last_update_check = time.time()
            settings = read_file(config_file())
            settings.update({"last_update_check": last_update_check})
            write_file(config_file(), settings)
    else:
        os.makedirs(os.path.dirname(config_file()), exist_ok=True)
        last_update_check = time.time()  # if the file doesn't exist
        settings = {}
        settings.update({"last_update_check": last_update_check})
        write_file(config_file(), settings)
    
    if time.time() - last_update_check < 43200 and not manual_check:
        return False  # Check for updates only once every 12 hours
    
    settings.update({"last_update_check": time.time()})
    write_file(config_file(), settings)
    import requests
    try:
        print("Checking for updates...")
        response = requests.get("https://api.github.com/repos/adam-color/AppUsageGUI/releases/latest", timeout=10)
        response.raise_for_status()  # Raises an HTTPError for bad responses

        data = response.json()
        RELEASE_DATA = data  # Store the release data globally
        latest_version = data["tag_name"].lstrip('v').split('.')
        current_version = __version__.split('.')

        # Compare version numbers
        for latest, current in zip(latest_version, current_version):
            if int(latest) > int(current):
                print("New updates available!")
                return True
            elif int(latest) < int(current):
                print("No new updates available.")
                return False

        # If we've gotten here, the versions are equal
        print("No new updates available.")
        return False

    except requests.RequestException as e:
        from traceback import format_exc
        print(f"Error checking for updates: Network error - {str(e) + ' - ' + str(format_exc())}")
    except (KeyError, ValueError, IndexError) as e:
        from traceback import format_exc
        print(f"Error checking for updates: Parsing error - {str(e) + ' - ' + str(format_exc())}")
    except Exception:
        from traceback import format_exc
        error = f"An unexpected error occurred while checking for updates:\n{str(format_exc())}"
        messagebox.showerror("Error", error)
        print(error)
    return False

def update():
    """Prompt the user to download the latest update from GitHub."""
    import sys
    import platform
    ask_update = messagebox.askquestion(
            'AppUsageGUI Updates',
            "A new update is available. Would you like to download it from the GitHub page?"
        )
    if ask_update == "yes":
        if sys.platform == "win32":
            suffix = "WINDOWS_setup.exe"
        elif sys.platform == "darwin":
            if platform.processor() == "arm":
                suffix = "macOS_arm64_setup.dmg"
            else:
                suffix = None
        else:
            suffix = None
        
        for asset in RELEASE_DATA['assets']:
            if asset['name'].endswith(suffix):
                download_url = asset['browser_download_url']
                break
        import webbrowser
        if suffix is None:
            webbrowser.open_new_tab("https://github.com/adam-color/AppUsageGUI/releases/latest")
            messagebox.showinfo("Update", "Your platform is currently unsupported.")
        elif download_url is not None:
            webbrowser.open_new_tab(download_url)
            webbrowser.open_new_tab("https://github.com/adam-color/AppUsageGUI/releases/latest")
            messagebox.showinfo("Update", "Please install the latest version after it downloads,\nautomatic updates are not yet available.\n\nPlease close AppUsageGUI after you download the new installer.")
