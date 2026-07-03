# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

HUAWEI Router Assistant — a PyQt5 desktop app that monitors a HUAWEI Mobile Wifi 3 Pro router. It polls router HTTP APIs for XML responses and displays battery, signal, traffic, and connection stats in a system-tray GUI built with PyQt-Fluent-Widgets.

## Environment

- **Python >= 3.12** required (enforced in `@pyproject.toml`)
- **Windows-only** — uses Windows notification API (`notifypy`), `.ico` icons, and PowerShell build scripts
- Package manager: **uv** (lockfile: `uv.lock`). Install deps with `uv sync`
- Virtual environment: `.venv` (managed by uv)

## Running the App

- **Development**: `python main.py` from the project root (requires `uv sync` first)
- **Distribution**: `.\build.ps1` runs PyInstaller using `@HUAWEI_Router_Assistant.spec` to produce a Windows `.exe`
- The app runs as a system-tray icon with three async polling loops (15s monitoring, 1s traffic, 15min battery history)

## Critical Gotcha: Router Must Be Reachable

The app connects to the router at `192.168.8.1` by default. All HTTP API calls will fail silently and show "Device offline" if the router is not on the local network. The `NO_PROXY` env var is set in `@app/common/RouterInfo.py` to bypass system proxy settings.

## Code Structure

- `main.py` — entry point, PyQt5 + qasync event loop setup, system tray
- `app/common/` — core logic: `@app/common/RouterInfo.py` (router API client), `@app/common/config.py` (settings), `@app/common/database.py` (SQLite battery history), `@app/common/global_logger.py`
- `app/components/` — UI card widgets for each info panel
- `app/view/` — window and interface definitions
- `app/config/config.json` — runtime settings (battery thresholds, language, theme)
- `app/resource/` — icons, translations, QSS stylesheets, compiled via `@app/resource/resource.qrc`

## Configuration

Settings are loaded from `app/config/config.json` using `qfluentwidgets.QConfig`. Key settings:
- Battery notification thresholds (upper/lower bounds)
- DPI scaling mode, language, theme
- `enableLogging` (default false) — when true, writes debug XML responses to `debug/` directory and logs to file

## Build Commands

- Install dependencies: `uv sync`
- Run: `python main.py`
- Package: `.\build.ps1` (PyInstaller, produces `dist\HUAWEI_Router_Assistant\`)
- PyInstaller spec: `@HUAWEI_Router_Assistant.spec` (includes battery icons and logo as data files, `--noconsole` mode)

## Version Control

Push directly to the main branch — no feature branches or PR workflow.

## Testing

`@test.py` is an unrelated utility script (Unix timestamp conversion), not a test suite. The project has no formal test framework. Add tests if needed.

## Known Limitations

- Password authentication to the router is not implemented (unknown secure mechanism)
- Some router data requires authenticated sessions and is unavailable
- SQLite database (`sqlite.db`) stores battery history with 12-hour retention
