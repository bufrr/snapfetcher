from __future__ import annotations

import argparse
import csv
import io
import json
import sys
from typing import Sequence

from .external import (
    chain_summaries,
    fetch_kjnodes_chains,
    fetch_kjnodes_snapshots,
    fetch_lavender_chains,
    fetch_lavender_snapshots,
    fetch_polkachu_chains,
    fetch_polkachu_snapshots,
)
from .publicnode import (
    ChainSummary,
    Snapshot,
    SnapshotFetchError,
    fetch_publicnode_snapshots,
    find_snapshots,
    list_chains,
)
from .selector import select_best_source

SOURCE_CHOICES = ("publicnode", "polkachu", "lavender", "kjnodes", "all")
ALL_SOURCES = ("publicnode", "polkachu", "lavender", "kjnodes")


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.json and args.csv:
        parser.error("--json and --csv cannot be used together")

    try:
        sources = _resolve_sources(args.source)
        if args.list_chains:
            chains = _list_chains_for_sources(
                sources,
                timeout=args.timeout,
                include_outdated=args.include_outdated,
            )
            if args.json:
                print(json.dumps([_chain_to_dict(chain) for chain in chains], indent=2))
            elif args.csv:
                print(_format_chain_csv(chains))
            else:
                print(_format_chain_table(chains))
            return 0

        chain, network, client = _resolve_filters(args)
        snapshots = _fetch_snapshots_for_sources(
            sources,
            chain=chain,
            network=network,
            timeout=args.timeout,
        )
        matches = find_snapshots(
            snapshots,
            chain=chain,
            network=network,
            client=client,
            snapshot_type=args.snapshot_type,
            include_outdated=args.include_outdated,
            archive=args.archive,
            pruned=args.pruned,
        )
        if args.best_source and len(sources) > 1:
            matches = select_best_source(
                matches,
                timeout=args.timeout,
                max_height_lag=args.max_height_lag,
            )
    except SnapshotFetchError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if not matches:
        print(_no_matches_message(args, chain=chain, network=network, client=client), file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps([_snapshot_to_dict(snapshot) for snapshot in matches], indent=2))
    elif args.csv:
        print(_format_snapshot_csv(matches))
    elif args.url_only:
        for snapshot in matches:
            print(snapshot.url)
    else:
        print(_format_table(matches))

    return 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Fetch snapshot URLs from PublicNode and optional snapshot providers.",
    )
    parser.add_argument(
        "--chain",
        help=(
            "Chain ID or name to match. If omitted, defaults to Ethereum "
            "mainnet geth. If supplied without --network or --client, matches all "
            "snapshots for that chain from the selected sources."
        ),
    )
    parser.add_argument(
        "--network",
        help="Network name to match. Omit with --chain to include all networks.",
    )
    parser.add_argument(
        "--client",
        help="Client ID to match. Omit with --chain to include all clients.",
    )
    parser.add_argument(
        "--type",
        choices=("base", "part", "full"),
        dest="snapshot_type",
        help="Snapshot type to match. Omit to return all matching segments.",
    )
    parser.add_argument(
        "--archive",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="Filter archive snapshots. Omit to allow either.",
    )
    parser.add_argument(
        "--pruned",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="Filter pruned snapshots. Omit to allow either.",
    )
    parser.add_argument(
        "--include-outdated",
        action="store_true",
        help="Include PublicNode entries marked as outdated.",
    )
    parser.add_argument(
        "--list-chains",
        action="store_true",
        help="List chain names, IDs, network names, and clients.",
    )
    parser.add_argument(
        "--url-only",
        action="store_true",
        help="Print only snapshot URLs, one per line.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print matching snapshot metadata as JSON.",
    )
    parser.add_argument(
        "--csv",
        action="store_true",
        help="Print spreadsheet-friendly CSV output.",
    )
    parser.add_argument(
        "--source",
        action="append",
        choices=SOURCE_CHOICES,
        help=(
            "Snapshot source to query. Repeat to query multiple sources. Defaults to publicnode. "
            "Use --source all for publicnode, polkachu, lavender, and kjnodes."
        ),
    )
    parser.add_argument(
        "--best-source",
        action=argparse.BooleanOptionalAction,
        default=True,
        help=(
            "For multiple sources, keep the fastest source after filtering out snapshots "
            "older than --max-height-lag from the freshest candidate."
        ),
    )
    parser.add_argument(
        "--max-height-lag",
        type=int,
        default=1000,
        help="Maximum block-height lag from the freshest candidate before speed testing. Defaults to 1000.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=30.0,
        help="Network timeout in seconds. Defaults to 30.",
    )
    return parser


