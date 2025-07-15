import asyncio
import queue
import threading
import customtkinter as ctk
from src.config import AppConfig
from src.logger import Logger
from src.gui import GuiManager
from src.ble_handler import BLEHandler
from src.discord_presence import DiscordPresence
from src.vrchat import VRChatOSC

class MainApplication:
    """
    The main application class that orchestrates all components.
    """
    def __init__(self, root: ctk.CTk):
        self.root = root
        self.config = AppConfig()
        self.data_queue = queue.Queue()
        
        # Initialize GUI first to get the log_text widget
        self.gui = GuiManager(root, self.config, None, self._get_gui_callbacks()) # type: ignore
        
        # Now initialize the logger with the actual widget
        self.logger = Logger(self.gui.log_text)
        self.gui.logger = self.logger # Assign the logger back to the GUI manager
        
        self.ble_handler = BLEHandler(self.data_queue, self.logger)
        client_id = self.config.get('discord_client_id') or '1285817369662328904'
        self.discord_presence = DiscordPresence(client_id, self.logger)
        self.vrchat_osc = VRChatOSC(self.logger)

        self.running = True
        self.monitor_thread = None
        self.last_heart_rate = None

    def _get_gui_callbacks(self) -> dict:
        """Returns a dictionary of callbacks for the GUI."""
        return {
            'on_closing': self.on_closing,
            'apply_settings': self.apply_settings,
            'toggle_discord': self.toggle_discord,
            'toggle_vrchat': self.toggle_vrchat,
            'change_theme': self.change_theme,
            'change_hr_source': self.change_hr_source,
        }

    def run(self):
        """Starts the application."""
        self.config.apply_theme()
        self.logger.process_pending_logs()

        # Start the main monitoring loop in a separate thread
        self.monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
        self.monitor_thread.start()

        # Start the periodic UI update
        self.root.after(1000, self.update_ui)
        
        # Start the GUI main loop
        self.gui.run()

    def monitor_loop(self):
        """The main loop for fetching heart rate data."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        while self.running:
            hr_source = self.config.get('hr_source', 'pulsoid')
            if hr_source == 'bluetooth':
                if not self.ble_handler.is_connected and not self.ble_handler.is_scanning:
                    # For simplicity, auto-connect to the first found device
                    # A real implementation would let the user choose from the GUI
                    devices = loop.run_until_complete(self.ble_handler.scan_for_devices())
                    if devices:
                        loop.run_until_complete(self.ble_handler.connect(devices[0].address))
            # Pulsoid logic would go here
            
            # This loop can be expanded to handle both sources
            threading.Event().wait(5) # Wait for 5 seconds before next cycle

    def update_ui(self):
        """Periodically updates the UI with new data."""
        if not self.running:
            return
            
        try:
            # Process all items in the queue
            while not self.data_queue.empty():
                self.last_heart_rate = self.data_queue.get_nowait()
                self.logger.save_heart_rate_log(self.last_heart_rate)

            # Update GUI elements
            self.gui.update_heart_rate(self.last_heart_rate)
            self.gui.update_status_dots(self.discord_presence.is_connected, self.vrchat_osc.is_connected and self.vrchat_osc.is_vrchat_running())

            # Update external services
            if self.config.get('discord_enabled'):
                self.discord_presence.update_presence(self.last_heart_rate, is_vrchat_running=self.vrchat_osc.is_vrchat_running())
            
            if self.config.get('vrchat_enabled'):
                self.vrchat_osc.update_parameters(self.last_heart_rate)

        except Exception as e:
            self.logger.log_activity(f"UI update error: {e}")

        # Schedule the next update
        self.root.after(1000, self.update_ui)

    def on_closing(self):
        """Handles the application closing event."""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
        
        if self.discord_presence.is_connected:
            self.discord_presence.close()
            
        if self.ble_handler.is_connected:
            loop = asyncio.new_event_loop()
            loop.run_until_complete(self.ble_handler.disconnect())
            loop.close()

        self.config.set('window_geometry', self.root.geometry())
        self.config.save_config()
        self.root.destroy()

    def apply_settings(self):
        """Applies settings from the GUI."""
        self.config.save_config()
        self.logger.log_activity("Settings applied.")
        
        # Reconnect services if necessary
        if self.config.get('discord_enabled') and not self.discord_presence.is_connected:
            self.discord_presence.connect()
        elif not self.config.get('discord_enabled') and self.discord_presence.is_connected:
            self.discord_presence.close()

    def toggle_discord(self):
        """Toggles Discord Rich Presence."""
        is_enabled = self.gui.discord_toggle.get()
        self.config.set('discord_enabled', is_enabled)
        if is_enabled:
            self.discord_presence.connect()
        else:
            self.discord_presence.close()
        self.logger.log_activity(f"Discord presence {'enabled' if is_enabled else 'disabled'}.")

    def toggle_vrchat(self):
        """Toggles VRChat OSC integration."""
        is_enabled = self.gui.vrchat_toggle.get()
        self.config.set('vrchat_enabled', is_enabled)
        # VRChat OSC is connectionless, so we just log the state change
        self.logger.log_activity(f"VRChat OSC {'enabled' if is_enabled else 'disabled'}.")

    def change_theme(self, theme: str):
        """Changes the application theme."""
        self.config.set('theme', theme.lower())
        self.config.apply_theme()
        self.logger.log_activity(f"Theme changed to {theme}.")

    def change_hr_source(self, source: str):
        """Changes the heart rate source."""
        self.config.set('hr_source', source.lower())
        self.logger.log_activity(f"Heart rate source changed to {source}.")
        # Reset connection state
        self.last_heart_rate = None
        if self.ble_handler.is_connected:
            loop = asyncio.new_event_loop()
            loop.run_until_complete(self.ble_handler.disconnect())
            loop.close()

if __name__ == "__main__":
    try:
        # Set DPI awareness for better rendering on Windows
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except (ImportError, AttributeError):
        pass

    root = ctk.CTk()
    app = MainApplication(root)
    app.run()