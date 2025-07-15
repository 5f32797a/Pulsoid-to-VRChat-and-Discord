from pythonosc import udp_client
from .utils import is_process_running
from .logger import Logger
from typing import Optional

class VRChatOSC:
    """
    Manages the OSC connection and parameter updates for VRChat.
    """
    def __init__(self, logger: Logger, ip="127.0.0.1", port=9000):
        """
        Initializes the VRChat OSC client.

        Args:
            logger (Logger): The application logger instance.
            ip (str): The IP address for the OSC server (usually localhost).
            port (int): The port for the OSC server (usually 9000).
        """
        self.logger = logger
        self.client = udp_client.SimpleUDPClient(ip, port)
        self.is_connected = False
        self._check_connection()

    def _check_connection(self):
        """
        Checks if the OSC client was initialized successfully.
        A simple check, as UDP is connectionless.
        """
        if self.client:
            self.is_connected = True
            self.logger.log_activity("VRChat OSC client initialized.")
        else:
            self.is_connected = False
            self.logger.log_activity("VRChat OSC client failed to initialize.")

    def is_vrchat_running(self) -> bool:
        """
        Checks if the VRChat process is running.

        Returns:
            bool: True if VRChat.exe is running, False otherwise.
        """
        return is_process_running("VRChat.exe")

    def update_parameters(self, heart_rate: Optional[int]):
        """
        Updates VRChat avatar parameters with the current heart rate.

        Args:
            heart_rate (Optional[int]): The current heart rate. If None, resets parameters.
        """
        if not self.is_connected or not self.is_vrchat_running():
            return

        try:
            if heart_rate is not None:
                self.client.send_message("/avatar/parameters/HR", int(heart_rate))
                hr_percent = min(max((heart_rate - 40) / (200 - 40), 0.0), 1.0)
                self.client.send_message("/avatar/parameters/HRPercent", hr_percent)
                self.client.send_message("/avatar/parameters/isHRConnected", True)
            else:
                # Reset parameters if heart rate is not available
                self.client.send_message("/avatar/parameters/HR", 0)
                self.client.send_message("/avatar/parameters/HRPercent", 0.0)
                self.client.send_message("/avatar/parameters/isHRConnected", False)
        except Exception as e:
            self.logger.log_activity(f"Failed to send VRChat OSC message: {e}")
            self.is_connected = False