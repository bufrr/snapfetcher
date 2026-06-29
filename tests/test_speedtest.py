import unittest

from snapfetcher.publicnode import Snapshot
from snapfetcher.speedtest import SpeedProbeResult, select_fastest_source


class SpeedTest(unittest.TestCase):
    def test_selects_fastest_source(self):
        snapshots = [
            _snapshot("publicnode", "https://example.com/publicnode.tar.lz4"),
            _snapshot("ethpandaops", "https://example.com/ethpanda.tar.zst"),
        ]

        selected = select_fastest_source(
            snapshots,
            timeout=1,
            probe=lambda url, timeout, probe_bytes: SpeedProbeResult(
                elapsed_seconds=0.2 if "publicnode" in url else 0.05,
                bytes_read=probe_bytes,
            ),
        )

        self.assertEqual([snapshot.source for snapshot in selected], ["ethpandaops"])

    def test_keeps_single_source_without_probe(self):
        snapshots = [
            _snapshot("publicnode", "https://example.com/base.tar.lz4"),
            _snapshot("publicnode", "https://example.com/part.tar.lz4"),
        ]

        selected = select_fastest_source(
            snapshots,
            timeout=1,
            probe=lambda url, timeout, probe_bytes: self.fail("probe should not run"),
        )

        self.assertEqual(selected, snapshots)

    def test_keeps_unique_client_while_selecting_fastest_overlap(self):
        snapshots = [
            _snapshot("publicnode", "https://example.com/publicnode-geth.tar.lz4", client_id="geth"),
            _snapshot("ethpandaops", "https://example.com/ethpanda-geth.tar.zst", client_id="geth"),
            _snapshot("ethpandaops", "https://example.com/ethpanda-reth.tar.zst", client_id="reth"),
        ]

        selected = select_fastest_source(
            snapshots,
            timeout=1,
            probe=lambda url, timeout, probe_bytes: SpeedProbeResult(
                elapsed_seconds=0.2 if "publicnode" in url else 0.05,
                bytes_read=probe_bytes,
            ),
        )

        self.assertEqual(
            [(snapshot.source, snapshot.client_id) for snapshot in selected],
            [("ethpandaops", "geth"), ("ethpandaops", "reth")],
        )

    def test_compares_clientless_chain_source_with_client_specific_source(self):
        snapshots = [
            _snapshot(
                "publicnode",
                "https://example.com/cosmos-publicnode.tar.lz4",
                currency_id="cosmos",
                currency_name="Cosmos",
                client_id=None,
            ),
            _snapshot(
                "polkachu",
                "https://example.com/cosmos-polkachu.tar.lz4",
                currency_id="cosmos",
                currency_name="CosmosHub",
                client_id="tendermint",
            ),
        ]

        selected = select_fastest_source(
            snapshots,
            timeout=1,
            probe=lambda url, timeout, probe_bytes: SpeedProbeResult(
                elapsed_seconds=0.05 if "publicnode" in url else 0.2,
                bytes_read=probe_bytes,
            ),
        )

        self.assertEqual([snapshot.source for snapshot in selected], ["publicnode"])

    def test_keeps_unique_network_while_selecting_fastest_overlap(self):
        snapshots = [
            _snapshot(
                "publicnode",
                "https://example.com/celestia-mainnet-publicnode.tar.lz4",
                currency_id="celestia",
                currency_name="Celestia",
                network_name="mainnet",
                client_id=None,
            ),
            _snapshot(
                "polkachu",
                "https://example.com/celestia-mainnet-polkachu.tar.lz4",
                currency_id="celestia",
                currency_name="Celestia",
                network_name="mainnet",
                client_id="tendermint",
            ),
            _snapshot(
                "publicnode",
                "https://example.com/celestia-testnet-publicnode.tar.lz4",
                currency_id="celestia",
                currency_name="Celestia",
                network_name="testnet",
                client_id=None,
            ),
        ]

        selected = select_fastest_source(
            snapshots,
            timeout=1,
            probe=lambda url, timeout, probe_bytes: SpeedProbeResult(
                elapsed_seconds=0.05 if "polkachu" in url else 0.2,
                bytes_read=probe_bytes,
            ),
        )

        self.assertEqual(
            [(snapshot.source, snapshot.network_name) for snapshot in selected],
            [("polkachu", "mainnet"), ("publicnode", "testnet")],
        )


def _snapshot(
    source,
    url,
    *,
    currency_id="ethereum",
    currency_name="Ethereum",
    network_name="mainnet",
    client_id="geth",
):
    return Snapshot(
        currency_id=currency_id,
        currency_name=currency_name,
        network_name=network_name,
        snapshot_name=f"ethereum-{source}",
        client_id=client_id,
        snapshot_type="full",
        block_heights=(1,),
        compressed_bytes=1024,
        uncompressed_bytes=None,
        node_version=None,
        url=url,
        permanent_url_pathname=None,
        timestamp=None,
        created_at=None,
        uploaded_at=None,
        metadata=(),
        schedule=None,
        locations=(),
        is_outdated=False,
        is_pruned=True,
        is_archive=False,
        source=source,
    )


if __name__ == "__main__":
    unittest.main()
