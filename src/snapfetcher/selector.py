from __future__ import annotations

from dataclasses import dataclass
import time
from typing import Callable, Iterable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .publicnode import Snapshot

USER_AGENT = "snapfetcher/0.1 (+https://github.com/bufrr/snapfetcher)"

Probe = Callable[[str, float, int], "ProbeResult"]


@dataclass(frozen=True)
class ProbeResult:
    url: str
    ok: bool
    seconds: float | None
    bytes_read: int
    mbps: float | None
    error: str | None = None


def select_best_source(
    snapshots: Iterable[Snapshot],
    *,
    timeout: float = 30.0,
    max_height_lag: int = 1000,
    probe_bytes: int = 256 * 1024,
    probe: Probe | None = None,
) -> list[Snapshot]:
    selected: list[Snapshot] = []
    for group in _group_by_selection_key(snapshots).values():
        by_source = _group_by_source(group)
        if len(by_source) <= 1:
            selected.extend(group)
            continue

        eligible = _fresh_snapshots(group, max_height_lag=max_height_lag)
        fastest = _fastest_source(eligible, timeout=timeout, probe_bytes=probe_bytes, probe=probe)
        selected.extend(snapshot for snapshot in group if snapshot.source == fastest)

    return sorted(selected, key=_snapshot_output_key)


def probe_url(url: str, timeout: float, probe_bytes: int) -> ProbeResult:
    request = Request(
        url,
        headers={"User-Agent": USER_AGENT, "Range": f"bytes=0-{probe_bytes - 1}"},
    )
    started = time.monotonic()
    try:
        with urlopen(request, timeout=timeout) as response:
            data = response.read(probe_bytes)
    except (HTTPError, URLError, TimeoutError) as exc:
        return ProbeResult(
            url=url,
            ok=False,
            seconds=None,
            bytes_read=0,
            mbps=None,
            error=str(exc),
        )

    seconds = max(time.monotonic() - started, 0.000001)
    bytes_read = len(data)
    return ProbeResult(
        url=url,
        ok=True,
        seconds=seconds,
        bytes_read=bytes_read,
        mbps=(bytes_read * 8 / seconds) / 1_000_000,
    )


def _fresh_snapshots(snapshots: list[Snapshot], *, max_height_lag: int) -> list[Snapshot]:
    heights = [snapshot.block_heights[-1] for snapshot in snapshots if snapshot.block_heights]
    if not heights:
        return snapshots

    max_height = max(heights)
    fresh = [
        snapshot
        for snapshot in snapshots
        if snapshot.block_heights and snapshot.block_heights[-1] >= max_height - max_height_lag
    ]
    return fresh or snapshots


def _fastest_source(
    snapshots: list[Snapshot],
    *,
    timeout: float,
    probe_bytes: int,
    probe: Probe | None,
) -> str:
    probe = probe or probe_url
    candidates = []
    for source, source_snapshots in sorted(_group_by_source(snapshots).items()):
        representative = _representative_snapshot(source_snapshots)
        result = probe(representative.url, timeout, probe_bytes)
        candidates.append((source, representative, result))

    successful = [candidate for candidate in candidates if candidate[2].ok and candidate[2].mbps is not None]
    if successful:
        return max(successful, key=lambda candidate: (candidate[2].mbps or 0, _height(candidate[1])))[0]

    return max(candidates, key=lambda candidate: _height(candidate[1]))[0]


def _group_by_source(snapshots: Iterable[Snapshot]) -> dict[str, list[Snapshot]]:
    grouped: dict[str, list[Snapshot]] = {}
    for snapshot in snapshots:
        grouped.setdefault(snapshot.source, []).append(snapshot)
    return grouped


def _group_by_selection_key(snapshots: Iterable[Snapshot]) -> dict[tuple[str, str, str], list[Snapshot]]:
    by_chain_network: dict[tuple[str, str], list[Snapshot]] = {}
    for snapshot in snapshots:
        key = (_norm(snapshot.currency_id), _norm(snapshot.network_name))
        by_chain_network.setdefault(key, []).append(snapshot)

    grouped: dict[tuple[str, str, str], list[Snapshot]] = {}
    for (chain, network), group in by_chain_network.items():
        clientless_group = any(snapshot.client_id is None for snapshot in group)
        for snapshot in group:
            client = "*" if clientless_group else _norm(snapshot.client_id)
            grouped.setdefault((chain, network, client), []).append(snapshot)
    return grouped


def _representative_snapshot(snapshots: list[Snapshot]) -> Snapshot:
    return sorted(snapshots, key=_snapshot_rank)[0]


def _snapshot_rank(snapshot: Snapshot) -> tuple[int, int, str]:
    type_rank = {"full": 0, "part": 1, "base": 2}.get(snapshot.snapshot_type.casefold(), 3)
    return type_rank, -_height(snapshot), snapshot.url


def _snapshot_output_key(snapshot: Snapshot) -> tuple[str, str, str, int, str]:
    return (
        snapshot.currency_id.casefold(),
        snapshot.network_name.casefold(),
        (snapshot.client_id or "").casefold(),
        _height(snapshot),
        snapshot.source,
    )


def _height(snapshot: Snapshot) -> int:
    return snapshot.block_heights[-1] if snapshot.block_heights else -1


def _norm(value: str | None) -> str:
    return (value or "").strip().casefold()
