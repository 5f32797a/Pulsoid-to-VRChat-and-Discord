import asyncio
import struct
from bleak import BleakScanner, BleakClient
from bleak.exc import BleakError
from bleak.backends.characteristic import BleakGATTCharacteristic
from typing import Optional
from queue import Queue
from .logger import Logger

HR_SERVICE_UUID = "0000180d-0000-1000-8000-00805f9b34fb"
HR_CHARACTERISTIC_UUID = "00002a37-0000-1000-8000-00805f9b34fb"

class BLEHandler:
    """
    Handles BLE scanning, connection, and data reception for heart rate monitors.
    """
    def __init__(self, data_queue: Queue, logger: Logger):
        """
        Initializes the BLE handler.

        Args:
            data_queue (Queue): A thread-safe queue to send heart rate data to.
            logger (Logger): The application logger instance.
        """
        self.data_queue = data_queue
        self.logger = logger
        self.client: Optional[BleakClient] = None
        self.is_connected = False
        self.is_scanning = False
        self.device_name = None

    async def scan_for_devices(self, timeout=5.0) -> list:
        """
        Scans for nearby BLE devices that advertise the heart rate service.

        Args:
            timeout (float): The duration of the scan in seconds.

        Returns:
            list: A list of discovered devices.
        """
        self.is_scanning = True
        self.logger.log_activity("Scanning for BLE heart rate devices...")
        try:
            devices = await BleakScanner.discover(timeout=timeout, service_uuids=[HR_SERVICE_UUID])
            self.logger.log_activity(f"Found {len(devices)} devices.")
            return list(devices)
        except BleakError as e:
            self.logger.log_activity(f"BLE scanning error: {e}")
            return []
        finally:
            self.is_scanning = False

    async def connect(self, device_address: str):
        """
        Connects to a specific BLE device by its address.

        Args:
            device_address (str): The address of the device to connect to.
        """
        if self.is_connected:
            return

        self.logger.log_activity(f"Attempting to connect to {device_address}...")
        try:
            self.client = BleakClient(device_address)
            await self.client.connect()
            self.is_connected = self.client.is_connected
            if self.is_connected:
                self.device_name = self.client.address  # Or device.name if available
                self.logger.log_activity(f"Connected to {self.device_name}")
                await self.client.start_notify(HR_CHARACTERISTIC_UUID, self._notification_handler)
            else:
                self.logger.log_activity("Failed to connect.")
        except BleakError as e:
            self.logger.log_activity(f"BLE connection error: {e}")
            self.is_connected = False
            self.client = None
        except Exception as e:
            self.logger.log_activity(f"An unexpected error occurred during BLE connection: {e}")
            self.is_connected = False
            self.client = None

    async def disconnect(self):
        """
        Disconnects from the currently connected BLE device.
        """
        if self.client and self.is_connected:
            try:
                await self.client.stop_notify(HR_CHARACTERISTIC_UUID)
                await self.client.disconnect()
                self.logger.log_activity(f"Disconnected from {self.device_name}")
            except BleakError as e:
                self.logger.log_activity(f"BLE disconnection error: {e}")
            finally:
                self.is_connected = False
                self.client = None
                self.device_name = None

    def _notification_handler(self, sender: BleakGATTCharacteristic, data: bytearray):
        """
        Callback for handling heart rate notifications from the BLE device.
        Parses the data and puts the heart rate value into the queue.

        Args:
            sender (BleakGATTCharacteristic): The characteristic that sent the notification.
            data (bytearray): The notification data.
        """
        # Heart rate data format can vary. This is a common implementation.
        # The first byte contains flags, the rest is the heart rate.
        flags = data[0]
        hr_format = (flags & 0x01)  # 0 = UINT8, 1 = UINT16

        if hr_format == 1:  # UINT16
            heart_rate = struct.unpack('<H', data[1:3])[0]
        else:  # UINT8
            heart_rate = struct.unpack('<B', data[1:2])[0]

        if heart_rate > 0:
            self.data_queue.put(heart_rate)