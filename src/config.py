import json
import os
import threading
import customtkinter as ctk

class AppConfig:
    """
    Manages the application's configuration, loading from and saving to a JSON file.
    """
    def __init__(self, config_file="heartrate_config.json"):
        """
        Initializes the configuration manager.

        Args:
            config_file (str): The name of the configuration file.
        """
        self.config_file = config_file
        self.config = {}
        self.lock = threading.Lock()
        self.load_config()

    def load_config(self):
        """
        Loads the configuration from the JSON file.
        If the file doesn't exist, it initializes with default values.
        """
        with self.lock:
            try:
                if os.path.exists(self.config_file):
                    with open(self.config_file, 'r') as f:
                        self.config = json.load(f)
                else:
                    self.config = self.get_default_config()
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading config file: {e}. Using default configuration.")
                self.config = self.get_default_config()

    def save_config(self):
        """
        Saves the current configuration to the JSON file.
        """
        with self.lock:
            try:
                with open(self.config_file, 'w') as f:
                    json.dump(self.config, f, indent=4)
            except IOError as e:
                print(f"Error saving config file: {e}")

    def get(self, key, default=None):
        """
        Retrieves a configuration value for a given key.

        Args:
            key (str): The configuration key.
            default: The default value to return if the key is not found.

        Returns:
            The configuration value or the default value.
        """
        with self.lock:
            return self.config.get(key, default)

    def set(self, key, value):
        """
        Sets a configuration value for a given key.

        Args:
            key (str): The configuration key.
            value: The value to set.
        """
        with self.lock:
            self.config[key] = value

    def get_default_config(self):
        """
        Returns a dictionary with the default configuration settings.

        Returns:
            dict: The default configuration.
        """
        return {
            'theme': 'dark',
            'pulsoid_api_key': '',
            'discord_client_id': '1285817369662328904',
            'large_image': None,
            'small_image': None,
            'window_geometry': '',
            'discord_enabled': True,
            'vrchat_enabled': True,
            'hr_source': 'pulsoid',
            'webhook_config': {
                'url': "",
                'threshold': 120,
                'cooldown': 300,
                'enabled': False
            }
        }

    def apply_theme(self):
        """Applies the saved theme to the application."""
        theme = self.get('theme', 'dark')
        if isinstance(theme, str) and theme.lower() in ['dark', 'light', 'system']:
            ctk.set_appearance_mode(theme.lower())
        else:
            ctk.set_appearance_mode('dark') # Fallback to dark
