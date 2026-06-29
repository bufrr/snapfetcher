from __future__ import annotations

from dataclasses import dataclass
from html import unescape
import re
from typing import Callable, Iterable
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen

from .publicnode import ChainSummary, Snapshot, SnapshotFetchError

POLKACHU_BASE_URL = "https://www.polkachu.com"
POLKACHU_SNAPSHOTS_PATH = "/tendermint_snapshots"
USER_AGENT = "snapfetcher/0.1 (+https://www.polkachu.com/tendermint_snapshots)"

FetchText = Callable[[str, float], str]


@dataclass(frozen=True)
class PolkachuChain:
    slug: str
    name: str
    url: str


def fetch_polkachu_chains(
    *,
    timeout: float = 30.0,
    fetch_text: FetchText | None = None,
) -> list[PolkachuChain]:
    fetch_text = fetch_text or _fetch_text
    html = fetch_text(urljoin(POLKACHU_BASE_URL, POLKACHU_SNAPSHOTS_PATH), timeout)
    return extract_polkachu_chains(html)


def extract_polkachu_chains(html: str) -> list[PolkachuChain]:
    chains: list[PolkachuChain] = []
    seen: set[str] = set()
    pattern = re.compile(
        r'<a\b[^>]*href="(?P<url>https://www\.polkachu\.com/tendermint_snapshots/(?P<slug>[^"/#?]+))"[^>]*>'
        r"(?P<label>.*?)</a>",
        re.IGNORECASE | re.DOTALL,
    )

    for match in pattern.finditer(html):
        slug = match.group("slug").strip()
        if slug in seen:
            continue
        name = _strip_tags(match.group("label"))
        if not name:
            continue
        chains.append(PolkachuChain(slug=slug, name=name, url=match.group("url")))
        seen.add(slug)

    if not chains:
        raise SnapshotFetchError("PolkaChu page did not include any Tendermint snapshot chains")

    return chains


def fetch_polkachu_snapshots(
    *,
    chain: str,
    timeout: float = 30.0,
    fetch_text: FetchText | None = None,
    chains: Iterable[PolkachuChain] | None = None,
) -> list[Snapshot]:
    fetch_text = fetch_text or _fetch_text
    chains = (
        chains
        if chains is not None
        else fetch_polkachu_chains(timeout=timeout, fetch_text=fetch_text)
    )
    polkachu_chain = find_polkachu_chain(chains, chain)
    if polkachu_chain is None:
        return []

    html = fetch_text(polkachu_chain.url, timeout)
    return [extract_polkachu_snapshot(html, polkachu_chain)]


def find_polkachu_chain(
    chains: Iterable[PolkachuChain],
    chain: str,
) -> PolkachuChain | None:
    chain_key = _norm(chain)
    for polkachu_chain in chains:
        if chain_key in {_norm(polkachu_chain.name), _norm(polkachu_chain.slug)}:
            return polkachu_chain
    return None


def polkachu_chain_summaries(chains: Iterable[PolkachuChain]) -> list[ChainSummary]:
    return [
        ChainSummary(
            currency_id=chain.slug,
            currency_name=chain.name,
            snapshot_count=1,
            networks=("mainnet",),
            clients=("tendermint",),
        )
        for chain in sorted(chains, key=lambda item: _norm(item.name))
    ]


