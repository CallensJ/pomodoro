import platform
import signal as signal_module

import pytest
from PySide6.QtCore import QProcess

from src.infrastructure.local_music_player import MCI_ALIAS, LocalMusicPlayer


@pytest.fixture
def linux_platform(monkeypatch):
    monkeypatch.setattr(platform, "system", lambda: "Linux")


@pytest.fixture
def windows_platform(monkeypatch):
    monkeypatch.setattr(platform, "system", lambda: "Windows")


# -- Linux --------------------------------------------------------------


def test_play_starts_ffplay_when_available(
    qtbot, monkeypatch, linux_platform, tmp_path
) -> None:
    monkeypatch.setattr(
        "shutil.which", lambda name: "/usr/bin/ffplay" if name == "ffplay" else None
    )
    started = []
    monkeypatch.setattr(
        QProcess, "start", lambda self, program, args: started.append((program, args))
    )

    track = tmp_path / "song.mp3"
    LocalMusicPlayer().play(track)

    assert len(started) == 1
    program, args = started[0]
    assert program == "/usr/bin/ffplay"
    assert str(track) in args


def test_play_falls_back_to_cvlc_when_ffplay_missing(
    qtbot, monkeypatch, linux_platform, tmp_path
) -> None:
    monkeypatch.setattr(
        "shutil.which", lambda name: "/usr/bin/cvlc" if name == "cvlc" else None
    )
    started = []
    monkeypatch.setattr(
        QProcess, "start", lambda self, program, args: started.append((program, args))
    )

    LocalMusicPlayer().play(tmp_path / "song.mp3")

    assert started[0][0] == "/usr/bin/cvlc"


def test_play_does_nothing_when_no_player_found(
    qtbot, monkeypatch, linux_platform, tmp_path
) -> None:
    monkeypatch.setattr("shutil.which", lambda name: None)
    started = []
    monkeypatch.setattr(
        QProcess, "start", lambda self, program, args: started.append((program, args))
    )

    LocalMusicPlayer().play(tmp_path / "song.mp3")

    assert started == []


def test_play_emits_playback_error_when_no_player_found(
    qtbot, monkeypatch, linux_platform, tmp_path
) -> None:
    monkeypatch.setattr("shutil.which", lambda name: None)

    player = LocalMusicPlayer()
    with qtbot.waitSignal(player.playback_error, timeout=1000) as blocker:
        player.play(tmp_path / "song.mp3")
    assert "No audio player" in blocker.args[0]


def test_pause_sends_sigstop_to_process(
    qtbot, monkeypatch, linux_platform, tmp_path
) -> None:
    monkeypatch.setattr(
        "shutil.which", lambda name: "/usr/bin/ffplay" if name == "ffplay" else None
    )
    monkeypatch.setattr(QProcess, "start", lambda self, program, args: None)
    monkeypatch.setattr(QProcess, "processId", lambda self: 4242)
    signals_sent = []
    monkeypatch.setattr("os.kill", lambda pid, sig: signals_sent.append((pid, sig)))

    player = LocalMusicPlayer()
    player.play(tmp_path / "song.mp3")
    player.pause()

    assert signals_sent == [(4242, signal_module.SIGSTOP)]


def test_resume_sends_sigcont_to_process(
    qtbot, monkeypatch, linux_platform, tmp_path
) -> None:
    monkeypatch.setattr(
        "shutil.which", lambda name: "/usr/bin/ffplay" if name == "ffplay" else None
    )
    monkeypatch.setattr(QProcess, "start", lambda self, program, args: None)
    monkeypatch.setattr(QProcess, "processId", lambda self: 4242)
    signals_sent = []
    monkeypatch.setattr("os.kill", lambda pid, sig: signals_sent.append((pid, sig)))

    player = LocalMusicPlayer()
    player.play(tmp_path / "song.mp3")
    player.resume()

    assert signals_sent == [(4242, signal_module.SIGCONT)]


