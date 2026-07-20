from src.presentation.youtube_player import YoutubePlayerWidget


def test_player_is_collapsed_by_default(qtbot) -> None:
    player = YoutubePlayerWidget()
    qtbot.addWidget(player)

    assert player.content.isHidden() is True
    assert player.toggle_button.text() == "▸ Music"


def test_invalid_url_shows_error_and_stays_collapsed(qtbot) -> None:
    player = YoutubePlayerWidget()
    qtbot.addWidget(player)

    loaded = player.load("not a youtube url")

    assert loaded is False
    assert player.error_label.isHidden() is False
    assert player.content.isHidden() is True


def test_valid_url_clears_error_and_expands(qtbot) -> None:
    player = YoutubePlayerWidget()
    qtbot.addWidget(player)

    loaded = player.load("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

    assert loaded is True
    assert player.error_label.isHidden() is True
    assert player.content.isHidden() is False


def test_url_loaded_signal_emits_only_on_success(qtbot) -> None:
    player = YoutubePlayerWidget()
    qtbot.addWidget(player)

    with qtbot.waitSignal(player.url_loaded, timeout=1000) as blocker:
        player.load("https://youtu.be/dQw4w9WgXcQ")
    assert blocker.args == ["https://youtu.be/dQw4w9WgXcQ"]


def test_toggle_button_collapses_and_expands(qtbot) -> None:
    player = YoutubePlayerWidget()
    qtbot.addWidget(player)
    player.load("https://youtu.be/dQw4w9WgXcQ")
    assert player.content.isHidden() is False

    player.toggle_button.click()
    assert player.content.isHidden() is True

    player.toggle_button.click()
    assert player.content.isHidden() is False


def test_play_and_pause_do_not_raise_without_loaded_video(qtbot) -> None:
    player = YoutubePlayerWidget()
    qtbot.addWidget(player)

    player.play()
    player.pause()


def test_offline_or_never_ready_player_shows_error_without_crashing(qtbot) -> None:
    player = YoutubePlayerWidget()
    qtbot.addWidget(player)
    player.load("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

    player._handle_ready_result(player._load_token, ready=False)

    assert player.error_label.isHidden() is False
    assert "internet connection" in player.error_label.text()


def test_stale_ready_check_after_new_load_is_ignored(qtbot) -> None:
    player = YoutubePlayerWidget()
    qtbot.addWidget(player)
    player.load("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    stale_token = player._load_token

    player.load("https://youtu.be/dQw4w9WgXcQ")
    player._handle_ready_result(stale_token, ready=False)

    assert player.error_label.isHidden() is True


def test_youtube_error_code_maps_to_friendly_message(qtbot) -> None:
    player = YoutubePlayerWidget()
    qtbot.addWidget(player)
    player.load("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

    player._on_title_changed("YT_ERROR:101")

    assert player.error_label.isHidden() is False
    assert "does not allow embedding" in player.error_label.text()


def test_unknown_error_code_falls_back_to_generic_message(qtbot) -> None:
    player = YoutubePlayerWidget()
    qtbot.addWidget(player)
    player.load("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

    player._on_title_changed("YT_ERROR:999")

    assert player.error_label.isHidden() is False
    assert player.error_label.text() == "This video cannot be played."