def extract_polkachu_snapshot(html: str, chain: PolkachuChain) -> Snapshot:
    title_match = re.search(r"<title>(?P<title>.*?) Node Snapshot \| Polkachu</title>", html, re.DOTALL)
    chain_name = _strip_tags(title_match.group("title")) if title_match else chain.name

    chain_id = _extract_labeled_value(html, "Chain ID")
    node_version = _extract_labeled_value(html, "Current Node Version")
    download_url = _extract_download_url(html)
    height = _extract_height(html, download_url)
    size_label = _extract_table_value(html, "Size")
    timestamp = _extract_table_value(html, "Timestamp")

    return Snapshot(
        currency_id=chain.slug,
        currency_name=chain_name,
        network_name="mainnet",
        snapshot_name=f"{chain.slug}-tendermint",
        client_id="tendermint",
        snapshot_type="full",
        block_heights=(height,) if height is not None else None,
        compressed_bytes=_parse_size(size_label),
        uncompressed_bytes=None,
        node_version=node_version,
        url=download_url,
        permanent_url_pathname=f"tendermint_snapshots/{chain.slug}",
        timestamp=timestamp,
        created_at=None,
        uploaded_at=timestamp,
        metadata=tuple(
            item
            for item in (
                ("source", "polkachu"),
                ("polkachu-slug", chain.slug),
                ("chain-id", chain_id),
            )
            if item[1]
        ),
        schedule="24h",
        locations=(),
        is_outdated=False,
        is_pruned=True,
        is_archive=False,
        source="polkachu",
    )


def _extract_labeled_value(html: str, label: str) -> str | None:
    pattern = re.compile(
        rf"<span\b[^>]*>\s*{re.escape(label)}\s*</span>\s*:\s*(?P<value>.*?)(?:\||</p>)",
        re.IGNORECASE | re.DOTALL,
    )
    match = pattern.search(html)
    if not match:
        return None
    return _strip_tags(match.group("value"))


def _extract_download_url(html: str) -> str:
    match = re.search(
        r'href="(?P<url>https://snapshots\.polkachu\.com/snapshots/[^"]+?\.tar\.lz4)"',
        html,
        re.IGNORECASE,
    )
    if not match:
        raise SnapshotFetchError("PolkaChu detail page did not include a snapshot download URL")
    return match.group("url")


def _extract_height(html: str, download_url: str) -> int | None:
    height_text = _extract_table_value(html, "Block Height")
    if height_text and height_text.isdigit():
        return int(height_text)

    filename_match = re.search(r"_(?P<height>\d+)\.tar\.lz4$", download_url)
    if filename_match:
        return int(filename_match.group("height"))
    return None


def _extract_table_value(html: str, heading: str) -> str | None:
    headings = [
        _strip_tags(match.group("content"))
        for match in re.finditer(r"<th\b[^>]*>(?P<content>.*?)</th>", html, re.IGNORECASE | re.DOTALL)
    ]
    values = [
        _strip_tags(match.group("content"))
        for match in re.finditer(r"<td\b[^>]*>(?P<content>.*?)</td>", html, re.IGNORECASE | re.DOTALL)
    ]
    heading_key = _norm(heading)
    for index, value in enumerate(headings):
        if _norm(value) == heading_key and index < len(values):
            return values[index] or None
    return None


def _fetch_text(url: str, timeout: float) -> str:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urlopen(request, timeout=timeout) as response:
            charset = response.headers.get_content_charset() or "utf-8"
            return response.read().decode(charset, errors="replace")
    except HTTPError as exc:
        raise SnapshotFetchError(f"PolkaChu request failed with HTTP {exc.code}: {url}") from exc
    except URLError as exc:
        raise SnapshotFetchError(f"PolkaChu request failed: {exc.reason}") from exc
    except TimeoutError as exc:
        raise SnapshotFetchError(f"PolkaChu request timed out: {url}") from exc


def _strip_tags(value: str) -> str:
    without_tags = re.sub(r"<[^>]+>", " ", value)
    return " ".join(unescape(without_tags).split())


def _parse_size(value: str | None) -> int | None:
    if not value:
        return None

    match = re.search(r"(?P<number>\d+(?:\.\d+)?)\s*(?P<unit>[KMGTPE]?B)", value, re.IGNORECASE)
    if not match:
        return None

    number = float(match.group("number"))
    unit = match.group("unit").upper()
    multiplier = {
        "B": 1,
        "KB": 1024,
        "MB": 1024**2,
        "GB": 1024**3,
        "TB": 1024**4,
        "PB": 1024**5,
        "EB": 1024**6,
    }[unit]
    return int(number * multiplier)


def _norm(value: str | None) -> str:
    return (value or "").strip().casefold()
