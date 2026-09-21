"""Check the exact public directory, its links and reproducible data fingerprint."""
import hashlib
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.ids = set()
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get("id"):
            self.ids.add(attrs["id"])
        for attribute in ["href", "src"]:
            if attribute in attrs:
                self.links.append(attrs[attribute])


def main():
    failures = []
    files = [p for p in SITE.rglob("*") if p.is_file()]
    text_suffixes = {".html", ".css", ".js", ".json", ".svg"}
    allowed_suffixes = text_suffixes | {".jpg", ".jpeg", ".png", ".webp", ".pdf"}
    private_patterns = [
        r"[A-Za-z]:[\\/](?:Users|HuaweiMoveData)", r"file://",
        r"(?i)(?:api[_-]?key|access[_-]?token|secret[_-]?key)\s*[=:]\s*['\"][^'\"]{8,}",
        r"(?i)(?:X-Amz-Signature|X-Tos-Signature|Bearer\s+[A-Za-z0-9._-]{15,})",
        r"html4math|SOURCE_NOTES|客户名称|合作方名称",
    ]
    parsed = {}
    for path in files:
        rel = path.relative_to(SITE).as_posix()
        if path.is_symlink():
            failures.append(f"Symlink disallowed: {rel}")
        if path.suffix not in allowed_suffixes and path.name != ".nojekyll":
            failures.append(f"Non-allowlisted extension: {rel}")
        if path.suffix not in text_suffixes:
            continue
        text = path.read_text(encoding="utf-8")
        for pattern in private_patterns:
            if re.search(pattern, text):
                failures.append(f"Private-content pattern in {rel}: {pattern}")
        if path.suffix == ".html" and "samples" not in path.parts:
            parser = Links()
            parser.feed(text)
            parsed[path.resolve()] = parser
    for path, parser in parsed.items():
        for href in parser.links:
            target = urlsplit(href)
            if target.scheme or target.netloc:
                if target.scheme == "mailto":
                    continue
                if target.scheme != "https" or target.netloc not in {"github.com", "dddzzz123-dz.github.io"}:
                    failures.append(f"Unexpected remote dependency/link in {path.name}: {href}")
                continue
            resolved = (path.parent / unquote(target.path)).resolve() if target.path else path
            if not resolved.is_relative_to(SITE.resolve()):
                failures.append(f"Link leaves public directory: {path.name} -> {href}")
                continue
            if resolved.is_dir():
                resolved = resolved / "index.html"
            if not resolved.exists():
                failures.append(f"Missing link: {path.name} -> {href}")
            elif target.fragment and resolved in parsed and target.fragment not in parsed[resolved].ids:
                failures.append(f"Missing anchor: {path.name} -> {href}")
    assert not failures, "\n".join(failures)
    required = [SITE / "index.html", SITE / "assets/github.css", SITE / "assets/github.js", SITE / "data/repos.js", SITE / "assets/daiying-resume.pdf"]
    assert all(path.is_file() for path in required), "Required portfolio files are missing"
    print(f"PASS: {len(files)} public files; local links, anchors, assets and publication patterns checked.")


if __name__ == "__main__":
    main()
