import unittest
import io
from types import SimpleNamespace
from unittest.mock import patch

import optimizer_core as core


class MaintenanceTests(unittest.TestCase):
    def test_app_scan_hides_windows_hosted_and_service_helpers(self):
        processes = [
            (100, "SearchHost.exe", "C:\\Windows\\SystemApps\\SearchHost.exe", 400),
            (101, "msedgewebview2.exe", "C:\\Program Files\\WebView\\msedgewebview2.exe", 100),
            (200, "nvcontainer.exe", "C:\\Program Files\\NVIDIA\\nvcontainer.exe", 1),
            (201, "nvcontainer.exe", "C:\\Program Files\\NVIDIA\\nvcontainer.exe", 200),
            (300, "User.exe", "C:\\Apps\\User.exe", 400),
            (400, "explorer.exe", "C:\\Windows\\explorer.exe", 1),
        ]
        items = [SimpleNamespace(pid=pid, info={"name": name, "exe": path, "ppid": parent})
                 for pid, name, path, parent in processes]
        service = SimpleNamespace(pid=lambda: 200)
        with patch.object(core.psutil, "process_iter", return_value=items), \
             patch.object(core.psutil, "win_service_iter", return_value=[service]), \
             patch.object(core, "_session_id", side_effect=lambda pid: 0 if pid == 200 else 1):
            names = [name for name, _, _ in core.running_apps()]
        self.assertEqual(names, ["User.exe"])

    def test_quick_network_refresh_avoids_stack_reset(self):
        with patch.object(core, "run_command", return_value=True) as run:
            self.assertTrue(core.refresh_network(lambda _: None))
        self.assertEqual([call.args[0] for call in run.call_args_list], [
            ["ipconfig", "/flushdns"], ["ipconfig", "/renew"]])

    def test_ip_reset_reports_protected_setting_as_partial(self):
        class Process:
            stdout = io.StringIO("Resetting Interface, OK!\nResetting , failed.\nAccess is denied.\n")
            def wait(self):
                return 1
        log = []
        with patch.object(core.subprocess, "Popen", return_value=Process()):
            result = core.run_command(["netsh", "int", "ip", "reset"], log.append,
                                      allow_partial_ip_reset=True)
        self.assertFalse(result)
        self.assertTrue(any("protected setting" in line for line in log))

    def test_ip_reset_without_progress_still_fails(self):
        class Process:
            stdout = io.StringIO("Access is denied.\n")
            def wait(self):
                return 1
        with patch.object(core.subprocess, "Popen", return_value=Process()):
            with self.assertRaises(RuntimeError):
                core.run_command(["netsh", "int", "ip", "reset"], lambda _: None,
                                 allow_partial_ip_reset=True)

    def test_network_reset_runs_each_step_once(self):
        with patch.object(core, "run_command") as run:
            core.reset_network(lambda _: None)
        self.assertEqual([call.args[0] for call in run.call_args_list], [
            ["ipconfig", "/flushdns"],
            ["netsh", "winsock", "reset"],
            ["netsh", "int", "ip", "reset"],
        ])

    def test_repair_stops_if_dism_fails(self):
        with patch.object(core, "run_command", side_effect=RuntimeError("DISM failed")) as run:
            with self.assertRaisesRegex(RuntimeError, "DISM failed"):
                core.repair_windows(lambda _: None)
        self.assertEqual(run.call_count, 1)

    def test_close_selected_rechecks_live_processes(self):
        completed = unittest.mock.Mock(returncode=0)
        with patch.object(core, "running_apps", return_value=[]), \
             patch.object(core, "_image_path", side_effect=["C:\\Example.exe", None]), \
             patch.object(core.subprocess, "run", return_value=completed) as run:
            result = core.close_selected([
                ("Example.exe", 42, "C:\\Example.exe"),
                ("Example.exe", 42, "C:\\Example.exe"),
                ("Gone.exe", 99, "C:\\Gone.exe"),
            ], lambda _: None)
        self.assertEqual((result.closed, result.already_stopped, result.failed), (1, 1, 0))
        self.assertEqual(run.call_count, 1)

    def test_process_disappearing_during_kill_is_not_a_failure(self):
        completed = unittest.mock.Mock(returncode=128, stderr="not found", stdout="")
        with patch.object(core, "running_apps", return_value=[]), \
             patch.object(core, "_image_path", side_effect=["C:\\Example.exe", None]), \
             patch.object(core.subprocess, "run", return_value=completed):
            result = core.close_selected([("Example.exe", 42, "C:\\Example.exe")], lambda _: None)
        self.assertEqual((result.closed, result.already_stopped, result.failed), (0, 1, 0))

    def test_restarted_app_is_reported_after_successful_close(self):
        completed = unittest.mock.Mock(returncode=0)
        with patch.object(core, "running_apps", return_value=[("Example.exe", 77, "C:\\Example.exe")]), \
             patch.object(core, "_image_path", return_value="C:\\Example.exe"), \
             patch.object(core.subprocess, "run", return_value=completed):
            result = core.close_selected([("Example.exe", 42, "C:\\Example.exe")], lambda _: None)
        self.assertEqual(result.closed, 1)
        self.assertEqual(result.still_running, ("Example.exe",))


if __name__ == "__main__":
    unittest.main()
