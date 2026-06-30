import unittest

from snapfetcher.external import (
    fetch_kjnodes_chains,
    fetch_kjnodes_snapshots,
    fetch_lavender_snapshots,
    fetch_polkachu_chains,
    fetch_polkachu_snapshots,
)


class ExternalProviderTest(unittest.TestCase):
    def test_fetches_polkachu_snapshot(self):
        chains = fetch_polkachu_chains(fetch_text=_fetch_text)

        snapshots = fetch_polkachu_snapshots(
            chain="CosmosHub",
            chains=chains,
            fetch_text=_fetch_text,
            fetch_headers=_fetch_headers,
        )

        self.assertEqual(len(snapshots), 1)
        snapshot = snapshots[0]
        self.assertEqual(snapshot.source, "polkachu")
        self.assertEqual(snapshot.currency_id, "cosmos")
        self.assertEqual(snapshot.network_name, "mainnet")
        self.assertEqual(snapshot.client_id, "tendermint")
        self.assertEqual(snapshot.block_heights, (31798367,))
        self.assertEqual(snapshot.compressed_bytes, 22000000000)

    def test_fetches_kjnodes_snapshot(self):
        chains = fetch_kjnodes_chains(fetch_text=_fetch_text)

        snapshots = fetch_kjnodes_snapshots(
            chain="cosmos",
            chains=chains,
            fetch_text=_fetch_text,
            fetch_headers=_fetch_headers,
        )

        self.assertEqual(len(snapshots), 1)
        snapshot = snapshots[0]
        self.assertEqual(snapshot.source, "kjnodes")
        self.assertEqual(snapshot.currency_id, "cosmos")
        self.assertEqual(snapshot.block_heights, (31781864,))
        self.assertEqual(snapshot.node_version, "v27.4.0")

    def test_fetches_lavender_snapshot_by_alias(self):
        snapshots = fetch_lavender_snapshots(
            chain="Cosmos",
            fetch_text=_fetch_text,
            fetch_headers=_fetch_headers,
        )

        self.assertEqual(len(snapshots), 1)
        snapshot = snapshots[0]
        self.assertEqual(snapshot.source, "lavender")
        self.assertEqual(snapshot.currency_id, "cosmos")
        self.assertEqual(snapshot.block_heights, (31802173,))
        self.assertEqual(
            snapshot.url,
            "https://snapshots.lavenderfive.com/snapshots/cosmoshub/cosmoshub_31802173.tar.zst",
        )


def _fetch_text(url, timeout):
    if url == "https://www.polkachu.com/tendermint_snapshots":
        return """
        <a href="https://www.polkachu.com/tendermint_snapshots/cosmos">CosmosHub</a>
        """
    if url == "https://www.polkachu.com/tendermint_snapshots/cosmos":
        return """
        Block Height Size Timestamp Download
        31798367 21 GB 34 minutes ago
        <a href="https://snapshots.polkachu.com/snapshots/cosmos/cosmos_31798367.tar.lz4">
        cosmos_31798367.tar.lz4</a>
        """
    if url == "https://services.kjnodes.com/":
        return '<a href="/mainnet/cosmoshub/snapshot/">Snapshot</a>'
    if url == "https://services.kjnodes.com/mainnet/cosmoshub/snapshot/":
        return """
        Block Age Download
        31781864 3 hours
        <a href="https://snapshots.kjnodes.com/cosmoshub/snapshot_latest.tar.lz4">snapshot (69.85 GB)</a>
        """
    if url == "https://www.lavenderfive.com/tools":
        return """
        https://snapshots.lavenderfive.com/snapshots/cosmoshub/latest.tar.zst
        https://snapshots.lavenderfive.com/snapshots/cosmoshub/cosmoshub_31800000.tar.zst
        https://snapshots.lavenderfive.com/snapshots/cosmoshub/cosmoshub_31802173.tar.zst
        """
    raise AssertionError(f"unexpected URL: {url}")


def _fetch_headers(url, timeout):
    if "polkachu" in url:
        return {"content-length": "22000000000", "last-modified": "Tue, 30 Jun 2026 07:05:14 GMT"}
    if "kjnodes" in url:
        return {
            "content-length": "75460524532",
            "last-modified": "Tue, 30 Jun 2026 00:28:54 GMT",
            "x-chain-blockheight": "31781864",
            "x-chain-version": "v27.4.0",
        }
    if "lavenderfive" in url:
        return {"content-length": "12274411044", "last-modified": "Mon, 29 Jun 2026 13:10:10 GMT"}
    return {}


if __name__ == "__main__":
    unittest.main()
