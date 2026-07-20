"""Scans a local folder for playable MP3 files."""

from pathlib import Path


def scan_mp3_files(folder: Path) -> list[Path]:
    if not folder.is_dir():
        return []
    return sorted(
        (
            entry
            for entry in folder.iterdir()
            if entry.is_file() and entry.suffix.lower() == ".mp3"
        ),
        key=lambda entry: entry.name.lower(),
    )
