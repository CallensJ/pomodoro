from pathlib import Path

from PySide6.QtCore import QObject, Signal

from src.presentation.music_player_widget import MusicPlayerWidget


class FakePlayer(QObject):
    track_finished = Signal()
    playback_error = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self.played: list[Path] = []
        self.paused = 0
        self.resumed = 0
        self.stopped = 0

    def play(self, file_path: Path) -> None:
        self.played.append(file_path)

    def pause(self) -> None:
        self.paused += 1

    def resume(self) -> None:
        self.resumed += 1

    def stop(self) -> None:
        self.stopped += 1


def make_folder_with_tracks(tmp_path: Path, names: list[str]) -> Path:
    for name in names:
        (tmp_path / name).write_bytes(b"")
    return tmp_path


def test_widget_is_collapsed_by_default(qtbot) -> None:
    widget = MusicPlayerWidget(player=FakePlayer())
    qtbot.addWidget(widget)

    assert widget.content.isHidden() is True


def test_load_folder_with_no_mp3_files_shows_error(qtbot, tmp_path) -> None:
    widget = MusicPlayerWidget(player=FakePlayer())
    qtbot.addWidget(widget)

    loaded = widget.load_folder(str(tmp_path))

    assert loaded is False
    assert widget.error_label.isHidden() is False
    assert widget.content.isHidden() is True


def test_load_folder_with_tracks_expands_and_shows_first_track(qtbot, tmp_path) -> None:
    folder = make_folder_with_tracks(tmp_path, ["b.mp3", "a.mp3"])
    widget = MusicPlayerWidget(player=FakePlayer())
    qtbot.addWidget(widget)

    loaded = widget.load_folder(str(folder))

    assert loaded is True
    assert widget.content.isHidden() is False
    assert widget.now_playing_label.text() == "Now playing: a.mp3"
    assert widget.track_count_label.text() == "Track 1/2"


def test_folder_loaded_signal_emits_on_success(qtbot, tmp_path) -> None:
    folder = make_folder_with_tracks(tmp_path, ["a.mp3"])
    widget = MusicPlayerWidget(player=FakePlayer())
    qtbot.addWidget(widget)

    with qtbot.waitSignal(widget.folder_loaded, timeout=1000) as blocker:
        widget.load_folder(str(folder))
    assert blocker.args == [str(folder)]


def test_play_starts_first_track_and_pause_pauses(qtbot, tmp_path) -> None:
    folder = make_folder_with_tracks(tmp_path, ["a.mp3"])
    player = FakePlayer()
    widget = MusicPlayerWidget(player=player)
    qtbot.addWidget(widget)
    widget.load_folder(str(folder))

    widget.play()
    assert player.played == [folder / "a.mp3"]
    assert widget.play_pause_button.text() == "Pause"

    widget.pause()
    assert player.paused == 1
    assert widget.play_pause_button.text() == "Play"


def test_play_after_pause_resumes_instead_of_restarting(qtbot, tmp_path) -> None:
    folder = make_folder_with_tracks(tmp_path, ["a.mp3"])
    player = FakePlayer()
    widget = MusicPlayerWidget(player=player)
    qtbot.addWidget(widget)
    widget.load_folder(str(folder))

    widget.play()
    widget.pause()
    widget.play()

    assert player.played == [folder / "a.mp3"]
    assert player.resumed == 1


def test_next_button_advances_and_wraps_to_first_track(qtbot, tmp_path) -> None:
    folder = make_folder_with_tracks(tmp_path, ["a.mp3", "b.mp3"])
    player = FakePlayer()
    widget = MusicPlayerWidget(player=player)
    qtbot.addWidget(widget)
    widget.load_folder(str(folder))
    widget.play()

    widget.next_button.click()
    assert widget.now_playing_label.text() == "Now playing: b.mp3"

    widget.next_button.click()
    assert widget.now_playing_label.text() == "Now playing: a.mp3"


def test_track_finished_auto_advances(qtbot, tmp_path) -> None:
    folder = make_folder_with_tracks(tmp_path, ["a.mp3", "b.mp3"])
    player = FakePlayer()
    widget = MusicPlayerWidget(player=player)
    qtbot.addWidget(widget)
    widget.load_folder(str(folder))
    widget.play()

    player.track_finished.emit()

    assert widget.now_playing_label.text() == "Now playing: b.mp3"
    assert widget.play_pause_button.text() == "Pause"


def test_playback_error_from_player_shows_inline_message(qtbot, tmp_path) -> None:
    folder = make_folder_with_tracks(tmp_path, ["a.mp3"])
    player = FakePlayer()
    widget = MusicPlayerWidget(player=player)
    qtbot.addWidget(widget)
    widget.load_folder(str(folder))

    player.playback_error.emit("No audio player found.")

    assert widget.error_label.isHidden() is False
    assert widget.error_label.text() == "No audio player found."


def test_toggle_button_collapses_and_expands(qtbot, tmp_path) -> None:
    folder = make_folder_with_tracks(tmp_path, ["a.mp3"])
    widget = MusicPlayerWidget(player=FakePlayer())
    qtbot.addWidget(widget)
    widget.load_folder(str(folder))
    assert widget.content.isHidden() is False

    widget.toggle_button.click()
    assert widget.content.isHidden() is True

    widget.toggle_button.click()
    assert widget.content.isHidden() is False
