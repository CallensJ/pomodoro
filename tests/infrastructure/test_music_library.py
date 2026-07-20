from src.infrastructure.music_library import scan_mp3_files


def test_scans_only_mp3_files(tmp_path) -> None:
    (tmp_path / "song.mp3").write_bytes(b"")
    (tmp_path / "notes.txt").write_bytes(b"")
    (tmp_path / "cover.jpg").write_bytes(b"")

    result = scan_mp3_files(tmp_path)

    assert [p.name for p in result] == ["song.mp3"]


def test_scan_is_case_insensitive_on_extension(tmp_path) -> None:
    (tmp_path / "a.MP3").write_bytes(b"")
    (tmp_path / "b.Mp3").write_bytes(b"")

    result = scan_mp3_files(tmp_path)

    assert [p.name for p in result] == ["a.MP3", "b.Mp3"]


def test_scan_sorts_files_alphabetically(tmp_path) -> None:
    (tmp_path / "charlie.mp3").write_bytes(b"")
    (tmp_path / "alpha.mp3").write_bytes(b"")
    (tmp_path / "Bravo.mp3").write_bytes(b"")

    result = scan_mp3_files(tmp_path)

    assert [p.name for p in result] == ["alpha.mp3", "Bravo.mp3", "charlie.mp3"]


def test_scan_is_not_recursive(tmp_path) -> None:
    subfolder = tmp_path / "subfolder"
    subfolder.mkdir()
    (subfolder / "nested.mp3").write_bytes(b"")
    (tmp_path / "top.mp3").write_bytes(b"")

    result = scan_mp3_files(tmp_path)

    assert [p.name for p in result] == ["top.mp3"]


def test_scan_returns_empty_list_for_folder_with_no_mp3_files(tmp_path) -> None:
    (tmp_path / "notes.txt").write_bytes(b"")

    assert scan_mp3_files(tmp_path) == []


def test_scan_returns_empty_list_for_nonexistent_folder(tmp_path) -> None:
    assert scan_mp3_files(tmp_path / "does-not-exist") == []
