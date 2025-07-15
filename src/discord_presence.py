import time
import asyncio
from typing import Optional
from pypresence import Presence, exceptions
from .utils import is_discord_running
from .logger import Logger

class DiscordPresence:
    """
    Manages the connection and updates for Discord Rich Presence.
    """
    def __init__(self, client_id: str, logger: Logger):
        """
        Initializes the Discord Presence manager.

        Args:
            client_id (str): The Discord application client ID.
            logger (Logger): The application logger instance.
        """
        self.client_id = client_id
        self.logger = logger
        self.rpc = None
        self.is_connected = False

    def connect(self):
        """
        Connects to the Discord RPC.
        Retries a few times if the connection fails.
        """
        if not is_discord_running():
            self.logger.log_activity("Discord is not running. Cannot connect Rich Presence.")
            return

        if self.is_connected:
            return

        try:
            self.rpc = Presence(self.client_id, loop=asyncio.get_event_loop())
            self.rpc.connect()
            self.is_connected = True
            self.logger.log_activity("Discord Rich Presence connected.")
        except (exceptions.DiscordNotFound, exceptions.InvalidPipe, FileNotFoundError) as e:
            self.logger.log_activity(f"Could not connect to Discord: {e}")
            self.rpc = None
        except Exception as e:
            self.logger.log_activity(f"An unexpected error occurred while connecting to Discord: {e}")
            self.rpc = None

    def close(self):
        """
        Closes the connection to the Discord RPC.
        """
        if self.rpc and self.is_connected:
            try:
                self.rpc.close()
                self.logger.log_activity("Discord Rich Presence disconnected.")
            except Exception as e:
                self.logger.log_activity(f"Error closing Discord RPC: {e}")
            finally:
                self.rpc = None
                self.is_connected = False

    def update_presence(self, heart_rate: Optional[int], custom_large_image: Optional[str] = None, custom_small_image: Optional[str] = None, is_vrchat_running: bool = False):
        """
        Updates the user's Discord presence with the current heart rate.

        Args:
            heart_rate (Optional[int]): The current heart rate. Can be None if disconnected.
            custom_large_image (Optional[str]): URL for a custom large image.
            custom_small_image (Optional[str]): URL for a custom small image.
            is_vrchat_running (bool): Whether VRChat is running.
        """
        if not self.is_connected or not self.rpc:
            return

        try:
            if not is_discord_running():
                self.logger.log_activity("Discord connection lost.")
                self.close()
                return

            presence_data = {
                'start': int(time.time()),
                'large_image': custom_large_image or 'fas-fa-heart',
                'small_image': custom_small_image,
                'large_text': 'Heart Rate Monitor',
                'small_text': 'VRChat Integration Active' if is_vrchat_running else 'VRChat Offline'
            }

            if heart_rate is not None:
                presence_data['details'] = f'❤ Heart Rate: {heart_rate} BPM'
                presence_data['state'] = 'Monitoring heart rate...'
            else:
                presence_data['details'] = '💔 Heart Rate Disconnected'
                presence_data['state'] = 'Waiting for connection...'

            self.rpc.update(**presence_data)
        except (exceptions.InvalidID, exceptions.ConnectionTimeout) as e:
            self.logger.log_activity(f"Discord presence update failed: {e}")
            self.close()
        except Exception as e:
            self.logger.log_activity(f"An unexpected error occurred during presence update: {e}")
            self.close()