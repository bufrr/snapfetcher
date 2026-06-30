from __future__ import annotations

from dataclasses import dataclass
from email.utils import parsedate_to_datetime
from html import unescape
import re
from typing import Callable
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen

from .publicnode import ChainSummary, Snapshot, SnapshotFetchError

POLKACHU_INDEX_URL = "https://www.polkachu.com/tendermint_snapshots"
KJNODES_INDEX_URL = "https://services.kjnodes.com/"
LAVENDER_TOOLS_URL = "https://www.lavenderfive.com/tools"
USER_AGENT = "snapfetcher/0.1 (+https://github.com/bufrr/snapfetcher)"

FetchText = Callable[[str, float], str]
FetchHeaders = Callable[[str, float], dict[str, str]]

CHAIN_ALIASES = {
    "cosmos": "cosmoshub",
    "cosmoshub": "cosmoshub",
    "cosmoshub4": "cosmoshub",
    "fetch": "fetchhub",
    "fetchai": "fetchhub",
    "terra": "terra2",
    "secret": "secretnetwork",
    "secretnetwork": "secretnetwork",
    "omniflix": "omniflixhub",
    "omniflixhub": "omniflixhub",
    "0g": "og",
}

DISPLAY_NAMES = {
    "cosmoshub": "Cosmos Hub",
    "fetchhub": "Fetch.ai",
    "secretnetwork": "Secret Network",
    "omniflixhub": "OmniFlix",
    "terra2": "Terra",
    "og": "0G",
}

CURRENCY_IDS = {
    "cosmoshub": "cosmos",
    "fetchhub": "fetch",
    "terra2": "terra",
    "og": "og",
}


@dataclass(frozen=True)
class ExternalChain:
    source: str
    slug: str
    name: str
    network: str
    url: str


def fetch_polkachu_chains(
    *,
    timeout: float = 30.0,
    fetch_text: FetchText | None = None,
) -> list[ExternalChain]:
    html = (fetch_text or _fetch_text)(POLKACHU_INDEX_URL, timeout)
    chains: dict[str, ExternalChain] = {}
    pattern = re.compile(
        r'<a\b[^>]*href="(?P<url>https://www\.polkachu\.com/tendermint_snapshots/'
        r'(?P<slug>[^"/#?]+))"[^>]*>(?P<name>.*?)</a>',
        re.IGNORECASE | re.DOTALL,
    )
    for match in pattern.finditer(html):
        slug = unescape(match.group("slug")).strip()
        name = _clean_html(match.group("name"))
        if not slug or not name:
            continue
        chains.setdefault(
            slug,
            ExternalChain(
                source="polkachu",
                slug=slug,
                name=name,
                network="mainnet",
                url=match.group("url"),
            ),
        )

    if not chains:
        raise SnapshotFetchError("PolkaChu page did not include any snapshot chains")
    return sorted(chains.values(), key=lambda chain: _norm_key(chain.name))


def fetch_polkachu_snapshots(
    *,
    chain: str,
    timeout: float = 30.0,
    chains: list[ExternalChain] | None = None,
    fetch_text: FetchText | None = None,
    fetch_headers: FetchHeaders | None = None,
) -> list[Snapshot]:
    chains = chains or fetch_polkachu_chains(timeout=timeout, fetch_text=fetch_text)
    polkachu_chain = find_external_chain(chains, chain)
    if polkachu_chain is None:
        return []

    html = (fetch_text or _fetch_text)(polkachu_chain.url, timeout)
    return [
        _snapshot_from_detail(
            source="polkachu",
            chain=polkachu_chain,
            html=html,
            url_pattern=r'https://snapshots\.polkachu\.com/snapshots/[^"]+?\.tar\.lz4',
            timeout=timeout,
            fetch_headers=fetch_headers,
            is_pruned=True,
            client_id="tendermint",
        )
    ]


