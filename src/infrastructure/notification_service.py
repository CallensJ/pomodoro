"""Best-effort desktop notifications; failures are logged, never raised further."""

import logging
import platform
import subprocess

logger = logging.getLogger(__name__)


class NotificationService:
    def notify(self, title: str, message: str) -> None:
        system = platform.system()
        try:
            if system == "Linux":
                self._notify_linux(title, message)
            elif system == "Windows":
                self._notify_windows(title, message)
            else:
                logger.info("Desktop notifications are not supported on %s", system)
        except (OSError, subprocess.SubprocessError):
            logger.exception("Failed to display desktop notification")

    def _notify_linux(self, title: str, message: str) -> None:
        subprocess.Popen(
            ["notify-send", title, message],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    def _notify_windows(self, title: str, message: str) -> None:
        safe_title = title.replace("'", "''")
        safe_message = message.replace("'", "''")
        script = (
            "Add-Type -AssemblyName System.Windows.Forms; "
            "$n = New-Object System.Windows.Forms.NotifyIcon; "
            "$n.Icon = [System.Drawing.SystemIcons]::Information; "
            "$n.Visible = $true; "
            f"$n.ShowBalloonTip(5000, '{safe_title}', '{safe_message}', "
            "[System.Windows.Forms.ToolTipIcon]::Info); "
            "Start-Sleep -Seconds 6; $n.Dispose()"
        )
        subprocess.Popen(
            ["powershell", "-NoProfile", "-Command", script],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
