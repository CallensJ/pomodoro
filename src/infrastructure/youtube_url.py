"""Parses and normalizes YouTube URLs into official embed URLs."""

import re
from dataclasses import dataclass
from urllib.parse import parse_qs, urlencode, urlparse

VIDEO_ID_PATTERN = re.compile(r"^[\w-]{5,20}$")
PLAYLIST_ID_PATTERN = re.compile(r"^[\w-]{10,60}$")

YOUTUBE_HOSTS = {"youtube.com", "www.youtube.com", "m.youtube.com"}
YOUTU_BE_HOSTS = {"youtu.be", "www.youtu.be"}


class YoutubeUrlError(ValueError):
    pass


@dataclass(frozen=True)
class ParsedYoutubeUrl:
    video_id: str | None
    playlist_id: str | None
    embed_url: str


def parse_youtube_url(url: str) -> ParsedYoutubeUrl:
    parsed = urlparse(url.strip())
    if parsed.scheme not in ("http", "https"):
        raise YoutubeUrlError("URL must start with http:// or https://")

    host = (parsed.hostname or "").lower()
    if host in YOUTU_BE_HOSTS:
        video_id, playlist_id = _from_youtu_be(parsed)
    elif host in YOUTUBE_HOSTS:
        video_id, playlist_id = _from_youtube_com(parsed)
    else:
        raise YoutubeUrlError("Only youtube.com and youtu.be URLs are supported")

    _validate_ids(video_id, playlist_id)
    return ParsedYoutubeUrl(
        video_id, playlist_id, _build_embed_url(video_id, playlist_id)
    )


def _from_youtu_be(parsed) -> tuple[str | None, str | None]:
    video_id = parsed.path.lstrip("/") or None
    query = parse_qs(parsed.query)
    playlist_id = query.get("list", [None])[0]
    return video_id, playlist_id


def _from_youtube_com(parsed) -> tuple[str | None, str | None]:
    query = parse_qs(parsed.query)
    if parsed.path == "/watch":
        video_id = query.get("v", [None])[0]
        playlist_id = query.get("list", [None])[0]
        return video_id, playlist_id
    if parsed.path == "/playlist":
        return None, query.get("list", [None])[0]
    if parsed.path.startswith("/embed/"):
        video_id = parsed.path.removeprefix("/embed/") or None
        playlist_id = query.get("list", [None])[0]
        return video_id, playlist_id
    raise YoutubeUrlError("Unsupported YouTube URL format")


def _validate_ids(video_id: str | None, playlist_id: str | None) -> None:
    if video_id is None and playlist_id is None:
        raise YoutubeUrlError("URL does not contain a video or playlist")
    if video_id is not None and not VIDEO_ID_PATTERN.match(video_id):
        raise YoutubeUrlError("Video ID has an unexpected format")
    if playlist_id is not None and not PLAYLIST_ID_PATTERN.match(playlist_id):
        raise YoutubeUrlError("Playlist ID has an unexpected format")


def _build_embed_url(video_id: str | None, playlist_id: str | None) -> str:
    path = f"/embed/{video_id}" if video_id else "/embed/videoseries"
    params = {"enablejsapi": "1"}
    if playlist_id:
        params["list"] = playlist_id
    return f"https://www.youtube.com{path}?{urlencode(params)}"
