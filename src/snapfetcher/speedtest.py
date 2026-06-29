from __future__ import annotations

from dataclasses import dataclass
import time
from typing import Callable, Iterable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .publicnode import Snapshot, SnapshotFetchError

USER_AGENT = "snapfetcher/0.1 speedtest"
DEFAULT_PROBE_BYTES = 64 * 1024

Probe = Callable[[str, float, int], "SpeedProbeResult"]


@dataclass(frozen=True)
class SpeedProbeResult:
    elapsed_seconds: float
    bytes_read: int


@dataclass(frozen=True)
class SourceSpeed:
    source: str
    url: str
    elapsed_seconds: float
    bytes_read: int


def select_fastest_source(
    snapshots: Iterable[Snapshot],
    *,
    timeout: float,
    probe_bytes: int = DEFAULT_PROBE_BYTES,
    probe: Probe | None = None,
) -> list[Snapshot]:
    snapshots = list(snapshots)
    selected: list[Snapshot] = []

    probe = probe or probe_url
    for group in _group_by_selection_key(snapshots).values():
        by_source = _group_by_source(group)
        if len(by_source) <= 1:
            selected.extend(group)
            continue

        results = speedtest_sources(by_source, timeout=timeout, probe_bytes=probe_bytes, probe=probe)
        fastest = min(results, key=lambda result: (result.elapsed_seconds, result.source))
        selected.extend(snapshot for snapshot in group if snapshot.source == fastest.source)

    return selected


def speedtest_sources(
    by_source: dict[str, list[Snapshot]],
    *,
    timeout: float,
    probe_bytes: int = DEFAULT_PROBE_BYTES,
    probe: Probe | None = None,
) -> list[SourceSpeed]:
    probe = probe or probe_url
    results: list[SourceSpeed] = []
    errors: list[str] = []

    for source, snapshots in sorted(by_source.items()):
        snapshot = _representative_snapshot(snapshots)
        try:
            result = probe(snapshot.url, timeout, probe_bytes)
        except SnapshotFetchError as exc:
            errors.append(f"{source}: {exc}")
            continue
        results.append(
            SourceSpeed(
                source=source,
                url=snapshot.url,
                elapsed_seconds=result.elapsed_seconds,
                bytes_read=result.bytes_read,
            )
        )

    if not results:
        detail = "; ".join(errors) if errors else "no sources to test"
        raise SnapshotFetchError(f"All source speed tests failed: {detail}")

    return results


def probe_url(url: str, timeout: float, probe_bytes: int = DEFAULT_PROBE_BYTES) -> SpeedProbeResult:
    headers = {
        "User-Agent": USER_AGENT,
        "Range": f"bytes=0-{max(probe_bytes, 1) - 1}",
    }
    request = Request(url, headers=headers)
    started_at = time.perf_counter()
    try:
        with urlopen(request, timeout=timeout) as response:
            data = response.read(probe_bytes)
    except HTTPError as exc:
        raise SnapshotFetchError(f"Speed test failed with HTTP {exc.code}: {url}") from exc
    except URLError as exc:
        raise SnapshotFetchError(f"Speed test failed: {exc.reason}") from exc
    except TimeoutError as exc:
        raise SnapshotFetchError(f"Speed test timed out: {url}") from exc

    return SpeedProbeResult(
        elapsed_seconds=time.perf_counter() - started_at,
        bytes_read=len(data),
    )


def _group_by_source(snapshots: Iterable[Snapshot]) -> dict[str, list[Snapshot]]:
    by_source: dict[str, list[Snapshot]] = {}
    for snapshot in snapshots:
        by_source.setdefault(snapshot.source, []).append(snapshot)
    return by_source


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
    height = snapshot.block_heights[-1] if snapshot.block_heights else -1
    return type_rank, -height, snapshot.url


def _norm(value: str | None) -> str:
    return (value or "").strip().casefold()
