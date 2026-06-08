"""
PC Optimizer - Single Python App

Features converted from the original batch files:
1. Delete Temp Files
2. Network Reset Utility
3. System Health Check
4. Task Slayer
5. Run All Tasks

Build command:
    py -m PyInstaller --onefile --windowed --name "PC Optimizer" --icon app_icon.ico --add-data "app_icon.ico;." pc_optimizer_app.py
"""

from __future__ import annotations

import ctypes
import os
import queue
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path
from typing import Callable, Iterable

import tkinter as tk
from tkinter import messagebox
from tkinter import scrolledtext


APP_NAME = "PC Optimizer"
APP_VERSION = "2"
WINDOW_WIDTH = 1040
WINDOW_HEIGHT = 780


# -----------------------------
# Windows/admin helpers
# -----------------------------


def is_windows() -> bool:
    return os.name == "nt"


def is_admin() -> bool:
    if not is_windows():
        return False
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def quote_arg(value: str) -> str:
    if not value:
        return '""'
    if any(ch in value for ch in ' \t"'):
        return '"' + value.replace('"', '\\"') + '"'
    return value


def relaunch_as_admin() -> bool:
    """Relaunch the current app with elevated privileges."""
    if not is_windows():
        return False

    try:
        if getattr(sys, "frozen", False):
            executable = sys.executable
            params = subprocess.list2cmdline(sys.argv[1:])
        else:
            executable = sys.executable
            script = str(Path(__file__).resolve())
            params = subprocess.list2cmdline([script, *sys.argv[1:]])

        result = ctypes.windll.shell32.ShellExecuteW(None, "runas", executable, params, None, 1)
        return int(result) > 32
    except Exception:
        return False


def resource_path(relative_path: str) -> Path:
    base_path = getattr(sys, "_MEIPASS", None)
    if base_path:
        return Path(base_path) / relative_path
    return Path(__file__).resolve().parent / relative_path


def command_exists(command: str) -> bool:
    if shutil.which(command):
        return True
    if not is_windows():
        return False

    system_root = Path(os.environ.get("SystemRoot", r"C:\Windows"))
    candidates = [
        system_root / "System32" / command,
        system_root / "System32" / f"{command}.exe",
        system_root / "Sysnative" / command,
        system_root / "Sysnative" / f"{command}.exe",
        system_root / "System32" / "WindowsPowerShell" / "v1.0" / command,
        system_root / "System32" / "WindowsPowerShell" / "v1.0" / f"{command}.exe",
    ]
    return any(path.exists() for path in candidates)


def create_no_window_flag() -> int:
    if is_windows():
        return getattr(subprocess, "CREATE_NO_WINDOW", 0)
    return 0


# -----------------------------
# Optimizer command data
# -----------------------------

