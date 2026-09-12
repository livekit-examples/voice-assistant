import asyncio
import os
import sys
import subprocess
import webbrowser
import datetime
import ctypes
import psutil
from pathlib import Path
from PIL import ImageGrab
from livekit.agents import llm

# Ensure UTF-8 output on Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Windows Virtual-Key codes
VK_VOLUME_MUTE = 0xAD
VK_VOLUME_DOWN = 0xAE
VK_VOLUME_UP = 0xAF
VK_MEDIA_NEXT_TRACK = 0xB0
VK_MEDIA_PREV_TRACK = 0xB1
VK_MEDIA_PLAY_PAUSE = 0xB3

# Notes folder
NOTES_DIR = Path.home() / "Documents" / "AI_Voice_Notes"
NOTES_DIR.mkdir(parents=True, exist_ok=True)

# Screenshots folder
SCREENSHOTS_DIR = Path.home() / "Pictures" / "AI_Voice_Screenshots"
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

def log_action(icon: str, title: str, details: str = "", status: str = "EXECUTED"):
    """Print high-visibility, formatted logs to the console for every voice command."""
    border = "=" * 65
    print(f"\n{border}", flush=True)
    print(f"🎤 {icon} [VOICE ACTION TRIGGERED]: {title.upper()}", flush=True)
    if details:
        print(f"   ℹ️  Details: {details}", flush=True)
    print(f"   ⚡ Result: {status}", flush=True)
    print(f"{border}\n", flush=True)

# Common Windows App Aliases
APP_COMMANDS = {
    "notepad": "notepad.exe",
    "notes": "notepad.exe",
    "calculator": "calc.exe",
    "calc": "calc.exe",
    "chrome": "chrome.exe",
    "google chrome": "chrome.exe",
    "edge": "msedge.exe",
    "microsoft edge": "msedge.exe",
    "browser": "msedge.exe",
    "file explorer": "explorer.exe",
    "explorer": "explorer.exe",
    "files": "explorer.exe",
    "my computer": "explorer.exe",
    "settings": "ms-settings:",
    "terminal": "wt.exe",
    "cmd": "cmd.exe",
    "command prompt": "cmd.exe",
    "powershell": "powershell.exe",
    "task manager": "taskmgr.exe",
    "taskmanager": "taskmgr.exe",
    "paint": "mspaint.exe",
    "spotify": "spotify.exe",
    "vscode": "code.cmd",
    "vs code": "code.cmd",
    "visual studio code": "code.cmd",
    "word": "winword.exe",
    "excel": "excel.exe",
    "powerpoint": "powerpnt.exe",
    "control panel": "control.exe",
    "snipping tool": "snippingtool.exe",
}

def launch_gui(target: str, fallback_cmd: str = "") -> bool:
    """Launch an application or document using the Windows Shell to guarantee it appears on the interactive desktop."""
    # Method 1: os.startfile (ShellExecute) - tells Windows shell to display the window
    try:
        os.startfile(target)
        return True
    except Exception:
        pass
    
    # Method 2: explorer.exe - runs through Windows Explorer on user desktop
    try:
        subprocess.Popen(f'explorer.exe "{target}"', shell=True)
        return True
    except Exception:
        pass
        
    # Method 3: PowerShell Start-Process
    try:
        subprocess.Popen(f'powershell.exe -NoProfile -Command "Start-Process \'{target}\'"', shell=True)
        return True
    except Exception:
        pass
        
    # Method 4: Fallback command
    if fallback_cmd:
        try:
            subprocess.Popen(fallback_cmd, shell=True)
            return True
        except Exception:
            pass
            
    return False

def _press_vkey(vkey: int, repeat: int = 1):
    for _ in range(repeat):
        ctypes.windll.user32.keybd_event(vkey, 0, 0, 0)
        ctypes.windll.user32.keybd_event(vkey, 0, 2, 0)

@llm.function_tool
async def open_application(app_name: str) -> str:
    """Open an application or desktop software on the user's laptop/PC screen.
    
    Args:
        app_name: Name of the application (e.g., 'notepad', 'chrome', 'calculator', 'spotify', 'vs code', 'file explorer', 'settings', 'paint', etc.)
    """
    clean_name = app_name.strip().lower()
    target = APP_COMMANDS.get(clean_name, clean_name)
    
    success = launch_gui(target, fallback_cmd=f'start "" "{clean_name}"')
    if success:
        log_action("🚀", f"OPEN APP: {app_name}", f"Target: {target}", "SUCCESS: Launched on screen")
        return f"Successfully opened {app_name} on your screen."
    else:
        log_action("❌", f"OPEN APP: {app_name}", f"Target: {target}", "FAILED")
        return f"Could not launch {app_name}. Please make sure it is installed."

