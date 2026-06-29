import unittest

from snapfetcher.ethpanda import (
    ETHPANDA_CLIENTS,
    ETHPANDA_NETWORKS,
    fetch_ethpanda_snapshot,
    is_ethereum_chain,
)


class EthPandaTest(unittest.TestCase):
    def test_fetches_snapshot_metadata_from_ethpanda_endpoints(self):
        snapshot = fetch_ethpanda_snapshot(
            "mainnet",
            "reth",
            timeout=1,
            fetch_text=_fake_text,
            fetch_headers=_fake_headers,
        )

        self.assertEqual(snapshot.source, "ethpandaops")
        self.assertEqual(snapshot.currency_id, "ethereum")
        self.assertEqual(snapshot.network_name, "mainnet")
        self.assertEqual(snapshot.client_id, "reth")
        self.assertEqual(snapshot.snapshot_type, "full")
        self.assertEqual(snapshot.block_heights, (12345,))
        self.assertEqual(snapshot.compressed_bytes, 987654321)
        self.assertEqual(snapshot.node_version, "reth/v2.2.0")
        self.assertEqual(
            snapshot.url,
            "https://snapshots.ethpandaops.io/mainnet/reth/12345/snapshot.tar.zst",
        )

    def test_recognizes_ethereum_chain_aliases(self):
        self.assertTrue(is_ethereum_chain("Ethereum"))
        self.assertTrue(is_ethereum_chain("eth"))
        self.assertFalse(is_ethereum_chain("Bitcoin"))

    def test_supported_matrix_matches_ethpanda_execution_snapshots(self):
        self.assertEqual(ETHPANDA_NETWORKS[0], "mainnet")
        self.assertIn("hoodi", ETHPANDA_NETWORKS)
        self.assertEqual(set(ETHPANDA_CLIENTS), {"besu", "erigon", "geth", "nethermind", "reth"})


def _fake_text(url, timeout):
    if url.endswith("/latest"):
        return "12345\n"
    if url.endswith("/_snapshot_web3_clientVersion.json"):
        return '{"jsonrpc":"2.0","id":1,"result":"reth/v2.2.0"}'
    raise AssertionError(f"unexpected text URL: {url}")


def _fake_headers(url, timeout):
    if url.endswith("/snapshot.tar.zst"):
        return {
            "content-length": "987654321",
            "last-modified": "Mon, 29 Jun 2026 03:57:58 GMT",
        }
    raise AssertionError(f"unexpected header URL: {url}")


if __name__ == "__main__":
    unittest.main()
