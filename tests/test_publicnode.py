import unittest

from snapfetcher.publicnode import (
    SnapshotFetchError,
    discover_build_id,
    extract_snapshots,
    find_snapshots,
    list_chains,
)


class PublicNodeTest(unittest.TestCase):
    def test_discovers_build_id_from_next_data(self):
        html = '<script id="__NEXT_DATA__">{"buildId":"abc123"}</script>'

        self.assertEqual(discover_build_id(html), "abc123")

    def test_discovers_build_id_from_manifest_asset(self):
        html = '<script src="/_next/static/build-456/_buildManifest.js"></script>'

        self.assertEqual(discover_build_id(html), "build-456")

    def test_raises_when_build_id_missing(self):
        with self.assertRaises(SnapshotFetchError):
            discover_build_id("<html></html>")

    def test_extracts_snapshot_list(self):
        snapshots = extract_snapshots(_payload())

        self.assertEqual(len(snapshots), 3)
        self.assertEqual(snapshots[0].currency_id, "ethereum")
        self.assertEqual(snapshots[0].client_id, "geth")
        self.assertEqual(snapshots[0].height_label, "0-10")

    def test_finds_current_ethereum_geth_segments_with_filters(self):
        snapshots = extract_snapshots(_payload())

        matches = find_snapshots(snapshots, network="mainnet", client="geth")

        self.assertEqual([snapshot.snapshot_type for snapshot in matches], ["base", "part"])
        self.assertEqual(
            [snapshot.url for snapshot in matches],
            [
                "https://snapshots.publicnode.com/ethereum-geth-base-0-10.tar.lz4",
                "https://snapshots.publicnode.com/ethereum-geth-part-11-20.tar.lz4",
            ],
        )

    def test_can_filter_snapshot_type(self):
        snapshots = extract_snapshots(_payload())

        matches = find_snapshots(snapshots, snapshot_type="part")

        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].snapshot_type, "part")

    def test_can_fetch_all_snapshots_by_chain_name(self):
        snapshots = extract_snapshots(_multi_chain_payload())

        matches = find_snapshots(snapshots, chain="Bitcoin", network=None, client=None)

        self.assertEqual(len(matches), 2)
        self.assertEqual({snapshot.network_name for snapshot in matches}, {"mainnet", "testnet"})
        self.assertTrue(all(snapshot.currency_name == "Bitcoin" for snapshot in matches))

    def test_lists_chain_names(self):
        snapshots = extract_snapshots(_multi_chain_payload())

        chains = list_chains(snapshots)

        self.assertEqual([chain.currency_name for chain in chains], ["Bitcoin", "Ethereum"])
        self.assertEqual(chains[0].snapshot_count, 2)
        self.assertEqual(chains[0].networks, ("mainnet", "testnet"))


def _payload():
    return {
        "pageProps": {
            "values": {
                "stats.$data": {"total": 1},
                "snapshots.$data": [
                    _snapshot("base", [0, 10], False),
                    _snapshot("part", [11, 20], False),
                    _snapshot("part", [11, 19], True),
                ],
            }
        }
    }


def _multi_chain_payload():
    payload = _payload()
    payload["pageProps"]["values"]["snapshots.$data"].extend(
        [
            _snapshot(
                "full",
                [100],
                False,
                currency_id="bitcoin",
                currency_name="Bitcoin",
                network_name="mainnet",
                snapshot_name="bitcoin",
                client_id=None,
            ),
            _snapshot(
                "full",
                [50],
                False,
                currency_id="bitcoin",
                currency_name="Bitcoin",
                network_name="testnet",
                snapshot_name="bitcoin-testnet",
                client_id=None,
            ),
        ]
    )
    return payload


def _snapshot(
    snapshot_type,
    block_heights,
    is_outdated,
    *,
    currency_id="ethereum",
    currency_name="Ethereum",
    network_name="mainnet",
    snapshot_name="ethereum-geth",
    client_id="geth",
):
    height = "-".join(str(item) for item in block_heights)
    return {
        "currencyId": currency_id,
        "currencyName": currency_name,
        "networkName": network_name,
        "snapshotName": snapshot_name,
        "clientId": client_id,
        "isPruned": False,
        "isArchive": False,
        "type": snapshot_type,
        "blockHeights": block_heights,
        "size": {"compressed": 1024, "uncompressed": 2048},
        "nodeVersion": "1.17.1",
        "url": f"https://snapshots.publicnode.com/{snapshot_name}-{snapshot_type}-{height}.tar.lz4",
        "permanentUrlPathname": f"{snapshot_name}-{snapshot_type}.tar.lz4",
        "timestamp": "2026-06-29T00:00:00.000Z",
        "createdAt": "2026-06-29T00:01:00.000Z",
        "uploadedAt": "2026-06-29T00:02:00.000Z",
        "metadata": [{"key": "db-engine", "value": "pebble"}],
        "schedule": "24h",
        "locations": ["DE", "JP", "US"],
        "isOutdated": is_outdated,
    }


if __name__ == "__main__":
    unittest.main()
