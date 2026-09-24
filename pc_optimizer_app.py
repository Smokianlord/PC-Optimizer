"""PC Optimizer 3: Windows maintenance dashboard."""
from __future__ import annotations

import ctypes
import os
from pathlib import Path
import queue
import shutil
import sys
import threading
import tkinter as tk
from tkinter import messagebox, ttk

import optimizer_core as core

VERSION = "3.3"
BG = "#0B1120"
PANEL = "#131F33"
PANEL_ALT = "#192940"
LINE = "#29405B"
TEXT = "#ECF4FF"
MUTED = "#9CB1C9"
BLUE = "#35A7FF"
GREEN = "#39D6A1"
AMBER = "#FFBE62"
RED = "#FF6D79"


def resource_path(name: str) -> Path:
    return Path(getattr(sys, "_MEIPASS", Path(__file__).parent)) / name


def memory_summary() -> str:
    class MemoryStatus(ctypes.Structure):
        _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
    data = MemoryStatus()
    data.dwLength = ctypes.sizeof(data)
    if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(data)):
        return f"{data.ullAvailPhys / 2**30:.1f} GB available"
    return "Unavailable"


class App:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title(f"PC Optimizer {VERSION}")
        self.root.geometry("1220x790")
        self.root.minsize(1050, 690)
        self.root.configure(bg=BG)
        icon = resource_path("app_icon.ico")
        if icon.exists():
            try:
                self.root.iconbitmap(str(icon))
            except tk.TclError:
                pass
        self.events: queue.Queue[tuple[str, object]] = queue.Queue()
        self.busy = False
        self.apps: dict[str, tuple[str, int, str]] = {}
        self.selected_pids: set[str] = set()
        self.nav: dict[str, tk.Button] = {}
        self.current_page = "Dashboard"
        self._make_shell()
        self.show("Dashboard")
        self.root.after(100, self._drain)
        self.root.after(250, self.refresh)

    def _button(self, parent: tk.Widget, label: str, command, *, primary=False, danger=False) -> tk.Button:
        color = RED if danger else BLUE if primary else PANEL_ALT
        return tk.Button(parent, text=label, command=command, bg=color,
                         fg="#071321" if primary else TEXT,
                         activebackground="#69BCFF" if primary else "#315071",
                         activeforeground=TEXT, relief="flat", bd=0,
                         font=("Segoe UI", 10, "bold"), padx=15, pady=9,
                         cursor="hand2")

    def _label(self, parent: tk.Widget, text: str, *, size=10, color=TEXT, bold=False, bg=PANEL) -> tk.Label:
        return tk.Label(parent, text=text, bg=bg, fg=color,
                        font=("Segoe UI", size, "bold" if bold else "normal"), anchor="w")

    def _make_shell(self) -> None:
        sidebar = tk.Frame(self.root, bg="#0E192B", width=225)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        tk.Label(sidebar, text="◈  PC OPTIMIZER", bg="#0E192B", fg=TEXT,
                 font=("Segoe UI", 15, "bold"), anchor="w").pack(fill="x", padx=20, pady=(28, 4))
        tk.Label(sidebar, text="CONTROL CENTER  /  V3.3", bg="#0E192B", fg=BLUE,
                 font=("Segoe UI", 8, "bold"), anchor="w").pack(fill="x", padx=20, pady=(0, 32))
        for label, symbol in (("Dashboard", "▦"), ("App Manager", "▣"),
                              ("Maintenance", "✦")):
            button = tk.Button(sidebar, text=f"{symbol}   {label}", command=lambda page=label: self.show(page),
                               bg="#0E192B", fg=MUTED, activebackground=PANEL_ALT,
                               activeforeground=TEXT, anchor="w", relief="flat", bd=0,
                               font=("Segoe UI", 11, "bold"), padx=20, pady=14,
                               cursor="hand2")
            button.pack(fill="x", padx=9, pady=3)
            self.nav[label] = button
        self._label(sidebar, "LOCAL WINDOWS TOOLS", size=8, color=MUTED, bg="#0E192B").pack(side="bottom", padx=20, pady=24)

        main = tk.Frame(self.root, bg=BG)
        main.pack(side="left", fill="both", expand=True)
        top = tk.Frame(main, bg=BG)
        top.pack(fill="x", padx=28, pady=(23, 16))
        self.heading = self._label(top, "Dashboard", size=24, bold=True, bg=BG)
        self.heading.pack(side="left")
        self._button(top, "Refresh", self.refresh).pack(side="right", padx=(8, 0))
        self.admin_button = self._button(top, "Run as admin", self.request_admin)
        self.admin_button.pack(side="right")
        self.admin_chip = self._label(top, "", size=9, color=GREEN, bold=True, bg=BG)
        self.admin_chip.pack(side="right", padx=18)
        self.content = tk.Frame(main, bg=BG)
        self.content.pack(fill="both", expand=True, padx=28)
        self._log_dock(main)
        footer = tk.Frame(main, bg=BG)
        footer.pack(fill="x", padx=28, pady=(10, 17))
        self.status = self._label(footer, "Ready", size=9, color=MUTED, bg=BG)
        self.status.pack(side="left")
        self._label(footer, "Actions run only after confirmation", size=9, color=MUTED, bg=BG).pack(side="right")

    def _clear_content(self) -> None:
        for child in self.content.winfo_children():
            child.destroy()

    def show(self, page: str) -> None:
        self.current_page = page
        self.heading.configure(text=page)
        for label, button in self.nav.items():
            button.configure(bg=PANEL_ALT if label == page else "#0E192B",
                             fg=TEXT if label == page else MUTED)
        self._clear_content()
        {"Dashboard": self._dashboard, "App Manager": self._app_manager,
         "Maintenance": self._maintenance}[page]()

    def _log_dock(self, parent: tk.Widget) -> None:
        dock = tk.Frame(parent, bg=BG)
        dock.pack(fill="x", padx=28, pady=(9, 0))
        header = tk.Frame(dock, bg=BG)
        header.pack(fill="x", pady=(0, 7))
        self._label(header, "LIVE ACTIVITY", size=10, color=MUTED, bold=True, bg=BG).pack(side="left")
        self._button(header, "Copy", self.copy_log).pack(side="right", padx=(7, 0))
        self._button(header, "Clear", self.clear_log).pack(side="right")
        box = tk.Frame(dock, bg=PANEL, highlightbackground=LINE, highlightthickness=1)
        box.pack(fill="x")
        self.log_box = tk.Text(box, height=7, bg=PANEL, fg="#CEE2F6", insertbackground=TEXT,
                               font=("Consolas", 9), relief="flat", padx=12, pady=9,
                               wrap="word", state="disabled")
        scroll = ttk.Scrollbar(box, orient="vertical", command=self.log_box.yview)
        self.log_box.configure(yscrollcommand=scroll.set)
        self.log_box.pack(side="left", fill="x", expand=True)
        scroll.pack(side="right", fill="y")

    def _card(self, parent: tk.Widget, title: str, subtitle: str = "") -> tk.Frame:
        card = tk.Frame(parent, bg=PANEL, highlightbackground=LINE, highlightthickness=1)
        self._label(card, title, size=14, bold=True).pack(anchor="w", padx=18, pady=(16, 3))
        if subtitle:
            self._label(card, subtitle, size=9, color=MUTED).pack(anchor="w", padx=18, pady=(0, 12))
        return card

    def _dashboard(self) -> None:
        self._label(self.content, "A clear view of what you can safely review and run.",
                    color=MUTED, bg=BG).pack(anchor="w", pady=(0, 18))
        metrics = tk.Frame(self.content, bg=BG)
        metrics.pack(fill="x")
        for col in range(3):
            metrics.columnconfigure(col, weight=1, uniform="metric")
        metric_data = (("MEMORY AVAILABLE", memory_summary(), GREEN),
                       ("C: DRIVE FREE", self._disk_summary(), BLUE),
                       ("RUNNING USER APPS", str(len(self.apps)), AMBER))
        for col, (title, value, accent) in enumerate(metric_data):
            card = tk.Frame(metrics, bg=PANEL, highlightbackground=LINE, highlightthickness=1)
            card.grid(row=0, column=col, sticky="nsew", padx=(0, 10) if col < 2 else 0)
            self._label(card, title, size=9, color=MUTED, bold=True).pack(anchor="w", padx=18, pady=(18, 5))
            self._label(card, value, size=21, color=accent, bold=True).pack(anchor="w", padx=18, pady=(0, 18))
        actions = tk.Frame(self.content, bg=BG)
        actions.pack(fill="both", expand=True, pady=(20, 0))
        actions.columnconfigure(0, weight=1, uniform="action")
        actions.columnconfigure(1, weight=1, uniform="action")
        cards = [
            ("Manage running apps", "Review individual processes before closing anything.", "Open App Manager", lambda: self.show("App Manager")),
            ("Clean temporary files", "Remove files from your Temp folder and Windows Temp.", "Review cleanup", lambda: self.run_action("Clean temporary files")),
            ("Refresh connection", "Flush DNS and renew DHCP without a restart.", "Refresh network", lambda: self.run_action("Refresh network")),
            ("Repair Windows", "Run DISM and System File Checker in sequence.", "Review repair", lambda: self.run_action("Repair Windows")),
        ]
        for index, (title, detail, label, command) in enumerate(cards):
            card = self._card(actions, title, detail)
            card.grid(row=index // 2, column=index % 2, sticky="nsew", padx=(0, 10) if index % 2 == 0 else 0,
                      pady=(0, 10))
            self._button(card, label, command, primary=index == 0).pack(anchor="w", padx=18, pady=(0, 17))

    def _disk_summary(self) -> str:
        try:
            return f"{shutil.disk_usage(os.environ.get('SystemDrive', 'C:') + os.sep).free / 2**30:.0f} GB"
        except OSError:
            return "Unavailable"

    def _app_manager(self) -> None:
        self._label(self.content, "Select desktop apps to close. Windows and service-managed helpers are excluded.",
                    color=MUTED, bg=BG).pack(anchor="w", pady=(0, 10))
        toolbar = tk.Frame(self.content, bg=BG)
        toolbar.pack(fill="x", pady=(0, 12))
        self.search_var = tk.StringVar()
        self._label(toolbar, "Search", size=10, color=MUTED, bg=BG).pack(side="left", padx=(0, 10))
        search = tk.Entry(toolbar, textvariable=self.search_var, bg=PANEL, fg=TEXT,
                          insertbackground=TEXT, relief="flat", font=("Segoe UI", 11), bd=8)
        search.pack(side="left", fill="x", expand=True)
        self.search_var.trace_add("write", lambda *_: self._fill_apps())
        self._button(toolbar, "Close selected", self.close_apps, danger=True).pack(side="right", padx=(8, 0))
        self._button(toolbar, "Refresh list", self.refresh).pack(side="right", padx=(8, 0))
        self._button(toolbar, "Deselect all", self.deselect_all).pack(side="right", padx=(8, 0))
        self._button(toolbar, "Select all", self.select_all).pack(side="right", padx=(8, 0))
        holder = tk.Frame(self.content, bg=PANEL, highlightbackground=LINE, highlightthickness=1)
        holder.pack(fill="both", expand=True)
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure("Apps.Treeview", background=PANEL, fieldbackground=PANEL, foreground=TEXT,
                        rowheight=32, borderwidth=0, font=("Segoe UI", 10))
        style.map("Apps.Treeview", background=[("selected", "#24598A")], foreground=[("selected", TEXT)])
        style.configure("Apps.Treeview.Heading", background=PANEL_ALT, foreground=TEXT,
                        font=("Segoe UI", 10, "bold"), relief="flat")
        style.configure("Vertical.TScrollbar", background=PANEL_ALT, troughcolor=PANEL,
                        bordercolor=PANEL, arrowcolor=TEXT)
        self.tree = ttk.Treeview(holder, columns=("picked", "name", "pid", "path"), show="headings",
                                 selectmode="none", style="Apps.Treeview")
        for column, title, width in (("picked", "Select", 65), ("name", "Application", 250),
                                     ("pid", "PID", 75), ("path", "Location", 520)):
            self.tree.heading(column, text=title)
            self.tree.column(column, width=width, anchor="w")
        self.tree.bind("<Button-1>", self._toggle_app)
        scroll = ttk.Scrollbar(holder, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        self._fill_apps()
        self.selection_label = self._label(self.content, "", size=9, color=MUTED, bg=BG)
        self.selection_label.pack(anchor="w", pady=(9, 0))
        self._update_selection_label()

    def _fill_apps(self) -> None:
        if not hasattr(self, "tree") or not self.tree.winfo_exists():
            return
        term = self.search_var.get().lower().strip()
        self.tree.delete(*self.tree.get_children())
        for key, (name, pid, path) in self.apps.items():
            if term and term not in name.lower() and term not in path.lower():
                continue
            picked = "☑" if key in self.selected_pids else "☐"
            self.tree.insert("", "end", iid=key, values=(picked, name, pid, path))
        self._update_selection_label()

    def _toggle_app(self, event: tk.Event) -> str | None:
        if self.tree.identify_region(event.x, event.y) != "cell":
            return None
        key = self.tree.identify_row(event.y)
        if not key:
            return None
        if key in self.selected_pids:
            self.selected_pids.remove(key)
        else:
            self.selected_pids.add(key)
        self.tree.set(key, "picked", "☑" if key in self.selected_pids else "☐")
        self._update_selection_label()
        return "break"

    def select_all(self) -> None:
        self.selected_pids.update(self.tree.get_children())
        self._fill_apps()

    def deselect_all(self) -> None:
        self.selected_pids.clear()
        self._fill_apps()

    def _update_selection_label(self) -> None:
        if hasattr(self, "selection_label") and self.selection_label.winfo_exists():
            self.selection_label.configure(text=f"{len(self.selected_pids)} selected  •  Click any row to toggle  •  Save work before closing")

    def _maintenance(self) -> None:
        self._label(self.content, "Choose a specific repair task. Administrator access is required for system changes.",
                    color=MUTED, bg=BG).pack(anchor="w", pady=(0, 16))
        tasks = [
            ("Clean temporary files", "Current-user and Windows Temp only. Locked files are skipped."),
            ("Refresh network", "Flush DNS and renew DHCP. No restart required."),
            ("Repair network stack", "Reset Winsock and TCP/IP. Windows requires a restart afterward."),
            ("Repair Windows", "Run DISM RestoreHealth and SFC. This can take a while."),
            ("Run full maintenance", "Run cleanup, quick network refresh, and Windows repair."),
        ]
        for title, detail in tasks:
            row = tk.Frame(self.content, bg=PANEL, highlightbackground=LINE, highlightthickness=1)
            row.pack(fill="x", pady=(0, 11))
            self._button(row, "Run", lambda task=title: self.run_action(task), primary=True).pack(side="right", padx=16, pady=13)
            self._label(row, title, size=13, bold=True).pack(anchor="w", padx=18, pady=(13, 2))
            self._label(row, detail, size=9, color=MUTED).pack(anchor="w", padx=18, pady=(0, 14))

    def log(self, message: str) -> None:
        self.events.put(("log", message))

    def _drain(self) -> None:
        try:
            while True:
                kind, payload = self.events.get_nowait()
                if kind == "log":
                    from datetime import datetime
                    line = f"[{datetime.now():%H:%M:%S}] {payload}\n"
                    self.log_lines = getattr(self, "log_lines", [])
                    self.log_lines.append(line)
                    if hasattr(self, "log_box") and self.log_box.winfo_exists():
                        self.log_box.configure(state="normal")
                        self.log_box.insert("end", line)
                        self.log_box.see("end")
                        self.log_box.configure(state="disabled")
                elif kind == "done":
                    self.busy = False
                    self.refresh()
                    self.status.configure(text=str(payload))
        except queue.Empty:
            pass
        self.root.after(100, self._drain)

    def refresh(self) -> None:
        try:
            self.apps = {str(pid): (name, pid, path) for name, pid, path in core.running_apps()}
            self.selected_pids.intersection_update(self.apps)
            self.status.configure(text=f"Ready  •  {len(self.apps)} user processes")
        except Exception as exc:
            self.log(f"App scan failed: {exc}")
        self.admin_chip.configure(text="● ADMIN" if core.is_admin() else "● STANDARD",
                                  fg=GREEN if core.is_admin() else AMBER)
        self.admin_button.configure(state="disabled" if core.is_admin() else "normal")
        if self.current_page == "Dashboard":
            self.show("Dashboard")
        elif self.current_page == "App Manager":
            self._fill_apps()

    def request_admin(self) -> None:
        try:
            if core.elevate():
                self.root.destroy()
            else:
                messagebox.showerror("Administrator access", "Windows did not grant administrator access.")
        except Exception as exc:
            messagebox.showerror("Administrator access", str(exc))

    def _start(self, title: str, work) -> None:
        if self.busy:
            messagebox.showinfo("Busy", "Wait for the current task to finish.")
            return
        self.busy = True
        self.status.configure(text=f"Running {title}…")
        self.log(f"Started {title}")
        def worker() -> None:
            try:
                outcome = work()
                result = outcome or f"Completed {title}"
                self.log(result)
            except Exception as exc:
                self.log(f"Failed {title}: {exc}")
                result = f"Failed {title}: {exc}"
            self.events.put(("done", result))
        threading.Thread(target=worker, daemon=True).start()

    def run_action(self, title: str) -> None:
        if self.busy:
            messagebox.showinfo("Busy", "Wait for the current task to finish.")
            return
        if not core.is_admin():
            messagebox.showinfo("Administrator required", "Run the app as administrator to perform maintenance.")
            return
        details = {
            "Clean temporary files": "Remove files in your Temp and Windows Temp folders?",
            "Refresh network": "Flush DNS and renew DHCP? This may briefly interrupt your connection but does not require a restart.",
            "Repair network stack": "Reset Winsock and TCP/IP? Windows requires a restart to apply these changes.",
            "Repair Windows": "Run DISM and SFC? This may take a long time.",
            "Run full maintenance": "Run cleanup, quick network refresh, and Windows repair in sequence?",
        }
        if not messagebox.askyesno(f"Confirm {title}", details[title]):
            return
        def work() -> str | None:
            if title in ("Clean temporary files", "Run full maintenance"):
                core.clean_temp(self.log)
            if title in ("Refresh network", "Run full maintenance"):
                network_complete = core.refresh_network(self.log)
            if title == "Repair network stack":
                network_complete = core.reset_network(self.log)
            if title in ("Repair Windows", "Run full maintenance"):
                core.repair_windows(self.log)
            if title in ("Refresh network", "Run full maintenance") and not network_complete:
                return "DNS cleared; DHCP renewal was unavailable. Review the log. No restart requested."
            if title == "Repair network stack":
                return "Network stack reset completed; restart Windows to apply it." if network_complete else "Network stack partially reset; restart Windows and review the log."
        self._start(title, work)

    def close_apps(self) -> None:
        selected = list(self.selected_pids)
        if not selected:
            messagebox.showinfo("Select apps", "Select one or more running apps first.")
            return
        processes = [self.apps[key] for key in selected if key in self.apps]
        names = sorted({self.apps[key][0] for key in selected if key in self.apps})
        if not messagebox.askyesno("Close selected apps",
                                   f"Force-close {len(processes)} process(es)? Unsaved work will be lost.\n\n" + ", ".join(names)):
            return
        def work() -> str:
            result = core.close_selected(processes, self.log)
            status = f"Closed {result.closed}; {result.already_stopped} already stopped; {result.failed} failed."
            if result.still_running:
                status += f" {len(result.still_running)} app name(s) still running or restarted."
            return status
        self._start("selected apps", work)

    def copy_log(self) -> None:
        self.root.clipboard_clear()
        self.root.clipboard_append("".join(getattr(self, "log_lines", [])))
        self.status.configure(text="Activity copied to clipboard")

    def clear_log(self) -> None:
        self.log_lines = []
        if hasattr(self, "log_box") and self.log_box.winfo_exists():
            self.log_box.configure(state="normal")
            self.log_box.delete("1.0", "end")
            self.log_box.configure(state="disabled")


def main() -> None:
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
