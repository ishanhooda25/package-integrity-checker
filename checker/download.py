import json
import os
import tarfile
import urllib.request
import zipfile


def get_pypi_info(name, version):
    """Ask PyPI about one package version and return the answer as a dictionary."""
    url = f"https://pypi.org/pypi/{name}/{version}/json"
    with urllib.request.urlopen(url, timeout=30) as response:
        return json.load(response)


def get_sdist_url(info):
    """Return the download link of the source archive (sdist), or None."""
    for entry in info.get("urls", []):
        if entry.get("packagetype") == "sdist":
            return entry["url"]
    return None


def _is_safe_path(name):
    """A path is unsafe if it is absolute, starts with a drive letter, or contains '..'."""
    name = name.replace("\\", "/")
    if name.startswith("/"):
        return False
    if len(name) > 1 and name[1] == ":":
        return False
    return ".." not in name.split("/")


def _check_names(names):
    """Stop with an error if any file name inside an archive is unsafe."""
    for name in names:
        if not _is_safe_path(name):
            raise ValueError(f"Unsafe path in archive: {name}")


def download_and_unpack(url, folder):
    """Download an archive into folder, unpack it safely, return the unpacked top folder."""
    os.makedirs(folder, exist_ok=True)
    filename = url.split("?")[0].rstrip("/").split("/")[-1]
    archive_path = os.path.join(folder, filename)
    urllib.request.urlretrieve(url, archive_path)

    extract_dir = os.path.join(folder, "extracted")
    os.makedirs(extract_dir, exist_ok=True)

    if filename.endswith((".tar.gz", ".tgz")):
        with tarfile.open(archive_path) as tar:
            members = tar.getmembers()
            _check_names([m.name for m in members])
            for m in members:
                # Links and device files can point outside the folder, so reject them.
                if m.issym() or m.islnk() or m.isdev():
                    raise ValueError(f"Unsafe file type in archive: {m.name}")
            tar.extractall(extract_dir, filter="data")
    elif filename.endswith(".zip"):
        with zipfile.ZipFile(archive_path) as archive:
            _check_names(archive.namelist())
            archive.extractall(extract_dir)
    else:
        raise ValueError(f"Unsupported archive type: {filename}")

    # Normal source archives contain exactly one top-level folder.
    entries = os.listdir(extract_dir)
    if len(entries) == 1 and os.path.isdir(os.path.join(extract_dir, entries[0])):
        return os.path.join(extract_dir, entries[0])
    return extract_dir