def fetch_kjnodes_chains(
    *,
    timeout: float = 30.0,
    fetch_text: FetchText | None = None,
) -> list[ExternalChain]:
    html = (fetch_text or _fetch_text)(KJNODES_INDEX_URL, timeout)
    chains: dict[tuple[str, str], ExternalChain] = {}
    pattern = re.compile(r'href="(?P<path>/(?P<network>mainnet|testnet)/(?P<slug>[^"/]+)/snapshot/)"')
    for match in pattern.finditer(html):
        slug = match.group("slug")
        network = match.group("network")
        key = (network, slug)
        name = DISPLAY_NAMES.get(slug) or slug.replace("-", " ").title()
        chains.setdefault(
            key,
            ExternalChain(
                source="kjnodes",
                slug=slug,
                name=name,
                network=network,
                url=urljoin(KJNODES_INDEX_URL, match.group("path")),
            ),
        )

    if not chains:
        raise SnapshotFetchError("KJNodes page did not include any snapshot chains")
    return sorted(chains.values(), key=lambda chain: (_norm_key(chain.name), chain.network))


def fetch_kjnodes_snapshots(
    *,
    chain: str,
    network: str | None = None,
    timeout: float = 30.0,
    chains: list[ExternalChain] | None = None,
    fetch_text: FetchText | None = None,
    fetch_headers: FetchHeaders | None = None,
) -> list[Snapshot]:
    chains = chains or fetch_kjnodes_chains(timeout=timeout, fetch_text=fetch_text)
    matches = [
        item
        for item in chains
        if _matches_chain(item, chain) and (network is None or _norm_key(item.network) == _norm_key(network))
    ]
    snapshots = []
    for item in matches:
        html = (fetch_text or _fetch_text)(item.url, timeout)
        snapshots.append(
            _snapshot_from_detail(
                source="kjnodes",
                chain=item,
                html=html,
                url_pattern=r'https://snapshots\.kjnodes\.com/[^"]+?snapshot_latest\.tar\.lz4',
                timeout=timeout,
                fetch_headers=fetch_headers,
                is_pruned=True,
                client_id="tendermint",
            )
        )
    return snapshots


def fetch_lavender_chains(
    *,
    timeout: float = 30.0,
    fetch_text: FetchText | None = None,
) -> list[ExternalChain]:
    html = (fetch_text or _fetch_text)(LAVENDER_TOOLS_URL, timeout)
    chains: dict[tuple[str, str], ExternalChain] = {}
    for network, slug, _url, _height in _iter_lavender_snapshot_urls(html):
        name = DISPLAY_NAMES.get(slug) or slug.replace("-", " ").title()
        chains.setdefault(
            (network, slug),
            ExternalChain(
                source="lavender",
                slug=slug,
                name=name,
                network=network,
                url=LAVENDER_TOOLS_URL,
            ),
        )
    return sorted(chains.values(), key=lambda chain: (_norm_key(chain.name), chain.network))


def fetch_lavender_snapshots(
    *,
    chain: str,
    network: str | None = None,
    timeout: float = 30.0,
    fetch_text: FetchText | None = None,
    fetch_headers: FetchHeaders | None = None,
) -> list[Snapshot]:
    html = (fetch_text or _fetch_text)(LAVENDER_TOOLS_URL, timeout)
    wanted_slugs = _candidate_slugs(chain)
    by_chain: dict[tuple[str, str], tuple[str, int | None]] = {}
    for snapshot_network, slug, url, height in _iter_lavender_snapshot_urls(html):
        if slug not in wanted_slugs:
            continue
        if network is not None and _norm_key(network) != _norm_key(snapshot_network):
            continue
        key = (snapshot_network, slug)
        current = by_chain.get(key)
        if current is None or (height or -1) > (current[1] or -1):
            by_chain[key] = (url, height)

    snapshots = []
    for (snapshot_network, slug), (url, height) in sorted(by_chain.items()):
        chain_info = ExternalChain(
            source="lavender",
            slug=slug,
            name=DISPLAY_NAMES.get(slug) or slug.replace("-", " ").title(),
            network=snapshot_network,
            url=LAVENDER_TOOLS_URL,
        )
        snapshots.append(
            _snapshot_from_url(
                source="lavender",
                chain=chain_info,
                url=url,
                height=height,
                timeout=timeout,
                fetch_headers=fetch_headers,
                is_pruned=True,
                client_id="tendermint",
            )
        )
    return snapshots


