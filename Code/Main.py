import tkinter as tk
from selenium_ui import SeleniumUI
from settings_manager import SettingsManager

if __name__ == "__main__":
    root = tk.Tk()
    selenium_ui = SeleniumUI(root)
    
    # Load settings from cache
    SettingsManager.load_settings_from_cache(selenium_ui)

    root.protocol("WM_DELETE_WINDOW", selenium_ui.on_close)
    root.mainloop()