def _resolve_filters(args: argparse.Namespace) -> tuple[str, str | None, str | None]:
    chain = args.chain or "ethereum"
    network = args.network
    client = args.client

    if args.chain is None:
        network = network or "mainnet"
        client = client or "geth"

    return chain, network, client


def _resolve_sources(values: list[str] | None) -> tuple[str, ...]:
    selected = values or ["publicnode"]
    if "all" in selected:
        selected = list(ALL_SOURCES)

    sources: list[str] = []
    seen: set[str] = set()
    for source in selected:
        if source == "all":
            continue
        if source not in seen:
            sources.append(source)
            seen.add(source)
    return tuple(sources)


def _fetch_snapshots_for_sources(
    sources: tuple[str, ...],
    *,
    chain: str,
    network: str | None,
    timeout: float,
) -> list[Snapshot]:
    snapshots: list[Snapshot] = []
    if "publicnode" in sources:
        snapshots.extend(fetch_publicnode_snapshots(timeout=timeout))
    if "polkachu" in sources:
        snapshots.extend(fetch_polkachu_snapshots(chain=chain, timeout=timeout))
    if "lavender" in sources:
        snapshots.extend(fetch_lavender_snapshots(chain=chain, network=network, timeout=timeout))
    if "kjnodes" in sources:
        snapshots.extend(fetch_kjnodes_snapshots(chain=chain, network=network, timeout=timeout))
    return snapshots


def _list_chains_for_sources(
    sources: tuple[str, ...],
    *,
    timeout: float,
    include_outdated: bool,
) -> list[ChainSummary]:
    chains: list[ChainSummary] = []
    if "publicnode" in sources:
        chains.extend(list_chains(fetch_publicnode_snapshots(timeout=timeout), include_outdated=include_outdated))
    if "polkachu" in sources:
        chains.extend(chain_summaries(fetch_polkachu_chains(timeout=timeout), client_id="tendermint"))
    if "lavender" in sources:
        chains.extend(chain_summaries(fetch_lavender_chains(timeout=timeout), client_id="tendermint"))
    if "kjnodes" in sources:
        chains.extend(chain_summaries(fetch_kjnodes_chains(timeout=timeout), client_id="tendermint"))
    return _merge_chain_summaries(chains)


def _merge_chain_summaries(chains: list[ChainSummary]) -> list[ChainSummary]:
    merged: dict[str, dict[str, object]] = {}
    for chain in chains:
        entry = merged.setdefault(
            chain.currency_id,
            {
                "name": chain.currency_name,
                "count": 0,
                "networks": set(),
                "clients": set(),
            },
        )
        entry["count"] += chain.snapshot_count
        entry["networks"].update(chain.networks)
        entry["clients"].update(chain.clients)

    return [
        ChainSummary(
            currency_id=currency_id,
            currency_name=str(entry["name"]),
            snapshot_count=int(entry["count"]),
            networks=tuple(sorted(entry["networks"], key=str.casefold)),
            clients=tuple(sorted(entry["clients"], key=str.casefold)),
        )
        for currency_id, entry in sorted(merged.items(), key=lambda item: str(item[1]["name"]).casefold())
    ]


def _format_table(snapshots: list[Snapshot]) -> str:
    rows = [
        (
            "source",
            "chain",
            "network",
            "client",
            "type",
            "height",
            "compressed",
            "uploaded",
            "url",
        )
    ]
    rows.extend(
        (
            snapshot.source,
            snapshot.currency_id,
            snapshot.network_name,
            snapshot.client_id or "-",
            snapshot.snapshot_type,
            snapshot.height_label,
            snapshot.compressed_size_label,
            snapshot.uploaded_at or "-",
            snapshot.url,
        )
        for snapshot in snapshots
    )

    widths = [max(len(row[index]) for row in rows) for index in range(len(rows[0]))]
    lines = []
    for row_index, row in enumerate(rows):
        lines.append("  ".join(value.ljust(widths[index]) for index, value in enumerate(row)))
        if row_index == 0:
            lines.append("  ".join("-" * width for width in widths))
    return "\n".join(lines)


