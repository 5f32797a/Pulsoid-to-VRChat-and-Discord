import psutil

def is_process_running(process_name: str) -> bool:
    """
    Checks if a process with the given name is currently running.

    Args:
        process_name (str): The name of the process executable (e.g., "Discord.exe").

    Returns:
        bool: True if the process is running, False otherwise.
    """
    try:
        for p in psutil.process_iter(['name']):
            if p.info['name'].lower() == process_name.lower():
                return True
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        # These exceptions can occur, just ignore them
        pass
    return False

def is_discord_running() -> bool:
    """
    Checks if any of the common Discord process names are running.

    Returns:
        bool: True if Discord is running, False otherwise.
    """
    discord_processes = ['discord.exe', 'discord ptb.exe', 'discord canary.exe']
    try:
        running_processes = [p.info['name'].lower() for p in psutil.process_iter(['name'])]
        return any(proc in running_processes for proc in discord_processes)
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        pass
    return False