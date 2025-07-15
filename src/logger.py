import os
import json
from datetime import datetime
import customtkinter as ctk
from tkinter import TclError

class Logger:
    """
    Manages logging for the application, directing messages to a GUI textbox
    and saving them to daily JSON log files.
    """
    def __init__(self, log_textbox: ctk.CTkTextbox, log_dir="HeartRate_Logs"):
        """
        Initializes the logger.

        Args:
            log_textbox (ctk.CTkTextbox): The textbox widget for displaying logs.
            log_dir (str): The directory where log files will be stored.
        """
        self.log_text = log_textbox
        self.log_dir = log_dir
        self.pending_logs = []
        self._setup_log_dir()

    def _setup_log_dir(self):
        """Creates the log directory if it doesn't exist."""
        try:
            if not os.path.exists(self.log_dir):
                os.makedirs(self.log_dir)
        except OSError as e:
            self.log_activity(f"Error creating log directory: {e}", to_file=False)

    def log_activity(self, message: str, to_file: bool = True):
        """
        Logs a message to the GUI and optionally to a file.

        Args:
            message (str): The message to log.
            to_file (bool): Whether to save the log to a file.
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"

        try:
            if self.log_text and self.log_text.winfo_exists():
                self.log_text.insert("0.0", log_message)
            else:
                self.pending_logs.append(log_message)
        except TclError:
            # This can happen if the widget is destroyed
            self.pending_logs.append(log_message)

        if to_file:
            self.save_log_entry({"timestamp": datetime.now().isoformat(), "message": message})

    def process_pending_logs(self):
        """Writes any pending logs to the GUI textbox."""
        try:
            if self.log_text and self.log_text.winfo_exists():
                while self.pending_logs:
                    self.log_text.insert("0.0", self.pending_logs.pop(0))
        except TclError:
            # Widget might have been destroyed
            pass

    def save_log_entry(self, log_entry: dict):
        """
        Saves a single log entry to the appropriate daily log file.

        Args:
            log_entry (dict): The log entry to save.
        """
        try:
            current_date = datetime.now().strftime("%Y-%m-%d")
            log_file = os.path.join(self.log_dir, f"activity_{current_date}.json")

            data = {"logs": []}
            if os.path.exists(log_file):
                try:
                    with open(log_file, 'r') as f:
                        data = json.load(f)
                except (json.JSONDecodeError, IOError):
                    # If file is corrupted or empty, start fresh
                    pass
            
            data.get("logs", []).append(log_entry)

            with open(log_file, 'w') as f:
                json.dump(data, f, indent=4)
        except (IOError, TypeError) as e:
            # Log this error to the GUI but not to file to avoid a loop
            self.log_activity(f"Error saving log entry: {e}", to_file=False)

    def save_heart_rate_log(self, heart_rate: int):
        """
        Saves heart rate data to a separate daily log file.

        Args:
            heart_rate (int): The heart rate measurement.
        """
        try:
            current_date = datetime.now().strftime("%Y-%m-%d")
            log_file = os.path.join(self.log_dir, f"heartrate_{current_date}.json")

            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "heart_rate": heart_rate
            }

            data = {"logs": []}
            if os.path.exists(log_file):
                try:
                    with open(log_file, 'r') as f:
                        data = json.load(f)
                except (json.JSONDecodeError, IOError):
                    pass
            
            data.get("logs", []).append(log_entry)

            with open(log_file, 'w') as f:
                json.dump(data, f, indent=4)
        except (IOError, TypeError) as e:
            self.log_activity(f"Error saving heart rate log: {e}", to_file=False)
