import pytest

from src.infrastructure.youtube_url import YoutubeUrlError, parse_youtube_url


def test_standard_watch_url() -> None:
    result = parse_youtube_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    assert result.video_id == "dQw4w9WgXcQ"
    assert result.playlist_id is None
    assert result.embed_url == "https://www.youtube.com/embed/dQw4w9WgXcQ?enablejsapi=1"


def test_watch_url_without_www() -> None:
    result = parse_youtube_url("https://youtube.com/watch?v=dQw4w9WgXcQ")
    assert result.video_id == "dQw4w9WgXcQ"


def test_mobile_host_watch_url() -> None:
    result = parse_youtube_url("https://m.youtube.com/watch?v=dQw4w9WgXcQ")
    assert result.video_id == "dQw4w9WgXcQ"


def test_shortened_youtu_be_url() -> None:
    result = parse_youtube_url("https://youtu.be/dQw4w9WgXcQ")
    assert result.video_id == "dQw4w9WgXcQ"
    assert result.embed_url == "https://www.youtube.com/embed/dQw4w9WgXcQ?enablejsapi=1"


def test_shortened_url_with_extra_query_params() -> None:
    result = parse_youtube_url("https://youtu.be/dQw4w9WgXcQ?t=42")
    assert result.video_id == "dQw4w9WgXcQ"


def test_playlist_url() -> None:
    result = parse_youtube_url(
        "https://www.youtube.com/playlist?list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf"
    )
    assert result.video_id is None
    assert result.playlist_id == "PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf"
    assert "videoseries" in result.embed_url
    assert "list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf" in result.embed_url


def test_watch_url_with_playlist_context() -> None:
    result = parse_youtube_url(
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf"
    )
    assert result.video_id == "dQw4w9WgXcQ"
    assert result.playlist_id == "PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf"
    assert "embed/dQw4w9WgXcQ" in result.embed_url
    assert "list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf" in result.embed_url


def test_already_embed_url_is_accepted() -> None:
    result = parse_youtube_url("https://www.youtube.com/embed/dQw4w9WgXcQ")
    assert result.video_id == "dQw4w9WgXcQ"


@pytest.mark.parametrize(
    "url",
    [
        "not a url",
        "ftp://youtube.com/watch?v=dQw4w9WgXcQ",
        "https://example.com/watch?v=dQw4w9WgXcQ",
        "https://youtube.com.evil.com/watch?v=dQw4w9WgXcQ",
        "https://www.youtube.com/",
        "https://www.youtube.com/watch",
        "https://www.youtube.com/watch?v=",
        "https://www.youtube.com/watch?v=<script>",
        "https://www.youtube.com/results?search_query=lofi",
    ],
)
def test_invalid_or_unsupported_urls_raise(url: str) -> None:
    with pytest.raises(YoutubeUrlError):
        parse_youtube_url(url)


def test_empty_string_raises() -> None:
    with pytest.raises(YoutubeUrlError):
        parse_youtube_url("")