def chain_summaries(chains: list[ExternalChain], *, client_id: str | None) -> list[ChainSummary]:
    grouped: dict[str, dict[str, object]] = {}
    for chain in chains:
        currency_id = _currency_id(chain.slug)
        entry = grouped.setdefault(
            currency_id,
            {
                "name": chain.name,
                "networks": set(),
                "clients": set(),
                "count": 0,
            },
        )
        entry["networks"].add(chain.network)
        if client_id:
            entry["clients"].add(client_id)
        entry["count"] += 1

    return [
        ChainSummary(
            currency_id=currency_id,
            currency_name=str(entry["name"]),
            snapshot_count=int(entry["count"]),
            networks=tuple(sorted(entry["networks"], key=_norm_key)),
            clients=tuple(sorted(entry["clients"], key=_norm_key)),
        )
        for currency_id, entry in sorted(grouped.items(), key=lambda item: _norm_key(str(item[1]["name"])))
    ]


def find_external_chain(chains: list[ExternalChain], value: str) -> ExternalChain | None:
    for chain in chains:
        if _matches_chain(chain, value):
            return chain
    return None


def _snapshot_from_detail(
    *,
    source: str,
    chain: ExternalChain,
    html: str,
    url_pattern: str,
    timeout: float,
    fetch_headers: FetchHeaders | None,
    is_pruned: bool,
    client_id: str | None,
) -> Snapshot:
    url_match = re.search(url_pattern, html)
    if not url_match:
        raise SnapshotFetchError(f"{source} detail page did not include a snapshot download URL")

    url = unescape(url_match.group(0))
    text = re.sub(r"\s+", " ", _clean_html(html))
    height = _extract_height(text, url)
    size = _extract_size(text)
    return _snapshot_from_url(
        source=source,
        chain=chain,
        url=url,
        height=height,
        timeout=timeout,
        fetch_headers=fetch_headers,
        is_pruned=is_pruned,
        client_id=client_id,
        size=size,
    )


def _snapshot_from_url(
    *,
    source: str,
    chain: ExternalChain,
    url: str,
    height: int | None,
    timeout: float,
    fetch_headers: FetchHeaders | None,
    is_pruned: bool,
    client_id: str | None,
    size: str | None = None,
) -> Snapshot:
    headers = _safe_headers(url, timeout, fetch_headers)
    header_height = _optional_int(headers.get("x-chain-blockheight") or headers.get("x-amz-meta-height"))
    height = height or header_height or _height_from_url(url)
    compressed_bytes = _optional_int(headers.get("content-length")) or _parse_size(size)
    uploaded_at = _http_date_to_iso(headers.get("last-modified"))
    node_version = headers.get("x-chain-version") or headers.get("x-amz-meta-node-version")

    return Snapshot(
        currency_id=_currency_id(chain.slug),
        currency_name=chain.name,
        network_name=chain.network,
        snapshot_name=f"{_currency_id(chain.slug)}-{source}",
        client_id=client_id,
        snapshot_type="full",
        block_heights=(height,) if height is not None else None,
        compressed_bytes=compressed_bytes,
        uncompressed_bytes=None,
        node_version=node_version,
        url=url,
        permanent_url_pathname=None,
        timestamp=None,
        created_at=None,
        uploaded_at=uploaded_at,
        metadata=(("source", source), ("page", chain.url)),
        schedule=None,
        locations=(),
        is_outdated=False,
        is_pruned=is_pruned,
        is_archive=False,
        source=source,
    )


def _iter_lavender_snapshot_urls(html: str):
    pattern = re.compile(
        r"https://snapshots\.lavenderfive\.com/(?P<prefix>snapshots|testnet-snapshots)/"
        r"(?P<slug>[^/]+)/(?P<file>[^\"'\\\s<>]+?\.tar\.(?:zst|lz4))"
    )
    seen: set[str] = set()
    for match in pattern.finditer(html):
        url = unescape(match.group(0)).rstrip("\\")
        if url in seen:
            continue
        seen.add(url)
        slug = match.group("slug")
        filename = match.group("file")
        network = "testnet" if match.group("prefix") == "testnet-snapshots" else "mainnet"
        height_match = re.search(r"_(\d+)\.tar\.(?:zst|lz4)$", filename)
        height = int(height_match.group(1)) if height_match else None
        yield network, slug, url, height