def _format_chain_table(chains: list[ChainSummary]) -> str:
    rows = [("chain", "id", "network_names", "clients")]
    rows.extend(
        (
            chain.currency_name,
            chain.currency_id,
            ", ".join(chain.networks) or "-",
            ", ".join(chain.clients) or "-",
        )
        for chain in chains
    )

    widths = [max(len(row[index]) for row in rows) for index in range(len(rows[0]))]
    lines = []
    for row_index, row in enumerate(rows):
        lines.append("  ".join(value.ljust(widths[index]) for index, value in enumerate(row)))
        if row_index == 0:
            lines.append("  ".join("-" * width for width in widths))
    return "\n".join(lines)


def _format_chain_csv(chains: list[ChainSummary]) -> str:
    rows = [
        (
            chain.currency_name,
            chain.currency_id,
            ", ".join(chain.networks) or "-",
            ", ".join(chain.clients) or "-",
        )
        for chain in chains
    ]
    return _format_csv(("chain", "id", "network_names", "clients"), rows)


def _format_snapshot_csv(snapshots: list[Snapshot]) -> str:
    rows = [
        (
            snapshot.source,
            snapshot.currency_id,
            snapshot.network_name,
            snapshot.client_id or "-",
            snapshot.snapshot_type,
            snapshot.height_label,
            snapshot.compressed_size_label,
            snapshot.uploaded_at or "-",
            snapshot.url,
        )
        for snapshot in snapshots
    ]
    return _format_csv(
        ("source", "chain", "network", "client", "type", "height", "compressed", "uploaded", "url"),
        rows,
    )


def _format_csv(headers: tuple[str, ...], rows) -> str:
    output = io.StringIO()
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(headers)
    writer.writerows(rows)
    return output.getvalue().rstrip("\n")


def _snapshot_to_dict(snapshot: Snapshot) -> dict[str, object]:
    return {
        "source": snapshot.source,
        "currencyId": snapshot.currency_id,
        "currencyName": snapshot.currency_name,
        "networkName": snapshot.network_name,
        "snapshotName": snapshot.snapshot_name,
        "clientId": snapshot.client_id,
        "type": snapshot.snapshot_type,
        "blockHeights": list(snapshot.block_heights) if snapshot.block_heights else None,
        "compressedBytes": snapshot.compressed_bytes,
        "uncompressedBytes": snapshot.uncompressed_bytes,
        "nodeVersion": snapshot.node_version,
        "url": snapshot.url,
        "permanentUrlPathname": snapshot.permanent_url_pathname,
        "timestamp": snapshot.timestamp,
        "createdAt": snapshot.created_at,
        "uploadedAt": snapshot.uploaded_at,
        "metadata": dict(snapshot.metadata),
        "schedule": snapshot.schedule,
        "locations": list(snapshot.locations),
        "isOutdated": snapshot.is_outdated,
        "isPruned": snapshot.is_pruned,
        "isArchive": snapshot.is_archive,
    }


def _chain_to_dict(chain: ChainSummary) -> dict[str, object]:
    return {
        "currencyId": chain.currency_id,
        "currencyName": chain.currency_name,
        "snapshotCount": chain.snapshot_count,
        "networkCount": len(chain.networks),
        "networkNames": list(chain.networks),
        "networks": list(chain.networks),
        "clients": list(chain.clients),
    }


def _no_matches_message(
    args: argparse.Namespace,
    *,
    chain: str,
    network: str | None,
    client: str | None,
) -> str:
    filters = [f"chain={chain}"]
    if network:
        filters.append(f"network={network}")
    if client:
        filters.append(f"client={client}")
    if args.snapshot_type:
        filters.append(f"type={args.snapshot_type}")
    if args.archive is not None:
        filters.append(f"archive={args.archive}")
    if args.pruned is not None:
        filters.append(f"pruned={args.pruned}")
    if not args.include_outdated:
        filters.append("outdated=False")
    return "error: no snapshots matched " + ", ".join(filters)
