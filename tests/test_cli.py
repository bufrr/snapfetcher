import unittest
from contextlib import redirect_stdout
from io import StringIO

import snapfetcher.cli as cli
from snapfetcher.cli import (
    _chain_to_dict,
    _format_chain_csv,
    _format_chain_table,
)
from snapfetcher.publicnode import ChainSummary, Snapshot


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

    def test_main_fetches_publicnode_snapshots(self):
        original_publicnode = cli.fetch_publicnode_snapshots
        try:
            cli.fetch_publicnode_snapshots = lambda timeout: [
                _snapshot("publicnode", "Ethereum", currency_id="ethereum", client_id="geth")
            ]
            output = StringIO()

            with redirect_stdout(output):
                code = cli.main(["--url-only"])

            self.assertEqual(code, 0)
            self.assertEqual(output.getvalue().strip(), "https://example.com/publicnode.tar.lz4")
        finally:
            cli.fetch_publicnode_snapshots = original_publicnode


def _snapshot(source, currency_name, *, client_id, currency_id="axelar"):
    return Snapshot(
        currency_id=currency_id,
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