@llm.function_tool
async def close_application(app_name: str) -> str:
    """Close an open application or process on the user's laptop.
    
    Args:
        app_name: Name of the app to close (e.g. 'notepad', 'chrome', 'calculator')
    """
    clean_name = app_name.strip().lower().replace(".exe", "")
    process_name = f"{clean_name}.exe"
    try:
        res = subprocess.run(f"taskkill /IM {process_name} /F", shell=True, capture_output=True, text=True)
        if "SUCCESS" in res.stdout or res.returncode == 0:
            log_action("🛑", f"CLOSE APP: {app_name}", f"Terminated process {process_name}", "SUCCESS: Closed on screen")
            return f"Closed {app_name} on your screen."
        else:
            log_action("⚠️", f"CLOSE APP: {app_name}", f"Process {process_name} not found or already closed", "NOT RUNNING")
            return f"{app_name} does not appear to be running."
    except Exception as e:
        log_action("❌", f"CLOSE APP: {app_name}", str(e), "ERROR")
        return f"Error closing {app_name}: {e}"

@llm.function_tool
async def open_website(url_or_name: str) -> str:
    """Open a website or web service in the default web browser on screen.
    
    Args:
        url_or_name: URL or website name (e.g. 'youtube.com', 'google.com', 'github', 'reddit', 'chatgpt')
    """
    target = url_or_name.strip().lower()
    
    site_map = {
        "youtube": "https://www.youtube.com",
        "google": "https://www.google.com",
        "github": "https://www.github.com",
        "reddit": "https://www.reddit.com",
        "twitter": "https://www.twitter.com",
        "x": "https://www.x.com",
        "gmail": "https://mail.google.com",
        "netflix": "https://www.netflix.com",
        "chatgpt": "https://chat.openai.com",
        "amazon": "https://www.amazon.com",
        "spotify": "https://open.spotify.com",
    }
    
    url = site_map.get(target)
    if not url:
        if not target.startswith("http://") and not target.startswith("https://"):
            url = f"https://{target}"
            if "." not in target:
                url = f"https://www.google.com/search?q={target}"
        else:
            url = target

    try:
        webbrowser.open(url)
        launch_gui(url)
        log_action("🌐", f"OPEN WEBSITE: {url_or_name}", f"URL: {url}", "SUCCESS: Opened in browser")
        return f"Opened {url_or_name} in your browser."
    except Exception as e:
        log_action("❌", f"OPEN WEBSITE: {url_or_name}", str(e), "ERROR")
        return f"Failed to open {url_or_name}: {e}"

@llm.function_tool
async def search_web(query: str, platform: str = "google") -> str:
    """Search Google or YouTube for a query.
    
    Args:
        query: What to search for (e.g. 'latest AI news', 'lofi beats', 'weather in Mumbai')
        platform: Where to search ('google' or 'youtube')
    """
    clean_query = query.strip()
    if platform.lower() == "youtube":
        url = f"https://www.youtube.com/results?search_query={clean_query.replace(' ', '+')}"
        log_action("🔍", f"SEARCH YOUTUBE: '{clean_query}'", f"URL: {url}", "SUCCESS")
        webbrowser.open(url)
        launch_gui(url)
        return f"Searching YouTube for '{clean_query}'."
    else:
        url = f"https://www.google.com/search?q={clean_query.replace(' ', '+')}"
        log_action("🔍", f"SEARCH GOOGLE: '{clean_query}'", f"URL: {url}", "SUCCESS")
        webbrowser.open(url)
        launch_gui(url)
        return f"Searching Google for '{clean_query}'."

