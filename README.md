# Pulsoid-to-VRChat-and-Discord

This application monitors your heart rate using a Bluetooth LE heart rate device or Pulsoid and displays it in a desktop application. It also provides integration with Discord Rich Presence and VRChat OSC.

## Features

*   **Heart Rate Monitoring**: Connect to a Bluetooth LE heart rate monitor or use Pulsoid to get real-time heart rate data.
*   **Desktop GUI**: A simple and clean user interface to display your heart rate and connection status.
*   **Discord Rich Presence**: Show your current heart rate on your Discord profile.
*   **VRChat OSC Integration**: Send your heart rate data to VRChat to be used with compatible avatars.
*   **Customizable Settings**: Configure your API keys, Discord presence, and application theme.
*   **Logging**: All activity and heart rate data is logged for later review.

## Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/5f32797a/Pulsoid-to-VRChat-and-Discord.git
    cd Pulsoid-to-VRChat-and-Discord
    ```

2.  **Create a virtual environment:**
    ```bash
    python -m venv .venv
    ```

3.  **Activate the virtual environment:**
    *   On Windows:
        ```bash
        .venv\Scripts\activate
        ```
    *   On macOS/Linux:
        ```bash
        source .venv/bin/activate
        ```

4.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Running the Application

To run the application, execute the following command from the root directory of the project:

```bash
python main.py
```

## Configuration

The application settings can be configured through the settings window in the application. The configuration is saved in the `heartrate_config.json` file.

*   **Theme**: Choose between `dark`, `light`, and `system` themes.
*   **Heart Rate Source**: Select between `Pulsoid` and `Bluetooth`.
*   **API Keys**: Enter your Pulsoid API key.
*   **Discord**: Set your Discord client ID and customize the rich presence with large and small images.

### VRChat Avatar Setup

To use the VRChat OSC integration, you need to set up your avatar with the following parameters:

*   **`HR`** (Int): Your current heart rate.
*   **`HRPercent`** (Float): Your heart rate as a percentage of the range 40-200 BPM.
*   **`isHRConnected`** (Bool): A boolean indicating if the heart rate monitor is connected.

You can use these parameters to create animations and effects on your avatar that react to your heart rate.