TASK_SLAYER_GROUPS: dict[str, list[str]] = {
    "Browsers": [
        "chrome.exe", "msedge.exe", "brave.exe", "firefox.exe", "opera.exe", "opera_gx.exe",
        "vivaldi.exe", "browser.exe", "Arc.exe", "MicrosoftEdgeUpdate.exe",
    ],
    "Gaming and Steam": [
        "steam.exe", "steamwebhelper.exe", "steamservice.exe", "steam_bootstrapper.exe",
        "steamvr.exe", "Steam Desktop Authenticator.exe",
    ],
    "Xbox and Gaming Services": [
        "XboxPcTray.exe", "XboxPcAppFT.exe", "Xbox.exe", "gamingservicesnet.exe", "gamingservices.exe",
    ],
    "File Sharing and Cloud Services": [
        "shareit.exe", "shareitservice.exe", "googledrivesync.exe", "GoogleDriveFS.exe",
        "OneDrive.exe", "Dropbox.exe", "MEGAsync.exe", "iCloudDrive.exe", "iCloudPhotos.exe",
    ],
    "Communication and Meeting Apps": [
        "discord.exe", "WhatsApp.exe", "Telegram.exe", "Signal.exe", "Skype.exe",
        "Teams.exe", "ms-teams.exe", "Zoom.exe", "slack.exe",
    ],
    "Cloudflare WARP": [
        "warp.exe", "warp-svc.exe", "cloudflare-warp.exe", "CloudflareWARP.exe", "WARPClient.exe",
    ],
    "WeMod": ["WeMod.exe", "WeModHelper.exe", "WeModAuxiliaryService.exe"],
    "CurseForge and Overwolf": ["CurseForge.exe", "Curse.Agent.Host.exe", "Overwolf.exe"],
    "TcNo Account Switcher": ["TcNo-Acc-Switcher-Tray_main.exe", "TcNo-Acc-Switcher_main.exe"],
    "Spotify": ["Spotify.exe", "SpotifyWebHelper.exe"],
    "System Utilities": [
        "AvroKeyboard.exe", "AvroSetup.exe", "Avro.exe", "CCleaner64.exe", "CCleaner.exe",
        "CCleanerSmartClean.exe", "CCXProcess.exe", "CCleanerPerformanceOptimizerService.exe",
        "AdobeIPCBroker.exe", "crashpad_handler.exe", "BraveCrashHandler64.exe",
        "BraveCrashHandler.exe", "BraveUpdate.exe", "Taskmgr.exe",
    ],
    "Torrent and Download Managers": ["qbittorrent.exe", "IDMan.exe"],
    "Background Services": [
        "wallpaper32.exe", "winrtutil32.exe", "wmpnetwk.exe", "NewsAndInterests.exe", "node.exe", "SearchApp.exe",
    ],
    "CSE Student Tools": [
        "Code.exe", "Cursor.exe", "Windsurf.exe", "VSCodium.exe", "GitHubDesktop.exe",
        "pycharm64.exe", "pycharm.exe", "idea64.exe", "idea.exe", "webstorm64.exe", "webstorm.exe",
        "studio64.exe", "adb.exe", "emulator.exe", "qemu-system-x86_64.exe",
        "Docker Desktop.exe", "Docker Desktop Backend.exe", "com.docker.backend.exe", "com.docker.service.exe",
        "postman.exe", "Insomnia.exe", "xampp-control.exe", "httpd.exe", "mysqld.exe",
        "python.exe", "pythonw.exe", "java.exe", "javaw.exe", "dotnet.exe", "node.exe",
    ],
    "BBA and Office Student Tools": [
        "WINWORD.EXE", "EXCEL.EXE", "POWERPNT.EXE", "MSACCESS.EXE", "OUTLOOK.EXE",
        "ONENOTE.EXE", "Acrobat.exe", "FoxitPDFReader.exe", "WPSOffice.exe", "wps.exe",
        "Notion.exe", "Obsidian.exe", "Mendeley Desktop.exe", "Zotero.exe",
    ],
    "EEE and Engineering Student Tools": [
        "MATLAB.exe", "ltspice.exe", "scad3.exe", "multisim.exe", "Ultiboard.exe",
        "ISIS.EXE", "ARES.EXE", "Proteus.exe", "kicad.exe", "eeschema.exe", "pcbnew.exe",
        "eagle.exe", "Fusion360.exe", "acad.exe", "SLDWORKS.exe", "CodeBlocks.exe",
    ],
    "Network and Remote Tools": ["DnsJumper.exe", "AnyDesk.exe", "TeamViewer.exe", "RustDesk.exe"],
    "Phone Link": ["PhoneLink.exe", "PhoneExperienceHost.exe", "YourPhone.exe", "YourPhoneApp.exe"],
    "Adobe and Related Services": [
        "AdobeCollabSync.exe", "acrotray.exe", "armsvc.exe", "AGMService.exe",
        "Photoshop.exe", "Illustrator.exe", "AfterFX.exe", "Premiere Pro.exe", "Lightroom.exe",
        "Adobe Desktop Service.exe", "Creative Cloud.exe", "CoreSync.exe",
    ],
    "Canva and Figma": ["Canva.exe", "Figma.exe", "figma_agent.exe"],
    "CCleaner Performance Optimizer": ["CCleanerPerformanceOptimizerService.exe"],
}

FEATURE_COMMANDS: dict[str, list[str]] = {
    "Clean Temporary Files": [],
    "Reset Internet Connection": ["ipconfig", "netsh", "powershell"],
    "Repair Windows System": ["DISM", "SFC", "chkdsk"],
    "Close Background Apps": ["taskkill"],
}


# -----------------------------
# UI widgets
# -----------------------------


def clamp(value: int) -> int:
    return max(0, min(255, value))


