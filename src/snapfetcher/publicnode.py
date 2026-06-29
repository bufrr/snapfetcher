from __future__ import annotations

from dataclasses import dataclass
import json
import re
from typing import Any, Iterable
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen

PUBLICNODE_BASE_URL = "https://www.publicnode.com"
PUBLICNODE_SNAPSHOTS_PATH = "/snapshots"
USER_AGENT = "snapfetcher/0.1 (+https://www.publicnode.com/snapshots)"


class SnapshotFetchError(RuntimeError):
    """Raised when PublicNode snapshot data cannot be fetched or parsed."""


@dataclass(frozen=True)
class Snapshot:
    currency_id: str
    currency_name: str
    network_name: str
    snapshot_name: str
    client_id: str | None
    snapshot_type: str
    block_heights: tuple[int, ...] | None
    compressed_bytes: int | None
    uncompressed_bytes: int | None
    node_version: str | None
    url: str
    permanent_url_pathname: str | None
    timestamp: str | None
    created_at: str | None
    uploaded_at: str | None
    metadata: tuple[tuple[str, Any], ...]
    schedule: str | None
    locations: tuple[str, ...]
    is_outdated: bool
    is_pruned: bool
    is_archive: bool

    @classmethod
    def from_publicnode(cls, item: dict[str, Any]) -> "Snapshot":
        size = item.get("size") or {}
        block_heights = item.get("blockHeights")
        metadata = item.get("metadata") or []
        locations = item.get("locations") or []

        return cls(
            currency_id=str(item.get("currencyId") or ""),
            currency_name=str(item.get("currencyName") or ""),
            network_name=str(item.get("networkName") or ""),
            snapshot_name=str(item.get("snapshotName") or ""),
            client_id=_optional_str(item.get("clientId")),
            snapshot_type=str(item.get("type") or ""),
            block_heights=tuple(block_heights) if isinstance(block_heights, list) else None,
            compressed_bytes=_optional_int(size.get("compressed")),
            uncompressed_bytes=_optional_int(size.get("uncompressed")),
            node_version=_optional_str(item.get("nodeVersion")),
            url=str(item.get("url") or ""),
            permanent_url_pathname=_optional_str(item.get("permanentUrlPathname")),
            timestamp=_optional_str(item.get("timestamp")),
            created_at=_optional_str(item.get("createdAt")),
            uploaded_at=_optional_str(item.get("uploadedAt")),
            metadata=tuple(
                (str(entry.get("key")), entry.get("value"))
                for entry in metadata
                if isinstance(entry, dict) and entry.get("key") is not None
            ),
            schedule=_optional_str(item.get("schedule")),
            locations=tuple(str(location) for location in locations),
            is_outdated=bool(item.get("isOutdated")),
            is_pruned=bool(item.get("isPruned")),
            is_archive=bool(item.get("isArchive")),
        )

    @property
    def height_label(self) -> str:
        if not self.block_heights:
            return "-"
        return "-".join(str(height) for height in self.block_heights)

    @property
    def compressed_size_label(self) -> str:
        return _format_bytes(self.compressed_bytes)


@dataclass(frozen=True)
class ChainSummary:
    currency_id: str
    currency_name: str
    snapshot_count: int
    networks: tuple[str, ...]
    clients: tuple[str, ...]


def fetch_publicnode_snapshots(
    base_url: str = PUBLICNODE_BASE_URL,
    timeout: float = 30.0,
) -> list[Snapshot]:
    """Fetch and parse PublicNode snapshots from the current Next.js data JSON."""

    html = _fetch_text(urljoin(base_url, PUBLICNODE_SNAPSHOTS_PATH), timeout)
    build_id = discover_build_id(html)
    data_url = urljoin(base_url, f"/_next/data/{build_id}/snapshots.json")
    payload = _fetch_json(data_url, timeout)
    return extract_snapshots(payload)


def discover_build_id(html: str) -> str:
    """Return the current Next.js build ID embedded in the snapshots page."""

    json_match = re.search(r'"buildId"\s*:\s*"([^"]+)"', html)
    if json_match:
        return json_match.group(1)

    asset_match = re.search(r"/_next/static/([^/]+)/_buildManifest\.js", html)
    if asset_match:
        return asset_match.group(1)

    raise SnapshotFetchError("Could not discover PublicNode Next.js build ID")


def extract_snapshots(payload: dict[str, Any]) -> list[Snapshot]:
    values = payload.get("pageProps", {}).get("values", {})
    if not isinstance(values, dict):
        raise SnapshotFetchError("PublicNode payload does not contain pageProps.values")

    for key, value in values.items():
        if not key.endswith("$data") or not isinstance(value, list):
            continue
        if value and all(isinstance(item, dict) and "url" in item for item in value):
            return [Snapshot.from_publicnode(item) for item in value if item.get("url")]

    raise SnapshotFetchError("PublicNode payload did not include a snapshot list")


