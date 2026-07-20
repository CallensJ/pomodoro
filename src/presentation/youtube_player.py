"""Collapsible YouTube concentration player backed by the IFrame Player API."""

import json

from PySide6.QtCore import QTimer, QUrl, Signal
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.infrastructure.youtube_url import (
    ParsedYoutubeUrl,
    YoutubeUrlError,
    parse_youtube_url,
)

READY_CHECK_DELAY_MS = 8000

ERROR_MESSAGES = {
    2: "Invalid video ID in the URL.",
    5: "This video cannot be played in an embedded player.",
    100: "Video not found or is private.",
    101: "The video owner does not allow embedding.",
    150: "The video owner does not allow embedding.",
}

PLAY_JS = "if (typeof player !== 'undefined' && player.playVideo) player.playVideo();"
PAUSE_JS = (
    "if (typeof player !== 'undefined' && player.pauseVideo) player.pauseVideo();"
)
READY_CHECK_JS = "typeof player !== 'undefined' && !!player.getPlayerState"


class YoutubePlayerWidget(QWidget):
    url_loaded = Signal(str)
    collapsed_changed = Signal(bool)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._load_token = 0
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

        url_row = QHBoxLayout()
        self.url_input = QLineEdit(objectName="youtubeUrlInput")
        self.url_input.setPlaceholderText("YouTube video or playlist URL")
        self.url_input.returnPressed.connect(self._on_load_clicked)
        self.load_button = QPushButton("Load")
        self.load_button.clicked.connect(self._on_load_clicked)
        url_row.addWidget(self.url_input, stretch=1)
        url_row.addWidget(self.load_button)
        content_layout.addLayout(url_row)

        self.error_label = QLabel(objectName="playerErrorLabel")
        self.error_label.setWordWrap(True)
        self.error_label.setVisible(False)
        content_layout.addWidget(self.error_label)

        self.web_view = QWebEngineView()
        self.web_view.setFixedHeight(200)
        self.web_view.titleChanged.connect(self._on_title_changed)
        content_layout.addWidget(self.web_view)

    def _on_toggle_clicked(self) -> None:
        self.set_collapsed(not self.content.isHidden())

    def set_collapsed(self, collapsed: bool) -> None:
        self.content.setVisible(not collapsed)
        self.toggle_button.setText(("▸" if collapsed else "▾") + " Music")
        self.collapsed_changed.emit(collapsed)

    def _on_load_clicked(self) -> None:
        self.load(self.url_input.text())

    def load(self, url: str) -> bool:
        url = url.strip()
        try:
            parsed = parse_youtube_url(url)
        except YoutubeUrlError as error:
            self._show_error(str(error))
            return False

        self._clear_error()
        self._load_token += 1
        token = self._load_token
        self.web_view.setHtml(
            _build_player_html(parsed), QUrl("https://www.youtube.com/")
        )
        QTimer.singleShot(READY_CHECK_DELAY_MS, lambda: self._check_ready(token))
        self.set_collapsed(False)
        self.url_loaded.emit(url)
        return True

    def _check_ready(self, token: int) -> None:
        if token != self._load_token:
            return
        self.web_view.page().runJavaScript(
            READY_CHECK_JS, lambda ready: self._handle_ready_result(token, ready)
        )

    def _handle_ready_result(self, token: int, ready: bool) -> None:
        if token != self._load_token or ready:
            return
        self._show_error("Could not load the video. Check your internet connection.")

    def _on_title_changed(self, title: str) -> None:
        if not title.startswith("YT_ERROR:"):
            return
        try:
            code = int(title.removeprefix("YT_ERROR:"))
        except ValueError:
            code = None
        self._show_error(ERROR_MESSAGES.get(code, "This video cannot be played."))

    def _show_error(self, message: str) -> None:
        self.error_label.setText(message)
        self.error_label.setVisible(True)

    def _clear_error(self) -> None:
        self.error_label.setVisible(False)

    def play(self) -> None:
        self.web_view.page().runJavaScript(PLAY_JS)

    def pause(self) -> None:
        self.web_view.page().runJavaScript(PAUSE_JS)


def _build_player_config(parsed: ParsedYoutubeUrl) -> str:
    config = {
        "height": "100%",
        "width": "100%",
        "playerVars": {"playsinline": 1, "origin": "https://www.youtube.com"},
    }
    if parsed.video_id:
        config["videoId"] = parsed.video_id
    if parsed.playlist_id:
        config["playerVars"]["list"] = parsed.playlist_id
        config["playerVars"]["listType"] = "playlist"
    return json.dumps(config)


def _build_player_html(parsed: ParsedYoutubeUrl) -> str:
    config_json = _build_player_config(parsed)
    return f"""<!DOCTYPE html>
<html>
<body style="margin:0;background:#000;">
<div id="player"></div>
<script>
  var tag = document.createElement('script');
  tag.src = "https://www.youtube.com/iframe_api";
  document.body.appendChild(tag);
  var player;
  function onYouTubeIframeAPIReady() {{
    player = new YT.Player('player', Object.assign({config_json}, {{
      events: {{
        onError: function(e) {{ document.title = 'YT_ERROR:' + e.data; }}
      }}
    }}));
  }}
</script>
</body>
</html>"""