def adjust_hex_color(hex_color: str, amount: int) -> str:
    hex_color = hex_color.strip("#")
    r = clamp(int(hex_color[0:2], 16) + amount)
    g = clamp(int(hex_color[2:4], 16) + amount)
    b = clamp(int(hex_color[4:6], 16) + amount)
    return f"#{r:02x}{g:02x}{b:02x}"


class ThreeDButton(tk.Canvas):
    """Canvas based raised button with shadow, hover, click depth, and safe text spacing."""

    def __init__(
        self,
        master: tk.Widget,
        title: str,
        subtitle: str,
        command: Callable[[], None],
        width: int = 300,
        height: int = 96,
        color: str = "#2f80ed",
        accent: str = "C",
        text_color: str = "#ffffff",
        **kwargs,
    ) -> None:
        super().__init__(
            master,
            width=width,
            height=height,
            bg=kwargs.pop("bg", "#0b1220"),
            highlightthickness=0,
            bd=0,
            cursor="hand2",
            **kwargs,
        )
        self.title = title
        self.subtitle = subtitle
        self.command = command
        self.width_value = width
        self.height_value = height
        self.color = color
        self.accent = accent
        self.text_color = text_color
        self.hovered = False
        self.pressed = False
        self.enabled = True
        self.draw()
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<ButtonPress-1>", self.on_press)
        self.bind("<ButtonRelease-1>", self.on_release)

    def rounded_rect(self, x1: int, y1: int, x2: int, y2: int, r: int, **kwargs) -> None:
        points = [
            x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r,
            x2, y2 - r, x2, y2, x2 - r, y2, x1 + r, y2,
            x1, y2, x1, y2 - r, x1, y1 + r, x1, y1,
        ]
        self.create_polygon(points, smooth=True, **kwargs)

    def draw(self) -> None:
        self.delete("all")
        offset = 8 if not self.pressed else 3
        body_y = 6 if not self.pressed else 11
        base = self.color
        if not self.enabled:
            base = "#64748b"
        elif self.hovered:
            base = adjust_hex_color(base, 16)

        dark = adjust_hex_color(base, -58)
        light = adjust_hex_color(base, 30)
        shadow = "#020617"
        w = self.width_value
        h = self.height_value

        # Raised 3D base and shadow.
        self.rounded_rect(10, 14 + offset, w - 8, h - 4 + offset, 16, fill=shadow, outline="")
        self.rounded_rect(8, body_y + 6, w - 10, h - 15, 16, fill=dark, outline="")
        self.rounded_rect(8, body_y, w - 10, h - 22, 16, fill=base, outline=light, width=2)

        # Small left badge gives each action a clear visual anchor without using emoji fonts.
        self.create_oval(24, body_y + 20, 54, body_y + 50, fill="#ffffff", outline="")
        self.create_text(
            39,
            body_y + 35,
            text=self.accent,
            anchor="center",
            font=("Segoe UI", 11, "bold"),
            fill=base,
        )

        self.create_text(
            66,
            body_y + 25,
            text=self.title,
            anchor="w",
            font=("Segoe UI", 12, "bold"),
            fill=self.text_color,
        )
        self.create_text(
            66,
            body_y + 53,
            text=self.subtitle,
            anchor="w",
            font=("Segoe UI", 9),
            fill="#edf6ff",
            width=w - 86,
        )

    def on_enter(self, _event: tk.Event) -> None:
        if not self.enabled:
            return
        self.hovered = True
        self.draw()

    def on_leave(self, _event: tk.Event) -> None:
        if not self.enabled:
            return
        self.hovered = False
        self.pressed = False
        self.draw()

    def on_press(self, _event: tk.Event) -> None:
        if not self.enabled:
            return
        self.pressed = True
        self.draw()

    def on_release(self, event: tk.Event) -> None:
        if not self.enabled:
            return
        inside = 0 <= event.x <= self.width_value and 0 <= event.y <= self.height_value
        self.pressed = False
        self.draw()
        if inside:
            self.command()

    def set_enabled(self, enabled: bool) -> None:
        self.enabled = enabled
        self.config(cursor="hand2" if enabled else "arrow")
        self.draw()


# -----------------------------
# Main app
# -----------------------------


class PCOptimizerApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.log_queue: queue.Queue[str] = queue.Queue()
        self.worker: threading.Thread | None = None
        self.buttons: list[ThreeDButton] = []

        self.root.title(f"{APP_NAME} v{APP_VERSION}")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.minsize(980, 720)
        self.root.configure(bg="#0b1220")

        icon_file = resource_path("app_icon.ico")
        if icon_file.exists() and is_windows():
            try:
                self.root.iconbitmap(str(icon_file))
            except Exception:
                pass

        self.build_ui()
        self.root.after(80, self.process_log_queue)
        self.write_startup_status()

    def build_ui(self) -> None:
        shell = tk.Frame(self.root, bg="#0b1220")
        shell.pack(fill="both", expand=True, padx=26, pady=20)

        header = tk.Frame(shell, bg="#0b1220")
        header.pack(fill="x")

        title_area = tk.Frame(header, bg="#0b1220")
        title_area.pack(side="left", fill="x", expand=True)

        tk.Label(
            title_area,
            text="PC Optimizer",
            bg="#0b1220",
            fg="#f8fafc",
            font=("Segoe UI", 26, "bold"),
        ).pack(anchor="w")

        tk.Label(
            title_area,
            text="A simple control panel for your PC cleanup, repair, network reset, and app closing tools.",
            bg="#0b1220",
            fg="#9fb3d1",
            font=("Segoe UI", 10),
        ).pack(anchor="w", pady=(2, 0))

        action_area = tk.Frame(header, bg="#0b1220")
        action_area.pack(side="right", anchor="ne")

        self.admin_button = tk.Button(
            action_area,
            text="Open as Administrator",
            command=self.request_admin,
            bg="#f97316",
            fg="#ffffff",
            activebackground="#fb923c",
            activeforeground="#ffffff",
            relief="raised",
            bd=4,
            font=("Segoe UI", 10, "bold"),
            padx=12,
            pady=6,
        )
        self.admin_button.pack(side="left", padx=(0, 10))
        if is_admin():
            self.admin_button.configure(state="disabled", text="Administrator Active")

        self.admin_badge = tk.Label(
            action_area,
            text="ADMIN MODE" if is_admin() else "STANDARD MODE",
            bg="#14532d" if is_admin() else "#92400e",
            fg="#ffffff",
            font=("Segoe UI", 10, "bold"),
            padx=13,
            pady=9,
        )
        self.admin_badge.pack(side="left")

        button_area = tk.Frame(shell, bg="#0b1220")
        button_area.pack(fill="x", pady=(18, 0))

        specs = [
            ("Clean Temporary Files", "Remove Windows cache and temp files", "#16a34a", "C", self.run_delete_temp),
            ("Reset Internet Connection", "Flush DNS and reset network settings", "#2563eb", "N", self.run_network_reset),
            ("Repair Windows System", "Run DISM, SFC, and disk check", "#7c3aed", "R", self.run_health_check),
            ("Close Background Apps", "Stop common study and background apps", "#dc2626", "A", self.run_task_slayer),
            ("Check Requirements", "Verify Windows, admin, and tools", "#0891b2", "V", self.run_validation),
            ("Run Full Optimization", "Run every maintenance step in order", "#ea580c", "F", self.run_all_tasks),
        ]

        for index, (title, subtitle, color, accent, command) in enumerate(specs):
            btn = ThreeDButton(
                button_area,
                title,
                subtitle,
                command,
                width=300,
                height=96,
                color=color,
                accent=accent,
                bg="#0b1220",
            )
            row, col = divmod(index, 3)
            btn.grid(row=row, column=col, padx=9, pady=9, sticky="nsew")
            self.buttons.append(btn)

        for col in range(3):
            button_area.grid_columnconfigure(col, weight=1)

        log_header = tk.Frame(shell, bg="#0b1220")
        log_header.pack(fill="x", pady=(20, 7))
        tk.Label(
            log_header,
            text="Activity Log",
            bg="#0b1220",
            fg="#f8fafc",
            font=("Segoe UI", 14, "bold"),
        ).pack(side="left")
        tk.Button(
            log_header,
            text="Clear Log",
            command=lambda: self.log_box.delete("1.0", "end"),
            bg="#1f2937",
            fg="#e5e7eb",
            activebackground="#374151",
            activeforeground="#ffffff",
            relief="raised",
            bd=3,
            font=("Segoe UI", 9, "bold"),
            padx=8,
            pady=2,
        ).pack(side="right")

        self.log_box = scrolledtext.ScrolledText(
            shell,
            height=17,
            bg="#020617",
            fg="#d1fae5",
            insertbackground="#ffffff",
            font=("Consolas", 10),
            relief="flat",
            bd=0,
            padx=10,
            pady=10,
            wrap="word",
        )
        self.log_box.pack(fill="both", expand=True)

        self.status_var = tk.StringVar(value="Ready")
        status = tk.Label(
            shell,
            textvariable=self.status_var,
            bg="#0b1220",
            fg="#94a3b8",
            font=("Segoe UI", 9),
            anchor="w",
        )
        status.pack(fill="x", pady=(8, 0))

    def write_startup_status(self) -> None:
        self.log(f"{APP_NAME} v{APP_VERSION} is ready.")
        if not is_windows():
            self.log("This app is designed for Windows. Open it on Windows to run the optimizer tools.")
            return
        if is_admin():
            self.log("Mode: Administrator. All optimizer actions are available.")
        else:
            self.log("Mode: Standard. Click 'Open as Administrator' before running optimizer actions.")

    def log(self, message: str) -> None:
        timestamp = time.strftime("%H:%M:%S")
        self.log_queue.put(f"[{timestamp}] {message}\n")

    def process_log_queue(self) -> None:
        try:
            while True:
                message = self.log_queue.get_nowait()
                self.log_box.insert("end", message)
                self.log_box.see("end")
        except queue.Empty:
            pass
        self.root.after(80, self.process_log_queue)

    def set_busy(self, busy: bool, status: str = "Ready") -> None:
        for button in self.buttons:
            button.set_enabled(not busy)
        self.status_var.set(status)
        if busy:
            self.admin_button.configure(state="disabled")
        else:
            self.admin_button.configure(state="disabled" if is_admin() else "normal")

    def request_admin(self) -> None:
        if not is_windows():
            messagebox.showerror("Windows required", "Administrator relaunch is only available on Windows.")
            return
        if relaunch_as_admin():
            self.root.destroy()
        else:
            messagebox.showerror("Could not open as Administrator", "Windows did not start the app as Administrator.")

    def require_ready(self, feature_name: str, commands: Iterable[str] | None = None) -> bool:
        if not is_windows():
            messagebox.showerror("Windows required", f"{feature_name} uses Windows maintenance commands.")
            return False
        if not is_admin():
            answer = messagebox.askyesno(
                "Administrator required",
                f"{feature_name} needs Administrator permission. Open the app as Administrator now?",
            )
            if answer:
                self.request_admin()
            return False
        missing = [cmd for cmd in (commands or []) if not command_exists(cmd)]
        if missing:
            messagebox.showerror(
                "Validation failed",
                "These required Windows tools were not found: " + ", ".join(missing),
            )
            return False
        return True

    def start_worker(self, title: str, target: Callable[[], None]) -> None:
        if self.worker and self.worker.is_alive():
            messagebox.showwarning("Please wait", "Another task is already running.")
            return

        def wrapper() -> None:
            self.set_busy_threadsafe(True, f"Running: {title}")
            self.log("=" * 72)
            self.log(f"START: {title}")
            try:
                target()
                self.log(f"DONE: {title}")
            except Exception as exc:
                self.log(f"ERROR: {exc}")
                self.root.after(0, lambda: messagebox.showerror("Task failed", str(exc)))
            finally:
                self.log("=" * 72)
                self.set_busy_threadsafe(False, "Ready")

        self.worker = threading.Thread(target=wrapper, daemon=True)
        self.worker.start()

    def set_busy_threadsafe(self, busy: bool, status: str) -> None:
        self.root.after(0, lambda: self.set_busy(busy, status))

    def run_subprocess(self, cmd: list[str], input_text: str | None = None, timeout: int | None = None) -> int:
        display = " ".join(quote_arg(part) for part in cmd)
        self.log(f"> {display}")
        try:
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE if input_text is not None else None,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                creationflags=create_no_window_flag(),
            )
            if input_text is not None and process.stdin:
                try:
                    process.stdin.write(input_text)
                    process.stdin.flush()
                    process.stdin.close()
                except Exception:
                    pass
            start = time.time()
            assert process.stdout is not None
            while True:
                line = process.stdout.readline()
                if line:
                    self.log(line.rstrip())
                elif process.poll() is not None:
                    break
                elif timeout and (time.time() - start) > timeout:
                    process.kill()
                    self.log("Command timed out and was stopped.")
                    return -1
            return process.wait()
        except FileNotFoundError:
            self.log(f"Command not found: {cmd[0]}")
            return 127

    def confirm(self, title: str, message: str) -> bool:
        result: list[bool] = []
        event = threading.Event()

        def ask() -> None:
            result.append(messagebox.askyesno(title, message))
            event.set()

        self.root.after(0, ask)
        event.wait()
        return bool(result and result[0])

    # -----------------------------
    # Feature actions
    # -----------------------------

    def run_validation(self) -> None:
        self.start_worker("Check Requirements", self.validation_action)

    def validation_action(self) -> None:
        self.log("Checking requirements...")
        self.log(f"Windows detected: {'Yes' if is_windows() else 'No'}")
        self.log(f"Administrator mode: {'Yes' if is_admin() else 'No'}")
        for feature, commands in FEATURE_COMMANDS.items():
            if not commands:
                self.log(f"{feature}: no external command required")
                continue
            missing = [cmd for cmd in commands if not command_exists(cmd)]
            if missing:
                self.log(f"{feature}: missing {', '.join(missing)}")
            else:
                self.log(f"{feature}: ready")

        if is_windows():
            paths = self.temp_paths()
            self.log("Cleanup folders that will be checked:")
            for path in paths:
                status = "found" if path.exists() else "not found"
                self.log(f" - {path} ({status})")
        self.log("Requirement check finished.")

    def run_delete_temp(self) -> None:
        if not self.require_ready("Clean Temporary Files", FEATURE_COMMANDS["Clean Temporary Files"]):
            return
        if not messagebox.askyesno(
            "Confirm cleanup",
            "This will remove files inside Windows Temp, Prefetch, and user Temp folders. Files currently used by Windows will be skipped. Continue?",
        ):
            return
        self.start_worker("Clean Temporary Files", self.delete_temp_action)

    def temp_paths(self) -> list[Path]:
        system_root = Path(os.environ.get("SystemRoot", r"C:\Windows"))
        paths = [
            system_root / "Temp",
            system_root / "Prefetch",
            Path(tempfile.gettempdir()),
        ]
        users_root = Path(os.environ.get("SystemDrive", "C:")) / "Users"
        if users_root.exists():
            for user_dir in users_root.iterdir():
                temp_dir = user_dir / "AppData" / "Local" / "Temp"
                if temp_dir.exists():
                    paths.append(temp_dir)
        unique: list[Path] = []
        seen: set[str] = set()
        for path in paths:
            key = str(path).lower()
            if key not in seen:
                unique.append(path)
                seen.add(key)
        return unique

    def safe_clean_folder(self, folder: Path) -> tuple[int, int, int]:
        folder = folder.resolve()
        if not folder.exists() or not folder.is_dir():
            self.log(f"Skipped missing folder: {folder}")
            return 0, 0, 0

        allowed_names = {"temp", "prefetch"}
        if folder.name.lower() not in allowed_names:
            self.log(f"Safety skip: {folder} is not a recognized temp folder.")
            return 0, 0, 1

        files_removed = 0
        dirs_removed = 0
        failed = 0
        self.log(f"Cleaning: {folder}")
        for item in list(folder.iterdir()):
            try:
                if item.is_dir() and not item.is_symlink():
                    shutil.rmtree(item, ignore_errors=False)
                    dirs_removed += 1
                else:
                    item.unlink(missing_ok=True)
                    files_removed += 1
            except Exception as exc:
                failed += 1
                self.log(f"Could not remove {item}: {exc}")
        return files_removed, dirs_removed, failed

    def delete_temp_action(self) -> None:
        total_files = 0
        total_dirs = 0
        total_failed = 0
        for folder in self.temp_paths():
            files_removed, dirs_removed, failed = self.safe_clean_folder(folder)
            total_files += files_removed
            total_dirs += dirs_removed
            total_failed += failed
        self.log(f"Cleanup summary: files removed={total_files}, folders removed={total_dirs}, skipped/failed={total_failed}")

    def run_network_reset(self) -> None:
        if not self.require_ready("Reset Internet Connection", FEATURE_COMMANDS["Reset Internet Connection"]):
            return
        if not messagebox.askyesno(
            "Confirm network reset",
            "This may temporarily disconnect your internet while DNS, IP, Winsock, TCP/IP, and network adapters are reset. Continue?",
        ):
            return
        self.start_worker("Reset Internet Connection", self.network_reset_action)

    def network_reset_action(self) -> None:
        self.log("Flushing DNS cache...")
        for _ in range(20):
            self.run_subprocess(["ipconfig", "/flushdns"])
        self.run_subprocess(["ipconfig", "/release"])
        self.run_subprocess(["ipconfig", "/renew"])
        self.run_subprocess(["netsh", "winsock", "reset"])
        self.run_subprocess(["netsh", "int", "ip", "reset"])

        ps_script = (
            "$adapters = Get-NetAdapter | Where-Object {$_.Status -eq 'Up' -and $_.HardwareInterface -eq $true}; "
            "foreach ($a in $adapters) { "
            "Write-Output ('Restarting adapter: ' + $a.Name); "
            "Disable-NetAdapter -Name $a.Name -Confirm:$false -ErrorAction Continue; "
            "Start-Sleep -Seconds 3; "
            "Enable-NetAdapter -Name $a.Name -Confirm:$false -ErrorAction Continue "
            "}"
        )
        self.run_subprocess(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_script])
        self.run_subprocess(["ipconfig", "/all"])
        self.log("Network reset completed. Restart the PC if internet issues continue.")

    def run_health_check(self) -> None:
        if not self.require_ready("Repair Windows System", FEATURE_COMMANDS["Repair Windows System"]):
            return
        if not messagebox.askyesno(
            "Confirm Windows repair",
            "This runs DISM, SFC, and CHKDSK. It can take a long time, and CHKDSK may run after the next restart. Continue?",
        ):
            return
        self.start_worker("Repair Windows System", self.health_check_action)

    def health_check_action(self) -> None:
        self.run_subprocess(["DISM", "/Online", "/Cleanup-Image", "/ScanHealth"])
        self.run_subprocess(["DISM", "/Online", "/Cleanup-Image", "/CheckHealth"])
        self.run_subprocess(["DISM", "/Online", "/Cleanup-Image", "/RestoreHealth"])
        self.run_subprocess(["SFC", "/SCANNOW"])
        self.run_subprocess(["chkdsk", "C:", "/F", "/R"], input_text="Y\n")
        self.log("Windows repair finished. Restart Windows if CHKDSK was scheduled.")

    def run_task_slayer(self) -> None:
        if not self.require_ready("Close Background Apps", FEATURE_COMMANDS["Close Background Apps"]):
            return
        if not messagebox.askyesno(
            "Confirm app closing",
            "This can close browsers, chat apps, coding tools, office apps, engineering apps, and other background programs. Save your work first. Continue?",
        ):
            return
        self.start_worker("Close Background Apps", self.task_slayer_action)

    def task_slayer_action(self) -> None:
        killed = 0
        not_running_or_failed = 0
        for group, processes in TASK_SLAYER_GROUPS.items():
            self.log(f"-- {group} --")
            for process_name in processes:
                code = self.run_subprocess(["taskkill", "/F", "/IM", process_name])
                if code == 0:
                    killed += 1
                else:
                    not_running_or_failed += 1
        self.log(f"App closing summary: closed/matched={killed}, not running or failed={not_running_or_failed}")

    def run_all_tasks(self) -> None:
        all_commands = [cmd for commands in FEATURE_COMMANDS.values() for cmd in commands]
        if not self.require_ready("Run Full Optimization", all_commands):
            return
        if not messagebox.askyesno(
            "Confirm full optimization",
            "This will run cleanup, network reset, Windows repair, and app closing in order. It may disconnect internet, close apps, and schedule CHKDSK on restart. Continue?",
        ):
            return
        self.start_worker("Run Full Optimization", self.run_all_action)

    def run_all_action(self) -> None:
        self.log("Running full sequence: Cleanup -> Network Reset -> Windows Repair -> Close Apps")
        self.delete_temp_action()
        self.network_reset_action()
        self.health_check_action()
        self.task_slayer_action()
        self.log("Full optimization completed.")


def main() -> None:
    root = tk.Tk()
    PCOptimizerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