def find_snapshots(
    snapshots: Iterable[Snapshot],
    *,
    chain: str = "ethereum",
    network: str | None = None,
    client: str | None = None,
    snapshot_type: str | None = None,
    include_outdated: bool = False,
    archive: bool | None = None,
    pruned: bool | None = None,
) -> list[Snapshot]:
    chain_key = _norm(chain)
    network_key = _norm(network) if network else None
    client_key = _norm(client) if client else None
    type_key = _norm(snapshot_type) if snapshot_type else None

    matches: list[Snapshot] = []
    for snapshot in snapshots:
        if not include_outdated and snapshot.is_outdated:
            continue
        if archive is not None and snapshot.is_archive != archive:
            continue
        if pruned is not None and snapshot.is_pruned != pruned:
            continue
        if type_key and _norm(snapshot.snapshot_type) != type_key:
            continue
        if not _matches_chain(snapshot, chain_key):
            continue
        if network_key and _norm(snapshot.network_name) != network_key:
            continue
        if client_key and not _matches_client(snapshot, client_key):
            continue
        matches.append(snapshot)

    return sorted(matches, key=_sort_key)


def list_chains(
    snapshots: Iterable[Snapshot],
    *,
    include_outdated: bool = False,
) -> list[ChainSummary]:
    by_chain: dict[str, dict[str, Any]] = {}
    for snapshot in snapshots:
        if not include_outdated and snapshot.is_outdated:
            continue

        chain_key = _norm(snapshot.currency_id)
        if chain_key not in by_chain:
            by_chain[chain_key] = {
                "currency_id": snapshot.currency_id,
                "currency_name": snapshot.currency_name,
                "snapshot_count": 0,
                "networks": set(),
                "clients": set(),
            }

        entry = by_chain[chain_key]
        entry["snapshot_count"] += 1
        entry["networks"].add(snapshot.network_name)
        if snapshot.client_id:
            entry["clients"].add(snapshot.client_id)

    return [
        ChainSummary(
            currency_id=entry["currency_id"],
            currency_name=entry["currency_name"],
            snapshot_count=entry["snapshot_count"],
            networks=tuple(sorted(entry["networks"], key=_norm)),
            clients=tuple(sorted(entry["clients"], key=_norm)),
        )
        for entry in sorted(by_chain.values(), key=lambda item: _norm(item["currency_name"]))
    ]


def _matches_chain(snapshot: Snapshot, chain_key: str) -> bool:
    return chain_key in {
        _norm(snapshot.currency_id),
        _norm(snapshot.currency_name),
    }


def _matches_client(snapshot: Snapshot, client_key: str) -> bool:
    if snapshot.client_id and _norm(snapshot.client_id) == client_key:
        return True
    return _norm(snapshot.snapshot_name).endswith(f"-{client_key}")


def _sort_key(snapshot: Snapshot) -> tuple[int, int, str]:
    type_rank = {"base": 0, "part": 1, "full": 2}.get(_norm(snapshot.snapshot_type), 3)
    end_height = snapshot.block_heights[-1] if snapshot.block_heights else -1
    return type_rank, end_height, snapshot.url


def _fetch_json(url: str, timeout: float) -> dict[str, Any]:
    text = _fetch_text(url, timeout)
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise SnapshotFetchError(f"PublicNode returned invalid JSON from {url}") from exc
    if not isinstance(data, dict):
        raise SnapshotFetchError(f"PublicNode returned unexpected JSON from {url}")
    return data


def _fetch_text(url: str, timeout: float) -> str:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urlopen(request, timeout=timeout) as response:
            charset = response.headers.get_content_charset() or "utf-8"
            return response.read().decode(charset, errors="replace")
    except HTTPError as exc:
        raise SnapshotFetchError(f"PublicNode request failed with HTTP {exc.code}: {url}") from exc
    except URLError as exc:
        raise SnapshotFetchError(f"PublicNode request failed: {exc.reason}") from exc
    except TimeoutError as exc:
        raise SnapshotFetchError(f"PublicNode request timed out: {url}") from exc


def _optional_int(value: Any) -> int | None:
    if value is None:
        return None
    return int(value)


def _optional_str(value: Any) -> str | None:
    if value is None:
        return None
    return str(value)


def _norm(value: str | None) -> str:
    return (value or "").strip().casefold()


def _format_bytes(value: int | None) -> str:
    if value is None:
        return "-"

    units = ("B", "KB", "MB", "GB", "TB", "PB")
    size = float(value)
    for unit in units:
        if size < 1024 or unit == units[-1]:
            if unit == "B":
                return f"{int(size)} {unit}"
            return f"{size:.1f} {unit}"
        size /= 1024
