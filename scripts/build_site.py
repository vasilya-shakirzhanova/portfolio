"""Validate and copy the existing static portfolio for GitHub Pages or Sites."""

from html.parser import HTMLParser
from pathlib import Path
import re
import shutil
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "dist"


class Page(HTMLParser):
    def __init__(self, path):
        super().__init__(convert_charrefs=True)
        self.path = path
        self.ids = set()
        self.links = []
        self.feed(path.read_text(encoding="utf-8"))

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            if attrs["id"] in self.ids:
                raise ValueError(f"{self.path.name}: duplicate id {attrs['id']}")
            self.ids.add(attrs["id"])
        for name in ("href", "src", "data-lightbox"):
            if attrs.get(name):
                self.links.append(attrs[name])
        if tag == "meta" and attrs.get("http-equiv", "").lower() == "refresh":
            match = re.search(r"url\s*=\s*(.+)", attrs.get("content", ""), re.I)
            if match:
                self.links.append(match.group(1).strip())


def validate_link(value, source, pages):
    url = urlsplit(value)
    if url.scheme or url.netloc:
        if url.hostname in ("localhost", "127.0.0.1"):
            raise ValueError(f"{source.name}: local preview URL in published content")
        return
    if url.path.startswith("/"):
        raise ValueError(f"{source.name}: root-relative URL breaks /portfolio/: {value}")
    target = (source.parent / unquote(url.path)).resolve() if url.path else source
    if not target.is_relative_to(ROOT) or not target.is_file():
        raise ValueError(f"{source.name}: missing or external local file: {value}")
    if url.fragment and target in pages and unquote(url.fragment) not in pages[target].ids:
        raise ValueError(f"{source.name}: missing anchor: {value}")


def build():
    pages = {p.resolve(): Page(p.resolve()) for p in sorted(ROOT.glob("*.html"))}
    if ROOT / "index.html" not in pages:
        raise ValueError("index.html is required")
    for path, page in pages.items():
        for link in page.links:
            validate_link(link, path, pages)
    stylesheet = ROOT / "styles.css"
    for match in re.finditer(r"url\(\s*['\"]?([^)'\"\s]+)", stylesheet.read_text()):
        validate_link(match.group(1), stylesheet, pages)
    assets = sorted(p for p in (ROOT / "assets").rglob("*") if p.is_file())
    if any(p.is_symlink() for p in (ROOT / "assets").rglob("*")):
        raise ValueError("Deployment assets must be regular files, not symbolic links")
    source_files = [*pages, stylesheet, ROOT / "script.js", ROOT / ".nojekyll", *assets]
    # Preserve existing local files; only update the corresponding build copies.
    OUTPUT.mkdir(exist_ok=True)
    for source in source_files:
        destination = OUTPUT / source.relative_to(ROOT)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
    expected = {p.relative_to(ROOT).as_posix() for p in source_files}
    actual = {p.relative_to(OUTPUT).as_posix() for p in OUTPUT.rglob("*") if p.is_file()}
    if extra := actual - expected:
        raise ValueError(f"Unexpected files in dist; review them before publishing: {sorted(extra)}")
    for source in source_files:
        if source.read_bytes() != (OUTPUT / source.relative_to(ROOT)).read_bytes():
            raise ValueError(f"Build copy differs from source: {source.name}")
    print(f"Ready: {len(pages)} HTML pages, {len(assets)} assets; all local links and anchors validated.")
    print("Output: dist/ (relative URLs work under /portfolio/ and at the site root).")


if __name__ == "__main__":
    build()
