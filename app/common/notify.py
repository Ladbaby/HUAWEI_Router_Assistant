import asyncio
from desktop_notifier import DesktopNotifier, Icon
from pathlib import Path

notifier = None
_tasks = set()


def _get_notifier() -> DesktopNotifier:
    """Return a shared DesktopNotifier instance."""
    global notifier
    if notifier is None:
        notifier = DesktopNotifier(app_name="HUAWEI Router Assistant")
    return notifier


def send_notification(title: str, message: str, icon_path: str | None = None) -> None:
    """Fire a native OS notification (fire-and-forget).

    On Windows this uses WinRT Toast Notifications, which integrates with
    Windows Notification Settings (Focus Assist / Do Not Disturb).
    On Linux this uses the DBus org.freedesktop.Notifications service.
    """
    async def _send() -> None:
        try:
            icon = None
            if icon_path is not None:
                icon = Icon(path=Path(icon_path).resolve())

            await _get_notifier().send(
                title=title,
                message=message,
                icon=icon,
            )
        except Exception:
            from .global_logger import logger
            logger.warning("Notification failed for '%s'", title, exc_info=True)

    task = asyncio.create_task(_send())
    _tasks.add(task)
    task.add_done_callback(lambda t: _tasks.discard(t))
