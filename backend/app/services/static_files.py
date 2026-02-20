from __future__ import annotations

from email.utils import formatdate
from pathlib import Path
from urllib.parse import parse_qs, quote

from fastapi.staticfiles import StaticFiles


class UploadsStaticFiles(StaticFiles):
    """Static file handler that adds ETag, cache, and download headers."""

    async def get_response(self, path: str, scope):
        response = await super().get_response(path, scope)
        if response.status_code == 404:
            return response

        query_params = {}
        if scope:
            raw_qs = scope.get("query_string") or b""
            if raw_qs:
                try:
                    query_params = parse_qs(raw_qs.decode("utf-8", errors="ignore"))
                except Exception:
                    query_params = {}

        try:
            full_path, stat_result = await self.lookup_path(path)
        except Exception:
            full_path = None
            stat_result = None

        if full_path and stat_result:
            etag = f"\"{stat_result.st_mtime_ns:x}-{stat_result.st_size:x}\""
            response.headers["Cache-Control"] = "no-store, max-age=0"
            response.headers["ETag"] = etag
            response.headers["Last-Modified"] = formatdate(stat_result.st_mtime, usegmt=True)
            if query_params.get("download"):
                filename = Path(full_path).name
                quoted = quote(filename)
                response.headers[
                    "Content-Disposition"
                ] = f'attachment; filename="{filename}"; filename*=UTF-8\'\'{quoted}'

        return response
