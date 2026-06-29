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


def _snapshot(source, url):
    return Snapshot(
        currency_id="ethereum",
        currency_name="Ethereum",
        network_name="mainnet",
        snapshot_name=f"ethereum-{source}",
        client_id="geth",
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
