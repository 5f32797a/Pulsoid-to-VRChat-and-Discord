# build_exe.py
import PyInstaller.__main__
import os
import sys

def create_exe(script_path, icon_path=None, name=None, assets_path=None):
    """
    Convert a Python script to an executable.

    Args:
        script_path (str): Path to the main Python script.
        icon_path (str, optional): Path to the .ico file.
        name (str, optional): Name for the output executable.
        assets_path (str, optional): Path to the assets directory to be included.
    """
    
    if not os.path.exists(script_path):
        raise FileNotFoundError(f"Script file not found: {script_path}")
    
    if icon_path and not os.path.exists(icon_path):
        raise FileNotFoundError(f"Icon file not found: {icon_path}")
    
    # Basic PyInstaller arguments
    args = [
        script_path,  # Your main Python script
        '--onefile',  # Create a single executable file
        '--clean',    # Clean PyInstaller cache
        '--noconsole',  # Don't show console window when running the exe
    ]
    
    # Add icon if specified
    if icon_path:
        args.extend(['--icon', icon_path])
    
    # Add name if specified
    if name:
        args.extend(['--name', name])

    # Add assets if specified
    if assets_path:
        args.extend(['--add-data', f'{assets_path}{os.pathsep}.'])
    
    # Run PyInstaller
    PyInstaller.__main__.run(args)

if __name__ == "__main__":
    # Example usage
    script_path = os.path.join("src", "main.py")
    icon_path = os.path.join("assets", "4403870.ico")
    assets_path = "assets"
    output_name = "HeartRateVRC_Discord_Beta"
    
    try:
        # Create assets directory if it doesn't exist
        if not os.path.exists(assets_path):
            os.makedirs(assets_path)
            
        # Move icon to assets folder if it exists in root
        if os.path.exists("4403870.ico"):
            os.rename("4403870.ico", icon_path)

        create_exe(script_path, icon_path, output_name, assets_path)
        print("Executable created successfully!")
    except Exception as e:
        print(f"Error creating executable: {e}")