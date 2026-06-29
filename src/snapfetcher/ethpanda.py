from __future__ import annotations

from email.utils import parsedate_to_datetime
import json
from typing import Callable
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen

from .publicnode import Snapshot, SnapshotFetchError

ETHPANDA_BASE_URL = "https://snapshots.ethpandaops.io"
ETHPANDA_NETWORKS = (
    "mainnet",
    "sepolia",
    "hoodi",
    "holesky",
    "perf-devnet-2",
    "perf-devnet-3",
)
ETHPANDA_CLIENTS = ("besu", "erigon", "geth", "nethermind", "reth")
USER_AGENT = "snapfetcher/0.1 (+https://ethpandaops.io/data/snapshots/)"

FetchText = Callable[[str, float], str]
FetchHeaders = Callable[[str, float], dict[str, str]]


def is_ethereum_chain(chain: str | None) -> bool:
    return _norm(chain) in {"ethereum", "eth"}


def is_ethereum_snapshot(snapshot: Snapshot) -> bool:
    return is_ethereum_chain(snapshot.currency_id) or is_ethereum_chain(snapshot.currency_name)


def fetch_ethpanda_snapshots(
    *,
    network: str | None = None,
    client: str | None = None,
    timeout: float = 30.0,
) -> list[Snapshot]:
    networks = _select_supported(ETHPANDA_NETWORKS, network, "network")
    clients = _select_supported(ETHPANDA_CLIENTS, client, "client")

    snapshots: list[Snapshot] = []
    for network_name in networks:
        for client_id in clients:
            snapshots.append(fetch_ethpanda_snapshot(network_name, client_id, timeout=timeout))

    return sorted(snapshots, key=lambda snapshot: (snapshot.network_name, snapshot.client_id or ""))


def fetch_ethpanda_snapshot(
    network: str,
    client: str,
    *,
    timeout: float = 30.0,
    fetch_text: FetchText | None = None,
    fetch_headers: FetchHeaders | None = None,
) -> Snapshot:
    fetch_text = fetch_text or _fetch_text
    fetch_headers = fetch_headers or _fetch_headers

    network = _norm(network)
    client = _norm(client)
    latest_url = _ethpanda_url(network, client, "latest")
    latest_value = fetch_text(latest_url, timeout).strip()
    try:
        block_number = int(latest_value)
    except ValueError as exc:
        raise SnapshotFetchError(
            f"EthPandaOps returned an invalid latest block for {network}/{client}: {latest_value}"
        ) from exc

    snapshot_url = _ethpanda_url(network, client, str(block_number), "snapshot.tar.zst")
    headers = fetch_headers(snapshot_url, timeout)
    compressed_bytes = _optional_int(headers.get("content-length"))
    uploaded_at = _http_date_to_iso(headers.get("last-modified"))
    node_version = _fetch_client_version(network, client, block_number, timeout, fetch_text)

    return Snapshot(
        currency_id="ethereum",
        currency_name="Ethereum",
        network_name=network,
        snapshot_name=f"ethereum-{network}-{client}",
        client_id=client,
        snapshot_type="full",
        block_heights=(block_number,),
        compressed_bytes=compressed_bytes,
        uncompressed_bytes=None,
        node_version=node_version,
        url=snapshot_url,
        permanent_url_pathname=f"{network}/{client}/latest",
        timestamp=None,
        created_at=None,
        uploaded_at=uploaded_at,
        metadata=(("source", "ethpandaops"),),
        schedule=None,
        locations=(),
        is_outdated=False,
        is_pruned=False,
        is_archive=False,
        source="ethpandaops",
    )


def _fetch_client_version(
    network: str,
    client: str,
    block_number: int,
    timeout: float,
    fetch_text: FetchText,
) -> str | None:
    url = _ethpanda_url(
        network,
        client,
        str(block_number),
        "_snapshot_web3_clientVersion.json",
    )
    try:
        payload = json.loads(fetch_text(url, timeout))
    except (SnapshotFetchError, json.JSONDecodeError):
        return None

    result = payload.get("result") if isinstance(payload, dict) else None
    return str(result) if result else None


def _ethpanda_url(*parts: str) -> str:
    path = "/".join(part.strip("/") for part in parts)
    return urljoin(ETHPANDA_BASE_URL + "/", path)


def _select_supported(
    supported: tuple[str, ...],
    value: str | None,
    label: str,
) -> tuple[str, ...]:
    if value is None:
        return supported

    normalized = _norm(value)
    if normalized not in supported:
        raise SnapshotFetchError(
            f"EthPandaOps does not expose Ethereum {label} '{value}'. "
            f"Supported {label}s: {', '.join(supported)}"
        )
    return (normalized,)


def _fetch_text(url: str, timeout: float) -> str:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urlopen(request, timeout=timeout) as response:
            charset = response.headers.get_content_charset() or "utf-8"
            return response.read().decode(charset, errors="replace")
    except HTTPError as exc:
        raise SnapshotFetchError(f"EthPandaOps request failed with HTTP {exc.code}: {url}") from exc
    except URLError as exc:
        raise SnapshotFetchError(f"EthPandaOps request failed: {exc.reason}") from exc
    except TimeoutError as exc:
        raise SnapshotFetchError(f"EthPandaOps request timed out: {url}") from exc


def _fetch_headers(url: str, timeout: float) -> dict[str, str]:
    request = Request(url, headers={"User-Agent": USER_AGENT}, method="HEAD")
    try:
        with urlopen(request, timeout=timeout) as response:
            return {key.casefold(): value for key, value in response.headers.items()}
    except HTTPError as exc:
        raise SnapshotFetchError(f"EthPandaOps request failed with HTTP {exc.code}: {url}") from exc
    except URLError as exc:
        raise SnapshotFetchError(f"EthPandaOps request failed: {exc.reason}") from exc
    except TimeoutError as exc:
        raise SnapshotFetchError(f"EthPandaOps request timed out: {url}") from exc


def _http_date_to_iso(value: str | None) -> str | None:
    if not value:
        return None

    try:
        parsed = parsedate_to_datetime(value)
    except (TypeError, ValueError):
        return value

    return parsed.isoformat()


def _optional_int(value: str | None) -> int | None:
    if value is None:
        return None
    return int(value)


def _norm(value: str | None) -> str:
    return (value or "").strip().casefold()