@llm.function_tool
async def write_note(note_content: str, title: str = "") -> str:
    """Write and save a note with the user's spoken words, and open it visibly in Notepad on screen.
    
    Args:
        note_content: The exact text/thoughts/information to write down in the note.
        title: Brief title for the note (e.g. 'Meeting Notes', 'Ideas', 'Shopping List').
    """
    now = datetime.datetime.now()
    timestamp_str = now.strftime("%Y-%m-%d_%H-%M-%S")
    clean_title = "".join(c for c in title if c.isalnum() or c in (" ", "_", "-")).strip() or "Voice_Note"
    filename = f"{clean_title}_{timestamp_str}.txt"
    file_path = NOTES_DIR / filename
    
    formatted_content = f"=========================================\nAI VOICE NOTE - {now.strftime('%A, %B %d, %Y at %I:%M %p')}\nTitle: {title or 'Voice Note'}\n=========================================\n\n{note_content.strip()}\n"
    
    try:
        file_path.write_text(formatted_content, encoding="utf-8")
        # Launch Notepad visibly on screen with the new note file
        launch_gui(str(file_path), fallback_cmd=f'notepad.exe "{file_path}"')
        log_action("📝", f"WRITE NOTE: {title or 'Voice Note'}", f"Saved to: {file_path}\n   Content: \"{note_content.strip()}\"", "SUCCESS: Opened Notepad on screen")
        return f"I've written your note '{title or 'Voice Note'}' and opened it in Notepad on your screen."
    except Exception as e:
        log_action("❌", "WRITE NOTE", str(e), "ERROR")
        return f"Failed to save note: {e}"

@llm.function_tool
async def volume_control(action: str, intensity: int = 5) -> str:
    """Adjust or mute the laptop audio volume.
    
    Args:
        action: 'up', 'down', 'mute', or 'unmute'
        intensity: Number of volume steps to change (default is 5)
    """
    act = action.strip().lower()
    if act == "up":
        _press_vkey(VK_VOLUME_UP, repeat=intensity)
        log_action("🔊", "VOLUME UP", f"Increased volume by {intensity} steps", "SUCCESS")
        return "Turned volume up."
    elif act == "down":
        _press_vkey(VK_VOLUME_DOWN, repeat=intensity)
        log_action("🔉", "VOLUME DOWN", f"Decreased volume by {intensity} steps", "SUCCESS")
        return "Turned volume down."
    elif act in ("mute", "unmute"):
        _press_vkey(VK_VOLUME_MUTE, repeat=1)
        log_action("🔇", "VOLUME MUTE", "Toggled volume mute", "SUCCESS")
        return "Toggled volume mute."
    else:
        log_action("⚠️", "VOLUME CONTROL", f"Unknown action {action}", "INVALID ACTION")
        return f"Unknown volume action: {action}. Please use up, down, or mute."

@llm.function_tool
async def media_control(action: str) -> str:
    """Control media playback on the laptop (music, videos).
    
    Args:
        action: 'play', 'pause', 'play_pause', 'next', or 'previous'
    """
    act = action.strip().lower()
    if act in ("play", "pause", "play_pause", "toggle"):
        _press_vkey(VK_MEDIA_PLAY_PAUSE, repeat=1)
        log_action("⏯️", "MEDIA PLAY/PAUSE", "Toggled media playback", "SUCCESS")
        return "Toggled media playback."
    elif act in ("next", "skip"):
        _press_vkey(VK_MEDIA_NEXT_TRACK, repeat=1)
        log_action("⏭️", "MEDIA NEXT TRACK", "Skipped to next song", "SUCCESS")
        return "Skipped to next track."
    elif act in ("previous", "prev", "back"):
        _press_vkey(VK_MEDIA_PREV_TRACK, repeat=1)
        log_action("⏮️", "MEDIA PREVIOUS TRACK", "Returned to previous song", "SUCCESS")
        return "Returned to previous track."
    else:
        return f"Unknown media action: {action}."

@llm.function_tool
async def take_screenshot(custom_name: str = "") -> str:
    """Take a screenshot of the laptop screen.
    
    Args:
        custom_name: Optional name for the screenshot file.
    """
    now = datetime.datetime.now()
    timestamp_str = now.strftime("%Y-%m-%d_%H-%M-%S")
    name = "".join(c for c in custom_name if c.isalnum() or c in ("_", "-")).strip() or "Screenshot"
    file_path = SCREENSHOTS_DIR / f"{name}_{timestamp_str}.png"
    
    # Method 1: Try PIL ImageGrab
    try:
        screenshot = ImageGrab.grab(all_screens=True)
        screenshot.save(file_path, "PNG")
        log_action("📸", "TAKE SCREENSHOT", f"Saved to: {file_path}", "SUCCESS: Captured with PIL")
        return f"Screenshot captured and saved to your Pictures folder as {file_path.name}."
    except Exception as pil_err:
        # Method 2: Launch Windows native Screen Snip overlay / Snipping Tool
        try:
            launch_gui("ms-screenclip:")
            log_action("📸", "TAKE SCREENSHOT", f"Opened Windows Screen Snip tool on screen", "SUCCESS: Screen Snip launched")
            return "I have opened the Windows Screen Snipping tool on your screen so you can capture the area."
        except Exception as e:
            log_action("❌", "TAKE SCREENSHOT", f"Failed: {e}", "ERROR")
            return f"Failed to take screenshot: {e}"

