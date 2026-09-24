"""Windows maintenance and app discovery for PC Optimizer."""
from __future__ import annotations

import ctypes
from dataclasses import dataclass
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
from typing import Callable

import psutil

Log = Callable[[str], None]
WINDOWS_PROCESSES = {
    "system", "registry", "smss.exe", "csrss.exe", "wininit.exe", "winlogon.exe",
    "services.exe", "lsass.exe", "svchost.exe", "dwm.exe", "sihost.exe",
    "explorer.exe", "taskmgr.exe", "searchhost.exe", "searchapp.exe",
    "startmenuexperiencehost.exe", "shellexperiencehost.exe", "runtimebroker.exe",
    "fontdrvhost.exe", "audiodg.exe", "spoolsv.exe", "conhost.exe",
    "pc optimizer v3.0.0.exe", "python.exe", "pythonw.exe",
    "defendersessionhelper.exe", "msmpeng.exe", "nissrv.exe",
}
WINDOWS_HOSTS = {
    "searchhost.exe", "searchapp.exe", "startmenuexperiencehost.exe",
    "shellexperiencehost.exe", "applicationframehost.exe", "services.exe", "svchost.exe",
}


def is_admin() -> bool:
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def elevate() -> bool:
    import sys
    executable = sys.executable
    args = sys.argv[1:] if getattr(sys, "frozen", False) else [str(Path(__file__).with_name("pc_optimizer_app.py")), *sys.argv[1:]]
    return ctypes.windll.shell32.ShellExecuteW(None, "runas", executable, subprocess.list2cmdline(args), None, 1) > 32


def _image_path(pid: int) -> str | None:
    kernel = ctypes.windll.kernel32
    kernel.OpenProcess.argtypes = [ctypes.c_ulong, ctypes.c_int, ctypes.c_ulong]
    kernel.OpenProcess.restype = ctypes.c_void_p
    kernel.QueryFullProcessImageNameW.argtypes = [ctypes.c_void_p, ctypes.c_ulong, ctypes.c_wchar_p, ctypes.POINTER(ctypes.c_ulong)]
    kernel.QueryFullProcessImageNameW.restype = ctypes.c_int
    kernel.CloseHandle.argtypes = [ctypes.c_void_p]
    handle = kernel.OpenProcess(0x1000, False, pid)
    if not handle:
        return None
    try:
        buffer = ctypes.create_unicode_buffer(32768)
        size = ctypes.c_ulong(len(buffer))
        return buffer.value if kernel.QueryFullProcessImageNameW(handle, 0, buffer, ctypes.byref(size)) else None
    finally:
        kernel.CloseHandle(handle)


def _session_id(pid: int) -> int | None:
    kernel = ctypes.windll.kernel32
    kernel.ProcessIdToSessionId.argtypes = [ctypes.c_ulong, ctypes.POINTER(ctypes.c_ulong)]
    kernel.ProcessIdToSessionId.restype = ctypes.c_int
    session = ctypes.c_ulong()
    return session.value if kernel.ProcessIdToSessionId(pid, ctypes.byref(session)) else None


def running_apps() -> list[tuple[str, int, str]]:
    """List desktop apps, excluding service and Windows-hosted helpers."""
    windows = os.environ.get("SystemRoot", r"C:\Windows").lower().rstrip("\\") + "\\"
    current_session = _session_id(os.getpid())
    processes = {proc.pid: proc.info for proc in psutil.process_iter(
        ["pid", "name", "exe", "ppid"], ad_value=None)}
    try:
        service_pids = {service.pid() for service in psutil.win_service_iter() if service.pid()}
    except (OSError, AttributeError):
        service_pids = set()

    def managed_helper(pid: int) -> bool:
        seen: set[int] = set()
        parent = processes.get(pid, {}).get("ppid")
        while parent and parent not in seen:
            seen.add(parent)
            info = processes.get(parent)
            if not info:
                break
            name = (info.get("name") or "").lower()
            if parent in service_pids or name in WINDOWS_HOSTS:
                return True
            if name == "explorer.exe":
                break
            if current_session is not None and _session_id(parent) != current_session:
                return True
            parent = info.get("ppid")
        return False

    apps: list[tuple[str, int, str]] = []
    for pid, info in processes.items():
        name = (info.get("name") or "").strip()
        if pid == os.getpid() or name.lower() in WINDOWS_PROCESSES or not name.lower().endswith(".exe"):
            continue
        if current_session is not None and _session_id(pid) != current_session:
            continue
        path = info.get("exe")
        if (path and not path.lower().startswith(windows)
                and "\\microsoft\\windows defender\\" not in path.lower()
                and not managed_helper(pid)):
            apps.append((name, pid, path))
    return sorted(apps, key=lambda item: (item[0].lower(), item[1]))


def temp_folders() -> list[Path]:
    paths = [Path(os.environ.get("SystemRoot", r"C:\Windows")) / "Temp", Path(tempfile.gettempdir())]
    return list(dict.fromkeys(path.resolve() for path in paths if path.exists()))


