"""How the page and its files are cached, and the headers the page carries.

The page itself is never cached, and every link it makes to its own script or
stylesheet carries a stamp of the static files' contents. A browser therefore
keeps each file for a year, and fetches a new one the moment an upgrade
changes it, instead of running an old script against a new page.

The page loads nothing inline, so its content security policy allows scripts,
styles and requests from this server only, and images also from the data and
blob addresses the previews use.
"""

import hashlib
import re
from pathlib import Path
from typing import Final

from starlette.responses import Response
from starlette.staticfiles import StaticFiles
from starlette.types import Scope

STAMP_LENGTH: Final = 12
ASSET_LINK: Final = re.compile(r'(?<=["\'])(/static/[\w.-]+\.(?:css|js))(?=["\'])')
PAGE_CACHE: Final = "no-store"
ASSET_CACHE: Final = "public, max-age=31536000, immutable"
CONTENT_SECURITY_POLICY: Final = (
    "default-src 'self'; script-src 'self'; style-src 'self'; "
    "img-src 'self' data: blob:; connect-src 'self'; object-src 'none'; "
    "base-uri 'none'; form-action 'self'; frame-ancestors 'none'"
)
PAGE_HEADERS: Final = {
    "Cache-Control": PAGE_CACHE,
    "Content-Security-Policy": CONTENT_SECURITY_POLICY,
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "no-referrer",
}


def asset_stamp(directory: Path) -> str:
    """A short digest of every file in the directory, names and contents alike."""
    digest = hashlib.sha256()
    for path in sorted(item for item in directory.rglob("*") if item.is_file()):
        digest.update(path.relative_to(directory).as_posix().encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()[:STAMP_LENGTH]


def stamped(markup: str, stamp: str) -> str:
    """The markup with every link to a local script or stylesheet stamped."""
    return ASSET_LINK.sub(lambda match: f"{match.group(1)}?v={stamp}", markup)


class CachedStaticFiles(StaticFiles):
    """Static files a browser may keep for a year, since their links are stamped."""

    async def get_response(self, path: str, scope: Scope) -> Response:
        """Serve the file, marked as safe to cache for a year."""
        response = await super().get_response(path, scope)
        response.headers["Cache-Control"] = ASSET_CACHE
        response.headers["X-Content-Type-Options"] = "nosniff"
        return response
