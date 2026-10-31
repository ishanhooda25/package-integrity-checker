import io
import tarfile
import zipfile
from pathlib import Path

import pytest

from checker.download import download_and_unpack, get_sdist_url


def make_tar(path, files):
    with tarfile.open(path, "w:gz") as tar:
        for name, data in files.items():
            info = tarfile.TarInfo(name=name)
            info.size = len(data)
            tar.addfile(info, io.BytesIO(data))


def make_zip(path, files):
    with zipfile.ZipFile(path, "w") as archive:
        for name, data in files.items():
            archive.writestr(name, data)


def test_get_sdist_url_finds_sdist():
    info = {"urls": [
        {"packagetype": "bdist_wheel", "url": "wheel-link"},
        {"packagetype": "sdist", "url": "sdist-link"},
    ]}
    assert get_sdist_url(info) == "sdist-link"


def test_get_sdist_url_returns_none_without_sdist():
    info = {"urls": [{"packagetype": "bdist_wheel", "url": "wheel-link"}]}
    assert get_sdist_url(info) is None


def test_unpack_tar_gz(tmp_path):
    archive = tmp_path / "pkg-1.0.tar.gz"
    make_tar(archive, {"pkg-1.0/a.txt": b"hello"})
    result = Path(download_and_unpack(archive.as_uri(), str(tmp_path / "out")))
    assert result.name == "pkg-1.0"
    assert (result / "a.txt").read_text() == "hello"


def test_unpack_zip(tmp_path):
    archive = tmp_path / "pkg-1.0.zip"
    make_zip(archive, {"pkg-1.0/a.txt": b"hello"})
    result = Path(download_and_unpack(archive.as_uri(), str(tmp_path / "out")))
    assert (result / "a.txt").read_text() == "hello"


def test_tar_with_dotdot_is_rejected(tmp_path):
    archive = tmp_path / "bad.tar.gz"
    make_tar(archive, {"../evil.txt": b"bad"})
    with pytest.raises(ValueError):
        download_and_unpack(archive.as_uri(), str(tmp_path / "out"))
    assert not (tmp_path / "out" / "evil.txt").exists()


def test_zip_with_dotdot_is_rejected(tmp_path):
    archive = tmp_path / "bad.zip"
    make_zip(archive, {"../evil.txt": b"bad"})
    with pytest.raises(ValueError):
        download_and_unpack(archive.as_uri(), str(tmp_path / "out"))
    assert not (tmp_path / "out" / "evil.txt").exists()


def test_tar_with_absolute_path_is_rejected(tmp_path):
    archive = tmp_path / "bad.tar.gz"
    make_tar(archive, {"/abs.txt": b"bad"})
    with pytest.raises(ValueError):
        download_and_unpack(archive.as_uri(), str(tmp_path / "out"))


def test_unsupported_archive_type_is_rejected(tmp_path):
    archive = tmp_path / "pkg.exe"
    archive.write_bytes(b"not an archive")
    with pytest.raises(ValueError):
        download_and_unpack(archive.as_uri(), str(tmp_path / "out"))