@llm.function_tool
async def get_system_status() -> str:
    """Get the laptop's battery status, charging status, CPU/RAM usage, and current date and time."""
    now = datetime.datetime.now().strftime("%I:%M %p on %A, %B %d, %Y")
    
    battery = psutil.sensors_battery()
    bat_str = "No battery detected (desktop)"
    if battery:
        status = "charging" if battery.power_plugged else "on battery"
        bat_str = f"{battery.percent}% ({status})"
        
    cpu = psutil.cpu_percent(interval=0.1)
    ram = psutil.virtual_memory().percent
    
    log_action("📊", "SYSTEM STATUS CHECK", f"Time: {now} | Battery: {bat_str} | CPU: {cpu}% | RAM: {ram}%", "SUCCESS")
    return f"The time is {now}. Battery is at {bat_str}. CPU usage is {cpu}%, and RAM usage is {ram}%."

@llm.function_tool
async def lock_laptop() -> str:
    """Lock the laptop workstation immediately."""
    try:
        ctypes.windll.user32.LockWorkStation()
        log_action("🔒", "LOCK WORKSTATION", "Locked Windows session", "SUCCESS")
        return "Locked your laptop."
    except Exception as e:
        log_action("❌", "LOCK WORKSTATION", str(e), "ERROR")
        return f"Could not lock laptop: {e}"

@llm.function_tool
async def run_terminal_command(command: str, description: str = "") -> str:
    """Automatically execute any Windows PowerShell or system command requested by the user.
    Use this when the user wants to perform computer tasks like checking disk space,
    creating directories, file management, checking networking/IP, pinging hosts, or querying system details.
    
    Args:
        command: The Windows PowerShell command to execute (e.g., 'Get-PSDrive C', 'New-Item -ItemType Directory -Path "$HOME\\Desktop\\Projects" -Force', 'ipconfig', 'Get-Process', etc.)
        description: Brief explanation of what the command accomplishes.
    """
    log_action("💻", f"AUTO COMMAND: {command}", f"Purpose: {description or 'Windows system command'}", "RUNNING...")
    
    # Safety guard against catastrophic disk destruction
    forbidden = ["format ", "del /s /q c:\\", "remove-item -recurse c:\\", "rmdir /s /q c:\\"]
    cmd_lower = command.lower()
    for bad in forbidden:
        if bad in cmd_lower:
            log_action("🛑", f"COMMAND BLOCKED: {command}", "Dangerous system operation prevented", "BLOCKED")
            return "Command was blocked for safety because it would wipe core system directories."
    
    try:
        def _execute():
            return subprocess.run(
                ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", command],
                capture_output=True,
                text=True,
                timeout=15,
            )

        res = await asyncio.to_thread(_execute)
        stdout = res.stdout.strip()
        stderr = res.stderr.strip()
        
        if res.returncode == 0:
            output_snippet = stdout[:400] if stdout else "Command completed successfully with no output."
            log_action("💻", f"COMMAND FINISHED: {command}", f"Output:\n{output_snippet}", "SUCCESS")
            return f"Command executed successfully: {output_snippet}"
        else:
            error_snippet = stderr[:300] if stderr else f"Exit code {res.returncode}"
            log_action("⚠️", f"COMMAND FAILED: {command}", f"Error:\n{error_snippet}", "FAILED")
            return f"Command completed with error: {error_snippet}"
    except subprocess.TimeoutExpired:
        log_action("⏰", f"COMMAND TIMEOUT: {command}", "Exceeded 15s limit", "TIMEOUT")
        return "Command timed out after 15 seconds."
    except Exception as e:
        log_action("❌", f"COMMAND ERROR: {command}", str(e), "EXCEPTION")
        return f"Failed to run command: {e}"

# All tools exported
LAPTOP_CONTROL_TOOLS = [
    open_application,
    close_application,
    open_website,
    search_web,
    write_note,
    volume_control,
    media_control,
    take_screenshot,
    get_system_status,
    lock_laptop,
    run_terminal_command,
]