def test_stop_kills_process_and_does_not_emit_track_finished(
    qtbot, monkeypatch, linux_platform, tmp_path
) -> None:
    monkeypatch.setattr(
        "shutil.which", lambda name: "/usr/bin/ffplay" if name == "ffplay" else None
    )
    monkeypatch.setattr(QProcess, "start", lambda self, program, args: None)
    killed = []
    monkeypatch.setattr(QProcess, "kill", lambda self: killed.append(True))

    player = LocalMusicPlayer()
    received = []
    player.track_finished.connect(lambda: received.append(True))
    player.play(tmp_path / "song.mp3")
    player.stop()

    assert killed == [True]
    assert received == []


def test_track_finished_emitted_when_process_exits_naturally(
    qtbot, monkeypatch, linux_platform, tmp_path
) -> None:
    monkeypatch.setattr(
        "shutil.which", lambda name: "/usr/bin/ffplay" if name == "ffplay" else None
    )
    monkeypatch.setattr(QProcess, "start", lambda self, program, args: None)

    player = LocalMusicPlayer()
    player.play(tmp_path / "song.mp3")

    with qtbot.waitSignal(player.track_finished, timeout=1000):
        player._process.finished.emit(0, QProcess.ExitStatus.NormalExit)


# -- Windows (mocked MCI calls; not runnable on a real Windows machine here) --


def test_play_windows_opens_and_plays_via_mci(
    qtbot, monkeypatch, windows_platform, tmp_path
) -> None:
    commands = []
    monkeypatch.setattr(
        LocalMusicPlayer, "_mci_command", lambda self, cmd: commands.append(cmd)
    )

    track = tmp_path / "song.mp3"
    LocalMusicPlayer().play(track)

    assert any("open" in c and str(track) in c for c in commands)
    assert commands[-1] == f"play {MCI_ALIAS}"


def test_pause_windows_sends_mci_pause_command(
    qtbot, monkeypatch, windows_platform, tmp_path
) -> None:
    commands = []
    monkeypatch.setattr(
        LocalMusicPlayer, "_mci_command", lambda self, cmd: commands.append(cmd)
    )

    player = LocalMusicPlayer()
    player.play(tmp_path / "song.mp3")
    commands.clear()
    player.pause()

    assert commands == [f"pause {MCI_ALIAS}"]


def test_resume_windows_sends_mci_resume_command(
    qtbot, monkeypatch, windows_platform, tmp_path
) -> None:
    commands = []
    monkeypatch.setattr(
        LocalMusicPlayer, "_mci_command", lambda self, cmd: commands.append(cmd)
    )

    player = LocalMusicPlayer()
    player.play(tmp_path / "song.mp3")
    commands.clear()
    player.resume()

    assert commands == [f"resume {MCI_ALIAS}"]


def test_stop_windows_sends_stop_and_close(
    qtbot, monkeypatch, windows_platform, tmp_path
) -> None:
    commands = []
    monkeypatch.setattr(
        LocalMusicPlayer, "_mci_command", lambda self, cmd: commands.append(cmd)
    )

    player = LocalMusicPlayer()
    player.play(tmp_path / "song.mp3")
    commands.clear()
    player.stop()

    assert commands == [f"stop {MCI_ALIAS}", f"close {MCI_ALIAS}"]


def test_poll_detects_natural_track_completion_on_windows(
    qtbot, monkeypatch, windows_platform, tmp_path
) -> None:
    monkeypatch.setattr(LocalMusicPlayer, "_mci_command", lambda self, cmd: None)
    monkeypatch.setattr(LocalMusicPlayer, "_mci_query_status", lambda self: "stopped")

    player = LocalMusicPlayer()
    player.play(tmp_path / "song.mp3")

    received = []
    player.track_finished.connect(lambda: received.append(True))
    player._poll_mci_status()

    assert received == [True]