def _candidate_slugs(value: str) -> set[str]:
    key = _norm_key(value)
    slugs = {key}
    if key in CHAIN_ALIASES:
        slugs.add(CHAIN_ALIASES[key])
    return slugs


def _matches_chain(chain: ExternalChain, value: str) -> bool:
    key = _norm_key(value)
    return key in {
        _norm_key(chain.slug),
        _norm_key(chain.name),
        _norm_key(_currency_id(chain.slug)),
        _norm_key(DISPLAY_NAMES.get(chain.slug)),
    } or CHAIN_ALIASES.get(key) == chain.slug


def _currency_id(slug: str) -> str:
    return CURRENCY_IDS.get(slug, slug)


def _safe_headers(
    url: str,
    timeout: float,
    fetch_headers: FetchHeaders | None,
) -> dict[str, str]:
    try:
        return fetch_headers(url, timeout) if fetch_headers else _fetch_headers(url, timeout)
    except SnapshotFetchError:
        return {}


def _fetch_text(url: str, timeout: float) -> str:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urlopen(request, timeout=timeout) as response:
            charset = response.headers.get_content_charset() or "utf-8"
            return response.read().decode(charset, errors="replace")
    except HTTPError as exc:
        raise SnapshotFetchError(f"request failed with HTTP {exc.code}: {url}") from exc
    except URLError as exc:
        raise SnapshotFetchError(f"request failed: {exc.reason}") from exc
    except TimeoutError as exc:
        raise SnapshotFetchError(f"request timed out: {url}") from exc


def _fetch_headers(url: str, timeout: float) -> dict[str, str]:
    request = Request(url, headers={"User-Agent": USER_AGENT}, method="HEAD")
    try:
        with urlopen(request, timeout=timeout) as response:
            return {key.casefold(): value for key, value in response.headers.items()}
    except HTTPError as exc:
        raise SnapshotFetchError(f"request failed with HTTP {exc.code}: {url}") from exc
    except URLError as exc:
        raise SnapshotFetchError(f"request failed: {exc.reason}") from exc
    except TimeoutError as exc:
        raise SnapshotFetchError(f"request timed out: {url}") from exc


def _clean_html(value: str) -> str:
    text = re.sub(r"<[^>]+>", " ", value)
    return unescape(re.sub(r"\s+", " ", text).strip())


def _extract_height(text: str, url: str) -> int | None:
    block_match = re.search(r"Block(?: Height)?(?: Age Download)?\s+(\d{5,})", text, re.IGNORECASE)
    if block_match:
        return int(block_match.group(1))
    return _height_from_url(url)


def _height_from_url(url: str) -> int | None:
    match = re.search(r"_(\d+)\.tar\.(?:lz4|zst)$", url)
    return int(match.group(1)) if match else None


def _extract_size(text: str) -> str | None:
    match = re.search(r"(\d+(?:\.\d+)?\s*(?:GB|GiB|MB|MiB|TB|TiB))", text, re.IGNORECASE)
    return match.group(1) if match else None


def _parse_size(value: str | None) -> int | None:
    if not value:
        return None
    match = re.match(r"(\d+(?:\.\d+)?)\s*([KMGT]i?B|B)", value.strip(), re.IGNORECASE)
    if not match:
        return None
    amount = float(match.group(1))
    unit = match.group(2).casefold()
    powers = {"b": 0, "kb": 1, "kib": 1, "mb": 2, "mib": 2, "gb": 3, "gib": 3, "tb": 4, "tib": 4}
    return int(amount * (1024 ** powers[unit]))


def _optional_int(value: str | None) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except ValueError:
        return None


def _http_date_to_iso(value: str | None) -> str | None:
    if not value:
        return None
    try:
        return parsedate_to_datetime(value).isoformat()
    except (TypeError, ValueError):
        return value


def _norm_key(value: str | None) -> str:
    return re.sub(r"[^a-z0-9]+", "", (value or "").casefold())
