"""Collapsible local music player: pick a folder, play its MP3 files."""

from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.infrastructure.local_music_player import LocalMusicPlayer
from src.infrastructure.music_library import scan_mp3_files


class MusicPlayerWidget(QWidget):
    folder_loaded = Signal(str)
    collapsed_changed = Signal(bool)

    def __init__(
        self, player: LocalMusicPlayer | None = None, parent: QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self._player = player if player is not None else LocalMusicPlayer()
        self._player.track_finished.connect(self._on_track_finished)
        self._player.playback_error.connect(self._show_error)
        self._tracks: list[Path] = []
        self._current_index = -1
        self._started = False
        self._is_playing = False
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        self.toggle_button = QPushButton("▸ Music", objectName="playerToggleButton")
        self.toggle_button.clicked.connect(self._on_toggle_clicked)
        layout.addWidget(self.toggle_button)

        self.content = QWidget()
        layout.addWidget(self.content)
        self._build_content(self.content)
        self.content.setVisible(False)

    def _build_content(self, content: QWidget) -> None:
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.addLayout(self._build_folder_row())
        self._build_status_labels(content_layout)
        content_layout.addLayout(self._build_controls_row())

    def _build_folder_row(self) -> QHBoxLayout:
        folder_row = QHBoxLayout()
        self.folder_label = QLabel("No folder selected", objectName="musicFolderLabel")
        self.folder_label.setWordWrap(True)
        self.choose_folder_button = QPushButton("Choose Folder")
        self.choose_folder_button.clicked.connect(self._on_choose_folder_clicked)
        folder_row.addWidget(self.folder_label, stretch=1)
        folder_row.addWidget(self.choose_folder_button)
        return folder_row

    def _build_status_labels(self, content_layout: QVBoxLayout) -> None:
        self.error_label = QLabel(objectName="playerErrorLabel")
        self.error_label.setWordWrap(True)
        self.error_label.setVisible(False)
        content_layout.addWidget(self.error_label)

        self.now_playing_label = QLabel(objectName="nowPlayingLabel")
        self.now_playing_label.setWordWrap(True)
        content_layout.addWidget(self.now_playing_label)

        self.track_count_label = QLabel(objectName="trackCountLabel")
        content_layout.addWidget(self.track_count_label)

    def _build_controls_row(self) -> QHBoxLayout:
        controls_row = QHBoxLayout()
        self.play_pause_button = QPushButton("Play")
        self.play_pause_button.clicked.connect(self._on_play_pause_clicked)
        self.next_button = QPushButton("Next")
        self.next_button.clicked.connect(self._on_next_clicked)
        controls_row.addWidget(self.play_pause_button, stretch=1)
        controls_row.addWidget(self.next_button)
        return controls_row

    def _on_toggle_clicked(self) -> None:
        self.set_collapsed(not self.content.isHidden())

    def set_collapsed(self, collapsed: bool) -> None:
        self.content.setVisible(not collapsed)
        self.toggle_button.setText(("▸" if collapsed else "▾") + " Music")
        self.collapsed_changed.emit(collapsed)

    def _on_choose_folder_clicked(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Choose Music Folder")
        if folder:
            self.load_folder(folder)

    def load_folder(self, folder: str) -> bool:
        tracks = scan_mp3_files(Path(folder))
        if not tracks:
            self._show_error("No MP3 files found in this folder.")
            return False

        self._clear_error()
        self._player.stop()
        self._tracks = tracks
        self._current_index = 0
        self._started = False
        self._is_playing = False
        self.folder_label.setText(folder)
        self.play_pause_button.setText("Play")
        self._update_now_playing()
        self.set_collapsed(False)
        self.folder_loaded.emit(folder)
        return True

    def _update_now_playing(self) -> None:
        if not self._tracks:
            self.now_playing_label.setText("")
            self.track_count_label.setText("")
            return
        track = self._tracks[self._current_index]
        self.now_playing_label.setText(f"Now playing: {track.name}")
        self.track_count_label.setText(
            f"Track {self._current_index + 1}/{len(self._tracks)}"
        )

    def _on_play_pause_clicked(self) -> None:
        self.pause() if self._is_playing else self.play()

    def play(self) -> None:
        if not self._tracks or self._is_playing:
            return
        if self._started:
            self._player.resume()
        else:
            self._start_current_track()
        self._is_playing = True
        self.play_pause_button.setText("Pause")

    def pause(self) -> None:
        if not self._is_playing:
            return
        self._player.pause()
        self._is_playing = False
        self.play_pause_button.setText("Play")

    def _start_current_track(self) -> None:
        self._player.play(self._tracks[self._current_index])
        self._started = True
        self._update_now_playing()

    def _on_next_clicked(self) -> None:
        self._advance_and_play()

    def _on_track_finished(self) -> None:
        self._advance_and_play()

    def _advance_and_play(self) -> None:
        if not self._tracks:
            return
        self._current_index = (self._current_index + 1) % len(self._tracks)
        self._start_current_track()
        self._is_playing = True
        self.play_pause_button.setText("Pause")

    def _show_error(self, message: str) -> None:
        self.error_label.setText(message)
        self.error_label.setVisible(True)

    def _clear_error(self) -> None:
        self.error_label.setVisible(False)
