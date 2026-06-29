import unittest

import snapfetcher.cli as cli
from snapfetcher.cli import _chain_to_dict, _format_chain_csv, _format_chain_table
from snapfetcher.polkachu import PolkachuChain
from snapfetcher.publicnode import ChainSummary, Snapshot, find_snapshots


class CliTest(unittest.TestCase):
    def test_chain_table_includes_network_names_without_counts(self):
        table = _format_chain_table(
            [
                ChainSummary(
                    currency_id="bitcoin",
                    currency_name="Bitcoin",
                    snapshot_count=4,
                    networks=("mainnet", "testnet"),
                    clients=(),
                )
            ]
        )

        header = table.splitlines()[0]

        self.assertNotIn("snapshots", header)
        self.assertNotIn("network_count", header)
        self.assertIn("network_names", table)
        self.assertIn("Bitcoin", table)
        self.assertIn("mainnet, testnet", table)

    def test_chain_json_keeps_summary_fields(self):
        payload = _chain_to_dict(
            ChainSummary(
                currency_id="ethereum",
                currency_name="Ethereum",
                snapshot_count=30,
                networks=("mainnet", "sepolia"),
                clients=("geth", "reth"),
            )
        )

        self.assertEqual(payload["networkCount"], 2)
        self.assertEqual(payload["networkNames"], ["mainnet", "sepolia"])
        self.assertEqual(payload["networks"], ["mainnet", "sepolia"])

    def test_chain_csv_is_spreadsheet_friendly(self):
        csv_output = _format_chain_csv(
            [
                ChainSummary(
                    currency_id="bitcoin",
                    currency_name="Bitcoin",
                    snapshot_count=4,
                    networks=("mainnet", "testnet"),
                    clients=(),
                )
            ]
        )

        self.assertEqual(
            csv_output,
            "chain,id,network_names,clients\nBitcoin,bitcoin,\"mainnet, testnet\",-",
        )

    def test_fetches_duplicate_chain_name_from_all_matching_sources(self):
        original_publicnode = cli.fetch_publicnode_snapshots
        original_polkachu_chains = cli.fetch_polkachu_chains
        original_polkachu_snapshots = cli.fetch_polkachu_snapshots
        try:
            cli.fetch_publicnode_snapshots = lambda timeout: [
                _snapshot("publicnode", "Axelar", client_id=None)
            ]
            cli.fetch_polkachu_chains = lambda timeout: [
                PolkachuChain(
                    slug="axelar",
                    name="Axelar",
                    url="https://www.polkachu.com/tendermint_snapshots/axelar",
                )
            ]
            cli.fetch_polkachu_snapshots = lambda chain, timeout, chains: [
                _snapshot("polkachu", "Axelar", client_id="tendermint")
            ]

            snapshots = cli._fetch_snapshots_for_filters(
                chain="Axelar",
                network=None,
                client=None,
                timeout=1,
            )
            matches = find_snapshots(snapshots, chain="Axelar")

            self.assertEqual({snapshot.source for snapshot in matches}, {"publicnode", "polkachu"})
            self.assertEqual({snapshot.client_id for snapshot in matches}, {None, "tendermint"})
        finally:
            cli.fetch_publicnode_snapshots = original_publicnode
            cli.fetch_polkachu_chains = original_polkachu_chains
            cli.fetch_polkachu_snapshots = original_polkachu_snapshots


def _snapshot(source, currency_name, *, client_id):
    return Snapshot(
        currency_id="axelar",
        currency_name=currency_name,
        network_name="mainnet",
        snapshot_name="axelar",
        client_id=client_id,
        snapshot_type="full",
        block_heights=(1,),
        compressed_bytes=1024,
        uncompressed_bytes=None,
        node_version=None,
        url=f"https://example.com/{source}.tar.lz4",
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