def clean_temp(log: Log) -> tuple[int, int]:
    removed = failed = 0
    for folder in temp_folders():
        if folder.name.lower() != "temp":
            continue
        log(f"Cleaning {folder}")
        for item in folder.iterdir():
            try:
                if item.is_dir() and not item.is_symlink():
                    shutil.rmtree(item)
                else:
                    item.unlink()
                removed += 1
            except OSError:
                failed += 1
    log(f"Cleanup complete: {removed} items removed, {failed} locked or unavailable.")
    return removed, failed


def run_command(args: list[str], log: Log, *, allow_partial_ip_reset: bool = False) -> bool:
    log("Running: " + subprocess.list2cmdline(args))
    flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    executable = args[0]
    if executable.lower() in {"ipconfig", "netsh", "dism", "sfc", "taskkill"}:
        candidate = Path(os.environ.get("SystemRoot", r"C:\Windows")) / "System32" / f"{executable}.exe"
        if candidate.exists():
            args = [str(candidate), *args[1:]]
    process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                               text=True, errors="replace", creationflags=flags)
    assert process.stdout is not None
    output: list[str] = []
    for line in process.stdout:
        clean = line.rstrip()
        output.append(clean)
        log(clean)
    code = process.wait()
    if code:
        combined = "\n".join(output).lower()
        denied = combined.count("access is denied")
        failed = combined.count("failed.")
        if allow_partial_ip_reset and denied > 0 and failed == denied and "ok!" in combined and "error" not in combined:
            log("Warning: most TCP/IP settings reset, but Windows denied one protected setting. Restart Windows to apply completed changes.")
            return False
        raise RuntimeError(f"{executable} exited with code {code}. See command output above.")
    return True


def reset_network(log: Log) -> bool:
    run_command(["ipconfig", "/flushdns"], log)
    run_command(["netsh", "winsock", "reset"], log)
    complete = run_command(["netsh", "int", "ip", "reset"], log, allow_partial_ip_reset=True)
    log("Network reset complete. Restart Windows to apply all changes." if complete
        else "Network reset partially complete. Restart Windows; one protected TCP/IP setting was denied.")
    return complete


def refresh_network(log: Log) -> bool:
    """Refresh DNS and DHCP without changing the Winsock/TCP stack."""
    run_command(["ipconfig", "/flushdns"], log)
    try:
        run_command(["ipconfig", "/renew"], log)
    except RuntimeError:
        log("DNS cache cleared, but DHCP renewal was unavailable or failed. Check the adapter details above; static IP adapters do not renew via DHCP.")
        return False
    log("DNS and DHCP refreshed. No restart is required for this action.")
    return True


def repair_windows(log: Log) -> None:
    run_command(["DISM", "/Online", "/Cleanup-Image", "/RestoreHealth"], log)
    run_command(["SFC", "/SCANNOW"], log)
    log("System repair complete.")


@dataclass(frozen=True)
class CloseResult:
    closed: int
    already_stopped: int
    failed: int
    still_running: tuple[str, ...]


def close_selected(processes: list[tuple[str, int, str]], log: Log) -> CloseResult:
    """Close selected process instances, never a reused PID or an app that vanished."""
    closed = stopped = failed = 0
    seen: set[int] = set()
    taskkill = Path(os.environ.get("SystemRoot", r"C:\Windows")) / "System32" / "taskkill.exe"
    executable = str(taskkill) if taskkill.exists() else "taskkill"
    for name, pid, expected_path in processes:
        if pid in seen:
            continue
        seen.add(pid)
        current_path = _image_path(pid)
        if current_path is None:
            stopped += 1
            log(f"Already stopped: {name} (PID {pid})")
            continue
        if current_path.casefold() != expected_path.casefold():
            stopped += 1
            log(f"Skipped reused PID {pid}; selected process is no longer running.")
            continue
        try:
            result = subprocess.run([executable, "/F", "/PID", str(pid)], capture_output=True,
                                    text=True, errors="replace", check=False,
                                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        except OSError as exc:
            failed += 1
            log(f"Could not close {name} (PID {pid}): {exc}")
            continue
        if result.returncode == 0:
            closed += 1
            log(f"Closed: {name} (PID {pid})")
        elif _image_path(pid) != expected_path:
            stopped += 1
            log(f"Already stopped: {name} (PID {pid})")
        else:
            failed += 1
            reason = (result.stderr or result.stdout).strip().splitlines()
            log(f"Could not close {name} (PID {pid}): {reason[-1] if reason else 'Windows denied the request.'}")
    selected_names = {name.casefold() for name, _, _ in processes}
    remaining = tuple(sorted({name for name, _, _ in running_apps() if name.casefold() in selected_names}, key=str.casefold))
    log(f"App closing complete: {closed} closed, {stopped} already stopped, {failed} failed.")
    if remaining:
        log("Selected app names still running or restarted: " + ", ".join(remaining))
    return CloseResult(closed, stopped, failed, remaining)
