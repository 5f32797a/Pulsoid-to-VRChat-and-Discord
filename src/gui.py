import customtkinter as ctk
from tkinter import messagebox, colorchooser
from typing import Callable, Optional
from .config import AppConfig
from .logger import Logger

class GuiManager:
    """
    Manages the entire user interface of the Heart Rate Monitor application.
    """
    def __init__(self, root: ctk.CTk, config: AppConfig, logger: Logger, callbacks: dict):
        """
        Initializes the GUI Manager.

        Args:
            root (ctk.CTk): The root CustomTkinter window.
            config (AppConfig): The application configuration instance.
            logger (Logger): The application logger instance.
            callbacks (dict): A dictionary of callback functions for UI events.
        """
        self.root = root
        self.config = config
        self.logger = logger
        self.callbacks = callbacks
        self.settings_window: Optional[ctk.CTkToplevel] = None

        self._setup_main_window()
        self._setup_ui()

    def _setup_main_window(self):
        """Configures the main application window."""
        self.root.title("Heart Rate Monitor")
        self.root.minsize(500, 600)
        
        window_width = 500
        window_height = 600
        
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        geometry = self.config.get('window_geometry')
        if geometry:
            self.root.geometry(geometry)
        else:
            self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")

        self.root.protocol("WM_DELETE_WINDOW", self.callbacks.get('on_closing'))

    def _setup_ui(self):
        """Sets up the main user interface elements."""
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(3, weight=1)

        # Main status frame
        main_status_frame = ctk.CTkFrame(self.root)
        main_status_frame.grid(row=0, column=0, padx=15, pady=(15, 5), sticky="ew")
        main_status_frame.grid_columnconfigure(0, weight=1)

        pulsoid_status = ctk.CTkFrame(main_status_frame, fg_color="transparent")
        pulsoid_status.pack(fill='x', padx=10, pady=5)

        self.pulsoid_status_icon = ctk.CTkLabel(pulsoid_status, text="🔌", font=ctk.CTkFont(size=24), text_color="red")
        self.pulsoid_status_icon.pack(side="left", padx=(5, 5))

        ctk.CTkLabel(pulsoid_status, text="HeartRate Monitor", font=ctk.CTkFont(size=18, weight="bold")).pack(side="left", padx=5)

        settings_button = ctk.CTkButton(pulsoid_status, text="⚙️ Settings", width=100, height=32, corner_radius=8, font=ctk.CTkFont(size=14), command=self.show_settings_window)
        settings_button.pack(side="right", padx=5)

        # Heart Rate Display
        hr_frame = ctk.CTkFrame(self.root)
        hr_frame.grid(row=1, column=0, padx=15, pady=10, sticky="nsew")
        self.hr_label = ctk.CTkLabel(hr_frame, text="Please Wait...", font=ctk.CTkFont(size=48, weight="bold"))
        self.hr_label.pack(pady=(15, 10))

        # Status Display
        status_frame = ctk.CTkFrame(self.root)
        status_frame.grid(row=2, column=0, padx=15, pady=10, sticky="nsew")
        center_container = ctk.CTkFrame(status_frame, fg_color="transparent")
        center_container.pack(expand=True, fill='x', padx=15, pady=10)
        center_container.grid_columnconfigure((0, 1), weight=1)

        # Discord Status
        discord_status_frame = ctk.CTkFrame(center_container, fg_color="transparent")
        discord_status_frame.grid(row=0, column=0, sticky="e", padx=(0, 20))
        self.discord_dot = ctk.CTkLabel(discord_status_frame, text="●", font=ctk.CTkFont(size=22), text_color="red")
        self.discord_dot.pack(side='left', padx=(5, 5))
        ctk.CTkLabel(discord_status_frame, text="Discord", font=ctk.CTkFont(size=16, weight="bold")).pack(side='left', padx=5)
        self.discord_toggle = ctk.CTkSwitch(discord_status_frame, text="", command=self.callbacks.get('toggle_discord'), width=40)
        self.discord_toggle.pack(side='left', padx=10)
        if self.config.get('discord_enabled', True):
            self.discord_toggle.select()

        # VRChat Status
        vrchat_status_frame = ctk.CTkFrame(center_container, fg_color="transparent")
        vrchat_status_frame.grid(row=0, column=1, sticky="w", padx=(20, 0))
        self.vrchat_dot = ctk.CTkLabel(vrchat_status_frame, text="●", font=ctk.CTkFont(size=22), text_color="red")
        self.vrchat_dot.pack(side='left', padx=(5, 5))
        ctk.CTkLabel(vrchat_status_frame, text="VRChat", font=ctk.CTkFont(size=16, weight="bold")).pack(side='left', padx=5)
        self.vrchat_toggle = ctk.CTkSwitch(vrchat_status_frame, text="", command=self.callbacks.get('toggle_vrchat'), width=40)
        self.vrchat_toggle.pack(side='left', padx=10)
        if self.config.get('vrchat_enabled', True):
            self.vrchat_toggle.select()

        # Log Section
        log_frame = ctk.CTkFrame(self.root)
        log_frame.grid(row=3, column=0, padx=15, pady=(10, 15), sticky="nsew")
        log_frame.grid_columnconfigure(0, weight=1)
        log_frame.grid_rowconfigure(1, weight=1)
        ctk.CTkLabel(log_frame, text="Activity Log", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, pady=10)
        self.log_text = ctk.CTkTextbox(log_frame, height=200)
        self.log_text.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))

    def update_heart_rate(self, heart_rate: Optional[int]):
        """Updates the heart rate display."""
        if heart_rate is not None:
            self.hr_label.configure(text=f"{heart_rate} BPM")
            self.pulsoid_status_icon.configure(text="⚡", text_color="green")
        else:
            self.hr_label.configure(text="--")
            self.pulsoid_status_icon.configure(text="🔌", text_color="red")

    def update_status_dots(self, discord_status: bool, vrchat_status: bool):
        """Updates the status indicators for Discord and VRChat."""
        self.discord_dot.configure(text_color="green" if discord_status else "red")
        self.vrchat_dot.configure(text_color="green" if vrchat_status else "red")

    def show_settings_window(self):
        """Displays the settings window."""
        if self.settings_window is not None and self.settings_window.winfo_exists():
            self.settings_window.focus()
            return

        self.settings_window = ctk.CTkToplevel(self.root)
        self.settings_window.title("Settings")
        self.settings_window.geometry("700x600")
        self.settings_window.transient(self.root)
        self.settings_window.grab_set()

        # Create tabs
        tabview = ctk.CTkTabview(self.settings_window)
        tabview.pack(fill="both", expand=True, padx=10, pady=10)

        general_tab = tabview.add("General")
        api_tab = tabview.add("API Keys")
        discord_tab = tabview.add("Discord")
        
        self._setup_general_tab(general_tab)
        self._setup_api_tab(api_tab)
        self._setup_discord_tab(discord_tab)

        save_button = ctk.CTkButton(self.settings_window, text="Save & Close", command=self._save_and_close_settings)
        save_button.pack(pady=10)

        self.settings_window.protocol("WM_DELETE_WINDOW", self._save_and_close_settings)

    def _setup_general_tab(self, tab):
        """Sets up the General settings tab."""
        frame = ctk.CTkFrame(tab, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(frame, text="Theme:", font=ctk.CTkFont(size=14)).pack(anchor="w", pady=(0, 5))
        theme_menu = ctk.CTkOptionMenu(frame, values=["System", "Light", "Dark"], command=self.callbacks.get('change_theme'))
        theme = self.config.get('theme', 'dark')
        if theme:
            theme_menu.set(theme.capitalize())
        theme_menu.pack(anchor="w")

        ctk.CTkLabel(frame, text="Heart Rate Source:", font=ctk.CTkFont(size=14)).pack(anchor="w", pady=(20, 5))
        source_menu = ctk.CTkOptionMenu(frame, values=["Pulsoid", "Bluetooth"], command=self.callbacks.get('change_hr_source'))
        hr_source = self.config.get('hr_source', 'pulsoid')
        if hr_source:
            source_menu.set(hr_source.capitalize())
        source_menu.pack(anchor="w")

    def _setup_api_tab(self, tab):
        """Sets up the API Keys settings tab."""
        frame = ctk.CTkFrame(tab, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(frame, text="Pulsoid API Key:", font=ctk.CTkFont(size=14)).pack(anchor="w", pady=(0, 5))
        self.api_key_entry = ctk.CTkEntry(frame, show="*", width=300)
        self.api_key_entry.insert(0, self.config.get('pulsoid_api_key', ''))
        self.api_key_entry.pack(anchor="w")

    def _setup_discord_tab(self, tab):
        """Sets up the Discord settings tab."""
        frame = ctk.CTkFrame(tab, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(frame, text="Discord Client ID:", font=ctk.CTkFont(size=14)).pack(anchor="w", pady=(0, 5))
        self.discord_id_entry = ctk.CTkEntry(frame, width=300)
        self.discord_id_entry.insert(0, self.config.get('discord_client_id', ''))
        self.discord_id_entry.pack(anchor="w")

        ctk.CTkLabel(frame, text="Large Image URL (optional):", font=ctk.CTkFont(size=14)).pack(anchor="w", pady=(20, 5))
        self.large_image_entry = ctk.CTkEntry(frame, width=300)
        self.large_image_entry.insert(0, self.config.get('large_image') or '')
        self.large_image_entry.pack(anchor="w")

        ctk.CTkLabel(frame, text="Small Image URL (optional):", font=ctk.CTkFont(size=14)).pack(anchor="w", pady=(20, 5))
        self.small_image_entry = ctk.CTkEntry(frame, width=300)
        self.small_image_entry.insert(0, self.config.get('small_image') or '')
        self.small_image_entry.pack(anchor="w")

    def _save_and_close_settings(self):
        """Saves the settings and closes the settings window."""
        # Update config from UI elements
        self.config.set('pulsoid_api_key', self.api_key_entry.get())
        self.config.set('discord_client_id', self.discord_id_entry.get())
        self.config.set('large_image', self.large_image_entry.get() or None)
        self.config.set('small_image', self.small_image_entry.get() or None)
        
        apply_settings_callback = self.callbacks.get('apply_settings')
        if apply_settings_callback:
            apply_settings_callback()
        
        if self.settings_window:
            self.settings_window.destroy()
            self.settings_window = None
        
        messagebox.showinfo("Settings Saved", "Your settings have been saved and applied.")

    def show_error(self, title: str, message: str):
        """Displays an error message box."""
        messagebox.showerror(title, message)

    def run(self):
        """Starts the GUI main loop."""
        self.root.mainloop()