import unittest

from snapfetcher.publicnode import Snapshot
from snapfetcher.selector import ProbeResult, select_best_source


class SelectorTest(unittest.TestCase):
    def test_filters_stale_snapshots_before_speed_test(self):
        snapshots = [
            _snapshot("polkachu", 100, "https://example.com/polkachu.tar.lz4"),
            _snapshot("lavender", 80, "https://example.com/lavender.tar.zst"),
        ]

        selected = select_best_source(
            snapshots,
            max_height_lag=5,
            probe=_probe({"polkachu": 10.0, "lavender": 100.0}),
        )

        self.assertEqual([snapshot.source for snapshot in selected], ["polkachu"])

    def test_speed_selects_among_fresh_candidates(self):
        snapshots = [
            _snapshot("publicnode", 99, "https://example.com/publicnode.tar.lz4"),
            _snapshot("polkachu", 100, "https://example.com/polkachu.tar.lz4"),
        ]

        selected = select_best_source(
            snapshots,
            max_height_lag=5,
            probe=_probe({"publicnode": 50.0, "polkachu": 10.0}),
        )

        self.assertEqual([snapshot.source for snapshot in selected], ["publicnode"])

    def test_keeps_all_snapshots_for_single_source(self):
        snapshots = [
            _snapshot("publicnode", 10, "https://example.com/base.tar.lz4", snapshot_type="base"),
            _snapshot("publicnode", 20, "https://example.com/part.tar.lz4", snapshot_type="part"),
        ]

        selected = select_best_source(snapshots, probe=_probe({}))

        self.assertEqual(selected, snapshots)


def _probe(speeds):
    def probe(url, timeout, probe_bytes):
        source = url.split("/")[-1].split(".")[0]
        return ProbeResult(
            url=url,
            ok=True,
            seconds=1.0,
            bytes_read=probe_bytes,
            mbps=speeds[source],
        )

    return probe


def _snapshot(source, height, url, *, snapshot_type="full"):
    return Snapshot(
        currency_id="cosmos",
        currency_name="Cosmos",
        network_name="mainnet",
        snapshot_name=f"cosmos-{source}",
        client_id="tendermint",
        snapshot_type=snapshot_type,
        block_heights=(height,),
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
