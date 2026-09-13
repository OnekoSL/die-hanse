"""Collect installed dependency notices for the Windows distribution.
Run with the backend Python environment after npm ci and cargo metadata.
"""
from pathlib import Path
import importlib.metadata as metadata
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
parts = ["Die Hanse — Third-party notices\n\nThese libraries retain their own licenses. "
         "This inventory also includes build/development dependencies.\n"]
missing = []

def include(name, version, license_name, paths):
    parts.append(f"\n{'=' * 72}\n{name} {version}\nLicense: {license_name}\n")
    found = False
    for path in sorted(set(paths)):
        if path.is_file():
            try:
                content = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                content = path.read_text(encoding="latin1")
            parts.append(f"\n--- {path.name} ---\n{content}\n")
            found = True
    if not found:
        fallback = ROOT / "licenses/third-party" / (name.replace("/", "_") + "-" + version + ".txt")
        if fallback.exists():
            parts.append(fallback.read_text(encoding="utf-8"))
        else:
            missing.append((name, version, license_name))


def notices(directory):
    result = []
    for path in directory.iterdir():
        if path.is_file() and path.name.lower().startswith(("license", "licence", "copying", "notice", "copyright")):
            result.append(path)
        elif path.is_dir() and path.name.lower() in {"licenses", "license"}:
            result.extend(p for p in path.rglob("*") if p.is_file())
    return result

for dist in sorted(metadata.distributions(), key=lambda d: d.metadata["Name"].lower()):
    paths = [Path(dist.locate_file(f)) for f in dist.files or []
             if any(part.lower().startswith(("license", "licence", "copying", "notice")) for part in Path(str(f)).parts)]
    include(dist.metadata["Name"], dist.version,
            dist.metadata.get("License-Expression") or dist.metadata.get("License", "See notice"), paths)

include("CPython", sys.version.split()[0], "PSF-2.0 and bundled component licenses", notices(Path(sys.base_prefix)))

for relative in ["web_ui/frontend", "lokal_exe"]:
    folder = ROOT / relative
    lock = json.loads((folder / "package-lock.json").read_text(encoding="utf-8"))
    for name, item in sorted(lock["packages"].items()):
        if not name or item.get("dev"):
            continue
        directory = folder / name
        if directory.exists():
            include(name.rsplit("node_modules/", 1)[-1], item.get("version", ""),
                    item.get("license", "See notice"), notices(directory))

cargo = json.loads((ROOT / "local/cargo-metadata.json").read_text(encoding="utf-8-sig"))
resolved = {node["id"] for node in cargo["resolve"]["nodes"]}
for package in sorted(cargo["packages"], key=lambda p: (p["name"], p["version"])):
    if package["id"] not in resolved or not package["source"]:
        continue
    directory = Path(package["manifest_path"]).parent
    paths = notices(directory)
    if package.get("license_file"):
        paths.append(directory / package["license_file"])
    parts.append(f"Source (unchanged): https://static.crates.io/crates/{package['name']}/{package['name']}-{package['version']}.crate\n")
    include(package["name"], package["version"], package.get("license", "See notice"), paths)

for extra in sorted(list((ROOT / "licenses/third-party").glob("victory-*-LICENSE.txt")) + list((ROOT / "licenses/third-party").glob("Rust-*-COPYRIGHT-library.html"))):
    parts.append(extra.read_text(encoding="utf-8"))
parts.append("\nUnmodified MPL components: source archives are available next to this release in dependency-sources.zip.\nThe MPL rights to those components are independent of Die Hanse's own noncommercial license.\nhttps://github.com/OnekoSL/die-hanse/releases/tag/v0.1.0-alpha.1\n")
(ROOT / "THIRD-PARTY-NOTICES.txt").write_text("\n".join(parts), encoding="utf-8")
(ROOT / "local/missing-notices.json").write_text(json.dumps(missing, indent=2), encoding="utf-8")
print(f"Notice file: {(ROOT / 'THIRD-PARTY-NOTICES.txt').stat().st_size} bytes")
print("Components without bundled notice:", json.dumps(missing))
